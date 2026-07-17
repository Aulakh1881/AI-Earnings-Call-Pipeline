import defeatbeta_api 
from defeatbeta_api.data.ticker import Ticker

ticker = Ticker('AMD')

news = ticker.news()
# Should print the news item with that UUID. 
# Also, unlike the orignal readme on DefeatBeta, the ticker symbol (for both news list and pretty table) only shows the ticker you defined (as shown in line 4)
news.print_pretty_table("b67526eb-581a-35b2-8357-b4f282fe876f") 

# This examples shows what happens when you try to fetch a news item that doesn't exist for the specified ticker 
# Not shown in orignal DefeatBeta repo, found through discovery
ticker = Ticker('TSLA')
news = ticker.news()

try:
    news.print_pretty_table("b67526eb-581a-35b2-8357-b4f282fe876f")
except Exception as e:
    print("Error fetching news item for TSLA:", e)

# Get list of relevent news items for a specific ticker
# Could use list (with report date) to filter for news items that are relevant to a specific earnings report
print(news.get_news_list())
