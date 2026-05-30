---
name: dashboard-builder
description: "Build self-contained interactive HTML dashboards with charts, filters, and tables. Generates a single browser-openable file — no server or dependencies required."
vibe: "Data without visualization is just noise."
context_trigger: "dashboard, visualization, KPI, chart, analytics view, build dashboard, data dashboard, monitoring, metrics view"
argument_hint: "<description> [data source]"
auto-invoke: false
model: default
source: "anthropics/knowledge-work-plugins — data/skills/build-dashboard (2026-05-24)"
stolen_date: "2026-05-24"
---

# Dashboard Builder — Interactive HTML Dashboards

> **Stolen from**: [Anthropic Data Plugin — build-dashboard](https://github.com/anthropics/knowledge-work-plugins/tree/main/data/skills/build-dashboard) (2026-05-24)
> **Adaptation**: Stripped enterprise connectors, added Athena-specific data patterns.

## When to Use

- Creating executive overview with KPI cards
- Turning query results into a shareable self-contained report
- Building a monitoring snapshot
- Needing multiple charts with filters in one browser-openable file
- Client deliverables requiring interactive data presentation

## Workflow

### 1. Understand Requirements

Determine:
- **Purpose**: Executive overview, operational monitoring, deep-dive analysis, team reporting
- **Audience**: Who will use this dashboard?
- **Key metrics**: What numbers matter most?
- **Dimensions**: What should users be able to filter or slice by?
- **Data source**: Live query, pasted data, CSV file, or sample data

### 2. Gather Data

**If data is available** → Parse, clean, embed as JSON in the HTML file.
**If working from description** → Create realistic sample dataset. Note it uses sample data. Provide swap instructions.

### 3. Design Layout

Follow standard dashboard layout:

```
┌──────────────────────────────────────────────────┐
│  Dashboard Title                    [Filters ▼]  │
├────────────┬────────────┬────────────┬───────────┤
│  KPI Card  │  KPI Card  │  KPI Card  │ KPI Card  │
├────────────┴────────────┼────────────┴───────────┤
│                         │                        │
│    Primary Chart        │   Secondary Chart      │
│    (largest area)       │                        │
│                         │                        │
├─────────────────────────┴────────────────────────┤
│                                                  │
│    Detail Table (sortable, scrollable)           │
│                                                  │
└──────────────────────────────────────────────────┘
```

Adapt to content:
- 2-4 KPI cards at top for headline numbers
- 1-3 charts in middle for trends and breakdowns
- Optional detail table at bottom for drill-down
- Filters in header or sidebar depending on complexity

### 4. Build HTML Dashboard

Single self-contained HTML file:

**Structure**: Semantic HTML5, responsive grid (CSS Grid/Flexbox), filter controls, KPI cards, chart containers, sortable data table.

**Styling**: Professional dark/light scheme, card-based layout with subtle shadows, consistent typography (system fonts), responsive, print-friendly.

**Interactivity**: Chart.js for charts, filter dropdowns updating all views simultaneously, sortable columns, hover tooltips, number formatting.

**Data**: All data embedded as JavaScript variables. No external fetches. Works completely offline.

### 5. Chart Types

| Chart | Use For |
|:------|:--------|
| Line | Time series trends |
| Bar | Category comparisons |
| Doughnut | Composition (<6 categories) |
| Stacked bar | Composition over time |
| Mixed (bar + line) | Volume with rate overlay |

### 6. Base Template

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard Title</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.5.1" integrity="sha384-jb8JQMbMoBUzgWatfe6COACi2ljcDdZQ2OxczGA3bGNeWe+6DChMTBJemed7ZnvJ" crossorigin="anonymous"></script>
    <style>
        /* --- Design System --- */
        :root {
            --bg: #0f1117; --surface: #1a1d2e; --border: #2a2d3e;
            --text: #e4e4e7; --text-muted: #71717a;
            --accent: #6366f1; --accent-hover: #818cf8;
            --success: #22c55e; --warning: #eab308; --danger: #ef4444;
            --radius: 12px; --shadow: 0 4px 24px rgba(0,0,0,.3);
        }
        * { margin:0; padding:0; box-sizing:border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
               background: var(--bg); color: var(--text); line-height: 1.5; }
        .dashboard { max-width: 1400px; margin: 0 auto; padding: 24px; }
        .kpi-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 24px; }
        .kpi-card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 20px; }
        .kpi-label { font-size: 0.875rem; color: var(--text-muted); margin-bottom: 4px; }
        .kpi-value { font-size: 2rem; font-weight: 700; }
        .kpi-change { font-size: 0.875rem; margin-top: 4px; }
        .kpi-change.positive { color: var(--success); }
        .kpi-change.negative { color: var(--danger); }
        .chart-row { display: grid; grid-template-columns: 2fr 1fr; gap: 16px; margin-bottom: 24px; }
        .chart-card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 20px; }
        .chart-card h3 { font-size: 1rem; margin-bottom: 12px; color: var(--text-muted); }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 10px 12px; text-align: left; border-bottom: 1px solid var(--border); }
        th { color: var(--text-muted); font-size: 0.8rem; text-transform: uppercase; cursor: pointer; }
        th:hover { color: var(--accent); }
        .filters { display: flex; gap: 12px; align-items: center; }
        select { background: var(--surface); color: var(--text); border: 1px solid var(--border);
                 border-radius: 8px; padding: 8px 12px; font-size: 0.875rem; }
        footer { text-align: center; color: var(--text-muted); font-size: 0.8rem; margin-top: 32px; }
        @media (max-width: 768px) { .chart-row { grid-template-columns: 1fr; } }
    </style>
</head>
<body>
    <div class="dashboard">
        <header style="display:flex; justify-content:space-between; align-items:center; margin-bottom:24px;">
            <h1>Dashboard Title</h1>
            <div class="filters"><!-- Filter controls --></div>
        </header>
        <section class="kpi-row"><!-- KPI cards --></section>
        <section class="chart-row"><!-- Chart containers --></section>
        <section class="chart-card"><!-- Data table --></section>
        <footer>Data as of: <span id="data-date"></span></footer>
    </div>
    <script>
        const DATA = []; // Embedded data
        class Dashboard {
            constructor(data) { this.rawData = data; this.filteredData = data; this.charts = {}; this.init(); }
            init() { this.setupFilters(); this.renderKPIs(); this.renderCharts(); this.renderTable(); }
            applyFilters() { /* Filter + re-render all views */ }
            setupFilters() {}
            renderKPIs() {}
            renderCharts() {}
            updateCharts() {}
            renderTable() {}
        }
        const dashboard = new Dashboard(DATA);
    </script>
</body>
</html>
```

### 7. Save and Open

1. Save as descriptive name (e.g., `sales_dashboard.html`)
2. Open in user's default browser
3. Confirm it renders correctly
4. Provide instructions for updating data or customizing

## References

- [Anthropic build-dashboard](https://github.com/anthropics/knowledge-work-plugins/tree/main/data/skills/build-dashboard) — Source skill
- [A30 Tutorial 2 Slide Deck](./.context/memories/case_studies/) — Athena precedent for web-based deliverables
