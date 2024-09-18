# Knowledge Dumper


## Overview

The **Knowledge Dumper** is a Python-based tool designed to aggregate content from multiple sources into a single, comprehensive text file. This tool is particularly useful for preparing large knowledge bases for use with Large Language Models (LLMs) by consolidating data from local directories, Python files, and remote web pages.

### Key Features:

1) Merge content from websites, with conversion to Markdown. 

![image](https://github.com/user-attachments/assets/6e7d14f5-dfab-4fb0-a234-bac9bc966e35)


2) Include files from a selected directory, supporting filtering by patterns and file extensions.


![image](https://github.com/user-attachments/assets/9e5648a6-b8fb-451c-babe-b419f534e59f)


3) Selectively extract Python classes, methods, functions, and symbols.

![image](https://github.com/user-attachments/assets/0989e932-2385-4428-917c-3f8687e2ba2c)

4) User-friendly graphical interface for easy project management.
5) Ideal for researchers, developers, and data scientists building knowledge bases for LLMs.

## Main Components

1. **StartWindow**: Interface for project selection and creation.
2. **MainWindow**: Primary workspace for managing files, symbols, and remote content.
3. **DatabaseManager**: Handles data storage and retrieval.
4. **ProjectManager**: Manages the project lifecycle and recent project tracking.
5. **FileTreeBuilder**: Creates a navigable structure of project files.
6. **FileMerger**: Combines selected content into a single output file.
7. **SymbolExtractor**: Analyzes Python files to extract relevant symbols.
8. **RemoteIndexer**: Fetches and processes content from web pages.

## Why Was This Tool Created?

This tool was born out of a personal need to streamline the process of gathering diverse content sources into a cohesive document. While it may have niche applications, it is extremely valuable for creating knowledge bases to aid LLM development and training.

## Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Installation Steps

1. Clone the repository or download the source code:
   ```bash
   git clone https://github.com/your-repo/file-merger-application.git
   cd file-merger-application
   ```

2. Create a virtual environment (optional but recommended):
   - On Windows:
     ```bash
     python -m venv venv
     venv\Scripts\activate
     ```
   - On macOS and Linux:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   python main.py
   ```

## Usage

1. Launch the application and create a new project or open an existing one.
2. In the **File Selection** tab, choose the files to include in your merged output.
3. Use the **Symbol Index** tab to view and filter extracted symbols from Python files.
4. In the **Remote Docs** tab, add and manage remote web pages to include in your merged content.
5. Click "Create output file" to generate your consolidated knowledge base file.

## Customization

This tool is highly customizable. Modify the source code to add new features, adjust the user interface, or tweak the merging logic to meet your specific needs, especially when preparing LLM knowledge bases.

## Contributing

Contributions to the project are welcome. Submit pull requests or open issues to suggest improvements or report bugs.

## License

This project is licensed under the MIT License.
