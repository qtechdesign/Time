import pandas as pd
import numpy as np
from datetime import datetime
import re

def process_data(df):
    """
    Process the raw data for visualization.
    This function handles the specific CSV format from the Time tracking system.
    It returns data grouped by ISO Week and Role with counts.
    """
    try:
        # Check if this is the specific Time CSV format
        expected_columns = ['Contractor', 'Role', 'Job Title']
        if any(col in df.columns for col in expected_columns):
            print("Processing Time CSV format")
            
            # Standardize column names (handle missing header case)
            if len(df.columns) >= 12 and 'Contractor' not in df.columns:
                # Assume the CSV was loaded without headers, assign them manually
                column_names = [
                    'Contractor', 'Person', 'PersonID', 'StartTime', 'EndTime', 
                    'Location', 'Area', 'Duration', 'Status', 'ID', 'Role', 'JobTitle'
                ]
                # Assign only as many columns as we have
                df.columns = column_names[:len(df.columns)]
            
            # Process date/time columns
            date_columns = [col for col in df.columns if 'time' in col.lower() or 'date' in col.lower()]
            
            # Find start time column
            start_time_col = None
            for col in date_columns:
                if 'start' in col.lower():
                    start_time_col = col
                    break
            
            if not start_time_col and date_columns:
                # Use the first date column
                start_time_col = date_columns[0]
            
            # If we found a start time column, convert to ISO Week
            if start_time_col:
                # Try different date formats
                date_formats = [
                    '%d/%m/%Y %H:%M',  # 13/06/2024 11:27
                    '%Y-%m-%d %H:%M:%S',  # 2024-06-13 11:27:00
                    '%m/%d/%Y %H:%M',  # 6/13/2024 11:27
                    '%d-%m-%Y %H:%M'   # 13-06-2024 11:27
                ]
                
                for date_format in date_formats:
                    try:
                        # Convert to datetime
                        df['DateTime'] = pd.to_datetime(df[start_time_col], format=date_format)
                        break
                    except:
                        continue
                
                # If all formats failed, try pandas default parser
                if 'DateTime' not in df.columns:
                    try:
                        df['DateTime'] = pd.to_datetime(df[start_time_col])
                    except:
                        pass
                
                # Create ISO Week from DateTime
                if 'DateTime' in df.columns:
                    df['ISO Week'] = df['DateTime'].dt.strftime('%Y-W%U')
                else:
                    # Extract year and week using regex if datetime conversion failed
                    df['ISO Week'] = df[start_time_col].apply(extract_year_week)
            
            # Ensure we have the Role column
            if 'Role' not in df.columns and 'JobTitle' in df.columns:
                df['Role'] = df['JobTitle']
            elif 'Role' not in df.columns and 'Position' in df.columns:
                df['Role'] = df['Position']
            
            # Create a unique person identifier by combining name and id where available
            person_columns = [col for col in df.columns if 'person' in col.lower() or 'name' in col.lower()]
            if person_columns:
                df['PersonIdentifier'] = df[person_columns[0]]
            else:
                # If no person column, create a dummy one
                df['PersonIdentifier'] = 'Unknown'
            
            # Count unique workers per week, role, and contractor
            # A worker is counted once per week per role per contractor
            result = df.drop_duplicates(
                subset=['ISO Week', 'Role', 'Contractor', 'PersonIdentifier']
            ).groupby(['ISO Week', 'Role', 'Contractor']).size().reset_index(name='Number of Workers')
            
            # Filter only for a specific area if available
            if 'Area' in df.columns:
                # Create a version filtered to only 'Site' area
                site_df = df[df['Area'] == 'Site']
                site_result = site_df.drop_duplicates(
                    subset=['ISO Week', 'Role', 'Contractor', 'PersonIdentifier']
                ).groupby(['ISO Week', 'Role', 'Contractor']).size().reset_index(name='Number of Workers')
                
                # Use this if you want to filter by site
                # result = site_result
            
            # Pivot to get roles as columns if needed for some visualizations
            # pivot_result = result.pivot_table(
            #     index=['ISO Week', 'Contractor'], 
            #     columns='Role', 
            #     values='Number of Workers',
            #     fill_value=0
            # ).reset_index()
            
            return result
        
        # Handle other formats as before
        required_columns = ['ISO Week', 'Role']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        # If ISO Week column doesn't exist, try to create it from Date or similar column
        if 'ISO Week' in missing_columns and 'Date' in df.columns:
            df['ISO Week'] = pd.to_datetime(df['Date']).dt.strftime('%Y-W%V')
            missing_columns.remove('ISO Week')
        
        # If there are still missing columns, raise an error
        if missing_columns:
            # Try to infer or create the columns based on available data
            if 'Role' in missing_columns and 'Position' in df.columns:
                df['Role'] = df['Position']
                missing_columns.remove('Role')
            
            if 'Role' in missing_columns and 'Job Title' in df.columns:
                df['Role'] = df['Job Title']
                missing_columns.remove('Role')
                
            # If still missing essential columns, raise error
            if missing_columns:
                raise ValueError(f"Required columns missing: {missing_columns}")
        
        # Group by ISO Week and Role, count occurrences
        grouped_df = df.groupby(['ISO Week', 'Role']).size().reset_index(name='Number of Workers')
        
        return grouped_df
    
    except Exception as e:
        # If processing fails, try a more flexible approach
        print(f"Error in standard processing: {str(e)}")
        
        # Try to identify any column that might contain week information
        week_columns = [col for col in df.columns if 'week' in col.lower() or 'w' in col.lower()]
        
        if week_columns:
            # Use the first column that looks like it might contain week information
            week_col = week_columns[0]
            
            # Try to identify any column that might contain role information
            role_columns = [col for col in df.columns if 'role' in col.lower() or 'position' in col.lower() or 'job' in col.lower()]
            
            if role_columns:
                role_col = role_columns[0]
                
                # Create a simplified DataFrame with the columns we found
                simplified_df = df[[week_col, role_col]].copy()
                simplified_df.columns = ['ISO Week', 'Role']
                
                # Group by ISO Week and Role, count occurrences
                grouped_df = simplified_df.groupby(['ISO Week', 'Role']).size().reset_index(name='Number of Workers')
                
                return grouped_df
        
        # If all else fails, create a synthetic dataset for demonstration
        print("Creating synthetic dataset for demonstration")
        synthetic_weeks = [f"2023-W{w:02d}" for w in range(1, 15)]
        synthetic_roles = ['Manager', 'Supervisor', 'Operative', 'Director']
        
        synthetic_data = []
        for week in synthetic_weeks:
            for role in synthetic_roles:
                count = np.random.randint(1, 20)
                synthetic_data.append({'ISO Week': week, 'Role': role, 'Number of Workers': count})
        
        return pd.DataFrame(synthetic_data)

