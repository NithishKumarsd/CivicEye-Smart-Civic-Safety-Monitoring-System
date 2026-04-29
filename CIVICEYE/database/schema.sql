-- CIVICEYE Database Schema
-- Professional Civic Complaint Management System

-- Users table (Citizens)
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mobile_number TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    district TEXT NOT NULL,
    location_permission BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME,
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'suspended', 'deleted'))
);

-- Roles table
CREATE TABLE IF NOT EXISTS roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role_name TEXT UNIQUE NOT NULL CHECK (role_name IN ('citizen', 'department_officer', 'admin')),
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Departments table
CREATE TABLE IF NOT EXISTS departments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL CHECK (name IN ('Roads', 'Sanitation', 'Electricity', 'Public Safety')),
    description TEXT,
    head_officer_id INTEGER,
    contact_email TEXT,
    contact_phone TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'inactive'))
);

-- Department Officers table
CREATE TABLE IF NOT EXISTS department_officers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    officer_id TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    name TEXT NOT NULL,
    department_id INTEGER NOT NULL,
    email TEXT,
    phone TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME,
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'suspended', 'deleted')),
    FOREIGN KEY (department_id) REFERENCES departments (id)
);

-- Admin table
CREATE TABLE IF NOT EXISTS admins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    admin_id TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME,
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'suspended'))
);

-- Locations table (Tamil Nadu Districts)
CREATE TABLE IF NOT EXISTS locations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    district_name TEXT UNIQUE NOT NULL,
    state TEXT DEFAULT 'Tamil Nadu',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Complaints table
CREATE TABLE IF NOT EXISTS complaints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    category TEXT CHECK (category IN ('Roads', 'Sanitation', 'Electricity', 'Public Safety')),
    department_id INTEGER,
    auto_detected BOOLEAN DEFAULT FALSE,
    location_address TEXT NOT NULL,
    district TEXT NOT NULL,
    latitude REAL,
    longitude REAL,
    nearby_emergency_places TEXT, -- JSON array of nearby places
    urgency_level TEXT NOT NULL CHECK (urgency_level IN ('Low', 'Medium', 'High')),
    ai_predicted_urgency TEXT CHECK (ai_predicted_urgency IN ('Low', 'Medium', 'High')),
    status TEXT DEFAULT 'Pending' CHECK (status IN ('Pending', 'Assigned', 'In Progress', 'Resolved', 'Closed', 'Escalated')),
    assigned_officer_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    resolved_at DATETIME,
    sla_deadline DATETIME,
    emergency_flag BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (department_id) REFERENCES departments (id),
    FOREIGN KEY (assigned_officer_id) REFERENCES department_officers (id)
);

-- Complaint Media table (Images/Videos)
CREATE TABLE IF NOT EXISTS complaint_media (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    complaint_id INTEGER NOT NULL,
    media_type TEXT NOT NULL CHECK (media_type IN ('image', 'video')),
    file_path TEXT NOT NULL,
    file_size INTEGER,
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (complaint_id) REFERENCES complaints (id) ON DELETE CASCADE
);

-- Urgency History table (Track urgency changes)
CREATE TABLE IF NOT EXISTS urgency_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    complaint_id INTEGER NOT NULL,
    old_urgency TEXT,
    new_urgency TEXT NOT NULL,
    changed_by_type TEXT NOT NULL CHECK (changed_by_type IN ('ai', 'department', 'admin')),
    changed_by_id INTEGER,
    reason TEXT,
    changed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (complaint_id) REFERENCES complaints (id) ON DELETE CASCADE
);

-- Department Actions table
CREATE TABLE IF NOT EXISTS department_actions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    complaint_id INTEGER NOT NULL,
    officer_id INTEGER NOT NULL,
    action_type TEXT NOT NULL CHECK (action_type IN ('assigned', 'status_change', 'urgency_change', 'note_added', 'resolved', 'reroute_request')),
    action_details TEXT,
    internal_notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (complaint_id) REFERENCES complaints (id) ON DELETE CASCADE,
    FOREIGN KEY (officer_id) REFERENCES department_officers (id)
);

