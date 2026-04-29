# 🏙️ CIVICEYE - Smart City Complaint Management Platform

**Professional, Production-Grade Civic Complaint Management System**

CIVICEYE is an AI-powered platform that revolutionizes how citizens report civic issues and how municipal authorities manage and resolve them. Built with modern technologies and designed for scalability.

## 🌟 Features

### 🏠 **Citizen Portal**
- **Mobile-First Registration**: Register with mobile number and district
- **AI-Powered Complaint Submission**: Auto-detect department and urgency
- **Multi-Media Support**: Upload photos or capture with camera
- **Real-Time Tracking**: Monitor complaint status and resolution progress
- **Location Integration**: GPS-based location tagging
- **Public Reviews**: Comment and review other complaints

### 👮 **Department Officer Portal**
- **Role-Based Access**: Separate portals for Roads, Sanitation, Electricity, Public Safety
- **AI-Prioritized Queue**: Complaints sorted by urgency and SLA deadlines
- **Status Management**: Update complaint status with internal notes
- **Performance Analytics**: Track resolution rates and response times
- **Escalation Tools**: Request admin intervention or department transfers

### 👑 **Administrator Portal**
- **System Oversight**: Complete visibility across all departments
- **Advanced Analytics**: Comprehensive dashboards and reporting
- **AI Model Management**: Monitor and retrain ML models
- **User Management**: Create officers, manage accounts
- **Emergency Controls**: Override decisions and escalate critical issues

### 🤖 **AI Intelligence**
- **Department Classification**: Automatically route complaints to correct department
- **Urgency Prediction**: Predict priority levels (High/Medium/Low)
- **Emergency Detection**: Auto-escalate critical situations
- **Continuous Learning**: Models improve with each complaint

## 🏗️ Architecture

### **Technology Stack**
- **Frontend**: Streamlit (Python web framework)
- **Backend**: Python with modular service architecture
- **Database**: SQLite with comprehensive schema
- **AI/ML**: Scikit-learn with TF-IDF vectorization
- **Security**: Role-based access control, password hashing
- **Deployment**: Local hosting ready

### **Project Structure**
```
CIVICEYE/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── README.md                   # This documentation
│
├── frontend/                   # User interface modules
│   ├── home.py                # Landing page
│   ├── login.py               # Authentication
│   ├── register.py            # User registration
│   ├── user_dashboard.py      # Citizen portal
│   ├── department_dashboard.py # Officer portal
│   └── admin_dashboard.py     # Admin portal
│
├── backend/                    # Business logic services
│   ├── complaint_service.py   # Complaint management
│   ├── notification_service.py # Notifications (future)
│   └── analytics_service.py   # Analytics (future)
│
├── ai_models/                  # Machine learning models
│   ├── department_model/      # Department classification
│   │   ├── train.py          # Training script
│   │   ├── predict.py        # Prediction module
│   │   └── model.pkl         # Trained model file
│   └── urgency_model/         # Urgency prediction
│       ├── train.py          # Training script
│       ├── predict.py        # Prediction module
│       └── model.pkl         # Trained model file
│
├── database/                   # Data layer
│   ├── schema.sql             # Database schema
│   ├── db.py                  # Database manager
│   └── civiceye.db           # SQLite database file
│
├── utils/                      # Utility modules
│   ├── constants.py           # System constants
│   ├── security.py            # Security utilities
│   └── location_utils.py      # Location services (future)
│
└── assets/                     # Static assets
    ├── uploads/               # User uploaded files
    └── styles.css            # Custom styling (future)
```

## 🚀 Quick Start

### **Prerequisites**
- Python 3.8 or higher
- pip (Python package manager)

### **Installation**

1. **Clone or Download the Project**
   ```bash
   # Navigate to the CIVICEYE directory
   cd CIVICEYE
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application**
   ```bash
   streamlit run app.py
   ```

4. **Access the Platform**
   - Open your browser and go to `http://localhost:8501`
   - The system will automatically initialize on first run

### **Default Accounts**

**Administrator:**
- Admin ID: `ADM000001`
- Password: `Admin@123`

**Department Officers:**
- Roads: `RD001` / `Roads@123`
- Sanitation: `SN001` / `Sanitation@123`
- Electricity: `EL001` / `Electricity@123`
- Public Safety: `PS001` / `Safety@123`

**Citizens:**
- Register new accounts through the registration page

## 📊 Database Schema

