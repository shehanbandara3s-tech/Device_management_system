import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import re
import hashlib

# --- Configuration ---
EXCEL_FILE = 'device_management.xlsx'
USERS_FILE = 'users.xlsx'
COLUMNS = [
    'Device_ID', 'Category', 'Status', 'Name', 'IP_Address', 
    'Date_Added', 'Department', 'AD_Username', 'Email_Address', 
    'Internet_Access', 'Disposal_Date'
]

# Default admin credentials
DEFAULT_ADMIN = {
    'username': 'admin',
    'password': 'admin123',  # Change this in production!
    'role': 'Admin',
    'name': 'System Administrator'
}

# --- Authentication Functions ---
def hash_password(password):
    """Hash password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    """Load users from Excel file."""
    try:
        df = pd.read_excel(USERS_FILE)
        return df
    except FileNotFoundError:
        # Create default admin user
        df = pd.DataFrame([{
            'username': DEFAULT_ADMIN['username'],
            'password': hash_password(DEFAULT_ADMIN['password']),
            'role': DEFAULT_ADMIN['role'],
            'name': DEFAULT_ADMIN['name']
        }])
        df.to_excel(USERS_FILE, index=False)
        return df

def verify_login(username, password):
    """Verify login credentials."""
    users_df = load_users()
    user = users_df[users_df['username'] == username]
    
    if len(user) == 0:
        return False, None, None
    
    stored_password = user.iloc[0]['password']
    hashed_input = hash_password(password)
    
    if stored_password == hashed_input:
        return True, user.iloc[0]['role'], user.iloc[0]['name']
    return False, None, None

def display_login_page():
    """Display modern login page."""
    st.markdown("""
        <style>
        .login-container {
            max-width: 400px;
            margin: 100px auto;
            padding: 40px;
            background: white;
            border-radius: 16px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }
        .login-header {
            text-align: center;
            color: #1f2937;
            margin-bottom: 30px;
        }
        .login-icon {
            font-size: 60px;
            text-align: center;
            margin-bottom: 20px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-icon">💻</div>', unsafe_allow_html=True)
        st.markdown('<h1 class="login-header">Device Management System</h1>', unsafe_allow_html=True)
        st.markdown('<h3 style="text-align: center; color: #6b7280; margin-bottom: 30px;">Sign In</h3>', unsafe_allow_html=True)
        
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("👤 Username", placeholder="Enter your username", key="login_username")
            password = st.text_input("🔒 Password", type="password", placeholder="Enter your password", key="login_password")
            
            st.write("")  # Spacing
            
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                submit = st.form_submit_button("🔓 Login", use_container_width=True, type="primary")
            
            with col_btn2:
                clear = st.form_submit_button("🔄 Clear", use_container_width=True)
            
            if submit:
                if not username or not password:
                    st.error("❌ Please enter both username and password")
                else:
                    success, role, name = verify_login(username, password)
                    
                    if success:
                        st.session_state['authenticated'] = True
                        st.session_state['username'] = username
                        st.session_state['role'] = role
                        st.session_state['user_name'] = name
                        st.success(f"✅ Welcome, {name}!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or password")
            
            if clear:
                st.rerun()
        
        st.markdown("---")
        
        # Default credentials info (remove in production)
        with st.expander("ℹ️ Default Login Credentials"):
            st.info("""
            **Default Admin Account:**
            - Username: `admin`
            - Password: `admin123`
            
            ⚠️ **Important:** Change the default password after first login!
            """)
        
        st.markdown('<p style="text-align: center; color: #9ca3af; margin-top: 30px;">v2.0 | Secure Edition</p>', unsafe_allow_html=True)

def logout():
    """Logout and clear session."""
    st.session_state['authenticated'] = False
    st.session_state['username'] = None
    st.session_state['role'] = None
    st.session_state['user_name'] = None
    st.rerun()

# --- Styling ---
def apply_custom_css():
    st.markdown("""
        <style>
        .stApp {
            background-color: #f8f9fa;
        }
        
        [data-testid="stMetricValue"] {
            font-size: 28px;
            font-weight: 600;
        }
        
        .stButton button {
            border-radius: 8px;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        
        .stForm {
            background-color: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        [data-testid="stDataFrame"] {
            border-radius: 8px;
            overflow: hidden;
        }
        
        [data-testid="stSidebar"] {
            background-color: #ffffff;
        }
        
        .stSuccess, .stError, .stWarning, .stInfo {
            border-radius: 8px;
            padding: 12px;
        }
        
        h1, h2, h3 {
            color: #1f2937;
        }
        
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        
        .stTabs [data-baseweb="tab"] {
            border-radius: 8px 8px 0 0;
            padding: 12px 24px;
            font-weight: 500;
        }
        </style>
    """, unsafe_allow_html=True)

# --- Data Functions ---
@st.cache_data
def load_data():
    """Loads the Excel file with enhanced error handling."""
    try:
        df = pd.read_excel(EXCEL_FILE)
        df['Date_Added'] = pd.to_datetime(df['Date_Added'], errors='coerce').dt.date
        df['Disposal_Date'] = pd.to_datetime(df['Disposal_Date'], errors='coerce').dt.date
        df['Department'] = df['Department'].fillna('Not Specified')
        return df
    except FileNotFoundError:
        df = pd.DataFrame(columns=COLUMNS)
        save_data(df)
        return df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame(columns=COLUMNS)

def save_data(df):
    """Saves DataFrame with proper formatting."""
    try:
        df_to_save = df.copy()
        for col in ['Date_Added', 'Disposal_Date']:
            df_to_save[col] = df_to_save[col].astype(str).replace({'NaT': '', 'None': ''})
        df_to_save[COLUMNS].to_excel(EXCEL_FILE, index=False)
        load_data.clear()
        return True
    except Exception as e:
        st.error(f"Error saving data: {str(e)}")
        return False

def get_working_df(raw_df):
    """Filter out department placeholder rows."""
    return raw_df[~raw_df['Device_ID'].astype(str).str.startswith('DEPT_ADD_')].copy()

def validate_device_id(device_id, existing_ids):
    """Validate device ID format and uniqueness."""
    if not device_id or device_id.strip() == "":
        return False, "Device ID cannot be empty."
    if device_id in existing_ids:
        return False, f"Device ID '{device_id}' already exists."
    if len(device_id) > 50:
        return False, "Device ID must be less than 50 characters."
    return True, ""

def validate_email(email):
    """Validate email format."""
    if not email or email.strip() == "":
        return True, ""
    
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email.strip()):
        return False, "Please enter a valid email address (e.g., user@example.com)"
    return True, ""

