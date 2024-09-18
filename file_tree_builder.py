import os
import fnmatch
from PyQt5.QtWidgets import QTreeWidgetItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon


class FileTreeBuilder:
    def __init__(self, directory_path, file_type_filter, exclude_patterns):
        self.directory_path = directory_path
        self.file_type_filter = file_type_filter
        self.exclude_patterns = exclude_patterns
        self.file_tree = {}

    def build_tree(self, parent_item):
        self._build_tree_recursive(parent_item, self.directory_path)

    def _build_tree_recursive(self, parent_item, current_path):
        item_list = os.listdir(current_path)
        item_list.sort()  # Optional: sort items

        for item_name in item_list:
            item_path = os.path.join(current_path, item_name)
            normalized_item_path = os.path.normpath(item_path)
            if any(pattern in normalized_item_path for pattern in self.exclude_patterns):
                continue
            if os.path.isdir(item_path):
                # Check if directory contains matching files
                if self.directory_contains_matching_files(item_path):
                    node = QTreeWidgetItem(parent_item, [item_name])
                    node.setFlags(node.flags() | Qt.ItemIsUserCheckable)
                    node.setCheckState(0, Qt.Checked)
                    # Set an icon for directories
                    node.setIcon(0, QIcon.fromTheme("folder"))
                    self.file_tree[item_path] = node
                    self._build_tree_recursive(node, item_path)
            elif os.path.isfile(item_path) and self._file_matches_filter(item_name):
                node = QTreeWidgetItem(parent_item, [item_name])
                node.setFlags(node.flags() | Qt.ItemIsUserCheckable)
                node.setCheckState(0, Qt.Checked)
                # Set an icon for files
                node.setIcon(0, QIcon.fromTheme("text-x-generic"))
                self.file_tree[item_path] = node

    def directory_contains_matching_files(self, directory):
        for root, dirs, files in os.walk(directory):
            root = os.path.normpath(root)
            # Exclude directories based on exclude patterns
            dirs[:] = [d for d in dirs if not any(pattern in os.path.join(root, d) for pattern in self.exclude_patterns)]
            for file in files:
                if any(pattern in os.path.join(root, file) for pattern in self.exclude_patterns):
                    continue
                if self._file_matches_filter(file):
                    return True
        return False

    def _file_matches_filter(self, filename):
        # Check if the file has an extension
        if not os.path.splitext(filename)[1]:
            return False  # File has no extension, do not match
        return any(fnmatch.fnmatch(filename, pattern) for pattern in self.file_type_filter)
