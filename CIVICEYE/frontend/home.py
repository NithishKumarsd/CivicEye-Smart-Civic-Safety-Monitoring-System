"""
CIVICEYE Home Page
Professional landing page with system overview and role selection
"""

import streamlit as st
from database.db import db
from utils.constants import DEPARTMENTS, TAMIL_NADU_DISTRICTS

def show_home_page():
    """Display the main landing page"""
    
    # Hero Section
    st.markdown("""
    <div class="main-header">
        <h1>🏙️ CIVICEYE</h1>
        <p>Smart City Complaint Management Platform</p>
        <p style="font-size: 1rem; margin-top: 1rem; opacity: 0.9;">
            Empowering citizens • AI-powered routing • Real-time tracking • Transparent governance
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick Stats Section
    show_platform_stats()
    
    # Role Selection Section
    st.markdown("## 👥 **Choose Your Role**")
    st.markdown("Select your role to access the appropriate dashboard and features.")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="info-card" style="text-align: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">🏠</div>
            <h3>Citizen Portal</h3>
            <p>Report civic issues and track resolutions</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 Access Citizen Portal", key="citizen_portal", use_container_width=True):
            st.session_state.page = 'login'
            st.session_state.login_type = 'citizen'
            st.rerun()
        
        with st.expander("📋 What Citizens Can Do"):
            st.markdown("""
            **Submit Complaints About:**
            - 🛣️ Road damage and potholes
            - 🗑️ Garbage overflow and waste issues
            - 💡 Street light failures
            - 💧 Water supply problems
            - ⚡ Electrical issues
            - 🚔 Public safety concerns
            
            **Features:**
            - 📸 Photo/video upload
            - 🤖 AI urgency prediction
            - 📍 GPS location tagging
            - 📊 Real-time status tracking
            - 💬 Public reviews and comments
            - 📧 Email notifications
            """)
    
    with col2:
        st.markdown("""
        <div class="info-card" style="text-align: center; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">👮</div>
            <h3>Department Officer</h3>
            <p>Manage and resolve citizen complaints</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("⚡ Access Officer Portal", key="officer_portal", use_container_width=True):
            st.session_state.page = 'login'
            st.session_state.login_type = 'department_officer'
            st.rerun()
        
        with st.expander("🔧 Officer Capabilities"):
            st.markdown("""
            **Department Responsibilities:**
            - 🛣️ **Roads**: Infrastructure, potholes, signals
            - 🧹 **Sanitation**: Waste, cleanliness, drainage
            - ⚡ **Electricity**: Street lights, power supply
            - 🚔 **Public Safety**: Security, emergencies
            
            **Officer Tools:**
            - 📋 Complaint queue management
            - 🎯 AI-prioritized assignments
            - 📝 Internal notes and updates
            - 🔄 Status change tracking
            - 📊 Performance analytics
            - 🚨 SLA deadline monitoring
            """)
    
    with col3:
        st.markdown("""
        <div class="info-card" style="text-align: center; background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">👑</div>
            <h3>Administrator</h3>
            <p>System oversight and management</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🎯 Access Admin Portal", key="admin_portal", use_container_width=True):
            st.session_state.page = 'login'
            st.session_state.login_type = 'admin'
            st.rerun()
        
        with st.expander("⚙️ Admin Powers"):
            st.markdown("""
            **System Management:**
            - 👁️ View all complaints across departments
            - 🔄 Approve/deny reroute requests
            - 🔗 Merge related complaints
            - 🚨 Emergency escalation
            - ⚠️ Department warnings
            
            **Analytics & Control:**
            - 📊 Performance dashboards
            - 📈 Resolution analytics
            - 🔍 Audit trail monitoring
            - 🛠️ System configuration
            - 👥 User management
            """)
    
    # Features Showcase
    st.markdown("---")
    st.markdown("## 🌟 **Platform Features**")
    
    feature_col1, feature_col2, feature_col3 = st.columns(3)
    
    with feature_col1:
        st.markdown("""
        <div class="info-card">
            <div style="text-align: center; font-size: 3rem; color: #667eea; margin-bottom: 1rem;">🤖</div>
            <h4>AI-Powered Intelligence</h4>
            <p>Advanced machine learning algorithms automatically:</p>
            <ul>
                <li>Predict complaint urgency levels</li>
                <li>Route to appropriate departments</li>
                <li>Estimate resolution timeframes</li>
                <li>Detect emergency situations</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with feature_col2:
        st.markdown("""
        <div class="info-card">
            <div style="text-align: center; font-size: 3rem; color: #f093fb; margin-bottom: 1rem;">📊</div>
            <h4>Real-Time Tracking</h4>
            <p>Complete transparency with:</p>
            <ul>
                <li>Live status updates</li>
                <li>SLA deadline monitoring</li>
                <li>Performance analytics</li>
                <li>Resolution progress tracking</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with feature_col3:
        st.markdown("""
        <div class="info-card">
            <div style="text-align: center; font-size: 3rem; color: #4facfe; margin-bottom: 1rem;">🔒</div>
            <h4>Secure & Scalable</h4>
            <p>Enterprise-grade security:</p>
            <ul>
                <li>Role-based access control</li>
                <li>Encrypted data storage</li>
                <li>Audit trail logging</li>
                <li>Mobile-first design</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # System Information
    st.markdown("---")
    st.markdown("## 📍 **Coverage Area**")
    
    info_col1, info_col2 = st.columns(2)
    
    with info_col1:
        st.markdown("""
        <div class="info-card">
            <h4>🗺️ Service Coverage</h4>
            <p><strong>State:</strong> Tamil Nadu</p>
            <p><strong>Districts Covered:</strong> All 37 districts</p>
            <p><strong>Population Served:</strong> 75+ Million</p>
            <p><strong>Languages:</strong> Tamil, English</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Show some districts
        st.markdown("**Major Districts:**")
        major_districts = ["Chennai", "Coimbatore", "Madurai", "Salem", "Tiruchirappalli", "Tirunelveli"]
        for district in major_districts:
            st.markdown(f"• {district}")
    
    with info_col2:
        st.markdown("""
        <div class="info-card">
            <h4>🏢 Department Coverage</h4>
        </div>
        """, unsafe_allow_html=True)
        
        for dept_name, dept_info in DEPARTMENTS.items():
            st.markdown(f"""
            **{dept_name}**  
            {dept_info['description']}
            """)
    
    # How It Works Section
    st.markdown("---")
    st.markdown("## 🔄 **How It Works**")
    
    step_col1, step_col2, step_col3, step_col4 = st.columns(4)
    
    with step_col1:
        st.markdown("""
        <div class="info-card" style="text-align: center;">
            <div style="font-size: 3rem; color: #667eea;">1️⃣</div>
            <h4>Submit</h4>
            <p>Citizens report issues with photos and location details</p>
        </div>
        """, unsafe_allow_html=True)
    
    with step_col2:
        st.markdown("""
        <div class="info-card" style="text-align: center;">
            <div style="font-size: 3rem; color: #f093fb;">2️⃣</div>
            <h4>AI Analysis</h4>
            <p>System predicts urgency and routes to appropriate department</p>
        </div>
        """, unsafe_allow_html=True)
    
    with step_col3:
        st.markdown("""
        <div class="info-card" style="text-align: center;">
            <div style="font-size: 3rem; color: #4facfe;">3️⃣</div>
            <h4>Resolution</h4>
            <p>Department officers work on the issue with real-time updates</p>
        </div>
        """, unsafe_allow_html=True)
    
    with step_col4:
        st.markdown("""
        <div class="info-card" style="text-align: center;">
            <div style="font-size: 3rem; color: #28a745;">4️⃣</div>
            <h4>Feedback</h4>
            <p>Citizens provide feedback to improve service quality</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Call to Action
    st.markdown("---")
    st.markdown("## 🚀 **Get Started Today**")
    
    cta_col1, cta_col2, cta_col3 = st.columns([1, 2, 1])
    
    with cta_col2:
        st.markdown("""
        <div class="info-card" style="text-align: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
            <h3>Ready to Make Your City Better?</h3>
            <p>Join thousands of citizens already using CIVICEYE to improve their communities.</p>
        </div>
        """, unsafe_allow_html=True)
        
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.button("📝 Register as Citizen", key="register_citizen", use_container_width=True):
                st.session_state.page = 'register'
                st.rerun()
        
        with col_btn2:
            if st.button("🔑 Login to Account", key="login_account", use_container_width=True):
                st.session_state.page = 'login'
                st.rerun()

def show_platform_stats():
    """Display platform statistics"""
    st.markdown("## 📊 **Platform Impact**")
    
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Get statistics
        cursor.execute("SELECT COUNT(*) FROM complaints")
        total_complaints = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM complaints WHERE status = 'Resolved'")
        resolved_complaints = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM department_officers")
        total_officers = cursor.fetchone()[0]
        
        # Calculate resolution rate
        resolution_rate = (resolved_complaints / total_complaints * 100) if total_complaints > 0 else 0
        
        # Get average resolution time
        cursor.execute("""
            SELECT AVG(
                (JULIANDAY(resolved_at) - JULIANDAY(created_at)) * 24
            ) as avg_hours
            FROM complaints
            WHERE status = 'Resolved' AND resolved_at IS NOT NULL
        """)
        result = cursor.fetchone()
        avg_resolution_hours = result[0] if result[0] else 0
        
        conn.close()
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-container">
                <h2 style="color: #667eea; font-size: 2.5rem; margin: 0;">{total_complaints:,}</h2>
                <p style="margin: 0.5rem 0 0 0; font-weight: 600;">Total Complaints</p>
                <p style="margin: 0; color: #666; font-size: 0.9rem;">Submitted by citizens</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-container">
                <h2 style="color: #28a745; font-size: 2.5rem; margin: 0;">{resolution_rate:.1f}%</h2>
                <p style="margin: 0.5rem 0 0 0; font-weight: 600;">Resolution Rate</p>
                <p style="margin: 0; color: #666; font-size: 0.9rem;">{resolved_complaints:,} issues resolved</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-container">
                <h2 style="color: #f093fb; font-size: 2.5rem; margin: 0;">{total_users:,}</h2>
                <p style="margin: 0.5rem 0 0 0; font-weight: 600;">Active Citizens</p>
                <p style="margin: 0; color: #666; font-size: 0.9rem;">Registered users</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            if avg_resolution_hours > 0:
                if avg_resolution_hours < 24:
                    time_display = f"{avg_resolution_hours:.1f}h"
                else:
                    time_display = f"{avg_resolution_hours/24:.1f}d"
            else:
                time_display = "N/A"
            
            st.markdown(f"""
            <div class="metric-container">
                <h2 style="color: #4facfe; font-size: 2.5rem; margin: 0;">{time_display}</h2>
                <p style="margin: 0.5rem 0 0 0; font-weight: 600;">Avg Resolution</p>
                <p style="margin: 0; color: #666; font-size: 0.9rem;">Response time</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Recent activity section removed for performance
    
    except Exception as e:
        st.warning("Statistics temporarily unavailable")
        
        # Show placeholder stats
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Complaints", "Loading...")
        with col2:
            st.metric("Resolution Rate", "Loading...")
        with col3:
            st.metric("Active Citizens", "Loading...")
        with col4:
            st.metric("Avg Resolution", "Loading...")