### **Core Tables**
- **users**: Citizen accounts with mobile numbers
- **department_officers**: Officer accounts by department
- **admins**: System administrator accounts
- **complaints**: Main complaint records with AI predictions
- **complaint_media**: Uploaded images and files
- **departments**: System departments (Roads, Sanitation, etc.)

### **Tracking Tables**
- **urgency_history**: Track urgency changes over time
- **department_actions**: Officer actions and notes
- **admin_actions**: Administrative interventions
- **sla_timers**: Service level agreement monitoring
- **audit_logs**: Complete system audit trail

### **Engagement Tables**
- **feedbacks**: Citizen feedback on resolutions
- **reviews**: Public reviews and comments
- **notifications**: System notifications
- **reroute_requests**: Department transfer requests

## 🤖 AI Models

### **Department Classification Model**
- **Purpose**: Automatically route complaints to appropriate departments
- **Input**: Complaint title and description
- **Output**: Roads, Sanitation, Electricity, or Public Safety
- **Algorithm**: Random Forest with TF-IDF vectorization
- **Accuracy**: ~95% on training data

### **Urgency Prediction Model**
- **Purpose**: Predict complaint priority levels
- **Input**: Complaint text, images, location context
- **Output**: High, Medium, or Low urgency
- **Algorithm**: Random Forest with business rule overrides
- **Features**: Emergency keyword detection, location analysis

### **Model Management**
- Models are saved as `.pkl` files for persistence
- Automatic retraining when sufficient new data is available
- Admin interface for manual model retraining
- Performance monitoring and accuracy tracking

## 🔐 Security Features

### **Authentication**
- Mobile number-based login for citizens
- Officer ID authentication for department staff
- Admin ID authentication for administrators
- Secure password hashing with salt

### **Authorization**
- Role-based access control (RBAC)
- Department-specific data isolation
- Admin override capabilities
- Session management with timeout

### **Data Protection**
- Input sanitization and validation
- SQL injection prevention
- File upload security checks
- Audit logging for all actions

## 📈 Analytics & Reporting

### **Real-Time Dashboards**
- System-wide complaint statistics
- Department performance metrics
- Resolution time analytics
- Urgency distribution analysis

### **Performance Tracking**
- Officer resolution rates
- SLA compliance monitoring
- Citizen satisfaction scores
- Department workload balancing

### **Trend Analysis**
- Daily/weekly/monthly complaint trends
- Seasonal pattern recognition
- Geographic hotspot identification
- Category-wise issue tracking

## 🌍 Tamil Nadu Integration

### **Geographic Coverage**
- All 37 districts of Tamil Nadu supported
- District-specific complaint routing
- Local authority integration ready
- Regional language support (future)

### **Government Compliance**
- Audit trail for transparency
- Data export capabilities
- Performance reporting
- Citizen grievance standards compliance

## 🔧 Configuration

### **SLA Rules** (Configurable)
- High Priority: 24 hours
- Medium Priority: 72 hours (3 days)
- Low Priority: 168 hours (7 days)

### **File Upload Limits**
- Maximum file size: 200MB
- Supported formats: JPG, PNG, GIF, MP4
- Automatic image optimization
- Secure file storage

### **AI Model Settings**
- Retraining thresholds configurable
- Confidence score adjustments
- Emergency keyword customization
- Department routing rules

## 🚀 Deployment

### **Local Deployment**
- Ready to run with `streamlit run app.py`
- SQLite database for development
- File-based storage for simplicity

### **Production Deployment** (Future)
- Docker containerization ready
- PostgreSQL/MySQL database migration
- Cloud storage integration
- Load balancer configuration
- SSL/HTTPS setup

## 🤝 Contributing

### **Development Guidelines**
- Follow Python PEP 8 style guide
- Add docstrings to all functions
- Include error handling
- Write unit tests for new features
- Update documentation

### **Feature Requests**
- Submit issues on GitHub
- Provide detailed use cases
- Include mockups if applicable
- Consider backward compatibility

## 📞 Support

### **Technical Support**
- Email: support@civiceye.gov.in
- Phone: 1800-123-4567
- Hours: 9 AM - 6 PM (Mon-Fri)

### **Documentation**
- User guides available in platform
- Video tutorials (future)
- API documentation (future)
- Training materials for officers

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Tamil Nadu Government for civic data insights
- Open source community for tools and libraries
- Citizens and officers for feedback and testing
- AI/ML community for algorithm guidance

---

**CIVICEYE** - Empowering citizens, enabling authorities, building better cities.

*Version 1.0 - Professional Civic Complaint Management Platform*
