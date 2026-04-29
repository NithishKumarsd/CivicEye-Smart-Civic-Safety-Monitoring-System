"""
CIVICEYE System Constants and Configuration
Professional Civic Complaint Management Platform
"""

# Tamil Nadu Districts (Official List)
TAMIL_NADU_DISTRICTS = [
    "Ariyalur", "Chengalpattu", "Chennai", "Coimbatore", "Cuddalore",
    "Dharmapuri", "Dindigul", "Erode", "Kallakurichi", "Kancheepuram",
    "Karur", "Krishnagiri", "Madurai", "Mayiladuthurai", "Nagapattinam",
    "Namakkal", "Nilgiris", "Perambalur", "Pudukkottai", "Ramanathapuram",
    "Ranipet", "Salem", "Sivaganga", "Tenkasi", "Thanjavur",
    "Theni", "Thoothukudi", "Tiruchirappalli", "Tirunelveli", "Tirupathur",
    "Tiruppur", "Tiruvallur", "Tiruvannamalai", "Tiruvarur", "Vellore",
    "Viluppuram", "Virudhunagar"
]

# Department Configuration
DEPARTMENTS = {
    "Roads": {
        "name": "Roads",
        "description": "Road maintenance, potholes, traffic signals, street infrastructure",
        "keywords": ["road", "pothole", "traffic", "signal", "street", "pavement", "highway", "bridge"]
    },
    "Sanitation": {
        "name": "Sanitation", 
        "description": "Garbage collection, waste management, cleanliness, drainage",
        "keywords": ["garbage", "waste", "trash", "cleaning", "sanitation", "drain", "sewer", "toilet"]
    },
    "Electricity": {
        "name": "Electricity",
        "description": "Street lights, power supply, electrical infrastructure",
        "keywords": ["light", "electricity", "power", "wire", "transformer", "pole", "cable", "outage"]
    },
    "Public Safety": {
        "name": "Public Safety",
        "description": "Safety concerns, emergencies, security issues, public order",
        "keywords": ["safety", "emergency", "security", "crime", "accident", "fire", "police", "danger"]
    }
}

# Urgency Levels
URGENCY_LEVELS = ["Low", "Medium", "High"]

# Complaint Status Options
COMPLAINT_STATUS = [
    "Pending",      # Initial status
    "Assigned",     # Assigned to department officer
    "In Progress",  # Officer working on it
    "Resolved",     # Issue resolved
    "Closed",       # Complaint closed (with/without resolution)
    "Escalated"     # Escalated to admin
]

# SLA Configuration (in hours)
SLA_RULES = {
    "High": 24,      # 24 hours for high priority
    "Medium": 72,    # 3 days for medium priority  
    "Low": 168       # 7 days for low priority
}

# Emergency Keywords (Auto-escalate to High priority)
EMERGENCY_KEYWORDS = [
    "emergency", "urgent", "immediate", "danger", "dangerous", "critical",
    "fire", "accident", "flood", "flooding", "burst", "leak", "gas",
    "explosion", "injured", "hurt", "bleeding", "unconscious", "trapped",
    "collapse", "sparking", "shock", "electrocution", "fallen", "blocking",
    "contaminated", "poisonous", "toxic", "disease", "illness", "outbreak"
]

# Nearby Emergency Places (for urgency calculation)
EMERGENCY_PLACES = [
    "Hospital", "Clinic", "Medical Center", "Emergency Room",
    "School", "College", "University", "Kindergarten", "Daycare",
    "Police Station", "Police Post", "Security Office",
    "Fire Station", "Fire Department", "Emergency Services",
    "Government Office", "Municipal Office", "Collectorate",
    "Bus Station", "Railway Station", "Airport", "Metro Station"
]

# File Upload Configuration
UPLOAD_CONFIG = {
    "max_file_size": 200 * 1024 * 1024,  # 200MB
    "allowed_image_types": [".jpg", ".jpeg", ".png", ".gif", ".webp"],
    "allowed_video_types": [".mp4", ".avi", ".mov", ".wmv"],
    "upload_directory": "assets/uploads",
    "thumbnail_size": (300, 300)
}

# Notification Types
NOTIFICATION_TYPES = {
    "complaint_update": "Complaint Status Updated",
    "assignment": "Complaint Assigned",
    "escalation": "Complaint Escalated", 
    "resolution": "Complaint Resolved",
    "feedback_request": "Feedback Requested",
    "sla_warning": "SLA Deadline Warning"
}

# User Roles
USER_ROLES = {
    "citizen": {
        "name": "Citizen",
        "permissions": ["submit_complaint", "view_own_complaints", "give_feedback", "review_complaints"]
    },
    "department_officer": {
        "name": "Department Officer", 
        "permissions": ["view_assigned_complaints", "update_status", "change_urgency", "add_notes", "request_reroute"]
    },
    "admin": {
        "name": "Administrator",
        "permissions": ["view_all_complaints", "approve_reroutes", "merge_complaints", "escalate", "warn_departments", "override_decisions"]
    }
}

# AI Model Configuration
AI_MODEL_CONFIG = {
    "department_model": {
        "model_path": "ai_models/department_model/model.pkl",
        "vectorizer_path": "ai_models/department_model/vectorizer.pkl",
        "retrain_threshold": 50,  # Retrain after 50 new complaints
        "confidence_threshold": 0.7
    },
    "urgency_model": {
        "model_path": "ai_models/urgency_model/model.pkl", 
        "vectorizer_path": "ai_models/urgency_model/vectorizer.pkl",
        "retrain_threshold": 100,  # Retrain after 100 new complaints
        "confidence_threshold": 0.6
    }
}

