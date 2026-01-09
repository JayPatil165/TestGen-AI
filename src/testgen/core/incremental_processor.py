"""
Universal Incremental File Processor for TestGen AI.

Processes individual file changes and triggers test generation
for ALL 14 programming languages.
"""

from typing import Optional, Callable, Dict, List
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass

from .change_detector import DetectedChange, UniversalChangeDetector
from .language_config import Language, get_language_config
from .universal_parser import UniversalCodeParser
from .prompt_templates import PromptGenerator
from .llm_client import LLMClient


@dataclass
class ProcessingResult:
    """Result of processing a single file change."""
    
    source_file: Path
    language: Language
    test_file: Optional[Path] = None
    generated_tests: Optional[str] = None
    success: bool = False
    error: Optional[str] = None
    processing_time: float = 0.0
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class UniversalIncrementalProcessor:
    """
    Universal incremental file processor supporting ALL 14 languages.
    
    Processes individual file changes and generates tests incrementally,
    updating only the affected test files.
    """
    
    def __init__(
        self,
        llm_client: Optional[LLMClient] = None,
        auto_save: bool = True
    ):
        """
        Initialize incremental processor.
        
        Args:
            llm_client: LLM client for test generation (optional for dry-run)
            auto_save: Automatically save generated tests
        """
        self.llm_client = llm_client
        self.auto_save = auto_save
        self.parser = UniversalCodeParser()
        self.prompt_generator = PromptGenerator()
        
        self.processing_history: List[ProcessingResult] = []
        self.active_processing: Dict[Path, datetime] = {}
    
    def process_change(self, change: DetectedChange) -> ProcessingResult:
        """
        Process a single file change.
        
        Args:
            change: Detected file change
            
        Returns:
            Processing result
        """
        start_time = datetime.now()
        
        try:
            # Don't process test files
            if change.is_test_file:
                return ProcessingResult(
                    source_file=change.source_file,
                    language=change.language,
                    success=True,
                    error="Skipped: test file (not a source file)"
                )
            
            # Don't process if already processing
            if change.source_file in self.active_processing:
                return ProcessingResult(
                    source_file=change.source_file,
                    language=change.language,
                    success=False,
                    error="Already processing this file"
                )
            
            # Mark as processing
            self.active_processing[change.source_file] = datetime.now()
            
            # Extract code from changed file
            code_content = self._extract_file_content(change.source_file)
            if not code_content:
                return ProcessingResult(
                    source_file=change.source_file,
                    language=change.language,
                    success=False,
                    error="Failed to read file content"
                )
            
            # Parse the code
            parsed = self.parser.parse(code_content, change.language)
            
            # Generate test file path
            test_file = self._get_test_file_path(change.source_file, change.language)
            
            # Generate tests using LLM
            generated_tests = None
            if self.llm_client:
                generated_tests = self._generate_tests_for_file(
                    code_content,
                    change.language,
                    parsed
                )
                
                # Update test file
                if generated_tests and self.auto_save:
                    self._update_test_file(test_file, generated_tests)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            result = ProcessingResult(
                source_file=change.source_file,
                language=change.language,
                test_file=test_file if generated_tests else None,
                generated_tests=generated_tests,
                success=True,
                processing_time=processing_time
            )
            
            self.processing_history.append(result)
            return result
            
        except Exception as e:
            return ProcessingResult(
                source_file=change.source_file,
                language=change.language,
                success=False,
                error=str(e)
            )
        finally:
            # Remove from active processing
            self.active_processing.pop(change.source_file, None)
    
    def _extract_file_content(self, file_path: Path) -> Optional[str]:
        """
        Extract content from a file.
        
        Args:
            file_path: Path to file
            
        Returns:
            File content or None
        """
        try:
            if not file_path.exists():
                return None
            
            return file_path.read_text(encoding='utf-8', errors='ignore')
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return None
    
    def _get_test_file_path(self, source_file: Path, language: Language) -> Path:
        """
        Generate test file path for a source file.
        
        Args:
            source_file: Source file path
            language: Programming language
            
        Returns:
            Test file path
        """
        config = get_language_config(language)
        
        # Get test directory pattern
        test_dir = config.get('test_directory', 'tests')
        
        # Get test naming pattern
        if language == Language.PYTHON:
            # Python: test_filename.py
            test_name = f"test_{source_file.stem}.py"
        elif language == Language.JAVASCRIPT or language == Language.TYPESCRIPT:
            # JS/TS: filename.test.js or filename.spec.ts
            ext = source_file.suffix
            test_name = f"{source_file.stem}.test{ext}"
        elif language == Language.JAVA:
            # Java: FilenameTest.java
            test_name = f"{source_file.stem}Test.java"
        elif language == Language.GO:
            # Go: filename_test.go
            test_name = f"{source_file.stem}_test.go"
        elif language == Language.CSHARP:
            # C#: FilenameTests.cs
            test_name = f"{source_file.stem}Tests.cs"
        elif language == Language.RUBY:
            # Ruby: filename_spec.rb
            test_name = f"{source_file.stem}_spec.rb"
        elif language == Language.RUST:
            # Rust: tests/filename_test.rs
            test_name = f"{source_file.stem}_test.rs"
        elif language == Language.PHP:
            # PHP: FilenameTest.php
            test_name = f"{source_file.stem}Test.php"
        elif language == Language.SWIFT:
            # Swift: FilenameTests.swift
            test_name = f"{source_file.stem}Tests.swift"
        elif language == Language.KOTLIN:
            # Kotlin: FilenameTest.kt
            test_name = f"{source_file.stem}Test.kt"
        elif language == Language.CPP:
            # C++: filename_test.cpp
            test_name = f"{source_file.stem}_test.cpp"
        else:
            # Default pattern
            test_name = f"test_{source_file.stem}{source_file.suffix}"
        
        # Construct test file path
        # If source is in src/, put test in tests/
        # Otherwise, put test in same directory
        if 'src' in source_file.parts:
            # Replace src with tests
            parts = list(source_file.parts)
            if 'src' in parts:
                idx = parts.index('src')
                parts[idx] = test_dir
            test_path = Path(*parts[:-1]) / test_name
        else:
            # Put in tests/ directory at project root
            test_path = Path(test_dir) / test_name
        
        return test_path
    
    def _generate_tests_for_file(
        self,
        code_content: str,
        language: Language,
        parsed_code: Optional[Dict] = None
    ) -> Optional[str]:
        """
        Generate tests for a file using LLM.
        
        Args:
            code_content: Source code content
            language: Programming language
            parsed_code: Optional parsed code structure
            
        Returns:
            Generated test code or None
        """
        if not self.llm_client:
            return None
        
        try:
            # Generate prompt
            prompt = self.prompt_generator.generate_test_prompt(
                code_content,
                language,
                parsed_code
            )
            
            # Get completion from LLM
            response = self.llm_client.generate(prompt)
            
            return response
            
        except Exception as e:
            print(f"Error generating tests: {e}")
            return None
    
    def _update_test_file(self, test_file: Path, test_content: str) -> bool:
        """
        Update (or create) a test file with generated content.
        
        Args:
            test_file: Test file path
            test_content: Generated test content
            
        Returns:
            True if successful
        """
        try:
            # Create directory if it doesn't exist
            test_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Write test content
            test_file.write_text(test_content, encoding='utf-8')
            
            print(f"✅ Updated test file: {test_file}")
            return True
            
        except Exception as e:
            print(f"❌ Error updating test file {test_file}: {e}")
            return False
    
    def get_processing_statistics(self) -> Dict[str, any]:
        """
        Get processing statistics.
        
        Returns:
            Statistics dictionary
        """
        successful = sum(1 for r in self.processing_history if r.success)
        failed = len(self.processing_history) - successful
        
        total_time = sum(r.processing_time for r in self.processing_history)
        avg_time = total_time / len(self.processing_history) if self.processing_history else 0
        
        by_language = {}
        for result in self.processing_history:
            lang = result.language.value
            by_language[lang] = by_language.get(lang, 0) + 1
        
        return {
            "total_processed": len(self.processing_history),
            "successful": successful,
            "failed": failed,
            "currently_processing": len(self.active_processing),
            "total_time": total_time,
            "average_time": avg_time,
            "by_language": by_language
        }
    
    def get_processing_history(
        self,
        language: Optional[Language] = None,
        successful_only: bool = False
    ) -> List[ProcessingResult]:
        """
        Get processing history with optional filtering.
        
        Args:
            language: Filter by language
            successful_only: Only successful results
            
        Returns:
            List of processing results
        """
        results = self.processing_history
        
        if language:
            results = [r for r in results if r.language == language]
        
        if successful_only:
            results = [r for r in results if r.success]
        
        return results


# Integration function
def create_incremental_processor_from_detector(
    detector: UniversalChangeDetector,
    llm_client: Optional[LLMClient] = None,
    auto_save: bool = True
) -> UniversalIncrementalProcessor:
    """
    Create processor and connect it to a change detector.
    
    Args:
        detector: Change detector
        llm_client: LLM client
        auto_save: Auto-save generated tests
        
    Returns:
        Configured processor
    """
    processor = UniversalIncrementalProcessor(llm_client, auto_save)
    
    # Register processor with detector
    def on_change_callback(change: DetectedChange):
        if change.should_trigger_generation:
            result = processor.process_change(change)
            if result.success and result.generated_tests:
                print(f"✨ Generated tests for {change.source_file.name}")
            elif result.error:
                print(f"⚠️  Processing error: {result.error}")
    
    detector.on_change(on_change_callback)
    
    return processor
