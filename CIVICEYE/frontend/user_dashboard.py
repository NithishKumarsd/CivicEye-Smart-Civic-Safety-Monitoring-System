"""
CIVICEYE User Dashboard
Citizen portal for complaint submission and tracking
"""

import streamlit as st
from datetime import datetime
from PIL import Image, ExifTags
import os
import streamlit.components.v1 as components

from utils.security import session_manager, sanitize_input
from backend.complaint_service import submit_complaint, get_user_complaints
from database.db import db
from utils.constants import DEPARTMENTS, TAMIL_NADU_DISTRICTS, EMERGENCY_PLACES

def get_gps_location():
    """Get current GPS location using browser geolocation API"""
    try:
        # This would normally use JavaScript, but for Streamlit we'll simulate
        # In a real implementation, you'd use streamlit-javascript or similar
        # For now, return None to indicate GPS not available
        return None
    except Exception as e:
        print(f"Error getting GPS location: {e}")
        return None

def get_location_from_exif(uploaded_file):
    """Extract GPS coordinates from image EXIF data"""
    try:
        image = Image.open(uploaded_file)
        exif_data = image._getexif()

        if not exif_data:
            return None

        # GPS tags
        gps_tags = {
            0: 'GPSVersionID',
            1: 'GPSLatitudeRef',
            2: 'GPSLatitude',
            3: 'GPSLongitudeRef',
            4: 'GPSLongitude',
            5: 'GPSAltitudeRef',
            6: 'GPSAltitude',
            7: 'GPSTimeStamp',
            8: 'GPSSatellites',
            9: 'GPSStatus',
            10: 'GPSMeasureMode',
            11: 'GPSDOP',
            12: 'GPSSpeedRef',
            13: 'GPSSpeed',
            14: 'GPSTrackRef',
            15: 'GPSTrack',
            16: 'GPSImgDirectionRef',
            17: 'GPSImgDirection',
            18: 'GPSMapDatum',
            19: 'GPSDestLatitudeRef',
            20: 'GPSDestLatitude',
            21: 'GPSDestLongitudeRef',
            22: 'GPSDestLongitude',
            23: 'GPSDestBearingRef',
            24: 'GPSDestBearing',
            25: 'GPSDestDistanceRef',
            26: 'GPSDestDistance',
            27: 'GPSProcessingMethod',
            28: 'GPSAreaInformation',
            29: 'GPSDateStamp',
            30: 'GPSDifferential'
        }

        gps_info = {}
        for tag, value in exif_data.items():
            if tag in ExifTags.TAGS:
                tag_name = ExifTags.TAGS[tag]
                if tag_name.startswith('GPS'):
                    gps_info[tag_name] = value

        if 'GPSLatitude' in gps_info and 'GPSLongitude' in gps_info:
            # Convert DMS to decimal degrees
            lat = gps_info['GPSLatitude']
            lon = gps_info['GPSLongitude']

            lat_ref = gps_info.get('GPSLatitudeRef', 'N')
            lon_ref = gps_info.get('GPSLongitudeRef', 'E')

            # Convert to decimal
            lat_decimal = lat[0] + lat[1]/60 + lat[2]/3600
            lon_decimal = lon[0] + lon[1]/60 + lon[2]/3600

            # Apply hemisphere
            if lat_ref == 'S':
                lat_decimal = -lat_decimal
            if lon_ref == 'W':
                lon_decimal = -lon_decimal

            return lat_decimal, lon_decimal

        return None

    except Exception as e:
        print(f"Error extracting EXIF location: {e}")
        return None

def check_feedback_exists(complaint_id):
    """Check if feedback has been submitted for a complaint"""
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM feedbacks WHERE complaint_id = ?", (complaint_id,))
        result = cursor.fetchone()
        conn.close()
        return result is not None
    except Exception as e:
        print(f"Error checking feedback: {e}")
        return False

