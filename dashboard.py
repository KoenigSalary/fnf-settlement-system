import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime, date, timedelta
import calendar
from dateutil.relativedelta import relativedelta
import re
import hashlib
import random
import plotly.express as px
import plotly.graph_objects as go

# Environment variables
rms_user = os.getenv('RMS_USER')
rms_pass = os.getenv('RMS_PASS')

# Try to import Google Sheets dependencies
try:
    import gspread
    from google.oauth2.service_account import Credentials
    GOOGLE_SHEETS_AVAILABLE = True
except ImportError:
    GOOGLE_SHEETS_AVAILABLE = False
    st.warning("Google Sheets integration not available. Using demo data.")

# Enhanced CSS Styling
def load_custom_css():
    st.markdown("""
    <style>
    /* Main App Styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #667eea;
        margin: 1rem 0;
        transition: transform 0.2s;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
    }
    
    .status-badge {
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.9rem;
        display: inline-block;
        margin: 0.2rem;
    }
    
    .status-draft { background-color: #ffeaa7; color: #2d3436; }
    .status-review { background-color: #fab1a0; color: #2d3436; }
    .status-approved { background-color: #00b894; color: white; }
    .status-rejected { background-color: #e17055; color: white; }
    .status-processed { background-color: #0984e3; color: white; }
    
    .info-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .success-card {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .warning-card {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        color: #2d3436;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .calculation-box {
        background: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    
    .employee-card {
        background: white;
        border: 1px solid #e9ecef;
        border-radius: 15px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        border-left: 5px solid #667eea;
    }
    
    .sidebar-metric {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        text-align: center;
    }
    
    .login-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
    }
    
    .feature-highlight {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        backdrop-filter: blur(10px);
    }
    
    .data-table {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Sidebar Styling */
    .sidebar-content {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    /* Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 1.5rem;
        font-weight: bold;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    
    /* Form Styling */
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #e9ecef;
        transition: border-color 0.3s;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    .stSelectbox > div > div > select {
        border-radius: 10px;
        border: 2px solid #e9ecef;
    }
    
    .stNumberInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #e9ecef;
    }
    
    /* Progress Bar Styling */
    .progress-bar {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        height: 10px;
        border-radius: 5px;
        margin: 1rem 0;
    }
    
    /* Animation */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .fade-in {
        animation: fadeIn 0.5s ease-in;
    }
    
    /* Enhanced Metrics */
    .enhanced-metric {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        border-left: 5px solid #667eea;
        margin: 1rem 0;
        transition: transform 0.2s;
    }
    
    .enhanced-metric:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #667eea;
        margin: 0.5rem 0;
    }
    
    .metric-label {
        font-size: 1rem;
        color: #6c757d;
        font-weight: 500;
    }
    </style>
    """, unsafe_allow_html=True)

# Load CSS on app start
load_custom_css()

# ====== Real Users Configuration ======
USERS_FILE = "users.json"

# 👇 Replace these with your actual users and roles
REAL_USERS = {
    "Payroll.fnf": "Payroll Team",
    "tax.fnf": "Tax Team", 
    "alice.johnson": "Payroll Team",
    "bob.wilson": "Tax Team",
    "sarah.davis": "Payroll Team",
    "mike.brown": "Tax Team",
    "emma.jones": "Payroll Team",
    "david.miller": "Tax Team",
    # Add more real users here
}

def _hash_pw(pw: str) -> str:
    """Hash password using SHA256"""
    try:
        return hashlib.sha256(pw.encode("utf-8")).hexdigest()
    except Exception:
        return pw  # fallback

def _default_users_real():
    """
    Seed users.json with real users from REAL_USERS:
    - No initial password (password_hash=None)
    - must_change_password=True (they must set it on first login)
    """
    base = {}
    for uname, role in REAL_USERS.items():
        base[uname] = {
            "role": role,
            "password_hash": None,           # set after first login
            "must_change_password": True,    # forced on first login
            "password_updated_at": None,
            "created_at": datetime.now().isoformat(),
        }
    return base

def load_users():
    """Load users from JSON file"""
    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, "r") as f:
                data = json.load(f)
            # ensure schema for all REAL_USERS
            changed = False
            if not isinstance(data, dict):
                data = {}
                changed = True
            for uname, role in REAL_USERS.items():
                if uname not in data:
                    data[uname] = {
                        "role": role,
                        "password_hash": None,
                        "must_change_password": True,
                        "password_updated_at": None,
                        "created_at": datetime.now().isoformat(),
                    }
                    changed = True
                else:
                    u = data[uname]
                    # backfill any missing keys
                    if "role" not in u: u["role"] = role; changed = True
                    if "password_hash" not in u: u["password_hash"] = None; changed = True
                    if "must_change_password" not in u: u["must_change_password"] = True; changed = True
                    if "password_updated_at" not in u: u["password_updated_at"] = None; changed = True
                    if "created_at" not in u: u["created_at"] = datetime.now().isoformat(); changed = True
            
            # Remove any users not in REAL_USERS (optional; comment out if you want to keep)
            for uname in list(data.keys()):
                if uname not in REAL_USERS:
                    del data[uname]
                    changed = True
            
            if changed:
                save_users(data)
            return data
        else:
            data = _default_users_real()
            save_users(data)
            return data
    except Exception:
        data = _default_users_real()
        save_users(data)
        return data

def save_users(users):
    """Save users to JSON file"""
    try:
        with open(USERS_FILE, "w") as f:
            json.dump(users, f, indent=2)
    except Exception as e:
        st.warning(f"Could not save users: {e}")

def verify_user(username: str, password: str) -> bool:
    """Verify user credentials"""
    users = load_users()
    u = users.get(username)
    if not u:
        return False
    if not u.get("password_hash"):
        # No password set yet → first login required
        return False
    return u["password_hash"] == _hash_pw(password)

def set_password(username: str, new_password: str):
    """Set new password for user"""
    users = load_users()
    if username in users:
        users[username]["password_hash"] = _hash_pw(new_password)
        users[username]["must_change_password"] = False  # Clear the flag
        users[username]["password_updated_at"] = datetime.now().isoformat()
        save_users(users)
        return True
    return False

def change_password_ui(location="sidebar", require_current: bool = True):
    """Debug version to see what's happening"""
    
    # 🔍 DEBUG INFO - Remove this after testing
    if location == "main":
        st.write("🔍 DEBUG INFO:")
        st.write(f"require_current: {require_current}")
        st.write(f"first_login: {st.session_state.get('first_login', False)}")
        st.write(f"must_change_password: {st.session_state.get('must_change_password', False)}")
        st.write("---")

    container = st.sidebar if location == "sidebar" else st
    form_key = f"change_password_form_{location}"

    with container:
        with st.form(form_key, clear_on_submit=False):
            if require_current:
                st.markdown("### 🔐 **Change Password**")
                
                # Show current password field ONLY when require_current=True
                current = st.text_input(
                    "Current Password",
                    type="password",
                    key=f"cp_current_{location}",
                    help="Enter your existing password"
                )
            else:
                st.markdown("### 🔐 **Set Up Your Password**")
                st.markdown("Create a secure password for your account.")
                current = None  # No current password needed

            # New password field
            new = st.text_input(
                "New Password" if require_current else "Create Password",
                type="password",
                help="Use 8+ chars with upper, lower, digit & special character.",
                key=f"cp_new_{location}"
            )
            
            # Confirm password field
            confirm = st.text_input(
                "Confirm New Password" if require_current else "Confirm Password",
                type="password",
                key=f"cp_confirm_{location}"
            )

            # Submit button
            submit_text = "🔄 Update Password" if require_current else "✅ Set Password"
            submit_pw = st.form_submit_button(submit_text, use_container_width=True)

        # Handle form submission
        if submit_pw:
            uname = st.session_state.get("username")
            if not uname:
                st.error("No logged-in user found.")
                return

            # Step 1: Validate current password ONLY if require_current=True
            if require_current:
                if not current or current.strip() == "":
                    st.error("Please enter your current password.")
                    return
                    
                if not verify_user(uname, current):
                    st.error("Current password is incorrect.")
                    return
            # If require_current=False, skip current password validation entirely

            # Step 2: Validate new password
            if not new or new.strip() == "":
                st.error("Please enter a new password.")
                return

            # Step 3: Password strength validation
            password_errors = []
            
            if len(new) < 8:
                password_errors.append("at least 8 characters")
            if not any(c.islower() for c in new):
                password_errors.append("one lowercase letter")
            if not any(c.isupper() for c in new):
                password_errors.append("one uppercase letter") 
            if not any(c.isdigit() for c in new):
                password_errors.append("one digit")
            if not any(not c.isalnum() for c in new):
                password_errors.append("one special character")
                
            if password_errors:
                st.error(f"Password must contain: {', '.join(password_errors)}")
                return

            # Step 4: Confirm password match
            if new != confirm:
                st.error("New password and confirmation do not match.")
                return

            # Step 5: Set the password
            if set_password(uname, new):
                success_msg = "✅ Password set successfully!" if not require_current else "✅ Password updated successfully!"
                st.success(success_msg)
                
                # Clear password-related session flags
                st.session_state.pop("must_change_password", None)
                st.session_state.pop("first_login", None)
                
                # For first-time setup, ensure user is properly logged in
                if not require_current:
                    users = load_users()
                    user_data = users.get(uname, {})
                    st.session_state["role"] = user_data.get("role", "Unknown")
                    st.session_state["username"] = uname
                    st.success(f"🎉 Welcome to the F&F Settlement System!")
                    st.balloons()
                
                # Force page reload to show main dashboard
                st.rerun()
            else:
                st.error("Failed to set password. Please try again.")

def create_enhanced_metric_card(title, value, delta=None, delta_color="normal", icon="📊"):
    """Create an enhanced metric card with custom styling"""
    delta_html = ""
    if delta is not None:
        color = "#00b894" if delta_color == "normal" else "#e17055" if delta_color == "inverse" else "#636e72"
        delta_html = f'<div style="color: {color}; font-size: 0.9rem; margin-top: 0.5rem;">{delta}</div>'
    
    st.markdown(f"""
    <div class="enhanced-metric">
        <div style="font-size: 1.5rem;">{icon}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-label">{title}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)

def create_status_badge(status):
    """Create a status badge with appropriate styling"""
    status_classes = {
        'Draft': 'status-draft',
        'Under Tax Review': 'status-review',
        'Pending Tax Review': 'status-review',
        'Tax Approved': 'status-approved',
        'Tax Rejected': 'status-rejected',
        'Payment Processed': 'status-processed'
    }
    
    class_name = status_classes.get(status, 'status-draft')
    return f'<span class="status-badge {class_name}">{status}</span>'

def add_sidebar_logo():
    """Add enhanced logo to sidebar with better styling"""
    with st.sidebar:
        # Enhanced logo section with styling
        st.markdown("""
        <div style='text-align: center; padding: 1rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; color: white; margin-bottom: 1rem;'>
            <h2 style='margin: 0; font-size: 1.5rem;'>🏢 Koenig Solutions</h2>
            <p style='margin: 0.5rem 0 0 0; font-size: 0.9rem; opacity: 0.9;'>F&F Settlement System</p>
        </div>
        """, unsafe_allow_html=True)
        
        # User info with enhanced styling
        if 'username' in st.session_state:
            st.markdown(f"""
            <div class="sidebar-content">
                <div style="text-align: center;">
                    <h3 style="margin: 0 0 1rem 0;">👤 {st.session_state.username}</h3>
                    <p style="margin: 0; opacity: 0.9;">🔧 {st.session_state.role}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Enhanced F&F statistics
            if 'fnf_submissions' in st.session_state:
                total_submissions = len(st.session_state.fnf_submissions)
                pending_review = len([s for s in st.session_state.fnf_submissions 
                                      if s['status'] in ['Under Tax Review', 'Pending Tax Review']])
                approved = len([s for s in st.session_state.fnf_submissions if s['status'] == 'Tax Approved'])
                processed = len([s for s in st.session_state.fnf_submissions if s['status'] == 'Payment Processed'])
                
                st.markdown("### 📊 F&F Statistics")
                
                # Create enhanced metrics in sidebar
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"""
                    <div class="sidebar-metric">
                        <div style="font-size: 1.5rem; font-weight: bold;">{total_submissions}</div>
                        <div style="font-size: 0.9rem; opacity: 0.9;">Total</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f"""
                    <div class="sidebar-metric">
                        <div style="font-size: 1.5rem; font-weight: bold;">{approved}</div>
                        <div style="font-size: 0.9rem; opacity: 0.9;">Approved</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="sidebar-metric">
                        <div style="font-size: 1.5rem; font-weight: bold;">{pending_review}</div>
                        <div style="font-size: 0.9rem; opacity: 0.9;">Pending</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f"""
                    <div class="sidebar-metric">
                        <div style="font-size: 1.5rem; font-weight: bold;">{processed}</div>
                        <div style="font-size: 0.9rem; opacity: 0.9;">Processed</div>
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown("---")

            # System features with icons
            st.markdown("""
            <div class="sidebar-content">
                <h4 style="margin: 0 0 1rem 0;">🚀 System Features</h4>
                <div style="font-size: 0.9rem; line-height: 1.6;">
                    ✅ Multi-month processing<br>
                    ✅ Tax regime support<br>
                    ✅ Investment deductions<br>
                    ✅ EPF & ESI calculations<br>
                    ✅ Real-time previews<br>
                    ✅ Professional reports
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("---")

            # Change password (available anytime)
            change_password_ui(location="sidebar")

            st.markdown("---")
            
            if st.button("🚪 Logout", use_container_width=True):
                # Clear session state
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()

@st.cache_data(ttl=300)
def load_employee_data():
    """Load employee data from Google Sheets only (strict; no demo fallback)."""
    SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets.readonly",
        "https://www.googleapis.com/auth/drive.readonly",
    ]
    try:
        # Use secrets-only (recommended)
        if "gcp_service_account" not in st.secrets:
            st.error("Missing st.secrets['gcp_service_account']. Add your service-account JSON + spreadsheet_id (+ optional worksheet_name or worksheet_gid).")
            st.stop()

        s = st.secrets["gcp_service_account"]
        creds = Credentials.from_service_account_info(s, scopes=SCOPES)
        gc = gspread.authorize(creds)

        spreadsheet_id = s.get("spreadsheet_id")
        worksheet_name = s.get("worksheet_name", "Employee Master")
        worksheet_gid = s.get("worksheet_gid")

        if not spreadsheet_id:
            st.error("st.secrets['gcp_service_account']['spreadsheet_id'] is required.")
            st.stop()

        ss = gc.open_by_key(spreadsheet_id)
        ws = ss.get_worksheet_by_id(int(worksheet_gid)) if worksheet_gid else ss.worksheet(worksheet_name)

        data = ws.get_all_records()
        if not data:
            st.error("Google Sheet is empty or unreadable.")
            st.stop()

        df = pd.DataFrame(data)

        # ---- Normalization (same as before) ----
        if 'Employee ID' in df.columns:
            df = df[(df['Employee ID'] != 0) & (df['Employee ID'] != '')]
            try:
                df['Employee ID'] = pd.to_numeric(df['Employee ID'], errors='coerce').astype('Int64')
            except Exception:
                pass

        if 'Salary' in df.columns:
            df['Salary'] = pd.to_numeric(df['Salary'], errors='coerce')
            df = df.dropna(subset=['Salary'])

        for col in ['Employee Name', 'Designation', 'BaseLocation', 'PAN No.']:
            if col in df.columns:
                df[col] = df[col].fillna('').astype(str)

        maybe_numeric_cols = [
            'EPF Rate','PF Rate','EPF Wages','PF Wages','EPF Full Month',
            'EPF Fixed','EPF Fixed Deduction','PF Wage Cap','EPF','PF',
            'PF Deduction','EPF Deduction','Employee EPF','EPF Employee',
            'PF Employee','Total EPF','EPF Amount','EPF Per Month','Employee PF Contribution',
            'PF Amount','PF Per Month'
        ]
        for cname in maybe_numeric_cols:
            if cname in df.columns:
                df[cname] = pd.to_numeric(df[cname].astype(str).str.replace(',', ''), errors='coerce')

        for cname in ['EPF Applicable','PF Applicable','EPF Capped','PF Capped']:
            if cname in df.columns:
                df[cname] = df[cname].astype(str)

        return df

    except Exception as e:
        st.error(f"Google Sheets error: {e}")
        st.stop()

