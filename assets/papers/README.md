# Paper Assets

This directory stores long-lived literature assets, not project code.

```text
metadata/  Generated reports, manifests, citation-source tables, and helper scripts.
pdf/       Local PDFs, grouped by topic or related-work role.
fulltext/  Markdown full text extracted from local PDFs.
notes/     Human reading notes for papers we expect to cite.
```

## Standard Workflow

1. Archive source PDFs under `pdf/`, with at most one topic/category level.
2. Convert PDFs into Markdown fulltext:

   ```bash
   python D:/0-Research/0-Tools/research-standard/convert_pdfs_to_fulltext.py .
   ```

3. Review `metadata/fulltext_summary.md` for failures and quality flags.
4. Keep reading notes in `notes/`; do not edit generated `fulltext/` outputs by hand.

