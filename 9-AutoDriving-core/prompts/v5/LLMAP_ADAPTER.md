# LLMAP parser prompt provenance and adapter

Source: Yuan et al., *LLMAP: LLM-Assisted Multi-Objective Route Planning with User Preferences*, Findings of EMNLP 2025, Appendix D.2 and frozen repository commit `281f6ad95f42ca386400e5288f006aeffa2ac282`, `dataset/HIPP.py`.

The three `llmap_*_original.txt` files preserve the repository prompt wording. The experimental request substitutes only `{{instruction}}` in the user template. Output adaptation occurs after collection:

- normalize `"None"` to JSON `null`;
- parse `HH:00` as minutes after midnight;
- retain `quality_weight` as the planning weight;
- record and validate `distance_weight`, then omit it from the common four-field intent because the common solver uses `1-quality_weight`;
- normalize known POI spacing/underscore aliases without consulting gold labels;
- reject malformed or unknown content rather than repairing it from the dataset.

This is reported as “LLMAP-parser prompt, unified-backend rerun”, not as a complete reproduction of LLMAP or MSGS.
