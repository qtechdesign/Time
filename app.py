import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np
import os
from utils import process_data, get_color_palette, sort_iso_weeks

# Page configuration
st.set_page_config(
    page_title="Time Tracker Analyzer",
    page_icon="⏱️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for dark mode and sleeker design
st.markdown("""
<style>
    /* Custom dark theme colors */
    :root {
        --background-color: #0e1117;
        --secondary-background-color: #1a1d24;
        --primary-color: #4a86e8;
        --secondary-color: #03DAC6;
        --text-color: #fafafa;
        --font: 'Roboto', sans-serif;
    }
    
    .stApp {
        background-color: var(--background-color);
        color: var(--text-color);
    }
    
    /* Sleeker rounded containers */
    div.css-1r6slb0.e1tzin5v2 {
        background-color: var(--secondary-background-color);
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.4);
    }
    
    /* Button styling */
    .stButton > button {
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        font-weight: 600;
        transition: all 0.2s ease;
        background-color: var(--primary-color);
        color: white;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 8px rgba(0, 0, 0, 0.15);
        background-color: #5c92e8;
    }
    
    /* Upload button */
    .css-u8hs99.e1ewe7hr3 {
        padding: 10px;
        border-radius: 10px;
        border: 2px dashed var(--primary-color);
    }
    
    /* Headers */
    h1, h2, h3 {
        color: var(--secondary-color);
        font-weight: 700;
    }

    /* Progress bar */
    .stProgress > div > div {
        background-color: var(--secondary-color);
        border-radius: 10px;
    }
    
    /* Footer */
    footer {
        visibility: hidden;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: var(--secondary-background-color);
        border-radius: 8px 8px 0px 0px;
        padding: 0px 20px;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: var(--primary-color) !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'step' not in st.session_state:
    st.session_state.step = 1

# Functions for navigation
def next_step():
    st.session_state.step += 1

def prev_step():
    st.session_state.step -= 1

def reset_app():
    st.session_state.step = 1
    if 'data' in st.session_state:
        del st.session_state.data
    if 'file_name' in st.session_state:
        del st.session_state.file_name
    if 'raw_data' in st.session_state:
        del st.session_state.raw_data

# Helper functions for data display
def display_column_mapping_info(raw_df):
    """Display information about how columns were mapped/detected."""
    st.subheader("CSV Column Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.caption("Detected Columns")
        columns = ", ".join(raw_df.columns.tolist())
        if len(columns) > 100:
            columns = columns[:100] + "..."
        st.write(columns)
    
    with col2:
        # Check for required columns
        required_columns = {
            "Contractor": ["Contractor", "Company", "Organization"],
            "Time Data": ["In", "Out", "Total Minutes"],
            "Worker Info": ["Worker Name", "Bio ID", "Worker ID"],
            "Location": ["Area", "Site"],
            "Role": ["Role", "Trade"]
        }
        
        results = []
        for category, columns in required_columns.items():
            found = [col for col in columns if col in raw_df.columns]
            if found:
                results.append(f"✅ {category}: {', '.join(found)}")
            else:
                results.append(f"⚠️ {category}: Missing")
        
        st.caption("Key Column Check")
        for result in results:
            st.write(result)
    
    # Add tips for users if key columns are missing
    missing_categories = [cat for cat, cols in required_columns.items() 
                         if not any(col in raw_df.columns for col in cols)]
    
    if missing_categories:
        st.warning(f"Missing data for: {', '.join(missing_categories)}. Some visualizations may not work properly.")
        
        with st.expander("Tips for fixing missing data"):
            st.markdown("""
            ## Column Name Tips
            
            For best results, your CSV should include these columns:
            
            - **Contractor/Company**: The name of the contracting company
            - **Worker Name**: The name of the worker
            - **Role/Trade**: Worker's role or job title
            - **In/Out**: Date and time of entry/exit (format: DD/MM/YYYY HH:MM)
            - **Area**: Location in the project (e.g., Site, Welfare)
            - **Total Minutes**: Duration in minutes (calculated automatically if missing)
            
            You can use our sample file as a template.
            """)

def ensure_required_columns(df):
    """Check for required columns and add them if missing"""
    required_columns = ['Contractor', 'Role', 'ISO Week', 'Number of Workers']
    
    for col in required_columns:
        if col not in df.columns:
            if col == 'Contractor':
                # If first column looks like a company name, use it
                if df.columns[0] in df.iloc[0].values and isinstance(df.iloc[0,0], str):
                    df[col] = df.iloc[:,0]
                else:
                    df[col] = 'Unknown Contractor'
            elif col == 'Role':
                # Look for role-like columns
                role_cols = [c for c in df.columns if c.lower() in ['job', 'title', 'position', 'trade']]
                if role_cols:
                    df[col] = df[role_cols[0]]
                else:
                    df[col] = 'Worker'
            elif col == 'ISO Week':
                # Create from date column if possible
                date_cols = [c for c in df.columns if c.lower() in ['date', 'time', 'in', 'out']]
                if date_cols:
                    try:
                        df[col] = pd.to_datetime(df[date_cols[0]]).dt.strftime('%Y-W%U')
                    except:
                        df[col] = 'Unknown Week'
                else:
                    df[col] = 'Unknown Week'
            elif col == 'Number of Workers':
                df[col] = 1
    
    return df

# Step 1: Streamlined Welcome Screen
if st.session_state.step == 1:
    st.title("Time Tracker Analyzer")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("""
        ## Visualize your Time Tracker data
        
        Upload your Time Tracker CSV file to analyze:
        
        - 📊 **Worker counts** by contractor and role
        - ⏱️ **Time spent analysis** for Site vs. Welfare
        - 👥 **Contractor comparison** across weeks
        - 🧑‍💼 **Role distribution** by contractor
        
        Simply upload your Time Tracker export file to begin.
        """)
    
    with col2:
        st.image("https://img.icons8.com/color/240/overtime--v1.png", width=150)
    
    st.markdown("---")
    
    # Combine upload and welcome on the first screen for a more straightforward flow
    uploaded_file = st.file_uploader("Choose a CSV file from Time Tracker", type="csv")
    
    if uploaded_file is not None:
        try:
            with st.spinner("Processing data..."):
                # Save the file name
                st.session_state.file_name = uploaded_file.name
                
                # Try different parsing approaches for the CSV
                try:
                    df = pd.read_csv(uploaded_file)
                except:
                    try:
                        df = pd.read_csv(uploaded_file, sep=';')
                    except:
                        try:
                            df = pd.read_csv(uploaded_file, header=None)
                        except:
                            st.error("Could not parse the CSV file. Please check the format.")
                            raise
                
                # Store the raw data and process it
                st.session_state.raw_data = df
                processed_data = process_data(df)
                
                # Ensure required columns exist
                processed_data = ensure_required_columns(processed_data)
                st.session_state.data = processed_data
                
                st.success(f"Successfully loaded {uploaded_file.name}")
                
                # Brief data preview and auto-continue to visualizations
                st.subheader("Data Preview")
                display_column_mapping_info(df)
                
                with st.expander("View Processed Data Sample"):
                    st.dataframe(processed_data.head(5), use_container_width=True)
                
                # Continue button
                st.button("Continue to Visualization", on_click=next_step, use_container_width=True)
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
            st.info("""
            Please check if your CSV file has the expected format. Common issues:
            
            1. Make sure your file has headers (column names)
            2. Check for special characters in column names
            3. Verify the file is properly formatted CSV
            
            You can use our sample data file as a reference.
            """)

# Step 2: Visualization (simplified to just one step instead of multiple)
elif st.session_state.step == 2:
    if 'data' not in st.session_state or 'raw_data' not in st.session_state:
        st.error("No data available. Please upload a CSV file first.")
        st.button("Go to Upload", on_click=lambda: setattr(st.session_state, 'step', 1))
    else:
        st.title("Time Tracker Analysis")
        
        # Show file name and a reset button in the header
        col1, col2 = st.columns([3, 1])
        with col1:
            st.caption(f"Data source: {st.session_state.file_name}")
        with col2:
            st.button("Load New File", on_click=reset_app, use_container_width=True)
        
        # Process data for visualization
        try:
            df = st.session_state.data
            raw_df = st.session_state.raw_data
            
            # Create tabs for different visualizations
            tab1, tab2, tab3, tab4 = st.tabs([
                "Workforce by Week", 
                "Site vs. Welfare Time", 
                "Contractor Comparison",
                "Role Distribution"
            ])
            
            # Tab 1: Workers per Week
            with tab1:
                st.subheader("Workers Per Week by Contractor")
                
                # Get unique contractors for filtering
                contractors = df['Contractor'].unique().tolist()
                
                if not contractors:
                    st.error("No contractors found in the data. Please check your CSV format.")
                else:
                    selected_contractor = st.selectbox("Select Contractor", options=contractors)
                    
                    # Filter data by selected contractor
                    filtered_df = df[df['Contractor'] == selected_contractor]
                    
                    if filtered_df.empty:
                        st.warning(f"No data available for contractor: {selected_contractor}")
                    else:
                        # Sort ISO weeks chronologically
                        all_weeks = filtered_df['ISO Week'].unique().tolist()
                        sorted_weeks = sort_iso_weeks(all_weeks)
                        
                        # Create visualization with Plotly
                        fig = px.bar(
                            filtered_df, 
                            x='ISO Week', 
                            y='Number of Workers',
                            color='Role',
                            title=f"Workers per Week for {selected_contractor}",
                            color_discrete_sequence=get_color_palette(),
                            barmode='stack',
                            category_orders={"ISO Week": sorted_weeks} if sorted_weeks else None
                        )
                        
                        # Customize figure layout
                        fig.update_layout(
                            template="plotly_dark",
                            paper_bgcolor="#0e1117",
                            plot_bgcolor="#0e1117",
                            legend=dict(orientation="h", yanchor="bottom", y=1.02),
                            margin=dict(l=20, r=20, t=60, b=20),
                        )
                        
                        # Display the chart
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Summary statistics
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            total_workers = filtered_df['Number of Workers'].sum()
                            st.metric("Total Workers", f"{total_workers}")
                        with col2:
                            peak_week = filtered_df.groupby('ISO Week')['Number of Workers'].sum().idxmax()
                            peak = filtered_df.groupby('ISO Week')['Number of Workers'].sum().max()
                            st.metric("Peak Week", f"{peak_week}: {peak} workers")
                        with col3:
                            unique_roles = filtered_df['Role'].nunique()
                            st.metric("Unique Roles", f"{unique_roles}")
            
            # Tab 2: Time Analysis (Site/Welfare) - Enhanced version
            with tab2:
                st.subheader("Time Spent Analysis (Site vs. Welfare)")
                
                # Check if we have area data and create time analysis
                if 'Area' in raw_df.columns:
                    # Get unique contractors for filtering
                    contractors = raw_df['Contractor'].unique().tolist() if 'Contractor' in raw_df.columns else []
                    
                    if contractors:
                        selected_contractor = st.selectbox("Select Contractor", options=contractors, key="time_analysis")
                        
                        # Filter data for selected contractor
                        filtered_raw_df = raw_df[raw_df['Contractor'] == selected_contractor]
                        
                        # Check for required columns
                        if 'In' in filtered_raw_df.columns and 'Out' in filtered_raw_df.columns and 'Area' in filtered_raw_df.columns:
                            # Calculate time spent in each area
                            try:
                                # Convert In/Out to datetime
                                filtered_raw_df['In_dt'] = pd.to_datetime(filtered_raw_df['In'], errors='coerce')
                                filtered_raw_df['Out_dt'] = pd.to_datetime(filtered_raw_df['Out'], errors='coerce')
                                
                                # Calculate duration (if Total Minutes not available)
                                if 'Total Minutes' in filtered_raw_df.columns:
                                    filtered_raw_df['Duration'] = pd.to_numeric(filtered_raw_df['Total Minutes'], errors='coerce')
                                else:
                                    filtered_raw_df['Duration'] = (filtered_raw_df['Out_dt'] - filtered_raw_df['In_dt']).dt.total_seconds() / 60
                                
                                # Extract date from In time
                                filtered_raw_df['Date'] = filtered_raw_df['In_dt'].dt.date
                                
                                # Group by Date and Area, sum duration
                                time_analysis = filtered_raw_df.groupby(['Date', 'Area'])['Duration'].sum().reset_index()
                                
                                # Identify available areas
                                areas = time_analysis['Area'].unique()
                                site_area = [a for a in areas if 'site' in a.lower()]
                                site_area = site_area[0] if site_area else 'Site' if 'Site' in areas else None
                                welfare_area = [a for a in areas if 'welfare' in a.lower()]
                                welfare_area = welfare_area[0] if welfare_area else 'Welfare' if 'Welfare' in areas else None
                                
                                if site_area or welfare_area:
                                    # Pivot to get areas as columns
                                    area_pivot = time_analysis.pivot(index='Date', columns='Area', values='Duration').reset_index()
                                    
                                    # Fill NaN with 0
                                    area_pivot = area_pivot.fillna(0)
                                    
                                    # Calculate total and ensure site/welfare columns exist
                                    if site_area and site_area not in area_pivot.columns:
                                        area_pivot[site_area] = 0
                                    if welfare_area and welfare_area not in area_pivot.columns:
                                        area_pivot[welfare_area] = 0
                                    
                                    # Calculate totals and percentages
                                    area_columns = [col for col in area_pivot.columns if col != 'Date']
                                    area_pivot['Total'] = area_pivot[area_columns].sum(axis=1)
                                    
                                    # Create stacked bar chart for daily breakdown
                                    fig = px.bar(
                                        area_pivot,
                                        x='Date',
                                        y=area_columns,
                                        title=f"Daily Time Spent by Area for {selected_contractor}",
                                        color_discrete_sequence=get_color_palette(),
                                        barmode='stack'
                                    )
                                    
                                    fig.update_layout(
                                        template="plotly_dark",
                                        paper_bgcolor="#0e1117",
                                        plot_bgcolor="#0e1117",
                                        legend=dict(orientation="h", yanchor="bottom", y=1.02),
                                        margin=dict(l=20, r=20, t=60, b=20),
                                        yaxis_title="Minutes"
                                    )
                                    
                                    st.plotly_chart(fig, use_container_width=True)
                                    
                                    # Summary statistics for each area with expandable details
                                    with st.expander("Time Breakdown Details"):
                                        # Convert minutes to hours for summary
                                        for area in area_columns:
                                            total_minutes = area_pivot[area].sum()
                                            hours = total_minutes / 60
                                            percent = (total_minutes / area_pivot['Total'].sum() * 100) if area_pivot['Total'].sum() > 0 else 0
                                            
                                            col1, col2, col3 = st.columns(3)
                                            with col1:
                                                st.metric(f"{area}", f"{hours:.1f} hours", f"{percent:.1f}%")
                                            with col2:
                                                st.metric(f"{area} (minutes)", f"{total_minutes:.0f} min")
                                            with col3:
                                                daily_avg = total_minutes / len(area_pivot) if len(area_pivot) > 0 else 0
                                                st.metric(f"Daily Average", f"{daily_avg:.1f} min/day")
                                    
                                    # Create worker efficiency analysis (assuming Site is productive time)
                                    if site_area and welfare_area:
                                        site_total = area_pivot[site_area].sum() if site_area in area_pivot.columns else 0
                                        welfare_total = area_pivot[welfare_area].sum() if welfare_area in area_pivot.columns else 0
                                        total_time = site_total + welfare_total
                                        
                                        # Calculate productivity ratio
                                        productivity = (site_total / total_time * 100) if total_time > 0 else 0
                                        
                                        st.subheader("Site vs. Welfare Time")
                                        
                                        col1, col2 = st.columns(2)
                                        
                                        with col1:
                                            # Create a gauge chart for productivity
                                            fig = go.Figure(go.Indicator(
                                                mode="gauge+number",
                                                value=productivity,
                                                title={'text': "Site Time Percentage"},
                                                gauge={
                                                    'axis': {'range': [0, 100]},
                                                    'bar': {'color': "#03DAC6"},
                                                    'steps': [
                                                        {'range': [0, 70], 'color': "#CF6679"},
                                                        {'range': [70, 85], 'color': "#ff9e0b"},
                                                        {'range': [85, 100], 'color': "#36B37E"}
                                                    ],
                                                },
                                                domain={'x': [0, 1], 'y': [0, 1]}
                                            ))
                                            
                                            fig.update_layout(
                                                template="plotly_dark",
                                                paper_bgcolor="#0e1117",
                                                plot_bgcolor="#0e1117",
                                                height=300
                                            )
                                            
                                            st.plotly_chart(fig, use_container_width=True)
                                        
                                        with col2:
                                            # Create a pie chart for time distribution
                                            area_summary = pd.DataFrame({
                                                'Area': [site_area, welfare_area],
                                                'Minutes': [site_total, welfare_total]
                                            })
                                            
                                            fig = px.pie(
                                                area_summary,
                                                values='Minutes',
                                                names='Area',
                                                title=f"Time Distribution",
                                                color_discrete_sequence=['#03DAC6', '#BB86FC'],
                                                hole=0.4
                                            )
                                            
                                            fig.update_layout(
                                                template="plotly_dark",
                                                paper_bgcolor="#0e1117",
                                                plot_bgcolor="#0e1117",
                                                height=300
                                            )
                                            
                                            st.plotly_chart(fig, use_container_width=True)
                                        
                                        # Time efficiency metrics
                                        col1, col2, col3 = st.columns(3)
                                        with col1:
                                            st.metric("Total Hours", f"{total_time/60:.1f}")
                                        with col2:
                                            site_hours = site_total / 60
                                            st.metric("Site Hours", f"{site_hours:.1f}")
                                        with col3:
                                            welfare_hours = welfare_total / 60
                                            st.metric("Welfare Hours", f"{welfare_hours:.1f}")
                                else:
                                    st.warning("No Site/Welfare areas found in the data. Please check your 'Area' column values.")
                            except Exception as e:
                                st.error(f"Error analyzing time data: {str(e)}")
                                st.code(str(e))
                        else:
                            st.warning("Required columns for time analysis (In, Out, Area) not found in the data.")
                    else:
                        st.warning("No contractor data found for time analysis.")
                else:
                    st.info("No Area column found in the data. This analysis requires an 'Area' column to distinguish between Site and Welfare areas.")
            
            # Tab 3: Contractor Comparison
            with tab3:
                st.subheader("Contractor Comparison")
                
                # Get unique contractors
                contractors = df['Contractor'].unique().tolist()
                
                if len(contractors) < 2:
                    st.info("At least 2 contractors are needed for comparison. Your data contains only one contractor.")
                else:
                    # Default to selecting all if there are 5 or fewer
                    default_selection = contractors if len(contractors) <= 5 else contractors[:5]
                    selected_contractors = st.multiselect(
                        "Select Contractors to Compare", 
                        options=contractors,
                        default=default_selection
                    )
                    
                    if selected_contractors:
                        # Filter data for selected contractors
                        comparison_df = df[df['Contractor'].isin(selected_contractors)]
                        
                        # Group by ISO Week and Contractor
                        weekly_data = comparison_df.groupby(['ISO Week', 'Contractor'])['Number of Workers'].sum().reset_index()
                        
                        # Sort ISO weeks
                        sorted_weeks = sort_iso_weeks(weekly_data['ISO Week'].unique().tolist())
                        
                        # Create line chart
                        fig = px.line(
                            weekly_data,
                            x='ISO Week',
                            y='Number of Workers',
                            color='Contractor',
                            title="Workforce Comparison Across Contractors",
                            color_discrete_sequence=get_color_palette(),
                            markers=True,
                            category_orders={"ISO Week": sorted_weeks} if sorted_weeks else None
                        )
                        
                        # Customize layout
                        fig.update_layout(
                            template="plotly_dark",
                            paper_bgcolor="#0e1117",
                            plot_bgcolor="#0e1117",
                            legend=dict(orientation="h", yanchor="bottom", y=1.02),
                            margin=dict(l=20, r=20, t=60, b=20),
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Summary statistics
                        st.subheader("Contractor Statistics")
                        stats = comparison_df.groupby('Contractor')['Number of Workers'].agg(['sum', 'mean', 'max']).reset_index()
                        stats.columns = ['Contractor', 'Total Workers', 'Average per Week', 'Peak Workers']
                        
                        # Round the average to 1 decimal place
                        stats['Average per Week'] = stats['Average per Week'].round(1)
                        
                        st.dataframe(stats, use_container_width=True)
                    else:
                        st.info("Please select at least one contractor for comparison.")
            
            # Tab 4: Role Distribution
            with tab4:
                st.subheader("Role Distribution Analysis")
                
                # Get unique contractors
                contractors = df['Contractor'].unique().tolist()
                
                if not contractors:
                    st.error("No contractors found in the data.")
                else:
                    selected_contractor = st.selectbox("Select Contractor", options=contractors, key="role_dist")
                    
                    # Filter data by selected contractor
                    filtered_df = df[df['Contractor'] == selected_contractor]
                    
                    if filtered_df.empty:
                        st.warning(f"No data for contractor: {selected_contractor}")
                    else:
                        # Group by Role and sum workers
                        role_data = filtered_df.groupby('Role')['Number of Workers'].sum().reset_index()
                        
                        # Sort by number of workers descending
                        role_data = role_data.sort_values('Number of Workers', ascending=False)
                        
                        # Create pie chart
                        fig = px.pie(
                            role_data,
                            values='Number of Workers',
                            names='Role',
                            title=f"Role Distribution for {selected_contractor}",
                            color_discrete_sequence=get_color_palette()
                        )
                        
                        # Customize layout
                        fig.update_layout(
                            template="plotly_dark",
                            paper_bgcolor="#0e1117",
                            plot_bgcolor="#0e1117"
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Role metrics
                        total_workers = role_data['Number of Workers'].sum()
                        top_role = role_data.iloc[0]['Role']
                        top_role_count = role_data.iloc[0]['Number of Workers']
                        top_role_percent = (top_role_count / total_workers * 100) if total_workers > 0 else 0
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Total Workforce", f"{total_workers}")
                        with col2:
                            st.metric("Number of Roles", f"{len(role_data)}")
                        with col3:
                            st.metric(f"Top Role: {top_role}", f"{top_role_count}", f"{top_role_percent:.1f}%")
                        
                        # Create bar chart showing roles over time
                        role_time = filtered_df.copy()
                        
                        # Sort ISO weeks
                        sorted_weeks = sort_iso_weeks(role_time['ISO Week'].unique().tolist())
                        
                        # Create line chart
                        fig = px.line(
                            role_time,
                            x='ISO Week',
                            y='Number of Workers',
                            color='Role',
                            title=f"Role Trends for {selected_contractor}",
                            color_discrete_sequence=get_color_palette(),
                            markers=True,
                            category_orders={"ISO Week": sorted_weeks} if sorted_weeks else None
                        )
                        
                        # Customize layout
                        fig.update_layout(
                            template="plotly_dark",
                            paper_bgcolor="#0e1117",
                            plot_bgcolor="#0e1117",
                            legend=dict(orientation="h", yanchor="bottom", y=1.02),
                            margin=dict(l=20, r=20, t=60, b=20),
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
        
        except Exception as e:
            st.error(f"Error generating visualizations: {str(e)}")
            st.code(str(e))
            st.info("Try uploading your file again or check if the CSV format matches the expected structure.")

# Minimal footer
st.markdown("---")
st.caption("Time Tracker Analyzer | Data processed locally") 