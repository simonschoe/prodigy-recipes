## README

1. Annotate rating reports using `prodigy`
```sh
set PRODIGY_PORT=8080
python -m prodigy cls_reports {database} input/reports.jsonl -F cls.py
```

Classes:
1. Internal - Capital Structure
2. Internal - Operating Performance
3. Internal - M&A
4. External - Macro or Regulatory Environment
5. External - Sovereign Rating
6. External - Methodology
7. Other
