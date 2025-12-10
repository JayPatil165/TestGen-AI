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
        Enhanced to extract full signatures, parameters, return types, docstrings, and decorators.
        
        Returns:
            Tuple of (function_signatures, class_info_with_methods, imports)
        """
        functions = []
        classes = []
        imports = []
        
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Build function signature
                    params = []
                    for arg in node.args.args:
                        param_str = arg.arg
                        # Add type annotation if present
                        if arg.annotation:
                            param_str += f": {ast.unparse(arg.annotation)}"
                        params.append(param_str)
                    
                    # Build signature string
                    sig = f"{node.name}({', '.join(params)})"
                    
                    # Add return type if present
                    if node.returns:
                        sig += f" -> {ast.unparse(node.returns)}"
                    
                    # Add decorators if present
                    if node.decorator_list:
                        decorators = [f"@{ast.unparse(d)}" for d in node.decorator_list]
                        sig = f"{' '.join(decorators)} {sig}"
                    
                    # Add docstring if present
                    docstring = ast.get_docstring(node)
                    if docstring:
                        # Just first line of docstring
                        first_line = docstring.split('\n')[0].strip()
                        sig += f' """  {first_line}'
                    
                    functions.append(sig)
                    
                elif isinstance(node, ast.ClassDef):
                    # Build class info with bases
                    class_info = node.name
                    if node.bases:
                        bases = [ast.unparse(base) for base in node.bases]
                        class_info += f"({', '.join(bases)})"
                    
                    # Add class decorators
                    if node.decorator_list:
                        decorators = [f"@{ast.unparse(d)}" for d in node.decorator_list]
                        class_info = f"{' '.join(decorators)} {class_info}"
                    
                    # Add docstring
                    docstring = ast.get_docstring(node)
                    if docstring:
                        first_line = docstring.split('\n')[0].strip()
                        class_info += f' """ {first_line}'
                    
                    # Extract class methods
                    methods = []
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            method_info = item.name
                            # Add method decorators
                            if item.decorator_list:
                                method_decorators = [ast.unparse(d) for d in item.decorator_list]
                                if any(d in method_decorators for d in ['property', 'classmethod', 'staticmethod']):
                                    method_info = f"@{method_decorators[0]} {method_info}"
                            methods.append(method_info)
                    
                    # Add methods to class info
                    if methods:
                        class_info += f" [methods: {', '.join(methods[:5])}]"  # Limit to first 5
                    
                    classes.append(class_info)
                    
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
        Enhanced to capture parameters, type annotations, JSDoc, class methods, and decorators.
        
        Returns:
            Tuple of (function_signatures, classes_with_methods, imports)
        """
        import re
        
        functions = []
        classes = []
        imports = []
        
        # Extract function declarations with parameters
        func_patterns = [
            r'function\s+(\w+)\s*\(([^)]*)\)(?:\s*:\s*(\w+))?',
            r'const\s+(\w+)\s*=\s*(?:async\s*)?\(([^)]*)\)(?:\s*:\s*(\w+))?\s*=>',
            r'(\w+)\s*:\s*(?:async\s*)?\(([^)]*)\)(?:\s*:\s*(\w+))?\s*=>',
            r'async\s+function\s+(\w+)\s*\(([^)]*)\)(?:\s*:\s*(\w+))?',
        ]
        
        for pattern in func_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if len(match) >= 2:
                    name, params = match[0], match[1]
                    sig = f"{name}({params})"
                    if len(match) > 2 and match[2]:
                        sig += f" : {match[2]}"
                    functions.append(sig)
        
        # Extract class declarations with methods
        class_pattern = r'class\s+(\w+)(?:\s+extends\s+(\w+))?\s*{([^}]+)}'
        class_matches = re.findall(class_pattern, content, re.DOTALL)
        for match in class_matches:
            class_name = match[0]
            extends = match[1]
            class_body = match[2]
            
            class_info = class_name
            if extends:
                class_info += f" extends {extends}"
            
            # Extract decorators (TypeScript)
            decorator_pattern = rf'@(\w+)\s+class\s+{class_name}'
            decorator_match = re.search(decorator_pattern, content)
            if decorator_match:
                class_info = f"@{decorator_match.group(1)} {class_info}"
            
            # Extract class methods
            method_pattern = r'(?:async\s+)?(\w+)\s*\([^)]*\)'
            methods = re.findall(method_pattern, class_body)
            # Filter out keywords
            methods = [m for m in methods if m not in ['if', 'while', 'for', 'switch', 'return']]
            
            if methods:
                class_info += f" [methods: {', '.join(methods[:5])}]"
            
            classes.append(class_info)
        
        # Extract React components with props
        component_pattern = r'(?:export\s+)?(?:default\s+)?function\s+([A-Z]\w+)\s*\(([^)]*)\)'
        component_matches = re.findall(component_pattern, content)
        for name, props in component_matches:
            sig = f"{name}({props})" if props else name
            
            # Check for React hooks in component body
            component_body_pattern = rf'function\s+{name}[^{{]*{{([^}}]+)}}'
            body_match = re.search(component_body_pattern, content, re.DOTALL)
            if body_match:
                hooks = re.findall(r'use(\w+)', body_match.group(1))
                if hooks:
                    sig += f" [hooks: {', '.join(set(hooks[:3]))}]"
            
            classes.append(f"Component: {sig}")
        
        # Extract imports
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
        Enhanced to capture method signatures, access modifiers, Javadoc, annotations, and class methods.
        
        Returns:
            Tuple of (method_signatures, classes_with_methods, imports)
        """
        import re
        
        functions = []
        classes = []
        imports = []
        
        # Extract class declarations with extends/implements and methods
        class_pattern = r'(?:public|private|protected)?\s*class\s+(\w+)(?:\s+extends\s+(\w+))?(?:\s+implements\s+([\w,\s]+))?\s*{([^}]*)'
        class_matches = re.findall(class_pattern, content, re.DOTALL)
        for match in class_matches:
            class_name = match[0]
            extends = match[1]
            implements = match[2]
            class_body = match[3][:500]  # Limit body size
            
            class_info = class_name
            if extends:
                class_info += f" extends {extends}"
            if implements:
                class_info += f" implements {implements}"
            
            # Check for class annotations
            annotation_pattern = rf'@(\w+)\s+(?:public|private|protected)?\s*class\s+{class_name}'
            annotation_match = re.search(annotation_pattern, content)
            if annotation_match:
                class_info = f"@{annotation_match.group(1)} {class_info}"
            
            # Extract methods from class body
            method_pattern = r'(?:public|private|protected)\s+(?:\w+\s+)?(\w+)\s*\('
            methods = re.findall(method_pattern, class_body)
            methods = [m for m in methods if m not in class_name]  # Remove constructor
            
            if methods:
                class_info += f" [methods: {', '.join(set(methods[:5]))}]"
            
            classes.append(class_info)
        
        # Extract interface declarations
        interface_pattern = r'(?:public|private)?\s*interface\s+(\w+)(?:\s+extends\s+([\w,\s]+))?\s*{([^}]*)'
        interface_matches = re.findall(interface_pattern, content, re.DOTALL)
        for match in interface_matches:
            interface_name = match[0]
            extends = match[1]
            interface_body = match[2][:300]
            
            interface_info = f"interface {interface_name}"
            if extends:
                interface_info += f" extends {extends}"
            
            # Extract interface methods
            method_pattern = r'(\w+)\s*\([^)]*\)\s*;'
            methods = re.findall(method_pattern, interface_body)
            if methods:
                interface_info += f" [methods: {', '.join(methods[:5])}]"
            
            classes.append(interface_info)
        
        # Extract method declarations with full signatures
        method_pattern = r'((?:public|private|protected|static|final)\s+)+(\w+(?:<[\w,\s<>]+>)?)\s+(\w+)\s*\(([^)]*)\)'
        method_matches = re.findall(method_pattern, content)
        for match in method_matches:
            modifiers = match[0].strip()
            return_type = match[1]
            method_name = match[2]
            params = match[3].strip()
            
            sig = f"{method_name}({params}) : {return_type}"
            if 'public' in modifiers:
                sig = "public " + sig
            elif 'private' in modifiers:
                sig = "private " + sig
            
            # Check for annotations
            annotation_pattern = rf'@(\w+)\s+{re.escape(match[0])}{re.escape(match[1])}\s+{re.escape(method_name)}'
            annotation_match = re.search(annotation_pattern, content)
            if annotation_match:
                sig = f"@{annotation_match.group(1)} {sig}"
            
            functions.append(sig)
        
        # Extract imports
        import_matches = re.findall(r'import\s+([\w.]+);', content)
        imports.extend(import_matches)
        
        return list(set(functions)), list(set(classes)), list(set(imports))
    
    def _extract_cpp_info(self, content: str) -> tuple[List[str], List[str], List[str]]:
        """
        Extract functions, classes, and includes from C/C++ code.
        Enhanced to capture function signatures, class methods, virtual functions, and namespaces.
        
        Returns:
            Tuple of (function_signatures, classes_with_methods, includes)
        """
        import re
        
        functions = []
        classes = []
        imports = []
        
        # Extract class declarations with inheritance and methods
        class_pattern = r'class\s+(\w+)(?:\s*:\s*(?:public|private|protected)\s+(\w+))?\s*{([^}]*)'
        class_matches = re.findall(class_pattern, content, re.DOTALL)
        for match in class_matches:
            class_name = match[0]
            base_class = match[1]
            class_body = match[2][:600]  # Limit body size
            
            class_info = class_name
            if base_class:
                class_info += f" : {base_class}"
            
            # Extract methods from class body (public, private, protected)
            method_pattern = r'(?:virtual\s+)?(?:static\s+)?(?:\w+\s+)?(\w+)\s*\([^)]*\)(?:\s*const)?'
            methods = re.findall(method_pattern, class_body)
            # Filter out keywords and the class name (constructor)
            methods = [m for m in methods if m not in ['if', 'while', 'for', 'switch', 'return', class_name]]
            
            # Check for virtual functions
            if 'virtual' in class_body:
                class_info += ' [has virtual]'
            
            if methods:
                class_info += f" [methods: {', '.join(set(methods[:5]))}]"
            
            classes.append(class_info)
        
        # Extract struct declarations with members
        struct_pattern = r'struct\s+(\w+)\s*{([^}]*)'
        struct_matches = re.findall(struct_pattern, content, re.DOTALL)
        for match in struct_matches:
            struct_name = match[0]
            struct_body = match[1][:300]
            
            struct_info = f"struct {struct_name}"
            
            # Extract member variables
            member_pattern = r'([a-zA-Z_]\w+)\s+(\w+)\s*;'
            members = re.findall(member_pattern, struct_body)
            if members:
                member_names = [m[1] for m in members[:3]]
                struct_info += f" [members: {', '.join(member_names)}]"
            
            classes.append(struct_info)
        
        # Extract namespace information
        namespace_pattern = r'namespace\s+(\w+)'
        namespace_matches = re.findall(namespace_pattern, content)
        if namespace_matches:
            classes.append(f"namespace: {', '.join(set(namespace_matches[:3]))}")
        
        # Extract function declarations/definitions with signatures
        func_pattern = r'([\\w:]+(?:\\s+[\\w:]+)?)\s+(\w+)\s*\(([^)]*)\)\s*(?:const)?\s*[{;]'
        func_matches = re.findall(func_pattern, content, re.MULTILINE)
        for match in func_matches:
            return_type = match[0].strip()
            func_name = match[1]
            params = match[2].strip()
            
            # Filter out control structures
            if func_name in ['if', 'while', 'for', 'switch', 'catch']:
                continue
            
            sig = f"{func_name}({params}) : {return_type}"
            functions.append(sig)
        
        # Extract includes
        include_matches = re.findall(r'#include\s+[<"]([^>"]+)[>"]', content)
        imports.extend(include_matches)
        
        return list(set(functions)), list(set(classes)), list(set(imports))
    
    def _extract_html_info(self, content: str) -> tuple[List[str], List[str], List[str]]:
        """
        Extract IDs, classes, and script sources from HTML.
        Enhanced to capture data attributes and element structure.
        
        Returns:
            Tuple of (ids_with_elements, classes_with_context, scripts/links)
        """
        import re
        
        ids = []
        classes = []
        scripts = []
        
        # Extract IDs with element types
        id_pattern = r'<(\w+)[^>]*\s+id=["\']([^"\']+)["\']'
        id_matches = re.findall(id_pattern, content)
        for element, id_name in id_matches:
            ids.append(f"{element}#{id_name}")
        
        # Extract classes with element context
        class_pattern = r'<(\w+)[^>]*\s+class=["\']([^"\']+)["\']'
        class_matches = re.findall(class_pattern, content)
        for element, class_str in class_matches:
            for cls in class_str.split():
                classes.append(f"{element}.{cls}")
        
        # Extract data attributes
        data_pattern = r'data-(\w+)=["\']([^"\']+)["\']'
        data_matches = re.findall(data_pattern, content)
        for data_key, data_val in data_matches[:5]:  # Limit to first 5
            ids.append(f"data-{data_key}={data_val[:20]}")  # Truncate long values
        
        # Extract script src and link href
        script_matches = re.findall(r'<script[^>]+src=["\']([^"\']+)["\']', content)
        scripts.extend(script_matches)
        
        link_matches = re.findall(r'<link[^>]+href=["\']([^"\']+)["\']', content)
        scripts.extend(link_matches)
        
        # Extract inline event handlers
        event_pattern = r'on(\w+)=["\']([^"\']+)["\']'
        event_matches = re.findall(event_pattern, content)
        for event, handler in event_matches[:3]:  # Limit to first 3
            ids.append(f"on{event}: {handler[:30]}")
        
        return list(set(ids)), list(set(classes)), list(set(scripts))
    
    def _extract_css_info(self, content: str) -> tuple[List[str], List[str], List[str]]:
        """
        Extract selectors, classes, and IDs from CSS.
        Enhanced to capture media queries, keyframes, and pseudo-selectors.
        
        Returns:
            Tuple of (selectors_and_queries, classes, ids)
        """
        import re
        
        selectors = []
        classes = []
        ids = []
        
        # Extract class selectors
        class_matches = re.findall(r'\.([a-zA-Z_][\w-]*)\s*[{,]', content)
        classes.extend(class_matches)
        
        # Extract ID selectors
        id_matches = re.findall(r'#([a-zA-Z_][\w-]*)\s*[{,]', content)
        ids.extend(id_matches)
        
        # Extract general selectors with pseudo-classes
        selector_pattern = r'([a-zA-Z][\w-]*(?::[\w-]+(?:\([^)]*\))?)?)\s*[{,]'
        selector_matches = re.findall(selector_pattern, content)
        selectors.extend(selector_matches)
        
        # Extract media queries
        media_pattern = r'@media\s+([^{]+)'
        media_matches = re.findall(media_pattern, content)
        for media in media_matches[:5]:  # Limit to first 5
            selectors.append(f"@media {media.strip()[:50]}")
        
        # Extract keyframes
        keyframe_pattern = r'@keyframes\s+([\w-]+)'
        keyframe_matches = re.findall(keyframe_pattern, content)
        for keyframe in keyframe_matches:
            selectors.append(f"@keyframes {keyframe}")
        
        # Extract CSS variables
        var_pattern = r'--([a-zA-Z][\w-]*)\s*:'
        var_matches = re.findall(var_pattern, content)
        for var in var_matches[:10]:  # Limit to first 10
            ids.append(f"--{var}")
        
        return list(set(selectors)), list(set(classes)), list(set(ids))
    
    def _extract_sql_info(self, content: str) -> tuple[List[str], List[str], List[str]]:
        """
        Extract tables, functions, and procedures from SQL.
        Enhanced to capture views, triggers, indexes, and parameters.
        
        Returns:
            Tuple of (functions_and_procs_with_params, tables_and_views, constraints)
        """
        import re
        
        tables = []
        functions = []
        procedures = []
        
        # Extract CREATE TABLE statements with primary keys
        table_pattern = r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?[`"]?(\w+)[`"]?\s*\(([^;]*)'
        table_matches = re.findall(table_pattern, content, re.IGNORECASE | re.DOTALL)
        for table_name, definition in table_matches:
            # Check for primary key
            if 'PRIMARY KEY' in definition.upper():
                pk_match = re.search(r'PRIMARY\s+KEY\s*\(([^)]+)\)', definition, re.IGNORECASE)
                if pk_match:
                    tables.append(f"{table_name} (PK: {pk_match.group(1).strip()})")
                else:
                    tables.append(table_name)
            else:
                tables.append(table_name)
        
        # Extract CREATE VIEW statements
        view_pattern = r'CREATE\s+(?:OR\s+REPLACE\s+)?VIEW\s+[`"]?(\w+)[`"]?'
        view_matches = re.findall(view_pattern, content, re.IGNORECASE)
        for view_name in view_matches:
            tables.append(f"VIEW: {view_name}")
        
        # Extract CREATE INDEX statements
        index_pattern = r'CREATE\s+(?:UNIQUE\s+)?INDEX\s+[`"]?(\w+)[`"]?\s+ON\s+[`"]?(\w+)[`"]?'
        index_matches = re.findall(index_pattern, content, re.IGNORECASE)
        for index_name, table_name in index_matches[:5]:  # Limit to first 5
            procedures.append(f"INDEX: {index_name} ON {table_name}")
        
        # Extract CREATE FUNCTION statements with parameters
        func_pattern = r'CREATE\s+(?:OR\s+REPLACE\s+)?FUNCTION\s+[`"]?(\w+)[`"]?\s*\(([^)]*)\)'
        func_matches = re.findall(func_pattern, content, re.IGNORECASE)
        for func_name, params in func_matches:
            if params.strip():
                functions.append(f"{func_name}({params.strip()[:50]})")
            else:
                functions.append(f"{func_name}()")
        
        # Extract CREATE PROCEDURE statements with parameters
        proc_pattern = r'CREATE\s+(?:OR\s+REPLACE\s+)?PROCEDURE\s+[`"]?(\w+)[`"]?\s*\(([^)]*)\)'
        proc_matches = re.findall(proc_pattern, content, re.IGNORECASE)
        for proc_name, params in proc_matches:
            if params.strip():
                procedures.append(f"PROC: {proc_name}({params.strip()[:50]})")
            else:
                procedures.append(f"PROC: {proc_name}()")
        
        # Extract CREATE TRIGGER statements
        trigger_pattern = r'CREATE\s+TRIGGER\s+[`"]?(\w+)[`"]?\s+(?:BEFORE|AFTER)\s+(\w+)\s+ON\s+[`"]?(\w+)[`"]?'
        trigger_matches = re.findall(trigger_pattern, content, re.IGNORECASE)
        for trigger_name, action, table_name in trigger_matches[:3]:  # Limit to first 3
            procedures.append(f"TRIGGER: {trigger_name} ({action} on {table_name})")
        
        return list(set(functions)), list(set(procedures)), list(set(tables))


# Convenience instance
scanner = CodeScanner()
