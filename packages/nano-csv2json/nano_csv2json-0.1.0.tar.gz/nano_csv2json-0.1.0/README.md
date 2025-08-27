# nano-csv2json
[![PyPI](https://img.shields.io/pypi/v/nano-csv2json-py.svg?color=blue)](https://pypi.org/project/nano-csv2json-py/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
![Size](https://img.shields.io/badge/size-~1KB-lightgrey.svg)
[![CI](https://github.com/ozgunlu/nano-csv2json/actions/workflows/ci.yml/badge.svg)](https://github.com/ozgunlu/nano-csv2json/actions)

Tiny **CSV → JSON Lines** converter — ~1 KB, zero deps.
Single-file, CLI included. Auto-sniffs delimiter; headers optional. Perfect for code-golf, minimal containers, or just for fun.

---

## ✨ Features
- ✅ CSV → **JSONL** (one JSON per line)
- ✅ Auto-detect delimiter (`,`, `;`, `\t`, …)
- ✅ Uses header row if present; `--no-header` → keys: `c1,c2,...`
- ✅ Zero dependencies, single tiny file

---

## 🚀 Usage
```bash
# Local (from repo)
python app_min.py data.csv
python app_min.py --no-header data_nohdr.csv
```

After installing:

```bash
# CLI
pip install nano-csv2json
nano-csv2json data.csv > out.jsonl
type data.csv | nano-csv2json         # Windows
cat data.csv | nano-csv2json          # Linux/macOS
```
> Output is JSON Lines (newline-separated JSON objects).

---

## 🤓 Why so small?

- Uses only the stdlib: `csv`, `json`, `io` — **no pandas**.
- Auto-detects delimiter with `csv.Sniffer()` (comma/semicolon/tab…).
- Streams to **JSON Lines** (one JSON per line) — no in-memory data frames.
- Header row → `csv.DictReader`; `--no-header` → `c1,c2,...` keys via `csv.reader`.
- Single tiny file + tiny CLI: perfect for scripts, containers, CI.

---

## 🎉 Fun Ideas

- **Pretty-print JSONL**
```bash
nano-csv2json data.csv | python -m json.tool
```
- **Filter with jq**
```bash
nano-csv2json data.csv | jq -r 'select(.status=="ok")'
```
- **STDIN piping**
```bash
curl -s https://example.com/data.csv | nano-csv2json > out.jsonl
# Windows
Invoke-WebRequest https://example.com/data.csv -UseBasicParsing | nano-csv2json > out.jsonl
```
- **Semicolon/TSV auto-sniff**
```bash
nano-csv2json data_semicolon.csv > out.jsonl
nano-csv2json data.tsv > out.jsonl
```
- **No header → synthetic keys**
```bash
nano-csv2json --no-header raw.csv | head -1
# {"c1":"val1","c2":"val2",...}
```
- **Compress on the fly**
```bash
nano-csv2json data.csv | gzip > out.jsonl.gz
```
- **First N records**
```bash
nano-csv2json data.csv | head -100 > sample.jsonl
```

---

> **Tip: Need a single JSON array? Collect lines with jq:**
> nano-csv2json data.csv | jq -s '.' > array.json

---

## 📜 License

MIT © 2025

