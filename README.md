# chatgpt_stock

We are developing a stock-trading-recommendation system using ChatGpt. The workflow
is as follows:

1. Run traditional momentum-based stock selection from a pool of candidates from
  * SP500
  * major ADR, such as ARM, TSM
  * major sector ETF, such as SOQ (semi-conductor)
1. Run financial news web-crawler for top momentum-based performers
  * Retrieve recent news
  * Classification news into Long / Short categories
1. Chatgpt used for understanding Long / Short strength and validations
1. Automated report generation in the following format
  * Stock, Long / Short Action, Liquidity Window, Target Price
