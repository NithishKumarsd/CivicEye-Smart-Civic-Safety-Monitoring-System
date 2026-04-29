"""
CIVICEYE Login Page
Role-based authentication for Citizens, Department Officers, and Administrators
"""

import streamlit as st
import time
from database.db import db
from utils.security import security_manager, session_manager
from utils.constants import ERROR_MESSAGES, SUCCESS_MESSAGES, DEFAULT_ADMIN, DEFAULT_OFFICERS

def show_login_page():
    """Display login page with role-based authentication"""
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🔑 Login to CIVICEYE</h1>
        <p>Access your dashboard based on your role</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Role selection tabs
    tab1, tab2, tab3 = st.tabs(["🏠 Citizen Login", "👮 Officer Login", "👑 Admin Login"])
    
    with tab1:
        show_citizen_login()
    
    with tab2:
        show_officer_login()
    
    with tab3:
        show_admin_login()
    
    # Help section
    show_login_help()

def show_citizen_login():
    """Display citizen login form"""
    st.markdown("### 🏠 **Citizen Portal Access**")
    st.markdown("Login with your registered mobile number and password.")
    
    with st.form("citizen_login_form"):
        col1, col2 = st.columns([1, 2])
        
        with col2:
            mobile_number = st.text_input(
                "📱 Mobile Number",
                placeholder="Enter your 10-digit mobile number",
                help="Use the mobile number you registered with",
                max_chars=10
            )
            
            password = st.text_input(
                "🔒 Password",
                type="password",
                placeholder="Enter your password",
                help="Enter your account password"
            )
            
            col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
            with col_btn2:
                login_btn = st.form_submit_button(
                    "🚀 Login as Citizen",
                    type="primary",
                    use_container_width=True
                )
        
        if login_btn:
            handle_citizen_login(mobile_number, password)
    
    # Registration link
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.info("Don't have an account?")
        if st.button("📝 Register as New Citizen", key="goto_register", use_container_width=True):
            st.session_state.page = 'register'
            st.rerun()

def show_officer_login():
    """Display department officer login form"""
    st.markdown("### 👮 **Department Officer Access**")
    st.markdown("Login with your official officer ID and password.")
    
    with st.form("officer_login_form"):
        col1, col2 = st.columns([1, 2])
        
        with col2:
            officer_id = st.text_input(
                "🆔 Officer ID",
                placeholder="e.g., RD001, SN001, EL001, PS001",
                help="Your official department officer ID"
            )
            
            password = st.text_input(
                "🔒 Password",
                type="password",
                placeholder="Enter your officer password",
                help="Your department-issued password"
            )
            
            col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
            with col_btn2:
                login_btn = st.form_submit_button(
                    "⚡ Login as Officer",
                    type="primary",
                    use_container_width=True
                )
        
        if login_btn:
            handle_officer_login(officer_id, password)
    
    # Default credentials info
    with st.expander("🔍 Default Officer Credentials (for testing)"):
        st.markdown("**Default officer accounts for testing:**")
        for officer in DEFAULT_OFFICERS:
            st.markdown(f"""
            **{officer['department']} Department:**
            - Officer ID: `{officer['officer_id']}`
            - Password: `{officer['password']}`
            """)

def show_admin_login():
    """Display admin login form"""
    st.markdown("### 👑 **Administrator Access**")
    st.markdown("System administrator login with elevated privileges.")
    
    with st.form("admin_login_form"):
        col1, col2 = st.columns([1, 2])
        
        with col2:
            admin_id = st.text_input(
                "🆔 Admin ID",
                placeholder="e.g., ADM000001",
                help="Your administrator ID"
            )
            
            password = st.text_input(
                "🔒 Password",
                type="password",
                placeholder="Enter admin password",
                help="Your administrator password"
            )
            
            col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
            with col_btn2:
                login_btn = st.form_submit_button(
                    "🎯 Login as Admin",
                    type="primary",
                    use_container_width=True
                )
        
        if login_btn:
            handle_admin_login(admin_id, password)
    
    # Default admin info
    with st.expander("🔍 Default Admin Credentials (for testing)"):
        st.markdown(f"""
        **Default administrator account:**
        - Admin ID: `{DEFAULT_ADMIN['admin_id']}`
        - Password: `{DEFAULT_ADMIN['password']}`
        """)

