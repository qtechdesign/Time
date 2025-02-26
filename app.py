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
    page_title="Contractor Workforce Analyzer",
    page_icon="👷",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for dark mode and rounded elements
st.markdown("""
<style>
    /* Custom dark theme colors */
    :root {
        --background-color: #0e1117;
        --secondary-background-color: #262730;
        --primary-color: #4a86e8;
        --secondary-color: #bb86fc;
        --text-color: #fafafa;
        --font: 'Roboto', sans-serif;
    }
    
    .stApp {
        background-color: var(--background-color);
        color: var(--text-color);
    }
    
    /* Rounded containers */
    div.css-1r6slb0.e1tzin5v2 {
        background-color: var(--secondary-background-color);
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
    }
    
    /* Button styling */
    .stButton > button {
        border-radius: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 8px rgba(0, 0, 0, 0.15);
    }
    
    /* Upload button */
    .css-u8hs99.e1ewe7hr3 {
        padding: 10px;
        border-radius: 20px;
        border: 2px dashed #4a86e8;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: var(--secondary-color);
        font-weight: 700;
    }

    /* Progress bar */
    .stProgress > div > div {
        background-color: var(--secondary-color);
        border-radius: 20px;
    }
    
    /* Footer */
    footer {
        visibility: hidden;
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

# Step 1: Welcome Screen
if st.session_state.step == 1:
    st.title("Contractor Workforce Analyzer")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ## 👋 Welcome to the Contractor Workforce Analyzer!
        
        This application helps you visualize contractor workforce data from your CSV files.
        
        ### Features:
        - 📊 Interactive charts for workers per week per contractor
        - 🔍 Filter by specific contractors or time periods
        - 📱 Fully responsive design
        - 🌙 Dark mode interface
        
        No data is stored in the cloud - your data remains on your device.
        """)
    
    with col2:
        st.image("https://img.icons8.com/fluency/240/analytics.png", width=200)
    
    st.markdown("---")
    
    start_col1, start_col2 = st.columns([4, 1])
    with start_col2:
        st.button("Let's Start!", on_click=next_step, use_container_width=True)

# Step 2: File Upload
elif st.session_state.step == 2:
    st.title("Upload Your Data")
    
    st.markdown("""
    ### Please upload your contractor workforce CSV file
    
    The application supports the Time tracking system CSV format with columns for:
    - Contractor
    - Person/Name
    - Start/End Times
    - Role/Job Title
    - Area (Site/Welfare)
    """)
    
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    
    if uploaded_file is not None:
        try:
            with st.spinner("Processing data..."):
                # Save the file name
                st.session_state.file_name = uploaded_file.name
                
                # Read and process data
                # Try with and without headers, and different separators
                try:
                    df = pd.read_csv(uploaded_file)
                except:
                    try:
                        df = pd.read_csv(uploaded_file, sep=';')
                    except:
                        try:
                            # Try without headers (common for exported reports)
                            df = pd.read_csv(uploaded_file, header=None)
                            # The process_data function will try to assign columns
                        except:
                            st.error("Could not parse the CSV file. Please check the format.")
                            raise
                
                # Store the raw data
                st.session_state.raw_data = df
                
                # Process data through our utility function
                processed_data = process_data(df)
                st.session_state.data = processed_data
                
                st.success(f"Successfully loaded {uploaded_file.name}")
                
                # Show a preview of the processed data
                st.subheader("Processed Data Preview")
                st.dataframe(processed_data.head(5), use_container_width=True)
                
                # Also show the original data preview
                with st.expander("View Raw Data Preview"):
                    st.dataframe(df.head(5), use_container_width=True)
                
                # Continue button
                st.button("Continue to Visualization", on_click=next_step, use_container_width=True)
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
            st.code(str(e))
    
    # Navigation buttons
    cols = st.columns([1, 4, 1])
    with cols[0]:
        st.button("← Back", on_click=prev_step)

