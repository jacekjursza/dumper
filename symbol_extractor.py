import os
import ast
from datetime import datetime


class SymbolExtractor:
    def __init__(self, directory_path, exclude_patterns, db_manager, selected_files):
        self.directory_path = directory_path
        self.exclude_patterns = exclude_patterns
        self.db_manager = db_manager
        self.selected_files = selected_files  # List of selected files
        self.symbols = []

    def reindex(self):
        # Get list of files to process (selected files)
        files_to_process = self.get_files_to_process()
        for file_path in files_to_process:
            self.process_file(file_path)
        # Update symbols in the database
        self.db_manager.update_symbols(self.symbols)
        # Remove symbols from files that are no longer selected
        self.db_manager.remove_symbols_of_unselected_files(self.selected_files)
    
    def get_files_to_process(self):
        files_to_process = []
        for file_path in self.selected_files:
            last_modified_time = self.db_manager.get_last_modified_time(file_path)
            file_modified_time = datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
            if last_modified_time != file_modified_time:
                files_to_process.append(file_path)
        return files_to_process

    def process_file(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            file_content = f.read()
        try:
            tree = ast.parse(file_content, filename=file_path)
        except SyntaxError:
            return  # Skip files with syntax errors

        # Get the file's last modification time
        file_modified_time = datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()

        visitor = SymbolVisitor(file_path, self.db_manager, file_modified_time)
        visitor.visit(tree)
        self.symbols.extend(visitor.symbols)


class SymbolVisitor(ast.NodeVisitor):
    def __init__(self, file_path, db_manager, file_modified_time):
        self.file_path = os.path.normpath(file_path)
        self.db_manager = db_manager
        self.symbols = []
        self.parent_id_stack = []
        self.file_modified_time = file_modified_time


    def visit_Module(self, node):
        self.parent_id_stack.append(None)  # Root has no parent
        self.generic_visit(node)
        self.parent_id_stack.pop()

    def visit_ClassDef(self, node):
        # Insert class symbol
        class_symbol = {
            'symbol_name': node.name,
            'symbol_type': 'class',
            'location': self.file_path,
            'line_start': node.lineno,
            'line_end': getattr(node, 'end_lineno', node.lineno),
            'modified_at': self.file_modified_time,
            'parent_id': self.parent_id_stack[-1]
        }
        class_id = self.db_manager.insert_symbol(class_symbol)
        self.symbols.append(class_symbol)

        self.parent_id_stack.append(class_id)
        self.generic_visit(node)
        self.parent_id_stack.pop()

    def visit_FunctionDef(self, node):
        # Determine if the function is a method (inside a class)
        symbol_type = 'method' if isinstance(node.parent, ast.ClassDef) else 'function'
        function_symbol = {
            'symbol_name': node.name,
            'symbol_type': symbol_type,
            'location': self.file_path,
            'line_start': node.lineno,
            'line_end': getattr(node, 'end_lineno', node.lineno),
            'modified_at': self.file_modified_time,
            'parent_id': self.parent_id_stack[-1]
        }
        function_id = self.db_manager.insert_symbol(function_symbol)
        self.symbols.append(function_symbol)

        self.parent_id_stack.append(function_id)
        self.generic_visit(node)
        self.parent_id_stack.pop()

    def visit_AsyncFunctionDef(self, node):
        self.visit_FunctionDef(node)

    def visit_Assign(self, node):
        # Handle global variables or class attributes
        for target in node.targets:
            if isinstance(target, ast.Name):
                symbol = {
                    'symbol_name': target.id,
                    'symbol_type': 'global_var' if self.parent_id_stack[-1] is None else 'class_attr',
                    'location': self.file_path,
                    'line_start': node.lineno,
                    'line_end': getattr(node, 'end_lineno', node.lineno),
                    'modified_at': self.file_modified_time,
                    'parent_id': self.parent_id_stack[-1]
                }
                symbol_id = self.db_manager.insert_symbol(symbol)
                self.symbols.append(symbol)
        self.generic_visit(node)

    def generic_visit(self, node):
        # Keep track of parent nodes
        for child in ast.iter_child_nodes(node):
            child.parent = node
        super().generic_visit(node)