-- Admin Actions table
CREATE TABLE IF NOT EXISTS admin_actions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    admin_id INTEGER NOT NULL,
    action_type TEXT NOT NULL CHECK (action_type IN ('reroute_approved', 'reroute_denied', 'merge_complaints', 'escalate_urgency', 'warn_department', 'freeze_department', 'override_decision')),
    target_type TEXT NOT NULL CHECK (target_type IN ('complaint', 'department', 'officer')),
    target_id INTEGER NOT NULL,
    action_details TEXT,
    reason TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (admin_id) REFERENCES admins (id)
);

-- Feedbacks table (User feedback after resolution)
CREATE TABLE IF NOT EXISTS feedbacks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    complaint_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    feedback_text TEXT,
    resolution_satisfaction TEXT CHECK (resolution_satisfaction IN ('Very Satisfied', 'Satisfied', 'Neutral', 'Dissatisfied', 'Very Dissatisfied')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (complaint_id) REFERENCES complaints (id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Reviews table (Public reviews on complaints)
CREATE TABLE IF NOT EXISTS reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    complaint_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    review_type TEXT NOT NULL CHECK (review_type IN ('same_issue', 'comment', 'support')),
    review_text TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (complaint_id) REFERENCES complaints (id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Notifications table
CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipient_type TEXT NOT NULL CHECK (recipient_type IN ('user', 'officer', 'admin')),
    recipient_id INTEGER NOT NULL,
    notification_type TEXT NOT NULL CHECK (notification_type IN ('complaint_update', 'assignment', 'escalation', 'resolution', 'feedback_request', 'sla_warning')),
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    complaint_id INTEGER,
    is_read BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (complaint_id) REFERENCES complaints (id) ON DELETE SET NULL
);

-- Reroute Requests table
CREATE TABLE IF NOT EXISTS reroute_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    complaint_id INTEGER NOT NULL,
    from_department_id INTEGER NOT NULL,
    to_department_id INTEGER,
    requested_by_officer_id INTEGER NOT NULL,
    reason TEXT NOT NULL,
    status TEXT DEFAULT 'Pending' CHECK (status IN ('Pending', 'Approved', 'Denied')),
    admin_response TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    processed_at DATETIME,
    processed_by_admin_id INTEGER,
    FOREIGN KEY (complaint_id) REFERENCES complaints (id) ON DELETE CASCADE,
    FOREIGN KEY (from_department_id) REFERENCES departments (id),
    FOREIGN KEY (to_department_id) REFERENCES departments (id),
    FOREIGN KEY (requested_by_officer_id) REFERENCES department_officers (id),
    FOREIGN KEY (processed_by_admin_id) REFERENCES admins (id)
);

-- Merge Requests table
CREATE TABLE IF NOT EXISTS merge_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    primary_complaint_id INTEGER NOT NULL,
    secondary_complaint_id INTEGER NOT NULL,
    requested_by_officer_id INTEGER NOT NULL,
    reason TEXT NOT NULL,
    status TEXT DEFAULT 'Pending' CHECK (status IN ('Pending', 'Approved', 'Denied')),
    admin_response TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    processed_at DATETIME,
    processed_by_admin_id INTEGER,
    FOREIGN KEY (primary_complaint_id) REFERENCES complaints (id) ON DELETE CASCADE,
    FOREIGN KEY (secondary_complaint_id) REFERENCES complaints (id) ON DELETE CASCADE,
    FOREIGN KEY (requested_by_officer_id) REFERENCES department_officers (id),
    FOREIGN KEY (processed_by_admin_id) REFERENCES admins (id)
);

-- Emergency Flags table
CREATE TABLE IF NOT EXISTS emergency_flags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    complaint_id INTEGER NOT NULL,
    flagged_by_type TEXT NOT NULL CHECK (flagged_by_type IN ('ai', 'user', 'officer', 'admin')),
    flagged_by_id INTEGER,
    flag_reason TEXT NOT NULL,
    severity_level TEXT NOT NULL CHECK (severity_level IN ('Critical', 'High', 'Medium')),
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    resolved_at DATETIME,
    FOREIGN KEY (complaint_id) REFERENCES complaints (id) ON DELETE CASCADE
);

