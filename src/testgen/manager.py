"""
TestGen-AI Workflow Manager

This module orchestrates the complete test generation workflow across all phases:
- Analyze: Scan source files
- Generate: Create tests using LLM
- Execute: Run generated tests
- Report: Generate reports

Supports all 14 languages: Python, JavaScript, TypeScript, Java, Go, C#, Ruby, 
Rust, PHP, Swift, Kotlin, C++, HTML, CSS
"""

from pathlib import Path
from typing import Dict, List, Any, Optional
import json
from datetime import datetime

# Core module imports - with graceful fallback for testing
try:
    from testgen.scanner.code_scanner import CodeScanner
except ImportError:
    CodeScanner = None

try:
    from testgen.llm.llm_client import LLMClient
except ImportError:
    LLMClient = None

try:
    from testgen.runner.test_runner import TestRunner
except ImportError:
    TestRunner = None

try:
    from testgen.watcher.file_watcher import FileWatcher
except ImportError:
    FileWatcher = None

try:
    from testgen.ui.reporter import ReportGenerator, ExecutionSummary
except ImportError:
    ReportGenerator = None
    ExecutionSummary = None

try:
    from testgen.ui.printer import ConsolePrinter
except ImportError:
    ConsolePrinter = None



class WorkflowState:
    """Represents the current state of the workflow."""
    
    def __init__(self):
        self.phase = "IDLE"  # IDLE, ANALYZING, GENERATING, EXECUTING, REPORTING
        self.files_scanned = []
        self.tests_generated = []
        self.test_results = []
        self.report_path = None
        self.errors = []
        self.start_time = None
        self.end_time = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary."""
        return {
            'phase': self.phase,
            'files_scanned': self.files_scanned,
            'tests_generated': self.tests_generated,
            'test_results': self.test_results,
            'report_path': self.report_path,
            'errors': self.errors,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None
        }


class WorkflowManager:
    """
    Orchestrates the complete test generation workflow.
    
    Coordinates all modules: scanner, LLM, runner, watcher, reporter
    """
    
    def __init__(
        self,
        project_path: str = ".",
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the workflow manager.
        
        Args:
            project_path: Root path of the project
            config: Optional configuration dictionary
        """
        self.project_path = Path(project_path)
        self.config = config or {}
        self.state = WorkflowState()
        
        # Initialize all core modules (with None fallback if not available)
        self.scanner = CodeScanner() if CodeScanner else None
        self.llm_client = LLMClient() if LLMClient else None
        self.runner = TestRunner() if TestRunner else None
        self.watcher = FileWatcher() if FileWatcher else None
        self.reporter = ReportGenerator() if ReportGenerator else None
        self.printer = ConsolePrinter() if ConsolePrinter else None
        
        # Workflow settings
        self.language = self.config.get('language', 'python')
        self.output_dir = Path(self.config.get('output_dir', 'tests'))
        self.report_dir = Path(self.config.get('report_dir', 'reports'))
        self.cache_dir = Path(self.config.get('cache_dir', '.testgen-cache'))
        
        # Initialize cache directory
        self.cache_dir.mkdir(exist_ok=True)
        
        # Task 95: Session tracking
        self.session_file = self.cache_dir / "session.json"
        self.operation_log = self.cache_dir / "operations.log"
        self._init_session()
        
        # Task 98: Structured logging
        self._init_logging()
        
        # Task 99: Verbose mode
        self.verbose = self.config.get('verbose', False)
        
    def execute_generate(
        self,
        source_files: Optional[List[str]] = None,
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute Analyze → Generate workflow.
        
        Args:
            source_files: List of source files to analyze (or None to scan all)
            language: Programming language (or None to use default)
            
        Returns:
            Dictionary with generated test results
        """
        self.state.phase = "ANALYZING"
        self.state.start_time = datetime.now()
        
        lang = language or self.language
        
        # Phase 1: Analyze (Scan)
        self.printer.print_header(f"🔍 Analyzing {lang.upper()} Code")
        
        if source_files:
            files = [Path(f) for f in source_files]
        else:
            # Scan all files
            files = self.scanner.scan_directory(
                str(self.project_path),
                language=lang
            )
        
        self.state.files_scanned = [str(f) for f in files]
        self.printer.print_success(f"Found {len(files)} source files")
        
        # Phase 2: Generate (LLM)
        self.state.phase = "GENERATING"
        self.printer.print_header("🤖 Generating Tests with LLM")
        
        generated_tests = []
        for file_path in files:
            try:
                # Read source code
                source_code = file_path.read_text()
                
                # Generate test
                test_code = self.llm_client.generate_test(
                    source_code=source_code,
                    language=lang,
                    file_path=str(file_path)
                )
                
                # Save generated test
                test_file = self._get_test_output_path(file_path, lang)
                test_file.parent.mkdir(parents=True, exist_ok=True)
                test_file.write_text(test_code)
                
                generated_tests.append(str(test_file))
                self.printer.print_success(f"Generated: {test_file.name}")
                
            except Exception as e:
                self.state.errors.append({
                    'file': str(file_path),
                    'phase': 'generate',
                    'error': str(e)
                })
                self.printer.print_error(f"Failed: {file_path.name} - {e}")
        
        self.state.tests_generated = generated_tests
        self.state.end_time = datetime.now()
        self.state.phase = "IDLE"
        
        return {
            'files_scanned': len(files),
            'tests_generated': len(generated_tests),
            'output_dir': str(self.output_dir),
            'language': lang,
            'duration': (self.state.end_time - self.state.start_time).total_seconds()
        }
    
    def execute_test(
        self,
        test_files: Optional[List[str]] = None,
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute test execution workflow.
        
        Args:
            test_files: List of test files to run (or None to run all)
            language: Programming language (or None to use default)
            
        Returns:
            Dictionary with test execution results
        """
        self.state.phase = "EXECUTING"
        self.state.start_time = datetime.now()
        
        lang = language or self.language
        
        self.printer.print_header(f"🧪 Running {lang.upper()} Tests")
        
        # Discover test files if not provided
        if not test_files:
            test_files = self._discover_test_files(lang)
        
        # Run tests
        results = self.runner.run_tests(
            test_files=test_files,
            language=lang
        )
        
        self.state.test_results = results
        self.state.end_time = datetime.now()
        self.state.phase = "IDLE"
        
        return {
            'tests_run': results.get('total', 0),
            'passed': results.get('passed', 0),
            'failed': results.get('failed', 0),
            'skipped': results.get('skipped', 0),
            'duration': results.get('duration', 0),
            'language': lang
        }
    
    def execute_report(
        self,
        results: Optional[Dict[str, Any]] = None,
        format: str = 'html'
    ) -> str:
        """
        Execute report generation workflow.
        
        Args:
            results: Test results (or None to use last execution)
            format: Report format ('html', 'json', 'both')
            
        Returns:
            Path to generated report
        """
        self.state.phase = "REPORTING"
        
        self.printer.print_header("📊 Generating Report")
        
        # Use provided results or last state
        report_data = results or self.state.test_results
        
        if not report_data:
            raise ValueError("No test results available for reporting")
        
        # Create execution summary
        summary = ExecutionSummary(
            project_name=self.project_path.name,
            total=report_data.get('total', 0),
            passed=report_data.get('passed', 0),
            failed=report_data.get('failed', 0),
            skipped=report_data.get('skipped', 0),
            duration=report_data.get('duration', 0),
            language=report_data.get('language', self.language),
            results=report_data.get('results', [])
        )
        
        # Generate reports
        self.report_dir.mkdir(parents=True, exist_ok=True)
        
        reports = []
        
        if format in ['html', 'both']:
            html_path = self.report_dir / "test_report.html"
            self.reporter.generate_html_from_template(summary, str(html_path))
            reports.append(str(html_path))
            self.printer.print_success(f"HTML report: {html_path}")
        
        if format in ['json', 'both']:
            json_path = self.report_dir / "test_report.json"
            self.reporter.generate_json(summary, str(json_path))
            reports.append(str(json_path))
            self.printer.print_success(f"JSON report: {json_path}")
        
        self.state.report_path = reports[0] if reports else None
        self.state.phase = "IDLE"
        
        return reports[0] if reports else None
    
    def execute_auto(
        self,
        source_files: Optional[List[str]] = None,
        language: Optional[str] = None,
        report_format: str = 'both'
    ) -> Dict[str, Any]:
        """
        Execute complete workflow: Analyze → Generate → Execute → Report.
        
        Args:
            source_files: List of source files (or None to scan all)
            language: Programming language (or None to use default)
            report_format: Report format ('html', 'json', 'both')
            
        Returns:
            Dictionary with complete workflow results
        """
        start_time = datetime.now()
        
        self.printer.print_status("🚀 Starting Complete Workflow")
        
        # Step 1: Generate tests
        gen_results = self.execute_generate(source_files, language)
        
        # Step 2: Execute tests
        test_results = self.execute_test(
            test_files=self.state.tests_generated,
            language=language or self.language
        )
        
        # Step 3: Generate report
        report_path = self.execute_report(test_results, report_format)
        
        end_time = datetime.now()
        total_duration = (end_time - start_time).total_seconds()
        
        self.printer.print_status(f"✅ Workflow Complete in {total_duration:.2f}s")
        
        return {
            'generate': gen_results,
            'test': test_results,
            'report': report_path,
            'total_duration': total_duration,
            'errors': self.state.errors
        }
    
    def get_state(self) -> Dict[str, Any]:
        """Get current workflow state."""
        return self.state.to_dict()
    
    def reset_state(self) -> None:
        """Reset workflow state."""
        self.state = WorkflowState()
    
    def _get_test_output_path(self, source_file: Path, language: str) -> Path:
        """
        Generate output path for test file.
        
        Args:
            source_file: Source file path
            language: Programming language
            
        Returns:
            Path for generated test file
        """
        # Determine test file naming convention
        if language == 'python':
            prefix = 'test_'
            ext = '.py'
        elif language in ['javascript', 'typescript']:
            prefix = ''
            suffix = '.test'
            ext = '.js' if language == 'javascript' else '.ts'
        elif language == 'java':
            prefix = ''
            suffix = 'Test'
            ext = '.java'
        else:
            prefix = 'test_'
            ext = source_file.suffix
        
        # Generate test filename
        stem = source_file.stem
        if language in ['javascript', 'typescript', 'java']:
            test_name = f"{stem}{suffix}{ext}"
        else:
            test_name = f"{prefix}{stem}{ext}"
        
        return self.output_dir / test_name
    
    def _discover_test_files(self, language: str) -> List[str]:
        """
        Discover test files in output directory.
        
        Args:
            language: Programming language
            
        Returns:
            List of test file paths
        """
        if not self.output_dir.exists():
            return []
        
        # Get file extension
        ext_map = {
            'python': '.py',
            'javascript': '.js',
            'typescript': '.ts',
            'java': '.java',
            'go': '.go',
            'csharp': '.cs',
            'ruby': '.rb',
            'rust': '.rs',
            'php': '.php',
            'swift': '.swift',
            'kotlin': '.kt',
            'cpp': '.cpp',
            'html': '.html',
            'css': '.css'
        }
        
        ext = ext_map.get(language, '.py')
        
        # Find all test files
        test_files = []
        for file in self.output_dir.glob(f"*test*{ext}"):
            test_files.append(str(file))
        
        return test_files
    
    # Task 94: Result Caching Methods
    
    def cache_scan_results(
        self,
        files: List[str],
        language: str
    ) -> None:
        """
        Cache scan results to file.
        
        Args:
            files: List of scanned file paths
            language: Programming language
        """
        cache_file = self.cache_dir / f"scan_{language}.json"
        cache_data = {
            'language': language,
            'files': files,
            'timestamp': datetime.now().isoformat(),
            'project_path': str(self.project_path)
        }
        
        cache_file.write_text(json.dumps(cache_data, indent=2))
    
    def load_scan_cache(
        self,
        language: str,
        max_age_seconds: int = 3600
    ) -> Optional[List[str]]:
        """
        Load cached scan results.
        
        Args:
            language: Programming language
            max_age_seconds: Maximum age of cache in seconds (default: 1 hour)
            
        Returns:
            List of cached file paths, or None if cache invalid
        """
        cache_file = self.cache_dir / f"scan_{language}.json"
        
        if not cache_file.exists():
            return None
        
        try:
            cache_data = json.loads(cache_file.read_text())
            
            # Check cache age
            cache_time = datetime.fromisoformat(cache_data['timestamp'])
            age = (datetime.now() - cache_time).total_seconds()
            
            if age > max_age_seconds:
                return None  # Cache expired
            
            return cache_data['files']
        except:
            return None
    
    def cache_test_results(
        self,
        results: Dict[str, Any],
        language: str
    ) -> None:
        """
        Cache test execution results.
        
        Args:
            results: Test execution results
            language: Programming language
        """
        cache_file = self.cache_dir / f"test_results_{language}.json"
        cache_data = {
            'language': language,
            'results': results,
            'timestamp': datetime.now().isoformat()
        }
        
        cache_file.write_text(json.dumps(cache_data, indent=2))
    
    def load_test_cache(
        self,
        language: str,
        max_age_seconds: int = 1800
    ) -> Optional[Dict[str, Any]]:
        """
        Load cached test results.
        
        Args:
            language: Programming language
            max_age_seconds: Maximum age of cache in seconds (default: 30 min)
            
        Returns:
            Cached test results, or None if cache invalid
        """
        cache_file = self.cache_dir / f"test_results_{language}.json"
        
        if not cache_file.exists():
            return None
        
        try:
            cache_data = json.loads(cache_file.read_text())
            
            # Check cache age
            cache_time = datetime.fromisoformat(cache_data['timestamp'])
            age = (datetime.now() - cache_time).total_seconds()
            
            if age > max_age_seconds:
                return None  # Cache expired
            
            return cache_data['results']
        except:
            return None
    
    def invalidate_cache(
        self,
        cache_type: str = 'all',
        language: Optional[str] = None
    ) -> None:
        """
        Invalidate caches.
        
        Args:
            cache_type: Type of cache to invalidate ('scan', 'test', 'all')
            language: Specific language cache to invalidate (or None for all)
        """
        if cache_type in ['scan', 'all']:
            if language:
                cache_file = self.cache_dir / f"scan_{language}.json"
                if cache_file.exists():
                    cache_file.unlink()
            else:
                # Remove all scan caches
                for cache_file in self.cache_dir.glob("scan_*.json"):
                    cache_file.unlink()
        
        if cache_type in ['test', 'all']:
            if language:
                cache_file = self.cache_dir / f"test_results_{language}.json"
                if cache_file.exists():
                    cache_file.unlink()
            else:
                # Remove all test caches
                for cache_file in self.cache_dir.glob("test_results_*.json"):
                    cache_file.unlink()
    
    def clear_all_caches(self) -> None:
        """Clear all caches."""
        self.invalidate_cache('all', None)
    
    # Task 95: Session Tracking Methods
    
    def _init_session(self) -> None:
        """Initialize session tracking."""
        session_data = {
            'session_id': datetime.now().strftime('%Y%m%d_%H%M%S'),
            'start_time': datetime.now().isoformat(),
            'current_operation': None,
            'operations': []
        }
        
        self.session_file.write_text(json.dumps(session_data, indent=2))
        
        # Initialize log file
        if not self.operation_log.exists():
            self.operation_log.write_text("")
    
    def start_operation(
        self,
        operation: str,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Start tracking an operation.
        
        Args:
            operation: Operation name ('generate', 'test', 'report', 'auto')
            details: Optional operation details
        """
        # Load session
        session = json.loads(self.session_file.read_text())
        
        # Update current operation
        session['current_operation'] = {
            'name': operation,
            'start_time': datetime.now().isoformat(),
            'details': details or {},
            'status': 'running'
        }
        
        # Save session
        self.session_file.write_text(json.dumps(session, indent=2))
        
        # Log operation start
        self._log_operation(f"START {operation}", details)
    
    def end_operation(
        self,
        operation: str,
        status: str = 'success',
        result: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        End tracking an operation.
        
        Args:
            operation: Operation name
            status: Operation status ('success', 'failed', 'cancelled')
            result: Optional operation result
        """
        # Load session
        session = json.loads(self.session_file.read_text())
        
        if session['current_operation'] and session['current_operation']['name'] == operation:
            current = session['current_operation']
            current['end_time'] = datetime.now().isoformat()
            current['status'] = status
            current['result'] = result or {}
            
            # Calculate duration
            start = datetime.fromisoformat(current['start_time'])
            end = datetime.fromisoformat(current['end_time'])
            current['duration_seconds'] = (end - start).total_seconds()
            
            # Add to operations history
            session['operations'].append(current)
            session['current_operation'] = None
            
            # Save session
            self.session_file.write_text(json.dumps(session, indent=2))
            
            # Log operation end
            self._log_operation(f"END {operation} - {status}", result)
    
    def get_session(self) -> Dict[str, Any]:
        """
        Get current session data.
        
        Returns:
            Session dictionary
        """
        if not self.session_file.exists():
            return {}
        
        return json.loads(self.session_file.read_text())
    
    def get_current_operation(self) -> Optional[Dict[str, Any]]:
        """
        Get currently running operation.
        
        Returns:
            Current operation dict, or None if no operation running
        """
        session = self.get_session()
        return session.get('current_operation')
    
    def get_operation_history(self) -> List[Dict[str, Any]]:
        """
        Get history of all operations.
        
        Returns:
            List of operation dictionaries
        """
        session = self.get_session()
        return session.get('operations', [])
    
    def _log_operation(
        self,
        message: str,
        data: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log operation to file.
        
        Args:
            message: Log message
            data: Optional data to log
        """
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] {message}"
        
        if data:
            log_entry += f" | {json.dumps(data)}"
        
        log_entry += "\n"
        
        # Append to log file
        with self.operation_log.open('a') as f:
            f.write(log_entry)
    
    def get_operation_logs(
        self,
        limit: Optional[int] = None
    ) -> List[str]:
        """
        Get operation logs.
        
        Args:
            limit: Optional limit on number of log entries
            
        Returns:
            List of log entries
        """
        if not self.operation_log.exists():
            return []
        
        logs = self.operation_log.read_text().strip().split('\n')
        logs = [l for l in logs if l]  # Remove empty lines
        
        if limit:
            return logs[-limit:]
        
        return logs
    
    def clear_session(self) -> None:
        """Clear session data and logs."""
        if self.session_file.exists():
            self.session_file.unlink()
        if self.operation_log.exists():
            self.operation_log.unlink()
        
        self._init_session()
    
    # Task 96: Global Error Handler Methods
    
    def handle_error(
        self,
        error: Exception,
        context: str,
        operation: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Global error handler.
        
        Args:
            error: Exception that occurred
            context: Context where error occurred
            operation: Optional operation name
            
        Returns:
            Error information dictionary
        """
        error_info = {
            'type': type(error).__name__,
            'message': str(error),
            'context': context,
            'operation': operation,
            'timestamp': datetime.now().isoformat()
        }
        
        # Log detailed error
        self._log_error(error_info, error)
        
        # Display user-friendly message
        self._display_user_friendly_error(error_info)
        
        # Add to state errors
        self.state.errors.append(error_info)
        
        return error_info
    
    def _log_error(
        self,
        error_info: Dict[str, Any],
        exception: Exception
    ) -> None:
        """
        Log detailed error to file.
        
        Args:
            error_info: Error information dictionary
            exception: The exception object
        """
        error_log = self.cache_dir / "errors.log"
        
        import traceback
        
        log_entry = f"""
{'=' * 70}
ERROR: {error_info['type']}
Time: {error_info['timestamp']}
Context: {error_info['context']}
Operation: {error_info.get('operation', 'N/A')}
Message: {error_info['message']}
Traceback:
{traceback.format_exc()}
{'=' * 70}
"""
        
        # Append to error log
        with error_log.open('a') as f:
            f.write(log_entry)
    
    def _display_user_friendly_error(
        self,
        error_info: Dict[str, Any]
    ) -> None:
        """
        Display user-friendly error message.
        
        Args:
            error_info: Error information dictionary
        """
        error_type = error_info['type']
        message = error_info['message']
        context = error_info['context']
        
        # Map error types to friendly messages
        friendly_messages = {
            'FileNotFoundError': f"❌ File not found: {message}",
            'PermissionError': f"❌ Permission denied: {message}",
            'ValueError': f"❌ Invalid value: {message}",
            'TypeError': f"❌ Type error: {message}",
            'ImportError': f"❌ Module not available: {message}",
            'ConnectionError': f"❌ Connection failed: {message}",
            'TimeoutError': f"❌ Operation timed out: {message}",
        }
        
        friendly_msg = friendly_messages.get(
            error_type,
            f"❌ Error in {context}: {message}"
        )
        
        if self.printer:
            self.printer.print_error(friendly_msg)
        else:
            print(friendly_msg)
    
    def get_error_log(
        self,
        limit: Optional[int] = None
    ) -> List[str]:
        """
        Get error log entries.
        
        Args:
            limit: Optional limit on number of entries
            
        Returns:
            List of error log entries
        """
        error_log = self.cache_dir / "errors.log"
        
        if not error_log.exists():
            return []
        
        content = error_log.read_text()
        
        # Split by separator
        entries = content.split('=' * 70)
        entries = [e.strip() for e in entries if e.strip()]
        
        if limit:
            return entries[-limit:]
        
        return entries
    
    def get_errors(self) -> List[Dict[str, Any]]:
        """
        Get all errors from current session.
        
        Returns:
            List of error dictionaries
        """
        return self.state.errors
    
    def clear_errors(self) -> None:
        """Clear error log and state errors."""
        error_log = self.cache_dir / "errors.log"
        if error_log.exists():
            error_log.unlink()
        
        self.state.errors = []
    
    # Task 97: Rollback Mechanisms
    
    def create_backup(
        self,
        directory: str,
        backup_name: Optional[str] = None
    ) -> str:
        """
        Create backup of directory.
        
        Args:
            directory: Directory to backup
            backup_name: Optional backup name (default: timestamped)
            
        Returns:
            Path to backup directory
        """
        import shutil
        
        source = Path(directory)
        if not source.exists():
            return None
        
        # Generate backup name
        if not backup_name:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f"backup_{timestamp}"
        
        backup_dir = self.cache_dir / "backups" / backup_name
        backup_dir.parent.mkdir(parents=True, exist_ok=True)
        
        # Copy directory
        shutil.copytree(source, backup_dir, dirs_exist_ok=True)
        
        return str(backup_dir)
    
    def restore_backup(
        self,
        backup_path: str,
        target_directory: str
    ) -> bool:
        """
        Restore from backup.
        
        Args:
            backup_path: Path to backup
            target_directory: Directory to restore to
            
        Returns:
            True if successful
        """
        import shutil
        
        backup = Path(backup_path)
        target = Path(target_directory)
        
        if not backup.exists():
            return False
        
        # Remove target if exists
        if target.exists():
            shutil.rmtree(target)
        
        # Restore from backup
        shutil.copytree(backup, target)
        
        return True
    
    def safe_file_operation(
        self,
        operation_func,
        *args,
        backup_dir: Optional[str] = None,
        **kwargs
    ) -> Any:
        """
        Execute file operation with automatic backup/rollback.
        
        Args:
            operation_func: Function to execute
            backup_dir: Optional directory to backup before operation
            *args, **kwargs: Arguments for operation_func
            
        Returns:
            Result of operation_func
        """
        backup_path = None
        
        try:
            # Create backup if directory specified
            if backup_dir:
                backup_path = self.create_backup(backup_dir)
            
            # Execute operation
            result = operation_func(*args, **kwargs)
            
            return result
            
        except Exception as e:
            # Rollback on failure
            if backup_path and backup_dir:
                self.restore_backup(backup_path, backup_dir)
                self.handle_error(e, "safe_file_operation", "rollback")
            
            raise
    
    # Task 98: Structured Logging System
    
    def _init_logging(self) -> None:
        """Initialize structured logging system."""
        import logging
        
        # Create logs directory
        log_dir = Path(".testgen") / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / "testgen.log"
        
        # Configure logger
        self.logger = logging.getLogger("testgen")
        self.logger.setLevel(logging.DEBUG)
        
        # File handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        
        # Add handler if not already added
        if not self.logger.handlers:
            self.logger.addHandler(file_handler)
    
    def log_debug(self, message: str, **kwargs) -> None:
        """Log debug message."""
        if hasattr(self, 'logger'):
            self.logger.debug(message, extra=kwargs)
    
    def log_info(self, message: str, **kwargs) -> None:
        """Log info message."""
        if hasattr(self, 'logger'):
            self.logger.info(message, extra=kwargs)
    
    def log_warning(self, message: str, **kwargs) -> None:
        """Log warning message."""
        if hasattr(self, 'logger'):
            self.logger.warning(message, extra=kwargs)
    
    def log_error(self, message: str, **kwargs) -> None:
        """Log error message."""
        if hasattr(self, 'logger'):
            self.logger.error(message, extra=kwargs)
    
    # Task 99: Verbose Mode
    
    def set_verbose(self, enabled: bool) -> None:
        """Enable or disable verbose mode."""
        self.verbose = enabled
        if self.verbose:
            self.log_info("Verbose mode enabled")
    
    def verbose_print(self, message: str, **kwargs) -> None:
        """Print message if verbose mode is enabled."""
        if self.verbose:
            if self.printer:
                self.printer.print_info(message)
            else:
                print(f"[VERBOSE] {message}")
            
            # Also log to file
            self.log_debug(f"VERBOSE: {message}", **kwargs)
    
    # Task 100: Configuration Integration
    
    @staticmethod
    def load_config(config_file: str = "config.py") -> Dict[str, Any]:
        """
        Load configuration from file, environment variables, and CLI.
        
        Priority: CLI flags > Environment variables > Config file
        
        Args:
            config_file: Path to configuration file
            
        Returns:
            Merged configuration dictionary
        """
        import os
        
        config = {}
        
        # 1. Load from config file if exists
        config_path = Path(config_file)
        if config_path.exists():
            # Read Python config file
            config_content = config_path.read_text()
            exec_globals = {}
            exec(config_content, exec_globals)
            config = {k: v for k, v in exec_globals.items() if not k.startswith('__')}
        
        # 2. Override with environment variables
        env_mapping = {
            'TESTGEN_LANGUAGE': 'language',
            'TESTGEN_OUTPUT_DIR': 'output_dir',
            'TESTGEN_REPORT_DIR': 'report_dir',
            'TESTGEN_CACHE_DIR': 'cache_dir',
            'TESTGEN_VERBOSE': 'verbose',
        }
        
        for env_var, config_key in env_mapping.items():
            if env_var in os.environ:
                value = os.environ[env_var]
                # Convert boolean strings
                if value.lower() in ['true', '1', 'yes']:
                    value = True
                elif value.lower() in ['false', '0', 'no']:
                    value = False
                config[config_key] = value
        
        return config
    
    @staticmethod
    def validate_config(config: Dict[str, Any]) -> bool:
        """
        Validate configuration settings.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            True if valid, raises ValueError if invalid
        """
        # Validate language
        valid_langs = ['python', 'javascript', 'typescript', 'java', 'go', 'csharp',
                       'ruby', 'rust', 'php', 'swift', 'kotlin', 'cpp', 'html', 'css']
        if 'language' in config and config['language'] not in valid_langs:
            raise ValueError(f"Invalid language: {config['language']}")
        
        # Validate paths exist if specified
        for path_key in ['output_dir', 'report_dir', 'cache_dir']:
            if path_key in config:
                path = Path(config[path_key])
                # Create if doesn't exist (validation with auto-fix)
                path.mkdir(parents=True, exist_ok=True)
        
        return True



# Factory function
def create_manager(
    project_path: str = ".",
    config: Optional[Dict[str, Any]] = None
) -> WorkflowManager:
    """
    Create a WorkflowManager instance.
    
    Args:
        project_path: Root path of the project
        config: Optional configuration dictionary
        
    Returns:
        WorkflowManager instance
    """
    return WorkflowManager(project_path, config)