def get_employee_by_id(employee_id, df):
    """Get employee details by ID"""
    try:
        # cast both to numeric safely
        df_ids = pd.to_numeric(df['Employee ID'], errors='coerce')
        employee_id = int(employee_id)
        employee = df[df_ids == employee_id]
        if not employee.empty:
            return employee.iloc[0]
    except Exception:
        pass
    return None

def parse_bool(val, default=None):
    """Parse Yes/No/True/False/1/0 -> bool, else default"""
    if pd.isna(val):
        return default
    s = str(val).strip().lower()
    if s in {'yes','y','true','t','1'}:
        return True
    if s in {'no','n','false','f','0'}:
        return False
    return default

def detect_epf_fixed_columns(df_columns):
    """
    Detect likely columns in Employee Master that hold the FULL-MONTH EPF
    (employee contribution). We exclude 'employer' words.
    """
    candidates_exact = [
        'EPF Full Month','EPF Fixed','EPF Fixed Deduction',
        'EPF','PF','PF Deduction','EPF Deduction','Employee EPF',
        'EPF Employee','PF Employee','Total EPF','EPF Amount','EPF Per Month',
        'Employee PF Contribution','PF Amount','PF Per Month'
    ]
    found = [c for c in candidates_exact if c in df_columns]

    # Fuzzy: any column containing EPF/PF + (amount|deduction|contribution|per month|monthly)
    pattern = re.compile(r'(?:^|\s)(?!employer)(epf|pf).*(amount|deduction|contribution|per\s*month|monthly)', re.I)
    for c in df_columns:
        if c not in found and pattern.search(c or ''):
            found.append(c)
    # De-dup preserving order
    seen = set()
    uniq = []
    for c in found:
        if c not in seen:
            uniq.append(c)
            seen.add(c)
    return uniq

def extract_epf_profile(emp_row, preferred_epf_col=None, all_cols=None):
    """
    Extract EPF policy for this employee from Employee Master if present.
    PRIORITY:
      1) If preferred_epf_col chosen and has value -> fixed_full_month_epf = that value
      2) Else scan detected EPF fixed columns -> first non-null numeric used
      3) Else compute from wages/rate/cap flags (no default cap unless flagged)
    """
    profile = {
        'applicable': True,                 # default: EPF applies
        'capped': None,                     # default: no cap UNLESS column says so
        'rate': 0.12,                       # default 12%
        'cap_wage': 15000,                  # default wage cap if capped==True
        'wages': None,                      # if provided (EPF Wages)
        'fixed_full_month_epf': None        # if provided, use this exact value
    }

    # applicable
    for c in ['EPF Applicable','PF Applicable']:
        if c in emp_row.index:
            profile['applicable'] = parse_bool(emp_row[c], default=profile['applicable'])

    # capped (only when explicitly set)
    for c in ['EPF Capped','PF Capped']:
        if c in emp_row.index:
            profile['capped'] = parse_bool(emp_row[c], default=profile['capped'])

    # rate
    for c in ['EPF Rate','PF Rate']:
        if c in emp_row.index and pd.notna(emp_row[c]):
            try:
                r = float(str(emp_row[c]).replace(',', ''))
                profile['rate'] = r/100.0 if r > 1.0 else r
            except:
                pass

    # cap wage (if provided)
    if 'PF Wage Cap' in emp_row.index and pd.notna(emp_row['PF Wage Cap']):
        try:
            cap = float(str(emp_row['PF Wage Cap']).replace(',', ''))
            if cap > 0:
                profile['cap_wage'] = cap
        except:
            pass

    # wages base
    for c in ['EPF Wages','PF Wages']:
        if c in emp_row.index and pd.notna(emp_row[c]):
            try:
                w = float(str(emp_row[c]).replace(',', ''))
                if w >= 0:
                    profile['wages'] = w
            except:
                pass

    # 1) Preferred fixed EPF column
    if preferred_epf_col and preferred_epf_col in emp_row.index and pd.notna(emp_row[preferred_epf_col]):
        try:
            profile['fixed_full_month_epf'] = float(str(emp_row[preferred_epf_col]).replace(',', ''))
            return profile
        except:
            pass

    # 2) Scan detected fixed EPF columns
    fixed_candidates = detect_epf_fixed_columns(all_cols or [])
    for c in fixed_candidates:
        if c in emp_row.index and pd.notna(emp_row[c]):
            try:
                val = float(str(emp_row[c]).replace(',', ''))
                if val >= 0:
                    profile['fixed_full_month_epf'] = val
                    return profile
            except:
                continue

    # 3) No fixed value found; compute later via wages/rate/cap
    return profile

def get_total_working_days(month_name, year=None, holidays=None):
    """
    Calculate working days considering:
    - 5-day work week (Monday-Friday only)
    - Exclude holidays if provided
    """
    month_map = {'January':1,'February':2,'March':3,'April':4,'May':5,'June':6,
                 'July':7,'August':8,'September':9,'October':10,'November':11,'December':12}
    m = month_map.get(month_name)
    if year is None:
        reference = st.session_state.get('last_working_day', date.today())
        year = reference.year if hasattr(reference, 'year') else date.today().year

    total_days = calendar.monthrange(year, m)[1]
    
    # Count only Monday-Friday (weekday 0-4), exclude Saturday(5) and Sunday(6)
    working_days = sum(1 for d in range(1, total_days+1) 
                      if calendar.weekday(year, m, d) < 5)  # 0-4 are Mon-Fri
    
    # Deduct holidays if provided
    if holidays:
        holiday_count = 0
        for holiday_date in holidays:
            try:
                if isinstance(holiday_date, str):
                    holiday_dt = datetime.strptime(holiday_date, '%Y-%m-%d').date()
                else:
                    holiday_dt = holiday_date
                
                # Check if holiday falls in this month and is a working day
                if (holiday_dt.year == year and holiday_dt.month == m and 
                    calendar.weekday(year, m, holiday_dt.day) < 5):
                    holiday_count += 1
            except Exception:
                continue
        
        working_days -= holiday_count
    
    return max(working_days, 0)  # Ensure non-negative
    
def holiday_input_section(month):
    """Add holiday input section for each month"""
    st.markdown("#### 📅 Holidays (Optional)")
    holidays_text = st.text_area(
        f"Holidays in {month} (one date per line, format: YYYY-MM-DD)",
        placeholder="2024-01-26\n2024-01-15",
        key=f"holidays_{month}",
        help="Enter holiday dates that should be excluded from working days"
    )
    
    holidays = []
    if holidays_text.strip():
        for line in holidays_text.strip().split('\n'):
            line = line.strip()
            if line:
                try:
                    holiday_date = datetime.strptime(line, '%Y-%m-%d').date()
                    holidays.append(holiday_date)
                except ValueError:
                    st.warning(f"Invalid date format: {line}. Use YYYY-MM-DD format.")
    
    return holidays

def _fy_start_year_from_session() -> int:
    """Return 2025 for FY 2025-26, etc., based on last_working_day (or today)."""
    try:
        d = st.session_state.get("last_working_day", date.today())
        if isinstance(d, datetime):
            d = d.date()
    except Exception:
        d = date.today()
    return d.year if d.month >= 4 else d.year - 1

def tds_old_from_total_income(total_income: float) -> float:
    """Old Regime: expects TOTAL INCOME already after std. deduction & investments."""
    ti = max(0.0, float(total_income))
    if ti <= 500_000.0:  # 87A rebate
        return 0.0
    tax = 0.0
    if ti > 1_000_000.0:
        tax += (ti - 1_000_000.0) * 0.30
        ti = 1_000_000.0
    if ti > 500_000.0:
        tax += (ti - 500_000.0) * 0.20
        ti = 500_000.0
    if ti > 250_000.0:
        tax += (ti - 250_000.0) * 0.05
    return round(tax * 1.04, 2)  # 4% cess

def tds_new_from_total_income(total_income: float) -> float:
    """New Regime (FY-aware): expects TOTAL INCOME already after std. deduction."""
    fy_start = _fy_start_year_from_session()
    ti = max(0.0, float(total_income))
    if fy_start >= 2025:  # FY 2025-26+
        edges = (0.0, 400_000.0, 800_000.0, 1_200_000.0, 1_600_000.0, 2_000_000.0, 2_400_000.0, float("inf"))
        rates = (0.00, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30)
        rebate_threshold = 1_200_000.0
    else:                 # FY 2024-25
        edges = (0.0, 300_000.0, 600_000.0, 900_000.0, 1_200_000.0, 1_500_000.0, float("inf"))
        rates = (0.00, 0.05, 0.10, 0.15, 0.20, 0.30)
        rebate_threshold = 700_000.0

    if ti <= rebate_threshold:  # 87A rebate
        return 0.0

    tax = 0.0
    for i in range(1, len(edges)):
        low, high = edges[i-1], edges[i]
        rate = rates[i-1]
        if ti > low:
            tax += (min(ti, high) - low) * rate
        else:
            break
    return round(tax * 1.04, 2)

def calculate_years_of_service(doj_str, last_working_day):
    """Calculate years of service from DOJ to last working day"""
    try:
        # Parse DOJ (assuming format like "01/01/93" or "01/01/1993")
        if len(doj_str.split('/')[2]) == 2:  # Two digit year
            doj = datetime.strptime(doj_str, '%d/%m/%y')
        else:  # Four digit year
            doj = datetime.strptime(doj_str, '%d/%m/%Y')
        
        # Parse last working day
        if isinstance(last_working_day, str):
            lwd = datetime.strptime(last_working_day, '%Y-%m-%d')
        else:
            lwd = last_working_day
        
        # Calculate difference
        diff = relativedelta(lwd, doj)
        
        # Convert to years (including months and days as decimal)
        years = diff.years + (diff.months / 12) + (diff.days / 365)
        
        return years
    except Exception as e:
        st.error(f"Error calculating service years: {e}")
        return 0

def years_for_gratuity(doj, lwd):
    diff = relativedelta(lwd, doj)
    # > 6 months counts as a full year
    years = diff.years + (1 if (diff.months > 6 or (diff.months == 6 and diff.days > 0)) else 0)
    return max(0, years)

def calculate_gratuity(tenure_years, last_basic_da):
    if tenure_years < 5:
        return 0.0
    raw = (tenure_years * last_basic_da * 15) / 26
    return round(min(raw, 20_00_000), 2)   # ₹20 lakh cap for private sector

def calculate_epf_with_limit(basic_salary, is_reduced=False):
    """
    Calculate EPF with company-specific rules:
    - Max EPF deduction limit is ₹1,800 (₹15,000 * 12%)
    - If salary reduced due to leave/absent, basic reduced proportionally
    - If basic < ₹15,000: EPF = actual_basic * 12%
    - If basic >= ₹15,000: EPF = ₹1,800 (max limit)
    """
    max_epf_basic = 15000
    epf_rate = 0.12
    max_epf_deduction = max_epf_basic * epf_rate  # ₹1,800
    
    if basic_salary <= max_epf_basic:
        # If basic is less than ₹15,000, calculate 12% of actual basic
        epf = basic_salary * epf_rate
    else:
        # If basic is ₹15,000 or more, EPF is capped at ₹1,800
        epf = max_epf_deduction
    
    return round(epf, 2)

