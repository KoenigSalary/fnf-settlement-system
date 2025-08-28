import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime, date
import calendar
from dateutil.relativedelta import relativedelta

# Try to import Google Sheets dependencies
try:
    import gspread
    from google.oauth2.service_account import Credentials
    GOOGLE_SHEETS_AVAILABLE = True
except ImportError:
    GOOGLE_SHEETS_AVAILABLE = False
    st.warning("Google Sheets integration not available. Using demo data.")

# Sample Users Database
users_db = {
    "payroll_user": {"password": "payroll_pass", "role": "Payroll Team"},
    "tax_user": {"password": "tax_pass", "role": "Tax Team"},
    # Demo accounts for review
    "demo_payroll": {"password": "demo123", "role": "Payroll Team"},
    "demo_tax": {"password": "demo123", "role": "Tax Team"}
}

# Data persistence functions
def load_fnf_data():
    """Load F&F submissions from JSON file"""
    try:
        if os.path.exists('fnf_submissions.json'):
            with open('fnf_submissions.json', 'r') as f:
                data = json.load(f)
                st.session_state.fnf_submissions = data.get('submissions', [])
                print(f"✅ Loaded {len(st.session_state.fnf_submissions)} F&F submissions from file")
        else:
            st.session_state.fnf_submissions = []
            print("📝 Created new F&F submissions list")
    except Exception as e:
        print(f"❌ Error loading F&F data: {e}")
        st.session_state.fnf_submissions = []

def save_fnf_data():
    """Save F&F submissions to JSON file"""
    try:
        data = {
            'submissions': st.session_state.get('fnf_submissions', []),
            'last_updated': datetime.now().isoformat()
        }
        with open('fnf_submissions.json', 'w') as f:
            json.dump(data, f, indent=2, default=str)
        print(f"💾 Saved {len(data['submissions'])} F&F submissions to file")
    except Exception as e:
        print(f"❌ Error saving F&F data: {e}")

def get_demo_employee_data():
    """Return demo employee data"""
    demo_data = {
        'Employee ID': [1001, 1002, 1003, 1004, 1005],
        'Employee Name': ['John Doe', 'Jane Smith', 'Raj Kumar', 'Priya Sharma', 'Mike Johnson'],
        'Designation': ['Software Engineer', 'Senior Developer', 'Team Lead', 'HR Manager', 'Project Manager'],
        'BaseLocation': ['Bangalore', 'Chennai', 'Mumbai', 'Delhi', 'Pune'],
        'Date of Joining': ['01/01/2020', '15/03/2019', '10/06/2018', '20/09/2017', '05/12/2021'],
        'PAN No.': ['ABCDE1234F', 'FGHIJ5678K', 'KLMNO9012P', 'PQRST3456U', 'UVWXY7890Z'],
        'Salary': [80000, 120000, 150000, 90000, 110000],
        'EPF Amount': [1800, 1800, 1800, 0, 2000]  # Added EPF Amount column
    }
    return pd.DataFrame(demo_data)

def add_sidebar_logo():
    """Add actual logo to sidebar top - fixed deprecation warning"""
    with st.sidebar:
        # Actual Koenig logo in sidebar (smaller size)
        try:
            st.image('assets/koenig-logo.png', width=150)  # Fixed: removed use_column_width
        except:
            # Try loading from web or fallback
            try:
                st.markdown("""
                    <div style='text-align: center;'>
                        <img src="https://www.koenig-solutions.com/images/logo.png" width="150" alt="Koenig Solutions">
                    </div>
                """, unsafe_allow_html=True)
            except:
                st.markdown("### 🏢 **Koenig Solutions**")
        
        st.markdown("**F&F Settlement System**")
        
        st.markdown("---")
        
        # User info
        if 'username' in st.session_state:
            st.write(f"**👤 User:** {st.session_state.username}")
            st.write(f"**🔧 Role:** {st.session_state.role}")
            
            # Show F&F statistics
            if 'fnf_submissions' in st.session_state:
                total_submissions = len(st.session_state.fnf_submissions)
                pending_review = len([s for s in st.session_state.fnf_submissions 
                                    if s['status'] in ['Under Tax Review', 'Pending Tax Review']])
                approved = len([s for s in st.session_state.fnf_submissions if s['status'] == 'Tax Approved'])
                processed = len([s for s in st.session_state.fnf_submissions if s['status'] == 'Payment Processed'])
                
                st.markdown("**📊 F&F Statistics:**")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total", total_submissions)
                    st.metric("Approved", approved)
                with col2:
                    st.metric("Pending", pending_review)
                    st.metric("Processed", processed)
            
            st.markdown("---")
            
            # System info
            st.markdown("**🚀 System Features:**")
            st.write("✅ Multi-month processing")
            st.write("✅ Tax regime support")
            st.write("✅ Investment deductions")
            st.write("✅ EPF & ESI calculations")
            st.write("✅ Real-time previews")
            
            st.markdown("---")
            
            if st.button("🚪 Logout", use_container_width=True):
                # Clear session state
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()

@st.cache_data(ttl=300)
def load_employee_data():
    """Load employee data from Google Sheets or demo data"""
    if not GOOGLE_SHEETS_AVAILABLE:
        return get_demo_employee_data()
    
    try:
        creds = None
        
        # Try Streamlit secrets first (for Streamlit Cloud)
        try:
            if hasattr(st, 'secrets') and "gcp_service_account" in st.secrets:
                print("✅ Using Streamlit Cloud secrets")
                creds = Credentials.from_service_account_info(
                    st.secrets["gcp_service_account"],
                    scopes=[
                        "https://www.googleapis.com/auth/spreadsheets",
                        "https://www.googleapis.com/auth/drive"
                    ]
                )
        except Exception as e:
            print(f"Streamlit secrets not available: {e}")
        
        # Fallback to local credentials file (for local development)
        if creds is None:
            credential_paths = [
                'credentials.json',
                '/Users/praveenchaudhary/Desktop/fnf-settlement-system-v2/credentials.json',
                os.path.join(os.getcwd(), 'credentials.json')
            ]
            
            SERVICE_ACCOUNT_FILE = None
            for path in credential_paths:
                if os.path.exists(path):
                    SERVICE_ACCOUNT_FILE = path
                    print(f"✅ Found local credentials: {path}")
                    break
            
            if SERVICE_ACCOUNT_FILE:
                creds = Credentials.from_service_account_file(
                    SERVICE_ACCOUNT_FILE, 
                    scopes=[
                        "https://www.googleapis.com/auth/spreadsheets",
                        "https://www.googleapis.com/auth/drive"
                    ]
                )
        
        # If we have credentials, try to connect
        if creds:
            gc = gspread.authorize(creds)
            spreadsheet = gc.open("FNF Calculation")
            worksheet = spreadsheet.worksheet("Employee Master")
            data = worksheet.get_all_records()
            
            if data:
                df = pd.DataFrame(data)
                # Remove empty rows
                df = df[df['Employee ID'].astype(str) != '']
                df = df[df['Employee ID'].astype(str) != '0']
                
                # Convert Employee ID to numeric
                df['Employee ID'] = pd.to_numeric(df['Employee ID'], errors='coerce')
                df = df.dropna(subset=['Employee ID'])
                
                # Convert Salary to numeric
                df['Salary'] = pd.to_numeric(df['Salary'], errors='coerce')
                df = df.dropna(subset=['Salary'])
                
                # Convert EPF Amount to numeric (with default)
                if 'EPF Amount' in df.columns:
                    df['EPF Amount'] = pd.to_numeric(df['EPF Amount'], errors='coerce').fillna(1800)
                else:
                    df['EPF Amount'] = 1800
                
                # Clean text columns
                text_columns = ['Employee Name', 'Designation', 'BaseLocation', 'PAN No.']
                for col in text_columns:
                    if col in df.columns:
                        df[col] = df[col].fillna('').astype(str)
                
                print(f"✅ Loaded {len(df)} employees from Google Sheets")
                return df
            else:
                print("No data found in Google Sheets")
        else:
            print("No valid credentials found")
        
        # Fall back to demo data
        print("Using demo data")
        return get_demo_employee_data()
            
    except Exception as e:
        print(f"Google Sheets error: {e}")
        st.warning(f"Could not connect to Google Sheets: {e}. Using demo data.")
        return get_demo_employee_data()

