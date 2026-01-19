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
        # Determine status color
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
        
        # Format language badge
        language_badge = ""
        if results.language:
            language_badge = f'<span class="badge" style="background-color: #17a2b8;">{results.language.upper()}</span>'
        
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
                    <td><span class="badge" style="background-color: #17a2b8;">{lang}</span></td>
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
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .summary-card.total {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }}
        .summary-card.passed {{ background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); }}
        .summary-card.failed {{ background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%); }}
        .summary-card.skipped {{ background: linear-gradient(135deg, #f2994a 0%, #f2c94c 100%); }}
        .summary-card.duration {{ background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }}
        .summary-card.rate {{ background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); }}
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
                <span class="status-badge">{status_text}</span>
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