# NEW: EPF computed from Employee Master profile (fixed or formula) then prorated
def calculate_epf_prorated(full_month_basic, present_days, total_working_days, epf_profile=None):
    """
    Compute full-month EPF from Employee Master policy, then prorate by attendance.
    - If 'fixed_full_month_epf' given: use it directly (can be 0, 1800, 10248, etc.)
    - Else if 'applicable' is False: full EPF = 0.
    - Else:
        - If 'capped' True: EPF = rate * min(wage_base, cap_wage)
        - If 'capped' False or None: EPF = rate * wage_base
      where wage_base = epf_profile['wages'] if provided else full_month_basic
    Finally, prorate: EPF * (present_days / total_working_days)
    """
    ratio = (present_days / total_working_days) if total_working_days else 0.0

    if not epf_profile:
        epf_profile = {'applicable': True, 'capped': None, 'rate': 0.12, 'cap_wage': 15000, 'wages': None, 'fixed_full_month_epf': None}

    # Not applicable
    if epf_profile.get('applicable') is False:
        return 0.0, 0.0, ratio, "EPF not applicable"

    # Fixed full-month EPF provided (our priority path)
    if epf_profile.get('fixed_full_month_epf') is not None:
        full_epf = float(epf_profile['fixed_full_month_epf'])
        return round(full_epf * ratio, 2), round(full_epf, 2), ratio, "Fixed full-month EPF from Employee Master"

    rate = float(epf_profile.get('rate', 0.12))
    cap_wage = float(epf_profile.get('cap_wage', 15000))
    wages_base = epf_profile.get('wages')
    if wages_base is None or wages_base <= 0:
        wages_base = full_month_basic

    if epf_profile.get('capped') is True:
        full_epf = rate * min(wages_base, cap_wage)
        reason = f"rate {rate*100:.1f}% × min(wage {wages_base:.0f}, cap {cap_wage:.0f})"
    else:
        full_epf = rate * wages_base
        reason = f"rate {rate*100:.1f}% × wage {wages_base:.0f} (no cap)"

    return round(full_epf * ratio, 2), round(full_epf, 2), ratio, reason

