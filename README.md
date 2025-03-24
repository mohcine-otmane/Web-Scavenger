# Web Scavenger
![Uploading WebScavenger.png…]()

A powerful web scraping tool that searches across multiple search engines to find and categorize various types of files and documents.

## Features

- Multi-engine search (Google and Bing)
- Automatic file type detection and categorization
- Support for various file formats (PDF, DOCX, XLSX, etc.)
- Undetected Chrome browser automation
- Detailed logging and error handling
- JSON output format for results

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

Run the script:
```bash
python WebScavanger.py
```

The program will prompt you for:
1. Your search query
2. Number of pages to search (default: 3)

Results will be saved to `webscavanger_results.json` and displayed in the console.

## License

Copyright (c) 2024 WebScavanger 
