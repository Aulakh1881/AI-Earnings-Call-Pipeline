import sys
import defeatbeta_api 
from defeatbeta_api.data.ticker import Ticker
from database.db_manager import DatabaseManager

class DefeatBetaScraper:
    def __init__(self, db_path: str = "database/earnings.db"):
        self.db = DatabaseManager(db_path)

    def fetch_and_store_latest(self, ticker: str) -> dict:
        # The latest trasncript is usually found in the last row of the metadata DataFrame
        print(f"Fetching latest transcript for {ticker}...")
        
        try:
            ticker_obj = Ticker(ticker.upper())
            transcripts = ticker_obj.earning_call_transcripts()
            
            # Get metadata (list of available quarters)
            metadata = transcripts.get_transcripts_list()
            
            if metadata.empty:
                return {
                    "status": "error",
                    "message": f"No transcripts found for {ticker}"
                }
            
            # The list is ascending (oldest → newest), so the LAST row is the newest
            latest = metadata.iloc[-1]
            
            fiscal_year = int(latest['fiscal_year'])
            fiscal_quarter = int(latest['fiscal_quarter'])
            report_date = latest['report_date']
            
            # Fetch the full transcript for that specific quarter
            df = transcripts.get_transcript(fiscal_year, fiscal_quarter)
            
            # Combine all paragraphs into one string
            full_text = "\n".join(df['content'].tolist())
            
            if not full_text or len(full_text) < 100:
                return {
                    "status": "error",
                    "message": f"Transcript content too short or missing for {ticker}"
                }
            
            success = self.db.insert_transcript(
                ticker=ticker.upper(),
                fiscal_year=fiscal_year,
                fiscal_quarter=fiscal_quarter,
                report_date=report_date,
                full_text=full_text
            )
            
            if success:
                return {
                    "status": "success",
                    "ticker": ticker.upper(),
                    "fiscal_year": fiscal_year,
                    "fiscal_quarter": fiscal_quarter,
                    "quarter_label": f"Q{fiscal_quarter} {fiscal_year}",
                    "report_date": report_date,
                    "paragraphs": len(df),
                    "text_preview": full_text[:200] + "..."
                }
            else:
                return {
                    "status": "skipped",
                    "message": f"Transcript for {ticker} Q{fiscal_quarter} {fiscal_year} already exists."
                }
                
        except Exception as e:
            print(f"Error fetching transcript for {ticker}: {e}")
            return {
                "status": "error",
                "message": str(e)
            }