def salary_breakdown_input_with_epf(month, base_salary=0.0, present_days=0, total_working_days=1, epf_profile=None):
    """Enhanced salary breakdown with EPF calculation"""
    st.markdown(f"""
    <div class="calculation-box">
        <h3>💰 Salary Breakdown for {month}</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Calculate salary breakdown using correct formula
    basic_salary = base_salary / 3  # Basic = Total ÷ 3
    hra = basic_salary * 0.50       # HRA = 50% of Basic
    special_allowances = base_salary - basic_salary - hra  # Rest amount
    
    # Handle case where salary is reduced due to absences
    is_salary_reduced = present_days < total_working_days
    if is_salary_reduced:
        reduction_ratio = present_days / total_working_days if total_working_days > 0 else 1
        prorated_basic = basic_salary * reduction_ratio
    else:
        prorated_basic = basic_salary
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        basic = st.number_input(
            f"Basic Salary (₹)", 
            min_value=0.0, 
            value=basic_salary,
            key=f"basic_{month}",
            step=100.0,
            help="Basic = Total Salary ÷ 3"
        )
        
        if is_salary_reduced:
            st.markdown(f"""
            <div class="warning-card">
                ⚠️ Prorated Basic: ₹{prorated_basic:,.2f}<br>
                <small>Ratio: {present_days}/{total_working_days}</small>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        hra = st.number_input(
            f"HRA (₹)", 
            min_value=0.0, 
            value=basic * 0.50,
            key=f"hra_{month}",
            step=50.0,
            help="HRA = 50% of Basic Salary"
        )
    
    with col3:
        # Calculate rest amount
        rest_amount = base_salary - basic - hra
        special_allowances = st.number_input(
            f"Special Allowances (₹)", 
            min_value=0.0, 
            value=rest_amount,
            key=f"special_{month}",
            step=50.0,
            help="Special = Total - Basic - HRA"
        )
    
    # EPF Calculation Section (from Employee Master + proration)
    st.markdown("### 🏦 EPF Calculation")
    epf_prorated, epf_full, ratio, reason = calculate_epf_prorated(basic, present_days, total_working_days, epf_profile)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="info-card">
            <h4>EPF Calculation Logic (Employee Master)</h4>
            <p>• Full-month EPF (before proration): <strong>₹{epf_full:,.2f}</strong></p>
            <p>• Basis: {reason}</p>
            <p>• Attendance ratio: {present_days}/{total_working_days} = {ratio:.2f}</p>
            <p>• Final EPF = Full EPF × Ratio = ₹{epf_full:,.2f} × {ratio:.2f} = <strong>₹{epf_prorated:,.2f}</strong></p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        epf = st.number_input(
            f"EPF Deduction (₹)", 
            min_value=0.0,
            value=epf_prorated,
            key=f"epf_{month}",
            step=10.0,
            help="Auto from Employee Master policy, prorated by attendance. You may override."
        )
        if abs(epf - epf_prorated) > 0.01:
            st.markdown(f"""
            <div class="warning-card">
                ⚠️ Manual override! Calculated: ₹{epf_prorated:,.2f}
            </div>
            """, unsafe_allow_html=True)
    
    total_breakdown = basic + hra + special_allowances
    
    # Enhanced breakdown verification table
    st.markdown("### 🔍 Breakdown Verification")
    verification_data = {
        'Component': ['Basic Salary', 'HRA', 'Special Allowances', 'TOTAL', 'EPF'],
        'Formula': [
            'Total ÷ 3',
            '50% of Basic', 
            'Rest Amount',
            'Sum of All',
            'Full-month EPF × (present/working)'
        ],
        'Amount': [
            f"₹{basic:,.2f}",
            f"₹{hra:,.2f}",
            f"₹{special_allowances:,.2f}",
            f"₹{total_breakdown:,.2f}",
            f"₹{epf:,.2f}"
        ],
        'Percentage': [
            f"{(basic/base_salary*100) if base_salary > 0 else 0:.1f}%",
            f"{(hra/base_salary*100) if base_salary > 0 else 0:.1f}%",
            f"{(special_allowances/base_salary*100) if base_salary > 0 else 0:.1f}%",
            "100.0%",
            ""
        ]
    }
    
    verification_df = pd.DataFrame(verification_data)
    st.dataframe(verification_df, hide_index=True, use_container_width=True)
    
    return {
        'basic': basic,
        'hra': hra,
        'special_allowances': special_allowances,
        'total': total_breakdown,
        'epf': epf,
        'epf_full_month': epf_full,
        'attendance_ratio': ratio,
    }

def investment_deductions_input(epf_auto: float = 0.0):
    """Enhanced Investment and deduction options for Old Tax Regime"""
    st.markdown("""
    <div class="main-header">
        <h2>💼 Investment & Deductions (Old Tax Regime Only)</h2>
        <p>Maximize your tax savings with these investment options</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Section 80C Investments
    st.markdown("### 📊 Section 80C Investments (Max ₹1,50,000)")
    col1, col2 = st.columns(2)
    
    with col1:
        ppf = st.number_input("💰 PPF (₹)", min_value=0.0, max_value=150000.0, value=0.0, step=5000.0)

        # 🔹 EPF auto-filled from F&F month calculation (sum of EPF)
        epf_employee = st.number_input(
            "🏦 EPF Employee Contribution (₹)",
            min_value=0.0,
            value=float(epf_auto or 0.0),
            step=100.0,
            help="Auto-filled from your month-wise EPF in F&F. You can override if needed."
        )
        
        if epf_auto > 0:
            st.markdown(f"""
            <div class="success-card">
                Auto EPF from F&F months: ₹{epf_auto:,.2f}
            </div>
            """, unsafe_allow_html=True)

        elss = st.number_input("📈 ELSS Mutual Funds (₹)", min_value=0.0, value=0.0, step=5000.0)
        life_insurance = st.number_input("🛡️ Life Insurance Premium (₹)", min_value=0.0, value=0.0, step=2000.0)
    
    with col2:
        fd_5year = st.number_input("🏛️ 5-Year Fixed Deposit (₹)", min_value=0.0, value=0.0, step=5000.0)
        nsc = st.number_input("📜 NSC (₹)", min_value=0.0, value=0.0, step=5000.0)
        suknya_samriddhi = st.number_input("👧 Sukanya Samriddhi (₹)", min_value=0.0, value=0.0, step=5000.0)
        tuition_fees = st.number_input("🎓 Children Tuition Fees (₹)", min_value=0.0, value=0.0, step=5000.0)
    
    total_80c = ppf + epf_employee + elss + life_insurance + fd_5year + nsc + suknya_samriddhi + tuition_fees
    eligible_80c = min(total_80c, 150000)
    
    if total_80c > 150000:
        st.markdown(f"""
        <div class="warning-card">
            ⚠️ Total 80C (₹{total_80c:,.0f}) exceeds limit. Eligible: ₹{eligible_80c:,.0f}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="success-card">
            ✅ Section 80C: ₹{eligible_80c:,.0f}
        </div>
        """, unsafe_allow_html=True)
    
    # Other Deductions
    st.markdown("### 🏥 Health & Other Deductions")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Section 80D (Health Insurance)**")
        health_insurance_self = st.number_input("👨‍👩‍👧‍👦 Self & Family (₹)", min_value=0.0, max_value=25000.0, value=0.0, step=1000.0)
        health_insurance_parents = st.number_input("👴👵 Parents (₹)", min_value=0.0, max_value=50000.0, value=0.0, step=1000.0)
        
        st.markdown("**Disability & Medical**")
        section_80dd = st.number_input("♿ 80DD - Disability (₹)", min_value=0.0, max_value=125000.0, value=0.0, step=5000.0)
        section_80ddb = st.number_input("🏥 80DDB - Medical Treatment (₹)", min_value=0.0, max_value=100000.0, value=0.0, step=5000.0)
    
    with col2:
        st.markdown("**Loan Interest**")
        home_loan_interest = st.number_input("🏠 Home Loan Interest (₹)", min_value=0.0, max_value=200000.0, value=0.0, step=5000.0)
        education_loan_interest = st.number_input("📚 Education Loan Interest (₹)", min_value=0.0, value=0.0, step=2000.0)
        
        st.markdown("**NPS Deductions**")
        nps_80ccd_1b = st.number_input("🏦 NPS 80CCD(1B) (₹)", min_value=0.0, max_value=50000.0, value=0.0, step=5000.0)
        nps_80ccd_2 = st.number_input("🏢 NPS 80CCD(2) Employer (₹)", min_value=0.0, value=0.0, step=5000.0)
    
    # Allowances (Exempt under Old Regime)
    st.markdown("### 🚗 Exempt Allowances (Old Regime)")
    col1, col2 = st.columns(2)
    
    with col1:
        conveyance_allowance = st.number_input("🚗 Conveyance Allowance (₹)", min_value=0.0, max_value=21600.0, value=0.0, step=1000.0)
        helper_allowance = st.number_input("🏠 Helper Allowance (₹)", min_value=0.0, value=0.0, step=500.0)
        lta = st.number_input("✈️ LTA (₹)", min_value=0.0, value=0.0, step=5000.0)
    
    with col2:
        tel_broadband = st.number_input("📞 Telephone & Broadband (₹)", min_value=0.0, value=0.0, step=500.0)
        ld_allowance = st.number_input("📚 L&D Allowance (₹)", min_value=0.0, value=0.0, step=1000.0)
        hra_exemption = st.number_input("🏠 HRA Exemption (₹)", min_value=0.0, value=0.0, step=2000.0)
    
    # Calculate totals
    total_80d = health_insurance_self + health_insurance_parents
    total_other_deductions = section_80dd + section_80ddb + home_loan_interest + education_loan_interest + nps_80ccd_1b + nps_80ccd_2
    total_exempt_allowances = conveyance_allowance + helper_allowance + lta + tel_broadband + ld_allowance + hra_exemption
    
    total_deductions = eligible_80c + total_80d + total_other_deductions
    
    # Enhanced Summary with visual cards
    st.markdown("### 📋 Investment & Deduction Summary")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        create_enhanced_metric_card("Section 80C", f"₹{eligible_80c:,.0f}", icon="📊")
        create_enhanced_metric_card("Section 80D", f"₹{total_80d:,.0f}", icon="🏥")
    
    with col2:
        create_enhanced_metric_card("Other Deductions", f"₹{total_other_deductions:,.0f}", icon="📋")
        create_enhanced_metric_card("Exempt Allowances", f"₹{total_exempt_allowances:,.0f}", icon="🚗")
    
    with col3:
        create_enhanced_metric_card("Total Tax Deductions", f"₹{total_deductions:,.0f}", icon="💰")
        st.markdown("""
        <div class="info-card">
            <strong>Note:</strong> Exempt allowances reduce taxable income
        </div>
        """, unsafe_allow_html=True)
    
    return {
        '80c_total': eligible_80c,
        '80d_total': total_80d,
        'other_deductions': total_other_deductions,
        'exempt_allowances': total_exempt_allowances,
        'total_deductions': total_deductions,
        'breakdown': {
            'ppf': ppf, 'epf_employee': epf_employee, 'elss': elss, 'life_insurance': life_insurance,
            'fd_5year': fd_5year, 'nsc': nsc, 'suknya_samriddhi': suknya_samriddhi, 'tuition_fees': tuition_fees,
            'health_insurance_self': health_insurance_self, 'health_insurance_parents': health_insurance_parents,
            'section_80dd': section_80dd, 'section_80ddb': section_80ddb,
            'home_loan_interest': home_loan_interest, 'education_loan_interest': education_loan_interest,
            'nps_80ccd_1b': nps_80ccd_1b, 'nps_80ccd_2': nps_80ccd_2,
            'conveyance_allowance': conveyance_allowance, 'helper_allowance': helper_allowance,
            'lta': lta, 'tel_broadband': tel_broadband, 'ld_allowance': ld_allowance, 'hra_exemption': hra_exemption
        }
    }

def enhanced_multi_month_salary_input(employee_monthly_salary=None, epf_profile=None):
    """Enhanced multi-month salary input with 5-day week and holiday support"""
    st.markdown("""
    <div class="main-header">
        <h2>💰 Multi-Month Salary Details</h2>
        <p>Configure salary details for multiple months with 5-day work week and holiday adjustments</p>
    </div>
    """, unsafe_allow_html=True)
    
    months = ["January", "February", "March", "April", "May", "June",
             "July", "August", "September", "October", "November", "December"]
    
    # Initialize salary data in session state if not exists
    if 'monthly_salaries' not in st.session_state:
        st.session_state.monthly_salaries = {
            month: {
                'total_salary': 0.0, 'basic': 0.0, 'hra': 0.0, 'special_allowances': 0.0,
                'present_days': 0, 'epf': 0.0, 'esi': 0.0, 'holidays': []
            } for month in months
        }
    
    # Enhanced month selection with better UI
    col1, col2 = st.columns(2)
    with col1:
        selected_months = st.multiselect(
            "🗓️ Select months to include in F&F settlement:",
            months,
            default=[],
            help="Choose the months for which F&F settlement needs to be calculated"
        )
    
    with col2:
        if st.button("🔄 Reset All Months", help="Clear all monthly data and start fresh"):
            st.session_state.monthly_salaries = {
                month: {
                    'total_salary': 0.0, 'basic': 0.0, 'hra': 0.0, 'special_allowances': 0.0,
                    'present_days': 0, 'epf': 0.0, 'esi': 0.0, 'holidays': []
                } for month in months
            }
            st.rerun()
    
    if not selected_months:
        st.markdown("""
        <div class="warning-card">
            ⚠️ Please select at least one month for F&F settlement
        </div>
        """, unsafe_allow_html=True)
        return {}
    
    st.markdown("---")
    
    # Use enhanced tabs for month details
    tabs = st.tabs([f"📅 {month}" for month in selected_months])
    for i, month in enumerate(selected_months):
        with tabs[i]:
            st.markdown(f"""
            <div class="employee-card">
                <h3>📅 {month} Details</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Holiday input section
            holidays = holiday_input_section(month)
            st.session_state.monthly_salaries[month]['holidays'] = holidays
            
            # Working days calculation with holidays
            total_working_days = get_total_working_days(month, holidays=holidays)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"""
                <div class="info-card">
                    <strong>📊 Working Days Information (5-day week)</strong><br>
                    Total working days: {total_working_days}<br>
                    Holidays excluded: {len(holidays)}
                </div>
                """, unsafe_allow_html=True)
                
                # Total salary input
                default_total_salary = st.session_state.monthly_salaries[month]['total_salary'] or (employee_monthly_salary or 0.0)
                total_salary = st.number_input(
                    f"💰 Total Salary (₹)", 
                    min_value=0.0, 
                    value=default_total_salary,
                    key=f"total_salary_{month}",
                    step=1000.0
                )
                
                # 🔥 FIX: Present days - ensure default value doesn't exceed max_value
                saved_present_days = st.session_state.monthly_salaries[month]['present_days']
                
                # Calculate safe default value
                if saved_present_days > 0:
                    # Use saved value, but ensure it doesn't exceed total_working_days
                    default_present = min(saved_present_days, total_working_days)
                else:
                    # Use total working days as default, but ensure it's not greater than max
                    default_present = total_working_days
                
                # Ensure default_present is within valid range
                default_present = max(0, min(default_present, total_working_days))
                
                present_days = st.number_input(
                    f"📅 Present Days", 
                    min_value=0, 
                    max_value=max(total_working_days, 1),  # Ensure max_value is at least 1
                    value=default_present,
                    key=f"days_{month}",
                    help=f"Maximum working days for {month}: {total_working_days}"
                )
            
            with col2:
                # ESI
                esi = st.number_input(
                    f"🏥 ESI Deduction (₹)", 
                    min_value=0.0,
                    value=st.session_state.monthly_salaries[month]['esi'],
                    key=f"esi_{month}",
                    step=10.0
                )
            
            # Salary breakdown with EPF calculation
            if total_salary > 0:
                breakdown = salary_breakdown_input_with_epf(
                    month, total_salary, present_days, total_working_days, epf_profile=epf_profile
                )
                
                # Calculate prorated salary
                if present_days > 0 and total_working_days > 0:
                    prorated_salary = (total_salary / total_working_days) * present_days
                    prorated_basic = (breakdown['basic'] / total_working_days) * present_days
                    prorated_hra = (breakdown['hra'] / total_working_days) * present_days
                    prorated_special = (breakdown['special_allowances'] / total_working_days) * present_days
                    
                    st.markdown(f"""
                    <div class="success-card">
                        ✅ Prorated Total: ₹{prorated_salary:,.2f}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    prorated_salary = prorated_basic = prorated_hra = prorated_special = 0
                    st.markdown("""
                    <div class="warning-card">
                        ⚠️ No salary calculated (0 present days)
                    </div>
                    """, unsafe_allow_html=True)
                
                # Update session state with breakdown
                st.session_state.monthly_salaries[month].update({
                    'total_salary': total_salary,
                    'basic': breakdown['basic'],
                    'hra': breakdown['hra'],
                    'special_allowances': breakdown['special_allowances'],
                    'present_days': present_days,
                    'epf': breakdown['epf'],
                    'esi': esi,
                    'total_working_days': total_working_days,
                    'prorated_salary': prorated_salary,
                    'prorated_basic': prorated_basic,
                    'prorated_hra': prorated_hra,
                    'prorated_special': prorated_special,
                    'attendance_ratio': breakdown['attendance_ratio'],
                    'epf_full_month': breakdown['epf_full_month']
                })
    
    # Enhanced summary with visual improvements
    st.markdown("---")
    st.markdown("""
    <div class="main-header">
        <h2>📊 Multi-Month Summary with EPF Details</h2>
    </div>
    """, unsafe_allow_html=True)
    
    active_months = {
        month: data for month, data in st.session_state.monthly_salaries.items() 
        if month in selected_months and (data['total_salary'] > 0 or data['present_days'] > 0)
    }
    
    if active_months:
        summary_data = []
        totals = {
            'total_salary': 0, 'prorated_total': 0, 'prorated_basic': 0,
            'prorated_hra': 0, 'prorated_special': 0, 'total_epf': 0, 'total_esi': 0
        }
        
        full_epf_list = []
        
        for month, data in active_months.items():
            summary_data.append({
                'Month': month,
                'Total Salary': f"₹{data['total_salary']:,.0f}",
                'Days': f"{data['present_days']}/{data['total_working_days']}",
                'Prorated Basic': f"₹{data['prorated_basic']:,.0f}",
                'Prorated HRA': f"₹{data['prorated_hra']:,.0f}",
                'Prorated Special': f"₹{data['prorated_special']:,.0f}",
                'EPF': f"₹{data['epf']:,.0f} ✅",
                'ESI': f"₹{data['esi']:,.0f}"
            })
            
            # Calculate totals
            for key in ['total_salary', 'prorated_salary', 'prorated_basic', 'prorated_hra', 'prorated_special', 'epf', 'esi']:
                totals[key.replace('prorated_salary', 'prorated_total').replace('epf', 'total_epf').replace('esi', 'total_esi')] += data[key]
            
            if 'epf_full_month' in data:
                full_epf_list.append(data['epf_full_month'])
        
        # Add totals row with enhanced styling
        summary_data.append({
            'Month': '🔢 TOTAL',
            'Total Salary': f"₹{totals['total_salary']:,.0f}",
            'Days': '—',
            'Prorated Basic': f"₹{totals['prorated_basic']:,.0f}",
            'Prorated HRA': f"₹{totals['prorated_hra']:,.0f}",
            'Prorated Special': f"₹{totals['prorated_special']:,.0f}",
            'EPF': f"₹{totals['total_epf']:,.0f}",
            'ESI': f"₹{totals['total_esi']:,.0f}"
        })
        
        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True, hide_index=True)
        
        # Enhanced EPF Summary with visual cards
        st.markdown("### 🏦 EPF Calculation Summary")
        col1, col2, col3 = st.columns(3)
        with col1:
            create_enhanced_metric_card("Total EPF (prorated)", f"₹{totals['total_epf']:,.0f}", icon="🏦")
        with col2:
            avg_epf = totals['total_epf'] / len(active_months) if active_months else 0
            create_enhanced_metric_card("Average Monthly EPF (actual)", f"₹{avg_epf:,.0f}", icon="📊")
        with col3:
            avg_full_master = (sum(full_epf_list) / len(full_epf_list)) if full_epf_list else 0
            create_enhanced_metric_card("Avg Full-Month EPF (Master)", f"₹{avg_full_master:,.0f}", icon="📋")
    
    return active_months

def holiday_input_section(month):
    """Add holiday input section for each month"""
    st.markdown("#### 📅 Holidays (Optional)")
    holidays_text = st.text_area(
        f"Holidays in {month} (one date per line, format: YYYY-MM-DD)",
        placeholder="2024-01-26\n2024-01-15",
        key=f"holidays_{month}",
        help="Enter holiday dates that should be excluded from working days"
    )
    
    holidays = []
    if holidays_text.strip():
        for line in holidays_text.strip().split('\n'):
            line = line.strip()
            if line:
                try:
                    holiday_date = datetime.strptime(line, '%Y-%m-%d').date()
                    holidays.append(holiday_date)
                except ValueError:
                    st.warning(f"Invalid date format: {line}. Use YYYY-MM-DD format.")
    
    return holidays

def get_total_working_days(month_name, year=None, holidays=None):
    """
    Calculate working days considering:
    - 5-day work week (Monday-Friday only)
    - Exclude holidays if provided
    """
    month_map = {'January':1,'February':2,'March':3,'April':4,'May':5,'June':6,
                 'July':7,'August':8,'September':9,'October':10,'November':11,'December':12}
    m = month_map.get(month_name)
    if year is None:
        reference = st.session_state.get('last_working_day', date.today())
        year = reference.year if hasattr(reference, 'year') else date.today().year

    total_days = calendar.monthrange(year, m)[1]
    
    # Count only Monday-Friday (weekday 0-4), exclude Saturday(5) and Sunday(6)
    working_days = sum(1 for d in range(1, total_days+1) 
                      if calendar.weekday(year, m, d) < 5)  # 0-4 are Mon-Fri
    
    # Deduct holidays if provided
    if holidays:
        holiday_count = 0
        for holiday_date in holidays:
            try:
                if isinstance(holiday_date, str):
                    holiday_dt = datetime.strptime(holiday_date, '%Y-%m-%d').date()
                else:
                    holiday_dt = holiday_date
                
                # Check if holiday falls in this month and is a working day
                if (holiday_dt.year == year and holiday_dt.month == m and 
                    calendar.weekday(year, m, holiday_dt.day) < 5):
                    holiday_count += 1
            except Exception:
                continue
        
        working_days -= holiday_count
    
    return max(working_days, 0)  # Ensure non-negative

def load_fnf_data():
    """Load F&F submissions from JSON file into session_state.fnf_submissions"""
    try:
        if os.path.exists('fnf_submissions.json'):
            with open('fnf_submissions.json', 'r') as f:
                data = json.load(f)
            st.session_state.fnf_submissions = data.get('submissions', [])
        else:
            st.session_state.fnf_submissions = []
    except Exception as e:
        st.warning(f"Could not load F&F data: {e}")
        st.session_state.fnf_submissions = []

def save_fnf_data():
    """Save current F&F submissions from session_state to JSON file"""
    try:
        payload = {
            'submissions': st.session_state.get('fnf_submissions', []),
            'last_updated': datetime.now().isoformat()
        }
        with open('fnf_submissions.json', 'w') as f:
            json.dump(payload, f, indent=2, default=str)
    except Exception as e:
        st.warning(f"Could not save F&F data: {e}")

def create_analytics_charts():
    """Create enhanced analytics charts"""
    if 'fnf_submissions' not in st.session_state or not st.session_state.fnf_submissions:
        st.markdown("""
        <div class="info-card">
            📊 No data available for analytics. Submit some F&F settlements to see charts here.
        </div>
        """, unsafe_allow_html=True)
        return

    submissions = st.session_state.fnf_submissions
    
    # Status Distribution Pie Chart
    status_counts = {}
    for sub in submissions:
        status = sub['status']
        status_counts[status] = status_counts.get(status, 0) + 1
    
    if status_counts:
        col1, col2 = st.columns(2)
        
        with col1:
            fig_pie = px.pie(
                values=list(status_counts.values()),
                names=list(status_counts.keys()),
                title="📊 F&F Status Distribution",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_pie.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Net Payable Distribution
            amounts = [sub['net_payable'] for sub in submissions if sub.get('net_payable', 0) > 0]
            if amounts:
                fig_hist = px.histogram(
                    x=amounts,
                    title="💰 Net Payable Distribution",
                    labels={'x': 'Net Payable (₹)', 'y': 'Count'},
                    color_discrete_sequence=['#667eea']
                )
                fig_hist.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                )
                st.plotly_chart(fig_hist, use_container_width=True)
    
    # Tax Regime Analysis
    tax_regimes = {}
    total_amounts = {}
    for sub in submissions:
        regime = sub.get('tax_regime', 'Unknown')
        tax_regimes[regime] = tax_regimes.get(regime, 0) + 1
        total_amounts[regime] = total_amounts.get(regime, 0) + sub.get('net_payable', 0)
    
    if len(tax_regimes) > 1:
        col1, col2 = st.columns(2)
        
        with col1:
            fig_regime = px.bar(
                x=list(tax_regimes.keys()),
                y=list(tax_regimes.values()),
                title="🏛️ Tax Regime Preference",
                labels={'x': 'Tax Regime', 'y': 'Count'},
                color=list(tax_regimes.values()),
                color_continuous_scale='Blues'
            )
            fig_regime.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
            )
            st.plotly_chart(fig_regime, use_container_width=True)
        
        with col2:
            fig_amounts = px.bar(
                x=list(total_amounts.keys()),
                y=list(total_amounts.values()),
                title="💸 Total Amounts by Tax Regime",
                labels={'x': 'Tax Regime', 'y': 'Total Amount (₹)'},
                color=list(total_amounts.values()),
                color_continuous_scale='Greens'
            )
            fig_amounts.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
            )
            st.plotly_chart(fig_amounts, use_container_width=True)

def fnf_settlement_form_payroll_only():
    """F&F Settlement Form for Payroll Team - No tax inputs, includes Gratuity"""
    st.markdown("""
    <div class="main-header">
        <h1>📋 Full & Final Settlement Form (Payroll)</h1>
        <p>Payroll processing - Tax deductions handled by Tax Team</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load employee data
    employee_df = load_employee_data()
    
    if employee_df.empty:
        st.error("Could not load employee data")
        return
    
    # Step 1: Enhanced Employee Selection
    st.markdown("""
    <div class="employee-card">
        <h3>🔍 Step 1: Select Employee</h3>
    </div>
    """, unsafe_allow_html=True)
    
    employee_df = employee_df.copy()
    try:
        employee_df['Employee ID'] = pd.to_numeric(employee_df['Employee ID'], errors='coerce').astype('Int64')
    except Exception:
        pass
    employee_df = employee_df.dropna(subset=['Employee ID'])
    employee_df['ID_Name'] = employee_df['Employee ID'].astype(int).astype(str) + " - " + employee_df['Employee Name']
    selected_emp = st.selectbox("Choose Employee", employee_df['ID_Name'].tolist(), index=0 if len(employee_df)>0 else None)
    employee_id = int(selected_emp.split(" - ")[0]) if selected_emp else None
    employee = get_employee_by_id(employee_id, employee_df)
    
    if employee is not None:
        st.markdown(f"""
        <div class="success-card">
            ✅ Employee Found: {employee['Employee Name']}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.error("❌ Employee not found")
        return

    # EPF column selection
    st.caption("💡 If your Employee Master has a specific column for monthly EPF deduction, choose it below.")
    epf_candidates = detect_epf_fixed_columns(employee_df.columns)
    epf_col_choice = st.selectbox(
        "EPF column (Employee Master)",
        options=(["(Auto-detect)"] + epf_candidates) if epf_candidates else ["(None found)"],
        index=1 if epf_candidates else 0
    )
    chosen_epf_col = None
    if epf_candidates and epf_col_choice != "(Auto-detect)":
        chosen_epf_col = epf_col_choice

    # Enhanced Employee Details Display
    st.markdown("""
    <div class="employee-card">
        <h3>👤 Employee Details (Auto-filled)</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h4>📋 Basic Information</h4>
            <p><strong>Employee ID:</strong> {employee['Employee ID']}</p>
            <p><strong>Employee Name:</strong> {employee['Employee Name']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h4>💼 Job Information</h4>
            <p><strong>Designation:</strong> {employee['Designation']}</p>
            <p><strong>Base Location:</strong> {employee['BaseLocation']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h4>📅 Key Details</h4>
            <p><strong>DOJ:</strong> {employee['Date of Joining']}</p>
            <p><strong>PAN No:</strong> {employee['PAN No.']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Step 2: Tax Regime Note (No selection, Tax Team handles this)
    st.markdown("""
    <div class="info-card">
        <h3>🏛️ Tax Processing Note</h3>
        <p>📋 Tax regime selection and investment deductions will be handled by the Tax Team during review.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # EPF policy for this employee (read from Master)
    epf_profile = extract_epf_profile(employee, preferred_epf_col=chosen_epf_col, all_cols=list(employee_df.columns))
    
    # Step 3: Multi-Month Salary Input (default salary from Employee Master)
    employee_monthly_salary = float(employee['Salary']) if 'Salary' in employee and pd.notnull(employee['Salary']) else 0.0
    active_months = enhanced_multi_month_salary_input(employee_monthly_salary=employee_monthly_salary, epf_profile=epf_profile)
    
    if not active_months:
        st.markdown("""
        <div class="warning-card">
            ⚠️ Please add salary details for at least one month to proceed
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Step 4: Payroll-Only F&F Details (NO TAX INPUTS OR INVESTMENT DEDUCTIONS)
    st.markdown("""
    <div class="employee-card">
        <h3>📝 Step 4: Payroll F&F Details</h3>
        <p>💡 Tax deductions and investment calculations will be handled by Tax Team</p>
    </div>
    """, unsafe_allow_html=True)

    # Form for additional details (no buttons inside)
    with st.form("fnf_payroll_details"):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 📅 Important Dates")
            resignation_date = st.date_input("Resignation Date", value=date.today())
            last_working_day = st.date_input("Last Working Day", value=date.today())
            st.session_state['last_working_day'] = last_working_day  # for working-days calc

            # Enhanced Gratuity auto-calc inputs
            doj_str = str(employee['Date of Joining'])
            try:
                if len(doj_str.split('/')[2]) == 2:
                    doj_dt = datetime.strptime(doj_str, '%d/%m/%y')
                else:
                    doj_dt = datetime.strptime(doj_str, '%d/%m/%Y')
            except Exception:
                try:
                    doj_dt = datetime.strptime(doj_str, '%Y-%m-%d')
                except Exception:
                    doj_dt = datetime(date.today().year, 1, 1)

            tenure_years = years_for_gratuity(
                doj_dt, datetime.combine(last_working_day, datetime.min.time())
            )
            last_basic_da = employee_monthly_salary / 3.0
            auto_gratuity = calculate_gratuity(tenure_years, last_basic_da)

            st.caption("💡 Gratuity uses > 6 months counted as +1 year; Last Basic = Salary ÷ 3")
            gratuity = st.number_input("🏆 Gratuity (₹)", value=float(auto_gratuity), min_value=0.0)

            # Enhanced Gratuity calculation details
            with st.expander("🏦 Gratuity Calculation Details", expanded=True):
                raw_gratuity = round((tenure_years * last_basic_da * 15) / 26, 2)
                capped_gratuity = round(min(raw_gratuity, 20_00_000), 2)
                eligible = tenure_years >= 5

                colg1, colg2, colg3 = st.columns(3)
                with colg1:
                    create_enhanced_metric_card("Service (years)", f"{tenure_years:.2f}", icon="📅")
                with colg2:
                    create_enhanced_metric_card("Last Basic (monthly)", f"₹{last_basic_da:,.2f}", icon="💰")
                with colg3:
                    create_enhanced_metric_card("Raw Gratuity", f"₹{raw_gratuity:,.2f}", icon="🧮")

                st.markdown(f"""
                <div class="calculation-box">
                    <h4>Formula: Gratuity = (Years × Last Basic × 15) ÷ 26</h4>
                    <p><strong>Computed:</strong> ({tenure_years:.2f} × ₹{last_basic_da:,.2f} × 15) ÷ 26 = <strong>₹{raw_gratuity:,.2f}</strong></p>
                </div>
                """, unsafe_allow_html=True)
    
                if not eligible:
                    st.markdown("""
                    <div class="warning-card">
                        ❌ Not eligible: service is less than <strong>5 years</strong> → Gratuity = ₹0.00
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    if raw_gratuity > 20_00_000:
                        st.markdown(f"""
                        <div class="info-card">
                            ℹ️ Cap applied: min(₹20,00,000, ₹{raw_gratuity:,.2f}) → <strong>₹{capped_gratuity:,.2f}</strong>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="success-card">
                            ✅ Eligible and <strong>no cap</strong> needed → <strong>₹{capped_gratuity:,.2f}</strong>
                        </div>
                        """, unsafe_allow_html=True)

            # Additional positives  
            bonus = st.number_input("🎁 Bonus (₹)", value=0.0, min_value=0.0)
            leave_encashment = st.number_input("🏖️ Leave Encashment (₹)", value=0.0, min_value=0.0)

        with col2:
            st.markdown("### 📉 Payroll Deductions Only")
 
            # PT only for Chennai and Bangalore
            pt_enabled = str(employee['BaseLocation']).lower() in ['chennai', 'bangalore']
            if pt_enabled:
                pt_total = st.number_input("🏛️ PT - Professional Tax Total (₹)", value=0.0, min_value=0.0)
                st.markdown("""
                <div class="success-card">
                    ✅ PT applicable for Chennai/Bangalore
                </div>
                """, unsafe_allow_html=True)
            else:
                pt_total = 0.0
                st.markdown("""
                <div class="info-card">
                    ℹ️ PT not applicable for this location
                </div>
                """, unsafe_allow_html=True)

            salary_advance = st.number_input("💳 Salary Advance (₹)", value=0.0, min_value=0.0)
            tada_recovery = st.number_input("🚗 TADA Recovery (₹)", value=0.0, min_value=0.0)
            wfh_recovery = st.number_input("🏠 WFH Recovery (₹)", value=0.0, min_value=0.0)
            notice_period_recovery = st.number_input("⏰ Notice Period Recovery (₹)", value=0.0, min_value=0.0)
            other_deductions = st.number_input("📝 Other Deductions (₹)", value=0.0, min_value=0.0)

            # Information about tax calculation
            st.markdown("""
            <div class="info-card">
                📋 <strong>Tax Calculation Note:</strong><br>
                • TDS and investment deductions will be calculated by Tax Team<br>
                • Tax regime selection handled during tax review<br>
                • This form covers payroll components only
            </div>
            """, unsafe_allow_html=True)

        # ✅ Submit button MUST be inside this form block
        calculate_clicked = st.form_submit_button("🧮 Calculate Payroll F&F", use_container_width=True)

    # Process calculation when form is submitted
    if calculate_clicked:
        # Store calculation results in session state (PAYROLL ONLY - NO TAX CALCULATIONS)
        st.session_state.calculation_done = True
        st.session_state.calculation_data = {
            'resignation_date': resignation_date,
            'last_working_day': last_working_day,
            'gratuity': gratuity,
            'bonus': bonus,
            'leave_encashment': leave_encashment,
            'pt_total': pt_total,
            'salary_advance': salary_advance,
            'tada_recovery': tada_recovery,
            'wfh_recovery': wfh_recovery,
            'notice_period_recovery': notice_period_recovery,
            'other_deductions': other_deductions,
            'tenure_years': tenure_years,
            'last_basic_da': last_basic_da
        }

    # Enhanced calculation results display (PAYROLL VIEW ONLY)
    if st.session_state.get('calculation_done', False):
        data = st.session_state.calculation_data

        # ---- Totals from active months (earnings components only) ----
        totals = {
            'total_salary': sum(m['total_salary'] for m in active_months.values()),
            'prorated_total': sum(m['prorated_salary'] for m in active_months.values()),
            'prorated_basic': sum(m['prorated_basic'] for m in active_months.values()),
            'prorated_hra': sum(m['prorated_hra'] for m in active_months.values()),
            'prorated_special': sum(m['prorated_special'] for m in active_months.values()),
            'total_epf': sum(m['epf'] for m in active_months.values()),
            'total_esi': sum(m['esi'] for m in active_months.values()),
        }

        # ---- Payroll calculation (NO TAX CALCULATIONS HERE) ----
        total_earnings = totals['prorated_total'] + data['gratuity'] + data['bonus'] + data['leave_encashment']

        # ---- Payroll deductions only ----
        payroll_deductions = (
            totals['total_epf'] + totals['total_esi'] + data['salary_advance'] + data['tada_recovery'] +
            data['wfh_recovery'] + data['notice_period_recovery'] + data['other_deductions']
        )

        # PT deduction
        pt_deduction = float(data.get('pt_total', 0.0) or 0.0)

        # Net before tax (Tax Team will calculate final TDS)
        net_before_tax = total_earnings - payroll_deductions - pt_deduction

        # Enhanced results display
        st.markdown("---")
        st.markdown("""
        <div class="main-header">
            <h2>📊 Payroll F&F Summary (Tax Team Review Pending)</h2>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="info-card">
            🛈 <strong>Important Note:</strong> This summary shows payroll components only. Tax calculations and final settlement amount will be determined by Tax Team.
        </div>
        """, unsafe_allow_html=True)

        # ---- Enhanced Month-wise breakdown ----
        st.markdown("### 📅 Month-wise Salary Breakdown")
        month_breakdown = []
        for month, m in active_months.items():
            month_breakdown.append({
                'Month': month,
                'Total Salary': f"₹{m['total_salary']:,.2f}",
                'Days': f"{m['present_days']}/{m['total_working_days']}",
                'Prorated Basic': f"₹{m['prorated_basic']:,.2f}",
                'Prorated HRA': f"₹{m['prorated_hra']:,.2f}",
                'Prorated Special': f"₹{m['prorated_special']:,.2f}",
                'EPF': f"₹{m['epf']:,.2f}",
                'ESI': f"₹{m['esi']:,.2f}",
            })
        month_df = pd.DataFrame(month_breakdown)
        st.dataframe(month_df, use_container_width=True, hide_index=True)

        # ---- Enhanced Overall Summary (PAYROLL ONLY) ----
        st.markdown("### 💰 Payroll F&F Summary")
        colo1, colo2, colo3 = st.columns(3)

        with colo1:
            st.markdown("""
            <div class="success-card">
                <h3>✅ EARNINGS</h3>
            </div>
            """, unsafe_allow_html=True)
            
            create_enhanced_metric_card("Basic Salary", f"₹{totals['prorated_basic']:,.2f}", icon="💰")
            create_enhanced_metric_card("HRA", f"₹{totals['prorated_hra']:,.2f}", icon="🏠")
            create_enhanced_metric_card("Special Allowances", f"₹{totals['prorated_special']:,.2f}", icon="📋")
            create_enhanced_metric_card("Gratuity", f"₹{data['gratuity']:,.2f}", icon="🏆")
            create_enhanced_metric_card("Bonus", f"₹{data['bonus']:,.2f}", icon="🎁")
            create_enhanced_metric_card("Leave Encashment", f"₹{data['leave_encashment']:,.2f}", icon="🏖️")
            
            st.markdown("---")
            create_enhanced_metric_card("Total Earnings", f"₹{total_earnings:,.2f}", icon="💵")

        with colo2:
            st.markdown("""
            <div class="warning-card">
                <h3>📉 PAYROLL DEDUCTIONS</h3>
            </div>
            """, unsafe_allow_html=True)
            
            create_enhanced_metric_card("Total EPF", f"₹{totals['total_epf']:,.2f}", icon="🏦")
            create_enhanced_metric_card("Total ESI", f"₹{totals['total_esi']:,.2f}", icon="🏥")
            create_enhanced_metric_card("PT", f"₹{pt_deduction:,.2f}", icon="🏛️")
            create_enhanced_metric_card("Salary Advance", f"₹{data['salary_advance']:,.2f}", icon="💳")
            create_enhanced_metric_card("TADA Recovery", f"₹{data['tada_recovery']:,.2f}", icon="🚗")
            create_enhanced_metric_card("WFH Recovery", f"₹{data['wfh_recovery']:,.2f}", icon="🏠")
            create_enhanced_metric_card("Notice Period", f"₹{data['notice_period_recovery']:,.2f}", icon="⏰")
            create_enhanced_metric_card("Other", f"₹{data['other_deductions']:,.2f}", icon="📝")
            
            st.markdown("---")
            create_enhanced_metric_card("Total Payroll Deductions", f"₹{payroll_deductions + pt_deduction:,.2f}", icon="📉")

        with colo3:
            st.markdown("""
            <div class="info-card">
                <h3>💼 NET (Before Tax)</h3>
            </div>
            """, unsafe_allow_html=True)
            
            create_enhanced_metric_card("Net Before Tax", f"₹{net_before_tax:,.2f}", delta="Pending Tax Review", icon="💰")
            
            st.markdown("""
            <div class="warning-card">
                ⏳ <strong>Next Steps:</strong><br>
                • Tax Team will calculate TDS<br>
                • Investment deductions review<br>
                • Final settlement amount
            </div>
            """, unsafe_allow_html=True)

        # ---- Persist submission (PAYROLL DATA ONLY) ----
        fnf_data = {
            'employee_id': int(employee['Employee ID']),
            'employee_name': employee['Employee Name'],
            'designation': employee['Designation'],
            'base_location': employee['BaseLocation'],
            'doj': employee['Date of Joining'],
            'resignation_date': data['resignation_date'].strftime('%d/%m/%Y'),
            'last_working_day': data['last_working_day'].strftime('%d/%m/%Y'),
            'active_months': active_months,
            'salary_totals': totals,
            'gratuity': data['gratuity'],
            'bonus': data['bonus'],
            'leave_encashment': data['leave_encashment'],
            'total_earnings': total_earnings,
            'pt_total': pt_deduction,
            'salary_advance': data['salary_advance'],
            'tada_recovery': data['tada_recovery'],
            'wfh_recovery': data['wfh_recovery'],
            'notice_period_recovery': data['notice_period_recovery'],
            'other_deductions': data['other_deductions'],
            'payroll_deductions': payroll_deductions,
            'net_before_tax': net_before_tax,
            'status': 'Pending Tax Review',
            'tenure_years': data['tenure_years'],
            'last_basic_da': data['last_basic_da'],
            'payroll_calculated': True,
            'tax_calculated': False,
            # Tax fields will be populated by Tax Team
            'tax_regime': None,
            'investments_data': {},
            'tds_amount': 0.0,
            'total_deductions': 0.0,
            'net_payable': 0.0,
            'taxable_income': 0.0
        }

        if 'fnf_submissions' not in st.session_state:
            st.session_state.fnf_submissions = []

        existing_index = None
        for i, submission in enumerate(st.session_state.fnf_submissions):
            if submission['employee_id'] == int(employee['Employee ID']):
                existing_index = i
                break

        if existing_index is not None:
            st.session_state.fnf_submissions[existing_index] = fnf_data
        else:
            st.session_state.fnf_submissions.append(fnf_data)

        # Enhanced Actions
        st.markdown("---")
        st.markdown("### 🎯 Next Steps")
        c1, c2, c3 = st.columns(3)

        with c1:
            if st.button("📤 Send to Tax Team", use_container_width=True):
                fnf_data['status'] = 'Under Tax Review'
                st.session_state.fnf_submissions[existing_index if existing_index is not None else -1] = fnf_data
                save_fnf_data()
                st.success("✅ Payroll F&F sent to Tax Team for tax calculation and review!")
                st.balloons()
                st.session_state.calculation_done = False
                st.rerun()

        with c2:
            if st.button("💾 Save Draft", use_container_width=True):
                fnf_data['status'] = 'Draft'
                st.session_state.fnf_submissions[existing_index if existing_index is not None else -1] = fnf_data
                save_fnf_data()
                st.info("💾 Payroll F&F saved as draft")
                st.session_state.calculation_done = False
                st.rerun()

        with c3:
            if st.button("📄 Payroll Report", use_container_width=True):
                st.info("📄 Payroll F&F report generated! Tax calculations pending.")

# File constants
FNF_FILE = "fnf_submissions.json"
FNF_CLOSED_FILE = "fnf_closed.json"

def load_fnf_closed_data():
    try:
        if os.path.exists(FNF_CLOSED_FILE):
            with open(FNF_CLOSED_FILE, "r") as f:
                return json.load(f)
    except Exception:
        pass
    return []

def save_fnf_closed_data(data):
    try:
        with open(FNF_CLOSED_FILE, "w") as f:
            json.dump(data, f, indent=2, default=str)
    except Exception as e:
        st.warning(f"Could not save closed F&F data: {e}")
        
def recompute_tax_updated(submission: dict, inv: dict, new_regime: str):
    """
    Updated tax computation with New Regime restrictions:
    - New Regime: Only 80CCD(2) allowed, no other deductions including EPF
    - Old Regime: All deductions as before
    """
    def _f(x, default=0.0):
        try: return float(x if x is not None else default)
        except Exception: return float(default)
    def _sum(d: dict, keys: list[str]) -> float:
        return sum(_f(d.get(k, 0.0)) for k in keys)

    # Earnings used for slab (gratuity excluded)
    taxable_earnings = (
        _f(submission.get('salary_totals', {}).get('prorated_total', 0.0))
        + _f(submission.get('bonus', 0.0))
        + _f(submission.get('leave_encashment', 0.0))
    )
    pt_deduction = _f(submission.get('pt_total', 0.0))

    # Normalize investments
    br = (inv or {}).get('breakdown', {})
    
    # Standard deduction (FY-aware for New regime)
    fy_start = _fy_start_year_from_session()
    std_deduction = 75_000.0 if (new_regime == "New Tax Regime" and fy_start >= 2025) else 50_000.0

    # Regime-specific deduction calculation
    if new_regime == "New Tax Regime":
        # NEW REGIME: Only 80CCD(2) allowed
        inv_80c = 0.0  # No 80C deductions in new regime
        inv_80d = 0.0  # No 80D deductions in new regime
        inv_other = _f(br.get('nps_80ccd_2', 0.0))  # Only employer NPS contribution
        exempt_allowances = 0.0  # No exempt allowances in new regime
        inv_total_for_tax = inv_other  # Only 80CCD(2)
        
        taxable_income = max(0.0, taxable_earnings - std_deduction - pt_deduction - inv_total_for_tax)
        tds_amount = tds_new_from_total_income(taxable_income)
        
    else:
        # OLD REGIME: All deductions allowed
        c80c_keys = ['ppf','epf_employee','elss','life_insurance','fd_5year','nsc','suknya_samriddhi','tuition_fees']
        inv_80c_uncapped = _sum(br, c80c_keys)
        inv_80c = min(inv_80c_uncapped, 150000.0)
        
        inv_80d = _sum(br, ['health_insurance_self','health_insurance_parents'])
        inv_other = _sum(br, ['section_80dd','section_80ddb','home_loan_interest','education_loan_interest','nps_80ccd_1b','nps_80ccd_2'])
        exempt_allowances = _sum(br, ['conveyance_allowance','helper_allowance','lta','tel_broadband','ld_allowance','hra_exemption'])
        inv_total_for_tax = inv_80c + inv_80d + inv_other
        
        taxable_income = max(0.0, taxable_earnings - std_deduction - pt_deduction - inv_total_for_tax - exempt_allowances)
        tds_amount = tds_old_from_total_income(taxable_income)

    # Payroll-side deductions (do not affect taxable income)
    payroll_deductions = (
        _f(submission.get('salary_totals', {}).get('total_epf', 0.0))
        + _f(submission.get('salary_totals', {}).get('total_esi', 0.0))
        + _f(submission.get('salary_advance', 0.0))
        + _f(submission.get('tada_recovery', 0.0))
        + _f(submission.get('wfh_recovery', 0.0))
        + _f(submission.get('notice_period_recovery', 0.0))
        + _f(submission.get('other_deductions', 0.0))
    )

    # Totals & net
    total_earnings = _f(submission.get('total_earnings', 0.0))
    if total_earnings == 0.0:
        total_earnings = (
            _f(submission.get('salary_totals', {}).get('prorated_total', 0.0))
            + _f(submission.get('gratuity', 0.0))
            + _f(submission.get('bonus', 0.0))
            + _f(submission.get('leave_encashment', 0.0))
        )

    total_deductions = payroll_deductions + pt_deduction + tds_amount
    net_payable = total_earnings - total_deductions

    # Build investment data structure
    if new_regime == "New Tax Regime":
        investments_data = {
            '80c_total': 0.0,
            '80d_total': 0.0,
            'other_deductions': round(inv_other, 2),
            'exempt_allowances': 0.0,
            'total_deductions': round(inv_other, 2),
            'breakdown': {'nps_80ccd_2': _f(br.get('nps_80ccd_2', 0.0))}
        }
    else:
        investments_data = {
            '80c_total': round(inv_80c, 2),
            '80d_total': round(inv_80d, 2),
            'other_deductions': round(inv_other, 2),
            'exempt_allowances': round(exempt_allowances, 2),
            'total_deductions': round(inv_total_for_tax, 2),
            'breakdown': {k: _f(br.get(k, 0.0)) for k in set(c80c_keys + [
                'health_insurance_self','health_insurance_parents','section_80dd','section_80ddb',
                'home_loan_interest','education_loan_interest','nps_80ccd_1b','nps_80ccd_2',
                'conveyance_allowance','helper_allowance','lta','tel_broadband','ld_allowance','hra_exemption'
            ])}
        }

    return {
        'regime': new_regime,
        'taxable_earnings': round(taxable_earnings, 2),
        'std_deduction': round(std_deduction, 2),
        'pt_deduction': round(pt_deduction, 2),
        'inv_80c': round(inv_80c, 2),
        'inv_80d': round(inv_80d, 2),
        'inv_other': round(inv_other, 2),
        'exempt_allowances': round(exempt_allowances, 2),
        'inv_total_for_tax': round(inv_total_for_tax, 2),
        'taxable_income': round(taxable_income, 2),
        'tds_amount': round(tds_amount, 2),
        'payroll_deductions': round(payroll_deductions, 2),
        'total_deductions': round(total_deductions, 2),
        'total_earnings': round(total_earnings, 2),
        'net_payable': round(net_payable, 2),
        'investments_data': investments_data,
    }
    
def tax_review_dashboard_updated():
    """Updated Tax Review Dashboard with regime-specific deduction inputs"""
    st.markdown("""
    <div class="main-header">
        <h1>🔍 Tax Review Dashboard</h1>
        <p>Review and approve F&F settlements with comprehensive tax analysis</p>
    </div>
    """, unsafe_allow_html=True)

    if 'fnf_submissions' not in st.session_state or not st.session_state.fnf_submissions:
        st.info("No F&F submissions for review yet.")
        return

    review_submissions = [
        s for s in st.session_state.fnf_submissions
        if s['status'] in ['Under Tax Review', 'Pending Tax Review', 'Tax Approved', 'Tax Rejected']
    ]
    if not review_submissions:
        st.info("Nothing pending for tax review.")
        return

    def k(base, idx): return f"{base}_{idx}"

    for i, submission in enumerate(review_submissions):
        with st.expander(f"{submission['employee_name']} (ID: {submission['employee_id']}) – {submission['status']}", expanded=True):
            # Header metrics
            c1, c2, c3 = st.columns(3)
            with c1: create_enhanced_metric_card("Taxable Income", f"₹{submission.get('taxable_income', 0):,.0f}", icon="📄")
            with c2: create_enhanced_metric_card("Current TDS", f"₹{submission.get('tds_amount', 0):,.0f}", icon="🏛️")
            with c3: create_enhanced_metric_card("Net Payable", f"₹{submission.get('net_payable', 0):,.0f}", icon="💼")

            inv_saved = submission.get('investments_data', {}) or {}
            breakdown_saved = inv_saved.get('breakdown', {})

            st.markdown("### 🏛️ Tax Regime Selection")
            # Regime selection
            new_tax_regime = st.selectbox(
                "Tax Regime",
                ["Old Tax Regime", "New Tax Regime"],
                index=0 if submission.get('tax_regime') == "Old Tax Regime" else 1,
                key=k("regime", i)
            )
            
            # Show regime-specific information
            if new_tax_regime == "New Tax Regime":
                st.markdown("""
                <div class="warning-card">
                    ⚠️ <strong>New Tax Regime Restrictions:</strong><br>
                    • Only 80CCD(2) deduction allowed<br>
                    • No EPF employee contribution deduction<br>
                    • No other investment deductions<br>
                    • No exempt allowances
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="success-card">
                    ✅ <strong>Old Tax Regime:</strong><br>
                    • All investment deductions available<br>
                    • EPF employee contribution deductible<br>
                    • Exempt allowances applicable
                </div>
                """, unsafe_allow_html=True)

            # 🔥 Initialize all variables first to avoid UnboundLocalError
            # Initialize all variables with default values
            ppf = elss = life = fd5 = nsc = suk = tuition = 0.0
            hi_self = hi_par = sec_dd = sec_ddb = 0.0
            hli = eli = nps1b = 0.0
            conv = helper = lta = tel = ld = hra_ex = 0.0
            epf_employee = 0.0
            nps2 = 0.0

            # Regime-specific input sections
            if new_tax_regime == "New Tax Regime":
                # NEW REGIME: Only 80CCD(2)
                st.markdown("#### 🏦 Available Deductions (New Tax Regime)")
                nps2 = st.number_input("🏢 NPS 80CCD(2) Employer Contribution", 0.0, step=1000.0, 
                                       value=float(breakdown_saved.get('nps_80ccd_2', 0.0)), key=k("nps2", i))
                
                # Create investment dict for NEW regime (only NPS 80CCD(2))
                inv_dict = {
                    'breakdown': {
                        'nps_80ccd_2': nps2,
                        # All other fields set to 0
                        'ppf': 0.0, 'epf_employee': 0.0, 'elss': 0.0, 'life_insurance': 0.0,
                        'fd_5year': 0.0, 'nsc': 0.0, 'suknya_samriddhi': 0.0, 'tuition_fees': 0.0,
                        'health_insurance_self': 0.0, 'health_insurance_parents': 0.0,
                        'section_80dd': 0.0, 'section_80ddb': 0.0,
                        'home_loan_interest': 0.0, 'education_loan_interest': 0.0, 'nps_80ccd_1b': 0.0,
                        'conveyance_allowance': 0.0, 'helper_allowance': 0.0, 'lta': 0.0,
                        'tel_broadband': 0.0, 'ld_allowance': 0.0, 'hra_exemption': 0.0
                    }
                }
                
            else:
                # OLD REGIME: All deductions
                st.markdown("#### 📊 Section 80C (Max ₹1,50,000)")
                c80c1, c80c2 = st.columns(2)
                with c80c1:
                    ppf = st.number_input("💰 PPF", 0.0, step=1000.0, value=float(breakdown_saved.get('ppf', 0.0)), key=k("ppf", i))
                    epf_default = breakdown_saved.get('epf_employee')
                    if epf_default is None:
                        epf_default = float(submission.get('salary_totals', {}).get('total_epf', 0.0))
                    epf_employee = st.number_input("🏦 EPF (Employee)", 0.0, step=100.0, value=float(epf_default), key=k("epfemp", i))
                    elss = st.number_input("📈 ELSS", 0.0, step=1000.0, value=float(breakdown_saved.get('elss', 0.0)), key=k("elss", i))
                    life = st.number_input("🛡️ Life Insurance", 0.0, step=500.0, value=float(breakdown_saved.get('life_insurance', 0.0)), key=k("life", i))
                with c80c2:
                    fd5 = st.number_input("🏛️ 5-Year FD", 0.0, step=1000.0, value=float(breakdown_saved.get('fd_5year', 0.0)), key=k("fd5", i))
                    nsc = st.number_input("📜 NSC", 0.0, step=1000.0, value=float(breakdown_saved.get('nsc', 0.0)), key=k("nsc", i))
                    suk = st.number_input("👧 Sukanya Samriddhi", 0.0, step=1000.0, value=float(breakdown_saved.get('suknya_samriddhi', 0.0)), key=k("suk", i))
                    tuition = st.number_input("🎓 Tuition Fees", 0.0, step=1000.0, value=float(breakdown_saved.get('tuition_fees', 0.0)), key=k("tuition", i))

                # 80D & Others
                st.markdown("#### 🏥 Health & Other Deductions")
                d1, d2 = st.columns(2)
                with d1:
                    hi_self = st.number_input("👨‍👩‍👧 Self & Family (80D)", 0.0, step=1000.0, value=float(breakdown_saved.get('health_insurance_self', 0.0)), key=k("hi_self", i))
                    hi_par = st.number_input("👴👵 Parents (80D)", 0.0, step=1000.0, value=float(breakdown_saved.get('health_insurance_parents', 0.0)), key=k("hi_par", i))
                    sec_dd = st.number_input("♿ 80DD", 0.0, step=1000.0, value=float(breakdown_saved.get('section_80dd', 0.0)), key=k("80dd", i))
                    sec_ddb = st.number_input("🏥 80DDB", 0.0, step=1000.0, value=float(breakdown_saved.get('section_80ddb', 0.0)), key=k("80ddb", i))
                with d2:
                    hli = st.number_input("🏠 Home Loan Interest", 0.0, step=5000.0, value=float(breakdown_saved.get('home_loan_interest', 0.0)), key=k("hli", i))
                    eli = st.number_input("📚 Education Loan Interest", 0.0, step=2000.0, value=float(breakdown_saved.get('education_loan_interest', 0.0)), key=k("eli", i))
                    nps1b = st.number_input("🏦 NPS 80CCD(1B)", 0.0, step=1000.0, value=float(breakdown_saved.get('nps_80ccd_1b', 0.0)), key=k("nps1b", i))
                    nps2 = st.number_input("🏢 NPS 80CCD(2) Employer", 0.0, step=1000.0, value=float(breakdown_saved.get('nps_80ccd_2', 0.0)), key=k("nps2", i))

                # Exempt allowances
                st.markdown("#### 🚗 Exempt Allowances")
                a1, a2 = st.columns(2)
                with a1:
                    conv = st.number_input("🚗 Conveyance", 0.0, step=1000.0, value=float(breakdown_saved.get('conveyance_allowance', 0.0)), key=k("conv", i))
                    helper = st.number_input("🏠 Helper", 0.0, step=500.0, value=float(breakdown_saved.get('helper_allowance', 0.0)), key=k("helper", i))
                    lta = st.number_input("✈️ LTA", 0.0, step=5000.0, value=float(breakdown_saved.get('lta', 0.0)), key=k("lta", i))
                with a2:
                    tel = st.number_input("📞 Telephone/Broadband", 0.0, step=500.0, value=float(breakdown_saved.get('tel_broadband', 0.0)), key=k("tel", i))
                    ld = st.number_input("📚 L&D Allowance", 0.0, step=1000.0, value=float(breakdown_saved.get('ld_allowance', 0.0)), key=k("ld", i))
                    hra_ex = st.number_input("🏠 HRA Exemption", 0.0, step=2000.0, value=float(breakdown_saved.get('hra_exemption', 0.0)), key=k("hraex", i))

                # Create investment dict for OLD regime (all deductions)
                inv_dict = {
                    'breakdown': {
                        'ppf': ppf, 'epf_employee': epf_employee, 'elss': elss, 'life_insurance': life,
                        'fd_5year': fd5, 'nsc': nsc, 'suknya_samriddhi': suk, 'tuition_fees': tuition,
                        'health_insurance_self': hi_self, 'health_insurance_parents': hi_par,
                        'section_80dd': sec_dd, 'section_80ddb': sec_ddb,
                        'home_loan_interest': hli, 'education_loan_interest': eli,
                        'nps_80ccd_1b': nps1b, 'nps_80ccd_2': nps2,
                        'conveyance_allowance': conv, 'helper_allowance': helper, 'lta': lta,
                        'tel_broadband': tel, 'ld_allowance': ld, 'hra_exemption': hra_ex
                    }
                }

            # PT editable by tax team
            pt_edit = st.number_input("🏛️ PT (u/s 16(iii))", 0.0, step=100.0,
                                      value=float(submission.get('pt_total', 0.0)), key=k("pt", i))

            # Live preview with updated calculation
            sub_preview = dict(submission)
            sub_preview['pt_total'] = pt_edit
            preview = recompute_tax_updated(sub_preview, inv_dict, new_tax_regime)

            # Summary cards (live)
            st.markdown("### 📋 Investment & Deduction Summary")
            s1, s2, s3, s4 = st.columns(4)
            with s1: create_enhanced_metric_card("80C (cap ₹1.5L)", f"₹{preview['inv_80c']:,.0f}", icon="📊")
            with s2: create_enhanced_metric_card("80D", f"₹{preview['inv_80d']:,.0f}", icon="🏥")
            with s3: create_enhanced_metric_card("Other Deductions", f"₹{preview['inv_other']:,.0f}", icon="📋")
            with s4: create_enhanced_metric_card("Exempt Allowances", f"₹{preview['exempt_allowances']:,.0f}", icon="🚗")

            # TDS override & additional tax deductions (live)
            tds_auto = float(preview['tds_amount'])
            new_tds = st.number_input("Revised TDS (manual override)", 0.0, step=500.0, value=tds_auto, key=k("tds", i))
            addl_tax_ded = st.number_input("Additional Tax Deductions (if any)", 0.0, step=500.0,
                                           value=float(submission.get('additional_deductions', 0.0)), key=k("addtax", i))

            revised_total_deductions = preview['total_deductions'] - preview['tds_amount'] + new_tds + addl_tax_ded
            revised_net_payable = preview['total_earnings'] - revised_total_deductions

            st.markdown("### 🧮 Revised Calculation Preview")
            p1, p2, p3, p4 = st.columns(4)
            with p1: create_enhanced_metric_card("Taxable Income", f"₹{preview['taxable_income']:,.0f}", icon="🧾")
            with p2: create_enhanced_metric_card("TDS (manual)", f"₹{new_tds:,.0f}", delta=f"{(new_tds-tds_auto):+,.0f}", icon="🏛️")
            with p3: create_enhanced_metric_card("Total Deductions", f"₹{revised_total_deductions:,.0f}", icon="📉")
            with p4: create_enhanced_metric_card("Net Payable", f"₹{revised_net_payable:,.0f}", delta=f"{(revised_net_payable - preview['net_payable']):+,.0f}", icon="💼")

            # --- Submit section: a form with an actual submit button ---
            with st.form(k("submit_form", i), clear_on_submit=False):
                decision = st.selectbox("Decision", ["Approve", "Send Back for Revision"], key=k("decision", i))
                comments = st.text_area("Comments", value=submission.get('tax_comments', ''), key=k("comments", i))
                submit_btn = st.form_submit_button("📋 Submit Tax Review", use_container_width=True)

            if submit_btn:
                # Persist current widget values
                submission['tax_regime'] = new_tax_regime
                submission['pt_total'] = pt_edit

                inv_save = dict(preview['investments_data'])
                inv_save['breakdown'] = inv_dict['breakdown']
                submission['investments_data'] = inv_save

                submission['taxable_income'] = preview['taxable_income']
                submission['tds_amount'] = new_tds
                submission['additional_deductions'] = addl_tax_ded
                submission['total_deductions'] = revised_total_deductions
                submission['net_payable'] = revised_net_payable

                submission['tax_comments'] = comments
                submission['tax_reviewed_by'] = st.session_state.get('username', 'Tax Team')
                submission['tax_review_date'] = datetime.now().strftime('%d/%m/%Y %H:%M')
                submission['status'] = 'Tax Approved' if decision == "Approve" else 'Tax Rejected'
                submission['tax_calculated'] = True

                save_fnf_data()
                if decision == "Approve":
                    st.success("✅ Approved and saved!")
                    st.balloons()
                else:
                    st.error("❌ Sent back to Payroll for revision.")
                st.rerun()

def payroll_dashboard():
    """Enhanced Payroll Dashboard (no tax-investment inputs on Payroll)"""
    st.markdown("""
    <div class="main-header">
        <h1>💼 Payroll Team Dashboard</h1>
        <p>Comprehensive payroll management and F&F settlement processing</p>
    </div>
    """, unsafe_allow_html=True)

    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "👥 Employee Master",
        "📋 F&F Settlement",
        "📊 F&F Status",
        "📈 Analytics",
        "🎯 Quick Actions",
    ])

    # --- Tab 1: Employee Master ---
    with tab1:
        st.markdown("""
        <div class="employee-card">
            <h3>👥 Employee Master Data</h3>
            <p>Search and manage employee information</p>
        </div>
        """, unsafe_allow_html=True)

        employee_df = load_employee_data()

        if not employee_df.empty:
            col1, col2 = st.columns([2, 1])
            with col1:
                search_term = st.text_input("🔍 Search Employee (ID or Name)",
                                            placeholder="Enter employee ID or name...")
            with col2:
                show_all = st.checkbox("Show All Employees", value=False)

            if search_term or show_all:
                if search_term and not show_all:
                    filtered_df = employee_df[
                        (employee_df['Employee ID'].astype(str).str.contains(search_term, na=False)) |
                        (employee_df['Employee Name'].str.contains(search_term, case=False, na=False))
                    ]
                else:
                    filtered_df = employee_df

                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    create_enhanced_metric_card("Total Employees", len(filtered_df), icon="👥")
                with c2:
                    avg_salary = filtered_df['Salary'].mean() if 'Salary' in filtered_df.columns else 0
                    create_enhanced_metric_card("Average Salary", f"₹{avg_salary:,.0f}", icon="💰")
                with c3:
                    locations = filtered_df['BaseLocation'].nunique() if 'BaseLocation' in filtered_df.columns else 0
                    create_enhanced_metric_card("Locations", locations, icon="🌍")
                with c4:
                    designations = filtered_df['Designation'].nunique() if 'Designation' in filtered_df.columns else 0
                    create_enhanced_metric_card("Designations", designations, icon="💼")

                st.dataframe(filtered_df, use_container_width=True, height=400)
            else:
                st.markdown("""
                <div class="info-card">
                    💡 Enter search terms or check "Show All Employees" to view data
                </div>
                """, unsafe_allow_html=True)
        else:
            st.error("Could not load employee data")

    # --- Tab 2: F&F Settlement (Payroll flow only; NO tax investments here) ---
    with tab2:
        # 🔥 CHANGE THIS LINE:
        fnf_settlement_form_payroll_only()  # ← Changed from fnf_settlement_form()

    # --- Tab 3: F&F Status ---
    with tab3:
        st.markdown("""
        <div class="employee-card">
            <h3>📊 F&F Settlement Status</h3>
            <p>Track and manage all F&F settlement submissions</p>
        </div>
        """, unsafe_allow_html=True)

        if 'fnf_submissions' in st.session_state and st.session_state.fnf_submissions:
            # Overview metrics
            status_counts = {}
            total_amounts = {}
            for submission in st.session_state.fnf_submissions:
                status = submission['status']
                status_counts[status] = status_counts[status] + 1 if status in status_counts else 1
                total_amounts[status] = total_amounts.get(status, 0) + submission.get('net_payable', 0)

            st.markdown("### 📈 Status Overview")
            cols = st.columns(max(1, len(status_counts)))
            for i, (status, count) in enumerate(status_counts.items()):
                with cols[i]:
                    create_enhanced_metric_card(
                        status,
                        count,
                        delta=f"₹{total_amounts[status]:,.0f}",
                        icon="📋"
                    )

            st.markdown("---")

            # Individual submissions
            for submission in st.session_state.fnf_submissions:
                status_badge = create_status_badge(submission['status'])

                with st.expander(f"{submission['employee_name']} - {submission['status']}", expanded=False):
                    col1, col2, col3 = st.columns(3)

                    # Employee & regime info
                    with col1:
                        st.markdown(f"""
                        <div class="metric-card">
                            <h4>👤 Employee Info</h4>
                            <p><strong>Employee:</strong> {submission['employee_name']}</p>
                            <p><strong>Employee ID:</strong> {submission['employee_id']}</p>
                            <p><strong>Last Working Day:</strong> {submission['last_working_day']}</p>
                        </div>
                        """, unsafe_allow_html=True)

                        if 'active_months' in submission:
                            months_list = list(submission['active_months'].keys())
                            st.markdown(f"**Months:** {', '.join(months_list)}")

                    # Financial summary (no investment display on Payroll view)
                    with col2:
                        # Show different metrics based on calculation status
                        if submission.get('tax_calculated', False):
                            net_amount = submission.get('net_payable', 0)
                            amount_label = "Net Payable"
                        else:
                            net_amount = submission.get('net_before_tax', 0)
                            amount_label = "Net Before Tax"
                            
                        st.markdown(f"""
                        <div class="metric-card">
                            <h4>💰 Financial Summary</h4>
                            <p><strong>Status:</strong> {status_badge}</p>
                            <p><strong>Total Earnings:</strong> ₹{submission['total_earnings']:,.2f}</p>
                            <p><strong>{amount_label}:</strong> ₹{net_amount:,.2f}</p>
                        </div>
                        """, unsafe_allow_html=True)

                        if 'salary_totals' in submission:
                            st.markdown(f"""
                            <div class="metric-card">
                                <h4>📊 Salary Details</h4>
                                <p><strong>Basic Salary:</strong> ₹{submission['salary_totals'].get('prorated_basic', 0):,.2f}</p>
                                <p><strong>HRA:</strong> ₹{submission['salary_totals'].get('prorated_hra', 0):,.2f}</p>
                                <p><strong>EPF:</strong> ₹{submission['salary_totals'].get('total_epf', 0):,.2f}</p>
                            </div>
                            """, unsafe_allow_html=True)

                    # Actions
                    with col3:
                        if submission['status'] == 'Tax Approved':
                            if st.button(f"💰 Process Payment", key=f"pay_{submission['employee_id']}"):
                                submission['status'] = 'Payment Processed'
                                submission['payment_processed_date'] = datetime.now().strftime('%d/%m/%Y %H:%M')
                                save_fnf_data()
                                st.success("✅ Payment processed!")
                                st.rerun()
                        elif submission['status'] == 'Tax Rejected':
                            if st.button(f"📝 Edit & Resubmit", key=f"edit_{submission['employee_id']}"):
                                st.info("Go to F&F Settlement tab to edit and resend to Tax Team")

                    # Show tax comments (read-only in payroll)
                    if submission.get('tax_comments'):
                        st.markdown(f"""
                        <div class="info-card">
                            <h4>💬 Tax Team Comments</h4>
                            <p>{submission['tax_comments']}</p>
                        </div>
                        """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="info-card">
                📋 No F&F settlements submitted yet
            </div>
            """, unsafe_allow_html=True)

    # --- Tab 4: Analytics & Reports ---
    with tab4:
        st.markdown("""
        <div class="employee-card">
            <h3>📈 Analytics & Reports</h3>
            <p>Visual analytics and insights for F&F settlements</p>
        </div>
        """, unsafe_allow_html=True)

        create_analytics_charts()

        employee_df = load_employee_data()
        if not employee_df.empty:
            st.markdown("### 📊 Employee Statistics")
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                create_enhanced_metric_card("Total Employees", len(employee_df), icon="👥")
            with c2:
                avg_salary = employee_df['Salary'].mean() if 'Salary' in employee_df.columns else 0
                create_enhanced_metric_card("Average Salary", f"₹{avg_salary:,.0f}", icon="💰")
            with c3:
                if 'fnf_submissions' in st.session_state:
                    pending_fnf = len([s for s in st.session_state.fnf_submissions
                                       if s['status'] != 'Payment Processed'])
                    create_enhanced_metric_card("Pending F&F", pending_fnf, icon="📋")
                else:
                    create_enhanced_metric_card("Pending F&F", 0, icon="📋")
            with c4:
                locations = employee_df['BaseLocation'].nunique() if 'BaseLocation' in employee_df.columns else 0
                create_enhanced_metric_card("Locations", locations, icon="🌍")

    # --- Tab 5: Quick Actions ---
    with tab5:
        st.markdown("""
        <div class="employee-card">
            <h3>🎯 Quick Actions</h3>
            <p>Frequently used actions and shortcuts</p>
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)

        with c1:
            st.markdown("""
            <div class="metric-card">
                <h4>📊 Bulk Operations</h4>
            </div>
            """, unsafe_allow_html=True)
            if st.button("📤 Export All F&F Data", use_container_width=True):
                st.info("📊 F&F data export functionality ready for implementation")
            if st.button("📥 Import Employee Data", use_container_width=True):
                st.info("📥 Employee data import functionality ready for implementation")

        with c2:
            st.markdown("""
            <div class="metric-card">
                <h4>🔄 System Actions</h4>
            </div>
            """, unsafe_allow_html=True)
            if st.button("🔄 Refresh Data", use_container_width=True):
                st.cache_data.clear()
                st.success("✅ Data refreshed successfully!")
                st.rerun()
            if st.button("📊 Generate Report", use_container_width=True):
                st.info("📊 Report generation functionality ready")

        with c3:
            st.markdown("""
            <div class="metric-card">
                <h4>⚙️ Settings</h4>
            </div>
            """, unsafe_allow_html=True)
            if st.button("⚙️ System Settings", use_container_width=True):
                st.info("⚙️ System settings panel ready for configuration")
            if st.button("📋 View Logs", use_container_width=True):
                st.info("📋 System logs viewer ready for implementation")
                
def login():
    """Enhanced login page with professional styling for real users"""
    
    # Load custom CSS for login page
    st.markdown("""
        <style>
        .login-container {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 3rem;
            border-radius: 20px;
            color: white;
            text-align: center;
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
            margin: 2rem 0;
        }
        
        .logo-section {
            display: grid;
            place-items: center;
            width: 100%;
            margin-bottom: 2rem;
        }
        
        .main-title {
            color: #1f4e79;
            font-size: 2.2rem;
            font-weight: 600;
            margin: 0;
            text-align: center;
        }
        
        .production-tag {
            background: #28a745;
            color: white;
            padding: 8px 20px;
            border-radius: 25px;
            font-size: 0.9rem;
            font-weight: 500;
            text-align: center;
            margin: 1rem 0;
        }
        
        .feature-highlight {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            padding: 1rem;
            margin: 0.5rem 0;
            backdrop-filter: blur(10px);
            text-align: left;
        }
        
        .perfect-center {
            display: grid;
            place-items: center;
            width: 100%;
            gap: 20px;
            text-align: center;
        }
        </style>
    """, unsafe_allow_html=True)

    users = load_users()

    # 🔹 CHECK: If user needs to set password for the first time (NO current password required)
    if st.session_state.get("needs_password_setup"):
        username = st.session_state.get("username")
        
        st.markdown('<div class="perfect-center">', unsafe_allow_html=True)
        
        # Logo section
        st.markdown('<div class="logo-section">', unsafe_allow_html=True)
        try:
            _, center_col, _ = st.columns([2, 1, 2])
            with center_col:
                st.image('koenig-logo.png', width=200)
        except Exception:
            st.markdown("""
                <div style="text-align: center;">
                    <h1 style="color: #667eea; font-size: 3rem;">🏢</h1>
                    <h2 style="color: #667eea; margin: 0;">Koenig Solutions</h2>
                </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown(f"""
            <div class="login-container">
                <h1 class="main-title" style="color: white;">Welcome, {username}!</h1>
                <div class="production-tag">First Time Setup - Create Your Password</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="employee-card">
                <h3>🔐 Create Your Password</h3>
                <p>Please create a secure password for your account.</p>
            </div>
            """, unsafe_allow_html=True)
            
            # 🔥 DIRECT PASSWORD SETUP FORM (No function call that might have bugs)
            with st.form("first_time_password_setup", clear_on_submit=False):
                st.markdown("### ✅ **Set Up Your Password**")
                
                new_password = st.text_input(
                    "Create Password",
                    type="password",
                    help="Use 8+ chars with upper, lower, digit & special character.",
                    key="new_password_setup"
                )
                
                confirm_password = st.text_input(
                    "Confirm Password",
                    type="password",
                    key="confirm_password_setup"
                )
                
                setup_submit = st.form_submit_button("✅ Create Password", use_container_width=True)
                
                if setup_submit:
                    # Validate password
                    if not new_password:
                        st.error("Please enter a password.")
                    elif len(new_password) < 8:
                        st.error("Password must be at least 8 characters long.")
                    elif not any(c.islower() for c in new_password):
                        st.error("Password must contain at least one lowercase letter.")
                    elif not any(c.isupper() for c in new_password):
                        st.error("Password must contain at least one uppercase letter.")
                    elif not any(c.isdigit() for c in new_password):
                        st.error("Password must contain at least one digit.")
                    elif not any(not c.isalnum() for c in new_password):
                        st.error("Password must contain at least one special character.")
                    elif new_password != confirm_password:
                        st.error("Passwords do not match.")
                    else:
                        # Set password
                        if set_password(username, new_password):
                            # Clear setup flags
                            st.session_state.pop("needs_password_setup", None)
                            
                            # Set user as logged in
                            user_data = users[username]
                            st.session_state["role"] = user_data["role"]
                            st.session_state["username"] = username
                            
                            # Load F&F data
                            try:
                                load_fnf_data()
                            except Exception:
                                pass
                            
                            st.success(f"🎉 Password created! Welcome to the F&F Settlement System!")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error("Failed to set password. Please try again.")
        
        st.markdown('</div>', unsafe_allow_html=True)
        return

    # 🔹 CHECK: If user needs to change existing password (current password required)
    if st.session_state.get("must_change_password") and st.session_state.get("username"):
        st.markdown('<div class="perfect-center">', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
            <div class="warning-card">
                🔄 <strong>Password Change Required</strong><br>
                Your password must be updated before continuing.
            </div>
            """, unsafe_allow_html=True)
            
            # Call function with current password required
            change_password_ui(location="main", require_current=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        return

    # 🔹 REGULAR LOGIN FORM
    st.markdown('<div class="perfect-center">', unsafe_allow_html=True)

    # Logo Section
    st.markdown('<div class="logo-section">', unsafe_allow_html=True)
    try:
        _, center_col, _ = st.columns([2, 1, 2])
        with center_col:
            st.image('koenig-logo.png', width=200)
    except Exception:
        st.markdown("""
            <div style="text-align: center;">
                <h1 style="color: #667eea; font-size: 3rem;">🏢</h1>
                <h2 style="color: #667eea; margin: 0;">Koenig Solutions</h2>
            </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Header
    st.markdown("""
        <div class="login-container">
            <h1 class="main-title" style="color: white;">F&F Settlement System - Production</h1>
            <div class="production-tag">Real User Authentication System</div>
        </div>
    """, unsafe_allow_html=True)

    # Main login content
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div class="employee-card">
            <h2 style="text-align: center;">🔐 System Login</h2>
        </div>
        """, unsafe_allow_html=True)

        # System capabilities
        st.markdown("### ✨ Production System Features")
        features = [
            "Real user authentication with secure password hashing",
            "First-time login password setup for new users", 
            "Multi-month salary processing with prorated calculations",
            "Automatic salary breakdown (Basic/HRA/Special Allowances)", 
            "Investment deductions for Old Tax Regime",
            "EPF calculation with Employee Master policy",
            "Auto-gratuity calculation using (n × b × 15) ÷ 26 formula",
            "Dual tax regime support (Old/New)",
            "Comprehensive tax calculations with TDS",
            "Role-based dashboards (Payroll + Tax Team)",
            "Real-time data persistence between user sessions",
            "Professional UI with enhanced analytics"
        ]
        
        for feature in features:
            st.markdown(f"""
            <div class="feature-highlight">
                ✅ {feature}
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### 🔑 Access System")

        # Login form
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input(
                "👤 Username", 
                placeholder="Enter your username", 
                key="auth_username"
            )
            password = st.text_input(
                "🔒 Password", 
                type="password", 
                placeholder="Enter your password (leave blank for first-time setup)", 
                key="auth_password"
            )
            submit_login = st.form_submit_button(
                "🚀 Login to System", 
                use_container_width=True
            )

        if submit_login:
            if not username:
                st.error("Please enter your username.")
                return
                
            # Check if user exists
            if username not in users:
                st.error("❌ User not found. Please contact administrator.")
                return
            
            user_data = users[username]
            
            # 🔥 FIRST TIME USER (no password set)
            if not user_data.get("password_hash"):
                st.session_state["username"] = username
                st.session_state["needs_password_setup"] = True  # Use different flag
                st.success("👋 Welcome! Please create your password.")
                st.rerun()
                return
            
            # 🔥 EXISTING USER - need password
            if not password:
                st.error("❌ Please enter your password.")
                return
            
            # Verify password
            if verify_user(username, password):
                st.session_state["role"] = user_data["role"]
                st.session_state["username"] = username
                st.session_state["must_change_password"] = bool(user_data.get("must_change_password", False))
                
                # Clear any setup flags
                st.session_state.pop("needs_password_setup", None)
                
                try:
                    load_fnf_data()
                except Exception:
                    pass
                
                if st.session_state["must_change_password"]:
                    st.warning("⚠️ You must change your password before continuing.")
                    st.rerun()
                else:
                    st.success(f"✅ Login successful! Welcome, {user_data['role']}")
                    st.balloons()
                    st.rerun()
            else:
                st.error("❌ Invalid password. Please try again.")

        # User info
        st.markdown("---")
        st.markdown("### 👥 **For New Users**")
        st.markdown("""
        <div class="info-card">
            🔐 <strong>New User?</strong><br>
            Enter your username and leave password blank for first-time setup.
        </div>
        """, unsafe_allow_html=True)

        # Current users
        with st.expander("👥 **Authorized Users**", expanded=False):
            st.markdown("### Current System Users:")
            for user, role in REAL_USERS.items():
                st.markdown(f"• **{user}** - {role}")
        
        # Footer
        st.markdown("---")
        st.markdown("""
            <div style='text-align: center; color: #666; font-size: 0.9em; padding: 20px;'>
                © 2024 Koenig Solutions - F&F Settlement System (Production)<br>
                <em>Secure Real User Authentication System</em>
            </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

def main():
    st.set_page_config(
        page_title="F&F Settlement System - Production",
        page_icon="💼",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    if 'fnf_submissions' not in st.session_state:
        st.session_state.fnf_submissions = []
    
    # Load F&F data on startup
    if 'fnf_submissions' not in st.session_state or not st.session_state.fnf_submissions:
        load_fnf_data()
    
    # Add sidebar logo for all authenticated pages
    if 'role' in st.session_state:
        add_sidebar_logo()
    
    if 'role' not in st.session_state:
        login()
    elif st.session_state['role'] == 'Payroll Team':
        payroll_dashboard()
    elif st.session_state['role'] == 'Tax Team':
        tax_review_dashboard_updated()  # ← Make sure this matches your function name
    else:
        st.error("Unknown role")

if __name__ == "__main__":
    main()
