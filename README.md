# Contractor Workforce Analyzer

A modern, responsive web application for visualizing contractor workforce data from CSV files.

![App Preview](https://img.icons8.com/fluency/240/analytics.png)

## Features

- 📊 Interactive charts for workers per week per contractor
- 🔍 Filter by specific contractors or time periods
- 📱 Fully responsive design
- 🌙 Dark mode interface
- 🔒 No cloud storage - all data processed locally

## Installation

1. Clone this repository:
   ```
   git clone <repository-url>
   cd contractor-workforce-analyzer
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Start the application:
   ```
   streamlit run app.py
   ```

2. Open your web browser and navigate to the URL displayed in the terminal (typically http://localhost:8501)

3. Follow the three-step process in the app:
   - Welcome screen
   - Upload your CSV file
   - Explore visualizations

## CSV File Format

The application supports the Time tracking system CSV format with columns for:
- **Contractor**: The name of the contractor
- **Person/Name**: The person's name
- **StartTime/EndTime**: Date and time of the activity
- **Area**: Location type (e.g., 'Site', 'Welfare')
- **Role/Job Title**: The worker's role or position
- **Duration**: Duration of the activity in minutes

Example CSV structure:
```
Contractor,Person,StartTime,EndTime,Area,Duration,Role
Allelys,John Smith,13/06/2024 11:27,13/06/2024 11:39,Site,12,Operative
Allelys,John Smith,13/06/2024 11:39,13/06/2024 13:08,Welfare,89,Operative
```

## Deployment Options

### Streamlit Cloud (Recommended)

The easiest way to deploy this app is using [Streamlit Cloud](https://streamlit.io/cloud):

1. Push your code to a GitHub repository
2. Sign up for Streamlit Cloud
3. Deploy directly from your GitHub repository
4. Your app will be available at a shareable URL

### Heroku

You can deploy to Heroku by:

1. Creating a `Procfile` with:
   ```
   web: streamlit run app.py --server.port=$PORT
   ```
2. Following the [Heroku deployment guide](https://devcenter.heroku.com/articles/getting-started-with-python)

### Vercel Deployment

While Vercel is primarily for static sites and serverless functions, you can deploy a Streamlit app on Vercel with some additional configuration:

1. Create a `vercel.json` file:
   ```json
   {
     "builds": [
       { "src": "index.py", "use": "@vercel/python" }
     ],
     "routes": [
       { "src": "/(.*)", "dest": "index.py" }
     ]
   }
   ```

2. Create a wrapper file `index.py`:
   ```python
   from http.server import BaseHTTPRequestHandler

   class handler(BaseHTTPRequestHandler):
       def do_GET(self):
           self.send_response(200)
           self.send_header('Content-type', 'text/plain')
           self.end_headers()
           self.wfile.write('Please note: Streamlit apps require a server runtime and cannot be deployed directly on Vercel. Consider using Streamlit Cloud or Heroku instead.'.encode())
           return
   ```

3. Deploy to Vercel

**Note**: This will only serve a static page explaining that Streamlit requires a server runtime. For a full-featured Streamlit app, we recommend using Streamlit Cloud, Heroku, or a containerized solution like Docker with a cloud provider that supports containers.

### Docker Deployment

For more advanced deployment, you can use Docker:

1. Create a `Dockerfile`:
   ```dockerfile
   FROM python:3.9-slim

   WORKDIR /app

   COPY requirements.txt .
   RUN pip install -r requirements.txt

   COPY . .

   EXPOSE 8501

   CMD ["streamlit", "run", "app.py"]
   ```

2. Build and run the Docker image:
   ```
   docker build -t contractor-workforce-analyzer .
   docker run -p 8501:8501 contractor-workforce-analyzer
   ```

## Development

This application is built with:
- [Streamlit](https://streamlit.io/) - The web framework
- [Plotly](https://plotly.com/) - For interactive visualizations
- [Pandas](https://pandas.pydata.org/) - For data manipulation

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Privacy

This application processes all data locally on your machine. No data is sent to any server or stored in the cloud. 