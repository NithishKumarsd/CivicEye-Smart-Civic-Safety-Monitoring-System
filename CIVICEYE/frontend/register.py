"""
CIVICEYE Registration Page
Citizen registration with mobile number validation and district selection
"""

import streamlit as st
import time
from database.db import db
from utils.security import security_manager, sanitize_input
from utils.constants import TAMIL_NADU_DISTRICTS, VALIDATION_RULES

def show_register_page():
    """Display citizen registration page"""

    # Initialize session state
    if 'registration_success' not in st.session_state:
        st.session_state.registration_success = False

    # Header
    st.markdown("""
    <div class="main-header">
        <h1>📝 Register for CIVICEYE</h1>
        <p>Join thousands of citizens making their city better</p>
    </div>
    """, unsafe_allow_html=True)

    # Registration form
    show_registration_form()

    # Information section
    show_registration_info()

def show_registration_form():
    """Display the main registration form"""

    # Show form only if registration not successful
    if not st.session_state.registration_success:
        st.markdown("## 🏠 **Create Citizen Account**")
        st.markdown("Register to submit complaints and track resolutions in your district.")

        with st.form("citizen_registration_form", clear_on_submit=False):
            col1, col2 = st.columns([1, 2])

            with col2:
                # Mobile number input
                mobile_number = st.text_input(
                    "📱 Mobile Number *",
                    placeholder="Enter your 10-digit mobile number",
                    help="This will be your login username. Must be a valid Indian mobile number.",
                    max_chars=10
                )

                # Password inputs
                password = st.text_input(
                    "🔒 Create Password *",
                    type="password",
                    placeholder="Create a strong password",
                    help="Minimum 8 characters with letters and numbers"
                )

                confirm_password = st.text_input(
                    "🔒 Confirm Password *",
                    type="password",
                    placeholder="Re-enter your password",
                    help="Must match the password above"
                )

                # District selection
                district = st.selectbox(
                    "📍 Select Your District *",
                    options=[""] + TAMIL_NADU_DISTRICTS,
                    help="Choose your district in Tamil Nadu"
                )

                # Location permission
                location_permission = st.checkbox(
                    "📍 Allow location access for better complaint tracking",
                    help="This helps us automatically detect your location when submitting complaints"
                )

                # Terms and conditions
                st.markdown("---")
                terms_agreed = st.checkbox(
                    "✅ I agree to the Terms of Service and Privacy Policy *",
                    help="Required to create an account"
                )

                # Submit button
                col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
                with col_btn2:
                    register_btn = st.form_submit_button(
                        "🎉 Create Account",
                        type="primary",
                        use_container_width=True
                    )

            # Handle form submission
            if register_btn:
                success = handle_registration(
                    mobile_number, password, confirm_password,
                    district, location_permission, terms_agreed
                )
                if success:
                    st.session_state.registration_success = True
                    st.rerun()
                else:
                    # Show error message outside form
                    st.error("❌ Registration failed. Please check your inputs and try again.")
                    st.error("This mobile number may already be registered or there was a validation error.")

        # Login link
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.info("Already have an account?")
            if st.button("🔑 Login to Existing Account", key="goto_login", use_container_width=True):
                st.session_state.page = 'login'
                st.rerun()

    # Show success UI if registration successful
    else:
        show_success_ui()

def handle_registration(mobile_number: str, password: str, confirm_password: str,
                       district: str, location_permission: bool, terms_agreed: bool):
    """Handle the registration process"""

    # Sanitize inputs
    mobile_number = sanitize_input(mobile_number)
    district = sanitize_input(district)

    # Validation
    if not all([mobile_number, password, confirm_password, district]):
        return False

    if not terms_agreed:
        return False

    # Validate mobile number
    is_valid_mobile, mobile_message = security_manager.validate_mobile_number(mobile_number)
    if not is_valid_mobile:
        return False

    # Validate password
    is_valid_password, password_message = security_manager.validate_password_strength(password)
    if not is_valid_password:
        return False

    # Check password confirmation
    if password != confirm_password:
        return False

    # Validate district
    if district not in TAMIL_NADU_DISTRICTS:
        return False

    # Create user account
    user_id = db.create_user(
        mobile_number=mobile_number,
        password=password,
        district=district,
        location_permission=location_permission
    )

    if user_id:
        # Store registration data for success UI
        st.session_state.registration_data = {
            'mobile_number': mobile_number,
            'district': district,
            'location_permission': location_permission
        }
        return True
    else:
        return False