def count_devices_with_email(df):
    """Count devices with valid email addresses."""
    if df.empty:
        return 0
    
    valid_emails = df['Email_Address'].apply(
        lambda x: isinstance(x, str) and x.strip() != '' and '@' in x
    )
    return valid_emails.sum()

# --- Dashboard with Charts ---
def display_enhanced_dashboard(df):
    """Enhanced dashboard with visualizations."""
    st.markdown("## 📊 Dashboard Overview")
    
    if df.empty:
        st.info("📭 No devices in the system yet. Start by adding your first device!")
        return
    
    # Summary metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    total = len(df)
    active = len(df[df['Status'] == 'Active'])
    disposed = len(df[df['Status'] == 'Disposed'])
    with_email = count_devices_with_email(df)
    with_internet = len(df[df['Internet_Access'] == 'Yes'])
    
    col1.metric("🖥️ Total Devices", total)
    col2.metric("✅ Active", active, delta=f"{(active/total*100):.1f}%")
    col3.metric("🗑️ Disposed", disposed)
    col4.metric("📧 With Email", with_email, delta=f"{(with_email/total*100):.1f}%")
    col5.metric("🌐 Internet", with_internet, delta=f"{(with_internet/total*100):.1f}%")
    
    st.markdown("---")
    
    # Charts Row 1
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.markdown("### 📦 Devices by Category")
        category_counts = df['Category'].value_counts().reset_index()
        category_counts.columns = ['Category', 'Count']
        fig1 = px.bar(category_counts, x='Category', y='Count', 
                      color='Count', color_continuous_scale='Blues',
                      text='Count')
        fig1.update_layout(showlegend=False, height=350)
        fig1.update_traces(textposition='outside')
        st.plotly_chart(fig1, use_container_width=True)
    
    with col_chart2:
        st.markdown("### 🔄 Status Distribution")
        status_counts = df['Status'].value_counts().reset_index()
        status_counts.columns = ['Status', 'Count']
        colors = {'Active': '#10b981', 'In Repair': '#f59e0b', 
                  'Disposed': '#ef4444', 'Storage': '#6366f1'}
        fig2 = px.pie(status_counts, values='Count', names='Status',
                      color='Status', color_discrete_map=colors,
                      hole=0.4)
        fig2.update_layout(height=350)
        st.plotly_chart(fig2, use_container_width=True)
    
    st.markdown("---")
    
    # Charts Row 2
    col_chart3, col_chart4 = st.columns(2)
    
    with col_chart3:
        st.markdown("### 🏢 Department Distribution")
        dept_counts = df['Department'].value_counts().head(10).reset_index()
        dept_counts.columns = ['Department', 'Count']
        fig3 = px.bar(dept_counts, x='Count', y='Department',
                      orientation='h', color='Count',
                      color_continuous_scale='Viridis', text='Count')
        fig3.update_layout(showlegend=False, height=350, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig3, use_container_width=True)
    
    with col_chart4:
        st.markdown("### 📅 Devices Added Over Time")
        df_time = df[df['Date_Added'].notna()].copy()
        if not df_time.empty:
            df_time['Date_Added'] = pd.to_datetime(df_time['Date_Added'])
            df_time['Month'] = df_time['Date_Added'].dt.to_period('M').astype(str)
            time_counts = df_time.groupby('Month').size().reset_index(name='Count')
            fig4 = px.line(time_counts, x='Month', y='Count', markers=True)
            fig4.update_layout(height=350)
            fig4.update_traces(line_color='#3b82f6', marker=dict(size=8))
            st.plotly_chart(fig4, use_container_width=True)
        else:
            st.info("No date data available for timeline visualization.")
    
    # Detailed Breakdown Table
    st.markdown("---")
    st.markdown("### 📊 Detailed Breakdown")
    
    col_table1, col_table2 = st.columns(2)
    
    with col_table1:
        st.markdown("**By Department & Status**")
        dept_status = df.groupby(['Department', 'Status']).size().unstack(fill_value=0)
        st.dataframe(dept_status, use_container_width=True)
    
    with col_table2:
        st.markdown("**By Category & Status**")
        cat_status = df.groupby(['Category', 'Status']).size().unstack(fill_value=0)
        st.dataframe(cat_status, use_container_width=True)

