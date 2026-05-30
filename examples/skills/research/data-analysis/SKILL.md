---
name: data-analysis
description: DuckDB-powered analytical engine for large data dumps (JSON, CSV, Parquet). Ingest → Profile → Query → File insights.
argument-hint: "analyze <file_path>"
allowed-tools:
  - Bash
  - FileWrite
auto-invoke: false
model: default
user-invocable: true
context_trigger:
  - "*.json > 10MB"
  - "*.csv > 10MB"
  - "data dump"
  - "analyze this data"
  - "large dataset"
who: Athena agent performing data analysis
what: Ingest, profile, query, and extract insights from large structured datasets
when: User provides a large data file (JSON/CSV/Parquet) or asks for data analysis
where: Local filesystem, DuckDB in-process
why: Eliminates ad-hoc Python one-shots for large data analysis. Provides reusable, cached, SQL-queryable analytical backend.
how: DuckDB embedded OLAP engine + Parquet columnar storage + auto-filing to case studies
---

# Data Analysis Skill (DuckDB Engine)

Wraps the Athena Data Engine (`data_engine.py`) for structured data analysis on large files.

## Triggers

- User provides a JSON, CSV, or Parquet file for analysis
- "Analyze this data", "What's in this file", "Run some numbers on"
- Any file > 10MB that needs analytical queries
- `/analyze` workflow invocation

## Dependencies

```bash
pip install duckdb
```

## Core Scripts

| Script | Purpose |
|--------|---------|
| `.agent/scripts/data_engine.py` | Core DuckDB wrapper — ingest, convert, query, profile |
| `.agent/scripts/auto_file_insights.py` | Auto-file extracted insights as case studies |

## Pipeline

### Phase 1: Ingest

```bash
python3 .agent/scripts/data_engine.py ingest /path/to/data.json
```

This will:
1. Auto-detect format (JSON/CSV/Parquet)
2. For Telegram exports: flatten nested text fields, extract metadata
3. Convert to Parquet with ZSTD compression (cached alongside the original)
4. Print schema, row count, nulls, date range, value distributions

**Cache behavior**: If a Parquet cache already exists and is newer than the source file, ingestion is skipped and the cache is used directly (instant).

### Phase 2: Query

```bash
python3 .agent/scripts/data_engine.py query /path/to/.athena_cache/parquet/data.parquet \
    "SELECT COUNT(*) FROM data WHERE text LIKE '%math%'"
```

The Parquet file is registered as table `data`. Use standard SQL.

**Common patterns**:

```sql
-- Row count
SELECT COUNT(*) FROM data

-- Date range
SELECT MIN(date), MAX(date) FROM data

-- Value distribution
SELECT column_name, COUNT(*) as cnt
FROM data
GROUP BY column_name
ORDER BY cnt DESC
LIMIT 20

-- Text search
SELECT date, text FROM data
WHERE text ILIKE '%keyword%'
LIMIT 10

-- Time series aggregation
SELECT strftime(date::TIMESTAMP, '%Y-%m') as month, COUNT(*) as volume
FROM data
GROUP BY month
ORDER BY month

-- Rate extraction (regex)
SELECT regexp_extract(text, '\$(\d+)', 1)::INT as rate, COUNT(*) as cnt
FROM data
WHERE rate IS NOT NULL
GROUP BY rate
ORDER BY cnt DESC
```

### Phase 3: Extract & File

After analysis, file insights using:

```bash
python3 .agent/scripts/auto_file_insights.py \
    --title "Analysis Title" \
    --domain "Market Analysis" \
    --tags "#data-analysis #market" \
    --context "Brief context" \
    --findings "Finding 1: detail||Finding 2: detail" \
    --patterns "Pattern 1||Pattern 2" \
    --relevance "Active project relevance" \
    --base-dir "./"
```

## Supported Formats

| Format | Detection | Notes |
|--------|-----------|-------|
| **Telegram JSON export** | `"messages"` key in root object | Auto-flattens nested text arrays, extracts metadata |
| **Generic JSON** | `.json` extension | DuckDB `read_json_auto()` |
| **CSV/TSV** | `.csv`/`.tsv` extension | DuckDB `read_csv_auto()` |
| **Parquet** | `.parquet`/`.pq` extension | Direct read, no conversion needed |

## Parquet Cache

- Stored in `.athena_cache/parquet/` alongside the source file
- ZSTD compression (5-10x smaller than JSON)
- Automatic cache invalidation if source file is modified
- Subsequent queries hit cache directly (millisecond latency)

## Performance Characteristics

| Operation | JSON (800MB) | Parquet (cached) |
|-----------|:------------:|:----------------:|
| First ingest | ~60s | — |
| Subsequent load | — | <1s |
| COUNT(*) | ~30s | <100ms |
| GROUP BY | ~45s | <500ms |
| Text search (LIKE) | ~60s | <2s |

## Anti-Patterns

- ❌ Loading entire JSON into Python memory (`json.load()` on 800MB files)
- ❌ Ad-hoc Python scripts for every new question
- ❌ Re-reading raw files on every query
- ❌ Regex extraction without profile step first

## Reference

- [CS-552: Tuition Market Data Archaeology](./.context/memories/case_studies/CS-552-tuition-market-data-archaeology.md) — First use case that exposed the need for this skill
