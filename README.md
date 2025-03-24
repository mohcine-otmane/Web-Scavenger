# Web Scavenger

A powerful web scraping tool that searches across multiple search engines to find and categorize various types of files and documents.

## Features

- Multi-engine search (Google and Bing)
- Automatic file type detection and categorization
- Support for various file formats (PDF, DOCX, XLSX, etc.)
- Undetected Chrome browser automation
- Detailed logging and error handling
- JSON output format for results
- Graphical User Interface (GUI) version available

## Requirements

- Python 3.13+
- Chrome browser
- Required Python packages (see requirements.txt)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/mohcine-otmane/Web-Scavenger.git
cd Web-Scavenger
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Command Line Version
Run the script:
```bash
python WebScavanger.py
```

### Graphical User Interface Version
Run the GUI version:
```bash
python webscavanger_gui.py
```

The program will prompt you for:
1. Your search query
2. Number of pages to search (default: 3)

Results will be saved to `webscavanger_results.json` and displayed in the console/GUI.

## License

Copyright (c) 2024 WebScavanger 