# --- Enhanced Form ---
def display_device_form(df, departments, mode='add', device_id=None):
    """Unified form for add/edit with better validation."""
    
    if mode == 'edit' and device_id:
        st.markdown(f"## ✏️ Edit Device: `{device_id}`")
        device_row = df[df['Device_ID'] == device_id].iloc[0]
    else:
        st.markdown("## ➕ Add New Device")
        device_row = None
    
    with st.form(key=f'device_form_{mode}', clear_on_submit=(mode=='add')):
        
        # Device Information Section
        st.markdown("#### 🖥️ Device Information")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if mode == 'add':
                device_id_input = st.text_input("Device ID *", placeholder="e.g., LAP-001")
            else:
                st.text_input("Device ID", value=device_id, disabled=True)
                device_id_input = device_id
            
            category = st.selectbox("Category *", 
                options=['Laptop', 'Desktop', 'Printer', 'Monitor', 'Server', 'Router', 'Switch', 'Other'],
                index=['Laptop', 'Desktop', 'Printer', 'Monitor', 'Server', 'Router', 'Switch', 'Other'].index(device_row['Category']) if device_row is not None else 0)
        
        with col2:
            status = st.selectbox("Status *", 
                options=['Active', 'In Repair', 'Disposed', 'Storage'],
                index=['Active', 'In Repair', 'Disposed', 'Storage'].index(device_row['Status']) if device_row is not None else 0)
            
            ip_address = st.text_input("IP Address", 
                value=device_row['IP_Address'] if device_row is not None else "",
                placeholder="e.g., 192.168.1.100")
        
        with col3:
            date_added = st.date_input("Date Added *", 
                value=device_row['Date_Added'] if device_row is not None else datetime.now().date())
            
            disposal_date_val = None if device_row is None or pd.isna(device_row['Disposal_Date']) else device_row['Disposal_Date']
            disposal_date = st.date_input("Disposal Date", value=disposal_date_val)
        
        st.markdown("---")
        
        # User Information Section
        st.markdown("#### 👤 User Information")
        col4, col5, col6 = st.columns(3)
        
        with col4:
            name = st.text_input("Name *", 
                value=device_row['Name'] if device_row is not None else "",
                placeholder="e.g., John Doe")
        
        with col5:
            dept_options = sorted([d for d in departments if d != 'Not Specified'])
            if device_row is not None:
                try:
                    dept_idx = dept_options.index(device_row['Department'])
                except ValueError:
                    dept_idx = 0
            else:
                dept_idx = 0
            
            department = st.selectbox("Department *", options=dept_options, index=dept_idx)
        
        with col6:
            ad_username = st.text_input("AD Username", 
                value=device_row['AD_Username'] if device_row is not None else "",
                placeholder="e.g., jdoe")
        
        st.markdown("---")
        
        # Access Information Section
        st.markdown("#### 🔐 Access Information")
        col7, col8 = st.columns(2)
        
        with col7:
            email = st.text_input("Email Address", 
                value=device_row['Email_Address'] if device_row is not None else "",
                placeholder="e.g., john.doe@company.com",
                help="Must be a valid email format")
        
        with col8:
            internet_options = ['Yes', 'No']
            internet_idx = 0
            if device_row is not None and device_row['Internet_Access'] in internet_options:
                internet_idx = internet_options.index(device_row['Internet_Access'])
            internet = st.selectbox("Internet Access", options=internet_options, index=internet_idx)
        
        # Email validation display outside columns
        if email and email.strip() != "":
            is_valid_email, email_error = validate_email(email)
            if not is_valid_email:
                st.error(f"⚠️ {email_error}")
            else:
                st.success("✅ Valid email format")
        
        st.markdown("---")
        
        # Submit buttons
        col_btn1, col_btn2 = st.columns([1, 5])
        
        with col_btn1:
            submitted = st.form_submit_button(
                "💾 Save Device" if mode == 'add' else "✅ Update Device",
                type="primary",
                use_container_width=True
            )
        
        with col_btn2:
            cancelled = st.form_submit_button("❌ Cancel", use_container_width=True)
        
        if cancelled:
            st.session_state['show_form'] = False
            st.session_state['edit_device_id'] = None
            st.rerun()
        
        if submitted:
            # Validation
            if not device_id_input or not name:
                st.error("❌ Device ID and Name are required fields.")
                st.stop()
            
            # Validate email if provided
            if email and email.strip() != "":
                is_valid_email, email_error = validate_email(email)
                if not is_valid_email:
                    st.error(f"❌ {email_error}")
                    st.stop()
            
            if mode == 'add':
                is_valid, error_msg = validate_device_id(device_id_input, df['Device_ID'].values)
                if not is_valid:
                    st.error(f"❌ {error_msg}")
                    st.stop()
            
            # Save data
            raw_df = load_data()
            
            new_data = {
                'Device_ID': device_id_input,
                'Category': category,
                'Status': status,
                'Name': name,
                'IP_Address': ip_address,
                'Date_Added': date_added,
                'Department': department,
                'AD_Username': ad_username,
                'Email_Address': email,
                'Internet_Access': internet,
                'Disposal_Date': disposal_date
            }
            
            if mode == 'add':
                new_row = pd.DataFrame([new_data])
                updated_df = pd.concat([raw_df, new_row], ignore_index=True)
            else:
                row_idx = raw_df[raw_df['Device_ID'] == device_id].index[0]
                for key, value in new_data.items():
                    raw_df.loc[row_idx, key] = value
                updated_df = raw_df
            
            if save_data(updated_df):
                st.success(f"✅ Device '{device_id_input}' {'added' if mode == 'add' else 'updated'} successfully!")
                st.session_state['show_form'] = False
                st.session_state['edit_device_id'] = None
                st.balloons()
                st.rerun()