def submit_feedback(complaint_id, user_id, rating, satisfaction, feedback_text):
    """Submit feedback for a resolved complaint"""
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO feedbacks (complaint_id, user_id, rating, resolution_satisfaction, feedback_text)
            VALUES (?, ?, ?, ?, ?)
        """, (complaint_id, user_id, rating, satisfaction, feedback_text))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error submitting feedback: {e}")
        return False

def request_rehelp(complaint_id, user_id):
    """Request re-help by escalating complaint to HIGH urgency and assigning to Admin"""
    try:
        conn = db.get_connection()
        cursor = conn.cursor()

        # Update complaint urgency to HIGH
        cursor.execute("""
            UPDATE complaints SET urgency_level = 'High', status = 'Escalated'
            WHERE id = ?
        """, (complaint_id,))

        # Log urgency change
        cursor.execute("""
            INSERT INTO urgency_history (complaint_id, old_urgency, new_urgency, changed_by_type, changed_by_id, reason)
            VALUES (?, (SELECT urgency_level FROM complaints WHERE id = ?), 'High', 'user', ?, 'Re-help requested by citizen')
        """, (complaint_id, complaint_id, user_id))

        # Create notification for admin
        cursor.execute("""
            INSERT INTO notifications (recipient_type, recipient_id, notification_type, title, message, complaint_id)
            SELECT 'admin', id, 'escalation', 'Re-Help Requested', 'Citizen requested additional help for complaint #' || ?, ?
            FROM admins
        """, (complaint_id, complaint_id))

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error requesting re-help: {e}")
        return False

def handle_logout():
    """Handle user logout"""
    # Clear all authentication session variables
    keys_to_clear = [
        'logged_in', 'user_id', 'user_role', 'user_data', 'user_type',
        'current_user', 'session_valid', 'admin_logged_in', 'officer_logged_in',
        'citizen_logged_in', 'complaint_mode', 'gps_location', 'image_method'
    ]
    
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    
    # Destroy session
    session_manager.destroy_session()
    
    # Redirect to home
    st.session_state.page = 'home'
    st.rerun()

def show_district_complaints_list(user_data):
    st.markdown("### 🏙️ **District Complaints**")
    st.markdown("View all complaints submitted in your district. This helps you stay informed about civic issues in your area.")

    # Get user district
    user_district = user_data.get('district')
    if not user_district:
        st.error("District information not available.")
        return

    # Fetch complaints from DB
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.*, d.name as department_name,
                   GROUP_CONCAT(cm.file_path) as image_paths
            FROM complaints c
            LEFT JOIN departments d ON c.department_id = d.id
            LEFT JOIN complaint_media cm ON c.id = cm.complaint_id
            WHERE c.district = ?
            GROUP BY c.id
            ORDER BY c.created_at DESC
        """, (user_district,))

        complaints = []
        for row in cursor.fetchall():
            complaint = dict(row)
            complaint['image_paths'] = row['image_paths'].split(',') if row['image_paths'] else []
            complaints.append(complaint)

        conn.close()

    except Exception as e:
        st.error(f"Error fetching district complaints: {e}")
        return

    if not complaints:
        st.info("📝 No complaints have been submitted in your district yet.")
        return

    # Statistics
    total = len(complaints)
    resolved = len([c for c in complaints if c['status'] == 'Resolved'])
    pending = total - resolved

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("📋 Total Complaints", total)
    with col2:
        st.metric("✅ Resolved", resolved)
    with col3:
        st.metric("🔄 Pending", pending)

    # Filter
    status_filter = st.selectbox(
        "Filter by Status:",
        options=["All", "Pending", "Assigned", "In Progress", "Resolved"],
        key="district_filter"
    )

    # Display complaints
    filtered_complaints = [
        c for c in complaints
        if status_filter == "All" or c['status'] == status_filter
    ]

    for complaint in filtered_complaints:
        show_complaint_card(complaint, section="district_list")