# Step 3: Visualization
elif st.session_state.step == 3:
    if 'data' not in st.session_state:
        st.error("No data available. Please upload a CSV file first.")
        st.button("Go to Upload", on_click=lambda: setattr(st.session_state, 'step', 2))
    else:
        st.title("Workforce Visualization")
        
        # Show file name
        st.caption(f"Data source: {st.session_state.file_name}")
        
        # Process data for visualization
        try:
            df = st.session_state.data
            
            # Create tabs for different visualizations
            tab1, tab2, tab3, tab4 = st.tabs([
                "Workers per Week", 
                "Contractor Comparison", 
                "Role Distribution",
                "Area Analysis (Site/Welfare)"
            ])
            
            with tab1:
                st.subheader("Total Workers Per ISO Week by Contractor")
                
                # Get unique contractors for filtering
                contractors = df['Contractor'].unique().tolist()
                selected_contractor = st.selectbox("Select Contractor", options=contractors)
                
                # Filter data by selected contractor
                filtered_df = df[df['Contractor'] == selected_contractor]
                
                # Sort ISO weeks chronologically
                all_weeks = filtered_df['ISO Week'].unique().tolist()
                sorted_weeks = sort_iso_weeks(all_weeks)
                
                # Apply sorting to the dataframe
                if sorted_weeks:
                    week_order = {week: i for i, week in enumerate(sorted_weeks)}
                    filtered_df['Week_Order'] = filtered_df['ISO Week'].map(week_order)
                    filtered_df = filtered_df.sort_values('Week_Order')
                
                # Create visualization with Plotly
                fig = px.bar(
                    filtered_df, 
                    x='ISO Week', 
                    y='Number of Workers',
                    color='Role',
                    title=f"Total Workers Per ISO Week for {selected_contractor}",
                    color_discrete_sequence=get_color_palette(),
                    barmode='stack',
                    category_orders={"ISO Week": sorted_weeks} if sorted_weeks else None
                )
                
                # Customize figure layout
                fig.update_layout(
                    template="plotly_dark",
                    paper_bgcolor="#0e1117",
                    plot_bgcolor="#0e1117",
                    font=dict(family="Roboto", size=14, color="#ffffff"),
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="center",
                        x=0.5,
                        bgcolor="rgba(0,0,0,0)"
                    ),
                    margin=dict(l=20, r=20, t=60, b=20),
                    xaxis=dict(
                        gridcolor="#1f2630",
                        title_font=dict(size=16)
                    ),
                    yaxis=dict(
                        gridcolor="#1f2630",
                        title_font=dict(size=16)
                    ),
                )
                
                # Make the graph interactive and responsive
                st.plotly_chart(fig, use_container_width=True)
                
                # Additional metadata
                peak_workforce = filtered_df.groupby('ISO Week')['Number of Workers'].sum().max()
                avg_workforce = filtered_df.groupby('ISO Week')['Number of Workers'].sum().mean()
                
                st.markdown(f"""
                **Summary for {selected_contractor}:**
                - Peak workforce: {peak_workforce} workers
                - Average workforce: {avg_workforce:.1f} workers per week
                - Number of roles: {filtered_df['Role'].nunique()}
                """)
            
            with tab2:
                st.subheader("Contractor Comparison")
                
                # Get unique contractors
                all_contractors = df['Contractor'].unique().tolist()
                selected_contractors = st.multiselect(
                    "Select Contractors to Compare", 
                    options=all_contractors,
                    default=all_contractors[:3] if len(all_contractors) > 3 else all_contractors
                )
                
                if selected_contractors:
                    # Filter data for selected contractors
                    multi_contractor_df = df[df['Contractor'].isin(selected_contractors)]
                    
                    # Process data for visualization
                    comparison_data = []
                    for contractor in selected_contractors:
                        contractor_df = multi_contractor_df[multi_contractor_df['Contractor'] == contractor]
                        weekly_sums = contractor_df.groupby('ISO Week')['Number of Workers'].sum().reset_index()
                        weekly_sums['Contractor'] = contractor
                        comparison_data.append(weekly_sums)
                    
                    comparison_df = pd.concat(comparison_data)
                    
                    # Sort ISO weeks chronologically
                    all_weeks = comparison_df['ISO Week'].unique().tolist()
                    sorted_weeks = sort_iso_weeks(all_weeks)
                    
                    # Create line chart
                    fig = px.line(
                        comparison_df,
                        x='ISO Week',
                        y='Number of Workers',
                        color='Contractor',
                        title="Workforce Comparison by Contractor",
                        color_discrete_sequence=get_color_palette(),
                        markers=True,
                        line_shape='linear',
                        category_orders={"ISO Week": sorted_weeks} if sorted_weeks else None
                    )
                    
                    # Customize figure layout
                    fig.update_layout(
                        template="plotly_dark",
                        paper_bgcolor="#0e1117",
                        plot_bgcolor="#0e1117",
                        font=dict(family="Roboto", size=14, color="#ffffff"),
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="center",
                            x=0.5,
                            bgcolor="rgba(0,0,0,0)"
                        ),
                        margin=dict(l=20, r=20, t=60, b=20),
                        xaxis=dict(gridcolor="#1f2630"),
                        yaxis=dict(gridcolor="#1f2630")
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Summary statistics
                    contractor_stats = comparison_df.groupby('Contractor')['Number of Workers'].agg(['mean', 'max']).reset_index()
                    contractor_stats.columns = ['Contractor', 'Average Workers', 'Peak Workers']
                    contractor_stats = contractor_stats.sort_values('Peak Workers', ascending=False)
                    
                    st.subheader("Contractor Statistics")
                    st.dataframe(contractor_stats, use_container_width=True)
                else:
                    st.info("Please select at least one contractor to display the comparison chart.")
            
            with tab3:
                st.subheader("Role Distribution Analysis")
                
                # Get unique contractors for filtering
                contractors = df['Contractor'].unique().tolist()
                selected_contractor = st.selectbox("Select Contractor", options=contractors, key="role_dist_contractor")
                
                # Filter data by selected contractor
                filtered_df = df[df['Contractor'] == selected_contractor]
                
                # Process data for visualization of role distribution
                role_data = filtered_df.groupby('Role')['Number of Workers'].sum().reset_index()
                
                # Create pie chart
                fig = px.pie(
                    role_data,
                    values='Number of Workers',
                    names='Role',
                    title=f"Role Distribution for {selected_contractor}",
                    color_discrete_sequence=get_color_palette(),
                    hole=0.4
                )
                
                # Customize figure layout
                fig.update_layout(
                    template="plotly_dark",
                    paper_bgcolor="#0e1117",
                    plot_bgcolor="#0e1117",
                    font=dict(family="Roboto", size=14, color="#ffffff"),
                    legend=dict(
                        orientation="h",
                        yanchor="top",
                        y=-0.1,
                        xanchor="center",
                        x=0.5,
                        bgcolor="rgba(0,0,0,0)"
                    ),
                    margin=dict(l=20, r=20, t=60, b=100)
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Role trends over time
                st.subheader("Role Trends Over Time")
                
                # Sort ISO weeks chronologically
                all_weeks = filtered_df['ISO Week'].unique().tolist()
                sorted_weeks = sort_iso_weeks(all_weeks)
                
                # Create line chart for role trends
                fig = px.line(
                    filtered_df,
                    x='ISO Week',
                    y='Number of Workers',
                    color='Role',
                    title=f"Role Trends for {selected_contractor}",
                    color_discrete_sequence=get_color_palette(),
                    markers=True,
                    category_orders={"ISO Week": sorted_weeks} if sorted_weeks else None
                )
                
                # Customize figure layout
                fig.update_layout(
                    template="plotly_dark",
                    paper_bgcolor="#0e1117",
                    plot_bgcolor="#0e1117",
                    font=dict(family="Roboto", size=14, color="#ffffff"),
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="center",
                        x=0.5,
                        bgcolor="rgba(0,0,0,0)"
                    ),
                    margin=dict(l=20, r=20, t=60, b=20),
                    xaxis=dict(gridcolor="#1f2630"),
                    yaxis=dict(gridcolor="#1f2630")
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            with tab4:
                st.subheader("Area Analysis (Site vs. Welfare)")
                
                # Check if we have area data in the raw data
                if 'raw_data' in st.session_state and 'Area' in st.session_state.raw_data.columns:
                    raw_df = st.session_state.raw_data
                    
                    # Get unique contractors for filtering
                    contractors = raw_df['Contractor'].unique().tolist()
                    selected_contractor = st.selectbox("Select Contractor", options=contractors, key="area_analysis_contractor")
                    
                    # Filter by contractor
                    filtered_raw_df = raw_df[raw_df['Contractor'] == selected_contractor]
                    
                    # Get unique areas
                    areas = filtered_raw_df['Area'].unique().tolist()
                    
                    if 'Site' in areas and 'Welfare' in areas:
                        # Create a column for Date (day only)
                        if 'StartTime' in filtered_raw_df.columns:
                            try:
                                filtered_raw_df['Date'] = pd.to_datetime(filtered_raw_df['StartTime']).dt.date
                            except:
                                # Try to extract date using regex
                                filtered_raw_df['Date'] = filtered_raw_df['StartTime'].str.extract(r'(\d{1,2}/\d{1,2}/\d{4})')[0]
                        
                        # Group by Date and Area and sum Duration
                        if 'Date' in filtered_raw_df.columns and 'Duration' in filtered_raw_df.columns:
                            # Convert Duration to numeric
                            filtered_raw_df['Duration'] = pd.to_numeric(filtered_raw_df['Duration'], errors='coerce')
                            
                            # Group by Date and Area
                            area_time = filtered_raw_df.groupby(['Date', 'Area'])['Duration'].sum().reset_index()
                            
                            # Pivot to get areas as columns
                            area_pivot = area_time.pivot(index='Date', columns='Area', values='Duration').reset_index()
                            
                            # Fill NaN with 0
                            area_pivot = area_pivot.fillna(0)
                            
                            # Ensure we have both Site and Welfare columns
                            if 'Site' not in area_pivot.columns:
                                area_pivot['Site'] = 0
                            if 'Welfare' not in area_pivot.columns:
                                area_pivot['Welfare'] = 0
                            
                            # Calculate total and percentages
                            area_pivot['Total'] = area_pivot['Site'] + area_pivot['Welfare']
                            area_pivot['Site %'] = area_pivot['Site'] / area_pivot['Total'] * 100
                            area_pivot['Welfare %'] = area_pivot['Welfare'] / area_pivot['Total'] * 100
                            
                            # Create a stacked bar chart
                            fig = px.bar(
                                area_pivot,
                                x='Date',
                                y=['Site', 'Welfare'],
                                title=f"Time Spent in Site vs. Welfare Areas for {selected_contractor}",
                                color_discrete_sequence=get_color_palette(),
                                barmode='stack'
                            )
                            
                            # Customize figure layout
                            fig.update_layout(
                                template="plotly_dark",
                                paper_bgcolor="#0e1117",
                                plot_bgcolor="#0e1117",
                                font=dict(family="Roboto", size=14, color="#ffffff"),
                                legend=dict(
                                    orientation="h",
                                    yanchor="bottom",
                                    y=1.02,
                                    xanchor="center",
                                    x=0.5,
                                    bgcolor="rgba(0,0,0,0)"
                                ),
                                margin=dict(l=20, r=20, t=60, b=20),
                                xaxis=dict(gridcolor="#1f2630"),
                                yaxis=dict(gridcolor="#1f2630", title="Minutes")
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Summary statistics
                            total_site = area_pivot['Site'].sum()
                            total_welfare = area_pivot['Welfare'].sum()
                            total_time = total_site + total_welfare
                            
                            site_percent = (total_site / total_time * 100) if total_time > 0 else 0
                            welfare_percent = (total_welfare / total_time * 100) if total_time > 0 else 0
                            
                            # Create two columns for the summary
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.metric("Total Site Time (minutes)", f"{total_site:.0f}", f"{site_percent:.1f}%")
                            
                            with col2:
                                st.metric("Total Welfare Time (minutes)", f"{total_welfare:.0f}", f"{welfare_percent:.1f}%")
                            
                            # Pie chart for overall distribution
                            area_summary = pd.DataFrame({
                                'Area': ['Site', 'Welfare'],
                                'Minutes': [total_site, total_welfare]
                            })
                            
                            fig = px.pie(
                                area_summary,
                                values='Minutes',
                                names='Area',
                                title=f"Overall Area Distribution for {selected_contractor}",
                                color_discrete_sequence=get_color_palette(),
                                hole=0.4
                            )
                            
                            fig.update_layout(
                                template="plotly_dark",
                                paper_bgcolor="#0e1117",
                                plot_bgcolor="#0e1117",
                                font=dict(family="Roboto", size=14, color="#ffffff")
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Display the data table
                            with st.expander("View Area Data by Date"):
                                st.dataframe(area_pivot, use_container_width=True)
                        
                        else:
                            st.warning("Required columns for area analysis (Date and Duration) not found in the data.")
                    else:
                        st.info("Site and Welfare areas not found in the data.")
                else:
                    st.info("Area data not available in the uploaded file. This tab requires data with an 'Area' column that identifies 'Site' and 'Welfare' areas.")
                    
                    # Show a sample of the expected format
                    st.markdown("""
                    ### Expected Data Format for Area Analysis
                    
                    The CSV should include columns for:
                    - **Contractor**: The name of the contractor
                    - **Area**: Specifically with values 'Site' and 'Welfare'
                    - **StartTime**: The start time/date of the activity
                    - **Duration**: The duration of the activity in minutes
                    
                    Example:
                    ```
                    Contractor,Person,StartTime,EndTime,Area,Duration
                    Allelys,John Smith,13/06/2024 11:27,13/06/2024 11:39,Site,12
                    Allelys,John Smith,13/06/2024 11:39,13/06/2024 13:08,Welfare,89
                    ```
                    """)
        
        except Exception as e:
            st.error(f"Error generating visualizations: {str(e)}")
            st.code(str(e))
        
        # Navigation buttons
        cols = st.columns([1, 3, 1])
        with cols[0]:
            st.button("← Back to Upload", on_click=lambda: setattr(st.session_state, 'step', 2))
        with cols[2]:
            st.button("Start Over", on_click=reset_app)

# Footer
st.markdown("---")
st.caption("© 2023 Contractor Workforce Analyzer | No data is stored in the cloud") 