"""
Code Scanner Module for TestGen AI.

This module provides intelligent code scanning and analysis capabilities.
It recursively scans directories, filters noise, and extracts code context
optimized for LLM consumption.
"""

import ast
from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum

from testgen.config import config


class FileType(str, Enum):
    """Supported file types for scanning."""
    # Programming Languages
    PYTHON = ".py"
    JAVASCRIPT = ".js"
    TYPESCRIPT = ".ts"
    JSX = ".jsx"
    TSX = ".tsx"
    JAVA = ".java"
    C = ".c"
    CPP = ".cpp"
    HEADER = ".h"
    HPP = ".hpp"
    CSHARP = ".cs"
    GO = ".go"
    RUST = ".rs"
    PHP = ".php"
    
    # Web Languages
    HTML = ".html"
    HTM = ".htm"
    CSS = ".css"
    SCSS = ".scss"
    SASS = ".sass"
    LESS = ".less"
    
    # Markup & Data Languages
    XML = ".xml"
    JSON = ".json"
    YAML = ".yaml"
    YML = ".yml"
    MARKDOWN = ".md"
    
    # Database
    SQL = ".sql"
    
    UNKNOWN = "unknown"


@dataclass
class CodeFile:
    """Represents a scanned code file."""
    path: Path
    relative_path: Path
    file_type: FileType
    size_bytes: int
    line_count: int
    functions: List[str] = field(default_factory=list)
    classes: List[str] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    content: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "path": str(self.path),
            "relative_path": str(self.relative_path),
            "file_type": self.file_type.value,
            "size_bytes": self.size_bytes,
            "line_count": self.line_count,
            "functions": self.functions,
            "classes": self.classes,
            "imports": self.imports,
            "has_content": self.content is not None
        }


@dataclass
class ScanResult:
    """Results from a directory scan."""
    root_path: Path
    files: List[CodeFile] = field(default_factory=list)
    total_files: int = 0
    total_lines: int = 0
    ignored_paths: Set[str] = field(default_factory=set)
    errors: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "root_path": str(self.root_path),
            "total_files": self.total_files,
            "total_lines": self.total_lines,
            "files": [f.to_dict() for f in self.files],
            "ignored_paths": list(self.ignored_paths),
            "errors": self.errors
        }
    
    def get_summary(self) -> str:
        """Get a human-readable summary."""
        return (
            f"Scanned {self.total_files} files\n"
            f"Total lines: {self.total_lines:,}\n"
            f"Ignored paths: {len(self.ignored_paths)}\n"
            f"Errors: {len(self.errors)}"
        )


