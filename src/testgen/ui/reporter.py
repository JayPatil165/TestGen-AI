"""
Report generation module for TestGen-AI.

Generates test execution reports in various formats (HTML, JSON, etc.)
for all 14 supported languages.
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime
import json


class ExecutionSummary:
    """Test execution summary data structure."""
    
    def __init__(
        self,
        project_name: str = "TestGen-AI Project",
        total: int = 0,
        passed: int = 0,
        failed: int = 0,
        skipped: int = 0,
        duration: float = 0.0,
        timestamp: Optional[datetime] = None,
        results: Optional[List[Dict[str, Any]]] = None,
        language: Optional[str] = None
    ):
        """
        Initialize execution summary.
        
        Args:
            project_name: Name of the project
            total: Total number of tests
            passed: Number of passed tests
            failed: Number of failed tests
            skipped: Number of skipped tests
            duration: Total execution duration in seconds
            timestamp: Test execution timestamp
            results: List of individual test results
            language: Programming language (if single language)
        """
        self.project_name = project_name
        self.total = total
        self.passed = passed
        self.failed = failed
        self.skipped = skipped
        self.duration = duration
        self.timestamp = timestamp or datetime.now()
        self.results = results or []
        self.language = language
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage."""
        if self.total == 0:
            return 0.0
        return (self.passed / self.total) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'project_name': self.project_name,
            'total': self.total,
            'passed': self.passed,
            'failed': self.failed,
            'skipped': self.skipped,
            'duration': self.duration,
            'timestamp': self.timestamp.isoformat(),
            'success_rate': self.success_rate,
            'language': self.language,
            'results': self.results
        }


