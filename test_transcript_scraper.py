from quarterly_report_scraper import DefeatBetaScraper

def main():
    scraper = DefeatBetaScraper(db_path="database/earnings.db")

    # Example ticker to fetch
    ticker = "TSLA"
    result = scraper.fetch_and_store_latest(ticker)
    
    # Print the result
    print("\n" + "=" * 60)
    print("RESULT:")
    print("=" * 60)
    for key, value in result.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    main()
