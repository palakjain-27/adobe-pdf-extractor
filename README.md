# PDF Outline Extractor (Round 1A)
A Python tool for extracting document outlines (headings structure) from PDF files with multilingual support, available as both a standalone script and a Docker container.
Extract structured outlines (H1, H2, H3) from PDF documents using font-size heuristics.

---
Features
Extracts headings (H1, H2, H3) from PDF documents

Supports multiple languages including:

English (en)

Japanese (ja)

Korean (ko)

Detects language automatically based on character patterns

Preserves document structure with page numbers

Generates JSON output with document metadata

Docker support for easy deployment
---

Requirements
For Standalone Use:
Python 3.6+

Dependencies listed in requirements.txt:

pdfminer.six

pdfplumber

regex

For Docker Use:
Docker installed on your system
---

How it works
- Processes all PDFs inside `/app/input/`
- Outputs a structured JSON outline in `/app/output/`
- Detects headings based on font size and position

Build & Run

1. Build Docker image:

```bash
docker build -t pdf-outline .




## Installation
Standalone Installation:
Clone the repository or download the files

Install dependencies:

bash
pip install -r requirements.txt
Docker Installation:
Build the Docker image:

bash
docker build -t pdf-outline-extractor .
Usage
Standalone Usage:
Place your PDF files in the /app/input directory (create it if it doesn't exist)

Run the script:

bash
python main.py
The tool will process all PDFs in the input directory and generate JSON files in /app/output

Docker Usage:
Create input and output directories on your host machine:

bash
mkdir -p ./input ./output
Place your PDF files in the ./input directory

Run the Docker container:

bash
docker run -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output pdf-outline-extractor
The tool will process all PDFs and save JSON outputs in ./output

Volume Mounts Explanation:
-v $(pwd)/input:/app/input - Maps host's ./input to container's /app/input

-v $(pwd)/output:/app/output - Maps host's ./output to container's /app/output

Output Format
The tool generates JSON files with the following structure:

json
{
  "title": "Document Title",
  "outline": [
    {
      "level": "H1",
      "text": "Heading Text",
      "page": 1,
      "language": "en",
      "font_size": 14.5
    },
    ...
  ],
  "metadata": {
    "avg_font_size": 12.0,
    "total_pages": 10
  }
}

Configuration
You can modify the following constants in main.py:

INPUT_DIR: Directory where input PDFs are stored (default: /app/input)

OUTPUT_DIR: Directory where JSON output will be saved (default: /app/output)

How It Works
Language Detection: The tool analyzes text character patterns to determine the document's primary language

Font Analysis: Calculates average font size to identify heading sizes relative to body text

Heading Detection: Uses language-specific heuristics to identify headings at different levels (H1-H3)

Structure Extraction: Groups consecutive words and identifies document structure

Dockerfile Contents
The Docker image is built with the following configuration:

Based on official Python 3.9-slim image

Installs all required dependencies from requirements.txt

Copies the application code into the container

Sets the working directory to /app

Configures the entrypoint to run main.py

Limitations
Works best with text-based PDFs (not scanned documents)

Heading detection may not be perfect for complex layouts

Language detection is based on character patterns and may not be 100% accurate ##

