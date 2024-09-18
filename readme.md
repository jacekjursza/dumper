# File Merger Application Documentation

## Overview

The File Merger Application is a Python-based desktop application that allows users to manage, analyze, and merge multiple Python files from a project directory. It also supports indexing and including content from remote web pages. The application uses SQLite for data storage and PyQt5 for the graphical user interface.

## Main Components

1. **StartWindow**: The initial window that allows users to create new projects, open existing ones, or import projects.
2. **MainWindow**: The primary interface for managing project files, symbols, and remote pages.
3. **DatabaseManager**: Handles all database operations, including initialization, upgrades, and data retrieval/storage.
4. **ProjectManager**: Manages project creation, loading, and recent project tracking.
5. **FileTreeBuilder**: Builds a tree structure of the project files and directories.
6. **FileMerger**: Responsible for merging selected files and remote pages into a single output file.
7. **SymbolExtractor**: Extracts symbols (classes, functions, methods, variables) from Python files.
8. **RemoteIndexer**: Fetches and indexes remote web pages.

## Key Features

1. **Project Management**
   - Create new projects
   - Open existing projects
   - Import projects from .db files
   - Track recent projects

2. **File Management**
   - Display project files in a tree structure
   - Filter files by type and exclude patterns
   - Select/deselect files for merging

3. **Symbol Indexing**
   - Extract symbols from Python files (classes, functions, methods, variables)
   - Display symbols in a table with filtering options
   - Include/exclude specific symbols from the merge output

4. **Remote Page Indexing**
   - Fetch and index remote web pages
   - Support for crawling linked pages up to a specified depth
   - Convert HTML to Markdown (optional)
   - Apply CSS selectors to filter content

5. **File Merging**
   - Merge selected files and remote pages into a single output file
   - Respect symbol inclusion/exclusion settings
   - Handle remote page content based on user settings

## Detailed Component Descriptions

### StartWindow (start_window.py)
- Displays recent projects
- Provides options to open, create, or import projects
- Initializes the main application window upon project selection

### MainWindow (main_window.py)
- Consists of three main tabs: File Selection, Symbol Index, and Remote Docs
- Manages file tree display, symbol table, and remote page table
- Handles user interactions for file selection, symbol filtering, and remote page management
- Initiates file merging process

### DatabaseManager (database_manager.py)
- Initializes and upgrades the SQLite database schema
- Manages CRUD operations for settings, symbols, and remote pages
- Handles database queries for various application features

### ProjectManager (project_manager.py)
- Manages project creation, loading, and import
- Tracks and updates recent projects list
- Handles project file operations (copy, save)

### FileTreeBuilder (file_tree_builder.py)
- Builds a tree structure of project files and directories
- Applies file type filters and exclusion patterns
- Creates QTreeWidgetItems for GUI representation

### FileMerger (file_merger.py)
- Merges selected files and remote pages into a single output file
- Processes Python files to include/exclude symbols based on user settings
- Handles remote page content inclusion and optional HTML to Markdown conversion

### SymbolExtractor (symbol_extractor.py)
- Parses Python files using the ast module
- Extracts symbols (classes, functions, methods, variables) from Python code
- Updates the database with extracted symbols

### RemoteIndexer (remote_indexer.py)
- Fetches remote web pages
- Supports crawling linked pages up to a specified depth
- Applies CSS selectors for content filtering (if specified)
- Updates the database with fetched page information

## Database Schema

The application uses an SQLite database with the following main tables:

1. **settings**: Stores project-wide settings
2. **symbols**: Stores extracted symbols from Python files
3. **remote_pages**: Stores information about indexed remote pages

## User Workflow

1. Start the application and select a project (create new, open existing, or import)
2. In the File Selection tab, choose files to include in the merge
3. In the Symbol Index tab, view and filter extracted symbols, choosing which to include/exclude
4. In the Remote Docs tab, add remote URLs to index and include in the merge
5. Initiate the merge process to create a single output file

