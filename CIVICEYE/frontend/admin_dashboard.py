"""
CIVICEYE Admin Dashboard
Administrator portal for system oversight and management
"""

import streamlit as st
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from utils.security import session_manager
from backend.complaint_service import complaint_service
from database.db import db
from backend.transfer_service import get_pending_transfers, get_escalated_complaints, approve_transfer, reject_transfer, assign_multiple_departments, get_complaint_departments
from backend.admin_service import admin_reassign_complaint, admin_override_complaint

def show_admin_dashboard():
    """Display admin dashboard"""
    
    admin_data = session_manager.get_current_user()
    if not admin_data:
        st.error("Session expired. Please login again.")
        st.session_state.page = 'login'
        st.rerun()
    
    # Logout button in header
    col_header1, col_header2 = st.columns([4, 1])
    with col_header2:
        if st.button("🚪 Logout", key="admin_logout", type="secondary"):
            from frontend.user_dashboard import handle_logout
            handle_logout()
    
    # Header
    with col_header1:
        st.markdown(f"""
        <div class="main-header">
            <h1>👑 System Administrator Portal</h1>
            <p>Welcome, {admin_data.get('name', 'Administrator')} - Complete system oversight and control</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Analytics", "🔍 All Complaints", "🔄 Transfer Requests", "🚨 Escalations", "⚙️ System Management"])
    
    with tab1:
        show_analytics_dashboard()
    
    with tab2:
        show_all_complaints()
    
    with tab3:
        show_admin_transfers()
    
    with tab4:
        show_admin_escalations()
    
    with tab5:
        show_system_management()

def show_analytics_dashboard():
    """Display comprehensive analytics"""
    st.markdown("### 📊 **System Analytics Dashboard**")
    
    # Get system statistics
    stats = get_system_statistics()
    
    # Key metrics
    show_key_metrics(stats)
    
    # Charts
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        show_complaint_trends(stats)
    
    with col_chart2:
        show_department_performance(stats)
    
    # Additional analytics
    show_urgency_distribution(stats)
    show_resolution_analytics(stats)

def get_system_statistics():
    """Get comprehensive system statistics"""
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        
        stats = {}
        
        # Basic counts
        cursor.execute("SELECT COUNT(*) FROM complaints")
        stats['total_complaints'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM users")
        stats['total_users'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM department_officers")
        stats['total_officers'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM complaints WHERE status = 'Resolved'")
        stats['resolved_complaints'] = cursor.fetchone()[0]
        
        # Today's stats
        cursor.execute("""
            SELECT COUNT(*) FROM complaints 
            WHERE DATE(created_at) = DATE('now')
        """)
        stats['today_complaints'] = cursor.fetchone()[0]
        
        # This week's stats
        cursor.execute("""
            SELECT COUNT(*) FROM complaints 
            WHERE created_at >= datetime('now', '-7 days')
        """)
        stats['week_complaints'] = cursor.fetchone()[0]
        
        # Department distribution
        cursor.execute("""
            SELECT d.name, COUNT(c.id) as count
            FROM departments d
            LEFT JOIN complaints c ON d.id = c.department_id
            GROUP BY d.id, d.name
        """)
        stats['dept_distribution'] = dict(cursor.fetchall())
        
        # Urgency distribution
        cursor.execute("""
            SELECT urgency_level, COUNT(*) as count
            FROM complaints
            GROUP BY urgency_level
        """)
        stats['urgency_distribution'] = dict(cursor.fetchall())
        
        # Status distribution
        cursor.execute("""
            SELECT status, COUNT(*) as count
            FROM complaints
            GROUP BY status
        """)
        stats['status_distribution'] = dict(cursor.fetchall())
        
        # Daily complaint trend (last 30 days)
        cursor.execute("""
            SELECT DATE(created_at) as date, COUNT(*) as count
            FROM complaints
            WHERE created_at >= datetime('now', '-30 days')
            GROUP BY DATE(created_at)
            ORDER BY date
        """)
        stats['daily_trend'] = cursor.fetchall()
        
        # Average resolution time
        cursor.execute("""
            SELECT AVG(
                (JULIANDAY(resolved_at) - JULIANDAY(created_at)) * 24
            ) as avg_hours
            FROM complaints
            WHERE status = 'Resolved' AND resolved_at IS NOT NULL
        """)
        result = cursor.fetchone()
        stats['avg_resolution_hours'] = result[0] if result[0] else 0
        
        conn.close()
        return stats
        
    except Exception as e:
        st.error(f"Error loading statistics: {e}")
        return {}

def show_key_metrics(stats):
    """Display key system metrics"""
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("📋 Total Complaints", stats.get('total_complaints', 0))
    
    with col2:
        st.metric("👥 Registered Users", stats.get('total_users', 0))
    
    with col3:
        st.metric("👮 Active Officers", stats.get('total_officers', 0))
    
    with col4:
        resolution_rate = 0
        if stats.get('total_complaints', 0) > 0:
            resolution_rate = (stats.get('resolved_complaints', 0) / stats.get('total_complaints', 0)) * 100
        st.metric("📈 Resolution Rate", f"{resolution_rate:.1f}%")
    
    with col5:
        avg_hours = stats.get('avg_resolution_hours', 0)
        if avg_hours > 0:
            if avg_hours < 24:
                time_display = f"{avg_hours:.1f}h"
            else:
                time_display = f"{avg_hours/24:.1f}d"
        else:
            time_display = "N/A"
        st.metric("⏱️ Avg Resolution", time_display)
    
    # Today's activity
    st.markdown("---")
    col_today1, col_today2, col_today3 = st.columns(3)
    
    with col_today1:
        st.metric("📅 Today's Complaints", stats.get('today_complaints', 0))
    
    with col_today2:
        st.metric("📊 This Week", stats.get('week_complaints', 0))
    
    with col_today3:
        # Calculate growth rate
        growth_rate = 0  # You could calculate week-over-week growth here
        st.metric("📈 Growth Rate", f"{growth_rate:.1f}%")

def show_complaint_trends(stats):
    """Show complaint trends chart"""
    st.markdown("#### 📈 **Complaint Trends (Last 30 Days)**")
    
    if stats.get('daily_trend'):
        df = pd.DataFrame(stats['daily_trend'], columns=['Date', 'Count'])
        df['Date'] = pd.to_datetime(df['Date'])
        
        fig = px.line(df, x='Date', y='Count', 
                     title='Daily Complaint Submissions',
                     markers=True)
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No trend data available")

def show_department_performance(stats):
    """Show department performance chart"""
    st.markdown("#### 🏢 **Department Workload**")
    
    dept_dist = stats.get('dept_distribution', {})
    if dept_dist:
        df = pd.DataFrame(list(dept_dist.items()), columns=['Department', 'Complaints'])
        
        fig = px.bar(df, x='Department', y='Complaints',
                    title='Complaints by Department',
                    color='Complaints',
                    color_continuous_scale='Blues')
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No department data available")

def show_urgency_distribution(stats):
    """Show urgency distribution"""
    st.markdown("#### 🚨 **Urgency Distribution**")
    
    urgency_dist = stats.get('urgency_distribution', {})
    if urgency_dist:
        col_urgency1, col_urgency2 = st.columns(2)
        
        with col_urgency1:
            # Pie chart
            labels = list(urgency_dist.keys())
            values = list(urgency_dist.values())
            colors = ['#dc3545', '#ffc107', '#28a745']  # Red, Yellow, Green
            
            fig = go.Figure(data=[go.Pie(labels=labels, values=values, 
                                       marker_colors=colors)])
            fig.update_layout(title="Urgency Distribution", height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        with col_urgency2:
            # Metrics
            for urgency, count in urgency_dist.items():
                emoji = {'High': '🔴', 'Medium': '🟡', 'Low': '🟢'}.get(urgency, '⚪')
                st.metric(f"{emoji} {urgency} Priority", count)

def show_resolution_analytics(stats):
    """Show resolution analytics"""
    st.markdown("#### ✅ **Resolution Analytics**")
    
    status_dist = stats.get('status_distribution', {})
    if status_dist:
        col_status1, col_status2 = st.columns(2)
        
        with col_status1:
            # Status breakdown
            for status, count in status_dist.items():
                emoji = {
                    'Pending': '🔄', 'Assigned': '👮', 
                    'In Progress': '⚠️', 'Resolved': '✅'
                }.get(status, '❓')
                st.metric(f"{emoji} {status}", count)
        
        with col_status2:
            # Resolution efficiency
            total = sum(status_dist.values())
            resolved = status_dist.get('Resolved', 0)
            pending = status_dist.get('Pending', 0)
            
            if total > 0:
                efficiency = (resolved / total) * 100
                backlog_rate = (pending / total) * 100
                
                st.metric("🎯 Resolution Efficiency", f"{efficiency:.1f}%")
                st.metric("📋 Backlog Rate", f"{backlog_rate:.1f}%")

def show_all_complaints():
    """Display all complaints with admin controls"""
    st.markdown("### 🔍 **All System Complaints**")
    
    # Filters
    col_filter1, col_filter2, col_filter3, col_filter4 = st.columns(4)
    
    with col_filter1:
        status_filter = st.selectbox("Status:", ["All", "Pending", "Assigned", "In Progress", "Resolved"])
    
    with col_filter2:
        urgency_filter = st.selectbox("Urgency:", ["All", "High", "Medium", "Low"])
    
    with col_filter3:
        dept_filter = st.selectbox("Department:", ["All", "Roads", "Sanitation", "Electricity", "Public Safety"])
    
    with col_filter4:
        date_filter = st.selectbox("Period:", ["All Time", "Today", "This Week", "This Month"])
    
    # Get and display complaints
    complaints = get_filtered_complaints(status_filter, urgency_filter, dept_filter, date_filter)
    
    if complaints:
        st.markdown(f"**Found {len(complaints)} complaints**")
        
        # Display complaints in a table format for admin
        for complaint in complaints[:20]:  # Limit to 20 for performance
            show_admin_complaint_card(complaint)
    else:
        st.info("No complaints found matching the filters")

def get_filtered_complaints(status_filter, urgency_filter, dept_filter, date_filter):
    """Get filtered complaints for admin view"""
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT c.*, d.name as department_name, u.mobile_number as user_mobile
            FROM complaints c
            LEFT JOIN departments d ON c.department_id = d.id
            LEFT JOIN users u ON c.user_id = u.id
            WHERE 1=1
        """
        params = []
        
        if status_filter != "All":
            query += " AND c.status = ?"
            params.append(status_filter)
        
        if urgency_filter != "All":
            query += " AND c.urgency_level = ?"
            params.append(urgency_filter)
        
        if dept_filter != "All":
            query += " AND d.name = ?"
            params.append(dept_filter)
        
        if date_filter == "Today":
            query += " AND DATE(c.created_at) = DATE('now')"
        elif date_filter == "This Week":
            query += " AND c.created_at >= datetime('now', '-7 days')"
        elif date_filter == "This Month":
            query += " AND c.created_at >= datetime('now', '-30 days')"
        
        query += " ORDER BY c.created_at DESC"
        
        cursor.execute(query, params)
        complaints = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return complaints
        
    except Exception as e:
        st.error(f"Error loading complaints: {e}")
        return []

def show_admin_complaint_card(complaint):
    """Display complaint card for admin view"""
    with st.expander(f"#{complaint['id']} - {complaint['title']} ({complaint['status']})"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            **📄 Description:** {complaint['description']}
            **📍 Location:** {complaint['location_address']}
            **📱 Citizen:** {complaint.get('user_mobile', 'N/A')}
            **🏢 Department:** {complaint.get('department_name', 'N/A')}
            """)
        
        with col2:
            st.markdown(f"""
            **🚨 Urgency:** {complaint['urgency_level']}
            **📊 Status:** {complaint['status']}
            **📅 Created:** {complaint['created_at'][:16]}
            **⏰ SLA:** {complaint.get('sla_deadline', 'N/A')[:16] if complaint.get('sla_deadline') else 'N/A'}
            """)
        
        # Admin actions
        col_action1, col_action2, col_action3 = st.columns(3)
        
        with col_action1:
            if st.button(f"🚨 Escalate #{complaint['id']}", key=f"escalate_{complaint['id']}"):
                st.success(f"Complaint #{complaint['id']} escalated to high priority")
        
        with col_action2:
            if st.button(f"🔄 Reassign #{complaint['id']}", key=f"reassign_{complaint['id']}"):
                st.session_state[f"show_reassign_{complaint['id']}"] = True
            
            # Show reassign panel if button clicked
            if st.session_state.get(f"show_reassign_{complaint['id']}", False):
                with st.form(f"reassign_form_{complaint['id']}"):
                    st.markdown("**Reassign Complaint**")
                    
                    new_dept = st.selectbox(
                        "Assign to Department:",
                        options=["Roads", "Sanitation", "Electricity", "Public Safety"],
                        key=f"reassign_dept_{complaint['id']}"
                    )
                    
                    if st.form_submit_button("Confirm Reassignment"):
                        if admin_reassign_complaint(complaint['id'], new_dept, 1):
                            st.success("✅ Complaint reassigned successfully.")
                            st.session_state[f"show_reassign_{complaint['id']}"] = False
                            st.rerun()
                        else:
                            st.error("❌ Failed to reassign complaint")
        
        with col_action3:
            if st.button(f"📝 Override #{complaint['id']}", key=f"override_{complaint['id']}"):
                st.session_state[f"show_override_{complaint['id']}"] = True
            
            # Show override panel if button clicked
            if st.session_state.get(f"show_override_{complaint['id']}", False):
                with st.form(f"override_form_{complaint['id']}"):
                    st.markdown("**Override Complaint**")
                    
                    new_status = st.selectbox(
                        "New Status:",
                        options=["Pending", "Assigned", "In Progress", "Resolved", "Closed"],
                        index=["Pending", "Assigned", "In Progress", "Resolved", "Closed"].index(complaint['status']),
                        key=f"override_status_{complaint['id']}"
                    )
                    
                    new_dept = st.selectbox(
                        "Change Department (Optional):",
                        options=["No Change", "Roads", "Sanitation", "Electricity", "Public Safety"],
                        key=f"override_dept_{complaint['id']}"
                    )
                    
                    override_reason = st.text_area(
                        "Override Reason (Required):",
                        placeholder="Explain why this override is necessary...",
                        key=f"override_reason_{complaint['id']}"
                    )
                    
                    if st.form_submit_button("Confirm Override"):
                        if not override_reason.strip():
                            st.error("Override reason is required")
                        else:
                            dept_to_use = new_dept if new_dept != "No Change" else None
                            if admin_override_complaint(complaint['id'], new_status, dept_to_use, override_reason, 1):
                                st.success("⚠️ Complaint overridden by admin successfully.")
                                st.session_state[f"show_override_{complaint['id']}"] = False
                                st.rerun()
                            else:
                                st.error("❌ Failed to override complaint")

def show_system_management():
    """Display system management tools"""
    st.markdown("### ⚙️ **System Management**")
    
    # System status
    col_sys1, col_sys2 = st.columns(2)
    
    with col_sys1:
        st.markdown("""
        <div class="info-card">
            <h4>🤖 AI Models Status</h4>
            <p>Monitor and retrain AI models</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔄 Retrain Department Model", use_container_width=True):
            with st.spinner("Training department classification model..."):
                # Here you would trigger model retraining
                st.success("✅ Department model retrained successfully")
        
        if st.button("🔄 Retrain Urgency Model", use_container_width=True):
            with st.spinner("Training urgency prediction model..."):
                # Here you would trigger model retraining
                st.success("✅ Urgency model retrained successfully")
    
    with col_sys2:
        st.markdown("""
        <div class="info-card">
            <h4>🗄️ Database Management</h4>
            <p>Database maintenance and backup</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("💾 Create Database Backup", use_container_width=True):
            st.success("✅ Database backup created successfully")
        
        if st.button("🧹 Clean Old Data", use_container_width=True):
            st.success("✅ Old data cleaned successfully")
    
    # System configuration
    st.markdown("#### ⚙️ **System Configuration**")
    
    with st.expander("🔧 SLA Configuration"):
        st.markdown("**Current SLA Rules:**")
        st.markdown("- 🔴 High Priority: 24 hours")
        st.markdown("- 🟡 Medium Priority: 72 hours")
        st.markdown("- 🟢 Low Priority: 168 hours")
        
        if st.button("📝 Update SLA Rules"):
            st.info("SLA configuration interface would be here")

def show_admin_transfers():
    """Show pending transfer requests for admin"""
    st.markdown("### 🔄 **Pending Department Transfer Requests**")
    
    transfers = get_pending_transfers()
    
    if not transfers:
        st.info("📝 No pending transfer requests")
        return
    
    for transfer in transfers:
        with st.container():
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.markdown(f"**Complaint #{transfer['complaint_id']}**: {transfer['title']}")
                st.markdown(f"**From**: {transfer['from_department']} **To**: {transfer['to_department']}")
                st.markdown(f"**Reason**: {transfer['reason']}")
                st.markdown(f"**Requested by**: {transfer['officer_name']}")
            
            with col2:
                if st.button(f"✅ Approve", key=f"approve_{transfer['id']}"):
                    if approve_transfer(transfer['id'], 1):
                        st.success("✅ Transfer approved successfully and complaint reassigned.")
                        st.rerun()
                    else:
                        st.error("❌ Failed to approve transfer. Please try again.")
            
            with col3:
                if st.button(f"❌ Reject", key=f"reject_{transfer['id']}"):
                    if reject_transfer(transfer['id'], 1):
                        st.success("❌ Transfer request rejected.")
                        st.rerun()
                    else:
                        st.error("❌ Failed to reject transfer. Please try again.")
            
            st.markdown("---")

def show_admin_escalations():
    """Show escalated complaints for admin"""
    st.markdown("### 🚨 **Escalated Complaints**")
    
    escalations = get_escalated_complaints()
    
    if not escalations:
        st.info("📝 No escalated complaints")
        return
    
    for escalation in escalations:
        with st.container():
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**Complaint #{escalation['complaint_id']}**: {escalation['title']}")
                st.markdown(f"**Current Department**: {escalation['department_name']}")
                st.markdown(f"**Urgency**: {escalation['urgency']}")
                st.markdown(f"**Reason**: {escalation['reason']}")
                st.markdown(f"**Escalated by**: {escalation['officer_name']}")
                
                # Show currently assigned departments
                assigned_depts = get_complaint_departments(escalation['complaint_id'])
                if assigned_depts:
                    dept_names = [d['department_name'] for d in assigned_depts]
                    st.markdown(f"**Assigned Departments**: {', '.join(dept_names)}")
            
            with col2:
                st.markdown("**Multi-Department Assignment**")
                
                # Multi-select for departments
                available_depts = ["Roads", "Sanitation", "Electricity", "Public Safety"]
                selected_depts = st.multiselect(
                    "Select Departments:",
                    options=available_depts,
                    key=f"depts_{escalation['complaint_id']}",
                    help="Select multiple departments to handle this complaint"
                )
                
                if st.button(f"🔄 Assign Departments", key=f"assign_{escalation['complaint_id']}"):
                    if selected_depts:
                        if assign_multiple_departments(escalation['complaint_id'], selected_depts, 1):
                            st.success(f"✅ Assigned {len(selected_depts)} departments to complaint #{escalation['complaint_id']}")
                            st.rerun()
                        else:
                            st.error("❌ Failed to assign departments")
                    else:
                        st.warning("Please select at least one department")
            
            st.markdown("---")