def show_user_dashboard():
    """Display user dashboard"""
    
    user_data = session_manager.get_current_user()
    if not user_data:
        st.error("Session expired. Please login again.")
        st.session_state.page = 'login'
        st.rerun()
    
    # Logout button in header
    col_header1, col_header2 = st.columns([4, 1])
    with col_header2:
        if st.button("🚪 Logout", key="user_logout", type="secondary"):
            handle_logout()
    
    # Header
    with col_header1:
        st.markdown(f"""
        <div class="main-header">
            <h1>🏠 Welcome, Citizen!</h1>
            <p>Submit complaints and track resolutions in {user_data.get('district', 'your district')}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🏙️ District Complaints", "📝 Submit Complaint", "📊 My Complaints", "ℹ️ Guidelines"])

    with tab1:
        show_district_complaints_list(user_data)

    with tab2:
        show_complaint_form(user_data)

    with tab3:
        show_user_complaints_list(user_data)

    with tab4:
        show_guidelines()

def show_complaint_form(user_data):
    """Display complaint submission form"""
    
    # SECTION 1: HEADER
    st.markdown("### 📋 **Submit a Civic Complaint**")
    st.markdown("Report civic issues in your area for quick resolution.")
    
    # Initialize session state
    if 'complaint_mode' not in st.session_state:
        st.session_state.complaint_mode = "AI Detect Issue"
    if 'gps_location' not in st.session_state:
        st.session_state.gps_location = None
    if 'image_method' not in st.session_state:
        st.session_state.image_method = "Use Camera"
    
    # SECTION 2: COMPLAINT MODE
    with st.container():
        st.markdown("#### **Step 1: Complaint Mode**")
        complaint_mode = st.radio(
            "How would you like to submit your complaint?",
            options=["AI Detect Issue", "Manual Complaint"],
            horizontal=True,
            key="mode_radio"
        )
        st.session_state.complaint_mode = complaint_mode
    
    st.markdown("---")
    
    # GPS Location Button (outside form)
    with st.container():
        st.markdown("#### **Step 2: Location Detection**")
        if st.button("📍 Get My Current Location", key="gps_btn"):
            gps_coords = get_gps_location()
            if gps_coords:
                st.session_state.gps_location = gps_coords
                st.success(f"✅ Location detected: {gps_coords[0]:.6f}, {gps_coords[1]:.6f}")
            else:
                st.warning("⚠️ GPS location not available")
    
    st.markdown("---")
    
    # SECTION 4: IMAGE INPUT (SINGLE SECTION)
    with st.container():
        st.markdown("#### **Step 3: Photo Evidence**")
        
        if complaint_mode == "AI Detect Issue":
            st.warning("⚠️ **Photo is MANDATORY for AI detection**")
        else:
            st.info("📷 **Photo is optional for manual complaints**")
        
        # Single image method selection
        image_method = st.radio(
            "Choose photo method:",
            options=["Use Camera", "Upload Image"],
            horizontal=True,
            key="image_method_radio"
        )
        st.session_state.image_method = image_method
        
        # Single image input based on method
        uploaded_file = None
        if image_method == "Use Camera":
            uploaded_file = st.camera_input("Take a photo of the issue")
        else:
            uploaded_file = st.file_uploader(
                "Choose an image file",
                type=['png', 'jpg', 'jpeg']
            )
    
    st.markdown("---")
    
    # Form with all inputs
    with st.form("complaint_form", clear_on_submit=True):
        
        # SECTION 3: COMPLAINT TITLE
        st.markdown("#### **Complaint Details**")
        title = st.text_input(
            "Complaint Title *",
            placeholder="Open manhole near bus stop",
            help="Minimum 5 characters required"
        )
        
        # SECTION 5: DEPARTMENT SELECTION (MANUAL ONLY)
        manual_department = None
        if complaint_mode == "Manual Complaint":
            st.markdown("**Department Selection**")
            manual_department = st.selectbox(
                "Select Department *",
                options=["Roads", "Sanitation", "Electricity", "Public Safety"]
            )
        
        # SECTION 6: LOCATION
        st.markdown("**Complaint Location**")
        location_method = st.radio(
            "Location method:",
            options=["Auto-detect my location", "Enter location manually"],
            horizontal=True
        )
        
        latitude = longitude = None
        location_address = ""
        
        if location_method == "Auto-detect my location":
            if st.session_state.gps_location:
                latitude, longitude = st.session_state.gps_location
                st.success(f"📍 Using GPS: {latitude:.6f}, {longitude:.6f}")
            else:
                st.error("❌ No GPS location detected. Use 'Get My Current Location' button above.")
        
        location_address = st.text_input(
            "Exact Location *",
            placeholder="Street name, area, landmark details",
            help="Be specific about the location"
        )
        
        # SECTION 7: URGENCY CONTEXT
        st.markdown("**Urgency Context**")
        urgency_options = st.multiselect(
            "Is this complaint near any of these places?",
            options=["Near School", "Near Hospital", "Near Police Station", "Public Crowd Area"]
        )
        
        # Description
        description = st.text_area(
            "Detailed Description *",
            placeholder="Describe the issue in detail...",
            height=120,
            help="Provide comprehensive details about the problem"
        )
        
        # SECTION 8: SUBMISSION
        st.markdown("---")
        submit_btn = st.form_submit_button(
            "🚀 Submit Complaint",
            type="primary",
            use_container_width=True
        )
        
        # SECTION 9: ON SUBMIT
        if submit_btn:
            # Validation
            if not title.strip() or len(title) < 5:
                st.error("❌ Title must be at least 5 characters")
                return
            
            if not description.strip():
                st.error("❌ Description is required")
                return
            
            if not location_address.strip() and not (latitude and longitude):
                st.error("❌ Location is required (GPS or manual address)")
                return
            
            # Photo validation for AI mode
            if complaint_mode == "AI Detect Issue" and not uploaded_file:
                st.error("❌ Photo is mandatory for AI Detect Issue mode")
                return
            
            # Department validation for Manual mode
            if complaint_mode == "Manual Complaint" and not manual_department:
                st.error("❌ Department selection is required for Manual mode")
                return
            
            # Submit complaint
            auto_detect = complaint_mode == "AI Detect Issue"
            
            handle_complaint_submission(
                user_data, title, description, location_address,
                uploaded_file, auto_detect, manual_department, urgency_options,
                latitude, longitude
            )

def handle_complaint_submission(user_data, title, description, location_address,
                              uploaded_file, auto_detect, manual_department, nearby_places,
                              latitude=None, longitude=None):
    """Handle complaint submission"""
    
    # Validation
    if not all([title.strip(), description.strip(), location_address.strip()]):
        st.error("❌ Please fill in all required fields")
        return

    if len(title) < 5:
        st.error("❌ Title must be at least 5 characters")
        return

    if len(description) < 5:
        st.error("❌ Description must be at least 5 characters")
        return
    
    # Submit complaint
    with st.spinner("🤖 Processing your complaint..."):
        complaint_id = submit_complaint(
            user_id=user_data['id'],
            title=title,
            description=description,
            location_address=location_address,
            district=user_data['district'],
            uploaded_file=uploaded_file,
            auto_detect_department=auto_detect,
            manual_department=manual_department,
            latitude=latitude,
            longitude=longitude,
            nearby_emergency_places=nearby_places
        )
    
    if complaint_id:
        st.success("🎉 **Complaint Submitted Successfully!**")
        
        # Show complaint details
        st.markdown("### 📋 **Complaint Details**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"""
            **Complaint ID:** #{complaint_id}
            **Title:** {title}
            **Location:** {location_address}
            **District:** {user_data['district']}
            """)
        
        with col2:
            st.success("""
            **Status:** Pending 🔄
            **AI Processing:** Complete ✅
            **Department:** Auto-assigned 🤖
            **Tracking:** Active 📊
            """)
        
        if uploaded_file:
            st.markdown("**📸 Attached Image:**")
            st.image(uploaded_file, width=400)
        
        st.markdown("### 💬 **What's Next?**")
        st.info("""
        ✅ Your complaint has been submitted and assigned to the appropriate department.
        
        📧 You'll receive updates as the status changes.
        
        📊 Track progress in the "My Complaints" tab.
        
        ⏰ Expected resolution based on AI urgency prediction.
        """)
    
    else:
        st.error("❌ Failed to submit complaint. Please try again.")

def show_user_complaints_list(user_data):
    """Display user's complaint history"""
    st.markdown("### 📊 **My Complaint History**")
    
    # Get user complaints
    complaints = get_user_complaints(user_data['id'])
    
    if not complaints:
        st.info("📝 You haven't submitted any complaints yet.")
        return
    
    # Statistics
    total = len(complaints)
    resolved = len([c for c in complaints if c['status'] == 'Resolved'])
    pending = total - resolved
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📋 Total Complaints", total)
    with col2:
        st.metric("✅ Resolved", resolved)
    with col3:
        st.metric("🔄 Pending", pending)
    
    # Filter
    status_filter = st.selectbox(
        "Filter by Status:",
        options=["All", "Pending", "Assigned", "In Progress", "Resolved"]
    )
    
    # Display complaints
    filtered_complaints = [
        c for c in complaints 
        if status_filter == "All" or c['status'] == status_filter
    ]
    
    for complaint in filtered_complaints:
        show_complaint_card(complaint, user_data, section="user_list")

def show_complaint_card(complaint, user_data=None, section="default"):
    """Display individual complaint card"""
    
    # Status styling
    status_colors = {
        'Pending': {'bg': '#fff3cd', 'text': '#856404', 'emoji': '🔄'},
        'Assigned': {'bg': '#d1ecf1', 'text': '#0c5460', 'emoji': '👮'},
        'In Progress': {'bg': '#ffeaa7', 'text': '#6c5ce7', 'emoji': '⚠️'},
        'Resolved': {'bg': '#d4edda', 'text': '#155724', 'emoji': '✅'}
    }
    
    urgency_colors = {
        'High': {'bg': '#f8d7da', 'text': '#721c24', 'emoji': '🔴'},
        'Medium': {'bg': '#fff3cd', 'text': '#856404', 'emoji': '🟡'},
        'Low': {'bg': '#d4edda', 'text': '#155724', 'emoji': '🟢'}
    }
    
    status_style = status_colors.get(complaint['status'], status_colors['Pending'])
    urgency_style = urgency_colors.get(complaint['urgency_level'], urgency_colors['Medium'])
    
    with st.container():
        # Header
        col_header1, col_header2 = st.columns([3, 1])
        
        with col_header1:
            st.markdown(f"#### 📋 #{complaint['id']} - {complaint['title']}")
        
        with col_header2:
            st.markdown(f"""
            <div style="text-align: right;">
                <span style="background: {status_style['bg']}; color: {status_style['text']}; 
                           padding: 0.25rem 0.6rem; border-radius: 15px; font-size: 0.8rem; font-weight: bold;">
                    {status_style['emoji']} {complaint['status']}
                </span>
                <br><br>
                <span style="background: {urgency_style['bg']}; color: {urgency_style['text']}; 
                           padding: 0.25rem 0.6rem; border-radius: 15px; font-size: 0.8rem; font-weight: bold;">
                    {urgency_style['emoji']} {complaint['urgency_level']}
                </span>
            </div>
            """, unsafe_allow_html=True)
        
        # Details
        col_details1, col_details2 = st.columns([2, 1])
        
        with col_details1:
            st.markdown(f"""
            **📄 Description:** {complaint['description']}
            
            **📍 Location:** {complaint['location_address']}
            
            **🏢 Department:** {complaint['department_name']}
            
            **📅 Submitted:** {complaint['created_at'][:16]}
            """)
            
            # Show images if available
            if complaint['image_paths'] and complaint['image_paths'][0]:
                with st.expander("📸 View Photos"):
                    for img_path in complaint['image_paths']:
                        if img_path and os.path.exists(img_path):
                            try:
                                image = Image.open(img_path)
                                st.image(image, width=300)
                            except:
                                st.warning("Cannot display image")
        
        with col_details2:
            if complaint['status'] == 'Resolved':
                st.success("🎉 **Completed!**")
                if complaint['resolved_at']:
                    st.write(f"**Resolved:** {complaint['resolved_at'][:16]}")

                # Feedback System for Resolved Complaints
                st.markdown("---")
                st.markdown("### 💬 **Feedback**")

                # Check if feedback already submitted
                feedback_submitted = check_feedback_exists(complaint['id'])

                if feedback_submitted:
                    st.info("✅ **Feedback Submitted** - Thank you for your input!")
                else:
                    with st.expander("📝 **Provide Feedback**"):
                        rating = st.slider(
                            "Rate the resolution (1-5 stars)", 
                            1, 5, 3, 
                            key=f"rating_slider_{complaint['id']}_{section}"
                        )
                        satisfaction = st.selectbox(
                            "Overall Satisfaction",
                            ["Very Dissatisfied", "Dissatisfied", "Neutral", "Satisfied", "Very Satisfied"],
                            key=f"satisfaction_{complaint['id']}_{section}"
                        )
                        feedback_text = st.text_area(
                            "Additional Comments (Optional)",
                            placeholder="Tell us about your experience...",
                            height=80,
                            key=f"feedback_text_{complaint['id']}_{section}"
                        )

                        col_fb1, col_fb2 = st.columns(2)
                        with col_fb1:
                            if st.button("✅ Submit Feedback", key=f"feedback_{complaint['id']}_{section}"):
                                if submit_feedback(complaint['id'], user_data['id'], rating, satisfaction, feedback_text):
                                    st.success("✅ Thank you for your feedback! Your input helps us improve our services.")
                                    st.rerun()
                                else:
                                    st.error("❌ Failed to submit feedback. Please try again.")

                        with col_fb2:
                            if st.button("🚨 Re-Help Needed", key=f"rehelp_{complaint['id']}_{section}"):
                                # Validate data before processing
                                if not complaint or not user_data:
                                    st.error("Unable to process re-help request at the moment.")
                                elif complaint.get('status') == 'Closed':
                                    st.warning("Cannot request re-help for closed complaints.")
                                elif not complaint.get('id') or not user_data.get('id'):
                                    st.error("Unable to process re-help request at the moment.")
                                else:
                                    if request_rehelp(complaint['id'], user_data['id']):
                                        st.success("✅ Re-help request submitted successfully!")
                                        st.rerun()
                                    else:
                                        st.error("❌ Failed to submit re-help request. Please try again.")

            elif complaint['status'] == 'In Progress':
                st.warning("⚠️ **In Progress**")
                st.write("Officer is working on this issue.")
            else:
                st.info("🔄 **Pending**")
                st.write("Waiting for assignment.")
        
        st.markdown("---")

def show_guidelines():
    """Display complaint guidelines"""
    st.markdown("### ℹ️ **Complaint Guidelines**")
    
    with st.expander("📋 **How to Submit Effective Complaints**"):
        st.markdown("""
        **For faster resolution:**
        
        1. **Be Specific**: Provide exact location with landmarks
        2. **Add Photos**: Visual evidence helps officers understand better
        3. **Detailed Description**: Explain when, how, and impact
        4. **Choose Correct Info**: Help AI route to right department
        5. **Monitor Progress**: Check status regularly
        """)
    
    with st.expander("🤖 **AI Features**"):
        st.markdown("""
        **Our AI automatically:**
        
        - **Predicts Department**: Routes to Roads, Sanitation, Electricity, or Public Safety
        - **Determines Urgency**: Classifies as High, Medium, or Low priority
        - **Estimates Timeline**: Provides expected resolution timeframe
        - **Detects Emergencies**: Auto-escalates critical situations
        """)
    
    with st.expander("📊 **Status Meanings**"):
        st.markdown("""
        - 🔄 **Pending**: Complaint submitted, waiting for assignment
        - 👮 **Assigned**: Officer has been assigned to handle
        - ⚠️ **In Progress**: Officer is actively working on the issue
        - ✅ **Resolved**: Issue has been fixed and closed
        """)
    
    with st.expander("🚨 **Emergency Situations**"):
        st.markdown("""
        **For immediate emergencies, call:**
        - 🚨 Police: 100
        - 🚒 Fire: 101
        - 🏥 Ambulance: 108
        
        **Use CIVICEYE for:**
        - Non-emergency civic issues
        - Infrastructure problems
        - Maintenance requests
        - Quality of life improvements
        """)