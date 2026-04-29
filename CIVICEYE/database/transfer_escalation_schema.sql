-- Transfer and Escalation Tables

CREATE TABLE IF NOT EXISTS transfer_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    complaint_id INTEGER NOT NULL,
    from_department_id INTEGER NOT NULL,
    to_department_id INTEGER NOT NULL,
    officer_id INTEGER NOT NULL,
    reason TEXT NOT NULL,
    status TEXT DEFAULT 'PENDING',
    processed_by INTEGER,
    processed_at TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (complaint_id) REFERENCES complaints(id),
    FOREIGN KEY (from_department_id) REFERENCES departments(id),
    FOREIGN KEY (to_department_id) REFERENCES departments(id),
    FOREIGN KEY (officer_id) REFERENCES department_officers(id),
    FOREIGN KEY (processed_by) REFERENCES admins(id)
);

CREATE TABLE IF NOT EXISTS escalations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    complaint_id INTEGER NOT NULL,
    department_id INTEGER NOT NULL,
    officer_id INTEGER NOT NULL,
    reason TEXT NOT NULL,
    urgency TEXT NOT NULL,
    status TEXT DEFAULT 'ESCALATED',
    created_at TEXT NOT NULL,
    FOREIGN KEY (complaint_id) REFERENCES complaints(id),
    FOREIGN KEY (department_id) REFERENCES departments(id),
    FOREIGN KEY (officer_id) REFERENCES department_officers(id)
);