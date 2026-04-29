"""
Transfer and Escalation Service
Handles department transfers and complaint escalations
"""

from datetime import datetime
from database.db import db

def request_department_transfer(complaint_id, from_department_id, to_department, officer_id, reason):
    """Request department transfer"""
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Get to_department_id
        cursor.execute("SELECT id FROM departments WHERE name = ?", (to_department,))
        to_dept_result = cursor.fetchone()
        if not to_dept_result:
            conn.close()
            return False
        
        to_department_id = to_dept_result['id']
        
        # Insert transfer request
        cursor.execute("""
            INSERT INTO transfer_requests 
            (complaint_id, from_department_id, to_department_id, officer_id, reason, status, created_at)
            VALUES (?, ?, ?, ?, ?, 'PENDING', ?)
        """, (complaint_id, from_department_id, to_department_id, officer_id, reason, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error requesting transfer: {e}")
        return False

def escalate_complaint(complaint_id, department_id, officer_id, reason, urgency):
    """Escalate complaint"""
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Update complaint status
        cursor.execute("""
            UPDATE complaints SET status = 'Escalated', urgency_level = ?
            WHERE id = ?
        """, (urgency, complaint_id))
        
        # Insert escalation record
        cursor.execute("""
            INSERT INTO escalations 
            (complaint_id, department_id, officer_id, reason, urgency, status, created_at)
            VALUES (?, ?, ?, ?, ?, 'ESCALATED', ?)
        """, (complaint_id, department_id, officer_id, reason, urgency, datetime.now().isoformat()))
        
        # Create notification for admin
        cursor.execute("""
            INSERT INTO notifications (recipient_type, recipient_id, notification_type, title, message, complaint_id)
            SELECT 'admin', id, 'escalation', 'Complaint Escalated', 
                   'Complaint #' || ? || ' has been escalated by officer', ?
            FROM admins
        """, (complaint_id, complaint_id))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error escalating complaint: {e}")
        return False

def get_pending_transfers():
    """Get pending transfer requests"""
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT tr.*, c.title, c.description, 
                   fd.name as from_department, td.name as to_department,
                   do.name as officer_name
            FROM transfer_requests tr
            JOIN complaints c ON tr.complaint_id = c.id
            JOIN departments fd ON tr.from_department_id = fd.id
            JOIN departments td ON tr.to_department_id = td.id
            JOIN department_officers do ON tr.officer_id = do.id
            WHERE tr.status = 'PENDING'
            ORDER BY tr.created_at DESC
        """)
        
        transfers = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return transfers
        
    except Exception as e:
        print(f"Error getting transfers: {e}")
        return []

def get_officer_transfer_requests(officer_id):
    """Get transfer requests made by specific officer"""
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT tr.*, c.title, c.description, 
                   fd.name as from_department, td.name as to_department,
                   tr.status, tr.created_at, tr.processed_at
            FROM transfer_requests tr
            JOIN complaints c ON tr.complaint_id = c.id
            JOIN departments fd ON tr.from_department_id = fd.id
            JOIN departments td ON tr.to_department_id = td.id
            WHERE tr.officer_id = ?
            ORDER BY tr.created_at DESC
        """, (officer_id,))
        
        transfers = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return transfers
        
    except Exception as e:
        print(f"Error getting officer transfers: {e}")
        return []

def get_escalated_complaints():
    """Get escalated complaints"""
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT e.*, c.title, c.description, c.urgency_level,
                   d.name as department_name, do.name as officer_name
            FROM escalations e
            JOIN complaints c ON e.complaint_id = c.id
            JOIN departments d ON e.department_id = d.id
            JOIN department_officers do ON e.officer_id = do.id
            WHERE e.status = 'ESCALATED'
            ORDER BY e.created_at DESC
        """)
        
        escalations = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return escalations
        
    except Exception as e:
        print(f"Error getting escalations: {e}")
        return []

def approve_transfer(transfer_id, admin_id):
    """Approve transfer request"""
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Get transfer details
        cursor.execute("SELECT * FROM transfer_requests WHERE id = ?", (transfer_id,))
        transfer = cursor.fetchone()
        if not transfer:
            conn.close()
            return False
        
        # Update complaint department
        cursor.execute("""
            UPDATE complaints SET department_id = ?
            WHERE id = ?
        """, (transfer['to_department_id'], transfer['complaint_id']))
        
        # Update transfer status
        cursor.execute("""
            UPDATE transfer_requests SET status = 'APPROVED', processed_by = ?, processed_at = ?
            WHERE id = ?
        """, (admin_id, datetime.now().isoformat(), transfer_id))
        
        # Create notification for officer
        cursor.execute("""
            INSERT INTO notifications (recipient_type, recipient_id, notification_type, title, message, complaint_id)
            VALUES ('officer', ?, 'assignment', 'Transfer Approved', 
                   'Your transfer request for complaint #' || ? || ' has been approved', ?)
        """, (transfer['officer_id'], transfer['complaint_id'], transfer['complaint_id']))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error approving transfer: {e}")
        return False

def reject_transfer(transfer_id, admin_id):
    """Reject transfer request"""
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Get transfer details
        cursor.execute("SELECT * FROM transfer_requests WHERE id = ?", (transfer_id,))
        transfer = cursor.fetchone()
        if not transfer:
            conn.close()
            return False
        
        cursor.execute("""
            UPDATE transfer_requests SET status = 'REJECTED', processed_by = ?, processed_at = ?
            WHERE id = ?
        """, (admin_id, datetime.now().isoformat(), transfer_id))
        
        # Create notification for officer
        cursor.execute("""
            INSERT INTO notifications (recipient_type, recipient_id, notification_type, title, message, complaint_id)
            VALUES ('officer', ?, 'complaint_update', 'Transfer Rejected', 
                   'Your transfer request for complaint #' || ? || ' has been rejected', ?)
        """, (transfer['officer_id'], transfer['complaint_id'], transfer['complaint_id']))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error rejecting transfer: {e}")
        return False

def assign_multiple_departments(complaint_id, department_names, admin_id):
    """Assign multiple departments to an escalated complaint"""
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Clear existing assignments
        cursor.execute("DELETE FROM complaint_departments WHERE complaint_id = ?", (complaint_id,))
        
        # Assign departments
        for i, dept_name in enumerate(department_names):
            # Get department ID
            cursor.execute("SELECT id FROM departments WHERE name = ?", (dept_name,))
            dept_result = cursor.fetchone()
            if not dept_result:
                continue
            
            dept_id = dept_result['id']
            role = 'PRIMARY' if i == 0 else 'SECONDARY'
            
            cursor.execute("""
                INSERT INTO complaint_departments (complaint_id, department_id, role, assigned_by)
                VALUES (?, ?, ?, ?)
            """, (complaint_id, dept_id, role, admin_id))
        
        # Update complaint status to ESCALATED
        cursor.execute("""
            UPDATE complaints SET status = 'Escalated' WHERE id = ?
        """, (complaint_id,))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error assigning multiple departments: {e}")
        return False

def get_complaint_departments(complaint_id):
    """Get departments assigned to a complaint"""
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT cd.*, d.name as department_name
            FROM complaint_departments cd
            JOIN departments d ON cd.department_id = d.id
            WHERE cd.complaint_id = ?
            ORDER BY cd.role DESC, cd.assigned_at
        """, (complaint_id,))
        
        departments = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return departments
        
    except Exception as e:
        print(f"Error getting complaint departments: {e}")
        return []