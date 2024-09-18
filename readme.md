# File Merger Application

## Overview

The File Merger Application is a powerful Python-based desktop tool designed to aggregate and merge content from multiple sources into a single, comprehensive file. Its primary purpose is to create a consolidated knowledge base suitable for use with Large Language Models (LLMs).

Key features include:
- Merging multiple Python files from a project directory
- Indexing and including content from remote web pages
- Intelligent symbol extraction and filtering
- User-friendly graphical interface for easy project management

This application is particularly useful for researchers, developers, and data scientists who need to prepare large, diverse datasets for training or fine-tuning LLMs.

## Main Components

1. **StartWindow**: Initial project selection and creation interface
2. **MainWindow**: Primary workspace for managing files, symbols, and remote content
3. **DatabaseManager**: Handles data storage and retrieval
4. **ProjectManager**: Manages project lifecycle and recent project tracking
5. **FileTreeBuilder**: Creates a navigable structure of project files
6. **FileMerger**: Combines selected content into a single output file
7. **SymbolExtractor**: Analyzes Python files to extract relevant symbols
8. **RemoteIndexer**: Fetches and processes content from web pages

## Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Steps

1. Clone the repository or download the source code:
   ```
   git clone https://github.com/your-repo/file-merger-application.git
   cd file-merger-application
   ```

2. Create a virtual environment (optional but recommended):
   - On Windows:
     ```
     python -m venv venv
     venv\Scripts\activate
     ```
   - On macOS and Linux:
     ```
     python3 -m venv venv
     source venv/bin/activate
     ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run the application:
   ```
   python main.py
   ```

## Usage

1. Launch the application and create a new project or open an existing one.
2. In the File Selection tab, choose the files you want to include in your merged output.
3. Use the Symbol Index tab to view and filter extracted symbols from Python files.
4. In the Remote Docs tab, add and manage remote web pages to include in your merged content.
5. Click "Create output file" to generate your consolidated knowledge base file.

## Customization

The application is highly customizable. You can modify the source code to add new features, change the user interface, or adjust the merging logic to better suit your specific needs for creating LLM knowledge bases.

## Contributing

Contributions to improve the File Merger Application are welcome. Please feel free to submit pull requests or open issues to suggest improvements or report bugs.

## License

MIT