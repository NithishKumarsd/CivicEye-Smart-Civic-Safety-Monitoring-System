"""
CIVICEYE Department Dashboard
Officer portal for managing and resolving complaints
"""

import streamlit as st
from datetime import datetime
from PIL import Image
import os

from utils.security import session_manager
from backend.complaint_service import complaint_service, update_complaint_status
from backend.transfer_service import request_department_transfer, escalate_complaint
from utils.constants import COMPLAINT_STATUS
from database.db import db

def handle_status_update(complaint_id, new_status, officer_id, notes):
    """Handle complaint status update with notification"""
    try:
        # Update complaint status
        success = update_complaint_status(complaint_id, new_status, officer_id, notes)
        
        if success:
            # Create notification for citizen
            conn = db.get_connection()
            cursor = conn.cursor()
            
            # Get complaint and user info
            cursor.execute("""
                SELECT c.user_id, c.title FROM complaints c WHERE c.id = ?
            """, (complaint_id,))
            result = cursor.fetchone()
            
            if result:
                user_id = result['user_id']
                complaint_title = result['title']
                
                # Create notification
                cursor.execute("""
                    INSERT INTO notifications (recipient_type, recipient_id, notification_type, title, message, complaint_id)
                    VALUES ('user', ?, 'complaint_update', 'Complaint Status Updated', 
                           'Your complaint "' || ? || '" status has been updated to ' || ? || ' by the department.', ?)
                """, (user_id, complaint_title, new_status, complaint_id))
                
                conn.commit()
            
            conn.close()
            st.success(f"✅ Complaint status updated to {new_status} successfully!")
        else:
            st.error("❌ Failed to update complaint status. Please try again.")
            
    except Exception as e:
        st.error(f"❌ Error updating status: {str(e)}")
        print(f"Error in handle_status_update: {e}")