def show_registration_info():
    """Display registration information and guidelines"""
    st.markdown("---")
    st.markdown("## ℹ️ **Registration Information**")
    
    info_col1, info_col2 = st.columns(2)
    
    with info_col1:
        with st.expander("📱 **Mobile Number Requirements**"):
            st.markdown("""
            **Your mobile number will be used for:**
            - Login username (instead of email)
            - SMS notifications (if available)
            - Account verification
            - Password recovery
            
            **Format requirements:**
            - Must be exactly 10 digits
            - Should start with 6, 7, 8, or 9
            - Must be a valid Indian mobile number
            - Example: 9876543210
            
            **Security note:**
            - Keep your mobile number updated
            - Don't share your login credentials
            - Report if your number is compromised
            """)
    
    with info_col2:
        with st.expander("🔒 **Password Security**"):
            st.markdown("""
            **Password requirements:**
            - Minimum 8 characters long
            - At least one uppercase letter (A-Z)
            - At least one lowercase letter (a-z)
            - At least one number (0-9)
            - Avoid common passwords
            
            **Security tips:**
            - Use a unique password for CIVICEYE
            - Don't use personal information
            - Consider using a password manager
            - Change password if compromised
            
            **Examples of strong passwords:**
            - MyCity2024!
            - Complaint@123
            - TamilNadu#456
            """)
    
    # District information
    with st.expander("📍 **District Selection Guide**"):
        st.markdown("""
        **Why district selection matters:**
        - Complaints are routed to local authorities
        - You'll see relevant local issues
        - Statistics are district-specific
        - Officers are assigned by district
        
        **Tamil Nadu Districts covered:**
        """)
        
        # Display districts in columns
        district_cols = st.columns(3)
        for i, district in enumerate(TAMIL_NADU_DISTRICTS):
            with district_cols[i % 3]:
                st.markdown(f"• {district}")
    
    # Privacy and terms
    with st.expander("🛡️ **Privacy & Terms**"):
        st.markdown("""
        **Data we collect:**
        - Mobile number (for login)
        - District (for complaint routing)
        - Location (only if you grant permission)
        - Complaint data (text, images, location)
        
        **How we use your data:**
        - Route complaints to appropriate departments
        - Send status updates and notifications
        - Generate anonymous analytics
        - Improve service quality
        
        **Your rights:**
        - View all your data
        - Request data deletion
        - Opt out of notifications
        - Update your information
        
        **Data security:**
        - Encrypted password storage
        - Secure database connections
        - Regular security audits
        - No data sharing with third parties
        """)
    
    # Benefits section
    st.markdown("### 🌟 **Benefits of Registration**")
    
    benefit_col1, benefit_col2, benefit_col3 = st.columns(3)
    
    with benefit_col1:
        st.markdown("""
        <div class="info-card" style="text-align: center;">
            <div style="font-size: 3rem; color: #667eea;">📝</div>
            <h4>Submit Complaints</h4>
            <p>Report civic issues with photos and detailed descriptions</p>
        </div>
        """, unsafe_allow_html=True)
    
    with benefit_col2:
        st.markdown("""
        <div class="info-card" style="text-align: center;">
            <div style="font-size: 3rem; color: #f093fb;">📊</div>
            <h4>Track Progress</h4>
            <p>Monitor complaint status and resolution progress in real-time</p>
        </div>
        """, unsafe_allow_html=True)
    
    with benefit_col3:
        st.markdown("""
        <div class="info-card" style="text-align: center;">
            <div style="font-size: 3rem; color: #4facfe;">🤝</div>
            <h4>Community Impact</h4>
            <p>Join other citizens in making your city cleaner and better</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Quick navigation
    st.markdown("---")
    nav_col1, nav_col2 = st.columns(2)
    
    with nav_col1:
        if st.button("🏠 Back to Home", key="nav_home_from_register", use_container_width=True):
            st.session_state.page = 'home'
            st.rerun()
    
    with nav_col2:
        if st.button("🔑 Already Registered? Login", key="nav_login_from_register", use_container_width=True):
            st.session_state.page = 'login'
            st.rerun()

def show_success_ui():
    """Display success UI after successful registration"""
    data = st.session_state.registration_data

    st.success("🎉 **Account created successfully!**")

    # Show account details
    st.markdown("### 📋 **Account Details**")

    col_detail1, col_detail2 = st.columns(2)

    with col_detail1:
        st.info(f"""
        **Mobile Number:** {data['mobile_number']}
        **District:** {data['district']}
        **Location Access:** {'Enabled' if data['location_permission'] else 'Disabled'}
        """)

    with col_detail2:
        st.success("""
        **Account Status:** Active ✅
        **Role:** Citizen 🏠
        **Registration:** Complete 🎯
        """)

    # Next steps
    st.markdown("### 🚀 **What's Next?**")
    st.markdown("""
    ✅ **Your CIVICEYE account is ready!**

    **You can now:**
    - 📝 Submit civic complaints with photos
    - 📊 Track complaint status in real-time
    - 💬 Review and comment on other complaints
    - 📧 Receive email notifications on updates
    - 🗺️ View complaints on interactive maps
    """)

    # Auto-redirect to login
    st.markdown("---")
    col_redirect1, col_redirect2, col_redirect3 = st.columns([1, 1, 1])

    with col_redirect2:
        if st.button("🔑 Login Now", key="login_after_register", use_container_width=True):
            st.session_state.page = 'login'
            st.session_state.login_type = 'citizen'
            st.rerun()

    # Auto-redirect after 5 seconds
    with st.empty():
        for i in range(5, 0, -1):
            st.info(f"Redirecting to login page in {i} seconds...")
            time.sleep(1)

        st.session_state.page = 'login'
        st.rerun()
