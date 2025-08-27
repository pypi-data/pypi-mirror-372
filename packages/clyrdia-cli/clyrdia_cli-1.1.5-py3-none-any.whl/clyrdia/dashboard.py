"""
Local Dashboard for Clyrdia CLI
This module provides a simple, always-available local dashboard
"""

import webbrowser
import socket
import threading
import time
import sqlite3
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import base64
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.columns import Columns
from rich.align import Align

console = Console()

class DashboardHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the dashboard"""
    
    def log_message(self, format, *args):
        """Suppress HTTP server logging - users don't need to see this"""
        # Completely suppress all HTTP server logging
        return
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
        if path == "/" or path == "":
            self.send_dashboard_page()
        elif path == "/api/status":
            self.send_api_response(self.get_status_data())
        elif path == "/api/metrics":
            self.send_api_response(self.get_metrics_data())
        elif path == "/api/benchmarks":
            self.send_api_response(self.get_benchmarks_data())
        elif path == "/api/models":
            self.send_api_response(self.get_models_data())
        elif path == "/api/costs":
            self.send_api_response(self.get_costs_data())
        else:
            self.send_error(404, "Not Found")
    
    def send_dashboard_page(self):
        """Send the main dashboard HTML page"""
        html = self.generate_dashboard_html()
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())
    
    def send_api_response(self, data: Dict[str, Any]):
        """Send JSON API response"""
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def get_status_data(self) -> Dict[str, Any]:
        """Get dashboard status data"""
        db_path = Path.home() / ".clyrdia" / "clyrdia.db"
        if not db_path.exists():
            return {
                "status": "no_data",
                "message": "No benchmark data found",
                "database_exists": False
            }
        
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Get basic stats
            cursor.execute("SELECT COUNT(*) FROM benchmark_results")
            total_results = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT COUNT(DISTINCT model_name) FROM benchmark_results")
            total_models = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT COUNT(DISTINCT test_name) FROM benchmark_results")
            total_tests = cursor.fetchone()[0] or 0
            
            conn.close()
            
            return {
                "status": "ready",
                "database_exists": True,
                "total_results": total_results,
                "total_models": total_models,
                "total_tests": total_tests
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "database_exists": True
            }
    
    def get_metrics_data(self) -> Dict[str, Any]:
        """Get performance metrics data"""
        db_path = Path.home() / ".clyrdia" / "clyrdia.db"
        if not db_path.exists():
            return {
                "accuracy": 0,
                "latency": 0,
                "cost_per_token": 0,
                "total_tokens": 0,
                "success_rate": 0
            }
        
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Get metrics - using actual schema columns
            cursor.execute("""
                SELECT 
                    AVG(quality_score) as avg_accuracy,
                    AVG(latency_ms) as avg_latency,
                    AVG(cost) as avg_cost,
                    SUM(input_tokens + output_tokens) as total_tokens,
                    COUNT(*) as total_results,
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_results
                FROM benchmark_results
            """)
            
            row = cursor.fetchone()
            if row and row[0] is not None:
                avg_accuracy, avg_latency, avg_cost, total_tokens, total_results, successful_results = row
                success_rate = (successful_results / total_results * 100) if total_results > 0 else 0
                
                return {
                    "accuracy": round(avg_accuracy, 2),
                    "latency": round(avg_latency, 2),
                    "cost_per_token": round(avg_cost, 6),
                    "total_tokens": total_tokens or 0,
                    "success_rate": round(success_rate, 1)
                }
            else:
                return {
                    "accuracy": 0,
                    "latency": 0,
                    "cost_per_token": 0,
                    "total_tokens": 0,
                    "success_rate": 0
                }
        except Exception:
            return {
                "accuracy": 0,
                "latency": 0,
                "cost_per_token": 0,
                "total_tokens": 0,
                "success_rate": 0
            }
    
    def get_benchmarks_data(self) -> Dict[str, Any]:
        """Get benchmark results data"""
        db_path = Path.home() / ".clyrdia" / "clyrdia.db"
        if not db_path.exists():
            return {"benchmarks": []}
        
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    test_name, model, quality_score as accuracy, latency_ms, cost as cost_per_token, 
                    (input_tokens + output_tokens) as total_tokens, success, timestamp as created_at
                FROM benchmark_results 
                ORDER BY timestamp DESC 
                LIMIT 50
            """)
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    "test_name": row[0],
                    "model_name": row[1],
                    "accuracy": row[2],
                    "latency_ms": row[3],
                    "cost_per_token": row[4],
                    "total_tokens": row[5],
                    "success": bool(row[6]),
                    "created_at": row[7]
                })
            
            conn.close()
            return {"benchmarks": results}
        except Exception:
            return {"benchmarks": []}
    
    def get_models_data(self) -> Dict[str, Any]:
        """Get model performance data"""
        db_path = Path.home() / ".clyrdia" / "clyrdia.db"
        if not db_path.exists():
            return {"models": []}
        
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    model,
                    COUNT(*) as total_runs,
                    AVG(quality_score) as avg_accuracy,
                    AVG(latency_ms) as avg_latency,
                    AVG(cost) as avg_cost,
                    SUM(input_tokens + output_tokens) as total_tokens
                FROM benchmark_results 
                GROUP BY model
                ORDER BY avg_accuracy DESC
            """)
            
            models = []
            for row in cursor.fetchall():
                models.append({
                    "name": row[0],
                    "total_runs": row[1],
                    "avg_accuracy": round(row[2], 2) if row[2] else 0,
                    "avg_latency": round(row[3], 2) if row[3] else 0,
                    "avg_cost": round(row[4], 6) if row[4] else 0,
                    "total_tokens": row[5] or 0
                })
            
            conn.close()
            return {"models": models}
        except Exception:
            return {"models": []}
    
    def get_costs_data(self) -> Dict[str, Any]:
        """Get cost analysis data"""
        db_path = Path.home() / ".clyrdia" / "clyrdia.db"
        if not db_path.exists():
            return {
                "total_cost": 0,
                "cost_by_model": {},
                "cost_by_test": {},
                "monthly_trend": []
            }
        
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Total cost
            cursor.execute("SELECT SUM(cost) FROM benchmark_results")
            total_cost = cursor.fetchone()[0] or 0
            
            # Cost by model
            cursor.execute("""
                SELECT model, SUM(cost) as model_cost
                FROM benchmark_results 
                GROUP BY model
                ORDER BY model_cost DESC
            """)
            
            cost_by_model = {}
            for row in cursor.fetchall():
                cost_by_model[row[0]] = round(row[1], 4)
            
            # Cost by test
            cursor.execute("""
                SELECT test_name, SUM(cost) as test_cost
                FROM benchmark_results 
                GROUP BY test_name
                ORDER BY test_cost DESC
            """)
            
            cost_by_test = {}
            for row in cursor.fetchall():
                cost_by_test[row[0]] = round(row[1], 4)
            
            conn.close()
            
            return {
                "total_cost": round(total_cost, 4),
                "cost_by_model": cost_by_model,
                "cost_by_test": cost_by_test,
                "monthly_trend": []  # TODO: Implement monthly trend
            }
        except Exception:
            return {
                "total_cost": 0,
                "cost_by_model": {},
                "cost_by_test": {},
                "monthly_trend": []
            }
    
    def generate_dashboard_html(self) -> str:
        """Generate the dashboard HTML page"""
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Clyrdia Dashboard</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 40px;
            color: white;
        }}
        
        .header h1 {{
            font-size: 3rem;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        .header p {{
            font-size: 1.2rem;
            opacity: 0.9;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        
        .stat-card {{
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.3s ease;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
        }}
        
        .stat-value {{
            font-size: 2.5rem;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 10px;
        }}
        
        .stat-label {{
            font-size: 1rem;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .section {{
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }}
        
        .section h2 {{
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.5rem;
        }}
        
        .data-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        
        .data-table th,
        .data-table td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }}
        
        .data-table th {{
            background: #f8f9fa;
            font-weight: 600;
            color: #667eea;
        }}
        
        .no-data {{
            text-align: center;
            padding: 40px;
            color: #666;
            font-style: italic;
        }}
        
        .refresh-btn {{
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 1rem;
            margin-bottom: 20px;
            transition: background 0.3s ease;
        }}
        
        .refresh-btn:hover {{
            background: #5a6fd8;
        }}
        
        .loading {{
            text-align: center;
            padding: 20px;
            color: #666;
        }}
        
        @media (max-width: 768px) {{
            .stats-grid {{
                grid-template-columns: 1fr;
            }}
            
            .header h1 {{
                font-size: 2rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Clyrdia Dashboard</h1>
            <p>Zero-Knowledge AI Benchmarking Platform</p>
        </div>
        
        <button class="refresh-btn" onclick="refreshData()">🔄 Refresh Data</button>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value" id="total-results">-</div>
                <div class="stat-label">Total Results</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="total-models">-</div>
                <div class="stat-label">Models Tested</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="avg-accuracy">-</div>
                <div class="stat-label">Avg Accuracy</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="total-cost">-</div>
                <div class="stat-label">Total Cost</div>
            </div>
        </div>
        
        <div class="section">
            <h2>📊 Performance Metrics</h2>
            <div id="metrics-content">
                <div class="loading">Loading metrics...</div>
            </div>
        </div>
        
        <div class="section">
            <h2>🤖 Model Performance</h2>
            <div id="models-content">
                <div class="loading">Loading models...</div>
            </div>
        </div>
        
        <div class="section">
            <h2>📈 Recent Benchmarks</h2>
            <div id="benchmarks-content">
                <div class="loading">Loading benchmarks...</div>
            </div>
        </div>
        
        <div class="section">
            <h2>💰 Cost Analysis</h2>
            <div id="costs-content">
                <div class="loading">Loading costs...</div>
            </div>
        </div>
    </div>
    
    <script>
        // Load data when page loads
        document.addEventListener('DOMContentLoaded', function() {{
            loadAllData();
        }});
        
        function refreshData() {{
            document.querySelector('.refresh-btn').textContent = '🔄 Refreshing...';
            document.querySelector('.refresh-btn').disabled = true;
            
            loadAllData().then(() => {{
                document.querySelector('.refresh-btn').textContent = '🔄 Refresh Data';
                document.querySelector('.refresh-btn').disabled = false;
            }}).catch((error) => {{
                document.querySelector('.refresh-btn').textContent = '🔄 Refresh Data';
                document.querySelector('.refresh-btn').disabled = false;
            }});
        }}
        
        async function loadAllData() {{
            try {{
                await Promise.all([
                    loadStatus(),
                    loadMetrics(),
                    loadModels(),
                    loadBenchmarks(),
                    loadCosts()
                ]);
            }} catch (error) {{
                throw error;
            }}
        }}
        
        async function loadStatus() {{
            try {{
                const response = await fetch('/api/status');
                if (!response.ok) {{
                    throw new Error(`HTTP error! status: ${{response.status}}`);
                }}
                const data = await response.json();
                
                document.getElementById('total-results').textContent = data.total_results || 0;
                document.getElementById('total-models').textContent = data.total_models || 0;
            }} catch (error) {{
                document.getElementById('total-results').textContent = '0';
                document.getElementById('total-models').textContent = '0';
            }}
        }}
        
        async function loadMetrics() {{
            try {{
                const response = await fetch('/api/metrics');
                if (!response.ok) {{
                    throw new Error(`HTTP error! status: ${{response.status}}`);
                }}
                const data = await response.json();
                
                const content = document.getElementById('metrics-content');
                content.innerHTML = `
                    <div class="stats-grid">
                        <div class="stat-card">
                            <div class="stat-value">${{data.accuracy || 0}}%</div>
                            <div class="stat-label">Accuracy</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">${{data.latency || 0}}ms</div>
                            <div class="stat-label">Latency</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">${{data.success_rate || 0}}%</div>
                            <div class="stat-label">Success Rate</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">${{(data.total_tokens || 0).toLocaleString()}}</div>
                            <div class="stat-label">Total Tokens</div>
                        </div>
                    </div>
                `;
            }} catch (error) {{
                const content = document.getElementById('metrics-content');
                content.innerHTML = `
                    <div class="stats-grid">
                        <div class="stat-card">
                            <div class="stat-value">0%</div>
                            <div class="stat-label">Accuracy</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">0ms</div>
                            <div class="stat-label">Latency</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">0%</div>
                            <div class="stat-label">Success Rate</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">0</div>
                            <div class="stat-label">Total Tokens</div>
                        </div>
                    </div>
                `;
            }}
        }}
        
        async function loadModels() {{
            try {{
                const response = await fetch('/api/models');
                if (!response.ok) {{
                    throw new Error(`HTTP error! status: ${{response.status}}`);
                }}
                const data = await response.json();
                
                const content = document.getElementById('models-content');
                if (!data.models || data.models.length === 0) {{
                    content.innerHTML = '<div class="no-data">No model data available. Run some benchmarks first!</div>';
                    return;
                }}
                
                let table = '<table class="data-table"><thead><tr><th>Model</th><th>Runs</th><th>Accuracy</th><th>Latency</th><th>Cost</th></tr></thead><tbody>';
                
                data.models.forEach(model => {{
                    table += `<tr>
                        <td><strong>${{model.name || 'Unknown'}}</strong></td>
                        <td>${{model.total_runs || 0}}</td>
                        <td>${{model.avg_accuracy || 0}}%</td>
                        <td>${{model.avg_latency || 0}}ms</td>
                        <td>$${{model.avg_cost || 0}}</td>
                    </tr>`;
                }});
                
                table += '</tbody></table>';
                content.innerHTML = table;
            }} catch (error) {{
                const content = document.getElementById('models-content');
                content.innerHTML = '<div class="no-data">Error loading model data. Please refresh the page.</div>';
            }}
        }}
        
        async function loadBenchmarks() {{
            try {{
                const response = await fetch('/api/benchmarks');
                if (!response.ok) {{
                    throw new Error(`HTTP error! status: ${{response.status}}`);
                }}
                const data = await response.json();
                
                const content = document.getElementById('benchmarks-content');
                if (!data.benchmarks || data.benchmarks.length === 0) {{
                    content.innerHTML = '<div class="no-data">No benchmark results available. Run some benchmarks first!</div>';
                    return;
                }}
                
                let table = '<table class="data-table"><thead><tr><th>Test</th><th>Model</th><th>Accuracy</th><th>Latency</th><th>Success</th><th>Date</th></tr></thead><tbody>';
                
                data.benchmarks.slice(0, 10).forEach(benchmark => {{
                    table += `<tr>
                        <td>${{benchmark.test_name || 'Unknown'}}</td>
                        <td><strong>${{benchmark.model_name || 'Unknown'}}</strong></td>
                        <td>${{benchmark.accuracy || 0}}%</td>
                        <td>${{benchmark.latency_ms || 0}}ms</td>
                        <td>${{benchmark.success ? '✅' : '❌'}}</td>
                        <td>${{benchmark.created_at || 'Unknown'}}</td>
                    </tr>`;
                }});
                
                table += '</tbody></table>';
                content.innerHTML = table;
            }} catch (error) {{
                const content = document.getElementById('benchmarks-content');
                content.innerHTML = '<div class="no-data">Error loading benchmark data. Please refresh the page.</div>';
            }}
        }}
        
        async function loadCosts() {{
            try {{
                const response = await fetch('/api/costs');
                if (!response.ok) {{
                    throw new Error(`HTTP error! status: ${{response.status}}`);
                }}
                const data = await response.json();
                
                const content = document.getElementById('costs-content');
                document.getElementById('total-cost').textContent = '$' + (data.total_cost || 0);
                
                if (!data.total_cost || data.total_cost === 0) {{
                    content.innerHTML = '<div class="no-data">No cost data available. Run some benchmarks first!</div>';
                    return;
                }}
                
                let html = '<div class="stats-grid">';
                html += '<div class="stat-card"><div class="stat-value">$' + (data.total_cost || 0) + '</div><div class="stat-label">Total Cost</div></div>';
                html += '</div>';
                
                if (data.cost_by_model && Object.keys(data.cost_by_model).length > 0) {{
                    html += '<h3>Cost by Model</h3><table class="data-table"><thead><tr><th>Model</th><th>Cost</th></tr></thead><tbody>';
                    Object.entries(data.cost_by_model).forEach(([model, cost]) => {{
                        html += `<tr><td><strong>${{model || 'Unknown'}}</strong></td><td>$${{cost || 0}}</td></tr>`;
                    }});
                    html += '</tbody></table>';
                }}
                
                content.innerHTML = html;
            }} catch (error) {{
                const content = document.getElementById('costs-content');
                content.innerHTML = '<div class="no-data">Error loading cost data. Please refresh the page.</div>';
            }}
        }}
    </script>
</body>
</html>
        """

class DashboardManager:
    """Local dashboard manager that always works"""
    
    def __init__(self):
        self.port = 3000  # Default port
        self.host = "localhost"  # Default host
        self.server = None
        self.server_thread = None
    
    def set_port(self, port: int):
        """Set the dashboard port"""
        self.port = port
    
    def is_dashboard_running(self) -> bool:
        """Check if dashboard is running on the configured port"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex((self.host, self.port))
                return result == 0
        except Exception:
            return False
    
    def start_dashboard(self):
        """Start the Next.js dashboard server"""
        if self.is_dashboard_running():
            console.print(f"[green]✅ Dashboard is already running on port {self.port}[/green]")
            return True
        
        try:
            # Start Next.js dashboard
            dashboard_dir = Path(__file__).parent.parent / "dashboard"
            
            if not dashboard_dir.exists():
                console.print(f"[red]❌ Dashboard directory not found: {dashboard_dir}[/red]")
                return False
            
            # Change to dashboard directory and start Next.js dev server
            import subprocess
            import sys
            
            # Start Next.js dev server in background
            process = subprocess.Popen(
                ["npm", "run", "dev"],
                cwd=dashboard_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait a moment for server to start
            time.sleep(3)
            
            if self.is_dashboard_running():
                console.print(f"[green]✅ Next.js Dashboard started successfully on port {self.port}[/green]")
                console.print(f"[dim]💡 Dashboard will continue running in the background[/dim]")
                console.print(f"[dim]💡 You can close this terminal and dashboard will remain accessible[/dim]")
                return True
            else:
                console.print(f"[red]❌ Failed to start Next.js dashboard on port {self.port}[/red]")
                return False
                
        except Exception as e:
            console.print(f"[red]❌ Error starting Next.js dashboard: {str(e)}[/red]")
            return False
    
    def stop_dashboard(self):
        """Stop the Next.js dashboard server"""
        try:
            # Find and kill Next.js processes on the dashboard port
            import subprocess
            import psutil
            
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['cmdline'] and any('next' in cmd.lower() for cmd in proc.info['cmdline'] if cmd):
                        if any(str(self.port) in cmd for cmd in proc.info['cmdline'] if cmd):
                            proc.terminate()
                            console.print(f"[yellow]🛑 Next.js Dashboard stopped on port {self.port}[/yellow]")
                            return
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            console.print(f"[yellow]🛑 No Next.js dashboard found running on port {self.port}[/yellow]")
        except Exception as e:
            console.print(f"[yellow]🛑 Error stopping dashboard: {str(e)}[/yellow]")
    
    def open_dashboard_url(self):
        """Show the dashboard URL for user to click"""
        url = f"http://{self.host}:{self.port}"
        console.print(f"[green]🌐 Dashboard is ready![/green]")
        console.print(f"[blue]🔗 Dashboard URL: {url}[/blue]")
        console.print("[yellow]💡 To access your dashboard:[/yellow]")
        console.print(f"[yellow]   1. Copy this URL:[/yellow] [bold blue]{url}[/bold blue]")
        console.print("[yellow]   2. Paste it into your web browser[/yellow]")
        console.print(f"[yellow]   3. Or run:[/yellow] [bold]open {url}[/bold]")
        console.print(f"[dim]💡 If the link doesn't work, manually copy: {url}[/dim]")
        
        # Try to open the dashboard in the default browser
        try:
            import webbrowser
            webbrowser.open(url)
            console.print("[green]✅ Opened dashboard in your default browser![/green]")
        except Exception as e:
            console.print(f"[yellow]⚠️  Couldn't auto-open browser: {str(e)}[/yellow]")
            console.print(f"[yellow]   Please manually copy and paste: {url}[/yellow]")
        
        console.print(f"\n[dim]💡 Dashboard is now running in the background on port {self.port}[/dim]")
        console.print(f"[dim]💡 You can run other commands while the dashboard continues running[/dim]")
    
    def show_dashboard_instructions(self):
        """Display dashboard information"""
        console.print()
        
        if self.is_dashboard_running():
            url = f"http://{self.host}:{self.port}"
            console.print(Panel.fit(
                f"[bold green]✅ Dashboard is running![/bold green]\n\n"
                f"🌐 Access your dashboard at: [bold blue][link={url}]{url}[/link][/bold blue]\n\n"
                "The dashboard is now available and will show:\n"
                "• 📊 Performance metrics (even with 0 data)\n"
                "• 🤖 Model comparisons\n"
                "• 💰 Cost analysis\n"
                "• 📈 Benchmark results\n\n"
                "💡 Click the link above to open in your browser\n"
                "🔄 Use the refresh button to update data\n"
                "📊 Dashboard works even with 0 credits - shows all historical data!",
                border_style="green",
                title="[bold]Dashboard Ready[/bold]"
            ))
        else:
            console.print(Panel.fit(
                "[bold yellow]⚠️  Dashboard not running[/bold yellow]\n\n"
                "Starting local dashboard...",
                border_style="yellow",
                title="[bold]Starting Dashboard[/bold]"
            ))
            
            if self.start_dashboard():
                self.show_dashboard_instructions()
            else:
                console.print("[red]❌ Failed to start dashboard[/red]")
    
    def check_dashboard_status(self):
        """Check and display dashboard status"""
        console.print()
        
        if self.is_dashboard_running():
            status_text = f"[green]✅ Dashboard is running on port {self.port}[/green]"
            url = f"http://{self.host}:{self.port}"
            
            console.print(Panel.fit(
                f"{status_text}\n\n"
                f"[bold]🌐 Access at:[/bold] [bold blue][link={url}]{url}[/link][/bold blue]\n\n"
                "[bold]Features:[/bold]\n"
                "• 📊 Real-time metrics and analytics\n"
                "• 🤖 Model performance comparison\n"
                "• 💰 Cost analysis and optimization\n"
                "• 📈 Historical trend analysis\n"
                "• 🔍 Detailed result inspection\n\n"
                "💡 Click the link above to open in your browser\n"
                "🔄 Use the refresh button to update data\n"
                "📊 Dashboard works even with 0 credits - shows all historical data!\n\n"
                "[bold]Server Info:[/bold]\n"
                f"• Host: {self.host}\n"
                f"• Port: {self.port}\n"
                "• Status: Running in background\n"
                "• Persistence: Will continue after CLI closes",
                border_style="green",
                title="[bold]Dashboard Status[/bold]"
            ))
        else:
            console.print(Panel.fit(
                f"[yellow]⚠️  Dashboard is not running on port {self.port}[/yellow]\n\n"
                "Starting dashboard...",
                border_style="yellow",
                title="[bold]Dashboard Status[/bold]"
            ))
            
            if self.start_dashboard():
                self.check_dashboard_status()
            else:
                console.print("[red]❌ Failed to start dashboard[/red]")
    
    def migrate_data(self):
        """Provide instructions for data migration"""
        console.print()
        
        console.print(Panel.fit(
            "[bold bright_cyan]🔄 Data Migration[/bold bright_cyan]\n\n"
            "Your existing benchmark data is automatically compatible with the dashboard!\n\n"
            "[bold]The dashboard will:[/bold]\n"
            "• 📊 Show all your historical results\n"
            "• 🤖 Compare model performance over time\n"
            "• 💰 Track cost trends and optimization\n"
            "• 📈 Provide insights and analytics\n\n"
            "[bold]No manual migration needed:[/bold]\n"
            "• Just run benchmarks normally\n"
            "• Data appears automatically in the dashboard\n"
            "• Real-time updates as you test\n\n"
            "🚀 Start benchmarking and see your data in the dashboard!",
            border_style="bright_cyan",
            title="[bold]Data Migration Guide[/bold]"
        ))
