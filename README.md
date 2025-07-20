# PDF Outline Extractor (Round 1A)

Extract structured outlines (H1, H2, H3) from PDF documents using font-size heuristics.

How it works
- Processes all PDFs inside `/app/input/`
- Outputs a structured JSON outline in `/app/output/`
- Detects headings based on font size and position

Build & Run

1. Build Docker image:

```bash
docker build -t pdf-outline .

