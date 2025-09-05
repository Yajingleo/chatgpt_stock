# chatgpt_stock

We are developing a stock-trading-recommendation system using ChatGpt. The workflow
is as follows:

1. *Stock selection*: Run traditional momentum-based stock selection from a pool of candidates from
   * SP500
   * major ADR, such as ARM, TSM
   * major sector ETF, such as SOQ (semi-conductor)
1. *News crawler*: Run financial news web-crawler for top momentum-based performers
   * Retrieve recent news
   * Classification news into Long / Short categories
1. *Liquidity window analysis*: Find historical periodicity of stock prices
   * Period: how long it would take a stock to keep rallying or selling-off
   * Liquidity window: how long one investor would hold and execute a buy or sell
1. Chatgpt used for understanding Long / Short strength and validations
   * Prompt engineering for reading and understanding the news
   * Give a numerical rating for BUY, HOLD, SELL
1. Automated report generation in the following format
   * Stock, Long / Short Action, Liquidity Window, Target Price