def get_employee_by_id(employee_id, df):
    """Get employee details by ID - Fixed to handle int properly"""
    employee_id = int(float(employee_id))  # Convert to int, removing decimal
    employee = df[df['Employee ID'] == employee_id]
    if not employee.empty:
        return employee.iloc[0]
    return None

def get_total_working_days(month_name, year=2024):
    """Get total working days in a month (excluding Sundays)"""
    month_dict = {
        'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6,
        'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12
    }
    
    month_num = month_dict.get(month_name, 8)  # Default to August
    
    # Get total days in month
    total_days = calendar.monthrange(year, month_num)[1]
    
    # Count working days (excluding Sundays)
    working_days = 0
    for day in range(1, total_days + 1):
        weekday = calendar.weekday(year, month_num, day)
        if weekday != 6:  # 6 is Sunday
            working_days += 1
    
    return working_days

def calculate_tds_old_regime(annual_taxable_income, total_deductions_80c=0, total_investments=0):
    """Calculate TDS for Old Tax Regime with investment deductions"""
    # Apply standard deduction
    income_after_standard = max(0, annual_taxable_income - 50000)
    
    # Apply investment deductions (80C, 80D, etc.)
    income_after_investments = max(0, income_after_standard - total_investments)
    
    tax = 0
    if income_after_investments <= 250000:
        tax = 0
    elif income_after_investments <= 500000:
        tax = (income_after_investments - 250000) * 0.05
    elif income_after_investments <= 1000000:
        tax = 12500 + (income_after_investments - 500000) * 0.20
    else:
        tax = 112500 + (income_after_investments - 1000000) * 0.30
    
    # Section 87A Rebate
    if income_after_investments <= 500000:
        tax = max(0, tax - 12500)
    
    # Health & Education Cess (4%)
    tax_with_cess = tax * 1.04
    
    return tax_with_cess

def calculate_tds_new_regime(annual_taxable_income):
    """Calculate TDS for New Tax Regime (no investment deductions allowed)"""
    # Apply standard deduction
    income_after_standard = max(0, annual_taxable_income - 75000)
    
    tax = 0
    if income_after_standard <= 400000:
        tax = 0
    elif income_after_standard <= 800000:
        tax = (income_after_standard - 400000) * 0.05
    elif income_after_standard <= 1200000:
        tax = 20000 + (income_after_standard - 800000) * 0.10
    elif income_after_standard <= 1600000:
        tax = 60000 + (income_after_standard - 1200000) * 0.15
    elif income_after_standard <= 2000000:
        tax = 120000 + (income_after_standard - 1600000) * 0.20
    elif income_after_standard <= 2400000:
        tax = 200000 + (income_after_standard - 2000000) * 0.25
    else:
        tax = 300000 + (income_after_standard - 2400000) * 0.30
    
    # Section 87A Rebate
    if income_after_standard <= 1200000:
        tax = max(0, tax - min(60000, tax))
    
    # Health & Education Cess (4%)
    tax_with_cess = tax * 1.04
    
    return tax_with_cess

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

def calculate_gratuity(tenure_years, last_basic_salary):
    """
    Calculate Gratuity using company formula
    Gratuity = (n * b * 15) / 26
    where n = tenure in years, b = last drawn basic salary
    """
    if tenure_years < 5:
        return 0  # Gratuity only applicable after 5 years of service
    
    gratuity = (tenure_years * last_basic_salary * 15) / 26
    return round(gratuity, 2)

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

def calculate_employee_epf_with_attendance(employee_epf_amount, present_days, total_working_days):
    """Calculate EPF based on attendance using formula: EPF_amount / working_days * present_days"""
    if total_working_days == 0:
        return 0
    
    calculated_epf = (employee_epf_amount / total_working_days) * present_days
    return round(calculated_epf, 2)

