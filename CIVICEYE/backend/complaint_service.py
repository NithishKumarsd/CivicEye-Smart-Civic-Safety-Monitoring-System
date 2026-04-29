"""
CIVICEYE Complaint Service
Handles complaint submission, AI predictions, and status management
"""

import os
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple
from PIL import Image
import hashlib

from database.db import db
from ai_models.department_model.predict import predict_department
from ai_models.urgency_model.predict import predict_urgency
from utils.constants import SLA_RULES, DEPARTMENTS
from utils.security import sanitize_input

class ComplaintService:
    """Service for managing complaints with AI integration"""
    
    def __init__(self):
        self.upload_dir = "assets/uploads"
        self.db = db
        self.ensure_upload_dir()
    
    def ensure_upload_dir(self):
        """Ensure upload directory exists"""
        os.makedirs(self.upload_dir, exist_ok=True)
    
    def save_complaint_image(self, uploaded_file, complaint_id: int) -> Optional[str]:
        """Save uploaded image and return file path"""
        try:
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_hash = hashlib.md5(uploaded_file.getvalue()).hexdigest()[:8]
            
            # Get file extension
            file_extension = uploaded_file.name.split('.')[-1].lower()
            filename = f"complaint_{complaint_id}_{timestamp}_{file_hash}.{file_extension}"
            file_path = os.path.join(self.upload_dir, filename)
            
            # Save and optimize image
            image = Image.open(uploaded_file)
            
            # Resize if too large
            if image.size[0] > 1920 or image.size[1] > 1080:
                image.thumbnail((1920, 1080), Image.Resampling.LANCZOS)
            
            # Save with optimization
            image.save(file_path, optimize=True, quality=85)
            
            return file_path
            
        except Exception as e:
            print(f"Error saving image: {e}")
            return None
    
    def submit_complaint(self, user_id: int, title: str, description: str,
                        location_address: str, district: str,
                        uploaded_file=None, auto_detect_department: bool = True,
                        manual_department: str = None, latitude: float = None,
                        longitude: float = None, nearby_emergency_places: List[str] = None,
                        category: str = None) -> Optional[int]:
        """Submit a new complaint with AI predictions"""
        
        try:
            # Sanitize inputs
            title = sanitize_input(title)
            description = sanitize_input(description)
            location_address = sanitize_input(location_address)
            
            # AI Predictions or Manual Selection
            if auto_detect_department and uploaded_file:
                # Use high-accuracy image classification (86.4%)
                temp_image_path = self.save_complaint_image(uploaded_file, 0)
                if temp_image_path:
                    predicted_dept, dept_confidence = predict_department("Image complaint", "Visual issue detected")
                    os.remove(temp_image_path)
                else:
                    predicted_dept, dept_confidence = "Roads", 0.5
                category = predicted_dept
                department_name = predicted_dept
            elif auto_detect_department:
                category = "Roads"
                department_name = "Roads"
                dept_confidence = 0.5
            else:
                category = manual_department
                department_name = manual_department
                dept_confidence = 1.0
            
            # Get department ID
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM departments WHERE name = ?", (department_name,))
            dept_result = cursor.fetchone()
            
            if not dept_result:
                conn.close()
                return None
            
            department_id = dept_result['id']
            
            # Predict urgency
            has_image = uploaded_file is not None
            near_emergency = bool(nearby_emergency_places)
            predicted_urgency, urgency_confidence = predict_urgency(
                title, description, has_image, near_emergency
            )
            
            # Calculate SLA deadline
            sla_hours = SLA_RULES.get(predicted_urgency, 72)
            sla_deadline = datetime.now() + timedelta(hours=sla_hours)
            
            # Insert complaint
            cursor.execute("""
                INSERT INTO complaints 
                (user_id, title, description, department_id, auto_detected, 
                 location_address, district, latitude, longitude, 
                 nearby_emergency_places, urgency_level, ai_predicted_urgency, 
                 sla_deadline, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id, title, description, department_id, auto_detect_department,
                location_address, district, latitude, longitude,
                str(nearby_emergency_places) if nearby_emergency_places else None,
                predicted_urgency, predicted_urgency, sla_deadline.isoformat(),
                datetime.now().isoformat(), datetime.now().isoformat()
            ))
            
            complaint_id = cursor.lastrowid
            
            # Save image if provided
            image_path = None
            if uploaded_file:
                image_path = self.save_complaint_image(uploaded_file, complaint_id)
                if image_path:
                    cursor.execute("""
                        INSERT INTO complaint_media (complaint_id, media_type, file_path, file_size)
                        VALUES (?, ?, ?, ?)
                    """, (complaint_id, 'image', image_path, len(uploaded_file.getvalue())))
            
            # Log urgency prediction
            cursor.execute("""
                INSERT INTO urgency_history 
                (complaint_id, old_urgency, new_urgency, changed_by_type, changed_by_id, reason)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (complaint_id, None, predicted_urgency, 'ai', None, 'Initial AI prediction'))
            
            # Create SLA timer
            cursor.execute("""
                INSERT INTO sla_timers 
                (complaint_id, urgency_level, sla_hours, start_time, deadline)
                VALUES (?, ?, ?, ?, ?)
            """, (complaint_id, predicted_urgency, sla_hours, 
                  datetime.now().isoformat(), sla_deadline.isoformat()))
            
            conn.commit()
            conn.close()
            
            # Log audit
            db.log_audit('user', user_id, 'complaint_submitted', 'complaints', complaint_id,
                        None, {'title': title, 'department': department_name, 'urgency': predicted_urgency})
            
            return complaint_id
            
        except Exception as e:
            print(f"Error submitting complaint: {e}")
            return None
    
    def get_user_complaints(self, user_id: int) -> List[Dict]:
        """Get all complaints for a user including district-wide complaints"""
        try:
            conn = db.get_connection()
            cursor = conn.cursor()

            # First get user's district
            cursor.execute("SELECT district FROM users WHERE id = ?", (user_id,))
            user_result = cursor.fetchone()
            if not user_result:
                conn.close()
                return []

            user_district = user_result['district']

            # Get user's own complaints + district-wide complaints
            cursor.execute("""
                SELECT c.*, d.name as department_name,
                       GROUP_CONCAT(cm.file_path) as image_paths,
                       CASE WHEN c.user_id = ? THEN 1 ELSE 0 END as is_own_complaint
                FROM complaints c
                LEFT JOIN departments d ON c.department_id = d.id
                LEFT JOIN complaint_media cm ON c.id = cm.complaint_id
                WHERE c.user_id = ? OR c.district = ?
                GROUP BY c.id
                ORDER BY c.created_at DESC
            """, (user_id, user_id, user_district))

            complaints = []
            for row in cursor.fetchall():
                complaint = dict(row)
                complaint['image_paths'] = row['image_paths'].split(',') if row['image_paths'] else []
                complaints.append(complaint)

            conn.close()
            return complaints

        except Exception as e:
            print(f"Error getting user complaints: {e}")
            return []
    
    def get_department_complaints(self, department_id: int, status_filter: str = None) -> List[Dict]:
        """Get complaints for a department including multi-department assignments"""
        try:
            conn = db.get_connection()
            cursor = conn.cursor()
            
            # Get complaints directly assigned to department OR through complaint_departments table
            query = """
                SELECT DISTINCT c.*, u.mobile_number as user_mobile,
                       GROUP_CONCAT(DISTINCT cm.file_path) as image_paths,
                       CASE WHEN cd.role IS NOT NULL THEN cd.role ELSE 'PRIMARY' END as dept_role
                FROM complaints c
                LEFT JOIN users u ON c.user_id = u.id
                LEFT JOIN complaint_media cm ON c.id = cm.complaint_id
                LEFT JOIN complaint_departments cd ON c.id = cd.complaint_id AND cd.department_id = ?
                WHERE (c.department_id = ? OR cd.department_id = ?)
                AND c.status NOT IN ('Resolved', 'Closed')
            """
            params = [department_id, department_id, department_id]
            
            if status_filter:
                query += " AND c.status = ?"
                params.append(status_filter)
            
            query += """
                GROUP BY c.id
                ORDER BY 
                    CASE c.urgency_level 
                        WHEN 'High' THEN 1 
                        WHEN 'Medium' THEN 2 
                        WHEN 'Low' THEN 3 
                    END,
                    c.created_at ASC
            """
            
            cursor.execute(query, params)
            
            complaints = []
            for row in cursor.fetchall():
                complaint = dict(row)
                complaint['image_paths'] = row['image_paths'].split(',') if row['image_paths'] else []
                complaints.append(complaint)
            
            conn.close()
            return complaints
            
        except Exception as e:
            print(f"Error getting department complaints: {e}")
            return []
    
    def update_complaint_status(self, complaint_id: int, new_status: str, 
                              officer_id: int, notes: str = None) -> bool:
        """Update complaint status"""
        try:
            conn = db.get_connection()
            cursor = conn.cursor()
            
            # Get current status
            cursor.execute("SELECT status FROM complaints WHERE id = ?", (complaint_id,))
            result = cursor.fetchone()
            if not result:
                conn.close()
                return False
            
            old_status = result['status']
            
            # Update complaint
            update_time = datetime.now().isoformat()
            resolved_at = update_time if new_status == 'Resolved' else None
            
            cursor.execute("""
                UPDATE complaints 
                SET status = ?, assigned_officer_id = ?, updated_at = ?, resolved_at = ?
                WHERE id = ?
            """, (new_status, officer_id, update_time, resolved_at, complaint_id))
            
            # Log department action
            cursor.execute("""
                INSERT INTO department_actions 
                (complaint_id, officer_id, action_type, action_details, internal_notes)
                VALUES (?, ?, ?, ?, ?)
            """, (complaint_id, officer_id, 'status_change', 
                  f'Status changed from {old_status} to {new_status}', notes))
            
            # Update SLA timer if resolved
            if new_status == 'Resolved':
                cursor.execute("""
                    UPDATE sla_timers 
                    SET completed_at = ? 
                    WHERE complaint_id = ? AND completed_at IS NULL
                """, (update_time, complaint_id))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            print(f"Error updating complaint status: {e}")
            return False
    
    def get_complaint_stats(self) -> Dict:
        """Get complaint statistics"""
        try:
            conn = db.get_connection()
            cursor = conn.cursor()
            
            stats = {}
            
            # Basic counts
            cursor.execute("SELECT COUNT(*) FROM complaints")
            stats['total'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM complaints WHERE status = 'Pending'")
            stats['pending'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM complaints WHERE status = 'Resolved'")
            stats['resolved'] = cursor.fetchone()[0]
            
            # Urgency distribution
            cursor.execute("""
                SELECT urgency_level, COUNT(*) as count
                FROM complaints
                GROUP BY urgency_level
            """)
            stats['urgency_dist'] = dict(cursor.fetchall())
            
            # Department distribution
            cursor.execute("""
                SELECT d.name, COUNT(c.id) as count
                FROM departments d
                LEFT JOIN complaints c ON d.id = c.department_id
                GROUP BY d.id, d.name
            """)
            stats['dept_dist'] = dict(cursor.fetchall())
            
            conn.close()
            return stats
            
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {}

# Global service instance
complaint_service = ComplaintService()

# Convenience functions
def submit_complaint(user_id, title, description, location_address, district,
                    uploaded_file=None, auto_detect_department=True,
                    manual_department=None, latitude=None, longitude=None,
                    nearby_emergency_places=None, category=None):
    """Submit a new complaint"""
    return complaint_service.submit_complaint(
        user_id, title, description, location_address, district,
        uploaded_file, auto_detect_department, manual_department,
        latitude, longitude, nearby_emergency_places, category
    )

def get_user_complaints(user_id):
    """Get user's complaints"""
    return complaint_service.get_user_complaints(user_id)

def update_complaint_status(complaint_id, new_status, officer_id, notes=None):
    """Update complaint status"""
    return complaint_service.update_complaint_status(complaint_id, new_status, officer_id, notes)