# --- Enhanced Data Table ---
def display_data_table(df, departments):
    """Enhanced data table with advanced filtering."""
    
    st.markdown("## 📋 Device Inventory")
    
    if df.empty:
        st.info("📭 No devices found. Click 'Add New Device' to get started!")
        return
    
    # Advanced Filters
    with st.expander("🔍 Advanced Filters", expanded=True):
        col_f1, col_f2, col_f3 = st.columns(3)
        
        with col_f1:
            search = st.text_input("🔎 Search", placeholder="Search all fields...")
        
        with col_f2:
            categories = ['All'] + sorted(df['Category'].unique().tolist())
            category_filter = st.multiselect("Category", categories, default=['All'])
        
        with col_f3:
            statuses = ['All'] + sorted(df['Status'].unique().tolist())
            status_filter = st.multiselect("Status", statuses, default=['All'])
        
        # Second row of filters
        col_f4, col_f5, col_f6 = st.columns(3)
        
        with col_f4:
            dept_list = ['All'] + sorted([d for d in df['Department'].unique().tolist() if d != 'Not Specified'])
            department_filter = st.multiselect("Department", dept_list, default=['All'])
        
        with col_f5:
            email_filter = st.selectbox("Email", ['All', 'Has Email', 'No Email'])
        
        with col_f6:
            internet_filter = st.selectbox("Internet", ['All', 'Yes', 'No'])
    
    # Apply filters
    filtered_df = df.copy()
    
    if search:
        search_lower = search.lower()
        mask = (
            filtered_df['Device_ID'].astype(str).str.lower().str.contains(search_lower) |
            filtered_df['Name'].astype(str).str.lower().str.contains(search_lower) |
            filtered_df['IP_Address'].astype(str).str.lower().str.contains(search_lower) |
            filtered_df['Department'].astype(str).str.lower().str.contains(search_lower) |
            filtered_df['Email_Address'].astype(str).str.lower().str.contains(search_lower)
        )
        filtered_df = filtered_df[mask]
    
    if 'All' not in category_filter and category_filter:
        filtered_df = filtered_df[filtered_df['Category'].isin(category_filter)]
    
    if 'All' not in status_filter and status_filter:
        filtered_df = filtered_df[filtered_df['Status'].isin(status_filter)]
    
    if 'All' not in department_filter and department_filter:
        filtered_df = filtered_df[filtered_df['Department'].isin(department_filter)]
    
    if email_filter == 'Has Email':
        filtered_df = filtered_df[
            filtered_df['Email_Address'].apply(
                lambda x: isinstance(x, str) and x.strip() != '' and '@' in x
            )
        ]
    elif email_filter == 'No Email':
        filtered_df = filtered_df[
            filtered_df['Email_Address'].apply(
                lambda x: not isinstance(x, str) or x.strip() == '' or '@' not in x
            )
        ]
    
    if internet_filter != 'All':
        filtered_df = filtered_df[filtered_df['Internet_Access'] == internet_filter]
    
    # Results summary
    st.markdown(f"**Showing {len(filtered_df)} of {len(df)} devices**")
    
    # Bulk actions
    col_bulk1, col_bulk2, col_bulk3 = st.columns([2, 1, 1])
    
    with col_bulk1:
        selected_ids = st.multiselect(
            "Select devices for bulk actions:",
            options=filtered_df['Device_ID'].tolist(),
            placeholder="Select one or more devices..."
        )
    
    with col_bulk2:
        if st.button("📥 Export Data", use_container_width=True):
            st.session_state['show_export'] = True
    
    with col_bulk3:
        if selected_ids and st.button("🗑️ Bulk Delete", type="primary", use_container_width=True):
            st.session_state['bulk_delete_ids'] = selected_ids
            st.session_state['show_bulk_delete_confirm'] = True
    
    # Export dialog
    if st.session_state.get('show_export', False):
        with st.container():
            st.info("📥 Exporting filtered data...")
            
            # Export to Excel
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                filtered_df.to_excel(writer, index=False, sheet_name='Devices')
            excel_data = output.getvalue()
            
            col_exp1, col_exp2 = st.columns(2)
            with col_exp1:
                st.download_button(
                    label="📊 Download Excel",
                    data=excel_data,
                    file_name=f"devices_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.ms-excel"
                )
            
            with col_exp2:
                csv_data = filtered_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📄 Download CSV",
                    data=csv_data,
                    file_name=f"devices_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            
            st.session_state['show_export'] = False
    
    # Bulk delete confirmation
    if st.session_state.get('show_bulk_delete_confirm', False):
        st.markdown("---")
        selected_count = len(st.session_state.get('bulk_delete_ids', []))
        
        st.error(f"⚠️ **BULK DELETION CONFIRMATION**")
        st.warning(f"Are you sure you want to permanently delete **{selected_count}** device(s)?")
        st.write("")  # spacing
        
        col_confirm1, col_confirm2, col_confirm3 = st.columns([1, 1, 4])
        
        with col_confirm1:
            if st.button("✅ Yes, Delete All", type="primary", use_container_width=True, key="confirm_bulk_delete"):
                raw_df = load_data()
                ids_to_delete = st.session_state.get('bulk_delete_ids', [])
                updated_df = raw_df[~raw_df['Device_ID'].isin(ids_to_delete)]
                if save_data(updated_df):
                    st.success(f"✅ Successfully deleted {selected_count} device(s)!")
                    st.session_state['show_bulk_delete_confirm'] = False
                    st.session_state['bulk_delete_ids'] = []
                    st.balloons()
                    st.rerun()
        
        with col_confirm2:
            if st.button("❌ Cancel", use_container_width=True, key="cancel_bulk_delete"):
                st.session_state['show_bulk_delete_confirm'] = False
                st.session_state['bulk_delete_ids'] = []
                st.rerun()
    
    st.markdown("---")
    
    # Display table
    display_cols = ['Device_ID', 'Category', 'Status', 'Name', 'IP_Address', 
                    'Department', 'Internet_Access', 'Email_Address', 'Date_Added']
    
    st.dataframe(
        filtered_df[display_cols],
        use_container_width=True,
        hide_index=True,
        column_config={
            "Device_ID": st.column_config.TextColumn("Device ID", width="medium"),
            "Status": st.column_config.TextColumn("Status", width="small"),
            "Name": st.column_config.TextColumn("Name", width="medium"),
            "Date_Added": st.column_config.DateColumn("Date Added", format="YYYY-MM-DD")
        }
    )
    
    # Quick actions
    st.markdown("---")
    st.markdown("### ⚡ Quick Actions")
    
    col_action1, col_action2, col_action3 = st.columns([2, 1, 1])
    
    with col_action1:
        device_for_action = st.selectbox(
            "Select a device:",
            options=filtered_df['Device_ID'].tolist(),
            key='quick_action_selector'
        )
    
    with col_action2:
        if st.button("✏️ Edit", use_container_width=True):
            st.session_state['edit_device_id'] = device_for_action
            st.session_state['show_form'] = True
            st.rerun()
    
    with col_action3:
        if st.button("🗑️ Delete", type="primary", use_container_width=True):
            st.session_state['delete_device_id'] = device_for_action
            st.session_state['show_delete_confirm'] = True
            st.rerun()  # Force immediate rerun to show confirmation
    
    # Single delete confirmation - moved outside columns to prevent tab switching
    if st.session_state.get('show_delete_confirm', False):
        st.markdown("---")
        device_to_delete = st.session_state.get('delete_device_id')
        
        st.error(f"⚠️ **CONFIRM DELETION**")
        st.warning(f"Are you sure you want to permanently delete device: **{device_to_delete}**?")
        st.write("")  # spacing
        
        col_del1, col_del2, col_del3 = st.columns([1, 1, 4])
        with col_del1:
            if st.button("✅ Yes, Delete", type="primary", use_container_width=True, key="confirm_delete_single"):
                raw_df = load_data()
                updated_df = raw_df[raw_df['Device_ID'] != device_to_delete]
                if save_data(updated_df):
                    st.success(f"✅ Device '{device_to_delete}' deleted successfully!")
                    st.session_state['show_delete_confirm'] = False
                    st.session_state['delete_device_id'] = None
                    st.balloons()
                    st.rerun()
        
        with col_del2:
            if st.button("❌ Cancel", use_container_width=True, key="cancel_delete_single"):
                st.session_state['show_delete_confirm'] = False
                st.session_state['delete_device_id'] = None
                st.rerun()