# Security Configuration
SECURITY_CONFIG = {
    "password_min_length": 8,
    "password_require_uppercase": True,
    "password_require_lowercase": True, 
    "password_require_numbers": True,
    "password_require_special": False,
    "session_timeout": 3600,  # 1 hour in seconds
    "max_login_attempts": 5,
    "lockout_duration": 900   # 15 minutes in seconds
}

# Dashboard Configuration
DASHBOARD_CONFIG = {
    "complaints_per_page": 20,
    "recent_complaints_limit": 10,
    "chart_colors": {
        "High": "#dc3545",    # Red
        "Medium": "#ffc107",  # Yellow
        "Low": "#28a745"      # Green
    },
    "status_colors": {
        "Pending": "#6c757d",     # Gray
        "Assigned": "#17a2b8",    # Cyan
        "In Progress": "#fd7e14", # Orange
        "Resolved": "#28a745",    # Green
        "Closed": "#6f42c1",      # Purple
        "Escalated": "#dc3545"    # Red
    }
}

# API Configuration (for future extensions)
API_CONFIG = {
    "rate_limit": 100,  # requests per minute
    "api_version": "v1",
    "enable_cors": True,
    "cors_origins": ["http://localhost:8501"]
}

# Logging Configuration
LOGGING_CONFIG = {
    "log_level": "INFO",
    "log_file": "logs/civiceye.log",
    "max_log_size": 10 * 1024 * 1024,  # 10MB
    "backup_count": 5,
    "log_format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
}

# System Messages
SYSTEM_MESSAGES = {
    "welcome": "Welcome to CIVICEYE - Smart City Complaint Management Platform",
    "complaint_submitted": "Your complaint has been submitted successfully. You will receive updates via notifications.",
    "complaint_resolved": "Your complaint has been resolved. Please provide feedback to help us improve.",
    "sla_warning": "SLA deadline is approaching for complaint #{complaint_id}",
    "emergency_detected": "Emergency situation detected. Complaint escalated to high priority.",
    "department_assigned": "Complaint has been assigned to {department} department.",
    "status_updated": "Complaint status updated to {status}",
    "feedback_requested": "Please provide feedback on the resolution of complaint #{complaint_id}"
}

# Error Messages
ERROR_MESSAGES = {
    "invalid_credentials": "Invalid mobile number or password",
    "account_locked": "Account temporarily locked due to multiple failed login attempts",
    "complaint_not_found": "Complaint not found or access denied",
    "file_too_large": "File size exceeds maximum limit of 200MB",
    "invalid_file_type": "Invalid file type. Please upload images or videos only",
    "database_error": "Database error occurred. Please try again later",
    "permission_denied": "You don't have permission to perform this action",
    "invalid_input": "Invalid input provided. Please check your data",
    "system_maintenance": "System is under maintenance. Please try again later"
}

# Success Messages  
SUCCESS_MESSAGES = {
    "account_created": "Account created successfully. You can now login",
    "complaint_submitted": "Complaint submitted successfully. Tracking ID: #{complaint_id}",
    "status_updated": "Complaint status updated successfully",
    "feedback_submitted": "Thank you for your feedback",
    "profile_updated": "Profile updated successfully",
    "password_changed": "Password changed successfully"
}

# Validation Rules
VALIDATION_RULES = {
    "mobile_number": {
        "pattern": r"^[6-9]\d{9}$",
        "message": "Please enter a valid 10-digit mobile number starting with 6, 7, 8, or 9"
    },
    "officer_id": {
        "pattern": r"^[A-Z]{2,4}\d{4,6}$", 
        "message": "Officer ID should be 2-4 letters followed by 4-6 digits (e.g., RD001234)"
    },
    "admin_id": {
        "pattern": r"^ADM\d{4,6}$",
        "message": "Admin ID should start with 'ADM' followed by 4-6 digits (e.g., ADM001234)"
    },
    "complaint_title": {
        "min_length": 10,
        "max_length": 200,
        "message": "Complaint title should be between 10-200 characters"
    },
    "complaint_description": {
        "min_length": 20,
        "max_length": 2000,
        "message": "Complaint description should be between 20-2000 characters"
    }
}

# Default Admin Account (for initial setup)
DEFAULT_ADMIN = {
    "admin_id": "ADM000001",
    "password": "Admin@123",
    "name": "System Administrator",
    "email": "admin@civiceye.gov.in"
}

# Default Department Officers (for testing)
DEFAULT_OFFICERS = [
    {
        "officer_id": "RD001",
        "password": "Roads@123", 
        "name": "Roads Department Officer",
        "department": "Roads",
        "email": "roads@civiceye.gov.in"
    },
    {
        "officer_id": "SN001",
        "password": "Sanitation@123",
        "name": "Sanitation Department Officer", 
        "department": "Sanitation",
        "email": "sanitation@civiceye.gov.in"
    },
    {
        "officer_id": "EL001",
        "password": "Electricity@123",
        "name": "Electricity Department Officer",
        "department": "Electricity", 
        "email": "electricity@civiceye.gov.in"
    },
    {
        "officer_id": "PS001",
        "password": "Safety@123",
        "name": "Public Safety Officer",
        "department": "Public Safety",
        "email": "safety@civiceye.gov.in"
    }
]