import os
import fnmatch
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTextEdit, QTreeWidget, QTreeWidgetItem, QPushButton, QFileDialog, QMessageBox,
    QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox, 
    QSpinBox, QPlainTextEdit, QProgressDialog

)
from PyQt5.QtWidgets import QCheckBox, QStyledItemDelegate, QPushButton

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QProgressDialog
from PyQt5.QtGui import QIcon

from PyQt5.QtCore import Qt, QDateTime
from database_manager import DatabaseManager
from file_tree_builder import FileTreeBuilder
from file_merger import FileMerger
from symbol_extractor import SymbolExtractor
from remote_indexer import RemoteIndexer

# main_window.py

import os
import fnmatch
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTextEdit, QTreeWidget, QTreeWidgetItem, QPushButton, QFileDialog,
    QMessageBox, QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView,
    QCheckBox, QSpinBox, QPlainTextEdit, QProgressDialog
)
from PyQt5.QtWidgets import QCheckBox, QStyledItemDelegate, QPushButton
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QProgressDialog
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QDateTime
from database_manager import DatabaseManager
from file_tree_builder import FileTreeBuilder
from file_merger import FileMerger
from symbol_extractor import SymbolExtractor
from remote_indexer import RemoteIndexer

# main_window.py

import os
import fnmatch
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTextEdit, QTreeWidget, QTreeWidgetItem, QPushButton, QFileDialog,
    QMessageBox, QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView,
    QCheckBox, QSpinBox, QPlainTextEdit, QProgressDialog
)
from PyQt5.QtWidgets import QCheckBox, QStyledItemDelegate, QPushButton
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QProgressDialog
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QDateTime
from database_manager import DatabaseManager
from file_tree_builder import FileTreeBuilder
from file_merger import FileMerger
from symbol_extractor import SymbolExtractor
from remote_indexer import RemoteIndexer