# --- Department Management ---
def display_department_management(raw_df):
    """Department management interface with back button."""
    
    # Back button at the top
    col_back, col_spacer = st.columns([1, 5])
    with col_back:
        if st.button("⬅️ Back to Dashboard", use_container_width=True, key="back_top"):
            st.session_state['show_dept_mgmt'] = False
            st.rerun()
    
    st.markdown("---")
    
    departments = sorted([d for d in raw_df['Department'].unique() if d != 'Not Specified'])
    
    st.markdown("## 🏢 Department Management")
    st.markdown("Manage departments across your organization")
    
    st.markdown("---")
    
    # Add new department section
    st.markdown("### ➕ Add New Department")
    col_dept1, col_dept2 = st.columns([3, 1])
    
    with col_dept1:
        new_dept = st.text_input("Department Name", placeholder="e.g., Engineering, HR, Finance", key="new_dept_input")
    
    with col_dept2:
        st.write("")
        st.write("")
        if st.button("➕ Add Department", use_container_width=True, type="primary"):
            if new_dept and new_dept.strip():
                existing_depts_lower = [d.lower() for d in departments]
                if new_dept.strip().lower() in existing_depts_lower:
                    st.warning("⚠️ Department already exists")
                else:
                    new_dept_data = {
                        'Device_ID': f'DEPT_ADD_{new_dept.upper()[:10]}_{datetime.now().strftime("%f")}',
                        'Department': new_dept.strip(),
                        'Status': 'Active'
                    }
                    new_row = pd.DataFrame([new_dept_data], columns=COLUMNS)
                    updated_df = pd.concat([raw_df, new_row], ignore_index=True)
                    if save_data(updated_df):
                        st.success(f"✅ Department '{new_dept}' added successfully!")
                        st.balloons()
                        st.rerun()
            else:
                st.error("❌ Please enter a department name")
    
    st.markdown("---")
    st.markdown("### 📋 Existing Departments")
    
    df_display = get_working_df(raw_df)
    
    if not departments:
        st.info("📭 No departments created yet. Add your first department above!")
    else:
        dept_stats = df_display.groupby('Department').agg({
            'Device_ID': 'count',
            'Status': lambda x: (x == 'Active').sum()
        }).reset_index()
        dept_stats.columns = ['Department', 'Total Devices', 'Active Devices']
        dept_stats = dept_stats[dept_stats['Department'] != 'Not Specified']
        dept_stats = dept_stats.sort_values('Total Devices', ascending=False)
        
        if len(dept_stats) > 0:
            total_devices = dept_stats['Total Devices'].sum()
            if total_devices > 0:
                dept_stats['Percentage'] = (dept_stats['Total Devices'] / total_devices * 100).round(1)
                dept_stats['Percentage'] = dept_stats['Percentage'].astype(str) + '%'
        
        st.dataframe(
            dept_stats, 
            use_container_width=True, 
            hide_index=True,
            column_config={
                "Department": st.column_config.TextColumn("Department", width="medium"),
                "Total Devices": st.column_config.NumberColumn("Total Devices", width="small"),
                "Active Devices": st.column_config.NumberColumn("Active Devices", width="small"),
                "Percentage": st.column_config.TextColumn("% of Total", width="small"),
            }
        )
        
        st.caption(f"Total: {len(dept_stats)} departments | {dept_stats['Total Devices'].sum()} devices")
    
    st.markdown("---")
    
    # Back button at the bottom as well
    col_back_bottom, col_spacer_bottom = st.columns([1, 5])
    with col_back_bottom:
        if st.button("⬅️ Back to Dashboard", use_container_width=True, key="back_bottom"):
            st.session_state['show_dept_mgmt'] = False
            st.rerun()

