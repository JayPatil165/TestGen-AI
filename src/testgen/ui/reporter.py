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
        errors: int = 0,
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
            errors: Number of tests with errors
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
        self.errors = errors
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
            'errors': self.errors,
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
        if results.total == 0:
            status_color = "#6c757d"
            status_text = "NO TESTS"
            badge_class = "no-tests"
        elif results.failed > 0 and results.passed == 0:
            status_color = "#dc3545"
            status_text = "ALL FAILED"
            badge_class = "failed"
        elif results.failed > 0:
            status_color = "#fd7e14"
            status_text = "PARTIAL PASS"
            badge_class = "partial"
        elif results.errors > 0 and results.passed == 0:
            status_color = "#dc3545"
            status_text = "ERRORS"
            badge_class = "failed"
        elif results.passed == results.total and results.total > 0:
            status_color = "#28a745"
            status_text = "ALL PASSED"
            badge_class = "passed"
        else:
            status_color = "#ffc107"
            status_text = "PARTIAL"
            badge_class = "partial"
        
        # Format language badge
        language_badge = ""
        if results.language:
            language_badge = f'<span class="badge language-badge">{results.language.upper()}</span>'
        
        # Extract project directory name from results
        project_dir_name = Path(results.project_name.replace('Test Report for ', '')).name if 'Test Report for ' in results.project_name else 'Project'
        
        # Collect unique languages and compute language-wise stats
        language_stats = {}
        for test_result in results.results:
            lang = test_result.get('language', 'unknown').lower()
            if lang not in language_stats:
                language_stats[lang] = {'total': 0, 'passed': 0, 'failed': 0, 'skipped': 0}
            language_stats[lang]['total'] += 1
            status = test_result.get('status', 'UNKNOWN').upper()
            if status == 'PASS':
                language_stats[lang]['passed'] += 1
            elif status == 'FAIL':
                language_stats[lang]['failed'] += 1
            elif status in ['SKIP', 'SKIPPED']:
                language_stats[lang]['skipped'] += 1
        
        # Generate test results table rows with details for ALL tests
        results_rows = ""
        for i, test_result in enumerate(results.results, 1):
            status = test_result.get('status', 'UNKNOWN').upper()
            test_name = test_result.get('test_name', 'Unknown Test')
            duration = test_result.get('duration', 0.0)
            duration_ns = duration * 1_000_000_000  # Convert to nanoseconds
            message = test_result.get('message', '')
            details = test_result.get('details', '')
            lang = test_result.get('language', 'unknown').lower()
            
            # Generate insightful details for passed tests if none provided
            if status == 'PASS' and not details and not message:
                # Extract meaningful info from test name
                if 'test_' in test_name:
                    test_part = test_name.split('::')[-1].replace('test_', '').replace('_', ' ').title()
                    details = f'✓ {test_part} validation passed'
                else:
                    details = '✓ All assertions passed'
            elif not details:
                details = message or 'No details available'
            
            # Single-line status badge with better colors
            if status == 'PASS':
                status_badge = '<span class="status-badge status-pass">PASS</span>'
            elif status == 'FAIL':
                status_badge = '<span class="status-badge status-fail">FAIL</span>'
            elif status in ['SKIP', 'SKIPPED']:
                status_badge = '<span class="status-badge status-skip">SKIP</span>'
            elif status == 'ERROR':
                status_badge = '<span class="status-badge status-error">ERROR</span>'
            else:
                status_badge = f'<span class="status-badge status-other">{status}</span>'
            
            results_rows += f"""
                <tr data-status="{status}" data-language="{lang}" data-duration="{duration_ns}">
                    <td>{i}</td>
                    <td><span class="lang-tag">{lang.upper()}</span></td>
                    <td class="test-name-cell">{test_name}</td>
                    <td>{status_badge}</td>
                    <td class="duration-cell">{duration_ns:,.0f}ns</td>
                    <td class="details-cell">{details}</td>
                </tr>
            """
        
        # Prepare chart data with language stats
        chart_data_json = json.dumps({
            'passed': results.passed,
            'failed': results.failed,
            'skipped': results.skipped,
            'total': results.total,
            'languages': language_stats
        })
        
        # Format language badge (smaller for title)
        language_badge = ""
        if results.language:
            language_badge = f'<span class="title-lang-badge">{results.language.upper()}</span>'
        
        # Build complete HTML
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TestGen-AI Report ({project_dir_name})</title>
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
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            overflow: hidden;
        }}

        .header {{
            background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
            color: white;
            padding: 40px;
            border-bottom: none;
            position: relative;
        }}

        .header-actions {{
            position: absolute;
            top: 20px;
            right: 20px;
            display: flex;
            gap: 10px;
        }}

        .btn-download {{
            background: rgba(255, 255, 255, 0.2);
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.4);
            padding: 8px 16px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 0.9em;
            font-weight: 500;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            gap: 6px;
        }}

        .btn-download:hover {{
            background: rgba(255, 255, 255, 0.3);
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        }}

        h1 {{
            font-size: 2em;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            gap: 12px;
            font-weight: 700;
            color: white;
        }}

        .title-lang-badge {{
            background: rgba(255, 255, 255, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.3);
            color: white;
            padding: 4px 12px;
            border-radius: 6px;
            font-size: 0.45em;
            font-weight: 600;
            letter-spacing: 0.5px;
        }}

        .timestamp {{
            font-size: 0.9em;
            color: rgba(255, 255, 255, 0.9);
            margin-top: 6px;
            font-weight: 400;
        }}

        .status-badge {{
            display: inline-block;
            padding: 8px 16px;
            border-radius: 8px;
            font-weight: 600;
            font-size: 0.9em;
            margin-top: 16px;
            backdrop-filter: blur(10px);
        }}
        
        .status-badge.passed {{
            background: rgba(16, 185, 129, 0.2);
            color: #d1fae5;
            border: 2px solid rgba(16, 185, 129, 0.5);
        }}
        
        .status-badge.failed {{
            background: rgba(239, 68, 68, 0.2);
            color: #fecaca;
            border: 2px solid rgba(239, 68, 68, 0.5);
        }}
        
        .status-badge.partial {{
            background: rgba(245, 158, 11, 0.2);
            color: #fde68a;
            border: 2px solid rgba(245, 158, 11, 0.5);
        }}
        
        .status-badge.no-tests {{
            background: rgba(156, 163, 175, 0.2);
            color: #e5e7eb;
            border: 2px solid rgba(156, 163, 175, 0.5);
        }}

        /* Single-line status badges in table - softer colors */
        table .status-badge {{
            padding: 3px 10px;
            border-radius: 6px;
            font-size: 0.7em;
            font-weight: 600;
            letter-spacing: 0.5px;
            margin: 0;
            display: inline-block;
            min-width: 60px;
            text-align: center;
        }}

        .status-pass {{
            background: #d1f4e0;
            color: #166534;
            border: 1px solid #86efac;
        }}

        .status-fail {{
            background: #fecaca;
            color: #991b1b;
            border: 1px solid #fca5a5;
        }}

        .status-skip {{
            background: #fed7aa;
            color: #9a3412;
            border: 1px solid #fdba74;
        }}

        .status-error {{
            background: #fecaca;
            color: #7f1d1d;
            border: 1px solid #f87171;
        }}

        .status-other {{
            background: #e5e7eb;
            color: #374151;
            border: 1px solid #d1d5db;
        }}

        .lang-tag {{
            background: #dbeafe;
            border: 1px solid #93c5fd;
            color: #1e40af;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.7em;
            font-weight: 500;
            letter-spacing: 0.3px;
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

        /* Filter section */
        .filters-section {{
            background: white;
            padding: 24px;
            border-radius: 12px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            border: 1px solid #e5e7eb;
        }}

        .filters-section h3 {{
            font-size: 1.1em;
            margin-bottom: 18px;
            color: #111827;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .filters-section h3::before {{
            content: '⚡';
            font-size: 1.2em;
        }}

        .filters-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 18px;
        }}

        .filter-group {{
            display: flex;
            flex-direction: column;
            gap: 6px;
        }}

        .filter-group label {{
            font-size: 0.8em;
            color: #6b7280;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        .filter-group select,
        .filter-group input {{
            padding: 10px 14px;
            border: 1.5px solid #d1d5db;
            border-radius: 8px;
            font-size: 0.9em;
            background: white;
            transition: all 0.2s ease;
        }}

        .filter-group select:focus,
        .filter-group input:focus {{
            outline: none;
            border-color: #3b82f6;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }}

        .filter-actions {{
            display: flex;
            gap: 12px;
            align-items: flex-end;
        }}

        .btn {{
            padding: 10px 18px;
            border: none;
            border-radius: 8px;
            font-size: 0.9em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
        }}

        .btn-primary {{
            background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%);
            color: white;
            box-shadow: 0 2px 4px rgba(37, 99, 235, 0.3);
        }}

        .btn-primary:hover {{
            transform: translateY(-1px);
            box-shadow: 0 4px 8px rgba(37, 99, 235, 0.4);
        }}

        .btn-secondary {{
            background: #f3f4f6;
            color: #374151;
        }}

        .btn-secondary:hover {{
            background: #d1d5db;
        }}

        .filter-info {{
            margin-top: 10px;
            font-size: 0.85em;
            color: #6b7280;
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
            background: linear-gradient(135deg, rgba(var(--card-rgb), 0.1) 0%, rgba(var(--card-rgb), 0.05) 100%);
            border: 2px solid rgba(var(--card-rgb), 0.3);
            color: rgb(var(--card-rgb));
            padding: 24px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }}

        .summary-card::before {{
            content: '';
            position: absolute;
            top: -50%;
            right: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(var(--card-rgb), 0.1) 0%, transparent 70%);
            transition: transform 0.6s;
        }}

        .summary-card:hover {{
            background: linear-gradient(135deg, rgba(var(--card-rgb), 0.15) 0%, rgba(var(--card-rgb), 0.08) 100%);
            box-shadow: 0 8px 16px rgba(var(--card-rgb), 0.2);
            transform: translateY(-4px);
            border-color: rgba(var(--card-rgb), 0.5);
        }}

        .summary-card:hover::before {{
            transform: translate(-50%, -50%);
        }}

        .summary-card.total {{
            --card-rgb: 99, 102, 241;
        }}

        .summary-card.passed {{
            --card-rgb: 34, 197, 94;
        }}

        .summary-card.failed {{
            --card-rgb: 239, 68, 68;
        }}

        .summary-card.skipped {{
            --card-rgb: 251, 146, 60;
        }}

        .summary-card.duration {{
            --card-rgb: 59, 130, 246;
        }}

        .summary-card.rate {{
            --card-rgb: 168, 85, 247;
        }}

        .summary-card h3 {{
            font-size: 0.75em;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: inherit;
            margin-bottom: 12px;
            font-weight: 700;
            opacity: 0.8;
            position: relative;
            z-index: 1;
        }}

        .summary-card .value {{
            font-size: 2.5em;
            font-weight: 700;
            line-height: 1;
            position: relative;
            z-index: 1;
        }}

        /* Charts Section */
        .charts-section {{
            margin-top: 40px;
            margin-bottom: 40px;
        }}

        .charts-section h2 {{
            font-size: 1.4em;
            margin-bottom: 20px;
            color: #374151;
            border-bottom: 2px solid #6366f1;
            padding-bottom: 10px;
            font-weight: 600;
        }}

        .charts-container {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 25px;
        }}

        .chart-wrapper {{
            background: white;
            padding: 28px;
            border-radius: 12px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            border: 1px solid #e5e7eb;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}

        .chart-wrapper:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        }}

        .chart-wrapper h3 {{
            font-size: 1.15em;
            margin-bottom: 20px;
            color: #111827;
            text-align: center;
            font-weight: 700;
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
            color: #374151;
            border-bottom: 2px solid #6366f1;
            padding-bottom: 10px;
            font-weight: 600;
        }}

        table {{
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            border: 1px solid #e5e7eb;
            font-size: 0.85em;
        }}

        thead {{
            background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
            color: white;
        }}

        th {{
            padding: 14px 18px;
            text-align: left;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.75em;
            letter-spacing: 0.08em;
            cursor: pointer;
            user-select: none;
            transition: background 0.2s ease;
        }}

        th:hover {{
            background: rgba(255, 255, 255, 0.15);
        }}

        th::after {{
            content: '⇅';
            margin-left: 8px;
            opacity: 0.6;
            font-size: 0.9em;
        }}

        td {{
            padding: 12px 18px;
            border-bottom: 1px solid #f0f0f0;
            font-size: 0.9em;
        }}

        tbody tr {{
            transition: all 0.15s ease;
            border-bottom: 1px solid #e5e7eb;
        }}

        tbody tr:hover {{
            background: linear-gradient(90deg, rgba(37, 99, 235, 0.04) 0%, rgba(59, 130, 246, 0.04) 100%);
            transform: translateX(2px);
        }}

        tbody tr:last-child {{
            border-bottom: none;
        }}

        tbody tr:last-child td {{
            border-bottom: none;
        }}

        .test-name-cell {{
            font-weight: 500;
            color: #374151;
        }}

        .duration-cell {{
            color: #6b7280;
            font-family: 'Courier New', monospace;
        }}

        .details-cell {{
            color: #6b7280;
            max-width: 400px;
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
                font-size: 1.4em;
            }}

            .summary-card .value {{
                font-size: 2em;
            }}

            table {{
                font-size: 0.85em;
            }}

            .filters-grid {{
                grid-template-columns: 1fr;
            }}
        }}

        /* Success Banner Notification */
        #successBanner {{
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            color: white;
            padding: 20px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
            z-index: 10000;
            display: none;
            animation: slideDown 0.3s ease-out;
        }}

        #successBanner.show {{
            display: block;
        }}

        @keyframes slideDown {{
            from {{
                transform: translateY(-100%);
                opacity: 0;
            }}
            to {{
                transform: translateY(0);
                opacity: 1;
            }}
        }}

        .banner-content {{
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 20px;
        }}

        .banner-message {{
            flex: 1;
        }}

        .banner-title {{
            font-size: 1.1em;
            font-weight: 700;
            margin-bottom: 6px;
        }}

        .banner-text {{
            font-size: 0.9em;
            opacity: 0.95;
        }}

        .banner-close {{
            background: rgba(255, 255, 255, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.3);
            color: white;
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.2s;
        }}

        .banner-close:hover {{
            background: rgba(255, 255, 255, 0.3);
            transform: scale(1.05);
        }}

        /* Success Banner Notification */
        #successBanner {{
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            color: white;
            padding: 20px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
            z-index: 10000;
            display: none;
            animation: slideDown 0.3s ease-out;
        }}

        #successBanner.show {{
            display: block;
        }}

        @keyframes slideDown {{
            from {{
                transform: translateY(-100%);
                opacity: 0;
            }}
            to {{
                transform: translateY(0);
                opacity: 1;
            }}
        }}

        .banner-content {{
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 15px;
        }}

        .banner-icon {{
            font-size: 1.4em;
            font-weight: bold;
            flex-shrink: 0;
        }}

        .banner-text {{
            font-size: 0.95em;
            opacity: 0.95;
            flex: 1;
        }}

        .banner-close {{
            background: rgba(255, 255, 255, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.3);
            color: white;
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.2s;
            flex-shrink: 0;
        }}

        .banner-close:hover {{
            background: rgba(255, 255, 255, 0.3);
            transform: scale(1.05);
        }}

        /* Print-friendly styles for PDF generation */
        @media print {{
            * {{
                -webkit-print-color-adjust: exact !important;
                print-color-adjust: exact !important;
                color-adjust: exact !important;
            }}

            @page {{
                margin: 15mm 12mm;
                size: A4 portrait;
            }}

            body {{
                background: white !important;
                padding: 0 !important;
                margin: 0 !important;
            }}

            #successBanner {{
                display: none !important;
            }}

            .container {{
                box-shadow: none !important;
                border-radius: 0 !important;
                max-width: 100% !important;
                width: 100% !important;
                page-break-inside: avoid;
                padding: 0 !important;
            }}

            .header {{
                background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%) !important;
                color: white !important;
                padding: 20px 15px !important;
                page-break-after: avoid;
                page-break-inside: avoid;
                margin: 0 !important;
            }}

            .header h1 {{
                font-size: 1.6em !important;
                margin: 0 0 5px 0 !important;
                text-align: center !important;
            }}

            .header p {{
                font-size: 0.9em !important;
                margin: 0 !important;
                opacity: 0.95;
            }}

            .header-actions {{
                display: none !important;
            }}

            .filters-section {{
                display: none !important;
            }}

            .content {{
                padding: 15px 12mm !important;
                page-break-inside: avoid;
            }}

            /* KPI Cards - Solid backgrounds for print */
            .summary {{
                display: grid !important;
                grid-template-columns: repeat(6, 1fr) !important;
                gap: 10px !important;
                margin-bottom: 20px !important;
                page-break-inside: avoid !important;
            }}

            .summary-card {{
                padding: 15px 10px !important;
                text-align: center !important;
                border: 3px solid !important;
                border-radius: 8px !important;
                page-break-inside: avoid !important;
                position: relative !important;
                overflow: visible !important;
            }}

            .summary-card::before,
            .summary-card::after {{
                display: none !important;
            }}

            .summary-card.total {{
                background: #3b82f6 !important;
                border-color: #1e40af !important;
                color: #000000 !important;
            }}

            .summary-card.passed {{
                background: #10b981 !important;
                border-color: #047857 !important;
                color: #000000 !important;
            }}

            .summary-card.failed {{
                background: #ef4444 !important;
                border-color: #b91c1c !important;
                color: #000000 !important;
            }}

            .summary-card.skipped {{
                background: #f59e0b !important;
                border-color: #d97706 !important;
                color: #000000 !important;
            }}

            .summary-card.duration {{
                background: #06b6d4 !important;
                border-color: #0891b2 !important;
                color: #000000 !important;
            }}

            .summary-card.rate {{
                background: #8b5cf6 !important;
                border-color: #6d28d9 !important;
                color: #000000 !important;
            }}

            .summary-card h3 {{
                font-size: 11px !important;
                color: #000000 !important;
                margin: 0 0 8px 0 !important;
                padding: 0 !important;
                text-transform: uppercase !important;
                letter-spacing: 1px !important;
                font-weight: 700 !important;
                opacity: 1 !important;
                position: relative !important;
                z-index: 10 !important;
            }}

            .summary-card .value {{
                font-size: 26px !important;
                color: #000000 !important;
                font-weight: 900 !important;
                line-height: 1 !important;
                margin: 0 !important;
                padding: 0 !important;
                position: relative !important;
                z-index: 10 !important;
            }}

            .charts-section {{
                display: block !important;
                page-break-before: auto;
                page-break-inside: avoid !important;
                margin-bottom: 20px !important;
                padding: 0 !important;
                visibility: visible !important;
            }}

            .charts-section h2 {{
                font-size: 1.2em !important;
                margin: 10px 0 8px 0 !important;
                color: #1e3a8a !important;
                page-break-after: avoid;
                text-align: center !important;
            }}

            .charts-container {{
                display: flex !important;
                flex-direction: row !important;
                gap: 8px !important;
                justify-content: space-between !important;
                visibility: visible !important;
                page-break-inside: avoid !important;
            }}

            .chart-wrapper {{
                page-break-inside: avoid !important;
                background: white !important;
                padding: 8px !important;
                border: 1px solid #e5e7eb !important;
                border-radius: 4px !important;
                display: block !important;
                visibility: visible !important;
                flex: 1 !important;
                min-width: 0 !important;
            }}

            .chart-wrapper h3 {{
                color: #1e3a8a !important;
                font-size: 0.85em !important;
                margin: 0 0 6px 0 !important;
                text-align: center !important;
            }}

            canvas {{
                max-width: 100% !important;
                height: auto !important;
                page-break-inside: avoid !important;
                display: block !important;
                visibility: visible !important;
            }}

            .results-section {{
                page-break-before: auto;
                page-break-inside: auto;
                margin-bottom: 15px !important;
            }}

            .results-section h2 {{
                page-break-after: avoid;
                margin: 15px 0 10px 0 !important;
                font-size: 1.3em !important;
                color: #1e3a8a !important;
            }}

            table {{
                break-inside: auto !important;
                font-size: 0.7em !important;
                width: 100% !important;
                page-break-inside: auto;
                border-collapse: collapse !important;
                margin-top: 10px;
            }}

            thead {{
                display: table-header-group !important;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            }}

            thead th {{
                color: white !important;
                padding: 8px 6px !important;
                font-size: 0.95em !important;
                font-weight: 600 !important;
                border: none !important;
            }}

            tbody tr {{
                page-break-inside: avoid !important;
                border-bottom: 1px solid #e5e7eb !important;
            }}

            tbody tr:nth-child(even) {{
                background: #f9fafb !important;
            }}

            td {{
                padding: 6px !important;
                font-size: 1em !important;
                vertical-align: top !important;
            }}

            th::after {{
                display: none !important;
            }}

            .test-name-cell {{
                max-width: 220px;
                font-size: 0.95em !important;
                word-wrap: break-word !important;
            }}

            .duration-cell {{
                font-size: 0.9em !important;
                white-space: nowrap;
            }}

            .details-cell {{
                max-width: 200px;
                font-size: 0.88em !important;
                word-wrap: break-word !important;
            }}

            .footer {{
                page-break-before: avoid;
                margin-top: 15px !important;
                padding: 15px 12mm !important;
                font-size: 0.85em !important;
                border-top: 1px solid #e5e7eb !important;
            }}
        }}
    </style>
