"""
Admin Service Functions
Handles admin-specific actions like reassign and override
"""

from datetime import datetime
from database.db import db

def admin_reassign_complaint(complaint_id, new_department_name, admin_id):
    """Admin directly reassigns complaint to a department"""
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Get new department ID
        cursor.execute("SELECT id FROM departments WHERE name = ?", (new_department_name,))
        dept_result = cursor.fetchone()
        if not dept_result:
            conn.close()
            return False
        
        new_department_id = dept_result['id']
        
        # Update complaint
        cursor.execute("""
            UPDATE complaints 
            SET department_id = ?, status = 'Assigned', updated_at = ?
            WHERE id = ?
        """, (new_department_id, datetime.now().isoformat(), complaint_id))
        
        # Log admin action
        cursor.execute("""
            INSERT INTO admin_actions 
            (admin_id, action_type, target_type, target_id, action_details, reason)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (admin_id, 'reroute_approved', 'complaint', complaint_id, 
              f'Complaint reassigned to {new_department_name}', 'Admin direct reassignment'))
        
        # Create notification
        cursor.execute("""
            INSERT INTO notifications (recipient_type, recipient_id, notification_type, title, message, complaint_id)
            SELECT 'officer', do.id, 'assignment', 'Complaint Assigned', 
                   'Complaint #' || ? || ' has been assigned to your department by admin', ?
            FROM department_officers do
            WHERE do.department_id = ?
        """, (complaint_id, complaint_id, new_department_id))
        
        # Log audit
        db.log_audit('admin', admin_id, 'complaint_reassigned', 'complaints', complaint_id,
                    None, {'new_department': new_department_name})
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error reassigning complaint: {e}")
        return False

def admin_override_complaint(complaint_id, new_status, new_department_name, override_reason, admin_id):
    """Admin overrides complaint status and/or department"""
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Get current complaint data
        cursor.execute("SELECT * FROM complaints WHERE id = ?", (complaint_id,))
        complaint = cursor.fetchone()
        if not complaint:
            conn.close()
            return False
        
        # Prepare update fields
        update_fields = []
        update_values = []
        
        if new_status:
            update_fields.append("status = ?")
            update_values.append(new_status)
            
            if new_status == 'Resolved':
                update_fields.append("resolved_at = ?")
                update_values.append(datetime.now().isoformat())
        
        if new_department_name:
            cursor.execute("SELECT id FROM departments WHERE name = ?", (new_department_name,))
            dept_result = cursor.fetchone()
            if dept_result:
                update_fields.append("department_id = ?")
                update_values.append(dept_result['id'])
        
        update_fields.append("updated_at = ?")
        update_values.append(datetime.now().isoformat())
        update_values.append(complaint_id)
        
        # Update complaint
        if update_fields:
            query = f"UPDATE complaints SET {', '.join(update_fields)} WHERE id = ?"
            cursor.execute(query, update_values)
        
        # Log admin action
        action_details = f"Status: {new_status}" if new_status else ""
        if new_department_name:
            action_details += f", Department: {new_department_name}"
        
        cursor.execute("""
            INSERT INTO admin_actions 
            (admin_id, action_type, target_type, target_id, action_details, reason)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (admin_id, 'override_decision', 'complaint', complaint_id, action_details, override_reason))
        
        # Create notification
        cursor.execute("""
            INSERT INTO notifications (recipient_type, recipient_id, notification_type, title, message, complaint_id)
            VALUES ('user', ?, 'complaint_update', 'Complaint Updated', 
                   'Your complaint #' || ? || ' has been updated by admin', ?)
        """, (complaint['user_id'], complaint_id, complaint_id))
        
        # Log audit
        db.log_audit('admin', admin_id, 'complaint_overridden', 'complaints', complaint_id,
                    None, {'new_status': new_status, 'new_department': new_department_name, 'reason': override_reason})
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error overriding complaint: {e}")
        return False