class ReportGenerator:
    """
    Generate test execution reports in various formats.
    
    Supports all 14 programming languages:
    Python, JavaScript, TypeScript, Java, Go, C#, Ruby, Rust, PHP,
    Swift, Kotlin, C++, HTML, CSS
    """
    
    def __init__(self):
        """Initialize the report generator."""
        self.supported_formats = ['html', 'json', 'markdown']
    
    def generate_html(
        self,
        results: ExecutionSummary,
        output_path: str
    ) -> str:
        """
        Generate an HTML report from test execution results.
        
        Args:
            results: ExecutionSummary containing test results
            output_path: Path where the HTML report will be saved
            
        Returns:
            Path to the generated HTML report
            
        Raises:
            ValueError: If results are invalid
            IOError: If file cannot be written
        """
        if not isinstance(results, ExecutionSummary):
            raise ValueError("results must be an ExecutionSummary instance")
        
        # Generate HTML content
        html_content = self._generate_html_content(results)
        
        # Write to file
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            output_file.write_text(html_content, encoding='utf-8')
        except IOError as e:
            raise IOError(f"Failed to write report to {output_path}: {e}")
        
        return str(output_file.absolute())
    
    def _generate_html_content(self, results: ExecutionSummary) -> str:
        """
        Generate HTML content for the report.
        
        Args:
            results: ExecutionSummary containing test results
            
        Returns:
            HTML string
        """
        # Determine status color and badge class
        if results.failed > 0:
            status_color = "#dc3545"  # Red
            status_text = "FAILED"
            badge_class = "failed"
        elif results.skipped > 0:
            status_color = "#ffc107"  # Yellow
            status_text = "PARTIAL"
            badge_class = "partial"
        elif results.passed == results.total and results.total > 0:
            status_color = "#28a745"  # Green
            status_text = "PASSED"
            badge_class = "passed"
        else:
            status_color = "#6c757d"  # Gray
            status_text = "NO TESTS"
            badge_class = "no-tests"
        
        # Format language badge
        language_badge = ""
        if results.language:
            language_badge = f'<span class="badge language-badge">{results.language.upper()}</span>'
        
        # Generate test results table rows
        results_rows = ""
        for i, test_result in enumerate(results.results, 1):
            status = test_result.get('status', 'UNKNOWN')
            test_name = test_result.get('test_name', 'Unknown Test')
            duration = test_result.get('duration', 0.0)
            details = test_result.get('details', '')
            lang = test_result.get('language', '').upper()
            
            # Status badge color
            if status == 'PASS':
                status_badge = '<span class="badge badge-success">✓ PASS</span>'
            elif status == 'FAIL':
                status_badge = '<span class="badge badge-danger">✗ FAIL</span>'
            elif status == 'SKIP':
                status_badge = '<span class="badge badge-warning">⊘ SKIP</span>'
            else:
                status_badge = f'<span class="badge badge-secondary">{status}</span>'
            
            results_rows += f"""
                <tr>
                    <td>{i}</td>
                    <td><span class="badge language-badge">{lang}</span></td>
                    <td>{test_name}</td>
                    <td>{status_badge}</td>
                    <td>{duration:.2f}s</td>
                    <td><small>{details}</small></td>
                </tr>
            """
        
        # Prepare chart data
        chart_data_json = json.dumps({
            'passed': results.passed,
            'failed': results.failed,
            'skipped': results.skipped,
            'total': results.total
        })
        
        # Build complete HTML
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TestGen-AI Report - {results.project_name}</title>
    <!-- Chart.js for graphs -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: #f8f9fa;
            padding: 20px;
            min-height: 100vh;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background-color: white;
            border-radius: 12px;
            box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
            overflow: hidden;
        }}

        .header {{
            background: #ffffff;
            color: #1f2937;
            padding: 32px 40px;
            border-bottom: 1px solid #e5e7eb;
            position: relative;
        }}

        h1 {{
            font-size: 1.875em;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            gap: 12px;
            font-weight: 600;
            color: #111827;
        }}

        .timestamp {{
            font-size: 0.875em;
            color: #6b7280;
            margin-top: 4px;
            font-weight: 400;
        }}

        .status-badge {{
            display: inline-block;
            padding: 6px 14px;
            border-radius: 6px;
            font-weight: 600;
            font-size: 0.875em;
            margin-top: 12px;
        }}
        
        .status-badge.passed {{
            background-color: #d1fae5;
            color: #065f46;
            border: 1px solid #10b981;
        }}
        
        .status-badge.failed {{
            background-color: #fee2e2;
            color: #991b1b;
            border: 1px solid #ef4444;
        }}
        
        .status-badge.partial {{
            background-color: #fef3c7;
            color: #92400e;
            border: 1px solid #f59e0b;
        }}
        
        .status-badge.no-tests {{
            background-color: #f3f4f6;
            color: #374151;
            border: 1px solid #d1d5db;
        }}

        .badge {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 0.75em;
            font-weight: 500;
            border: 1px solid;
        }}

        .language-badge {{
            background: #eff6ff;
            border-color: #3b82f6;
            color: #1e40af;
            font-weight: 600;
            letter-spacing: 0.025em;
            padding: 5px 12px;
            transition: all 0.2s ease;
        }}
        
        .language-badge:hover {{
            background: #dbeafe;
            border-color: #2563eb;
        }}
        
        .language-badges {{
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            align-items: center;
        }}

        .content {{
            padding: 40px;
        }}

        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}

        .summary-card {{
            background: rgba(var(--card-rgb), 0.08);
            border: 2px solid rgba(var(--card-rgb), 1);
            color: rgb(var(--card-rgb));
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            transition: all 0.2s ease;
        }}

        .summary-card:hover {{
            background: rgba(var(--card-rgb), 0.15);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transform: translateY(-2px);
        }}

        .summary-card.total {{
            --card-rgb: 99, 102, 241;
        }}

        .summary-card.passed {{
            --card-rgb: 16, 185, 129;
        }}

        .summary-card.failed {{
            --card-rgb: 239, 68, 68;
        }}

        .summary-card.skipped {{
            --card-rgb: 245, 158, 11;
        }}

        .summary-card.duration {{
            --card-rgb: 59, 130, 246;
        }}

        .summary-card.rate {{
            --card-rgb: 132, 204, 22;
        }}

        .summary-card h3 {{
            font-size: 0.75em;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #111827;
            margin-bottom: 10px;
            font-weight: 600;
            opacity: 0.7;
        }}

        .summary-card .value {{
            font-size: 2.25em;
            font-weight: 600;
            line-height: 1;
        }}
        
        /* Scroll-triggered animations */
        .summary-card {{
            opacity: 0;
            transform: translateY(20px);
            animation: fadeInUp 0.6s ease forwards;
        }}
        
        .summary-card:nth-child(1) {{ animation-delay: 0.1s; }}
        .summary-card:nth-child(2) {{ animation-delay: 0.2s; }}
        .summary-card:nth-child(3) {{ animation-delay: 0.3s; }}
        .summary-card:nth-child(4) {{ animation-delay: 0.4s; }}
        .summary-card:nth-child(5) {{ animation-delay: 0.5s; }}
        .summary-card:nth-child(6) {{ animation-delay: 0.6s; }}
        
        @keyframes fadeInUp {{
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}

        /* Charts Section */
        .charts-section {{
            margin-top: 40px;
            margin-bottom: 40px;
        }}

        .charts-section h2 {{
            font-size: 1.5em;
            margin-bottom: 20px;
            color: #333;
            border-bottom: 2px solid #5C6BC0;
            padding-bottom: 10px;
        }}

        .charts-container {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
        }}

        .chart-wrapper {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        }}

        .chart-wrapper h3 {{
            font-size: 1.1em;
            margin-bottom: 15px;
            color: #333;
            text-align: center;
        }}

        .chart-wrapper canvas {{
            max-height: 250px !important;
        }}

        .results-section {{
            margin-top: 40px;
        }}

        .results-section h2 {{
            font-size: 1.5em;
            margin-bottom: 20px;
            color: #333;
            border-bottom: 2px solid #5C6BC0;
            padding-bottom: 10px;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        }}

        thead {{
            background: linear-gradient(135deg, #5C6BC0 0%, #7986CB 100%);
            color: white;
        }}

        th {{
            padding: 15px 12px;
            text-align: left;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.85em;
            letter-spacing: 0.5px;
        }}

        td {{
            padding: 12px;
            border-bottom: 1px solid #f0f0f0;
        }}

        tbody tr {{
            transition: background-color 0.15s ease;
        }}

        tbody tr:hover {{
            background-color: #f8f9fa;
        }}

        tbody tr:last-child td {{
            border-bottom: none;
        }}

        .badge-success {{
            background: linear-gradient(135deg, #66BB6A 0%, #81C784 100%);
        }}

        .badge-danger {{
            background: linear-gradient(135deg, #EF5350 0%, #E57373 100%);
        }}

        .badge-warning {{
            background: linear-gradient(135deg, #FFA726 0%, #FFB74D 100%);
            color: #fff;
        }}

        .badge-secondary {{
            background: linear-gradient(135deg, #78909C 0%, #90A4AE 100%);
        }}

        .footer {{
            margin-top: 40px;
            padding: 25px 40px;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            text-align: center;
            color: #555;
        }}

        .footer p {{
            margin: 5px 0;
        }}

        .footer .languages {{
            font-size: 0.85em;
            color: #666;
            margin-top: 10px;
        }}

        @media (max-width: 768px) {{
            body {{
                padding: 10px;
            }}

            .summary {{
                grid-template-columns: 1fr;
            }}

            .charts-container {{
                grid-template-columns: 1fr;
            }}

            h1 {{
                font-size: 1.5em;
            }}

            .summary-card .value {{
                font-size: 2em;
            }}

            table {{
                font-size: 0.85em;
            }}
        }}
    </style>
</head>

<body>
    <div class="container">
        <div class="header">
            <h1>
                TestGen-AI Test Report
                {language_badge}
            </h1>
            <div class="timestamp">Generated: {results.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</div>
            <div>
                <span class="status-badge">{status_text}</span>
            </div>
        </div>

        <div class="content">
            <div class="summary">
                <div class="summary-card total">
                    <h3>Total Tests</h3>
                    <div class="value">{results.total}</div>
                </div>

                <div class="summary-card passed">
                    <h3>Passed</h3>
                    <div class="value">{results.passed}</div>
                </div>

                <div class="summary-card failed">
                    <h3>Failed</h3>
                    <div class="value">{results.failed}</div>
                </div>

                <div class="summary-card skipped">
                    <h3>Skipped</h3>
                    <div class="value">{results.skipped}</div>
                </div>

                <div class="summary-card duration">
                    <h3>Duration</h3>
                    <div class="value">{results.duration:.2f}s</div>
                </div>

                <div class="summary-card rate">
                    <h3>Success Rate</h3>
                    <div class="value">{results.success_rate:.1f}%</div>
                </div>
            </div>

            <!-- Charts Section -->
            <div class="charts-section">
                <h2>📊 Visual Analytics</h2>
                <div class="charts-container">
                    <div class="chart-wrapper">
                        <h3>Test Results Distribution</h3>
                        <canvas id="resultsChart"></canvas>
                    </div>
                    <div class="chart-wrapper">
                        <h3>Success Rate</h3>
                        <canvas id="successRateChart"></canvas>
                    </div>
                </div>
            </div>

            <div class="results-section">
                <h2>Test Results</h2>
                <table>
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Language</th>
                            <th>Test Name</th>
                            <th>Status</th>
                            <th>Duration</th>
                            <th>Details</th>
                        </tr>
                    </thead>
                    <tbody>
                        {results_rows if results_rows else '<tr><td colspan="6" style="text-align: center; padding: 20px; color: #999;">No test results available</td></tr>'}
                    </tbody>
                </table>
            </div>
        </div>

        <div class="footer">
            <p><strong>Generated by TestGen-AI</strong></p>
            <p>Universal Multi-Language Testing Framework</p>
            <p class="languages">
                <small>
                    Supports: Python, JavaScript, TypeScript, Java, Go, C#, Ruby, Rust, PHP, Swift, Kotlin, C++, HTML, CSS
                </small>
            </p>
        </div>
    </div>

    <script>
        // Chart.js implementation with proper error handling
        const chartData = {chart_data_json};
        
        // Results Distribution Chart (Doughnut)
        const resultsCtx = document.getElementById('resultsChart');
        if (resultsCtx && chartData.total > 0) {{
            new Chart(resultsCtx, {{
                type: 'doughnut',
                data: {{
                    labels: ['Passed', 'Failed', 'Skipped'],
                    datasets: [{{
                        data: [chartData.passed, chartData.failed, chartData.skipped],
                        backgroundColor: [
                            'rgba(102, 187, 106, 0.8)',  // Green
                            'rgba(239, 83, 80, 0.8)',    // Red
                            'rgba(255, 167, 38, 0.8)'    // Orange
                        ],
                        borderColor: [
                            'rgba(102, 187, 106, 1)',
                            'rgba(239, 83, 80, 1)',
                            'rgba(255, 167, 38, 1)'
                        ],
                        borderWidth: 2
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {{
                        legend: {{
                            position: 'bottom',
                            labels: {{
                                padding: 15,
                                font: {{
                                    size: 12
                                }}
                            }}
                        }}
                    }}
                }}
            }});
        }} else if (resultsCtx) {{
            resultsCtx.parentElement.innerHTML = '<div style="text-align: center; padding: 40px; color: #999;">No test data available for visualization</div>';
        }}

        // Success Rate Chart (Bar)
        const successCtx = document.getElementById('successRateChart');
        if (successCtx && chartData.total > 0) {{
            const successRate = chartData.total > 0 ? (chartData.passed / chartData.total) * 100 : 0;
            const failureRate = 100 - successRate;
            
            new Chart(successCtx, {{
                type: 'bar',
                data: {{
                    labels: ['Success Rate', 'Failure Rate'],
                    datasets: [{{
                        label: 'Percentage',
                        data: [successRate, failureRate],
                        backgroundColor: [
                            'rgba(156, 204, 101, 0.8)',  // Success: Green
                            'rgba(239, 83, 80, 0.8)'     // Failure: Red
                        ],
                        borderColor: [
                            'rgba(156, 204, 101, 1)',
                            'rgba(239, 83, 80, 1)'
                        ],
                        borderWidth: 2
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: true,
                    scales: {{
                        y: {{
                            beginAtZero: true,
                            max: 100,
                            ticks: {{
                                callback: function(value) {{
                                    return value + '%';
                                }}
                            }}
                        }}
                    }},
                    plugins: {{
                        legend: {{
                            display: false
                        }}
                    }}
                }}
            }});
        }} else if (successCtx) {{
            successCtx.parentElement.innerHTML = '<div style="text-align: center; padding: 40px; color: #999;">No test data available for visualization</div>';
        }}
    </script>
</body>
</html>
"""
        
        return html

        
        # Generate test results table rows
        results_rows = ""
        for i, test_result in enumerate(results.results, 1):
            status = test_result.get('status', 'UNKNOWN')
            test_name = test_result.get('test_name', 'Unknown Test')
            duration = test_result.get('duration', 0.0)
            details = test_result.get('details', '')
            lang = test_result.get('language', '').upper()
            
            # Status badge color
            if status == 'PASS':
                status_badge = '<span class="badge badge-success">✔ PASS</span>'
            elif status == 'FAIL':
                status_badge = '<span class="badge badge-danger">✘ FAIL</span>'
            elif status == 'SKIP':
                status_badge = '<span class="badge badge-warning">⊘ SKIP</span>'
            else:
                status_badge = f'<span class="badge badge-secondary">{status}</span>'
            
            results_rows += f"""
                <tr>
                    <td>{i}</td>
                    <td><span class="badge" style="background: linear-gradient(135deg, #4A90E2 0%, #357ABD 100%);">{lang}</span></td>
                    <td>{test_name}</td>
                    <td>{status_badge}</td>
                    <td>{duration:.2f}s</td>
                    <td><small>{details}</small></td>
                </tr>
            """
        
        # Build complete HTML
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TestGen-AI Report - {results.project_name}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            padding: 30px;
        }}
        .header {{
            border-bottom: 3px solid {status_color};
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        h1 {{
            margin: 0 0 10px 0;
            color: #333;
        }}
        .timestamp {{
            color: #666;
            font-size: 14px;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .summary-card {{
            background: rgba(0, 0, 0, 0.05);
            border: 2px solid rgba(0, 0, 0, 0.1);
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }}
        .summary-card.total {{ background: rgba(92, 107, 192, 0.12); border: 2px solid rgb(92, 107, 192); color: rgb(92, 107, 192); }}
        .summary-card.passed {{ background: rgba(102, 187, 106, 0.12); border: 2px solid rgb(102, 187, 106); color: rgb(102, 187, 106); }}
        .summary-card.failed {{ background: rgba(239, 83, 80, 0.12); border: 2px solid rgb(239, 83, 80); color: rgb(239, 83, 80); }}
        .summary-card.skipped {{ background: rgba(255, 167, 38, 0.12); border: 2px solid rgb(255, 167, 38); color: rgb(255, 167, 38); }}
        .summary-card.duration {{ background: rgba(66, 165, 245, 0.12); border: 2px solid rgb(66, 165, 245); color: rgb(66, 165, 245); }}
        .summary-card.rate {{ background: rgba(156, 204, 101, 0.12); border: 2px solid rgb(156, 204, 101); color: rgb(156, 204, 101); }}
        .summary-card:hover {{ background: rgba(var(--card-rgb), 0.18); transform: translateY(-4px); box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15); }}
        .summary-card h3 {{
            margin: 0 0 10px 0;
            font-size: 14px;
            text-transform: uppercase;
            opacity: 0.9;
        }}
        .summary-card .value {{
            font-size: 32px;
            font-weight: bold;
            margin: 0;
        }}
        .status-badge {{
            display: inline-block;
            padding: 8px 16px;
            background-color: {status_color};
            color: white;
            border-radius: 4px;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        th {{
            background-color: #f8f9fa;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            border-bottom: 2px solid #dee2e6;
        }}
        td {{
            padding: 12px;
            border-bottom: 1px solid #dee2e6;
        }}
        tr:hover {{
            background-color: #f8f9fa;
        }}
        .badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 600;
            color: white;
        }}
        .badge-success {{ background-color: #28a745; }}
        .badge-danger {{ background-color: #dc3545; }}
        .badge-warning {{ background-color: #ffc107; color: #000; }}
        .badge-secondary {{ background-color: #6c757d; }}
        .footer {{
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #dee2e6;
            text-align: center;
            color: #666;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{results.project_name} {language_badge}</h1>
            <div class="timestamp">Generated: {results.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</div>
            <div style="margin-top: 10px;">
                <span class="status-badge {badge_class}">{status_text}</span>
            </div>
        </div>
        
        <div class="summary">
            <div class="summary-card total">
                <h3>Total Tests</h3>
                <div class="value">{results.total}</div>
            </div>
            <div class="summary-card passed">
                <h3>Passed</h3>
                <div class="value">{results.passed}</div>
            </div>
            <div class="summary-card failed">
                <h3>Failed</h3>
                <div class="value">{results.failed}</div>
            </div>
            <div class="summary-card skipped">
                <h3>Skipped</h3>
                <div class="value">{results.skipped}</div>
            </div>
            <div class="summary-card duration">
                <h3>Duration</h3>
                <div class="value">{results.duration:.2f}s</div>
            </div>
            <div class="summary-card rate">
                <h3>Success Rate</h3>
                <div class="value">{results.success_rate:.1f}%</div>
            </div>
        </div>
        
        <h2>Test Results</h2>
        <table>
            <thead>
                <tr>
                    <th>#</th>
                    <th>Language</th>
                    <th>Test Name</th>
                    <th>Status</th>
                    <th>Duration</th>
                    <th>Details</th>
                </tr>
            </thead>
            <tbody>
                {results_rows}
            </tbody>
        </table>
        
        <div class="footer">
            <p>Generated by TestGen-AI | Universal Multi-Language Testing Framework</p>
            <p><small>Supports: Python, JavaScript, TypeScript, Java, Go, C#, Ruby, Rust, PHP, Swift, Kotlin, C++, HTML, CSS</small></p>
        </div>
    </div>
</body>
</html>"""
        
        return html
    
    def generate_json(
        self,
        results: ExecutionSummary,
        output_path: str
    ) -> str:
        """
        Generate a JSON report from test execution results.
        
        Args:
            results: ExecutionSummary containing test results
            output_path: Path where the JSON report will be saved
            
        Returns:
            Path to the generated JSON report
        """
        if not isinstance(results, ExecutionSummary):
            raise ValueError("results must be an ExecutionSummary instance")
        
        # Convert to dictionary
        report_data = results.to_dict()
        
        # Write to file
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with output_file.open('w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            raise IOError(f"Failed to write report to {output_path}: {e}")
        
        return str(output_file.absolute())
    
    def render_template(
        self,
        results: ExecutionSummary,
        template_path: str = "templates/report.html"
    ) -> str:
        """
        Render HTML report using Jinja2 template.
        
        Loads template from file and renders it with test results context.
        
        Args:
            results: ExecutionSummary containing test results
            template_path: Path to Jinja2 template file
            
        Returns:
            Rendered HTML string
            
        Raises:
            ValueError: If results are invalid
            FileNotFoundError: If template file not found
        """
        if not isinstance(results, ExecutionSummary):
            raise ValueError("results must be an ExecutionSummary instance")
        
        try:
            from jinja2 import Environment, FileSystemLoader, select_autoescape
        except ImportError:
            raise ImportError("Jinja2 is required for template rendering. Install it with: pip install jinja2")
        
        # Get template directory and filename
        template_file = Path(template_path)
        if not template_file.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")
        
        template_dir = str(template_file.parent)
        template_name = template_file.name
        
        # Create Jinja2 environment
        env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )
        
        # Load template
        template = env.get_template(template_name)
        
        # Prepare context
        context = self._prepare_template_context(results)
        
        # Render template
        html = template.render(**context)
        
        return html
    
    def _prepare_template_context(self, results: ExecutionSummary) -> Dict[str, Any]:
        """
        Prepare context dictionary for template rendering.
        
        Args:
            results: ExecutionSummary containing test results
            
        Returns:
            Context dictionary for template
        """
        # Determine status
        if results.failed > 0:
            status_color = "#dc3545"  # Red
            status_text = "FAILED"
        elif results.skipped > 0:
            status_color = "#ffc107"  # Yellow
            status_text = "PARTIAL"
        elif results.passed == results.total and results.total > 0:
            status_color = "#28a745"  # Green
            status_text = "PASSED"
        else:
            status_color = "#6c757d"  # Gray
            status_text = "NO TESTS"
        
        # Build context
        context = {
            'project_name': results.project_name,
            'language': results.language,
            'timestamp': results.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'status_color': status_color,
            'status_text': status_text,
            'total': results.total,
            'passed': results.passed,
            'failed': results.failed,
            'skipped': results.skipped,
            'duration': results.duration,
            'success_rate': results.success_rate,
            'results': results.results
        }
        
        return context
    
    def generate_html_from_template(
        self,
        results: ExecutionSummary,
        output_path: str,
        template_path: str = "templates/report.html"
    ) -> str:
        """
        Generate HTML report using Jinja2 template and save to file.
        
        Combines render_template() and file saving.
        
        Args:
            results: ExecutionSummary containing test results
            output_path: Path where the HTML report will be saved
            template_path: Path to Jinja2 template file
            
        Returns:
            Path to the generated HTML report
            
        Raises:
            ValueError: If results are invalid
            FileNotFoundError: If template not found
            IOError: If file cannot be written
        """
        # Render template
        html_content = self.render_template(results, template_path)
        
        # Write to file
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            output_file.write_text(html_content, encoding='utf-8')
        except IOError as e:
            raise IOError(f"Failed to write report to {output_path}: {e}")
        
        return str(output_file.absolute())
    
    def save_history(
        self,
        results: ExecutionSummary,
        history_file: str = ".testgen_history.json"
    ) -> None:
        """
        Save current test results to history file.
        
        Args:
            results: ExecutionSummary to save
            history_file: Path to history file
        """
        import json
        from datetime import datetime
        
        history_path = Path(history_file)
        
        # Load existing history
        history = []
        if history_path.exists():
            try:
                with history_path.open('r') as f:
                    history = json.load(f)
            except:
                history = []
        
        # Add current results
        history_entry = {
            'timestamp': datetime.now().isoformat(),
            'project_name': results.project_name,
            'language': results.language,
            'total': results.total,
            'passed': results.passed,
            'failed': results.failed,
            'skipped': results.skipped,
            'duration': results.duration,
            'success_rate': results.success_rate,
            'results': results.results
        }
        
        history.append(history_entry)
        
        # Keep last 10 runs
        history = history[-10:]
        
        # Save history
        with history_path.open('w') as f:
            json.dump(history, f, indent=2)
    
    def load_history(
        self,
        history_file: str = ".testgen_history.json"
    ) -> List[Dict[str, Any]]:
        """
        Load historical test results.
        
        Args:
            history_file: Path to history file
            
        Returns:
            List of historical results
        """
        import json
        
        history_path = Path(history_file)
        if not history_path.exists():
            return []
        
        try:
            with history_path.open('r') as f:
                return json.load(f)
        except:
            return []
    
    def compare_with_previous(
        self,
        current: ExecutionSummary,
        history_file: str = ".testgen_history.json"
    ) -> Dict[str, Any]:
        """
        Compare current results with previous run.
        
        Args:
            current: Current ExecutionSummary
            history_file: Path to history file
            
        Returns:
            Comparison dictionary with trends and new failures
        """
        history = self.load_history(history_file)
        
        if not history:
            return {
                'has_previous': False,
                'trend': 'UNKNOWN',
                'new_failures': [],
                'fixed_tests': [],
                'success_rate_change': 0.0
            }
        
        # Get previous run
        previous = history[-1]
        
        # Calculate trend
        current_rate = current.success_rate
        prev_rate = previous['success_rate']
        rate_change = current_rate - prev_rate
        
        if rate_change > 5:
            trend = 'IMPROVING'
        elif rate_change < -5:
            trend = 'DEGRADING'
        else:
            trend = 'STABLE'
        
        # Find new failures
        prev_failed_tests = {
            r['test_name'] for r in previous.get('results', [])
            if r.get('status') == 'FAIL'
        }
        current_failed_tests = {
            r['test_name'] for r in current.results
            if r.get('status') == 'FAIL'
        }
        
        new_failures = list(current_failed_tests - prev_failed_tests)
        fixed_tests = list(prev_failed_tests - current_failed_tests)
        
        return {
            'has_previous': True,
            'trend': trend,
            'new_failures': new_failures,
            'fixed_tests': fixed_tests,
            'success_rate_change': rate_change,
            'previous_passed': previous['passed'],
            'previous_failed': previous['failed'],
            'previous_rate': prev_rate
        }



# Factory function
def create_reporter() -> ReportGenerator:
    """
    Create a ReportGenerator instance.
    
    Returns:
        ReportGenerator instance
    """
    return ReportGenerator()