class CodeScanner:
    """
    Intelligent code scanner for extracting source code information.
    
    Features:
    - Recursive directory traversal
    - Intelligent filtering (gitignore, custom patterns)
    - Multi-language support (Python, JS, TS, Java)
    - Function/class extraction
    - Smart context optimization for LLMs
    """
    
    def __init__(self, ignore_patterns: Optional[List[str]] = None, include_config_files: bool = False):
        """
        Initialize the scanner.
        
        Args:
            ignore_patterns: Custom patterns to ignore (uses config defaults if None)
            include_config_files: Whether to include configuration files in scan
        """
        self.ignore_patterns = ignore_patterns or config.ignore_patterns
        self.supported_extensions = config.supported_extensions
        self.max_file_size_lines = config.max_file_size_lines
        self.include_config_files = include_config_files
    
    def scan_directory(self, path: str | Path) -> ScanResult:
        """
        Scan a directory and extract code information.
        
        Args:
            path: Path to the directory to scan
            
        Returns:
            ScanResult containing all scanned files and metadata
            
        Raises:
            ValueError: If path doesn't exist or isn't a directory
        """
        root_path = Path(path).resolve()
        
        # Validate path
        if not root_path.exists():
            raise ValueError(f"Path does not exist: {root_path}")
        
        if not root_path.is_dir():
            raise ValueError(f"Path is not a directory: {root_path}")
        
        # Initialize result
        result = ScanResult(root_path=root_path)
        
        # Read .gitignore patterns if available and merge with default patterns
        gitignore_patterns = self._read_gitignore(root_path)
        all_patterns = list(set(self.ignore_patterns + gitignore_patterns))
        
        # Temporarily use merged patterns for this scan
        original_patterns = self.ignore_patterns
        self.ignore_patterns = all_patterns
        
        if len(gitignore_patterns) > 0:
            # Log that we found and are using gitignore
            result.ignored_paths.add(f".gitignore (loaded {len(gitignore_patterns)} patterns)")
        
        try:
            for item in root_path.rglob("*"):
                # Skip if should be ignored
                if self._should_ignore(item, root_path):
                    result.ignored_paths.add(str(item.relative_to(root_path)))
                    continue
                
                # Only process files
                if not item.is_file():
                    continue
                
                # Skip binary files
                if self._is_binary_file(item):
                    result.ignored_paths.add(f"{item.relative_to(root_path)} (binary)")
                    continue
                
                # Skip config files unless explicitly included
                if not self.include_config_files and self._is_config_file(item):
                    result.ignored_paths.add(f"{item.relative_to(root_path)} (config)")
                    continue
                
                # Check if file type is supported
                file_type = self._get_file_type(item)
                if file_type == FileType.UNKNOWN:
                    # Skip unsupported file types unless extension is in supported list
                    if item.suffix not in self.supported_extensions:
                        continue
                
                try:
                    # Read file content
                    content = item.read_text(encoding='utf-8', errors='ignore')
                    line_count = len(content.splitlines())
                    
                    # Create file metadata
                    code_file = CodeFile(
                        path=item,
                        relative_path=item.relative_to(root_path),
                        file_type=file_type,
                        size_bytes=item.stat().st_size,
                        line_count=line_count
                    )
                    
                    # Extract code information based on file type
                    if file_type == FileType.PYTHON:
                        functions, classes, imports = self._extract_python_info(content)
                        code_file.functions = functions
                        code_file.classes = classes
                        code_file.imports = imports
                        
                    elif file_type in (FileType.JAVASCRIPT, FileType.TYPESCRIPT, FileType.JSX, FileType.TSX):
                        functions, classes, imports = self._extract_javascript_info(content)
                        code_file.functions = functions
                        code_file.classes = classes
                        code_file.imports = imports
                        
                    elif file_type == FileType.JAVA:
                        functions, classes, imports = self._extract_java_info(content)
                        code_file.functions = functions
                        code_file.classes = classes
                        code_file.imports = imports
                        
                    elif file_type in (FileType.C, FileType.CPP, FileType.HEADER, FileType.HPP):
                        functions, classes, imports = self._extract_cpp_info(content)
                        code_file.functions = functions
                        code_file.classes = classes
                        code_file.imports = imports
                    
                    elif file_type in (FileType.HTML, FileType.HTM):
                        ids, classes, scripts = self._extract_html_info(content)
                        code_file.functions = ids  # Store IDs as "functions"
                        code_file.classes = classes
                        code_file.imports = scripts  # Store scripts/links as "imports"
                    
                    elif file_type in (FileType.CSS, FileType.SCSS, FileType.SASS, FileType.LESS):
                        selectors, classes, ids = self._extract_css_info(content)
                        code_file.functions = selectors  # Store selectors as "functions"
                        code_file.classes = classes
                        code_file.imports = ids  # Store IDs as "imports"
                    
                    elif file_type == FileType.SQL:
                        tables, functions, procedures = self._extract_sql_info(content)
                        code_file.functions = functions + procedures  # Combine functions and procedures
                        code_file.classes = tables  # Store tables as "classes"
                        code_file.imports = []
                    
                    # Store content if file is small enough
                    if line_count <= self.max_file_size_lines:
                        code_file.content = content
                    
                    # Add to results
                    result.files.append(code_file)
                    result.total_lines += line_count
                    
                except Exception as e:
                    # Log error but continue scanning
                    error_msg = f"Error scanning {item}: {str(e)}"
                    result.errors.append(error_msg)
                    continue
            
            # Update totals
            result.total_files = len(result.files)
        
        finally:
            # Restore original patterns
            self.ignore_patterns = original_patterns
        
        return result
    
    def _should_ignore(self, path: Path, root: Path) -> bool:
        """
        Check if a path should be ignored based on patterns.
        
        Args:
            path: Path to check
            root: Root directory being scanned
            
        Returns:
            True if path should be ignored, False otherwise
        """
        # Get relative path for pattern matching
        try:
            rel_path = path.relative_to(root)
        except ValueError:
            return False
        
        path_str = str(rel_path).replace("\\", "/")
        
        # Check against ignore patterns
        for pattern in self.ignore_patterns:
            # Directory pattern
            if pattern.endswith("/"):
                if path_str.startswith(pattern.rstrip("/")):
                    return True
                # Also match if any parent directory matches
                if any(part == pattern.rstrip("/") for part in rel_path.parts):
                    return True
            # Wildcard pattern
            elif "*" in pattern:
                import re
                regex_pattern = pattern.replace("*", ".*").replace("?", ".")
                if re.match(regex_pattern, path_str):
                    return True
            # Exact match
            else:
                if pattern in path_str or rel_path.name == pattern:
                    return True
        
        return False
    
    def _is_binary_file(self, path: Path) -> bool:
        """
        Check if a file is binary by reading the first chunk.
        
        Args:
            path: Path to the file
            
        Returns:
            True if file appears to be binary
        """
        try:
            # Read first 8KB to check for binary content
            with open(path, 'rb') as f:
                chunk = f.read(8192)
                # Check for null bytes (common in binary files)
                if b'\x00' in chunk:
                    return True
                # Check for high ratio of non-text bytes
                text_chars = bytearray({7,8,9,10,12,13,27} | set(range(0x20, 0x100)) - {0x7f})
                non_text = sum(1 for byte in chunk if byte not in text_chars)
                return non_text / len(chunk) > 0.3 if chunk else False
        except Exception:
            # If we can't read, assume it's binary or inaccessible
            return True
    
    def _is_config_file(self, path: Path) -> bool:
        """
        Check if a file is a configuration file.
        
        Args:
            path: Path to the file
            
        Returns:
            True if file is a configuration file
        """
        # Common config file patterns
        config_names = {
            '.gitignore', '.dockerignore', '.npmignore',
            'package.json', 'package-lock.json', 'yarn.lock',
            'Pipfile', 'Pipfile.lock', 'requirements.txt',
            'setup.py', 'setup.cfg', 'pyproject.toml',
            'tsconfig.json', 'jsconfig.json',
            '.eslintrc', '.prettierrc', '.editorconfig',
            'Dockerfile', 'docker-compose.yml',
            'Makefile', 'CMakeLists.txt',
            '.env', '.env.example', '.env.local',
            'webpack.config.js', 'vite.config.js',
            '.gitlab-ci.yml', '.travis.yml', 'azure-pipelines.yml'
        }
        
        config_extensions = {
            '.lock', '.toml', '.ini', '.cfg', '.conf',
            '.config', '.yaml', '.yml'
        }
        
        # Check exact filename matches
        if path.name in config_names:
            return True
        
        # Check if filename starts with a dot (hidden config files)
        if path.name.startswith('.') and path.suffix not in {'.py', '.js', '.ts', '.java', '.c', '.cpp', '.h'}:
            return True
        
        # Check extension-based config files
        if path.suffix.lower() in config_extensions:
            return True
        
        return False
    
    def _read_gitignore(self, root: Path) -> List[str]:
        """
        Read and parse .gitignore file if it exists.
        
        Args:
            root: Root directory to check for .gitignore
            
        Returns:
            List of ignore patterns from .gitignore
        """
        gitignore_path = root / ".gitignore"
        patterns = []
        
        if not gitignore_path.exists():
            return patterns
        
        try:
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                for line in f:
                    # Remove comments and whitespace
                    line = line.strip()
                    
                    # Skip empty lines and comments
                    if not line or line.startswith('#'):
                        continue
                    
                    # Remove trailing spaces
                    line = line.rstrip()
                    
                    # Handle negation patterns (not implemented yet, just skip)
                    if line.startswith('!'):
                        continue
                    
                    patterns.append(line)
        
        except Exception:
            # If we can't read gitignore, just continue
            pass
        
        return patterns
    
    def _get_file_type(self, path: Path) -> FileType:
        """Determine file type from extension."""
        ext = path.suffix.lower()
        
        # Programming Languages
        if ext == ".py":
            return FileType.PYTHON
        elif ext == ".js":
            return FileType.JAVASCRIPT
        elif ext == ".ts":
            return FileType.TYPESCRIPT
        elif ext == ".jsx":
            return FileType.JSX
        elif ext == ".tsx":
            return FileType.TSX
        elif ext == ".java":
            return FileType.JAVA
        elif ext == ".c":
            return FileType.C
        elif ext in (".cpp", ".cc", ".cxx"):
            return FileType.CPP
        elif ext == ".h":
            return FileType.HEADER
        elif ext in (".hpp", ".hh", ".hxx"):
            return FileType.HPP
        elif ext == ".cs":
            return FileType.CSHARP
        elif ext == ".go":
            return FileType.GO
        elif ext == ".rs":
            return FileType.RUST
        elif ext == ".php":
            return FileType.PHP
        
        # Web Languages
        elif ext == ".html":
            return FileType.HTML
        elif ext == ".htm":
            return FileType.HTM
        elif ext == ".css":
            return FileType.CSS
        elif ext == ".scss":
            return FileType.SCSS
        elif ext == ".sass":
            return FileType.SASS
        elif ext == ".less":
            return FileType.LESS
        
        # Markup & Data
        elif ext == ".xml":
            return FileType.XML
        elif ext == ".json":
            return FileType.JSON
        elif ext in (".yaml", ".yml"):
            return FileType.YAML if ext == ".yaml" else FileType.YML
        elif ext == ".md":
            return FileType.MARKDOWN
        
        # Database
        elif ext == ".sql":
            return FileType.SQL
        
        else:
            return FileType.UNKNOWN
    
    def _extract_python_info(self, content: str) -> tuple[List[str], List[str], List[str]]:
        """
        Extract functions, classes, and imports from Python code.
        
        Returns:
            Tuple of (functions, classes, imports)
        """
        functions = []
        classes = []
        imports = []
        
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append(node.name)
                elif isinstance(node, ast.ClassDef):
                    classes.append(node.name)
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.append(alias.name)
                    else:
                        if node.module:
                            imports.append(node.module)
        
        except SyntaxError:
            # Handle syntax errors gracefully
            pass
        
        return functions, classes, imports
    
    def _extract_javascript_info(self, content: str) -> tuple[List[str], List[str], List[str]]:
        """
        Extract functions, classes, and imports from JavaScript/TypeScript code.
        Uses regex-based extraction (basic but functional).
        
        Returns:
            Tuple of (functions, classes, imports)
        """
        import re
        
        functions = []
        classes = []
        imports = []
        
        # Extract function declarations
        # Matches: function name(...), const name = (...) =>, async function name
        func_patterns = [
            r'function\s+(\w+)\s*\(',
            r'const\s+(\w+)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>',
            r'(\w+)\s*:\s*(?:async\s*)?\([^)]*\)\s*=>',  # Object method
            r'async\s+function\s+(\w+)\s*\(',
        ]
        
        for pattern in func_patterns:
            matches = re.findall(pattern, content)
            functions.extend(matches)
        
        # Extract class declarations
        class_matches = re.findall(r'class\s+(\w+)', content)
        classes.extend(class_matches)
        
        # Extract React components (function components)
        component_matches = re.findall(r'(?:export\s+)?(?:default\s+)?function\s+([A-Z]\w+)\s*\(', content)
        classes.extend(component_matches)
        
        # Extract imports
        # Matches: import ... from '...', require('...')
        import_patterns = [
            r'import\s+.*?from\s+[\'"]([^\'"]+)[\'"]',
            r'require\([\'"]([^\'"]+)[\'"]\)',
        ]
        
        for pattern in import_patterns:
            matches = re.findall(pattern, content)
            imports.extend(matches)
        
        return list(set(functions)), list(set(classes)), list(set(imports))
    
    def _extract_java_info(self, content: str) -> tuple[List[str], List[str], List[str]]:
        """
        Extract functions, classes, and imports from Java code.
        
        Returns:
            Tuple of (functions/methods, classes, imports)
        """
        import re
        
        functions = []
        classes = []
        imports = []
        
        # Extract class declarations
        class_matches = re.findall(r'(?:public|private|protected)?\s*class\s+(\w+)', content)
        classes.extend(class_matches)
        
        # Extract interface declarations
        interface_matches = re.findall(r'(?:public|private)?\s*interface\s+(\w+)', content)
        classes.extend(interface_matches)
        
        # Extract method declarations
        method_pattern = r'(?:public|private|protected|static|\s)+\w+\s+(\w+)\s*\([^)]*\)\s*(?:throws\s+\w+\s*)?{'
        method_matches = re.findall(method_pattern, content)
        functions.extend(method_matches)
        
        # Extract imports
        import_matches = re.findall(r'import\s+([\w.]+);', content)
        imports.extend(import_matches)
        
        return list(set(functions)), list(set(classes)), list(set(imports))
    
    def _extract_cpp_info(self, content: str) -> tuple[List[str], List[str], List[str]]:
        """
        Extract functions, classes, and includes from C/C++ code.
        
        Returns:
            Tuple of (functions, classes, includes)
        """
        import re
        
        functions = []
        classes = []
        imports = []
        
        # Extract class declarations
        class_matches = re.findall(r'class\s+(\w+)', content)
        classes.extend(class_matches)
        
        # Extract struct declarations
        struct_matches = re.findall(r'struct\s+(\w+)', content)
        classes.extend(struct_matches)
        
        # Extract function declarations (basic)
        # Matches: return_type function_name(...)
        func_pattern = r'^\s*(?:[\w:]+\s+)*(\w+)\s*\([^)]*\)\s*(?:const)?\s*[{;]'
        func_matches = re.findall(func_pattern, content, re.MULTILINE)
        functions.extend([f for f in func_matches if f not in ['if', 'while', 'for', 'switch']])
        
        # Extract includes
        include_matches = re.findall(r'#include\s+[<"]([^>"]+)[>"]', content)
        imports.extend(include_matches)
        
        return list(set(functions)), list(set(classes)), list(set(imports))
    
    def _extract_html_info(self, content: str) -> tuple[List[str], List[str], List[str]]:
        """
        Extract IDs, classes, and script sources from HTML.
        
        Returns:
            Tuple of (ids, classes, scripts/links)
        """
        import re
        
        ids = []
        classes = []
        scripts = []
        
        # Extract IDs
        id_matches = re.findall(r'id=["\']([^"\']+)["\']', content)
        ids.extend(id_matches)
        
        # Extract classes
        class_matches = re.findall(r'class=["\']([^"\']+)["\']', content)
        for class_str in class_matches:
            # Split multiple classes
            classes.extend(class_str.split())
        
        # Extract script src and link href
        script_matches = re.findall(r'<script[^>]+src=["\']([^"\']+)["\']', content)
        scripts.extend(script_matches)
        
        link_matches = re.findall(r'<link[^>]+href=["\']([^"\']+)["\']', content)
        scripts.extend(link_matches)
        
        return list(set(ids)), list(set(classes)), list(set(scripts))
    
    def _extract_css_info(self, content: str) -> tuple[List[str], List[str], List[str]]:
        """
        Extract selectors, classes, and IDs from CSS.
        
        Returns:
            Tuple of (selectors, classes, ids)
        """
        import re
        
        selectors = []
        classes = []
        ids = []
        
        # Extract class selectors
        class_matches = re.findall(r'\.([a-zA-Z_][\w-]*)\s*{', content)
        classes.extend(class_matches)
        
        # Extract ID selectors
        id_matches = re.findall(r'#([a-zA-Z_][\w-]*)\s*{', content)
        ids.extend(id_matches)
        
        # Extract general selectors (elements, pseudo-classes)
        selector_matches = re.findall(r'([a-zA-Z][\w-]*(?::[\w-]+)?)\s*{', content)
        selectors.extend(selector_matches)
        
        return list(set(selectors)), list(set(classes)), list(set(ids))
    
    def _extract_sql_info(self, content: str) -> tuple[List[str], List[str], List[str]]:
        """
        Extract tables, functions, and procedures from SQL.
        
        Returns:
            Tuple of (tables, functions, procedures)
        """
        import re
        
        tables = []
        functions = []
        procedures = []
        
        # Extract CREATE TABLE statements
        table_matches = re.findall(r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?[`"]?(\w+)[`"]?', content, re.IGNORECASE)
        tables.extend(table_matches)
        
        # Extract CREATE FUNCTION statements
        func_matches = re.findall(r'CREATE\s+(?:OR\s+REPLACE\s+)?FUNCTION\s+[`"]?(\w+)[`"]?', content, re.IGNORECASE)
        functions.extend(func_matches)
        
        # Extract CREATE PROCEDURE statements
        proc_matches = re.findall(r'CREATE\s+(?:OR\s+REPLACE\s+)?PROCEDURE\s+[`"]?(\w+)[`"]?', content, re.IGNORECASE)
        procedures.extend(proc_matches)
        
        return list(set(tables)), list(set(functions)), list(set(procedures))


# Convenience instance
scanner = CodeScanner()
