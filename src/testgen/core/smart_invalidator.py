"""
Universal Smart Invalidation for TestGen AI.

Intelligently decides when to regenerate tests based on change type
across ALL 14 programming languages.
"""

from typing import Optional, Dict, List
from pathlib import Path
from enum import Enum
from dataclasses import dataclass
from datetime import datetime

from .change_detector import DetectedChange
from .language_config import Language


class InvalidationAction(str, Enum):
    """Action to take based on invalidation decision."""
    REGENERATE = "regenerate"      # Regenerate tests
    SKIP = "skip"                  # Skip regeneration
    DELETE_TEST = "delete_test"    # Delete test file
    DELETE_SOURCE = "delete_source"  # Delete source file (rare)
    NONE = "none"                  # No action


@dataclass
class InvalidationDecision:
    """Decision about whether to regenerate tests."""
    
    action: InvalidationAction
    reason: str
    source_file: Optional[Path] = None
    test_file: Optional[Path] = None
    language: Optional[Language] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class UniversalSmartInvalidator:
    """
    Smart invalidation logic for ALL 14 programming languages.
    
    Decides when to regenerate tests based on:
    - Test file changes → skip (tests already written)
    - Source file changes → regenerate (code changed)
    - File deletions → cleanup
    """
    
    def __init__(self):
        """Initialize smart invalidator."""
        self.decisions: List[InvalidationDecision] = []
        self._regenerations = 0
        self._skips = 0
        self._deletions = 0
    
    def should_regenerate(self, change: DetectedChange) -> InvalidationDecision:
        """
        Decide if tests should be regenerated for a change.
        
        Args:
            change: Detected file change
            
        Returns:
            Invalidation decision
        """
        # Handle test file changes - DON'T regenerate
        if change.is_test_file:
            decision = InvalidationDecision(
                action=InvalidationAction.SKIP,
                reason="Test file changed (not a source file)",
                source_file=None,
                test_file=change.source_file,
                language=change.language
            )
            self._skips += 1
            self.decisions.append(decision)
            return decision
        
        # Handle source file deletions
        if change.event.change_type.value == "deleted":
            corresponding_test = self.get_corresponding_test_file(
                change.source_file,
                change.language
            )
            
            decision = InvalidationDecision(
                action=InvalidationAction.DELETE_TEST,
                reason="Source file deleted, test file should be cleaned up",
                source_file=change.source_file,
                test_file=corresponding_test,
                language=change.language
            )
            self._deletions += 1
            self.decisions.append(decision)
            return decision
        
        # Handle source file changes - REGENERATE
        corresponding_test = self.get_corresponding_test_file(
            change.source_file,
            change.language
        )
        
        decision = InvalidationDecision(
            action=InvalidationAction.REGENERATE,
            reason="Source file changed, regenerating tests",
            source_file=change.source_file,
            test_file=corresponding_test,
            language=change.language
        )
        self._regenerations += 1
        self.decisions.append(decision)
        return decision
    
    def get_corresponding_test_file(
        self,
        source_file: Path,
        language: Language
    ) -> Path:
        """
        Get corresponding test file for a source file.
        
        Args:
            source_file: Source file path
            language: Programming language
            
        Returns:
            Test file path
        """
        # Language-specific test file naming conventions
        if language == Language.PYTHON:
            # test_filename.py
            test_name = f"test_{source_file.stem}.py"
        elif language == Language.JAVASCRIPT or language == Language.TYPESCRIPT:
            # filename.test.js or filename.test.ts
            ext = source_file.suffix
            test_name = f"{source_file.stem}.test{ext}"
        elif language == Language.JAVA:
            # FilenameTest.java
            test_name = f"{source_file.stem}Test.java"
        elif language == Language.GO:
            # filename_test.go
            test_name = f"{source_file.stem}_test.go"
        elif language == Language.CSHARP:
            # FilenameTests.cs
            test_name = f"{source_file.stem}Tests.cs"
        elif language == Language.RUBY:
            # filename_spec.rb
            test_name = f"{source_file.stem}_spec.rb"
        elif language == Language.RUST:
            # filename_test.rs
            test_name = f"{source_file.stem}_test.rs"
        elif language == Language.PHP:
            # FilenameTest.php
            test_name = f"{source_file.stem}Test.php"
        elif language == Language.SWIFT:
            # FilenameTests.swift
            test_name = f"{source_file.stem}Tests.swift"
        elif language == Language.KOTLIN:
            # FilenameTest.kt
            test_name = f"{source_file.stem}Test.kt"
        elif language == Language.CPP:
            # filename_test.cpp
            test_name = f"{source_file.stem}_test.cpp"
        else:
            # Default: test_filename.ext
            test_name = f"test_{source_file.stem}{source_file.suffix}"
        
        # Determine test directory
        # If source is in src/, put test in tests/
        if 'src' in source_file.parts:
            parts = list(source_file.parts)
            if 'src' in parts:
                idx = parts.index('src')
                parts[idx] = 'tests'
            test_path = Path(*parts[:-1]) / test_name
        else:
            # Put in tests/ at project root
            test_path = Path('tests') / test_name
        
        return test_path
    
    def get_corresponding_source_file(
        self,
        test_file: Path,
        language: Language
    ) -> Optional[Path]:
        """
        Get corresponding source file for a test file.
        
        Args:
            test_file: Test file path
            language: Programming language
            
        Returns:
            Source file path or None
        """
        name = test_file.stem
        ext = test_file.suffix
        
        # Strip test patterns to get source name
        if language == Language.PYTHON:
            # test_filename.py → filename.py
            if name.startswith('test_'):
                source_name = name[5:] + ext
            else:
                source_name = name.replace('_test', '') + ext
        elif language == Language.JAVASCRIPT or language == Language.TYPESCRIPT:
            # filename.test.js → filename.js
            source_name = name.replace('.test', '').replace('.spec', '') + ext
        elif language == Language.JAVA:
            # FilenameTest.java → Filename.java
            source_name = name.replace('Test', '') + ext
        elif language == Language.GO:
            # filename_test.go → filename.go
            source_name = name.replace('_test', '') + ext
        elif language == Language.CSHARP:
            # FilenameTests.cs → Filename.cs
            source_name = name.replace('Tests', '').replace('Test', '') + ext
        elif language == Language.RUBY:
            # filename_spec.rb → filename.rb
            source_name = name.replace('_spec', '') + ext
        elif language == Language.RUST:
            # filename_test.rs → filename.rs
            source_name = name.replace('_test', '') + ext
        elif language == Language.PHP:
            # FilenameTest.php → Filename.php
            source_name = name.replace('Test', '') + ext
        elif language == Language.SWIFT:
            # FilenameTests.swift → Filename.swift
            source_name = name.replace('Tests', '').replace('Test', '') + ext
        elif language == Language.KOTLIN:
            # FilenameTest.kt → Filename.kt
            source_name = name.replace('Test', '') + ext
        elif language == Language.CPP:
            # filename_test.cpp → filename.cpp
            source_name = name.replace('_test', '') + ext
        else:
            # Default
            source_name = name.replace('test_', '').replace('_test', '') + ext
        
        # Map tests/ to src/
        if 'tests' in test_file.parts:
            parts = list(test_file.parts)
            if 'tests' in parts:
                idx = parts.index('tests')
                parts[idx] = 'src'
            source_path = Path(*parts[:-1]) / source_name
        else:
            # Assume src/ at project root
            source_path = Path('src') / source_name
        
        return source_path
    
    def get_statistics(self) -> Dict[str, any]:
        """
        Get invalidation statistics.
        
        Returns:
            Statistics dictionary
        """
        by_action = {}
        for decision in self.decisions:
            action = decision.action.value
            by_action[action] = by_action.get(action, 0) + 1
        
        by_language = {}
        for decision in self.decisions:
            if decision.language:
                lang = decision.language.value
                by_language[lang] = by_language.get(lang, 0) + 1
        
        return {
            "total_decisions": len(self.decisions),
            "regenerations": self._regenerations,
            "skips": self._skips,
            "deletions": self._deletions,
            "by_action": by_action,
            "by_language": by_language
        }
    
    def get_recent_decisions(self, n: int = 10) -> List[InvalidationDecision]:
        """Get most recent decisions."""
        return self.decisions[-n:] if self.decisions else []
    
    def clear_history(self) -> None:
        """Clear decision history."""
        self.decisions.clear()
        self._regenerations = 0
        self._skips = 0
        self._deletions = 0


# Convenience function
def create_invalidator() -> UniversalSmartInvalidator:
    """Create a smart invalidator instance."""
    return UniversalSmartInvalidator()
