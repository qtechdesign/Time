# Kanadevia Time Tracker Analyzer

![Kanadevia Time Tracker](https://img.icons8.com/color/240/overtime--v1.png)

## Overview

The Kanadevia Time Tracker Analyzer is a powerful data visualization tool designed to help construction project managers analyze workforce data from time tracking systems. This tool transforms raw time tracking CSV exports into actionable insights about contractor workforce distribution, site vs. welfare time analysis, role distribution, and contractor comparisons.

## Features

- **🚀 User-Friendly Interface**: Sleek, modern dark-themed UI with intuitive navigation
- **👷 Workforce Analysis**: Track workers per week, broken down by contractor and role
- **⏱️ Site vs. Welfare Analysis**: Visualize productive vs. non-productive time
- **📈 Contractor Comparison**: Compare multiple contractors' workforce numbers over time
- **👥 Role Distribution**: Analyze the distribution of roles within each contractor
- **🔒 Privacy-Focused**: All data is processed locally in your browser - no data is sent to any server

## Live Demo

Try the live demo: [Kanadevia Time Tracker Analyzer on Streamlit](https://time-tracker-analyzer.streamlit.app/)

## Installation

### Prerequisites

- Python 3.8+
- pip (Python package installer)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/kanadevia-time-tracker.git
   cd kanadevia-time-tracker
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application locally:
   ```bash
   streamlit run app.py
   ```

## Usage

1. Start the application with `streamlit run app.py`
2. Upload your Time Tracker CSV export file
3. Navigate through the different visualization tabs:
   - Workforce by Week
   - Site vs. Welfare Time
   - Contractor Comparison
   - Role Distribution

## Expected CSV Format

For best results, your CSV should include these columns:

- **Contractor/Company**: The name of the contracting company
- **Worker Name**: The name of the worker
- **Role/Trade**: Worker's role or job title
- **In/Out**: Date and time of entry/exit (format: DD/MM/YYYY HH:MM)
- **Area**: Location in the project (e.g., Site, Welfare)
- **Total Minutes**: Duration in minutes (calculated automatically if missing)

A sample CSV file is included in the repository.

## Customization

The application can be customized through modifying:

- `utils.py` for data processing logic 
- `app.py` for UI components and visualizations

## Technologies Used

- **Streamlit**: Frontend framework
- **Pandas**: Data manipulation
- **Plotly**: Interactive visualizations
- **NumPy**: Numerical operations

## Contact

- Website: [kanadevia.io](https://kanadevia.io)
- Email: [safety@kanadevia.io](mailto:safety@kanadevia.io)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Screenshots

![Workforce Analysis](https://example.com/screenshot1.jpg)
![Time Analysis](https://example.com/screenshot2.jpg)

## Acknowledgements

- Icons by [Icons8](https://icons8.com/)
- Color palettes inspired by [Material Design](https://material.io/design/color/the-color-system.html) 