</head>

<body>
    <!-- Success Banner -->
    <div id="successBanner" class="success-banner">
        <div class="banner-content">
            <span class="banner-icon">✓</span>
            <span id="bannerText" class="banner-text"></span>
            <button onclick="closeBanner()" class="banner-close">×</button>
        </div>
    </div>

    <div class="container">
        <div class="header">
            <div class="header-actions">
                <button class="btn-download" onclick="downloadPDF()">
                    📄 Save as PDF
                </button>
            </div>
            <h1>
                TestGen-AI Test Report
                {language_badge}
            </h1>
            <div class="timestamp">Generated: {results.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</div>
            <div>
                <span class="status-badge {badge_class}">{status_text}</span>
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
                    <div class="value">{results.duration:.3f}s</div>
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
                    <div class="chart-wrapper" id="langChartWrapper">
                        <h3>Results by Language</h3>
                        <canvas id="languageChart"></canvas>
                    </div>
                </div>
            </div>

            <div class="results-section">
                <h2>Test Results</h2>
                
                <!-- Filters Section -->
                <div class="filters-section">
                    <h3>🔍 Filters & Search</h3>
                    <div class="filters-grid">
                        <div class="filter-group">
                            <label for="statusFilter">Status:</label>
                            <select id="statusFilter">
                                <option value="all">All Statuses</option>
                                <option value="PASS">Passed</option>
                                <option value="FAIL">Failed</option>
                                <option value="SKIP">Skipped</option>
                                <option value="ERROR">Error</option>
                            </select>
                        </div>
                        <div class="filter-group">
                            <label for="languageFilter">Language:</label>
                            <select id="languageFilter">
                                <option value="all">All Languages</option>
                            </select>
                        </div>
                        <div class="filter-group">
                            <label for="minDuration">Min Duration (ns):</label>
                            <input type="number" id="minDuration" placeholder="0" step="1" min="0">
                        </div>
                        <div class="filter-group">
                            <label for="maxDuration">Max Duration (ns):</label>
                            <input type="number" id="maxDuration" placeholder="No limit" step="1" min="0">
                        </div>
                    </div>
                    <div class="filter-actions" style="margin-top: 15px;">
                        <button class="btn btn-primary" onclick="applyFilters()">Apply Filters</button>
                        <button class="btn btn-secondary" onclick="resetFilters()">Reset</button>
                        <div class="filter-info" id="filterInfo"></div>
                    </div>
                </div>

                <table id="resultsTable">
                    <thead>
                        <tr>
                            <th onclick="sortTable(0)" style="cursor: pointer;">#</th>
                            <th onclick="sortTable(1)" style="cursor: pointer;">Language</th>
                            <th>Test Name</th>
                            <th onclick="sortTable(3)" style="cursor: pointer;">Status</th>
                            <th onclick="sortTable(4)" style="cursor: pointer;">Duration</th>
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
        // Data from Python
        const chartData = {chart_data_json};

        // Populate language filter
        const languageFilter = document.getElementById('languageFilter');
        const languages = Object.keys(chartData.languages || {{}});
        languages.forEach(lang => {{
            const option = document.createElement('option');
            option.value = lang;
            option.textContent = lang.toUpperCase();
            languageFilter.appendChild(option);
        }});

        // --- CHART CONFIGURATION (Softer colors) ---
        if (typeof Chart !== 'undefined') {{
            Chart.defaults.font.family = "'Segoe UI', 'Roboto', 'Helvetica Neue', sans-serif";
            Chart.defaults.color = '#6b7280';
        }}

        // 1. Result Distribution Chart (Doughnut) - Softer colors
        const resultsCtx = document.getElementById('resultsChart');
        if (resultsCtx && chartData.total > 0) {{
            new Chart(resultsCtx, {{
                type: 'doughnut',
                data: {{
                    labels: ['Passed', 'Failed', 'Skipped'],
                    datasets: [{{
                        data: [chartData.passed, chartData.failed, chartData.skipped],
                        backgroundColor: ['#86efac', '#fca5a5', '#fde68a'],
                        borderWidth: 1,
                        borderColor: ['#22c55e', '#ef4444', '#f59e0b'],
                        hoverOffset: 4
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: '65%',
                    plugins: {{
                        legend: {{ position: 'bottom', labels: {{ padding: 15, font: {{ size: 12 }} }} }}
                    }}
                }}
            }});
        }}

        // 2. Success Rate Chart (Bar - Horizontal) - Softer colors
        const successCtx = document.getElementById('successRateChart');
        if (successCtx && chartData.total > 0) {{
            const successRate = (chartData.passed / chartData.total) * 100;
            const failureRate = 100 - successRate;
            
            new Chart(successCtx, {{
                type: 'bar',
                indexAxis: 'y',
                data: {{
                    labels: ['Success Rate'],
                    datasets: [
                        {{
                            label: 'Success',
                            data: [successRate],
                            backgroundColor: '#86efac',
                            borderColor: '#22c55e',
                            borderWidth: 1,
                            barThickness: 30
                        }},
                        {{
                            label: 'Failure',
                            data: [failureRate],
                            backgroundColor: '#fca5a5',
                            borderColor: '#ef4444',
                            borderWidth: 1,
                            barThickness: 30
                        }}
                    ]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{
                        x: {{ stacked: true, max: 100, grid: {{ display: false }} }},
                        y: {{ stacked: true, grid: {{ display: false }} }}
                    }},
                    plugins: {{ legend: {{ display: true, position: 'bottom', labels: {{ padding: 10, font: {{ size: 11 }} }} }} }}
                }}
            }});
        }}

        // 3. Language-wise Chart (Grouped Bar) - NEW
        const langCtx = document.getElementById('languageChart');
        if (langCtx && Object.keys(chartData.languages || {{}}).length > 0) {{
            const langData = chartData.languages;
            const langLabels = Object.keys(langData).map(l => l.toUpperCase());
            const passedData = Object.values(langData).map(d => d.passed);
            const failedData = Object.values(langData).map(d => d.failed);
            const skippedData = Object.values(langData).map(d => d.skipped);
            
            new Chart(langCtx, {{
                type: 'bar',
                data: {{
                    labels: langLabels,
                    datasets: [
                        {{
                            label: 'Passed',
                            data: passedData,
                            backgroundColor: '#86efac',
                            borderColor: '#22c55e',
                            borderWidth: 1
                        }},
                        {{
                            label: 'Failed',
                            data: failedData,
                            backgroundColor: '#fca5a5',
                            borderColor: '#ef4444',
                            borderWidth: 1
                        }},
                        {{
                            label: 'Skipped',
                            data: skippedData,
                            backgroundColor: '#fde68a',
                            borderColor: '#f59e0b',
                            borderWidth: 1
                        }}
                    ]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{
                        y: {{ beginAtZero: true, grid: {{ color: '#f3f4f6' }} }},
                        x: {{ grid: {{ display: false }} }}
                    }},
                    plugins: {{ 
                        legend: {{ position: 'bottom', labels: {{ padding: 10, font: {{ size: 11 }} }} }} 
                    }}
                }}
            }});
        }} else {{
            document.getElementById('langChartWrapper').style.display = 'none';
        }}

        // --- TABLE FILTERING & SORTING ---
        let sortDirection = {{}};

        function sortTable(columnIndex) {{
            const table = document.getElementById('resultsTable');
            const tbody = table.querySelector('tbody');
            const rows = Array.from(tbody.querySelectorAll('tr'));
            
            const isAscending = sortDirection[columnIndex] !== 'asc';
            sortDirection[columnIndex] = isAscending ? 'asc' : 'desc';

            rows.sort((rowA, rowB) => {{
                let cellA = rowA.children[columnIndex].innerText.trim();
                let cellB = rowB.children[columnIndex].innerText.trim();

                // Duration column (numeric)
                if (columnIndex === 4) {{
                    const numA = parseFloat(rowA.dataset.duration);
                    const numB = parseFloat(rowB.dataset.duration);
                    return isAscending ? numA - numB : numB - numA;
                }}
                
                // Index column (numeric)
                if (columnIndex === 0) {{
                    const numA = parseInt(cellA);
                    const numB = parseInt(cellB);
                    return isAscending ? numA - numB : numB - numA;
                }}
                
                // Text columns
                return isAscending ? cellA.localeCompare(cellB) : cellB.localeCompare(cellA);
            }});

            tbody.append(...rows);
        }}

        function applyFilters() {{
            const statusFilter = document.getElementById('statusFilter').value;
            const languageFilter = document.getElementById('languageFilter').value;
            const minDuration = parseFloat(document.getElementById('minDuration').value) || 0;
            const maxDuration = parseFloat(document.getElementById('maxDuration').value) || Infinity;

            const table = document.getElementById('resultsTable');
            const tbody = table.querySelector('tbody');
            const rows = Array.from(tbody.querySelectorAll('tr'));
            
            let visibleCount = 0;
            
            rows.forEach(row => {{
                if (!row.dataset.status) return; // Skip header/empty rows
                
                const rowStatus = row.dataset.status;
                const rowLanguage = row.dataset.language;
                const rowDuration = parseFloat(row.dataset.duration);
                
                const statusMatch = (statusFilter === 'all' || rowStatus === statusFilter);
                const languageMatch = (languageFilter === 'all' || rowLanguage === languageFilter);
                const durationMatch = (rowDuration >= minDuration && rowDuration <= maxDuration);
                
                if (statusMatch && languageMatch && durationMatch) {{
                    row.style.display = '';
                    visibleCount++;
                }} else {{
                    row.style.display = 'none';
                }}
            }});

            document.getElementById('filterInfo').textContent = 
                `Showing ${{visibleCount}} of ${{rows.length}} tests`;
        }}

        function resetFilters() {{
            document.getElementById('statusFilter').value = 'all';
            document.getElementById('languageFilter').value = 'all';
            document.getElementById('minDuration').value = '';
            document.getElementById('maxDuration').value = '';
            applyFilters();
        }}

        // Helper functions
        function closeBanner() {{
            document.getElementById('successBanner').classList.remove('show');
        }}

        function showBanner(filename) {{
            const banner = document.getElementById('successBanner');
            const bannerText = document.getElementById('bannerText');
            
            // Get the current page location to determine report directory
            const currentPath = window.location.pathname;
            const reportDir = currentPath.substring(0, currentPath.lastIndexOf('/'));
            const reportPath = reportDir.replace(/^.*[\\/]TestGen-AI/, 'TestGen-AI');
            
            bannerText.innerHTML = `Suggested filename: <strong>${{filename}}</strong> • Save location: Your downloads folder • Report: ${{reportPath}}`;
            banner.classList.add('show');
            
            // Auto-hide after 10 seconds
            setTimeout(() => {{
                closeBanner();
            }}, 10000);
        }}

        // --- PDF DOWNLOAD FUNCTION ---
        function downloadPDF() {{
            // Get IST timestamp for suggested filename
            const now = new Date();
            const istOffset = 5.5 * 60 * 60 * 1000;
            const istDate = new Date(now.getTime() + istOffset);
            
            const year = istDate.getUTCFullYear();
            const month = String(istDate.getUTCMonth() + 1).padStart(2, '0');
            const day = String(istDate.getUTCDate()).padStart(2, '0');
            const hour = String(istDate.getUTCHours()).padStart(2, '0');
            const minute = String(istDate.getUTCMinutes()).padStart(2, '0');
            const second = String(istDate.getUTCSeconds()).padStart(2, '0');
            
            const suggestedFilename = `TestGen-AI_Report_${{year}}-${{month}}-${{day}}_${{hour}}-${{minute}}-${{second}}.pdf`;
            
            // Set document title (used as default filename in most browsers)
            const originalTitle = document.title;
            document.title = suggestedFilename.replace('.pdf', '');
            
            // Trigger browser print dialog
            window.print();
            
            // Restore title after print dialog closes
            document.title = originalTitle;
        }}

        // Initialize
        resetFilters();
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
            <div class="subtitle" style="font-size: 1.1em; color: #6b7280; margin-bottom: 12px; font-weight: 500;">by TestGen-AI</div>
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
    
    def generate_pdf(
        self,
        results: ExecutionSummary,
        output_path: str
    ) -> str:
        """
        Generate a PDF report from test execution results by converting HTML to PDF.
        This preserves all the beautiful styling from the HTML report.

        Args:
            results: ExecutionSummary containing test results
            output_path: Path where the PDF report will be saved

        Returns:
            Path to the generated PDF report
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Try weasyprint first (best option - preserves HTML/CSS perfectly)
        try:
            from weasyprint import HTML
            
            # Generate HTML content first
            html_content = self._generate_html_content(results)
            
            # Convert HTML to PDF
            HTML(string=html_content).write_pdf(str(output_file))
            
            return str(output_file)
            
        except ImportError:
            # Fallback: Try pdfkit (requires wkhtmltopdf installed)
            try:
                import pdfkit
                
                # Generate HTML content
                html_content = self._generate_html_content(results)
                
                # Write to temp HTML file
                temp_html = output_file.with_suffix('.tmp.html')
                temp_html.write_text(html_content, encoding='utf-8')
                
                # Convert HTML to PDF
                pdfkit.from_file(str(temp_html), str(output_file))
                
                # Clean up temp file
                temp_html.unlink()
                
                return str(output_file)
                
            except ImportError:
                # Final fallback: Generate HTML report with print-friendly CSS
                # User can use browser's print-to-PDF feature
                html_path = output_file.with_suffix('.html')
                self.generate_html(results, str(html_path))
                
                raise ImportError(
                    "PDF generation requires either 'weasyprint' or 'pdfkit'.\n"
                    f"Install with: pip install weasyprint\n"
                    f"Or use your browser to print the HTML report to PDF: {html_path}\n"
                    "The HTML report has been saved and optimized for PDF printing."
                )

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