def show_department_dashboard():
    """Display department officer dashboard"""
    
    officer_data = session_manager.get_current_user()
    if not officer_data:
        st.error("Session expired. Please login again.")
        st.session_state.page = 'login'
        st.rerun()
    
    # Logout button in header
    col_header1, col_header2 = st.columns([4, 1])
    with col_header2:
        if st.button("🚪 Logout", key="dept_logout", type="secondary"):
            from frontend.user_dashboard import handle_logout
            handle_logout()
    
    # Header
    with col_header1:
        st.markdown(f"""
        <div class="main-header">
            <h1>👮 {officer_data.get('department_name', 'Department')} Officer Portal</h1>
            <p>Welcome, {officer_data.get('name', 'Officer')} - Manage and resolve citizen complaints</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Complaint Queue", "📊 My Performance", "🔄 Transfers", "⚙️ Tools"])
    
    with tab1:
        show_complaint_queue(officer_data)
    
    with tab2:
        show_performance_metrics(officer_data)
    
    with tab3:
        show_transfer_requests(officer_data)
    
    with tab4:
        show_officer_tools(officer_data)

def show_complaint_queue(officer_data):
    """Display complaint queue for the department"""
    st.markdown("### 📋 **Complaint Management Queue**")
    
    # Filters
    col_filter1, col_filter2, col_filter3 = st.columns(3)
    
    with col_filter1:
        # Only show active statuses for officers (exclude Resolved and Closed)
        active_statuses = [status for status in COMPLAINT_STATUS if status not in ['Resolved', 'Closed']]
        status_filter = st.selectbox(
            "Filter by Status:",
            options=["All"] + active_statuses
        )
    
    with col_filter2:
        urgency_filter = st.selectbox(
            "Filter by Urgency:",
            options=["All", "High", "Medium", "Low"]
        )
    
    with col_filter3:
        sort_by = st.selectbox(
            "Sort by:",
            options=["Urgency + Date", "Date Created", "SLA Deadline"]
        )
    
    # Get complaints for department
    department_id = officer_data.get('department_id')
    complaints = complaint_service.get_department_complaints(
        department_id, 
        status_filter if status_filter != "All" else None
    )
    
    # Apply filters
    if urgency_filter != "All":
        complaints = [c for c in complaints if c['urgency_level'] == urgency_filter]
    
    if not complaints:
        st.info("📝 No complaints found matching the selected filters.")
        return
    
    # Statistics
    show_queue_stats(complaints)
    
    # Display complaints
    st.markdown("---")
    for complaint in complaints:
        show_officer_complaint_card(complaint, officer_data)

def show_queue_stats(complaints):
    """Display queue statistics"""
    total = len(complaints)
    high_urgency = len([c for c in complaints if c['urgency_level'] == 'High'])
    pending = len([c for c in complaints if c['status'] == 'Pending'])
    in_progress = len([c for c in complaints if c['status'] == 'In Progress'])
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📋 Total Queue", total)
    with col2:
        st.metric("🔴 High Priority", high_urgency)
    with col3:
        st.metric("🔄 Pending", pending)
    with col4:
        st.metric("⚠️ In Progress", in_progress)

def show_officer_complaint_card(complaint, officer_data):
    """Display complaint card for officers"""
    
    # Status and urgency styling
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
        # Header with badges
        col_header1, col_header2 = st.columns([3, 1])
        
        with col_header1:
            st.markdown(f"#### 📋 #{complaint['id']} - {complaint['title']}")
            st.markdown(f"**Citizen:** {complaint.get('user_mobile', 'N/A')}")
        
        with col_header2:
            st.markdown(f"""
            <div style="text-align: right;">
                <span style="background: {urgency_style['bg']}; color: {urgency_style['text']}; 
                           padding: 0.25rem 0.6rem; border-radius: 15px; font-size: 0.8rem; font-weight: bold;">
                    {urgency_style['emoji']} {complaint['urgency_level']} Priority
                </span>
                <br><br>
                <span style="background: {status_style['bg']}; color: {status_style['text']}; 
                           padding: 0.25rem 0.6rem; border-radius: 15px; font-size: 0.8rem; font-weight: bold;">
                    {status_style['emoji']} {complaint['status']}
                </span>
            </div>
            """, unsafe_allow_html=True)
        
        # Complaint details
        col_details1, col_details2 = st.columns([2, 1])
        
        with col_details1:
            st.markdown(f"""
            **📄 Description:** {complaint['description']}
            
            **📍 Location:** {complaint['location_address']}
            
            **📅 Submitted:** {complaint['created_at'][:16]}
            
            **⏰ SLA Deadline:** {complaint.get('sla_deadline', 'N/A')[:16] if complaint.get('sla_deadline') else 'N/A'}
            """)
            
            # Show images
            if complaint.get('image_paths') and complaint['image_paths'][0]:
                with st.expander("📸 View Evidence Photos"):
                    for img_path in complaint['image_paths']:
                        if img_path and os.path.exists(img_path):
                            try:
                                image = Image.open(img_path)
                                st.image(image, width=300)
                            except:
                                st.warning("Cannot display image")
        
        with col_details2:
            # Action buttons
            st.markdown("**🔧 Actions:**")
            
            # Status update - only show active statuses for officers
            active_statuses = [status for status in COMPLAINT_STATUS if status not in ['Closed']]
            new_status = st.selectbox(
                "Update Status:",
                options=active_statuses,
                index=active_statuses.index(complaint['status']) if complaint['status'] in active_statuses else 0,
                key=f"status_{complaint['id']}"
            )
            
            # Internal notes
            notes = st.text_area(
                "Internal Notes:",
                placeholder="Add notes for internal tracking...",
                key=f"notes_{complaint['id']}",
                height=80
            )
            
            # Update button
            if st.button(f"💾 Update #{complaint['id']}", key=f"update_{complaint['id']}"):
                handle_status_update(complaint['id'], new_status, officer_data['id'], notes)
            
            # Transfer button
            if st.button(f"🔄 Request Transfer", key=f"transfer_{complaint['id']}"):
                st.session_state[f"show_transfer_{complaint['id']}"] = True
            
            # Show transfer form if button clicked
            if st.session_state.get(f"show_transfer_{complaint['id']}", False):
                with st.form(f"transfer_form_{complaint['id']}"):
                    st.markdown("**Request Department Transfer**")
                    
                    # Get available departments (exclude current)
                    available_depts = ["Roads", "Sanitation", "Electricity", "Public Safety"]
                    current_dept = officer_data.get('department_name', '')
                    if current_dept in available_depts:
                        available_depts.remove(current_dept)
                    
                    target_dept = st.selectbox(
                        "Transfer to Department:",
                        options=available_depts,
                        key=f"target_dept_{complaint['id']}"
                    )
                    reason = st.text_area(
                        "Transfer Reason:", 
                        placeholder="Explain why this complaint should be transferred...",
                        key=f"transfer_reason_{complaint['id']}"
                    )
                    
                    col_submit, col_cancel = st.columns(2)
                    with col_submit:
                        if st.form_submit_button("🔄 Submit Transfer Request"):
                            if reason.strip():
                                success = request_department_transfer(
                                    complaint['id'], officer_data['department_id'], 
                                    target_dept, officer_data['id'], reason
                                )
                                if success:
                                    st.success(f"✅ Transfer request submitted for complaint #{complaint['id']}")
                                    st.session_state[f"show_transfer_{complaint['id']}"] = False
                                    st.rerun()
                                else:
                                    st.error("❌ Failed to submit transfer request")
                            else:
                                st.error("Please provide a reason for transfer")
                    
                    with col_cancel:
                        if st.form_submit_button("Cancel"):
                            st.session_state[f"show_transfer_{complaint['id']}"] = False
                            st.rerun()
            
            # Escalate button
            if st.button(f"🚨 Escalate", key=f"escalate_{complaint['id']}"):
                st.session_state[f"show_escalate_{complaint['id']}"] = True
            
            # Show escalation form if button clicked
            if st.session_state.get(f"show_escalate_{complaint['id']}", False):
                with st.form(f"escalate_form_{complaint['id']}"):
                    st.markdown("**Escalate Complaint**")
                    
                    urgency = st.selectbox(
                        "Escalation Urgency:", 
                        options=["High", "Medium", "Low"],
                        index=0,  # Default to High
                        key=f"escalate_urgency_{complaint['id']}"
                    )
                    reason = st.text_area(
                        "Escalation Reason:", 
                        placeholder="Explain why this complaint needs escalation...",
                        key=f"escalate_reason_{complaint['id']}"
                    )
                    
                    col_submit, col_cancel = st.columns(2)
                    with col_submit:
                        if st.form_submit_button("🚨 Submit Escalation"):
                            if reason.strip():
                                success = escalate_complaint(
                                    complaint['id'], officer_data['department_id'], 
                                    officer_data['id'], reason, urgency
                                )
                                if success:
                                    st.success(f"✅ Complaint #{complaint['id']} escalated")
                                    st.session_state[f"show_escalate_{complaint['id']}"] = False
                                    st.rerun()
                                else:
                                    st.error("❌ Failed to escalate complaint")
                            else:
                                st.error("Please provide a reason for escalation")
                    
                    with col_cancel:
                        if st.form_submit_button("Cancel"):
                            st.session_state[f"show_escalate_{complaint['id']}"] = False
                            st.rerun()
        
        st.markdown("---")

def show_performance_metrics(officer_data):
    """Display officer performance metrics"""
    st.markdown("### 📊 **Performance Dashboard**")
    
    try:
        # Get officer's complaint statistics
        conn = complaint_service.db.get_connection()
        cursor = conn.cursor()
        
        officer_id = officer_data['id']
        
        # Total assigned complaints
        cursor.execute("""
            SELECT COUNT(*) FROM complaints WHERE assigned_officer_id = ?
        """, (officer_id,))
        total_assigned = cursor.fetchone()[0]
        
        # Resolved complaints
        cursor.execute("""
            SELECT COUNT(*) FROM complaints 
            WHERE assigned_officer_id = ? AND status = 'Resolved'
        """, (officer_id,))
        total_resolved = cursor.fetchone()[0]
        
        # Average resolution time
        cursor.execute("""
            SELECT AVG(
                (JULIANDAY(resolved_at) - JULIANDAY(created_at)) * 24
            ) as avg_hours
            FROM complaints
            WHERE assigned_officer_id = ? AND status = 'Resolved'
        """, (officer_id,))
        result = cursor.fetchone()
        avg_resolution_hours = result[0] if result[0] else 0
        
        # This month's performance
        cursor.execute("""
            SELECT COUNT(*) FROM complaints 
            WHERE assigned_officer_id = ? 
            AND strftime('%Y-%m', created_at) = strftime('%Y-%m', 'now')
        """, (officer_id,))
        this_month = cursor.fetchone()[0]
        
        conn.close()
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📋 Total Assigned", total_assigned)
        
        with col2:
            st.metric("✅ Resolved", total_resolved)
        
        with col3:
            resolution_rate = (total_resolved / total_assigned * 100) if total_assigned > 0 else 0
            st.metric("📈 Resolution Rate", f"{resolution_rate:.1f}%")
        
        with col4:
            if avg_resolution_hours > 0:
                if avg_resolution_hours < 24:
                    time_display = f"{avg_resolution_hours:.1f}h"
                else:
                    time_display = f"{avg_resolution_hours/24:.1f}d"
            else:
                time_display = "N/A"
            st.metric("⏱️ Avg Resolution", time_display)
        
        # Monthly performance
        st.markdown("### 📅 **This Month's Activity**")
        st.metric("📊 Complaints This Month", this_month)
        
        # Performance tips
        st.markdown("### 💡 **Performance Tips**")
        
        if resolution_rate < 70:
            st.warning("📈 **Improvement Opportunity**: Focus on resolving pending complaints to improve your resolution rate.")
        elif resolution_rate > 90:
            st.success("🎉 **Excellent Performance**: You're maintaining a high resolution rate!")
        
        if avg_resolution_hours > 72:
            st.info("⏰ **Speed Tip**: Try to resolve complaints faster to improve citizen satisfaction.")
    
    except Exception as e:
        st.error(f"Error loading performance data: {e}")

def show_officer_tools(officer_data):
    """Display officer tools and utilities"""
    st.markdown("### ⚙️ **Officer Tools**")
    
    # Quick actions
    col_tool1, col_tool2 = st.columns(2)
    
    with col_tool1:
        st.markdown("""
        <div class="info-card">
            <h4>🚨 Emergency Escalation</h4>
            <p>Escalate urgent complaints that need immediate attention or admin intervention.</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚨 Request Emergency Escalation", use_container_width=True):
            show_escalation_form(officer_data)
    
    with col_tool2:
        st.markdown("""
        <div class="info-card">
            <h4>🔄 Department Transfer</h4>
            <p>Request to transfer complaints to other departments if misrouted.</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔄 Request Department Transfer", use_container_width=True):
            show_transfer_form(officer_data)
    
    # Guidelines
    with st.expander("📋 **Officer Guidelines**"):
        st.markdown(f"""
        **As a {officer_data.get('department_name', 'Department')} Officer, you should:**
        
        1. **Prioritize by Urgency**: Handle High priority complaints first
        2. **Update Status Regularly**: Keep citizens informed of progress
        3. **Add Internal Notes**: Document actions taken for audit trail
        4. **Meet SLA Deadlines**: Resolve within expected timeframes
        5. **Request Help**: Escalate or transfer if needed
        
        **SLA Targets:**
        - 🔴 High Priority: 24 hours
        - 🟡 Medium Priority: 72 hours  
        - 🟢 Low Priority: 7 days
        """)
    
    with st.expander("🔧 **Status Definitions**"):
        st.markdown("""
        - **Pending**: Just submitted, not yet assigned
        - **Assigned**: Assigned to you, ready to work on
        - **In Progress**: You're actively working on it
        - **Resolved**: Issue fixed and complaint closed
        """)

def show_transfer_form(officer_data):
    """Show transfer form for general use"""
    st.markdown("#### 🔄 **Department Transfer Request**")
    
    with st.form("general_transfer_form"):
        complaint_id = st.number_input("Complaint ID", min_value=1, step=1)
        
        # Get available departments (exclude current)
        available_depts = ["Roads", "Sanitation", "Electricity", "Public Safety"]
        current_dept = officer_data.get('department_name', '')
        if current_dept in available_depts:
            available_depts.remove(current_dept)
        
        target_dept = st.selectbox("Transfer to Department:", options=available_depts)
        reason = st.text_area("Transfer Reason", placeholder="Explain why this should be transferred...")
        
        if st.form_submit_button("🔄 Submit Transfer Request"):
            if complaint_id and reason:
                success = request_department_transfer(
                    complaint_id, officer_data['department_id'], 
                    target_dept, officer_data['id'], reason
                )
                if success:
                    st.success(f"✅ Transfer request submitted for complaint #{complaint_id}")
                else:
                    st.error("❌ Failed to submit transfer request")
            else:
                st.error("Please fill in all fields")

def show_escalation_form(officer_data):
    """Show emergency escalation form"""
    st.markdown("#### 🚨 **Emergency Escalation Request**")
    
    with st.form("escalation_form"):
        complaint_id = st.number_input("Complaint ID", min_value=1, step=1)
        urgency = st.selectbox("Urgency Level:", options=["High", "Medium", "Low"])
        reason = st.text_area("Escalation Reason", placeholder="Explain why this needs admin attention...")
        
        if st.form_submit_button("🚨 Submit Escalation"):
            if complaint_id and reason:
                success = escalate_complaint(
                    complaint_id, officer_data['department_id'], 
                    officer_data['id'], reason, urgency
                )
                if success:
                    st.success(f"✅ Escalation request submitted for complaint #{complaint_id}")
                else:
                    st.error("❌ Failed to submit escalation")
            else:
                st.error("Please fill in all fields")

def show_transfer_requests(officer_data):
    """Show transfer requests for officer"""
    st.markdown("### 🔄 **My Transfer Requests**")
    
    from backend.transfer_service import get_officer_transfer_requests
    
    transfers = get_officer_transfer_requests(officer_data['id'])
    
    if not transfers:
        st.info("📝 No transfer requests submitted yet.")
        return
    
    for transfer in transfers:
        status_colors = {
            'PENDING': {'bg': '#fff3cd', 'text': '#856404', 'emoji': '🔄'},
            'APPROVED': {'bg': '#d4edda', 'text': '#155724', 'emoji': '✅'},
            'REJECTED': {'bg': '#f8d7da', 'text': '#721c24', 'emoji': '❌'}
        }
        
        status_style = status_colors.get(transfer['status'], status_colors['PENDING'])
        
        with st.container():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**Complaint #{transfer['complaint_id']}**: {transfer['title']}")
                st.markdown(f"**From**: {transfer['from_department']} → **To**: {transfer['to_department']}")
                st.markdown(f"**Reason**: {transfer['reason']}")
                st.markdown(f"**Requested**: {transfer['created_at'][:16]}")
                if transfer['processed_at']:
                    st.markdown(f"**Processed**: {transfer['processed_at'][:16]}")
            
            with col2:
                st.markdown(f"""
                <div style="text-align: right;">
                    <span style="background: {status_style['bg']}; color: {status_style['text']}; 
                               padding: 0.25rem 0.6rem; border-radius: 15px; font-size: 0.8rem; font-weight: bold;">
                        {status_style['emoji']} {transfer['status']}
                    </span>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")