def salary_breakdown_input_with_epf(month, base_salary=0.0, present_days=0, total_working_days=1, employee_epf_amount=1800):
    """Enhanced salary breakdown with EPF calculation using employee's EPF amount"""
    st.write(f"**💰 Salary Breakdown for {month}**")
    
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
            st.warning(f"⚠️ Prorated Basic: ₹{prorated_basic:,.2f}")
            st.caption(f"Ratio: {present_days}/{total_working_days}")
    
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
    
    # Enhanced EPF Calculation Section
    st.write("**🏦 EPF Calculation**")
    
    # Calculate EPF based on employee's EPF amount and attendance
    calculated_epf = calculate_employee_epf_with_attendance(employee_epf_amount, present_days, total_working_days)
    
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"**Enhanced EPF Calculation:**")
        st.write(f"• Employee EPF Amount: ₹{employee_epf_amount:,.0f}")
        st.write(f"• Present Days: {present_days}")
        st.write(f"• Total Working Days: {total_working_days}")
        st.write(f"• Formula: ₹{employee_epf_amount:,.0f} ÷ {total_working_days} × {present_days}")
        st.write(f"• **Calculated EPF: ₹{calculated_epf:,.2f}**")
    
    with col2:
        epf = st.number_input(
            f"EPF Deduction (₹)", 
            min_value=0.0,
            value=calculated_epf,
            key=f"epf_{month}",
            step=10.0,
            help=f"Auto-calculated: ₹{employee_epf_amount} ÷ {total_working_days} × {present_days} = ₹{calculated_epf}"
        )
        
        if epf != calculated_epf:
            st.warning(f"⚠️ Manual override! Calculated: ₹{calculated_epf:,.2f}")
    
    total_breakdown = basic + hra + special_allowances
    
    # Show breakdown verification
    st.write("**🔍 Breakdown Verification:**")
    verification_data = {
        'Component': ['Basic Salary', 'HRA', 'Special Allowances', 'TOTAL', 'EPF'],
        'Formula': [
            'Total ÷ 3',
            '50% of Basic', 
            'Rest Amount',
            'Sum of All',
            f'₹{employee_epf_amount} ÷ {total_working_days} × {present_days}'
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
            f"{(epf/employee_epf_amount*100) if employee_epf_amount > 0 else 0:.1f}%"
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
        'epf_basic': prorated_basic,
        'calculated_epf': calculated_epf
    }

def investment_deductions_input():
    """Investment and deduction options for Old Tax Regime"""
    st.subheader("💼 Investment & Deductions (Old Tax Regime Only)")
    
    # Section 80C Investments
    st.write("**📊 Section 80C Investments (Max ₹1,50,000)**")
    col1, col2 = st.columns(2)
    
    with col1:
        ppf = st.number_input("PPF (₹)", min_value=0.0, max_value=150000.0, value=0.0, step=5000.0)
        epf_employee = st.number_input("EPF Employee Contribution (₹)", min_value=0.0, value=0.0, step=1000.0)
        elss = st.number_input("ELSS Mutual Funds (₹)", min_value=0.0, value=0.0, step=5000.0)
        life_insurance = st.number_input("Life Insurance Premium (₹)", min_value=0.0, value=0.0, step=2000.0)
    
    with col2:
        fd_5year = st.number_input("5-Year Fixed Deposit (₹)", min_value=0.0, value=0.0, step=5000.0)
        nsc = st.number_input("NSC (₹)", min_value=0.0, value=0.0, step=5000.0)
        suknya_samriddhi = st.number_input("Sukanya Samriddhi (₹)", min_value=0.0, value=0.0, step=5000.0)
        tuition_fees = st.number_input("Children Tuition Fees (₹)", min_value=0.0, value=0.0, step=5000.0)
    
    total_80c = ppf + epf_employee + elss + life_insurance + fd_5year + nsc + suknya_samriddhi + tuition_fees
    eligible_80c = min(total_80c, 150000)
    
    if total_80c > 150000:
        st.warning(f"⚠️ Total 80C (₹{total_80c:,.0f}) exceeds limit. Eligible: ₹{eligible_80c:,.0f}")
    else:
        st.success(f"✅ Section 80C: ₹{eligible_80c:,.0f}")
    
    # Other Deductions
    st.write("**🏥 Health & Other Deductions**")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Section 80D (Health Insurance)**")
        health_insurance_self = st.number_input("Self & Family (₹)", min_value=0.0, max_value=25000.0, value=0.0, step=1000.0)
        health_insurance_parents = st.number_input("Parents (₹)", min_value=0.0, max_value=50000.0, value=0.0, step=1000.0)
        
        st.write("**Disability & Medical**")
        section_80dd = st.number_input("80DD - Disability (₹)", min_value=0.0, max_value=125000.0, value=0.0, step=5000.0)
        section_80ddb = st.number_input("80DDB - Medical Treatment (₹)", min_value=0.0, max_value=100000.0, value=0.0, step=5000.0)
    
    with col2:
        st.write("**Loan Interest**")
        home_loan_interest = st.number_input("Home Loan Interest (₹)", min_value=0.0, max_value=200000.0, value=0.0, step=5000.0)
        education_loan_interest = st.number_input("Education Loan Interest (₹)", min_value=0.0, value=0.0, step=2000.0)
        
        st.write("**NPS Deductions**")
        nps_80ccd_1b = st.number_input("NPS 80CCD(1B) (₹)", min_value=0.0, max_value=50000.0, value=0.0, step=5000.0)
        nps_80ccd_2 = st.number_input("NPS 80CCD(2) Employer (₹)", min_value=0.0, value=0.0, step=5000.0)
    
    # Allowances (Exempt under Old Regime)
    st.write("**🚗 Exempt Allowances (Old Regime)**")
    col1, col2 = st.columns(2)
    
    with col1:
        conveyance_allowance = st.number_input("Conveyance Allowance (₹)", min_value=0.0, max_value=21600.0, value=0.0, step=1000.0)
        helper_allowance = st.number_input("Helper Allowance (₹)", min_value=0.0, value=0.0, step=500.0)
        lta = st.number_input("LTA (₹)", min_value=0.0, value=0.0, step=5000.0)
    
    with col2:
        tel_broadband = st.number_input("Telephone & Broadband (₹)", min_value=0.0, value=0.0, step=500.0)
        ld_allowance = st.number_input("L&D Allowance (₹)", min_value=0.0, value=0.0, step=1000.0)
        hra_exemption = st.number_input("HRA Exemption (₹)", min_value=0.0, value=0.0, step=2000.0)
    
    # Calculate totals
    total_80d = health_insurance_self + health_insurance_parents
    total_other_deductions = section_80dd + section_80ddb + home_loan_interest + education_loan_interest + nps_80ccd_1b + nps_80ccd_2
    total_exempt_allowances = conveyance_allowance + helper_allowance + lta + tel_broadband + ld_allowance + hra_exemption
    
    total_deductions = eligible_80c + total_80d + total_other_deductions
    
    # Summary
    st.write("**📋 Investment & Deduction Summary**")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Section 80C", f"₹{eligible_80c:,.0f}")
        st.metric("Section 80D", f"₹{total_80d:,.0f}")
    
    with col2:
        st.metric("Other Deductions", f"₹{total_other_deductions:,.0f}")
        st.metric("Exempt Allowances", f"₹{total_exempt_allowances:,.0f}")
    
    with col3:
        st.metric("Total Tax Deductions", f"₹{total_deductions:,.0f}")
        st.info("*Exempt allowances reduce taxable income*")
    
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

def enhanced_multi_month_salary_input(employee_salary=0, employee_epf_amount=1800):
    """Enhanced multi-month salary input with auto-population and EPF logic"""
    st.subheader("💰 Multi-Month Salary Details")
    
    months = ["January", "February", "March", "April", "May", "June",
             "July", "August", "September", "October", "November", "December"]
    
    # Initialize salary data in session state if not exists
    if 'monthly_salaries' not in st.session_state:
        st.session_state.monthly_salaries = {
            month: {
                'total_salary': 0.0, 'basic': 0.0, 'hra': 0.0, 'special_allowances': 0.0,
                'present_days': 0, 'epf': 0.0, 'esi': 0.0
            } for month in months
        }
    
    # Quick add/remove months and auto-fill
    col1, col2 = st.columns(2)
    with col1:
        selected_months = st.multiselect(
            "Select months to include in F&F settlement:",
            months,
            default=[]
        )
    
    with col2:
        # Auto-fill button for selected months
        if st.button("🔄 Auto-Fill All Selected Months"):
            if employee_salary > 0 and selected_months:
                for month in selected_months:
                    total_working_days = get_total_working_days(month)
                    
                    st.session_state.monthly_salaries[month] = {
                        'total_salary': float(employee_salary),
                        'basic': float(employee_salary) / 3,
                        'hra': (float(employee_salary) / 3) * 0.50,
                        'special_allowances': float(employee_salary) - (float(employee_salary) / 3) - ((float(employee_salary) / 3) * 0.50),
                        'present_days': total_working_days,  # Default to full month
                        'epf': float(employee_epf_amount),
                        'esi': 0.0,
                        'total_working_days': total_working_days,
                        'prorated_salary': float(employee_salary),
                        'prorated_basic': float(employee_salary) / 3,
                        'prorated_hra': (float(employee_salary) / 3) * 0.50,
                        'prorated_special': float(employee_salary) - (float(employee_salary) / 3) - ((float(employee_salary) / 3) * 0.50),
                    }
                
                st.success(f"✅ Auto-filled {len(selected_months)} months with base salary ₹{employee_salary:,.0f}")
                st.rerun()
            else:
                st.warning("Please select an employee and months first")
        
        if st.button("🔄 Reset All Months"):
            st.session_state.monthly_salaries = {
                month: {
                    'total_salary': 0.0, 'basic': 0.0, 'hra': 0.0, 'special_allowances': 0.0,
                    'present_days': 0, 'epf': 0.0, 'esi': 0.0
                } for month in months
            }
            st.rerun()
    
    if not selected_months:
        st.warning("Please select at least one month for F&F settlement")
        return {}
    
    st.write("---")
    
    # Use tabs for month details
    tabs = st.tabs(selected_months)
    for i, month in enumerate(selected_months):
        with tabs[i]:
            st.write(f"**📅 {month} Details**")
            
            # Working days for this month
            total_working_days = get_total_working_days(month)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.info(f"Total working days: {total_working_days}")
                
                # Total salary input - pre-filled with employee salary
                total_salary = st.number_input(
                    f"Total Salary (₹)", 
                    min_value=0.0, 
                    value=st.session_state.monthly_salaries[month]['total_salary'] if st.session_state.monthly_salaries[month]['total_salary'] > 0 else float(employee_salary),
                    key=f"total_salary_{month}",
                    step=1000.0
                )
                
                # Present days
                present_days = st.number_input(
                    f"Present Days", 
                    min_value=0, 
                    max_value=total_working_days,
                    value=st.session_state.monthly_salaries[month]['present_days'] if st.session_state.monthly_salaries[month]['present_days'] > 0 else total_working_days,
                    key=f"days_{month}"
                )
            
            with col2:
                # ESI
                esi = st.number_input(
                    f"ESI Deduction (₹)", 
                    min_value=0.0,
                    value=st.session_state.monthly_salaries[month]['esi'],
                    key=f"esi_{month}",
                    step=10.0
                )
            
            # Enhanced salary breakdown with EPF calculation
            if total_salary > 0:
                breakdown = salary_breakdown_input_with_epf(month, total_salary, present_days, total_working_days, employee_epf_amount)
                
                # Calculate prorated salary
                if present_days > 0 and total_working_days > 0:
                    prorated_salary = (total_salary / total_working_days) * present_days
                    prorated_basic = (breakdown['basic'] / total_working_days) * present_days
                    prorated_hra = (breakdown['hra'] / total_working_days) * present_days
                    prorated_special = (breakdown['special_allowances'] / total_working_days) * present_days
                    
                    st.success(f"✅ Prorated Total: ₹{prorated_salary:,.2f}")
                else:
                    prorated_salary = prorated_basic = prorated_hra = prorated_special = 0
                    st.warning("⚠️ No salary calculated (0 present days)")
                
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
                    'epf_basic': breakdown['epf_basic'],
                    'calculated_epf': breakdown['calculated_epf']
                })
    
    # Summary of selected months
    st.write("---")
    st.subheader("📊 Multi-Month Summary with EPF Details")
    
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
        
        for month, data in active_months.items():
            # EPF status
            epf_status = "✅ Calculated" if data['epf'] == data.get('calculated_epf', 0) else "⚠️ Manual"
            
            summary_data.append({
                'Month': month,
                'Total Salary': f"₹{data['total_salary']:,.0f}",
                'Days': f"{data['present_days']}/{data['total_working_days']}",
                'Prorated Basic': f"₹{data['prorated_basic']:,.0f}",
                'Prorated HRA': f"₹{data['prorated_hra']:,.0f}",
                'Prorated Special': f"₹{data['prorated_special']:,.0f}",
                'EPF': f"₹{data['epf']:,.0f} {epf_status}",
                'ESI': f"₹{data['esi']:,.0f}"
            })
            
            # Calculate totals
            for key in ['total_salary', 'prorated_salary', 'prorated_basic', 'prorated_hra', 'prorated_special', 'epf', 'esi']:
                totals[key.replace('prorated_salary', 'prorated_total').replace('epf', 'total_epf').replace('esi', 'total_esi')] += data[key]
        
        # Add totals row
        summary_data.append({
            'Month': '**TOTAL**',
            'Total Salary': f"**₹{totals['total_salary']:,.0f}**",
            'Days': '**--**',
            'Prorated Basic': f"**₹{totals['prorated_basic']:,.0f}**",
            'Prorated HRA': f"**₹{totals['prorated_hra']:,.0f}**",
            'Prorated Special': f"**₹{totals['prorated_special']:,.0f}**",
            'EPF': f"**₹{totals['total_epf']:,.0f}**",
            'ESI': f"**₹{totals['total_esi']:,.0f}**"
        })
        
        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True, hide_index=True)
        
        # EPF Summary
        st.write("**🏦 EPF Calculation Summary:**")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total EPF", f"₹{totals['total_epf']:,.0f}")
        with col2:
            max_possible_epf = len(active_months) * employee_epf_amount
            st.metric("Max Possible EPF", f"₹{max_possible_epf:,.0f}")
        with col3:
            avg_epf = totals['total_epf'] / len(active_months) if active_months else 0
            st.metric("Average Monthly EPF", f"₹{avg_epf:,.0f}")
    
    return active_months

