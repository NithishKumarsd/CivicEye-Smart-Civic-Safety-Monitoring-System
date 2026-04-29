-- Complaint Departments Junction Table
-- Supports multi-department assignment for escalated complaints

CREATE TABLE IF NOT EXISTS complaint_departments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    complaint_id INTEGER NOT NULL,
    department_id INTEGER NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('PRIMARY', 'SECONDARY')),
    assigned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    assigned_by INTEGER, -- admin_id who assigned
    FOREIGN KEY (complaint_id) REFERENCES complaints (id) ON DELETE CASCADE,
    FOREIGN KEY (department_id) REFERENCES departments (id),
    FOREIGN KEY (assigned_by) REFERENCES admins (id),
    UNIQUE(complaint_id, department_id) -- Prevent duplicate assignments
);

-- Index for performance
CREATE INDEX IF NOT EXISTS idx_complaint_departments_complaint ON complaint_departments(complaint_id);
CREATE INDEX IF NOT EXISTS idx_complaint_departments_department ON complaint_departments(department_id);