# AI-Earnings-Call-Pipeline
*Note* This represents the current structure and/or progress of the repo (we are currently just researching and code is foundational)

## Installation

### 1. Install the required Python package

The scraper uses the official `defeatbeta-api` library to fetch transcripts and news data. Use pip install defeatbeta-api

*Important*
The defeatbeta-api library depends on a component called cache_httpfs, which may not work natively on Windows (worked for me). If you encounter an error during installation or when running the scraper, refer to the DefeatBeta repo

## 2. Database Setup

The project uses **SQLite** to store transcripts and news locally. The database is created automatically the first time you run the scraper—no manual setup required.

### File Location

By default, the database is saved as `database/earnings.db`.

---

### Tables

#### `transcripts` Table (Earnings Call Transcripts)

| Column | Type | Description |
| :--- | :--- | :--- |
| `ticker` | TEXT | Stock ticker (e.g., `TSLA`) |
| `fiscal_year` | INTEGER | Fiscal year |
| `fiscal_quarter` | INTEGER | Fiscal quarter (1–4) |
| `report_date` | TEXT | Earnings call date (`YYYY-MM-DD`) |
| `full_text` | TEXT | Combined transcript content (all paragraphs) |
| `fetched_at` | DATETIME | Auto-timestamp when inserted |

**Primary Key:** `(ticker, fiscal_year, fiscal_quarter)` – ensures only one transcript per company per quarter is stored.

---

#### `news` Table (Stock News Articles)

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | INTEGER | Auto-incrementing internal ID |
| `source` | TEXT | Data source (currently only `DEFEATBETA`) |
| `source_id` | TEXT | Unique ID from the source (UUID from DefeatBeta) |
| `symbol` | TEXT | The ticker the news is stored for |
| `title` | TEXT | Article headline |
| `content` | TEXT | Full article text (fetched via `get_news()`) |
| `publisher` | TEXT | News publisher (e.g., `Zacks`, `Motley Fool`) |
| `report_date` | TEXT | Publication date (`YYYY-MM-DD`) |
| `type` | TEXT | Article type (e.g., `STORY`) |
| `link` | TEXT | URL to the full article |
| `fetched_at` | DATETIME | Auto-timestamp when inserted |

**Unique Constraint:** `(source, source_id, symbol)` – this allows storing the same article for multiple tickers (e.g., an article mentioning both TSLA and AAPL) without creating duplicate records.

---

## 3. Key Research Findings

This section documents the critical, non-obvious behaviors discovered while testing the `defeatbeta-api` library.

---

### 5.1 Transcripts – Ordering

**`get_transcripts_list()` returns data in ascending order (oldest → newest).**

- The first row (index `0`) is the **oldest** transcript (e.g., 2011 for TSLA).
- The last row (index `-1`) is the **most recent** transcript.

**Correct way to get the latest transcript (example):**
metadata = ticker.earning_call_transcripts().get_transcripts_list()
latest = metadata.iloc[-1]

The transcripts are well formatted and maintained. The api provides the exact content of each earnings-call.
The database is updated every week (according ot the creator)

### 5.2 News - Object Pre-Filtered by Ticker

When you create a Ticker object and call .news(), the resulting object is filtered to only include articles that mention that specific ticker in their symbols list.

Example:
news_tsla = Ticker('TSLA').news()   # Only articles where TSLA is in related_symbols
news_amd  = Ticker('AMD').news()    # Only articles where AMD is in related_symbols

Consequences:
get_news_list() for news_tsla will only return articles that mention TSLA.
If you try to call news_tsla.get_news(uuid) on a UUID that does not mention TSLA, the API will throw an error.

### 5.3 News - Discrepancy on DefeatBeta Repo between related_symbol and symbol 
On the orignal repoit says that get_news_list() and news.print.pretty_table() shows the related_symbols (essentially all the companies talked about in the transcript)
However, when I tested I was only abel to see the symbol that i defined in the ticker variable
For example, when I did Ticker('TSLA') the news articles only showed the TSLA symbol at the top (but the content of the news was unchanged). This is something to keep in mind