# --- Main Application ---
def main():
    st.set_page_config(
        page_title="Device Management System",
        page_icon="💻",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    apply_custom_css()
    
    # Initialize authentication session state
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False
    
    # Check if user is logged in
    if not st.session_state['authenticated']:
        display_login_page()
        return  # Stop execution if not logged in
    
    # Initialize other session states
    if 'show_form' not in st.session_state:
        st.session_state['show_form'] = False
    if 'edit_device_id' not in st.session_state:
        st.session_state['edit_device_id'] = None
    if 'show_dept_mgmt' not in st.session_state:
        st.session_state['show_dept_mgmt'] = False
    
    # Load data
    raw_df = load_data()
    df = get_working_df(raw_df)
    departments = raw_df['Department'].dropna().unique().tolist()
    
    # Header
    col_title, col_user = st.columns([4, 1])
    with col_title:
        st.title("💻 Smart Device Management System")
        st.markdown("**Enterprise-Grade Device Tracking & Management**")
    with col_user:
        st.write("")  # Spacing
        st.markdown(f"**👤 {st.session_state.get('user_name', 'User')}**")
        st.caption(f"Role: {st.session_state.get('role', 'User')}")
    
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 🎛️ Control Panel")
        
        # User info section
        st.markdown("---")
        st.markdown("### 👤 User Information")
        st.info(f"""
        **Name:** {st.session_state.get('user_name', 'Unknown')}  
        **Role:** {st.session_state.get('role', 'User')}  
        **Username:** {st.session_state.get('username', 'guest')}
        """)
        
        if st.button("🚪 Logout", use_container_width=True, type="primary"):
            logout()
        
        st.markdown("---")
        
        if st.button("➕ Add New Device", use_container_width=True):
            st.session_state['show_form'] = True
            st.session_state['edit_device_id'] = None
            st.session_state['show_dept_mgmt'] = False
            st.rerun()
        
        if st.button("🏢 Manage Departments", use_container_width=True):
            st.session_state['show_dept_mgmt'] = True
            st.session_state['show_form'] = False
            st.session_state['edit_device_id'] = None
            st.rerun()
        
        st.markdown("---")
        
        # Quick Stats
        st.markdown("### 📊 Quick Stats")
        st.metric("Total Devices", len(df))
        st.metric("Active", len(df[df['Status'] == 'Active']))
        st.metric("Departments", len([d for d in departments if d != 'Not Specified']))
        
        st.markdown("---")
        
        # Quick Links
        st.markdown("### 🔗 Quick Links")
        st.markdown("""
        - 📖 [User Guide](#)
        - 🆘 [Support](#)
        - 📋 [Documentation](#)
        """)
        
        st.markdown("---")
        st.caption("v2.0 | Secure Edition")
    
    # Main content area
    if st.session_state['show_form']:
        if st.session_state['edit_device_id']:
            display_device_form(df, departments, mode='edit', 
                              device_id=st.session_state['edit_device_id'])
        else:
            display_device_form(df, departments, mode='add')
    
    elif st.session_state['show_dept_mgmt']:
        display_department_management(raw_df)
    
    else:
        # Tabs for main views
        tab1, tab2 = st.tabs(["📊 Dashboard", "📋 Device Inventory"])
        
        with tab1:
            display_enhanced_dashboard(df)
        
        with tab2:
            display_data_table(df, departments)

if __name__ == '__main__':
    main()