-- SLA Timers table
CREATE TABLE IF NOT EXISTS sla_timers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    complaint_id INTEGER NOT NULL,
    urgency_level TEXT NOT NULL,
    sla_hours INTEGER NOT NULL,
    start_time DATETIME NOT NULL,
    deadline DATETIME NOT NULL,
    paused_duration INTEGER DEFAULT 0, -- in minutes
    is_breached BOOLEAN DEFAULT FALSE,
    breach_time DATETIME,
    completed_at DATETIME,
    FOREIGN KEY (complaint_id) REFERENCES complaints (id) ON DELETE CASCADE
);

-- Audit Logs table
CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_type TEXT NOT NULL CHECK (user_type IN ('user', 'officer', 'admin', 'system')),
    user_id INTEGER,
    action TEXT NOT NULL,
    table_name TEXT,
    record_id INTEGER,
    old_values TEXT, -- JSON
    new_values TEXT, -- JSON
    ip_address TEXT,
    user_agent TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Insert Tamil Nadu Districts
INSERT OR IGNORE INTO locations (district_name) VALUES
('Ariyalur'), ('Chengalpattu'), ('Chennai'), ('Coimbatore'), ('Cuddalore'),
('Dharmapuri'), ('Dindigul'), ('Erode'), ('Kallakurichi'), ('Kancheepuram'),
('Karur'), ('Krishnagiri'), ('Madurai'), ('Mayiladuthurai'), ('Nagapattinam'),
('Namakkal'), ('Nilgiris'), ('Perambalur'), ('Pudukkottai'), ('Ramanathapuram'),
('Ranipet'), ('Salem'), ('Sivaganga'), ('Tenkasi'), ('Thanjavur'),
('Theni'), ('Thoothukudi'), ('Tiruchirappalli'), ('Tirunelveli'), ('Tirupathur'),
('Tiruppur'), ('Tiruvallur'), ('Tiruvannamalai'), ('Tiruvarur'), ('Vellore'),
('Viluppuram'), ('Virudhunagar');

-- Insert Roles
INSERT OR IGNORE INTO roles (role_name, description) VALUES
('citizen', 'Regular citizens who can submit complaints'),
('department_officer', 'Department officers who handle complaints'),
('admin', 'System administrators with full access');

-- Insert Departments
INSERT OR IGNORE INTO departments (name, description) VALUES
('Roads', 'Road maintenance, potholes, traffic signals'),
('Sanitation', 'Garbage collection, waste management, cleanliness'),
('Electricity', 'Street lights, power supply, electrical issues'),
('Public Safety', 'Safety concerns, emergencies, security issues');

-- Create Indexes for Performance
CREATE INDEX IF NOT EXISTS idx_complaints_user_id ON complaints(user_id);
CREATE INDEX IF NOT EXISTS idx_complaints_department_id ON complaints(department_id);
CREATE INDEX IF NOT EXISTS idx_complaints_status ON complaints(status);
CREATE INDEX IF NOT EXISTS idx_complaints_urgency ON complaints(urgency_level);
CREATE INDEX IF NOT EXISTS idx_complaints_created_at ON complaints(created_at);
CREATE INDEX IF NOT EXISTS idx_complaints_district ON complaints(district);
CREATE INDEX IF NOT EXISTS idx_complaints_sla_deadline ON complaints(sla_deadline);

CREATE INDEX IF NOT EXISTS idx_users_mobile ON users(mobile_number);
CREATE INDEX IF NOT EXISTS idx_users_district ON users(district);

CREATE INDEX IF NOT EXISTS idx_officers_department ON department_officers(department_id);
CREATE INDEX IF NOT EXISTS idx_officers_officer_id ON department_officers(officer_id);

CREATE INDEX IF NOT EXISTS idx_notifications_recipient ON notifications(recipient_type, recipient_id);
CREATE INDEX IF NOT EXISTS idx_notifications_unread ON notifications(is_read);

CREATE INDEX IF NOT EXISTS idx_audit_logs_user ON audit_logs(user_type, user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at);

CREATE INDEX IF NOT EXISTS idx_complaint_media_complaint ON complaint_media(complaint_id);
CREATE INDEX IF NOT EXISTS idx_urgency_history_complaint ON urgency_history(complaint_id);
CREATE INDEX IF NOT EXISTS idx_department_actions_complaint ON department_actions(complaint_id);
CREATE INDEX IF NOT EXISTS idx_feedbacks_complaint ON feedbacks(complaint_id);
CREATE INDEX IF NOT EXISTS idx_reviews_complaint ON reviews(complaint_id);