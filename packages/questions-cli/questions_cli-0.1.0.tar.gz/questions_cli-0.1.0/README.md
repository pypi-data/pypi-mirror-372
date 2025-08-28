## Questions App Query CLI

A CLI for processing a questions for search queries on the app.

### Install from PyPI

```bash
pip install questions-cli
```

### Install (local dev)

```bash
pip install -e .
```

### Usage

- Show help:

```bash
questions-cli --help
```

- Show version:

```bash
questions-cli --version
```

- Quick run (process CSV):

```bash
questions-cli data/queries.csv
```

- Explicit ingest command (same behavior):

```bash
questions-cli ingest data/queries.csv
```

### Common options

- `-d, --delimiter` CSV delimiter (default `,`)
- `--dry-run` Parse and classify/generate without DB writes
- `--limit N` Process only first N rows
- `--subjects-file PATH` Subjects mapping file (csv/yaml/json)

### Examples

```bash
questions-cli data/queries.csv --dry-run
questions-cli ingest data/queries.csv -d ';' --limit 100
questions-cli ingest data/queries.csv --subjects-file subjects.yaml
``` 