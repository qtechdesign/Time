from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        html_content = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Contractor Workforce Analyzer</title>
            <style>
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #f8f8f2;
                    background-color: #0e1117;
                    margin: 0;
                    padding: 0;
                    display: flex;
                    flex-direction: column;
                    min-height: 100vh;
                    align-items: center;
                }
                .container {
                    max-width: 800px;
                    margin: 2rem auto;
                    padding: 2rem;
                    background-color: #262730;
                    border-radius: 20px;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
                }
                h1 {
                    color: #bb86fc;
                    text-align: center;
                    margin-bottom: 1.5rem;
                }
                p {
                    margin-bottom: 1rem;
                }
                .highlight {
                    color: #03dac6;
                    font-weight: bold;
                }
                .button {
                    display: inline-block;
                    background-color: #bb86fc;
                    color: #0e1117;
                    padding: 0.8rem 1.5rem;
                    text-decoration: none;
                    border-radius: 30px;
                    font-weight: bold;
                    margin-top: 1rem;
                    transition: all 0.3s ease;
                }
                .button:hover {
                    background-color: #c7a2f2;
                    transform: translateY(-2px);
                    box-shadow: 0 6px 8px rgba(0, 0, 0, 0.1);
                }
                .logo {
                    text-align: center;
                    margin-bottom: 2rem;
                }
                .footer {
                    margin-top: auto;
                    text-align: center;
                    padding: 1rem;
                    font-size: 0.9rem;
                    color: #888;
                }
                code {
                    background-color: #1f1f1f;
                    padding: 0.2rem 0.4rem;
                    border-radius: 4px;
                    font-family: 'Courier New', monospace;
                }
            </style>
        </head>
        <body>
            <div class="logo">
                <img src="https://img.icons8.com/fluency/240/analytics.png" alt="Analytics Icon" width="100">
            </div>
            
            <div class="container">
                <h1>Contractor Workforce Analyzer</h1>
                <p>Thank you for your interest in the <span class="highlight">Contractor Workforce Analyzer</span> application!</p>
                
                <p>This is a Streamlit application that requires a server runtime, which is not directly compatible with Vercel's serverless deployment model.</p>
                
                <p>For the best experience with this application, we recommend deploying on one of these platforms:</p>
                
                <ul>
                    <li><span class="highlight">Streamlit Cloud</span> - The easiest option for Streamlit apps</li>
                    <li><span class="highlight">Heroku</span> - Great for web applications</li>
                    <li><span class="highlight">Docker</span> - For more advanced deployment options</li>
                </ul>
                
                <p>To run this application locally:</p>
                <code>pip install -r requirements.txt</code><br>
                <code>streamlit run app.py</code>
                
                <p>
                    <a href="https://github.com/yourusername/contractor-workforce-analyzer" class="button">View on GitHub</a>
                </p>
            </div>
            
            <div class="footer">
                &copy; 2023 Contractor Workforce Analyzer | No data is stored in the cloud
            </div>
        </body>
        </html>
        """
        
        self.wfile.write(html_content.encode('utf-8'))
        return 