"""
CIVICEYE Security Module
Handles authentication, authorization, password validation, and security utilities
"""

import hashlib
import re
import secrets
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple
import streamlit as st

from utils.constants import (
    SECURITY_CONFIG, VALIDATION_RULES, ERROR_MESSAGES, 
    SUCCESS_MESSAGES, USER_ROLES
)

class SecurityManager:
    """Comprehensive security manager for CIVICEYE system"""
    
    def __init__(self):
        self.failed_attempts = {}  # Track failed login attempts
        self.locked_accounts = {}  # Track locked accounts
    
    def hash_password(self, password: str) -> str:
        """Hash password using SHA-256 with salt"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}:{password_hash}"
    
    def verify_password(self, password: str, stored_hash: str) -> bool:
        """Verify password against stored hash"""
        try:
            if ':' not in stored_hash:
                # Legacy hash without salt (backward compatibility)
                return hashlib.sha256(password.encode()).hexdigest() == stored_hash
            
            salt, password_hash = stored_hash.split(':', 1)
            computed_hash = hashlib.sha256((password + salt).encode()).hexdigest()
            return computed_hash == password_hash
        except Exception:
            return False
    
    def validate_password_strength(self, password: str) -> Tuple[bool, str]:
        """Validate password strength according to security policy"""
        config = SECURITY_CONFIG
        
        if len(password) < config['password_min_length']:
            return False, f"Password must be at least {config['password_min_length']} characters long"
        
        if config['password_require_uppercase'] and not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        
        if config['password_require_lowercase'] and not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        
        if config['password_require_numbers'] and not re.search(r'\d', password):
            return False, "Password must contain at least one number"
        
        if config['password_require_special'] and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Password must contain at least one special character"
        
        # Check for common weak passwords
        weak_patterns = [
            r'123456', r'password', r'qwerty', r'abc123', r'admin',
            r'(.)\1{3,}',  # Repeated characters (aaaa, 1111)
        ]
        
        for pattern in weak_patterns:
            if re.search(pattern, password.lower()):
                return False, "Password is too weak. Please choose a stronger password"
        
        return True, "Password is strong"
    
    def validate_mobile_number(self, mobile: str) -> Tuple[bool, str]:
        """Validate Indian mobile number format"""
        pattern = VALIDATION_RULES['mobile_number']['pattern']
        message = VALIDATION_RULES['mobile_number']['message']
        
        if not re.match(pattern, mobile):
            return False, message
        
        return True, "Valid mobile number"
    
    def validate_officer_id(self, officer_id: str) -> Tuple[bool, str]:
        """Validate department officer ID format"""
        pattern = VALIDATION_RULES['officer_id']['pattern']
        message = VALIDATION_RULES['officer_id']['message']
        
        if not re.match(pattern, officer_id):
            return False, message
        
        return True, "Valid officer ID"
    
    def validate_admin_id(self, admin_id: str) -> Tuple[bool, str]:
        """Validate admin ID format"""
        pattern = VALIDATION_RULES['admin_id']['pattern']
        message = VALIDATION_RULES['admin_id']['message']
        
        if not re.match(pattern, admin_id):
            return False, message
        
        return True, "Valid admin ID"
    
    def check_account_lockout(self, identifier: str) -> Tuple[bool, Optional[int]]:
        """Check if account is locked due to failed attempts"""
        if identifier in self.locked_accounts:
            lock_time = self.locked_accounts[identifier]
            unlock_time = lock_time + SECURITY_CONFIG['lockout_duration']
            
            if time.time() < unlock_time:
                remaining_time = int(unlock_time - time.time())
                return True, remaining_time
            else:
                # Lockout expired, remove from locked accounts
                del self.locked_accounts[identifier]
                if identifier in self.failed_attempts:
                    del self.failed_attempts[identifier]
        
        return False, None
    
    def record_failed_attempt(self, identifier: str):
        """Record failed login attempt"""
        current_time = time.time()
        
        if identifier not in self.failed_attempts:
            self.failed_attempts[identifier] = []
        
        # Remove attempts older than 1 hour
        self.failed_attempts[identifier] = [
            attempt_time for attempt_time in self.failed_attempts[identifier]
            if current_time - attempt_time < 3600
        ]
        
        # Add current attempt
        self.failed_attempts[identifier].append(current_time)
        
        # Check if account should be locked
        if len(self.failed_attempts[identifier]) >= SECURITY_CONFIG['max_login_attempts']:
            self.locked_accounts[identifier] = current_time
    
    def clear_failed_attempts(self, identifier: str):
        """Clear failed attempts after successful login"""
        if identifier in self.failed_attempts:
            del self.failed_attempts[identifier]
        if identifier in self.locked_accounts:
            del self.locked_accounts[identifier]
    
    def sanitize_input(self, input_text: str) -> str:
        """Sanitize user input to prevent injection attacks"""
        if not input_text:
            return ""
        
        # Remove potentially dangerous characters
        sanitized = re.sub(r'[<>"\';\\]', '', str(input_text))
        
        # Limit length
        sanitized = sanitized[:2000]
        
        # Strip whitespace
        sanitized = sanitized.strip()
        
        return sanitized
    
    def validate_file_upload(self, uploaded_file) -> Tuple[bool, str]:
        """Validate uploaded file for security"""
        if not uploaded_file:
            return True, "No file uploaded"
        
        # Check file size
        file_size = len(uploaded_file.getvalue())
        max_size = SECURITY_CONFIG.get('max_file_size', 200 * 1024 * 1024)  # 200MB default
        
        if file_size > max_size:
            return False, f"File size ({file_size / 1024 / 1024:.1f}MB) exceeds maximum limit ({max_size / 1024 / 1024:.0f}MB)"
        
        # Check file extension
        filename = uploaded_file.name.lower()
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.mp4', '.avi', '.mov']
        
        if not any(filename.endswith(ext) for ext in allowed_extensions):
            return False, "Invalid file type. Only images and videos are allowed"
        
        # Check for suspicious file names
        suspicious_patterns = [
            r'\.php', r'\.js', r'\.html', r'\.exe', r'\.bat', r'\.sh',
            r'script', r'<script', r'javascript:', r'vbscript:'
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, filename):
                return False, "Suspicious file detected"
        
        return True, "File is valid"

class RoleBasedAccessControl:
    """Role-based access control manager"""
    
    def __init__(self):
        self.roles = USER_ROLES
    
    def has_permission(self, user_role: str, permission: str) -> bool:
        """Check if user role has specific permission"""
        if user_role not in self.roles:
            return False
        
        return permission in self.roles[user_role]['permissions']
    
    def get_user_permissions(self, user_role: str) -> List[str]:
        """Get all permissions for a user role"""
        if user_role not in self.roles:
            return []
        
        return self.roles[user_role]['permissions']
    
    def can_access_complaint(self, user_role: str, user_id: int, complaint_data: Dict) -> bool:
        """Check if user can access specific complaint"""
        if user_role == 'admin':
            return True  # Admin can access all complaints
        
        if user_role == 'citizen':
            # Citizens can only access their own complaints
            return complaint_data.get('user_id') == user_id
        
        if user_role == 'department_officer':
            # Officers can access complaints assigned to their department
            return complaint_data.get('department_id') == user_id  # Assuming user_id is department_id for officers
        
        return False
    
    def can_modify_complaint(self, user_role: str, user_id: int, complaint_data: Dict) -> bool:
        """Check if user can modify specific complaint"""
        if user_role == 'admin':
            return True  # Admin can modify all complaints
        
        if user_role == 'department_officer':
            # Officers can modify complaints assigned to them
            return complaint_data.get('assigned_officer_id') == user_id
        
        return False  # Citizens cannot modify complaints after submission

class SessionManager:
    """Session management for user authentication"""
    
    def __init__(self):
        self.session_timeout = SECURITY_CONFIG['session_timeout']
    
    def create_session(self, user_data: Dict, user_type: str):
        """Create user session"""
        session_data = {
            'user_data': user_data,
            'user_type': user_type,
            'login_time': datetime.now(),
            'last_activity': datetime.now(),
            'session_id': secrets.token_urlsafe(32)
        }
        
        # Store in Streamlit session state
        for key, value in session_data.items():
            st.session_state[key] = value
        
        st.session_state.authenticated = True
    
    def is_session_valid(self) -> bool:
        """Check if current session is valid"""
        if not st.session_state.get('authenticated', False):
            return False
        
        last_activity = st.session_state.get('last_activity')
        if not last_activity:
            return False
        
        # Check session timeout
        if datetime.now() - last_activity > timedelta(seconds=self.session_timeout):
            self.destroy_session()
            return False
        
        # Update last activity
        st.session_state.last_activity = datetime.now()
        return True
    
    def destroy_session(self):
        """Destroy user session"""
        session_keys = [
            'authenticated', 'user_data', 'user_type', 'login_time',
            'last_activity', 'session_id'
        ]
        
        for key in session_keys:
            if key in st.session_state:
                del st.session_state[key]
    
    def get_current_user(self) -> Optional[Dict]:
        """Get current authenticated user data"""
        if self.is_session_valid():
            return st.session_state.get('user_data')
        return None
    
    def get_user_type(self) -> Optional[str]:
        """Get current user type"""
        if self.is_session_valid():
            return st.session_state.get('user_type')
        return None

# Global instances
security_manager = SecurityManager()
rbac = RoleBasedAccessControl()
session_manager = SessionManager()

# Convenience functions
def validate_password(password: str) -> Tuple[bool, str]:
    """Validate password strength"""
    return security_manager.validate_password_strength(password)

def validate_mobile(mobile: str) -> Tuple[bool, str]:
    """Validate mobile number"""
    return security_manager.validate_mobile_number(mobile)

def hash_password(password: str) -> str:
    """Hash password"""
    return security_manager.hash_password(password)

def verify_password(password: str, stored_hash: str) -> bool:
    """Verify password"""
    return security_manager.verify_password(password, stored_hash)

def sanitize_input(text: str) -> str:
    """Sanitize user input"""
    return security_manager.sanitize_input(text)

def check_permission(permission: str) -> bool:
    """Check if current user has permission"""
    user_type = session_manager.get_user_type()
    if not user_type:
        return False
    return rbac.has_permission(user_type, permission)

def require_auth(user_types: List[str] = None):
    """Decorator to require authentication"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not session_manager.is_session_valid():
                st.error("Please login to access this page")
                st.stop()
            
            if user_types:
                current_user_type = session_manager.get_user_type()
                if current_user_type not in user_types:
                    st.error("Access denied. Insufficient permissions.")
                    st.stop()
            
            return func(*args, **kwargs)
        return wrapper
    return decorator