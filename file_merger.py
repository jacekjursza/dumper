# file_merger.py

import ast
import logging
import os
from urllib.parse import urldefrag

import astor
import html2text
import requests
from PyQt5.QtCore import Qt
from bs4 import BeautifulSoup  # Dodane

# file_merger.py

# Konfiguracja logowania
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class FileMerger:

    def __init__(self, file_tree, directory_path, exclude_patterns, db_manager, convert_html_to_md, css_selectors, remove_imports):
        self.file_tree = file_tree
        self.directory_path = directory_path
        self.exclude_patterns = exclude_patterns
        self.db_manager = db_manager
        self.convert_html_to_md = convert_html_to_md
        self.css_selectors = [selector.strip() for selector in css_selectors.split(';') if selector.strip()] if css_selectors else []
        self.remove_imports = remove_imports

    def merge_files(self, output_file_path):
        with open(output_file_path, 'w', encoding='utf-8') as outfile:
            symbols_to_exclude = self.db_manager.get_symbols_to_exclude()
            for path, node in self.file_tree.items():
                if node.checkState(0) == Qt.Checked and os.path.isfile(path):
                    relative_path = os.path.relpath(path, self.directory_path)
                    if any(pattern in relative_path for pattern in self.exclude_patterns):
                        continue
                    self.process_file(path, outfile, symbols_to_exclude, relative_path)
            remote_pages = self.db_manager.get_all_remote_pages()
            unique_urls = set()
            for page in remote_pages:
                normalized_url = self.normalize_url(page['url'])
                if normalized_url in unique_urls:
                    continue  # Ignorowanie duplikatów
                unique_urls.add(normalized_url)
                if page['include_in_dump'] == 1:
                    try:
                        response = requests.get(normalized_url)
                        if response.status_code == 200:
                            content = response.text
                            if self.css_selectors:
                                soup = BeautifulSoup(content, 'html.parser')
                                filtered_content = ""
                                for selector in self.css_selectors:
                                    elements = soup.select(selector)
                                    for element in elements:
                                        filtered_content += str(element)
                                content = filtered_content
                            if self.convert_html_to_md:
                                content = html2text.html2text(content)
                            outfile.write(f"\n\n##---> {normalized_url}\n\n")
                            outfile.write(content)
                    except requests.RequestException as e:
                        logging.error(f"Error fetching {normalized_url}: {e}")

    def normalize_url(self, url):
        # Usunięcie fragmentu (#...) z URL
        url, _ = urldefrag(url)
        return url

    def process_file(self, file_path, outfile, symbols_to_exclude, relative_path):
        _, file_extension = os.path.splitext(file_path)
        outfile.write(f'\n\n##---> {relative_path}\n\n')
        if file_extension.lower() == '.py':
            self.process_python_file(file_path, outfile, symbols_to_exclude)
        else:
            self.process_non_python_file(file_path, outfile)

    def process_python_file(self, file_path, outfile, symbols_to_exclude):
        with open(file_path, 'r', encoding='utf-8') as infile:
            file_content = infile.read()
        try:
            tree = ast.parse(file_content, filename=file_path)
            modifier = ASTModifier(symbols_to_exclude, file_path, self.remove_imports)
            modified_tree = modifier.visit(tree)
            ast.fix_missing_locations(modified_tree)
            modified_code = astor.to_source(modified_tree)
            outfile.write(modified_code)
        except SyntaxError as e:
            logging.warning(f'Syntax error in Python file {file_path}, including without modifications: {e}')
            outfile.write(file_content)

    def process_non_python_file(self, file_path, outfile):
        try:
            with open(file_path, 'r', encoding='utf-8') as infile:
                file_content = infile.read()
            outfile.write(file_content)
        except Exception as e:
            logging.warning(f'Error reading file {file_path}: {e}')
            outfile.write(f'# Error reading file: {e}\n')


class ASTModifier(ast.NodeTransformer):

    def __init__(self, symbols_to_exclude, file_path, remove_imports):
        self.symbols_to_exclude = symbols_to_exclude
        self.file_path = os.path.normpath(file_path)
        self.remove_imports = remove_imports
        super().__init__()

    def visit_Import(self, node):
        if self.remove_imports:
            return None
        return node

    def visit_ImportFrom(self, node):
        if self.remove_imports:
            return None
        return node

    def visit_ClassDef(self, node):
        full_symbol_name = (self.file_path, node.name, 'class')
        if full_symbol_name in self.symbols_to_exclude:
            return None
        return self.generic_visit(node)

    def visit_FunctionDef(self, node):
        parent = getattr(node, 'parent', None)
        if isinstance(parent, ast.ClassDef):
            symbol_type = 'method'
        else:
            symbol_type = 'function'
        full_symbol_name = (self.file_path, node.name, symbol_type)
        if full_symbol_name in self.symbols_to_exclude:
            return None
        return self.generic_visit(node)

    def generic_visit(self, node):
        for child in ast.iter_child_nodes(node):
            child.parent = node
        return super().generic_visit(node)

