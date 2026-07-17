import sqlite3
from typing import List, Dict, Optional
from datetime import date, datetime, timedelta

class DatabaseManager:
    def __init__(self, db_path = "earning_calls.db"):
        self.db_path = db_path
        self.create_tables()
    
    def create_tables(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Transcripts table
            # Made composite key because a companies only have 1 earnings transcript per quarter (will also help in later methods)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transcripts (
                    ticker TEXT,
                    fiscal_year INTEGER,
                    fiscal_quarter INTEGER,
                    report_date TEXT,
                    full_text TEXT,
                    fetched_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (ticker, fiscal_year, fiscal_quarter) 
                )
            ''')

            # News table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS news (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT NOT NULL,              -- e.g., DefeatBeta
                    source_id TEXT NOT NULL,           -- UUID from DefeatBeta or anything to uniquely identify the news item
                    symbol TEXT,                       -- Single ticker per record
                    title TEXT,
                    content TEXT,
                    publisher TEXT,
                    report_date TEXT,
                    news_type TEXT,
                    link TEXT,
                    fetched_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(source, source_id, symbol)          -- Allow same article for different symbol
                )
            ''')
            conn.commit()
            print(f"Database initialized at {self.db_path}")
    
    def transcript_exists(self, ticker: str, fiscal_year: int, fiscal_quarter: int) -> bool:
        # Check if a transcript for a specific (ticker, year, quarter) already exists
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT 1 FROM transcripts WHERE ticker=? AND fiscal_year=? AND fiscal_quarter=?",
            (ticker, fiscal_year, fiscal_quarter)
        )
        exists = cursor.fetchone() is not None
        conn.close()
        return exists
    
    def insert_transcript(self, ticker: str, fiscal_year: int, fiscal_quarter: int, report_date: str, full_text: str) -> bool:
        # Insert a new earnings-call into the db. Return true if inserted or false if already exists (duplicate)
        quarter_label = f"Q{fiscal_quarter} {fiscal_year}"

        # Check if the transcript already exists
        if self.transcript_exists(ticker, fiscal_year, fiscal_quarter):
            print(f"Transcript for {ticker} ({quarter_label}) already exists. Skipping...")
            return False
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO transcripts 
            (ticker, fiscal_year, fiscal_quarter, report_date, full_text)
            VALUES (?, ?, ?, ?, ?)
            """,
            (ticker, fiscal_year, fiscal_quarter, report_date, full_text)
        )

        conn.commit()
        conn.close()
        print(f"Inserted {ticker} ({quarter_label}) transcript.")
        return True
    
    def get_previous_transcripts(self, ticker: str, limit: int = 3) -> List[Dict]:
        # Fetch the most recent N transcripts for a given ticker.
        # Returns a list of dicts sorted from OLDEST to NEWEST (ascending)
        # Realistically 3-4 previous trasncripts should be enough to analyze relevant trends 

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT fiscal_year, fiscal_quarter, full_text
            FROM transcripts
            WHERE ticker = ?
            ORDER BY fiscal_year DESC, fiscal_quarter DESC
            LIMIT ?
            """,
            (ticker, limit)
        )

        rows = cursor.fetchall()
        conn.close()

        results = [dict(row) for row in rows]
        results.reverse() # Returns oldest -> newest

        return results
    
    def get_latest_transcript_metadata(self, ticker: str) -> Optional[Dict]:
        # Get the fiscal_year, fiscal_quarter, and report_date of the most recent transcript
        # Returns None if no transcripts exists for this ticker
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(
            """
            SELECT fiscal_year, fiscal_quarter, report_date
            FROM transcripts
            WHERE ticker = ?
            ORDER BY fiscal_year DESC, fiscal_quarter DESC
            LIMIT 1
            """,
            (ticker,)
        )
        
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    # Haven't tested this yet
    def insert_news(self, source: str, source_id: str, symbol: str, title: str, content: str, publisher: str, report_date: str, type: str, link: str) -> bool:
        
        # Insert a news article for a specific symbol.
        # Returns True if inserted, False if duplicate (same source, source_id, symbol).
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                INSERT OR IGNORE INTO news 
                (source, source_id, symbol, title, content, publisher, report_date, news_type, link)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (source, source_id, symbol, title, content, publisher, report_date, news_type, link)
            )
            conn.commit()
            inserted = cursor.rowcount > 0
            conn.close()
            return inserted
        except Exception as e:
            print(f"Error inserting news: {e}")
            conn.close()
            return False

