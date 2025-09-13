import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

def get_employee_data():
    """Fetch employee data from the 'Employee Master' worksheet"""
    
    SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    
    SERVICE_ACCOUNT_FILE = '/Users/praveenchaudhary/Desktop/FNF/credentials.json'
    
    try:
        # Authenticate
        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        gc = gspread.authorize(creds)
        
        # Open the spreadsheet by name
        spreadsheet = gc.open("FNF Calculation")
        
        # Access the "Employee Master" worksheet (not the first sheet)
        worksheet = spreadsheet.worksheet("Employee Master")  # Access by name
        
        # Get all data
        data = worksheet.get_all_records()
        
        # Convert to pandas DataFrame
        df = pd.DataFrame(data)
        
        print(f"✅ Successfully loaded {len(df)} employees from 'Employee Master' worksheet")
        return df
        
    except gspread.exceptions.WorksheetNotFound:
        print("❌ 'Employee Master' worksheet not found")
        print("Available worksheets:")
        try:
            spreadsheet = gc.open("FNF Calculation")
            for ws in spreadsheet.worksheets():
                print(f"  - {ws.title}")
        except:
            pass
        return pd.DataFrame()
        
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return pd.DataFrame()

if __name__ == "__main__":
    # Test the function
    df = get_employee_data()
    if not df.empty:
        print("Data from Employee Master worksheet:")
        print(df.head())
        print(f"\nColumns: {list(df.columns)}")
        print(f"Shape: {df.shape}")
    else:
        print("Failed to load data or worksheet is empty")