class MainWindow(QMainWindow):

    def __init__(self, project):
        super().__init__()
        self.selected_files = None
        self.setWindowTitle(f"File Merger Application - {project['name']}")
        self.setGeometry(600, 300, 800, 600)
        self.project = project
        self.db_manager = DatabaseManager(self.project['db_file'])
        self.directory_path = ''
        self.file_tree = {}
        self.excluded_files = set()
        self.remove_imports = False
        self._build_ui()
        self.load_project_settings()
        self.load_remote_settings()
        self.populate_file_tree()
        self.load_symbols_into_table()
        self.apply_symbol_filters()

    def _build_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        self.tab1 = QWidget()
        self._build_tab1()
        self.tabs.addTab(self.tab1, 'File Selection')

        self.tab2 = QWidget()
        self._build_tab2()
        self.tabs.addTab(self.tab2, 'Symbol Index')

        self.tab3 = QWidget()
        self._build_tab3()
        self.tabs.addTab(self.tab3, 'Remote Docs')

        self.remove_imports_checkbox = QCheckBox("Remove Python imports")
        self.remove_imports_checkbox.stateChanged.connect(self.on_remove_imports_changed)
        self.layout.addWidget(self.remove_imports_checkbox)

        self.create_output_button = QPushButton('Create output file')
        self.create_output_button.clicked.connect(self.merge_selected_files)
        self.layout.addWidget(self.create_output_button)

    def on_remove_imports_changed(self, state):
        self.remove_imports = state == Qt.Checked

    def _build_tab1(self):
        tab1_layout = QVBoxLayout(self.tab1)
        self.file_type_layout = QHBoxLayout()
        self.file_type_label = QLabel('File Type Filter:')
        self.file_type_layout.addWidget(self.file_type_label)
        self.file_type_input = QLineEdit()
        self.file_type_layout.addWidget(self.file_type_input)
        tab1_layout.addLayout(self.file_type_layout)
        self.exclude_patterns_label = QLabel('Exclude Patterns (one per line):')
        tab1_layout.addWidget(self.exclude_patterns_label)
        self.exclude_patterns_input = QTextEdit()
        self.exclude_patterns_input.setFixedHeight(60)
        tab1_layout.addWidget(self.exclude_patterns_input)
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel('Files and Folders')
        self.tree.setSelectionMode(QTreeWidget.MultiSelection)
        self.tree.itemChanged.connect(self.on_item_changed)
        tab1_layout.addWidget(self.tree)
        self.button_layout = QHBoxLayout()
        self.reload_button = QPushButton('Reload')
        self.reload_button.clicked.connect(self.reload_tree)
        self.button_layout.addWidget(self.reload_button)
        tab1_layout.addLayout(self.button_layout)

    def _build_tab2(self):
        tab2_layout = QVBoxLayout(self.tab2)
        self.filter_layout = QHBoxLayout()
        self.symbol_type_checkboxes = {}
        symbol_types = ['class', 'function', 'method', 'global_var', 'class_attr']
        for symbol_type in symbol_types:
            checkbox = QCheckBox(symbol_type.capitalize())
            checkbox.setChecked(True)
            checkbox.stateChanged.connect(self.apply_symbol_filters)
            self.filter_layout.addWidget(checkbox)
            self.symbol_type_checkboxes[symbol_type] = checkbox
        self.filter_layout.addStretch()
        self.include_all_button = QPushButton('Include All')
        self.include_all_button.clicked.connect(self.include_all_symbols)
        self.filter_layout.addWidget(self.include_all_button)
        self.exclude_all_button = QPushButton('Exclude All')
        self.exclude_all_button.clicked.connect(self.exclude_all_symbols)
        self.filter_layout.addWidget(self.exclude_all_button)
        tab2_layout.addLayout(self.filter_layout)
        self.symbol_table = QTableWidget()
        self.symbol_table.setColumnCount(9)
        self.symbol_table.setHorizontalHeaderLabels(['ID', 'Symbol Name',
                                                     'Symbol Type', 'Parent ID', 'File Name', 'Line Start',
                                                     'Line End', 'Modified At', 'Include'])
        self.symbol_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.symbol_table.setSortingEnabled(True)
        tab2_layout.addWidget(self.symbol_table)
        self.reindex_button = QPushButton('Reindex Project')
        self.reindex_button.clicked.connect(self.reindex_project)
        tab2_layout.addWidget(self.reindex_button)

    def _build_tab3(self):
        tab3_layout = QVBoxLayout(self.tab3)
        self.url_input_label = QLabel('Enter URLs (one per line):')
        tab3_layout.addWidget(self.url_input_label)
        self.url_input = QPlainTextEdit()
        tab3_layout.addWidget(self.url_input)

        self.depth_layout = QHBoxLayout()
        self.depth_label = QLabel('Depth:')
        self.depth_layout.addWidget(self.depth_label)
        self.depth_spinbox = QSpinBox()
        self.depth_spinbox.setRange(0, 3)
        self.depth_spinbox.setValue(0)
        self.depth_layout.addWidget(self.depth_spinbox)
        self.depth_layout.addStretch()
        tab3_layout.addLayout(self.depth_layout)

        # Nowy wiersz dla CSS Selectors
        self.css_selectors_layout = QHBoxLayout()
        self.css_selectors_label = QLabel('CSS Selectors (separated by ;):')
        self.css_selectors_layout.addWidget(self.css_selectors_label)
        self.css_selectors_input = QLineEdit()
        self.css_selectors_layout.addWidget(self.css_selectors_input)
        tab3_layout.addLayout(self.css_selectors_layout)

        self.convert_html_checkbox = QCheckBox('Convert HTML to Markdown')
        self.convert_html_checkbox.setChecked(True)
        tab3_layout.addWidget(self.convert_html_checkbox)

        self.reindex_remote_button = QPushButton('Reindex Remote')
        self.reindex_remote_button.clicked.connect(self.reindex_remote)
        tab3_layout.addWidget(self.reindex_remote_button)

        self.remote_table = QTableWidget()
        self.remote_table.setColumnCount(3)
        self.remote_table.setHorizontalHeaderLabels(['URL', 'Page Title', 'Include'])
        self.remote_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        tab3_layout.addWidget(self.remote_table)

        self.remote_buttons_layout = QHBoxLayout()
        self.include_all_remote_button = QPushButton('Include All')
        self.include_all_remote_button.clicked.connect(self.include_all_remote)
        self.remote_buttons_layout.addWidget(self.include_all_remote_button)
        self.exclude_all_remote_button = QPushButton('Exclude All')
        self.exclude_all_remote_button.clicked.connect(self.exclude_all_remote)
        self.remote_buttons_layout.addWidget(self.exclude_all_remote_button)
        self.remote_buttons_layout.addStretch()
        tab3_layout.addLayout(self.remote_buttons_layout)

    def include_all_symbols(self):
        for row in range(self.symbol_table.rowCount()):
            symbol_type_item = self.symbol_table.item(row, 2)
            if symbol_type_item:
                symbol_type = symbol_type_item.text()
                if symbol_type in ['class', 'function', 'method']:
                    checkbox = self.symbol_table.cellWidget(row, 8)
                    if checkbox and not checkbox.isChecked():
                        checkbox.blockSignals(True)
                        checkbox.setChecked(True)
                        checkbox.blockSignals(False)
                        symbol_id = checkbox.symbol_id
                        self.db_manager.update_symbol_include_state(symbol_id, 1)

    def exclude_all_symbols(self):
        for row in range(self.symbol_table.rowCount()):
            symbol_type_item = self.symbol_table.item(row, 2)
            if symbol_type_item:
                symbol_type = symbol_type_item.text()
                if symbol_type in ['class', 'function', 'method']:
                    checkbox = self.symbol_table.cellWidget(row, 8)
                    if checkbox and checkbox.isChecked():
                        checkbox.blockSignals(True)
                        checkbox.setChecked(False)
                        checkbox.blockSignals(False)
                        symbol_id = checkbox.symbol_id
                        self.db_manager.update_symbol_include_state(symbol_id, 0)

    def include_all_remote(self):
        for row in range(self.remote_table.rowCount()):
            checkbox = self.remote_table.cellWidget(row, 2)
            if checkbox and not checkbox.isChecked():
                checkbox.blockSignals(True)
                checkbox.setChecked(True)
                checkbox.blockSignals(False)
                page_id = checkbox.page_id
                self.db_manager.update_remote_page_include_state(page_id, 1)

    def exclude_all_remote(self):
        for row in range(self.remote_table.rowCount()):
            checkbox = self.remote_table.cellWidget(row, 2)
            if checkbox and checkbox.isChecked():
                checkbox.blockSignals(True)
                checkbox.setChecked(False)
                checkbox.blockSignals(False)
                page_id = checkbox.page_id
                self.db_manager.update_remote_page_include_state(page_id, 0)

    def load_remote_pages_into_table(self):
        self.remote_table.setRowCount(0)
        remote_pages = self.db_manager.get_all_remote_pages()
        for page in remote_pages:
            row_position = self.remote_table.rowCount()
            self.remote_table.insertRow(row_position)
            self.remote_table.setItem(row_position, 0, QTableWidgetItem(page['url']))
            self.remote_table.setItem(row_position, 1, QTableWidgetItem(page['title']))
            include_checkbox = QCheckBox()
            include_checkbox.setChecked(page['include_in_dump'] == 1)
            include_checkbox.stateChanged.connect(self.on_remote_include_checkbox_state_changed)
            include_checkbox.page_id = page['id']
            self.remote_table.setCellWidget(row_position, 2, include_checkbox)

    def on_remote_include_checkbox_state_changed(self, state):
        checkbox = self.sender()
        page_id = checkbox.page_id
        include_in_dump = 1 if state == Qt.Checked else 0
        self.db_manager.update_remote_page_include_state(page_id, include_in_dump)

    def closeEvent(self, event):
        self.save_project_state()
        super().closeEvent(event)

    def save_project_state(self):
        selected_files = []
        for path, node in self.file_tree.items():
            if node.checkState(0) == Qt.Checked:
                selected_files.append(path)

        settings = self.db_manager.load_settings()
        settings['selected_files'] = '\n'.join(selected_files)
        self.db_manager.save_settings(settings)

    def save_remote_settings(self, urls, depth, css_selectors):
        settings = {
            'remote_urls': '\n'.join(urls),
            'remote_depth': str(depth),
            'convert_html_to_md': str(int(self.convert_html_checkbox.isChecked())),
            'css_selectors': css_selectors  # Dodane
        }
        self.db_manager.save_remote_settings(settings)

    def load_remote_settings(self):
        settings = self.db_manager.load_remote_settings()
        urls = settings.get('remote_urls', '')
        depth = int(settings.get('remote_depth', '0'))
        self.url_input.setPlainText(urls)
        self.depth_spinbox.setValue(depth)
        convert_html_to_md = settings.get('convert_html_to_md', '1')
        self.convert_html_checkbox.setChecked(bool(int(convert_html_to_md)))
        css_selectors = settings.get('css_selectors', '')  # Dodane
        self.css_selectors_input.setText(css_selectors)  # Dodane
        self.load_remote_pages_into_table()

    def apply_symbol_filters(self):
        selected_types = [stype for stype, cb in self.symbol_type_checkboxes.items() if cb.isChecked()]
        self.load_symbols_into_table(selected_types)

    def load_project_settings(self):
        settings = self.db_manager.load_settings()
        self.directory_path = settings.get('directory', '')
        self.file_type_input.setText(settings.get('file_type_filter', '*.py'))
        exclude_patterns = settings.get('exclude_patterns', '')
        self.exclude_patterns_input.setText(exclude_patterns.replace(';', '\n'))

        selected_files = settings.get('selected_files', '').split('\n')
        self.selected_files = set(selected_files) if selected_files != [''] else set()

    def save_project_settings(self):
        excluded_files = [path for path, node in self.file_tree.items() if node.checkState(0) == Qt.Unchecked]
        settings = {
            'directory': self.directory_path,
            'file_type_filter': self.file_type_input.text().strip(),
            'exclude_patterns': ';'.join(self.get_exclude_patterns()),
            'excluded_files': '\n'.join(excluded_files)
        }
        self.db_manager.save_settings(settings)

    def populate_file_tree(self):
        self.tree.clear()
        self.file_tree = {}
        file_type_filter = [pattern.strip() for pattern in self.file_type_input.text().split(';') if pattern.strip()]
        exclude_patterns = self.get_exclude_patterns()
        root_node = QTreeWidgetItem(self.tree, [self.directory_path])
        root_node.setFlags(root_node.flags() | Qt.ItemIsUserCheckable)
        root_node.setCheckState(0, Qt.Checked)
        file_tree_builder = FileTreeBuilder(self.directory_path, file_type_filter, exclude_patterns)
        file_tree_builder.build_tree(root_node)
        self.file_tree = file_tree_builder.file_tree
        self.expand_all(root_node)
        self.apply_selected_files()

    def expand_all(self, item):
        item.setExpanded(True)
        for i in range(item.childCount()):
            self.expand_all(item.child(i))

    def get_exclude_patterns(self):
        return self.exclude_patterns_input.toPlainText().strip().splitlines()

    def apply_selected_files(self):
        for path, node in self.file_tree.items():
            if path in self.selected_files:
                node.setCheckState(0, Qt.Checked)
            else:
                node.setCheckState(0, Qt.Unchecked)

    def apply_excluded_files(self):
        for path, node in self.file_tree.items():
            if path in self.excluded_files:
                node.setCheckState(0, Qt.Unchecked)

    def on_item_changed(self, item, column):
        if item.checkState(0) == Qt.PartiallyChecked:
            item.setCheckState(0, Qt.Checked)
        state = item.checkState(0)
        for i in range(item.childCount()):
            child = item.child(i)
            child.setCheckState(0, state)

    def merge_selected_files(self):
        output_file, _ = QFileDialog.getSaveFileName(self, 'Save Merged File', '', 'Text Files (*.txt);;All Files (*)')
        if output_file:
            exclude_patterns = self.get_exclude_patterns()
            convert_html_to_md = self.convert_html_checkbox.isChecked()
            css_selectors = self.css_selectors_input.text().strip()
            file_merger = FileMerger(self.file_tree, self.directory_path, exclude_patterns, self.db_manager, convert_html_to_md, css_selectors, self.remove_imports)
            file_merger.merge_files(output_file)
            QMessageBox.information(self, 'Merge Complete', 'Files have been merged successfully.')

    def reload_tree(self):
        self.save_project_settings()
        self.populate_file_tree()

    def reindex_project(self):
        self.save_project_settings()
        exclude_patterns = self.get_exclude_patterns()
        selected_files = self.get_selected_files()
        symbol_extractor = SymbolExtractor(self.directory_path, exclude_patterns, self.db_manager, selected_files)
        self.reindex_button.setEnabled(False)
        self.progress_dialog = QProgressDialog('Reindexing in progress...', None, 0, 0, self)
        self.progress_dialog.setWindowTitle('Reindexing')
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.setCancelButton(None)
        self.progress_dialog.show()
        self.reindex_thread = ReindexThread(symbol_extractor)
        self.reindex_thread.finished.connect(self.reindex_finished)
        self.reindex_thread.start()

    def reindex_finished(self):
        self.progress_dialog.close()
        self.reindex_button.setEnabled(True)
        self.load_symbols_into_table()
        QMessageBox.information(self, 'Reindexing Complete', 'Project reindexing is complete.')

    def reindex_remote(self):
        urls = self.url_input.toPlainText().strip().splitlines()
        depth = self.depth_spinbox.value()
        css_selectors = self.css_selectors_input.text().strip()  # Dodane
        if not urls:
            QMessageBox.warning(self, 'Input Error', 'Please enter at least one URL.')
            return
        self.save_remote_settings(urls, depth, css_selectors)  # Zaktualizowane
        self.reindex_remote_button.setEnabled(False)
        self.remote_progress_dialog = QProgressDialog('Reindexing remote URLs...', None, 0, 0, self)
        self.remote_progress_dialog.setWindowTitle('Reindexing')
        self.remote_progress_dialog.setWindowModality(Qt.WindowModal)
        self.remote_progress_dialog.setCancelButton(None)
        self.remote_progress_dialog.show()
        self.remote_thread = RemoteReindexThread(urls, depth, self.db_manager)
        self.remote_thread.finished.connect(self.reindex_remote_finished)
        self.remote_thread.start()

    def reindex_remote_finished(self):
        self.remote_progress_dialog.close()
        self.reindex_remote_button.setEnabled(True)
        self.load_remote_pages_into_table()
        QMessageBox.information(self, 'Reindexing Complete', 'Remote reindexing is complete.')

    def get_selected_files(self):
        selected_files = []
        for path, node in self.file_tree.items():
            if node.checkState(0) == Qt.Checked and os.path.isfile(path):
                selected_files.append(os.path.normpath(path))
        return selected_files

    def load_symbols_into_table(self, selected_types=None):
        self.symbol_table.setRowCount(0)
        symbols = self.db_manager.get_all_symbols()
        for symbol in symbols:
            if selected_types and symbol['symbol_type'] not in selected_types:
                continue
            row_position = self.symbol_table.rowCount()
            self.symbol_table.insertRow(row_position)
            self.symbol_table.setItem(row_position, 0, QTableWidgetItem(str(symbol['id'])))
            self.symbol_table.setItem(row_position, 1, QTableWidgetItem(symbol['symbol_name']))
            self.symbol_table.setItem(row_position, 2, QTableWidgetItem(symbol['symbol_type']))
            self.symbol_table.setItem(row_position, 3, QTableWidgetItem(str(symbol['parent_id']) if symbol['parent_id'] else ''))
            normalized_location = os.path.normpath(symbol['location'])
            self.symbol_table.setItem(row_position, 4, QTableWidgetItem(normalized_location))
            self.symbol_table.setItem(row_position, 5, QTableWidgetItem(str(symbol['line_start'])))
            self.symbol_table.setItem(row_position, 6, QTableWidgetItem(str(symbol['line_end'])))
            self.symbol_table.setItem(row_position, 7, QTableWidgetItem(symbol['modified_at']))
            symbol_type = symbol['symbol_type']
            if symbol_type in ['class', 'function', 'method']:
                include_checkbox = QCheckBox()
                include_checkbox.setChecked(symbol['include_in_dump'] == 1)
                include_checkbox.stateChanged.connect(self.on_include_checkbox_state_changed)
                include_checkbox.symbol_id = symbol['id']
                self.symbol_table.setCellWidget(row_position, 8, include_checkbox)
            else:
                self.symbol_table.setItem(row_position, 8, QTableWidgetItem(''))

    def on_include_checkbox_state_changed(self, state):
        checkbox = self.sender()
        symbol_id = checkbox.symbol_id
        include_in_dump = 1 if state == Qt.Checked else 0
        self.db_manager.update_symbol_include_state(symbol_id, include_in_dump)


class ReindexThread(QThread):
    finished = pyqtSignal()

    def __init__(self, symbol_extractor):
        super().__init__()
        self.symbol_extractor = symbol_extractor

    def run(self):
        self.symbol_extractor.reindex()
        self.finished.emit()

class RemoteReindexThread(QThread):
    finished = pyqtSignal()

    def __init__(self, urls, depth, db_manager):
        super().__init__()
        self.urls = urls
        self.depth = depth
        self.db_manager = db_manager

    def run(self):
        remote_indexer = RemoteIndexer(self.urls, self.depth, self.db_manager)
        remote_indexer.reindex()
        self.finished.emit()
