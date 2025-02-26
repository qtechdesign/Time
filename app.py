import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np
import os
from utils import process_data, get_color_palette, sort_iso_weeks
import base64

# Page configuration
st.set_page_config(
    page_title="Kanadevia Time Tracker",
    page_icon="⏱️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Add clipboard.js and modern clipboard API for graph copying
st.markdown("""
<script src="https://cdnjs.cloudflare.com/ajax/libs/clipboard.js/2.0.8/clipboard.min.js"></script>
<script>
// Function to initialize clipboard functionality
function initClipboard() {
    try {
        // Try to initialize clipboard.js
        var clipboard = new ClipboardJS('.copy-btn');
        console.log('Clipboard.js initialized');
        
        clipboard.on('success', function(e) {
            console.log('Copy success via clipboard.js');
            showSuccessMessage(e.trigger.getAttribute('data-target'));
            e.clearSelection();
        });
        
        clipboard.on('error', function(e) {
            console.log('Clipboard.js failed, trying navigator.clipboard API');
            // Try the modern clipboard API as fallback
            tryNavigatorClipboard(e.trigger);
        });
    } catch (err) {
        console.error('Error initializing clipboard:', err);
    }
}

// Function to try the modern navigator.clipboard API
function tryNavigatorClipboard(buttonElement) {
    if (!buttonElement || !navigator.clipboard) {
        console.error('Modern clipboard API not available');
        alert('Copying failed. Please use the download button instead.');
        return;
    }
    
    var imageUrl = buttonElement.getAttribute('data-clipboard-text');
    
    // Fetch the image and copy it using the modern API
    fetch(imageUrl)
        .then(response => response.blob())
        .then(blob => {
            try {
                // For browsers supporting clipboard.write
                if (navigator.clipboard.write) {
                    navigator.clipboard.write([
                        new ClipboardItem({
                            'image/png': blob
                        })
                    ]).then(function() {
                        console.log('Image copied via navigator.clipboard.write');
                        showSuccessMessage(buttonElement.getAttribute('data-target'));
                    }).catch(function(err) {
                        console.error('navigator.clipboard.write failed:', err);
                        alert('Copying failed. Please use the download button instead.');
                    });
                } else {
                    alert('Direct image copying not supported in this browser. Please use the download button.');
                }
            } catch (err) {
                console.error('Modern clipboard operation failed:', err);
                alert('Copying failed. Please use the download button instead.');
            }
        })
        .catch(err => {
            console.error('Failed to fetch image for clipboard:', err);
            alert('Copying failed. Please use the download button instead.');
        });
}

// Function to show success message
function showSuccessMessage(targetId) {
    var successMsg = document.getElementById('copy-success-' + targetId);
    if(successMsg) {
        successMsg.style.display = 'block';
        setTimeout(function() {
            successMsg.style.display = 'none';
        }, 2000);
    }
}

// Initialize clipboard when DOM is loaded and periodically check for new buttons
document.addEventListener('DOMContentLoaded', function() {
    // Initial initialization
    setTimeout(initClipboard, 1000);
    
    // Periodically reinitialize to catch dynamically added buttons
    setInterval(initClipboard, 3000);
});
</script>
<style>
.chart-action-container {
    display: flex;
    gap: 10px;
    margin: 10px 0;
    flex-wrap: wrap;
}
.copy-btn, .download-btn {
    background-color: #4a86e8;
    color: white;
    border: none;
    padding: 8px 15px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
    text-align: center;
    flex: 1;
    min-width: 150px;
    max-width: 200px;
    transition: background-color 0.3s;
    text-decoration: none;
    display: inline-block;
}
.download-btn {
    background-color: #36B37E;
}
.copy-btn:hover {
    background-color: #3a76d8;
}
.download-btn:hover {
    background-color: #2d9669;
}
.copy-success {
    color: #36B37E;
    display: none;
    margin-top: 5px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# Check for kaleido package for image export
try:
    import kaleido
    KALEIDO_AVAILABLE = True
except ImportError:
    KALEIDO_AVAILABLE = False
    st.warning("⚠️ Chart copying feature requires the kaleido package. Install with: `pip install -U kaleido`")

# Custom function to add copy button for Plotly charts
def add_copy_button_to_chart(fig, title="Chart"):
    """Add buttons to copy or download the chart as an image"""
    if not KALEIDO_AVAILABLE:
        st.warning("📌 Chart export features require the kaleido package. Install with: `pip install -U kaleido`")
        return
        
    try:
        # Generate a unique ID for this chart
        import uuid
        chart_id = str(uuid.uuid4())[:8]
        
        # Convert chart to base64 image with higher quality
        try:
            img_bytes = fig.to_image(format="png", scale=3, width=1200, height=800)
            img_b64 = base64.b64encode(img_bytes).decode()
            img_data_url = f"data:image/png;base64,{img_b64}"
        except Exception as e:
            st.warning(f"Error generating image: {str(e)}")
            return
        
        # Create HTML with both copy and download buttons - SIMPLIFIED VERSION
        buttons_html = f"""
        <div class="chart-action-container">
            <button 
                class="copy-btn" 
                data-clipboard-text="{img_data_url}"
                data-target="{chart_id}"
            >
                📋 Copy to Clipboard
            </button>
            
            <a 
                href="{img_data_url}" 
                download="{title.replace(' ', '_')}.png" 
                class="download-btn"
            >
                💾 Download PNG
            </a>
        </div>
        <div id="copy-success-{chart_id}" class="copy-success">
            ✅ Chart copied to clipboard!
        </div>
        """
        
        # Use components.html instead of st.markdown for better HTML rendering
        import streamlit.components.v1 as components
        components.html(buttons_html, height=80)
    except Exception as e:
        st.warning(f"Unable to generate chart action buttons: {str(e)}")
        st.code(str(e))

# Custom CSS for dark mode and sleeker design - REMOVE ANIMATIONS
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
    
    /* Fix for overlapping legends */
    .js-plotly-plot .plotly .legend {
        padding: 10px 0;
    }
    
    /* Add space for legends */
    .plot-container {
        margin-top: 30px !important;
    }

    .copy-btn, .download-btn {
        background-color: #4a86e8;
        color: white;
        border: none;
        padding: 5px 10px;
        margin: 5px;
        border-radius: 4px;
        cursor: pointer;
        font-size: 12px;
        text-decoration: none;
        display: inline-block;
    }
    .copy-btn:hover, .download-btn:hover {
        background-color: #5c92e8;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for contractor selections
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'selected_contractors' not in st.session_state:
    st.session_state.selected_contractors = []
if 'selected_contractor' not in st.session_state:
    st.session_state.selected_contractor = None
if 'time_analysis_contractor' not in st.session_state:
    st.session_state.time_analysis_contractor = None
if 'role_dist_contractor' not in st.session_state:
    st.session_state.role_dist_contractor = None
if 'role_colors' not in st.session_state:
    st.session_state.role_colors = {}  # For consistent role coloring
if 'allow_multiple_selection' not in st.session_state:
    st.session_state.allow_multiple_selection = True  # Changed from False to True to enable by default

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
    if 'selected_contractor' in st.session_state:
        del st.session_state.selected_contractor
    if 'selected_contractors' in st.session_state:
        del st.session_state.selected_contractors
    if 'time_analysis_contractor' in st.session_state:
        del st.session_state.time_analysis_contractor
    if 'role_dist_contractor' in st.session_state:
        del st.session_state.role_dist_contractor
    if 'allow_multiple_selection' in st.session_state:
        del st.session_state.allow_multiple_selection

# Callback functions for contractor selection
def update_selected_contractor():
    # When allow_multiple_selection is True, use multiselect values
    if st.session_state.allow_multiple_selection:
        st.session_state.selected_contractors = st.session_state.contractor_multiselect
        if len(st.session_state.selected_contractors) > 0:
            st.session_state.selected_contractor = st.session_state.selected_contractors[0]
        else:
            st.session_state.selected_contractor = None
    else:
        # When using single select
        st.session_state.selected_contractor = st.session_state.contractor_select
        st.session_state.selected_contractors = [st.session_state.selected_contractor] if st.session_state.selected_contractor else []
    
    # Sync all contractor selections
    st.session_state.time_analysis_contractor = st.session_state.selected_contractor
    st.session_state.role_dist_contractor = st.session_state.selected_contractor

def toggle_multiple_selection():
    st.session_state.allow_multiple_selection = not st.session_state.allow_multiple_selection
    # If turning off multiple selection and we have contractors selected,
    # keep only the first one as the selected contractor
    if not st.session_state.allow_multiple_selection and st.session_state.selected_contractors:
        st.session_state.selected_contractor = st.session_state.selected_contractors[0]
    else:
        # If turning on multiple selection, initialize with current selection
        if st.session_state.selected_contractor:
            st.session_state.selected_contractors = [st.session_state.selected_contractor]

# Unified contractor selection function for all tabs
def select_contractor(location, default_contractor=None, key_prefix=""):
    contractors = st.session_state.data['Contractor'].unique().tolist()
    
    if not contractors:
        location.error("No contractors found in the data. Please check your CSV format.")
        return None
    
    # Initialize selected_contractor if it's None
    if st.session_state.selected_contractor is None or st.session_state.selected_contractor not in contractors:
        st.session_state.selected_contractor = contractors[0]
        st.session_state.selected_contractors = [contractors[0]]
    
    # Define building services contractors to always include if available
    building_services = ["Argus Fire", "Emico", "Greenwood Louvres", "Sotham Engineering", "Ronzoni"]
    available_building_services = [c for c in contractors if c in building_services]
    
    # If no selection yet or we're at the initial load, use building services contractors if available
    if not st.session_state.selected_contractors or set(st.session_state.selected_contractors) != set(available_building_services):
        if available_building_services:
            # Always include all available building services contractors
            default_selection = available_building_services
        else:
            # Get top contractors by unique worker count
            contractor_workers = {}
            for contractor in contractors:
                contractor_data = st.session_state.raw_data[st.session_state.raw_data['Contractor'] == contractor] if 'Contractor' in st.session_state.raw_data.columns else st.session_state.raw_data
                contractor_workers[contractor] = calculate_unique_workers(contractor_data)
            
            # Get top 5 contractors
            top_contractors = sorted(contractor_workers.items(), key=lambda x: x[1], reverse=True)[:5]
            default_selection = [c[0] for c in top_contractors]
    else:
        # Use current selection
        default_selection = st.session_state.selected_contractors
        
    # Ensure default selection only includes valid contractors
    default_selection = [c for c in default_selection if c in contractors]
    if not default_selection and contractors:
        default_selection = [contractors[0]]
    
    # Use multiselect similar to Contractor Comparison tab
    selected = location.multiselect(
        "Select Contractor(s)", 
        options=contractors,
        default=default_selection,
        key=f"{key_prefix}_contractor_multiselect"
    )
    
    # Store in session state
    st.session_state.selected_contractors = selected
    if selected:
        st.session_state.selected_contractor = selected[0]
    else:
        st.session_state.selected_contractor = None
    
    # Sync all contractor selections
    st.session_state.time_analysis_contractor = st.session_state.selected_contractor
    st.session_state.role_dist_contractor = st.session_state.selected_contractor
    
    return selected

# Calculate unique workers in the dataset
def calculate_unique_workers(raw_df):
    """Calculate the total number of unique workers across the entire dataset"""
    if 'Worker Name' in raw_df.columns:
        # If we have Worker ID as well, use both for uniqueness
        if 'Worker ID' in raw_df.columns:
            unique_identifiers = raw_df['Worker Name'] + '_' + raw_df['Worker ID'].astype(str)
        else:
            unique_identifiers = raw_df['Worker Name']
        
        return unique_identifiers.nunique()
    elif 'Bio ID' in raw_df.columns:
        return raw_df['Bio ID'].nunique()
    else:
        # Try to find person-like columns
        person_cols = [col for col in raw_df.columns if any(p in col.lower() for p in ['name', 'worker', 'person', 'employee'])]
        if person_cols:
            return raw_df[person_cols[0]].nunique()
        
        # Fallback to whatever is available
        return len(raw_df)

# Function to process data to ensure unique worker counts
def process_data_for_unique_workers(df, raw_df, contractor=None):
    """Process dataframe to ensure it reflects unique worker counts"""
    if contractor:
        filtered_raw_df = raw_df[raw_df['Contractor'] == contractor] if 'Contractor' in raw_df.columns else raw_df
        filtered_df = df[df['Contractor'] == contractor]
    else:
        filtered_raw_df = raw_df
        filtered_df = df
    
    # Group by ISO Week and Role, but ensure we're counting unique workers
    result = filtered_df.copy()
    
    # Group by ISO Week and Role, and count unique workers
    if 'Worker Name' in filtered_raw_df.columns and 'Worker ID' in filtered_raw_df.columns and 'ISO Week' in filtered_raw_df.columns and 'Role' in filtered_raw_df.columns:
        # We need to completely recalculate this based on raw data
        # Create unique identifier
        filtered_raw_df['Unique_ID'] = filtered_raw_df['Worker Name'] + '_' + filtered_raw_df['Worker ID'].astype(str)
        
        # Add ISO Week if not present
        if 'ISO Week' not in filtered_raw_df.columns:
            filtered_raw_df['ISO Week'] = filtered_raw_df['In_dt'].dt.strftime('%Y-W%U') if 'In_dt' in filtered_raw_df.columns else 'Unknown'
            
        # Count unique workers by week and role
        unique_counts = filtered_raw_df.groupby(['ISO Week', 'Role'])['Unique_ID'].nunique().reset_index()
        unique_counts.columns = ['ISO Week', 'Role', 'Number of Workers']
        
        return unique_counts
    
    return filtered_df

# Create a consistent color mapping for roles
def get_consistent_role_colors(df):
    """Create a consistent color mapping for all roles in the dataset"""
    if 'role_colors' not in st.session_state or not st.session_state.role_colors:
        all_roles = df['Role'].unique().tolist()
        # Use get_color_palette without parameters and get enough colors for all roles
        palette = get_color_palette()
        # Make sure we have enough colors for all roles by repeating the palette if needed
        while len(palette) < len(all_roles):
            palette.extend(palette)
        palette = palette[:len(all_roles)]
        st.session_state.role_colors = {role: color for role, color in zip(all_roles, palette)}
    return st.session_state.role_colors

# Helper function to display key facts about the dataset - REMOVE ANIMATIONS
def display_key_facts(df, raw_df):
    """Display key facts and summary statistics about the dataset"""
    st.subheader("📊 Key Facts Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_unique_workers = calculate_unique_workers(raw_df)
        st.markdown(f"""
        <div>
            <h3>Total Unique Workers</h3>
            <h1>{total_unique_workers} 👷</h1>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        total_contractors = df['Contractor'].nunique()
        st.markdown(f"""
        <div>
            <h3>Total Contractors</h3>
            <h1>{total_contractors} 🏢</h1>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        total_roles = df['Role'].nunique()
        st.markdown(f"""
        <div>
            <h3>Unique Roles</h3>
            <h1>{total_roles} 🛠️</h1>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        if 'ISO Week' in df.columns:
            weeks = df['ISO Week'].nunique()
            st.markdown(f"""
            <div>
                <h3>Weeks of Data</h3>
                <h1>{weeks} 📅</h1>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div>
                <h3>Total Records</h3>
                <h1>{len(raw_df)} 📄</h1>
            </div>
            """, unsafe_allow_html=True)
    
    # Additional summary data
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Top 10 Contractors by Unique Worker Count")
        # Calculate unique workers per contractor
        contractor_workers = {}
        for contractor in df['Contractor'].unique():
            contractor_data = raw_df[raw_df['Contractor'] == contractor] if 'Contractor' in raw_df.columns else raw_df
            contractor_workers[contractor] = calculate_unique_workers(contractor_data)
        
        # Convert to DataFrame and sort
        top_contractors_df = pd.DataFrame({
            'Contractor': list(contractor_workers.keys()),
            'Unique Workers': list(contractor_workers.values())
        }).sort_values('Unique Workers', ascending=False).head(10)
        
        # Create a horizontal bar chart
        fig = px.bar(
            y=top_contractors_df['Contractor'],
            x=top_contractors_df['Unique Workers'],
            orientation='h',
            title="Top Contractors by Unique Workers",
            color=top_contractors_df['Unique Workers'],
            color_continuous_scale=px.colors.sequential.Viridis,
            labels={'y': 'Contractor', 'x': 'Unique Workers'}
        )
        
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0e1117",
            plot_bgcolor="#0e1117",
            height=400,  # Increased height to fit more contractors
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
        add_copy_button_to_chart(fig, "Top Contractors by Unique Workers")
        
        # Display all contractors on the home page
        st.subheader("All Contractors - Unique Worker Analysis")
        # Create a dataframe with all contractors and their unique worker counts
        all_contractors_df = pd.DataFrame({
            'Contractor': list(contractor_workers.keys()),
            'Unique Workers': list(contractor_workers.values())
        }).sort_values('Unique Workers', ascending=False)
        
        st.dataframe(all_contractors_df, use_container_width=True)
    
    with col2:
        st.subheader("Top 10 Roles by Unique Worker Count")
        # Group by role and count unique workers
        role_counts = df.groupby('Role')['Number of Workers'].sum().sort_values(ascending=False).head(10)
        
        # Create a horizontal bar chart with consistent colors
        role_colors = get_consistent_role_colors(df)
        colors = [role_colors.get(role, "#FF9900") for role in role_counts.index]
        
        fig = px.bar(
            y=role_counts.index,
            x=role_counts.values,
            orientation='h',
            title="Top Roles by Worker Count",
            color=role_counts.index,
            color_discrete_map=role_colors,
            labels={'y': 'Role', 'x': 'Worker Count'}
        )
        
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0e1117",
            plot_bgcolor="#0e1117",
            height=400,  # Increased height to fit more roles
            legend_title_text="",
            showlegend=False  # Hide legend as it's redundant with axis labels
        )
        
        st.plotly_chart(fig, use_container_width=True)
        add_copy_button_to_chart(fig, "Top Roles by Worker Count")

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
    st.title("Kanadevia Time Tracker Analyzer 🚀")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("""
        ## 📊 Visualize your Time Tracker data
        
        Upload your Time Tracker CSV file to analyze:
        
        - 👷 **Worker counts** by contractor and role
        - ⏱️ **Time spent analysis** for Site vs. Welfare
        - 📈 **Contractor comparison** across weeks
        - 👥 **Role distribution** by contractor
        
        Simply upload your Time Tracker export file to begin.
        """)
    
    with col2:
        st.image("https://img.icons8.com/color/240/overtime--v1.png", width=150)
    
    st.markdown("---")
    
    # Combine upload and welcome on the first screen for a more straightforward flow
    uploaded_file = st.file_uploader("Choose a CSV file from Time Tracker", type="csv")
    
    if uploaded_file is not None:
        try:
            with st.spinner("Processing data... ⚙️"):
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
                
                # Calculate and store unique workers count
                st.session_state.unique_workers = calculate_unique_workers(df)
                
                st.success(f"Successfully loaded {uploaded_file.name} ✅")
                
                # Add a continue button right after success message
                st.button("Continue to Visualization 📊", on_click=next_step, key="continue_button_top", use_container_width=True)
                
                # Display key facts about the data
                display_key_facts(processed_data, df)
                
                # Brief data preview and auto-continue to visualizations
                st.subheader("Data Preview")
                display_column_mapping_info(df)
                
                with st.expander("View Processed Data Sample"):
                    st.dataframe(processed_data.head(5), use_container_width=True)
                
                # Continue button (second one at the bottom)
                st.button("Continue to Visualization 📊", on_click=next_step, key="continue_button_bottom", use_container_width=True)
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
        st.title("Kanadevia Time Tracker Analysis 📊")
        
        # Show file name and a reset button in the header
        col1, col2 = st.columns([3, 1])
        with col1:
            st.caption(f"Data source: {st.session_state.file_name}")
        with col2:
            st.button("Load New File 📁", on_click=reset_app, use_container_width=True)
        
        # Process data for visualization
        try:
            df = st.session_state.data
            raw_df = st.session_state.raw_data
            
            # Get consistent role colors to use across all visualizations
            role_colors = get_consistent_role_colors(df)
            
            # Create tabs for different visualizations
            tab1, tab2, tab3, tab4 = st.tabs([
                "👷 Workforce by Week", 
                "⏱️ Site vs. Welfare Time", 
                "📈 Contractor Comparison",
                "👥 Role Distribution"
            ])
            
            # Tab 1: Workers per Week
            with tab1:
                st.subheader("Unique Workers Per Week by Contractor")
                
                # Use the unified contractor selection function
                selected_contractors = select_contractor(st, key_prefix="tab1")
                
                if selected_contractors:
                    # Handle either single or multiple contractors
                    all_filtered_df = []
                    
                    for contractor in selected_contractors:
                        # Get data with unique worker counts
                        filtered_df = process_data_for_unique_workers(df, raw_df, contractor)
                        
                        if not filtered_df.empty:
                            # Add contractor column if multiple contractors selected
                            if len(selected_contractors) > 1:
                                filtered_df['Selected Contractor'] = contractor
                            
                            all_filtered_df.append(filtered_df)
                    
                    if all_filtered_df:
                        # Combine all data
                        combined_df = pd.concat(all_filtered_df, ignore_index=True)
                        
                        # Sort ISO weeks chronologically
                        all_weeks = combined_df['ISO Week'].unique().tolist()
                        sorted_weeks = sort_iso_weeks(all_weeks)
                        
                        # Create visualization with Plotly using consistent role colors
                        if len(selected_contractors) > 1:
                            # If multiple contractors, group by contractor and ISO Week
                            fig = px.bar(
                                combined_df, 
                                x='ISO Week', 
                                y='Number of Workers',
                                color='Selected Contractor',
                                title=f"Unique Workers per Week for {len(selected_contractors)} Contractors",
                                barmode='group',
                                category_orders={"ISO Week": sorted_weeks} if sorted_weeks else None
                            )
                        else:
                            # Single contractor - use role breakdown
                            fig = px.bar(
                                combined_df, 
                                x='ISO Week', 
                                y='Number of Workers',
                                color='Role',
                                title=f"Unique Workers per Week for {selected_contractors[0]}",
                                color_discrete_map=role_colors,
                                barmode='stack',
                                category_orders={"ISO Week": sorted_weeks} if sorted_weeks else None
                            )
                        
                        # Update y-axis title to clarify these are unique workers
                        fig.update_layout(
                            yaxis_title="Unique Worker Count",
                        )
                        
                        # Customize figure layout - FIX LEGEND OVERLAP
                        fig.update_layout(
                            template="plotly_dark",
                            paper_bgcolor="#0e1117",
                            plot_bgcolor="#0e1117",
                            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
                            margin=dict(l=20, r=20, t=80, b=20),  # Increased top margin for legend
                            legend_title_text="",
                            title=dict(y=0.95)  # Move title up to make room for legend
                        )
                        
                        # Display the chart
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Add copy button
                        if len(selected_contractors) == 1:
                            chart_title = f"Unique Workers per Week for {selected_contractors[0]}"
                        else:
                            chart_title = f"Unique Workers per Week Comparison"
                        add_copy_button_to_chart(fig, chart_title)
                        
                        # If only one contractor is selected, show detailed statistics
                        if len(selected_contractors) == 1:
                            # Summary statistics with animation
                            col1, col2, col3 = st.columns(3)
                            
                            # Get worker count info
                            contractor = selected_contractors[0]
                            filtered_raw_df = raw_df[raw_df['Contractor'] == contractor] if 'Contractor' in raw_df.columns else raw_df
                            
                            with col1:
                                unique_workers = calculate_unique_workers(filtered_raw_df)
                                st.markdown(f"""
                                <div>
                                    <h3>Total Unique Workers</h3>
                                    <h1>{unique_workers} 👷</h1>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            with col2:
                                peak_week = combined_df.groupby('ISO Week')['Number of Workers'].sum().idxmax()
                                peak = combined_df.groupby('ISO Week')['Number of Workers'].sum().max()
                                st.metric("Peak Week", f"{peak_week}: {peak} unique workers")
                            
                            with col3:
                                unique_roles = combined_df['Role'].nunique()
                                st.metric("Unique Roles 🛠️", f"{unique_roles}")
                        else:
                            # Show summary comparison for multiple contractors
                            st.subheader("Contractor Comparison Summary")
                            
                            # Create summary dataframe
                            summary_data = []
                            for contractor in selected_contractors:
                                contractor_df = combined_df[combined_df['Selected Contractor'] == contractor]
                                filtered_raw_df = raw_df[raw_df['Contractor'] == contractor] if 'Contractor' in raw_df.columns else raw_df
                                
                                summary_data.append({
                                    "Contractor": contractor,
                                    "Total Unique Workers": calculate_unique_workers(filtered_raw_df),
                                    "Peak Week Workers": contractor_df.groupby('ISO Week')['Number of Workers'].sum().max(),
                                    "Unique Roles": contractor_df['Role'].nunique() if 'Role' in contractor_df.columns else 0
                                })
                            
                            summary_df = pd.DataFrame(summary_data)
                            st.dataframe(summary_df, use_container_width=True)
                    else:
                        st.warning(f"No data available for the selected contractor(s)")
                else:
                    st.info("Please select at least one contractor")
            
            # Tab 2: Time Analysis (Site/Welfare) - Enhanced version
            with tab2:
                st.subheader("Time Spent Analysis (Site vs. Welfare)")
                
                # Check if we have area data
                if 'Area' not in raw_df.columns:
                    st.info("No Area column found in the data. This analysis requires an 'Area' column to distinguish between Site and Welfare areas.")
                else:
                    # Get available contractors
                    contractors = raw_df['Contractor'].unique().tolist()
                    
                    # Check if Emico is in the data and set it as default
                    default_contractor = "Emico" if "Emico" in contractors else None
                    
                    # For this tab, we'll use a simple selectbox since only one contractor can be displayed
                    selected_contractor = st.selectbox(
                        "Select Contractor",
                        options=contractors,
                        index=contractors.index(default_contractor) if default_contractor in contractors else 0,
                        key="time_analysis_selectbox"
                    )
                    
                    if selected_contractor:
                        # Filter data for selected contractor
                        filtered_raw_df = raw_df[raw_df['Contractor'] == selected_contractor]
                        
                        # Check for required columns
                        if 'In' in filtered_raw_df.columns and 'Out' in filtered_raw_df.columns and 'Area' in filtered_raw_df.columns:
                            # Calculate time spent in each area
                            try:
                                # Convert In/Out to datetime
                                filtered_raw_df = filtered_raw_df.copy()  # Make a proper copy to avoid SettingWithCopyWarning
                                filtered_raw_df.loc[:, 'In_dt'] = pd.to_datetime(filtered_raw_df['In'], errors='coerce')
                                filtered_raw_df.loc[:, 'Out_dt'] = pd.to_datetime(filtered_raw_df['Out'], errors='coerce')
                                
                                # Calculate duration (if Total Minutes not available)
                                if 'Total Minutes' in filtered_raw_df.columns:
                                    filtered_raw_df.loc[:, 'Duration'] = pd.to_numeric(filtered_raw_df['Total Minutes'], errors='coerce')
                                else:
                                    filtered_raw_df.loc[:, 'Duration'] = (filtered_raw_df['Out_dt'] - filtered_raw_df['In_dt']).dt.total_seconds() / 60
                                
                                # Extract date from In time and create ISO Week column for consistency
                                filtered_raw_df.loc[:, 'Date'] = filtered_raw_df['In_dt'].dt.date
                                filtered_raw_df.loc[:, 'ISO Week'] = filtered_raw_df['In_dt'].dt.strftime('%Y-W%U')
                                
                                # Group by ISO Week and Area (instead of Date), sum duration
                                time_analysis = filtered_raw_df.groupby(['ISO Week', 'Area'])['Duration'].sum().reset_index()
                                
                                # Identify available areas
                                areas = time_analysis['Area'].unique()
                                site_area = [a for a in areas if 'site' in a.lower()]
                                site_area = site_area[0] if site_area else 'Site' if 'Site' in areas else None
                                welfare_area = [a for a in areas if 'welfare' in a.lower()]
                                welfare_area = welfare_area[0] if welfare_area else 'Welfare' if 'Welfare' in areas else None
                                
                                if site_area or welfare_area:
                                    # Pivot to get areas as columns - using ISO Week instead of Date
                                    area_pivot = time_analysis.pivot(index='ISO Week', columns='Area', values='Duration').reset_index()
                                    
                                    # Fill NaN with 0
                                    area_pivot = area_pivot.fillna(0)
                                    
                                    # Calculate total and ensure site/welfare columns exist
                                    if site_area and site_area not in area_pivot.columns:
                                        area_pivot[site_area] = 0
                                    if welfare_area and welfare_area not in area_pivot.columns:
                                        area_pivot[welfare_area] = 0
                                    
                                    # Calculate totals and percentages
                                    area_columns = [col for col in area_pivot.columns if col != 'ISO Week']
                                    area_pivot['Total'] = area_pivot[area_columns].sum(axis=1)
                                    
                                    # Sort ISO weeks chronologically
                                    sorted_weeks = sort_iso_weeks(area_pivot['ISO Week'].unique().tolist())
                                    
                                    # Create stacked bar chart for breakdown by ISO Week
                                    fig = px.bar(
                                        area_pivot,
                                        x='ISO Week',
                                        y=area_columns,
                                        title=f"Time Spent by Area for {selected_contractor}",
                                        color_discrete_sequence=get_color_palette(),
                                        barmode='stack',
                                        category_orders={"ISO Week": sorted_weeks} if sorted_weeks else None
                                    )
                                    
                                    # Add hover template
                                    for trace in fig.data:
                                        trace.update(
                                            hovertemplate='%{y:.1f} minutes<br>%{x}<extra></extra>'
                                        )
                                    
                                    # Fix legend overlap
                                    fig.update_layout(
                                        template="plotly_dark",
                                        paper_bgcolor="#0e1117",
                                        plot_bgcolor="#0e1117",
                                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
                                        margin=dict(l=20, r=20, t=80, b=20),
                                        yaxis_title="Minutes",
                                        title=dict(y=0.95),
                                        xaxis_title="ISO Week"
                                    )
                                    
                                    st.plotly_chart(fig, use_container_width=True)
                                    
                                    # Add copy button
                                    add_copy_button_to_chart(fig, f"Time Spent by Area for {selected_contractor}")
                                    
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
                                                weekly_avg = total_minutes / len(area_pivot) if len(area_pivot) > 0 else 0
                                                st.metric(f"Average per Week", f"{weekly_avg:.1f} min/week")
                                    
                                    # Create worker efficiency analysis (assuming Site is productive time)
                                    if site_area and welfare_area:
                                        site_total = area_pivot[site_area].sum() if site_area in area_pivot.columns else 0
                                        welfare_total = area_pivot[welfare_area].sum() if welfare_area in area_pivot.columns else 0
                                        total_time = site_total + welfare_total
                                        
                                        # Calculate productivity ratio
                                        productivity = (site_total / total_time * 100) if total_time > 0 else 0
                                        
                                        st.subheader("Site vs. Welfare Time 📊")
                                        
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
                                            
                                            # Add copy button
                                            add_copy_button_to_chart(fig, "Site Time Percentage Gauge")
                                        
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
                                            
                                            # Add copy button
                                            add_copy_button_to_chart(fig, "Time Distribution Pie Chart")
                                        
                                        # Time efficiency metrics with animation
                                        col1, col2, col3 = st.columns(3)
                                        with col1:
                                            st.markdown(f"""
                                            <div>
                                                <h3>Total Hours</h3>
                                                <h1>{total_time/60:.1f} ⏱️</h1>
                                            </div>
                                            """, unsafe_allow_html=True)
                                        with col2:
                                            site_hours = site_total / 60
                                            st.metric("Site Hours 🏗️", f"{site_hours:.1f}")
                                        with col3:
                                            welfare_hours = welfare_total / 60
                                            st.metric("Welfare Hours ☕", f"{welfare_hours:.1f}")
                                else:
                                    st.warning("No Site/Welfare areas found in the data. Please check your 'Area' column values.")
                            except Exception as e:
                                st.error(f"Error analyzing time data: {str(e)}")
                                st.code(str(e))
                        else:
                            st.warning("Required columns for time analysis (In, Out, Area) not found in the data.")
                    else:
                        st.info("Please select a contractor for time analysis.")
            
            # Tab 3: Contractor Comparison
            with tab3:
                st.subheader("Contractor Comparison 📊")
                
                # Get unique contractors
                contractors = df['Contractor'].unique().tolist()
                
                if len(contractors) < 2:
                    st.info("At least 2 contractors are needed for comparison. Your data contains only one contractor.")
                else:
                    # Use the unified contractor selection function for consistency
                    selected_contractors = select_contractor(st, key_prefix="tab3")
                    
                    if selected_contractors:
                        # Process data to ensure unique worker counts for each contractor
                        comparison_data = []
                        for contractor in selected_contractors:
                            contractor_data = process_data_for_unique_workers(df, raw_df, contractor)
                            comparison_data.append(contractor_data)
                        
                        # Combine all contractor data
                        if comparison_data:
                            comparison_df = pd.concat(comparison_data, ignore_index=True)
                            
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
                                title="Unique Worker Comparison Across Contractors",
                                color_discrete_sequence=get_color_palette(),
                                markers=True,
                                category_orders={"ISO Week": sorted_weeks} if sorted_weeks else None
                            )
                            
                            # Update y-axis title to clarify these are unique workers
                            fig.update_layout(
                                yaxis_title="Unique Worker Count",
                            )
                            
                            # Fix legend overlap
                            fig.update_layout(
                                template="plotly_dark",
                                paper_bgcolor="#0e1117",
                                plot_bgcolor="#0e1117",
                                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
                                margin=dict(l=20, r=20, t=80, b=20),
                                title=dict(y=0.95)
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Add copy button for comparison chart
                            add_copy_button_to_chart(fig, "Contractor Comparison Chart")
                            
                            # Summary statistics
                            st.subheader("Contractor Statistics 📈")
                            stats = comparison_df.groupby('Contractor')['Number of Workers'].agg(['sum', 'mean', 'max']).reset_index()
                            stats.columns = ['Contractor', 'Total Unique Workers', 'Average per Week', 'Peak Workers']
                            
                            # Round the average to 1 decimal place
                            stats['Average per Week'] = stats['Average per Week'].round(1)
                            
                            st.dataframe(stats, use_container_width=True)
                        else:
                            st.warning("No data available for selected contractors.")
                    else:
                        st.info("Please select at least one contractor for comparison.")
            
            # Tab 4: Role Distribution
            with tab4:
                st.subheader("Role Distribution Analysis 👥")
                
                # Get available contractors
                contractors = raw_df['Contractor'].unique().tolist()
                
                # Check if Emico is in the data and set it as default
                default_contractor = "Emico" if "Emico" in contractors else None
                
                # For this tab, we'll use a simple selectbox since only one contractor can be displayed
                selected_contractor = st.selectbox(
                    "Select Contractor",
                    options=contractors,
                    index=contractors.index(default_contractor) if default_contractor in contractors else 0,
                    key="role_distribution_selectbox"
                )
                
                if selected_contractor:
                    # Get data with unique worker counts
                    filtered_df = process_data_for_unique_workers(df, raw_df, selected_contractor)
                    
                    if filtered_df.empty:
                        st.warning(f"No data for contractor: {selected_contractor}")
                    else:
                        # Group by Role and sum unique workers
                        role_data = filtered_df.groupby('Role')['Number of Workers'].sum().reset_index()
                        
                        # Sort by number of workers descending
                        role_data = role_data.sort_values('Number of Workers', ascending=False)
                        
                        # Create pie chart with consistent role colors
                        fig = px.pie(
                            role_data,
                            values='Number of Workers',
                            names='Role',
                            title=f"Unique Role Distribution for {selected_contractor}",
                            color='Role',
                            color_discrete_map=role_colors
                        )
                        
                        # Customize layout
                        fig.update_layout(
                            template="plotly_dark",
                            paper_bgcolor="#0e1117",
                            plot_bgcolor="#0e1117"
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Add copy button
                        add_copy_button_to_chart(fig, f"Role Distribution for {selected_contractor}")
                        
                        # Role metrics with animation
                        total_workers = role_data['Number of Workers'].sum()
                        top_role = role_data.iloc[0]['Role']
                        top_role_count = role_data.iloc[0]['Number of Workers']
                        top_role_percent = (top_role_count / total_workers * 100) if total_workers > 0 else 0
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            # Get unique workers for this contractor
                            filtered_raw_df = raw_df[raw_df['Contractor'] == selected_contractor] if 'Contractor' in raw_df.columns else raw_df
                            unique_workers = calculate_unique_workers(filtered_raw_df)
                            st.markdown(f"""
                            <div>
                                <h3>Unique Workers</h3>
                                <h1>{unique_workers} 👷</h1>
                            </div>
                            """, unsafe_allow_html=True)
                        with col2:
                            st.metric("Number of Roles 🛠️", f"{len(role_data)}")
                        with col3:
                            st.metric(f"Top Role: {top_role}", f"{top_role_count}", f"{top_role_percent:.1f}%")
                        
                        # Create line chart showing roles over time with unique worker counts
                        # Sort ISO weeks
                        sorted_weeks = sort_iso_weeks(filtered_df['ISO Week'].unique().tolist())
                        
                        # Create line chart
                        fig = px.line(
                            filtered_df,
                            x='ISO Week',
                            y='Number of Workers',
                            color='Role',
                            title=f"Unique Worker Role Trends for {selected_contractor}",
                            color_discrete_map=role_colors,
                            markers=True,
                            category_orders={"ISO Week": sorted_weeks} if sorted_weeks else None
                        )
                        
                        # Update y-axis title to clarify these are unique workers
                        fig.update_layout(
                            yaxis_title="Unique Worker Count",
                        )
                        
                        # Fix legend overlap
                        fig.update_layout(
                            template="plotly_dark",
                            paper_bgcolor="#0e1117",
                            plot_bgcolor="#0e1117",
                            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
                            margin=dict(l=20, r=20, t=80, b=20),
                            title=dict(y=0.95)
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Add copy button
                        add_copy_button_to_chart(fig, f"Unique Worker Role Trends for {selected_contractor}")
                else:
                    st.info("Please select a contractor")
        
        except Exception as e:
            st.error(f"Error generating visualizations: {str(e)}")
            st.code(str(e))
            st.info("Try uploading your file again or check if the CSV format matches the expected structure.")

# Enhanced footer with company information
st.markdown("---")
st.markdown("""
<div style="display: flex; justify-content: space-between; align-items: center;">
    <div>
        <h4 style="margin: 0;">Kanadevia Time Tracker Analyzer</h4>
        <p style="margin: 0;">Data processed locally for security 🔒</p>
    </div>
    <div style="text-align: right;">
        <p style="margin: 0;">Website: <a href="https://kanadevia.io" target="_blank">kanadevia.io</a></p>
        <p style="margin: 0;">Contact: <a href="mailto:safety@kanadevia.io">safety@kanadevia.io</a></p>
    </div>
</div>
""", unsafe_allow_html=True) 