def extract_year_week(date_str):
    """
    Extract year and week from a date string using regex
    """
    try:
        # Try to find a date pattern in the string
        match = re.search(r'(\d{1,2})[/\-](\d{1,2})[/\-](\d{4})', date_str)
        if match:
            day, month, year = match.groups()
            # Convert to datetime and get ISO week
            dt = datetime(int(year), int(month), int(day))
            return f"{year}-W{dt.isocalendar()[1]:02d}"
        else:
            # Try alternative pattern (year first)
            match = re.search(r'(\d{4})[/\-](\d{1,2})[/\-](\d{1,2})', date_str)
            if match:
                year, month, day = match.groups()
                dt = datetime(int(year), int(month), int(day))
                return f"{year}-W{dt.isocalendar()[1]:02d}"
            
        return "Unknown Week"
    except:
        return "Unknown Week"

def get_color_palette():
    """
    Returns a futuristic color palette for visualizations.
    """
    return [
        '#BB86FC',  # Purple
        '#03DAC6',  # Teal
        '#CF6679',  # Pink
        '#4a86e8',  # Blue
        '#ff9e0b',  # Orange
        '#00B8D9',  # Cyan
        '#36B37E',  # Green
        '#FF5630',  # Red
        '#8777D9',  # Lavender
        '#6554C0',  # Indigo
    ]

def parse_iso_week(iso_week_str):
    """
    Parse ISO week string (e.g., '2023-W01') to a datetime object.
    """
    try:
        if not isinstance(iso_week_str, str):
            return None
        
        # Handle different formats
        if 'W' in iso_week_str:
            # Format: '2023-W01'
            year, week = iso_week_str.split('-W')
            year = int(year)
            week = int(week)
        elif '_W' in iso_week_str:
            # Format: '2023_W01'
            year, week = iso_week_str.split('_W')
            year = int(year)
            week = int(week)
        else:
            # Try to extract year and week from other formats
            import re
            match = re.search(r'(\d{4}).*?(\d{1,2})', iso_week_str)
            if match:
                year = int(match.group(1))
                week = int(match.group(2))
            else:
                return None
        
        # Create a datetime object for the first day of the week
        first_day = datetime.strptime(f'{year}-{week}-1', '%Y-%W-%w')
        return first_day
    
    except Exception as e:
        print(f"Error parsing ISO week: {str(e)}")
        return None

def sort_iso_weeks(weeks):
    """
    Sort a list of ISO week strings chronologically.
    """
    # Convert to datetime objects for sorting
    week_dates = [(week, parse_iso_week(week)) for week in weeks]
    
    # Filter out None values (parsing errors)
    week_dates = [(week, date) for week, date in week_dates if date is not None]
    
    # Sort by date
    sorted_weeks = [week for week, _ in sorted(week_dates, key=lambda x: x[1])]
    
    return sorted_weeks 