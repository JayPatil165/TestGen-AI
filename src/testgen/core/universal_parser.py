"""
Universal Code Parser using Tree-sitter.

Parses code in ANY supported language using Tree-sitter.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

try:
    from tree_sitter import Language, Parser
    TREE_SITTER_AVAILABLE = True
except ImportError:
    TREE_SITTER_AVAILABLE = False
    print("Warning: tree-sitter not installed. Install with: pip install tree-sitter")

from .language_config import Language as LangEnum, get_language_config, get_language_by_extension


@dataclass
class Function:
    """Represents a function/method."""
    name: str
    parameters: List[str]
    return_type: Optional[str]
    docstring: Optional[str]
    body: str
    line_start: int
    line_end: int
    is_test: bool = False
    is_async: bool = False


@dataclass
class Class:
    """Represents a class."""
    name: str
    methods: List[Function]
    attributes: List[str]
    docstring: Optional[str]
    line_start: int
    line_end: int
    is_test_class: bool = False


class UniversalCodeParser:
    """
    Universal code parser using Tree-sitter.
    
    Parses code in ANY supported language with a consistent API.
    
    Example:
        >>> parser = UniversalCodeParser(language="python")
        >>> functions = parser.extract_functions("my_code.py")
        >>> 
        >>> parser = UniversalCodeParser(language="javascript")
        >>> functions = parser.extract_functions("my_code.js")
    """
    
    def __init__(self, language: str = "python"):
        """
        Initialize parser for a specific language.
        
        Args:
            language: Language name (python, javascript, java, etc.)
        """
        self.language_name = language
        
        # Get language config
        lang_enum = LangEnum(language) if language in [l.value for l in LangEnum] else LangEnum.PYTHON
        self.config = get_language_config(lang_enum)
        
        # Try to initialize tree-sitter
        self.parser = None
        self.tree_sitter_available = TREE_SITTER_AVAILABLE
        
        if TREE_SITTER_AVAILABLE:
            try:
                # Note: Tree-sitter languages need to be built separately
                # For now, we'll use fallback parsing
                self.parser = Parser()
                # self.parser.set_language(Language('build/my-languages.so', self.config.tree_sitter_language))
            except Exception as e:
                self.tree_sitter_available = False
                if self.config.language != LangEnum.PYTHON:
                    print(f"Tree-sitter not fully configured for {language}. Using fallback parser.")
    
    def extract_functions(
        self,
        code_or_file: str,
        is_file: bool = True
    ) -> List[Function]:
        """
        Extract all functions from code.
        
        Args:
            code_or_file: File path or code string
            is_file: If True, treat as file path
            
        Returns:
            List of Function objects
        """
        if is_file:
            with open(code_or_file, 'r', encoding='utf-8') as f:
                code = f.read()
        else:
            code = code_or_file
        
        # Use tree-sitter if available
        if self.tree_sitter_available and self.parser:
            return self._extract_functions_tree_sitter(code)
        else:
            # Fallback to language-specific parsing
            return self._extract_functions_fallback(code)
    
    def extract_classes(
        self,
        code_or_file: str,
        is_file: bool = True
    ) -> List[Class]:
        """
        Extract all classes from code.
        
        Args:
            code_or_file: File path or code string
            is_file: If True, treat as file path
            
        Returns:
            List of Class objects
        """
        if is_file:
            with open(code_or_file, 'r', encoding='utf-8') as f:
                code = f.read()
        else:
            code = code_or_file
        
        if self.tree_sitter_available and self.parser:
            return self._extract_classes_tree_sitter(code)
        else:
            return self._extract_classes_fallback(code)
    
    def _extract_functions_tree_sitter(self, code: str) -> List[Function]:
        """Extract functions using tree-sitter (when available)."""
        # TODO: Implement tree-sitter parsing
        # For now, fall back
        return self._extract_functions_fallback(code)
    
    def _extract_classes_tree_sitter(self, code: str) -> List[Class]:
        """Extract classes using tree-sitter (when available)."""
        # TODO: Implement tree-sitter parsing
        return self._extract_classes_fallback(code)
    
    def _extract_functions_fallback(self, code: str) -> List[Function]:
        """
        Fallback function extraction (language-specific).
        
        Uses simple regex/AST parsing for each language.
        """
        if self.config.language == LangEnum.PYTHON:
            return self._extract_functions_python(code)
        elif self.config.language in [LangEnum.JAVASCRIPT, LangEnum.TYPESCRIPT]:
            return self._extract_functions_javascript(code)
        elif self.config.language == LangEnum.JAVA:
            return self._simple_function_extract(code, r'(public|private|protected).*?\s+\w+\s+(\w+)\s*\(')
        elif self.config.language == LangEnum.GO:
            return self._simple_function_extract(code, r'func\s+(\w+)\s*\(')
        else:
            # Generic extraction
            return self._simple_function_extract(code, self.config.function_pattern + r'\s+(\w+)\s*\(')
    
    def _extract_classes_fallback(self, code: str) -> List[Class]:
        """Fallback class extraction."""
        if self.config.language == LangEnum.PYTHON:
            return self._extract_classes_python(code)
        else:
            return []
    
    def _extract_functions_python(self, code: str) -> List[Function]:
        """Extract Python functions using AST."""
        import ast
        
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return []
        
        functions = []
        lines = code.split('\n')
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Get docstring
                docstring = ast.get_docstring(node)
                
                # Get parameters
                params = [arg.arg for arg in node.args.args]
                
                # Get return type
                return_type = ast.unparse(node.returns) if node.returns else None
                
                # Get body
                start_line = node.lineno - 1
                end_line = node.end_lineno if node.end_lineno else start_line + 1
                body = '\n'.join(lines[start_line:end_line])
                
                # Check if test
                is_test = node.name.startswith('test_')

                
                functions.append(Function(
                    name=node.name,
                    parameters=params,
                    return_type=return_type,
                    docstring=docstring,
                    body=body,
                    line_start=start_line + 1,
                    line_end=end_line,
                    is_test=is_test,
                    is_async=isinstance(node, ast.AsyncFunctionDef)
                ))
        
        return functions
    
    def _extract_classes_python(self, code: str) -> List[Class]:
        """Extract Python classes using AST."""
        import ast
        
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return []
        
        classes = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Get methods
                methods = []
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        methods.append(Function(
                            name=item.name,
                            parameters=[arg.arg for arg in item.args.args],
                            return_type=None,
                            docstring=ast.get_docstring(item),
                            body="",
                            line_start=item.lineno,
                            line_end=item.end_lineno or item.lineno,
                            is_test=item.name.startswith('test_')
                        ))
                
                classes.append(Class(
                    name=node.name,
                    methods=methods,
                    attributes=[],
                    docstring=ast.get_docstring(node),
                    line_start=node.lineno,
                    line_end=node.end_lineno or node.lineno,
                    is_test_class=node.name.startswith('Test')
                ))
        
        return classes
    
    def _extract_functions_javascript(self, code: str) -> List[Function]:
        """Extract JavaScript functions using regex (simple fallback)."""
        import re
        
        functions = []
        lines = code.split('\n')
        
        # Match: function name(...) or const name = (...) => or async function
        patterns = [
            r'^\s*(async\s+)?function\s+(\w+)\s*\(',
            r'^\s*const\s+(\w+)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>',
            r'^\s*(\w+)\s*:\s*(?:async\s*)?function\s*\(',
        ]
        
        for i, line in enumerate(lines):
            for pattern in patterns:
                match = re.search(pattern, line)
                if match:
                    name = match.group(2) if match.lastindex >= 2 else match.group(1)
                    is_async = 'async' in line
                    is_test = 'test' in name.lower() or 'it(' in line or 'describe(' in line
                    
                    functions.append(Function(
                        name=name,
                        parameters=[],
                        return_type=None,
                        docstring=None,
                        body=line,
                        line_start=i + 1,
                        line_end=i + 1,
                        is_test=is_test,
                        is_async=is_async
                    ))
        
        return functions
    
    def _simple_function_extract(self, code: str, pattern: str) -> List[Function]:
        """Simple regex-based function extraction."""
        import re
        
        functions = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines):
            match = re.search(pattern, line)
            if match:
                name = match.group(match.lastindex) if match.lastindex else "unknown"
                
                functions.append(Function(
                    name=name,
                    parameters=[],
                    return_type=None,
                    docstring=None,
                    body=line,
                    line_start=i + 1,
                    line_end=i + 1,
                    is_test=self.config.test_function_prefix.lower() in name.lower()
                ))
        
        return functions
    
    def get_imports(self, code: str) -> List[str]:
        """
        Extract import statements from code.
        
        Args:
            code: Source code
            
        Returns:
            List of import statements
        """
        import re
        
        imports = []
        keyword = self.config.import_keyword
        
        pattern = rf'^\s*{keyword}\s+.+'
        
        for line in code.split('\n'):
            if re.match(pattern, line):
                imports.append(line.strip())
        
        return imports
    
    def count_lines_of_code(self, code: str) -> Dict[str, int]:
        """
        Count lines of code (total, code, comments, blank).
        
        Args:
            code: Source code
            
        Returns:
            Dictionary with line counts
        """
        lines = code.split('\n')
        total = len(lines)
        blank = sum(1 for line in lines if not line.strip())
        
        comment_style = self.config.comment_style
        comments = sum(1 for line in lines if line.strip().startswith(comment_style))
        
        code_lines = total - blank - comments
        
        return {
            'total': total,
            'code': code_lines,
            'comments': comments,
            'blank': blank
        }
