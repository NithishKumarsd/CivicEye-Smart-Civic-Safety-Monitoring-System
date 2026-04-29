"""
CIVICEYE - Smart City Complaint Management Platform
Main Application Entry Point

Professional, Production-Grade Civic Complaint Management System
Built with Streamlit, SQLite, and AI-Powered Routing
"""

import streamlit as st
import sys
import os
from datetime import datetime

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import core modules
from database.db import db
from utils.security import session_manager
from utils.constants import SYSTEM_MESSAGES, DEFAULT_ADMIN, DEFAULT_OFFICERS

# Import frontend modules
from frontend.home import show_home_page
from frontend.login import show_login_page
from frontend.register import show_register_page
from frontend.user_dashboard import show_user_dashboard
from frontend.department_dashboard import show_department_dashboard
from frontend.admin_dashboard import show_admin_dashboard

# Configure Streamlit page
st.set_page_config(
    page_title="CIVICEYE - Smart City Platform",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/civiceye/help',
        'Report a bug': 'https://github.com/civiceye/issues',
        'About': "CIVICEYE - Professional Civic Complaint Management Platform"
    }
)

# Custom CSS for professional styling
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary-color: #2E86AB;
        --secondary-color: #A23B72;
        --accent-color: #F18F01;
        --success-color: #C73E1D;
        --background-color: #F5F7FA;
        --text-color: #2C3E50;
        --border-color: #E1E8ED;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom header styling */
    .main-header {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
        font-weight: 700;
    }
    
    .main-header p {
        font-size: 1.2rem;
        opacity: 0.9;
        margin: 0;
    }
    
    /* Card styling */
    .info-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border-left: 5px solid var(--primary-color);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .info-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(0,0,0,0.15);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(45deg, var(--primary-color), var(--secondary-color));
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, var(--primary-color) 0%, var(--secondary-color) 100%);
    }
    
    /* Metrics styling */
    .metric-container {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 3px 10px rgba(0,0,0,0.1);
        border-top: 4px solid var(--accent-color);
    }
    
    /* Status badges */
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 0.25rem;
    }
    
    .status-pending { background: #fff3cd; color: #856404; }
    .status-assigned { background: #d1ecf1; color: #0c5460; }
    .status-progress { background: #ffeaa7; color: #6c5ce7; }
    .status-resolved { background: #d4edda; color: #155724; }
    .status-escalated { background: #f8d7da; color: #721c24; }
    
    /* Urgency badges */
    .urgency-high { background: #f8d7da; color: #721c24; border: 2px solid #dc3545; }
    .urgency-medium { background: #fff3cd; color: #856404; border: 2px solid #ffc107; }
    .urgency-low { background: #d4edda; color: #155724; border: 2px solid #28a745; }
    
    /* Form styling */
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 2px solid var(--border-color);
        padding: 0.75rem;
    }
    
    .stTextArea > div > div > textarea {
        border-radius: 10px;
        border: 2px solid var(--border-color);
        padding: 0.75rem;
    }
    
    .stSelectbox > div > div > select {
        border-radius: 10px;
        border: 2px solid var(--border-color);
        padding: 0.75rem;
    }
    
    /* Alert styling */
    .alert-success {
        background: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #28a745;
        margin: 1rem 0;
    }
    
    .alert-warning {
        background: #fff3cd;
        color: #856404;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #ffc107;
        margin: 1rem 0;
    }
    
    .alert-error {
        background: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #dc3545;
        margin: 1rem 0;
    }
    
    /* Loading animation */
    .loading-spinner {
        border: 4px solid #f3f3f3;
        border-top: 4px solid var(--primary-color);
        border-radius: 50%;
        width: 40px;
        height: 40px;
        animation: spin 1s linear infinite;
        margin: 20px auto;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 2rem;
        }
        
        .main-header p {
            font-size: 1rem;
        }
        
        .info-card {
            padding: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)

def initialize_system():
    """Initialize the CIVICEYE system"""
    try:
        # Initialize database
        db.init_database()
        
        # Create default admin if not exists
        admin_data = db.authenticate_admin(DEFAULT_ADMIN['admin_id'], DEFAULT_ADMIN['password'])
        if not admin_data:
            admin_id = db.create_admin(
                admin_id=DEFAULT_ADMIN['admin_id'],
                password=DEFAULT_ADMIN['password'],
                name=DEFAULT_ADMIN['name'],
                email=DEFAULT_ADMIN['email']
            )
            if admin_id:
                print(f"✅ Default admin created: {DEFAULT_ADMIN['admin_id']}")
        
        # Create default department officers if not exist
        for officer in DEFAULT_OFFICERS:
            officer_data = db.authenticate_officer(officer['officer_id'], officer['password'])
            if not officer_data:
                officer_id = db.create_department_officer(
                    officer_id=officer['officer_id'],
                    password=officer['password'],
                    name=officer['name'],
                    department_name=officer['department'],
                    email=officer['email']
                )
                if officer_id:
                    print(f"✅ Default officer created: {officer['officer_id']} ({officer['department']})")
        
        return True
        
    except Exception as e:
        st.error(f"❌ System initialization failed: {e}")
        return False

def show_sidebar():
    """Display sidebar navigation"""
    with st.sidebar:
        st.markdown("### 🏙️ **CIVICEYE**")
        st.markdown("*Smart City Platform*")
        st.markdown("---")
        
        # Show user info if authenticated
        if session_manager.is_session_valid():
            user_data = session_manager.get_current_user()
            user_type = session_manager.get_user_type()
            
            if user_data:
                st.success(f"👋 Welcome!")
                
                if user_type == 'citizen':
                    st.info(f"📱 {user_data.get('mobile_number', 'N/A')}")
                    st.info(f"📍 {user_data.get('district', 'N/A')}")
                elif user_type == 'department_officer':
                    st.info(f"👮 {user_data.get('name', 'Officer')}")
                    st.info(f"🏢 {user_data.get('department_name', 'N/A')}")
                elif user_type == 'admin':
                    st.info(f"👑 {user_data.get('name', 'Administrator')}")
                    st.info(f"🆔 {user_data.get('admin_id', 'N/A')}")
                
                st.markdown("---")
                
                # Logout button
                if st.button("🚪 Logout", key="logout_btn", use_container_width=True):
                    session_manager.destroy_session()
                    st.rerun()
        else:
            st.info("Please login to access your dashboard")
        
        st.markdown("---")
        
        # Navigation buttons
        if st.button("🏠 Home", key="nav_home", use_container_width=True):
            st.session_state.page = 'home'
            st.rerun()
        
        if not session_manager.is_session_valid():
            if st.button("🔑 Login", key="nav_login", use_container_width=True):
                st.session_state.page = 'login'
                st.rerun()
            
            if st.button("📝 Register", key="nav_register", use_container_width=True):
                st.session_state.page = 'register'
                st.rerun()
        
        # System info
        st.markdown("---")
        st.markdown("### 📊 **System Info**")
        
        try:
            conn = db.get_connection()
            cursor = conn.cursor()
            
            # Get basic stats
            cursor.execute("SELECT COUNT(*) FROM complaints")
            total_complaints = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM users")
            total_users = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM complaints WHERE status = 'Resolved'")
            resolved_complaints = cursor.fetchone()[0]
            
            conn.close()
            
            st.metric("Total Complaints", total_complaints)
            st.metric("Registered Users", total_users)
            st.metric("Resolved Issues", resolved_complaints)
            
            if total_complaints > 0:
                resolution_rate = (resolved_complaints / total_complaints) * 100
                st.metric("Resolution Rate", f"{resolution_rate:.1f}%")
            
        except Exception as e:
            st.warning("Stats unavailable")
        
        # Footer
        st.markdown("---")
        st.markdown("""
        <div style='text-align: center; color: #666; font-size: 0.8rem;'>
            <p>CIVICEYE v1.0<br>
            Professional Civic Platform<br>
            © 2024 Smart City Initiative</p>
        </div>
        """, unsafe_allow_html=True)

def main():
    """Main application logic with routing"""
    
    # Initialize system on first run
    if 'system_initialized' not in st.session_state:
        with st.spinner("🚀 Initializing CIVICEYE System..."):
            if initialize_system():
                st.session_state.system_initialized = True
                st.success("✅ System initialized successfully!")
            else:
                st.error("❌ System initialization failed!")
                st.stop()
    
    # Initialize session state
    if 'page' not in st.session_state:
        st.session_state.page = 'home'
    
    # Show sidebar
    show_sidebar()
    
    # Main content routing
    try:
        if st.session_state.page == 'home':
            show_home_page()
        
        elif st.session_state.page == 'login':
            show_login_page()
        
        elif st.session_state.page == 'register':
            show_register_page()
        
        elif st.session_state.page == 'user_dashboard':
            if session_manager.is_session_valid() and session_manager.get_user_type() == 'citizen':
                show_user_dashboard()
            else:
                st.error("🔒 Access denied. Please login as a citizen.")
                st.session_state.page = 'login'
                st.rerun()
        
        elif st.session_state.page == 'department_dashboard':
            if session_manager.is_session_valid() and session_manager.get_user_type() == 'department_officer':
                show_department_dashboard()
            else:
                st.error("🔒 Access denied. Please login as a department officer.")
                st.session_state.page = 'login'
                st.rerun()
        
        elif st.session_state.page == 'admin_dashboard':
            if session_manager.is_session_valid() and session_manager.get_user_type() == 'admin':
                show_admin_dashboard()
            else:
                st.error("🔒 Access denied. Please login as an administrator.")
                st.session_state.page = 'login'
                st.rerun()
        
        else:
            st.error("🚫 Page not found")
            st.session_state.page = 'home'
            st.rerun()
    
    except Exception as e:
        st.error(f"❌ Application error: {e}")
        st.error("Please refresh the page or contact support if the problem persists.")
        
        # Show error details in expander for debugging
        with st.expander("🔍 Error Details (for developers)"):
            st.exception(e)

if __name__ == "__main__":
    main()