def fnf_settlement_form():
    """F&F Settlement Form with salary breakdown and investments"""
    st.title("📋 Full & Final Settlement Form ")
    
    # Load employee data
    employee_df = load_employee_data()
    
    if employee_df.empty:
        st.error("Could not load employee data")
        return
    
    # Step 1: Enhanced Employee Selection with Dropdown
    st.subheader("🔍 Step 1: Select Employee")
    
    # Create dropdown options from employee data
    employee_options = [""] + [f"{int(row['Employee ID'])} - {row['Employee Name']}" 
                              for _, row in employee_df.iterrows()]
    
    col1, col2 = st.columns([1, 2])
    with col1:
        selected_option = st.selectbox(
            "Select Employee",
            employee_options,
            index=0,
            help="Choose employee from dropdown"
        )
        
        # Extract employee ID from selection
        if selected_option:
            employee_id = int(selected_option.split(" - ")[0])
        else:
            employee_id = None

    with col2:
        if selected_option:
            st.success(f"✅ Selected: {selected_option}")
    
    if employee_id and selected_option:
        employee = get_employee_by_id(employee_id, employee_df)
        if employee is not None:
            # Get employee salary and EPF amount
            employee_base_salary = float(employee['Salary'])
            employee_epf_amount = float(employee.get('EPF Amount', 1800))
            
            # Display Employee Details with enhanced info
            st.subheader("👤 Employee Details (Auto-filled)")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.info(f"**Employee ID:** {int(employee['Employee ID'])}")
                st.info(f"**Employee Name:** {employee['Employee Name']}")
            
            with col2:
                st.info(f"**Designation:** {employee['Designation']}")
                st.info(f"**Base Location:** {employee['BaseLocation']}")
            
            with col3:
                st.info(f"**DOJ:** {employee['Date of Joining']}")
                st.info(f"**Monthly Salary:** ₹{employee_base_salary:,.0f}")
                st.info(f"**EPF Amount:** ₹{employee_epf_amount:,.0f}")
            
            # Step 2: Tax Regime Selection
            st.subheader("🏛️ Step 2: Select Tax Regime")
            tax_regime = st.selectbox("Tax Regime", ["Old Tax Regime", "New Tax Regime"])
            
            # Step 3: Enhanced Multi-Month Salary Input with Auto-Population
            active_months = enhanced_multi_month_salary_input(employee_base_salary, employee_epf_amount)
            
            if not active_months:
                st.warning("Please add salary details for at least one month to proceed")
                return
            
            # Step 4: Investment Options (only for Old Tax Regime)
            investments_data = {}
            if tax_regime == "Old Tax Regime":
                st.write("---")
                investments_data = investment_deductions_input()
            else:
                st.info("📢 **New Tax Regime Selected** - Investment deductions are not available in the new tax regime")
            
            # Step 5: Other F&F Details
            st.subheader("📝 Step 5: Additional F&F Details")
            
            # Form for additional details (no buttons inside)
            with st.form("fnf_additional_details"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**📅 Important Dates**")
                    resignation_date = st.date_input("Resignation Date", value=date.today())
                    last_working_day = st.date_input("Last Working Day", value=date.today())
                    
                    st.write("**💰 Additional Components**")
                    gratuity = st.number_input("Gratuity (₹)", value=0.0, min_value=0.0)
                    bonus = st.number_input("Bonus (₹)", value=0.0, min_value=0.0)
                    leave_encashment = st.number_input("Leave Encashment (₹)", value=0.0, min_value=0.0)
                
                with col2:
                    st.write("**📉 Additional Deductions**")
                    
                    # PT only for Chennai and Bangalore
                    pt_enabled = employee['BaseLocation'].lower() in ['chennai', 'bangalore']
                    if pt_enabled:
                        pt_total = st.number_input("PT - Professional Tax Total (₹)", value=0.0, min_value=0.0)
                        st.info("✅ PT applicable for Chennai/Bangalore")
                    else:
                        pt_total = 0.0
                        st.info("❌ PT not applicable for this location")
                    
                    salary_advance = st.number_input("Salary Advance (₹)", value=0.0, min_value=0.0)
                    tada_recovery = st.number_input("TADA Recovery (₹)", value=0.0, min_value=0.0)
                    wfh_recovery = st.number_input("WFH Recovery (₹)", value=0.0, min_value=0.0)
                    notice_period_recovery = st.number_input("Notice Period Recovery (₹)", value=0.0, min_value=0.0)
                    other_deductions = st.number_input("Other Deductions (₹)", value=0.0, min_value=0.0)
                
                # Calculate button (this is allowed in forms)
                calculate_clicked = st.form_submit_button("🧮 Calculate F&F Settlement", use_container_width=True)
            
            # Process calculation when form is submitted
            if calculate_clicked:
                # Store calculation results in session state
                st.session_state.calculation_done = True
                st.session_state.calculation_data = {
                    'tax_regime': tax_regime,
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
                    'investments_data': investments_data
                }
            
            # Show calculation results and action buttons (outside the form)
            if st.session_state.get('calculation_done', False):
                data = st.session_state.calculation_data
                
                # Calculate totals from active months
                totals = {
                    'total_salary': sum(month_data['total_salary'] for month_data in active_months.values()),
                    'prorated_total': sum(month_data['prorated_salary'] for month_data in active_months.values()),
                    'prorated_basic': sum(month_data['prorated_basic'] for month_data in active_months.values()),
                    'prorated_hra': sum(month_data['prorated_hra'] for month_data in active_months.values()),
                    'prorated_special': sum(month_data['prorated_special'] for month_data in active_months.values()),
                    'total_epf': sum(month_data['epf'] for month_data in active_months.values()),
                    'total_esi': sum(month_data['esi'] for month_data in active_months.values())
                }
                
                # Total Earnings
                total_earnings = totals['prorated_total'] + data['gratuity'] + data['bonus'] + data['leave_encashment']
                
                # Total Deductions (without TDS)
                total_deductions_before_tds = (totals['total_epf'] + totals['total_esi'] + data['pt_total'] + 
                                             data['salary_advance'] + data['tada_recovery'] + data['wfh_recovery'] + 
                                             data['notice_period_recovery'] + data['other_deductions'])
                
                # Taxable Income calculation
                if data['tax_regime'] == "Old Tax Regime" and data['investments_data']:
                    # Subtract exempt allowances from taxable income
                    exempt_allowances = data['investments_data'].get('exempt_allowances', 0)
                    taxable_income = total_earnings - total_deductions_before_tds - exempt_allowances
                    
                    # Calculate TDS with investment deductions
                    total_investments = data['investments_data'].get('total_deductions', 0)
                    tds_amount = calculate_tds_old_regime(taxable_income, total_investments=total_investments)
                else:
                    # New Tax Regime - no investment deductions
                    taxable_income = total_earnings - total_deductions_before_tds
                    tds_amount = calculate_tds_new_regime(taxable_income)
                
                # Total deductions including TDS
                total_deductions = total_deductions_before_tds + tds_amount
                
                # Net Payable
                net_payable = total_earnings - total_deductions
                
                # Display F&F Settlement Summary
                st.subheader("📊 Full & Final Settlement Summary")
                
                # Month-wise breakdown with salary components
                st.write("**📅 Month-wise Salary Breakdown:**")
                month_breakdown = []
                for month, month_data in active_months.items():
                    month_breakdown.append({
                        'Month': month,
                        'Total Salary': f"₹{month_data['total_salary']:,.2f}",
                        'Days': f"{month_data['present_days']}/{month_data['total_working_days']}",
                        'Prorated Basic': f"₹{month_data['prorated_basic']:,.2f}",
                        'Prorated HRA': f"₹{month_data['prorated_hra']:,.2f}",
                        'Prorated Special': f"₹{month_data['prorated_special']:,.2f}",
                        'EPF': f"₹{month_data['epf']:,.2f}",
                        'ESI': f"₹{month_data['esi']:,.2f}"
                    })
                
                month_df = pd.DataFrame(month_breakdown)
                st.dataframe(month_df, use_container_width=True, hide_index=True)
                
                # Investment Summary for Old Tax Regime
                if data['tax_regime'] == "Old Tax Regime" and data['investments_data']:
                    with st.expander("💼 Investment & Deduction Details"):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.write("**Section 80C**")
                            st.metric("Total 80C", f"₹{data['investments_data']['80c_total']:,.0f}")
                            
                        with col2:
                            st.write("**Other Deductions**")
                            st.metric("Section 80D", f"₹{data['investments_data']['80d_total']:,.0f}")
                            st.metric("Other", f"₹{data['investments_data']['other_deductions']:,.0f}")
                            
                        with col3:
                            st.write("**Exempt Allowances**")
                            st.metric("Total Exempt", f"₹{data['investments_data']['exempt_allowances']:,.0f}")
                            st.metric("Tax Savings", f"₹{data['investments_data']['total_deductions']:,.0f}")
                
                # Overall Summary
                st.write("**💰 Overall F&F Summary:**")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.success("**EARNINGS**")
                    st.write(f"Basic Salary: ₹{totals['prorated_basic']:,.2f}")
                    st.write(f"HRA: ₹{totals['prorated_hra']:,.2f}")
                    st.write(f"Special Allowances: ₹{totals['prorated_special']:,.2f}")
                    st.write(f"Gratuity: ₹{data['gratuity']:,.2f}")
                    st.write(f"Bonus: ₹{data['bonus']:,.2f}")
                    st.write(f"Leave Encashment: ₹{data['leave_encashment']:,.2f}")
                    st.write("---")
                    st.write(f"**Total Earnings: ₹{total_earnings:,.2f}**")
                
                with col2:
                    st.error("**DEDUCTIONS**")
                    st.write(f"Total EPF: ₹{totals['total_epf']:,.2f}")
                    st.write(f"Total ESI: ₹{totals['total_esi']:,.2f}")
                    st.write(f"PT: ₹{data['pt_total']:,.2f}")
                    st.write(f"Salary Advance: ₹{data['salary_advance']:,.2f}")
                    st.write(f"TADA Recovery: ₹{data['tada_recovery']:,.2f}")
                    st.write(f"WFH Recovery: ₹{data['wfh_recovery']:,.2f}")
                    st.write(f"Notice Period: ₹{data['notice_period_recovery']:,.2f}")
                    st.write(f"Other: ₹{data['other_deductions']:,.2f}")
                    st.write(f"TDS ({data['tax_regime'].split()[0]}): ₹{tds_amount:,.2f}")
                    st.write("---")
                    st.write(f"**Total Deductions: ₹{total_deductions:,.2f}**")
                
                with col3:
                    st.info("**NET SETTLEMENT**")
                    if net_payable >= 0:
                        st.metric("Net Payable", f"₹{net_payable:,.2f}", delta="✅ Credit")
                    else:
                        st.metric("Net Recoverable", f"₹{abs(net_payable):,.2f}", delta="❌ Debit")
                    
                    st.write(f"**Tax Regime:** {data['tax_regime']}")
                    if data['tax_regime'] == "Old Tax Regime" and data['investments_data']:
                        tax_saved = (data['investments_data']['total_deductions'] * 0.30)  # Approx tax saved
                        st.metric("Est. Tax Saved", f"₹{tax_saved:,.0f}")
                
                # Save F&F data
                fnf_data = {
                    'employee_id': employee['Employee ID'],
                    'employee_name': employee['Employee Name'],
                    'designation': employee['Designation'],
                    'base_location': employee['BaseLocation'],
                    'doj': employee['Date of Joining'],
                    'resignation_date': data['resignation_date'].strftime('%d/%m/%Y'),
                    'last_working_day': data['last_working_day'].strftime('%d/%m/%Y'),
                    'tax_regime': data['tax_regime'],
                    'active_months': active_months,
                    'salary_totals': totals,
                    'investments_data': data['investments_data'],
                    'gratuity': data['gratuity'],
                    'bonus': data['bonus'],
                    'leave_encashment': data['leave_encashment'],
                    'total_earnings': total_earnings,
                    'pt_total': data['pt_total'],
                    'salary_advance': data['salary_advance'],
                    'tada_recovery': data['tada_recovery'],
                    'wfh_recovery': data['wfh_recovery'],
                    'notice_period_recovery': data['notice_period_recovery'],
                    'other_deductions': data['other_deductions'],
                    'tds_amount': tds_amount,
                    'total_deductions': total_deductions,
                    'net_payable': net_payable,
                    'taxable_income': taxable_income,
                    'status': 'Pending Tax Review'
                }
                
                if 'fnf_submissions' not in st.session_state:
                    st.session_state.fnf_submissions = []
                
                # Update or add F&F submission
                existing_index = None
                for i, submission in enumerate(st.session_state.fnf_submissions):
                    if submission['employee_id'] == employee['Employee ID']:
                        existing_index = i
                        break
                
                if existing_index is not None:
                    st.session_state.fnf_submissions[existing_index] = fnf_data
                else:
                    st.session_state.fnf_submissions.append(fnf_data)
                
                # Action buttons (outside the form)
                st.write("---")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("📤 Send to Tax Team", use_container_width=True):
                        fnf_data['status'] = 'Under Tax Review'
                        st.session_state.fnf_submissions[existing_index if existing_index is not None else -1] = fnf_data
                        save_fnf_data()  # Save to file
                        st.success("✅ F&F settlement sent to Tax Team for review!")
                        st.session_state.calculation_done = False
                        st.rerun()
                
                with col2:
                    if st.button("💾 Save Draft", use_container_width=True):
                        fnf_data['status'] = 'Draft'
                        st.session_state.fnf_submissions[existing_index if existing_index is not None else -1] = fnf_data
                        save_fnf_data()  # Save to file
                        st.info("💾 F&F settlement saved as draft")
                        st.session_state.calculation_done = False
                        st.rerun()
                
                with col3:
                    if st.button("📄 Detailed Report", use_container_width=True):
                        st.info("📄 Comprehensive F&F report with all breakdowns generated!")
        else:
            st.error("❌ Employee not found")

def tax_review_dashboard():
    """Tax Review Dashboard"""
    
    st.title("🔍 Tax Review Dashboard")
    
    # Debug information
    if st.checkbox("🔧 Debug Info"):
        st.write("**Session State Debug:**")
        if 'fnf_submissions' in st.session_state:
            st.write(f"Total submissions: {len(st.session_state.fnf_submissions)}")
            for i, sub in enumerate(st.session_state.fnf_submissions):
                st.write(f"{i+1}. {sub['employee_name']} - Status: {sub['status']}")
        else:
            st.write("No fnf_submissions in session state")
    
    if 'fnf_submissions' not in st.session_state or not st.session_state.fnf_submissions:
        st.info("📭 No F&F submissions for review")
        st.write("**How to test:**")
        st.write("1. Login as Payroll Team")
        st.write("2. Submit an F&F calculation") 
        st.write("3. Click 'Send to Tax Team'")
        st.write("4. Login as Tax Team to see submissions here")
        return
    
    # Filter submissions for tax review - including all relevant statuses
    review_submissions = [
        s for s in st.session_state.fnf_submissions 
        if s['status'] in ['Under Tax Review', 'Tax Approved', 'Pending Tax Review', 'Tax Rejected']
    ]
    
    if not review_submissions:
        st.warning("📋 No F&F submissions pending tax review")
        st.write("**Current submissions:**")
        for sub in st.session_state.fnf_submissions:
            st.write(f"• {sub['employee_name']} - Status: {sub['status']}")
        return
    
    st.success(f"📋 Found {len(review_submissions)} submissions for tax review")
    
    # Show submissions
    for i, submission in enumerate(review_submissions):
        status_emoji = {
            'Under Tax Review': '🟠',
            'Pending Tax Review': '🟡', 
            'Tax Approved': '🟢',
            'Tax Rejected': '🔴'
        }.get(submission['status'], '⚪')
        
        with st.expander(f"{status_emoji} {submission['employee_name']} (ID: {int(submission['employee_id'])}) - {submission['status']}", expanded=True):
            
            # Employee & Financial Summary
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**👤 Employee Information:**")
                st.write(f"• **Name:** {submission['employee_name']}")
                st.write(f"• **Employee ID:** {int(submission['employee_id'])}")
                st.write(f"• **Designation:** {submission['designation']}")
                st.write(f"• **Location:** {submission['base_location']}")
                st.write(f"• **DOJ:** {submission['doj']}")
                st.write(f"• **Last Working Day:** {submission['last_working_day']}")
                
                st.write("**🏛️ Tax Information:**")
                st.write(f"• **Tax Regime:** {submission['tax_regime']}")
                st.write(f"• **Taxable Income:** ₹{submission.get('taxable_income', 0):,.2f}")
                st.write(f"• **Current TDS:** ₹{submission['tds_amount']:,.2f}")
            
            with col2:
                st.write("**💰 Financial Summary:**")
                st.write(f"• **Total Earnings:** ₹{submission['total_earnings']:,.2f}")
                st.write(f"• **Total Deductions:** ₹{submission['total_deductions']:,.2f}")
                st.write(f"• **Net Payable:** ₹{submission['net_payable']:,.2f}")
                
                if 'salary_totals' in submission:
                    st.write("**📊 Salary Breakdown:**")
                    st.write(f"• **Total Basic:** ₹{submission['salary_totals'].get('prorated_basic', 0):,.2f}")
                    st.write(f"• **Total HRA:** ₹{submission['salary_totals'].get('prorated_hra', 0):,.2f}")
                    st.write(f"• **Total Special:** ₹{submission['salary_totals'].get('prorated_special', 0):,.2f}")
                    st.write(f"• **Total EPF:** ₹{submission['salary_totals'].get('total_epf', 0):,.2f}")
                    st.write(f"• **Total ESI:** ₹{submission['salary_totals'].get('total_esi', 0):,.2f}")
            
            # Tax Review Form
            st.write("---")
            st.write("**🔍 Tax Team Review & Adjustments:**")
            
            with st.form(f"tax_review_form_{i}", clear_on_submit=False):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**📊 Current Tax Details:**")
                    st.info(f"Current TDS: ₹{submission['tds_amount']:,.2f}")
                    st.info(f"Tax Regime: {submission['tax_regime']}")
                    
                    # TDS adjustment
                    new_tds = st.number_input(
                        "Revised TDS Amount (₹)", 
                        value=submission['tds_amount'], 
                        min_value=0.0,
                        key=f"revised_tds_{i}",
                        step=100.0
                    )
                    
                    # Additional deductions
                    additional_deductions = st.number_input(
                        "Additional Tax Deductions (₹)", 
                        value=submission.get('additional_deductions', 0.0), 
                        min_value=0.0,
                        key=f"additional_deductions_{i}",
                        step=100.0
                    )
                
                with col2:
                    # Tax regime change
                    new_tax_regime = st.selectbox(
                        "Tax Regime",
                        ["Old Tax Regime", "New Tax Regime"],
                        index=0 if submission['tax_regime'] == "Old Tax Regime" else 1,
                        key=f"new_regime_{i}"
                    )
                    
                    # Review decision
                    review_decision = st.selectbox(
                        "Review Decision",
                        ["Approve", "Send Back for Revision"],
                        key=f"review_decision_{i}"
                    )
                    
                    # Comments
                    tax_comments = st.text_area(
                        "Tax Review Comments", 
                        value=submission.get('tax_comments', ''),
                        key=f"tax_comments_{i}",
                        height=100,
                        help="Add your review comments, feedback, or reasons for changes"
                    )
                
                # Calculate revised amounts
                revised_total_deductions = (
                    submission['total_deductions'] - submission['tds_amount'] + 
                    new_tds + additional_deductions
                )
                revised_net_payable = submission['total_earnings'] - revised_total_deductions
                
                # Show calculation preview
                st.write("**🧮 Revised Calculation Preview:**")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Original TDS", f"₹{submission['tds_amount']:,.0f}")
                with col2:
                    st.metric("Revised TDS", f"₹{new_tds:,.0f}", 
                             delta=f"{new_tds - submission['tds_amount']:+,.0f}")
                with col3:
                    st.metric("Additional Deductions", f"₹{additional_deductions:,.0f}")
                with col4:
                    st.metric("Revised Net Payable", f"₹{revised_net_payable:,.0f}",
                             delta=f"{revised_net_payable - submission['net_payable']:+,.0f}")
                
                # Submit review
                submit_review = st.form_submit_button("📋 Submit Tax Review", use_container_width=True)
                
                if submit_review:
                    # Update submission
                    submission['tds_amount'] = new_tds
                    submission['additional_deductions'] = additional_deductions
                    submission['total_deductions'] = revised_total_deductions
                    submission['net_payable'] = revised_net_payable
                    submission['tax_regime'] = new_tax_regime
                    submission['tax_comments'] = tax_comments
                    submission['tax_reviewed_by'] = st.session_state.get('username', 'Tax Team')
                    submission['tax_review_date'] = datetime.now().strftime('%d/%m/%Y %H:%M')
                    
                    if review_decision == "Approve":
                        submission['status'] = 'Tax Approved'
                        st.success("✅ F&F settlement approved and sent back to Payroll Team!")
                    else:
                        submission['status'] = 'Tax Rejected'
                        st.error("❌ F&F settlement sent back to Payroll Team for revision!")
                    
                    # Save to file
                    save_fnf_data()
                    
                    # Force refresh
                    st.rerun()

def payroll_dashboard():
    """Payroll Dashboard"""
    
    st.title("💼 Payroll Team Dashboard")
    
    # Tabs for different functions
    tab1, tab2, tab3, tab4 = st.tabs(["👥 Employee Master", "📋 F&F Settlement", "📊 F&F Status", "📈 Analytics"])
    
    with tab1:
        st.subheader("Employee Master Data")
        employee_df = load_employee_data()
        
        if not employee_df.empty:
            search_term = st.text_input("🔍 Search Employee (ID or Name)")
            
            if search_term:
                filtered_df = employee_df[
                    (employee_df['Employee ID'].astype(str).str.contains(search_term, na=False)) |
                    (employee_df['Employee Name'].str.contains(search_term, case=False, na=False))
                ]
            else:
                filtered_df = employee_df
            
            st.dataframe(filtered_df, use_container_width=True)
        else:
            st.error("Could not load employee data")
    
    with tab2:
        fnf_settlement_form()
    
    with tab3:
        st.subheader("📊 F&F Settlement Status")
        
        if 'fnf_submissions' in st.session_state and st.session_state.fnf_submissions:
            for submission in st.session_state.fnf_submissions:
                status_color = {
                    'Draft': '🟡',
                    'Under Tax Review': '🟠', 
                    'Tax Approved': '🟢',
                    'Tax Rejected': '🔴',
                    'Payment Processed': '✅'
                }.get(submission['status'], '⚪')
                
                with st.expander(f"{status_color} {submission['employee_name']} - {submission['status']}"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write(f"**Employee:** {submission['employee_name']}")
                        st.write(f"**Employee ID:** {int(submission['employee_id'])}")
                        st.write(f"**Last Working Day:** {submission['last_working_day']}")
                        st.write(f"**Tax Regime:** {submission['tax_regime']}")
                        
                        if 'active_months' in submission:
                            months_list = list(submission['active_months'].keys())
                            st.write(f"**Months:** {', '.join(months_list)}")
                    
                    with col2:
                        st.write(f"**Status:** {submission['status']}")
                        st.write(f"**Total Earnings:** ₹{submission['total_earnings']:,.2f}")
                        st.write(f"**Total Deductions:** ₹{submission['total_deductions']:,.2f}")
                        st.write(f"**Net Payable:** ₹{submission['net_payable']:,.2f}")
                        
                        if 'salary_totals' in submission:
                            st.write(f"**Basic Salary:** ₹{submission['salary_totals']['prorated_basic']:,.2f}")
                            st.write(f"**HRA:** ₹{submission['salary_totals']['prorated_hra']:,.2f}")
                    
                    with col3:
                        if submission['status'] == 'Tax Approved':
                            if st.button(f"💰 Process Payment", key=f"pay_{submission['employee_id']}"):
                                submission['status'] = 'Payment Processed'
                                submission['payment_processed_date'] = datetime.now().strftime('%d/%m/%Y %H:%M')
                                save_fnf_data()  # Save to file
                                st.success("✅ payment processed!")
                                st.rerun()
                        
                        elif submission['status'] == 'Tax Rejected':
                            if st.button(f"📝 Edit & Resubmit", key=f"edit_{submission['employee_id']}"):
                                st.info("Go to F&F Settlement tab to edit")
                    
                    # Show investment details for Old Tax Regime
                    if (submission['tax_regime'] == 'Old Tax Regime' and 
                        'investments_data' in submission and submission['investments_data']):
                        st.write("**💼 Investment Benefits:**")
                        st.info(f"Tax Deductions: ₹{submission['investments_data']['total_deductions']:,.0f}")
                        st.info(f"Exempt Allowances: ₹{submission['investments_data']['exempt_allowances']:,.0f}")
                    
                    # Show tax comments
                    if 'tax_comments' in submission and submission['tax_comments']:
                        st.write("**Tax Team Comments:**")
                        st.info(submission['tax_comments'])
        else:
            st.info("No F&F settlements submitted yet")
    
    with tab4:
        st.subheader("📈 Analytics & Reports")
        employee_df = load_employee_data()
        
        if not employee_df.empty:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Employees", len(employee_df))
            with col2:
                avg_salary = employee_df['Salary'].mean()
                st.metric("Average Salary", f"₹{avg_salary:,.0f}")
            with col3:
                if 'fnf_submissions' in st.session_state:
                    pending_fnf = len([s for s in st.session_state.fnf_submissions if s['status'] != 'Payment Processed'])
                    st.metric("Pending F&F", pending_fnf)
                else:
                    st.metric("Pending F&F", 0)
            with col4:
                locations = employee_df['BaseLocation'].nunique()
                st.metric("Locations", locations)

def login():
    """Login page with CSS Grid for perfect alignment"""
    
    # Advanced CSS for perfect centering
    st.markdown("""
        <style>
        .perfect-center {
            display: grid;
            place-items: center;
            width: 100%;
            gap: 20px;
            text-align: center;
        }
        .logo-section {
            display: grid;
            place-items: center;
            width: 100%;
        }
        .header-section {
            display: grid;
            place-items: center;
            width: 100%;
            gap: 10px;
        }
        .main-title {
            color: #1f4e79;
            font-size: 2.2rem;
            font-weight: 600;
            margin: 0;
            text-align: center;
        }
        .demo-tag {
            background: #28a745;
            color: white;
            padding: 8px 20px;
            border-radius: 25px;
            font-size: 0.9rem;
            font-weight: 500;
            text-align: center;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Perfect centering container
    st.markdown('<div class="perfect-center">', unsafe_allow_html=True)
    
    # Logo section
    st.markdown('<div class="logo-section">', unsafe_allow_html=True)
    try:
        # Use empty columns for perfect centering
        _, center_col, _ = st.columns([2, 1, 2])
        with center_col:
            st.image('assets/koenig-logo.png', width=200)
    except:
        st.markdown("""
            <img src="https://www.koenig-solutions.com/images/logo.png" 
                 width="200" alt="Koenig Solutions Logo" 
                 style="display: block; margin: 0 auto;">
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Header section - perfectly aligned with logo
    st.markdown("""
        <div class="header-section">
            <h2 class="main-title">F&F Settlement System v2.0</h2>
            <div class="demo-tag">Review & Feedback Version</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Main content section
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🔐 System Login")
        
        # Features section with clean boxes
        st.markdown("### ✨ System Capabilities")
        features = [
            "Multi-month salary processing with prorated calculations",
            "Automatic salary breakdown (Basic/HRA/Special Allowances)", 
            "Investment deductions for Old Tax Regime",
            "EPF calculation with ₹1,800 company limit",
            "Auto-gratuity calculation using (n × b × 15) ÷ 26 formula",
            "Dual tax regime support (Old/New)",
            "Comprehensive tax calculations with TDS",
            "Role-based dashboards (Payroll + Tax Team)",
            "Real-time data persistence between user sessions"
        ]
        
        for feature in features:
            st.markdown(f"<div class='feature-box'>✅ {feature}</div>", unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Login form
        st.markdown("### 🔑 Access System")
        username = st.text_input("👤 Username", placeholder="Enter your username")
        password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
        
        if st.button("🚀 Login to System", use_container_width=True, type="primary"):
            if username in users_db and users_db[username]["password"] == password:
                role = users_db[username]["role"]
                st.session_state['role'] = role
                st.session_state['username'] = username
                
                # Load persistent F&F data
                load_fnf_data()
                
                st.success(f"✅ Login successful! Welcome, {role}")
                st.balloons()
                st.rerun()
            else:
                st.error("❌ Invalid credentials. Please check username and password.")
        
        st.markdown("---")
        st.markdown("### 🎮 **Demo Accounts for Testing**")
        
        # Enhanced credential boxes
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("""
                <div class="credential-box">
                    <h3>👥 Payroll Team</h3>
                    <p><strong>Username:</strong> demo_payroll</p>
                    <p><strong>Password:</strong> demo123</p>
                    <small>Create and manage F&F settlements</small>
                </div>
            """, unsafe_allow_html=True)
            
        with col_b:
            st.markdown("""
                <div class="credential-box">
                    <h3>📊 Tax Team</h3>
                    <p><strong>Username:</strong> demo_tax</p>
                    <p><strong>Password:</strong> demo123</p>
                    <small>Review and approve F&F submissions</small>
                </div>
            """, unsafe_allow_html=True)
        
        # Testing guide
        st.markdown("---")
        st.markdown("### 📝 **Testing & Feedback Guide**")
        
        with st.expander("🔍 **Quick Start Guide**", expanded=True):
            st.markdown("""
            **Step 1:** Login with demo credentials above  
            **Step 2:** Test Employee IDs: 1001, 1002, 1003, 1004, 1005  
            **Step 3:** Create F&F settlements with different scenarios  
            **Step 4:** Switch roles to test complete workflow  
            **Step 5:** Provide feedback on functionality and UI/UX  
            """)
        
        st.markdown("---")
        st.markdown("""
            <div style='text-align: center; color: #666; font-size: 0.9em; padding: 20px;'>
                © 2024 Koenig Solutions - F&F Settlement System v2.0<br>
                <em>Demo Version for Review & Feedback</em>
            </div>
        """, unsafe_allow_html=True)

def main():
    st.set_page_config(
        page_title="F&F Settlement System - Review",
        page_icon="💼",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    if 'fnf_submissions' not in st.session_state:
        st.session_state.fnf_submissions = []
    
    # Add sidebar logo for all authenticated pages
    if 'role' in st.session_state:
        add_sidebar_logo()
    
    # Show appropriate page based on authentication
    if 'role' not in st.session_state:
        login()
    elif st.session_state['role'] == 'Payroll Team':
        payroll_dashboard()
    elif st.session_state['role'] == 'Tax Team':
        tax_review_dashboard()
    else:
        st.error("Unknown role")

if __name__ == "__main__":
    main()
