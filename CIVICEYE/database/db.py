import sqlite3
import os
from datetime import datetime, timedelta
import json
import hashlib
from typing import Optional, Dict, List, Any

class DatabaseManager:
    """Professional database manager for CIVICEYE system"""
    
    def __init__(self, db_path: str = "database/civiceye.db"):
        self.db_path = db_path
        self.ensure_db_directory()
        self.init_database()
    
    def ensure_db_directory(self):
        """Ensure database directory exists"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection with proper configuration"""
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraints
        conn.execute("PRAGMA journal_mode = WAL")  # Better concurrency
        return conn
    
    def init_database(self):
        """Initialize database with schema"""
        try:
            schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
            
            if not os.path.exists(schema_path):
                raise FileNotFoundError(f"Schema file not found: {schema_path}")
            
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Execute schema in chunks (split by semicolon)
            statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]
            
            for statement in statements:
                try:
                    cursor.execute(statement)
                except sqlite3.Error as e:
                    print(f"Warning: Error executing statement: {e}")
                    print(f"Statement: {statement[:100]}...")
            
            # Execute transfer/escalation schema
            transfer_schema_path = os.path.join(os.path.dirname(__file__), "transfer_escalation_schema.sql")
            if os.path.exists(transfer_schema_path):
                with open(transfer_schema_path, 'r', encoding='utf-8') as f:
                    transfer_sql = f.read()
                
                transfer_statements = [stmt.strip() for stmt in transfer_sql.split(';') if stmt.strip()]
                for statement in transfer_statements:
                    try:
                        cursor.execute(statement)
                    except sqlite3.Error as e:
                        print(f"Warning: Error executing transfer statement: {e}")
            
            # Execute complaint departments schema
            complaint_dept_schema_path = os.path.join(os.path.dirname(__file__), "complaint_departments_schema.sql")
            if os.path.exists(complaint_dept_schema_path):
                with open(complaint_dept_schema_path, 'r', encoding='utf-8') as f:
                    complaint_dept_sql = f.read()
                
                complaint_dept_statements = [stmt.strip() for stmt in complaint_dept_sql.split(';') if stmt.strip()]
                for statement in complaint_dept_statements:
                    try:
                        cursor.execute(statement)
                    except sqlite3.Error as e:
                        print(f"Warning: Error executing complaint departments statement: {e}")
            
            conn.commit()
            conn.close()
            
            print("Database initialized successfully")
            
        except Exception as e:
            print(f"Database initialization failed: {e}")
            raise
    
    def hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self, mobile_number: str, password: str, district: str, 
                   location_permission: bool = False) -> Optional[int]:
        """Create new user account"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Check if mobile number already exists
            cursor.execute("SELECT id FROM users WHERE mobile_number = ?", (mobile_number,))
            if cursor.fetchone():
                conn.close()
                return None
            
            password_hash = self.hash_password(password)
            
            cursor.execute("""
                INSERT INTO users (mobile_number, password_hash, district, location_permission)
                VALUES (?, ?, ?, ?)
            """, (mobile_number, password_hash, district, location_permission))
            
            user_id = cursor.lastrowid
            
            # Log user creation
            self.log_audit('system', None, 'user_created', 'users', user_id, 
                          None, {'mobile_number': mobile_number, 'district': district})
            
            conn.commit()
            conn.close()
            
            return user_id
            
        except Exception as e:
            print(f"Error creating user: {e}")
            return None
    
    def authenticate_user(self, mobile_number: str, password: str) -> Optional[Dict]:
        """Authenticate user login"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            password_hash = self.hash_password(password)
            
            cursor.execute("""
                SELECT id, mobile_number, district, location_permission, status
                FROM users 
                WHERE mobile_number = ? AND password_hash = ? AND status = 'active'
            """, (mobile_number, password_hash))
            
            user = cursor.fetchone()
            
            if user:
                # Update last login
                cursor.execute("""
                    UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?
                """, (user['id'],))
                
                conn.commit()
                conn.close()
                
                return dict(user)
            
            conn.close()
            return None
            
        except Exception as e:
            print(f"Error authenticating user: {e}")
            return None
    
    def create_department_officer(self, officer_id: str, password: str, name: str, 
                                department_name: str, email: str = None, phone: str = None) -> Optional[int]:
        """Create department officer account"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Get department ID
            cursor.execute("SELECT id FROM departments WHERE name = ?", (department_name,))
            dept = cursor.fetchone()
            if not dept:
                conn.close()
                return None
            
            department_id = dept['id']
            
            # Check if officer ID already exists
            cursor.execute("SELECT id FROM department_officers WHERE officer_id = ?", (officer_id,))
            if cursor.fetchone():
                conn.close()
                return None
            
            password_hash = self.hash_password(password)
            
            cursor.execute("""
                INSERT INTO department_officers 
                (officer_id, password_hash, name, department_id, email, phone)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (officer_id, password_hash, name, department_id, email, phone))
            
            officer_db_id = cursor.lastrowid
            
            conn.commit()
            conn.close()
            
            return officer_db_id
            
        except Exception as e:
            print(f"Error creating department officer: {e}")
            return None
    
    def authenticate_officer(self, officer_id: str, password: str) -> Optional[Dict]:
        """Authenticate department officer login"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            password_hash = self.hash_password(password)
            
            cursor.execute("""
                SELECT o.id, o.officer_id, o.name, o.email, o.phone, o.status,
                       d.name as department_name, d.id as department_id
                FROM department_officers o
                JOIN departments d ON o.department_id = d.id
                WHERE o.officer_id = ? AND o.password_hash = ? AND o.status = 'active'
            """, (officer_id, password_hash))
            
            officer = cursor.fetchone()
            
            if officer:
                # Update last login
                cursor.execute("""
                    UPDATE department_officers SET last_login = CURRENT_TIMESTAMP WHERE id = ?
                """, (officer['id'],))
                
                conn.commit()
                conn.close()
                
                return dict(officer)
            
            conn.close()
            return None
            
        except Exception as e:
            print(f"Error authenticating officer: {e}")
            return None
    
    def create_admin(self, admin_id: str, password: str, name: str, 
                    email: str = None, phone: str = None) -> Optional[int]:
        """Create admin account"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Check if admin ID already exists
            cursor.execute("SELECT id FROM admins WHERE admin_id = ?", (admin_id,))
            if cursor.fetchone():
                conn.close()
                return None
            
            password_hash = self.hash_password(password)
            
            cursor.execute("""
                INSERT INTO admins (admin_id, password_hash, name, email, phone)
                VALUES (?, ?, ?, ?, ?)
            """, (admin_id, password_hash, name, email, phone))
            
            admin_db_id = cursor.lastrowid
            
            conn.commit()
            conn.close()
            
            return admin_db_id
            
        except Exception as e:
            print(f"Error creating admin: {e}")
            return None
    
    def authenticate_admin(self, admin_id: str, password: str) -> Optional[Dict]:
        """Authenticate admin login"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            password_hash = self.hash_password(password)
            
            cursor.execute("""
                SELECT id, admin_id, name, email, phone, status
                FROM admins 
                WHERE admin_id = ? AND password_hash = ? AND status = 'active'
            """, (admin_id, password_hash))
            
            admin = cursor.fetchone()
            
            if admin:
                # Update last login
                cursor.execute("""
                    UPDATE admins SET last_login = CURRENT_TIMESTAMP WHERE id = ?
                """, (admin['id'],))
                
                conn.commit()
                conn.close()
                
                return dict(admin)
            
            conn.close()
            return None
            
        except Exception as e:
            print(f"Error authenticating admin: {e}")
            return None
    
    def get_districts(self) -> List[str]:
        """Get list of Tamil Nadu districts"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT district_name FROM locations ORDER BY district_name")
            districts = [row['district_name'] for row in cursor.fetchall()]
            
            conn.close()
            return districts
            
        except Exception as e:
            print(f"Error getting districts: {e}")
            return []
    
    def get_departments(self) -> List[Dict]:
        """Get list of departments"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, name, description 
                FROM departments 
                WHERE status = 'active' 
                ORDER BY name
            """)
            
            departments = [dict(row) for row in cursor.fetchall()]
            
            conn.close()
            return departments
            
        except Exception as e:
            print(f"Error getting departments: {e}")
            return []
    
    def log_audit(self, user_type: str, user_id: Optional[int], action: str,
                  table_name: str = None, record_id: int = None,
                  old_values: Dict = None, new_values: Dict = None,
                  ip_address: str = None, user_agent: str = None):
        """Log audit trail"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO audit_logs
                (user_type, user_id, action, table_name, record_id, old_values, new_values, ip_address, user_agent)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_type, user_id, action, table_name, record_id,
                json.dumps(old_values) if old_values else None,
                json.dumps(new_values) if new_values else None,
                ip_address, user_agent
            ))

            conn.commit()
        except Exception as e:
            print(f"Error logging audit: {e}")
        finally:
            conn.close()
    
    def test_connection(self) -> bool:
        """Test database connection and basic operations"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Test basic query
            cursor.execute("SELECT COUNT(*) as count FROM users")
            result = cursor.fetchone()
            
            conn.close()
            
            print(f"Database connection test successful. Users count: {result['count']}")
            return True
            
        except Exception as e:
            print(f"Database connection test failed: {e}")
            return False

# Global database instance
db = DatabaseManager()

# Convenience functions for backward compatibility
def get_db_connection():
    """Get database connection (backward compatibility)"""
    return db.get_connection()

def init_database():
    """Initialize database (backward compatibility)"""
    return db.init_database()