def handle_citizen_login(mobile_number: str, password: str):
    """Handle citizen login process"""
    
    # Validation
    if not mobile_number or not password:
        st.error("Please fill in all fields")
        return
    
    # Validate mobile number format
    is_valid, message = security_manager.validate_mobile_number(mobile_number)
    if not is_valid:
        st.error(message)
        return
    
    # Authenticate user
    with st.spinner("🔐 Authenticating..."):
        user_data = db.authenticate_user(mobile_number, password)
    
    if user_data:
        # Create session
        session_manager.create_session(user_data, 'citizen')
        
        st.success(f"✅ Welcome back! Redirecting to your dashboard...")
        time.sleep(1)
        
        st.session_state.page = 'user_dashboard'
        st.rerun()
    
    else:
        st.error("❌ Invalid mobile number or password")

def handle_officer_login(officer_id: str, password: str):
    """Handle department officer login process"""
    
    # Validation
    if not officer_id or not password:
        st.error("Please fill in all fields")
        return
    
    # Authenticate officer
    with st.spinner("🔐 Authenticating officer..."):
        officer_data = db.authenticate_officer(officer_id, password)
    
    if officer_data:
        # Create session
        session_manager.create_session(officer_data, 'department_officer')
        
        st.success(f"✅ Welcome, {officer_data['name']}! Redirecting to officer dashboard...")
        time.sleep(1)
        
        st.session_state.page = 'department_dashboard'
        st.rerun()
    
    else:
        st.error("❌ Invalid officer ID or password")

def handle_admin_login(admin_id: str, password: str):
    """Handle admin login process"""
    
    # Validation
    if not admin_id or not password:
        st.error("Please fill in all fields")
        return
    
    # Authenticate admin
    with st.spinner("🔐 Authenticating administrator..."):
        admin_data = db.authenticate_admin(admin_id, password)
    
    if admin_data:
        # Create session
        session_manager.create_session(admin_data, 'admin')
        
        st.success(f"✅ Welcome, {admin_data['name']}! Redirecting to admin dashboard...")
        time.sleep(1)
        
        st.session_state.page = 'admin_dashboard'
        st.rerun()
    
    else:
        st.error("❌ Invalid admin ID or password")

def show_login_help():
    """Display login help and information"""
    st.markdown("---")
    st.markdown("## ℹ️ **Login Help & Information**")
    
    help_col1, help_col2 = st.columns(2)
    
    with help_col1:
        with st.expander("🏠 **Citizen Login Help**"):
            st.markdown("""
            **How to login as a citizen:**
            1. Enter your registered 10-digit mobile number
            2. Enter your account password
            3. Click "Login as Citizen"
            
            **Mobile number format:**
            - Must be 10 digits
            - Should start with 6, 7, 8, or 9
            - Example: 9876543210
            """)
    
    with help_col2:
        with st.expander("👮 **Officer & Admin Help**"):
            st.markdown("""
            **Officer ID Format:**
            - Roads: RD001, RD002, etc.
            - Sanitation: SN001, SN002, etc.
            - Electricity: EL001, EL002, etc.
            - Public Safety: PS001, PS002, etc.
            
            **Admin ID Format:**
            - Starts with "ADM"
            - Example: ADM000001
            """)
    
    # Quick navigation
    st.markdown("---")
    nav_col1, nav_col2 = st.columns(2)
    
    with nav_col1:
        if st.button("🏠 Back to Home", key="nav_home_from_login", use_container_width=True):
            st.session_state.page = 'home'
            st.rerun()
    
    with nav_col2:
        if st.button("📝 Register New Account", key="nav_register_from_login", use_container_width=True):
            st.session_state.page = 'register'
            st.rerun()