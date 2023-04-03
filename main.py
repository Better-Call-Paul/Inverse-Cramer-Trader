from transformers import AutoTokenizer, AutoModelForSequenceClassification
from scipy.special import softmax
import openai
import re
import alpaca_trade_api as tradeapi
from alpaca_trade_api.rest import REST

class GPT_Translator:
  
    def __init__(self, api_key):
        self.apiKey = api_key
        pass
    
    def getResponse(self, tweet):
  
        API_KEY = "#Your key
        openai.api_key = API_KEY
        model = "text-davinci-002"

        tweetRec = "What is the effect of this development on the company: " + tweet + "?"

        response = openai.Completion.create(
            prompt = tweetRec,
            model = model,
            max_tokens = 100,
            temperature = 0.9,
            n = 3,
            stop = "?"
        )

        return response.choices[0].text
    
    def getTicker(self, tweet, alpaca_api_key, alpaca_secret_key):
        # Initialize the Alpaca API
        api = tradeapi.REST(alpaca_api_key, alpaca_secret_key, base_url='https://paper-api.alpaca.markets', api_version='v2')
        
        #while loop to run until a valid ticker is found
        #check if the ticker is valid with the get_asset function
        ticker_prompt = "Based on the following tweet, return only the ticker symbol of the company that is being discussed, do not include the $, all the characters must be capitalized, and it must be four characters long: " + tweet
      
        while True:
            response = openai.Completion.create(
            prompt=ticker_prompt,
            model="text-davinci-002",
            max_tokens=10,
            temperature=0.9,
            n=1,
        )
            ticker = response.choices[0].text.strip()
            
            try:
                asset = api.get_asset(ticker)
                if asset is not None and asset.tradable:
                    return ticker
            except Exception as e:
                pass
            
            continue
    
                
     
        
class SentimentAnalyzer:

    def __init__(self):
        self.roberta = "cardiffnlp/twitter-roberta-base-sentiment"
        self.model = AutoModelForSequenceClassification.from_pretrained(self.roberta)
        self.tokenizer = AutoTokenizer.from_pretrained(self.roberta)
        self.labels = ['Negative', 'Neutral', 'Positive']

    def analyze(self, response):
        response_words = []
        for word in response.split(' '):
            if word.startswith('@') and len(word) > 1:
                word = '@user'
            elif word.startswith('http'):
                word = "http"
            response_words.append(word)

        response_proc = " ".join(response_words)
        encoded_response = self.tokenizer(response_proc, return_tensors='pt')
        output = self.model(**encoded_response)
        scores = output[0][0].detach().numpy()
        scores = softmax(scores)
        
        minimum_score = scores.argmin()
        minimum_label = self.labels[minimum_score]
        return minimum_label, scores
    
class TradeRecommender:

    def __init__(self, api_key):
        self.api_key = api_key
        openai.api_key = self.api_key

    def recommend_trade(self, ticker, sentiment_label):
        #get the minimum_label from the sentiment analyzer
        
        prompt = f"If the price of {ticker} is trending in a {sentiment_label} direction, should an investor buy or sell a stock. YOU MUST ONLY RESPOND WITH EITHER THE STRING BUY OR SELL, RESPONSE must be all lowercase either buy or sell"

        response = openai.Completion.create(
            prompt=prompt,
            model="text-davinci-002",
            max_tokens=10,  # Limiting max tokens to get a concise response
            temperature=0.9,
            n=1,
            stop=None  # Removing stop tokens to get the full response
        )

        # Extract the trade recommendation from the response and align it to the expected format
        trade_recommendation = response.choices[0].text.strip().lower()

        # Validate the trade recommendation to ensure it is either "buy" or "sell"
        if trade_recommendation == "buy":
            return "buy"
        elif trade_recommendation == "sell":
            return "sell"
        else:
            # Handle unexpected values (e.g., return a default value or raise an exception)
            return "buy"
    
    
class Alpaca:
    def __init__(self, api_key, secret_key, base_url):
        self.api = tradeapi.REST(api_key, secret_key, base_url)
        
    #Method to execute a trade
    def execute_trade(self, symbol, user_qty, side):
        if (self.validate_trade(symbol, user_qty, side) == True):
            market_order = self.api.submit_order(
                symbol=symbol,
                qty=user_qty,
                side=side,
                type="market",
                time_in_force="gtc"
            )
            return "Trade Executed"

        else:
            return "Insufficient Funds or Shares for this Trade"
        


    def validate_trade(self, symbol, user_qty, side):
        
        account = self.api.get_account()
        avaliable_cash = float(account.cash)
        #get the current price of the stock
        stock_price = float(self.api.get_latest_trade(symbol).price)
        
        try:
            position = self.api.get_position(symbol)
            shares = int(position.qty)
        except Exception as e:
            shares = 0
            
        if side == "buy":
            return avaliable_cash >= user_qty * stock_price
        elif side == "sell":
            return shares >= user_qty
        else:
            return False
             
def main(user_tweet, user_qty):
    #Initilizae Alpaca
    endPoint = "https://paper-api.alpaca.markets"
    api_key = #Your Key
    secret_key = #Your Key
    base_url = "https://paper-api.alpaca.markets"
    alpaca = Alpaca(api_key, secret_key, base_url)
    # GPT
    
    gpt_translator = GPT_Translator("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")
    response = gpt_translator.getResponse(user_tweet)
    ticker = gpt_translator.getTicker(user_tweet, api_key, secret_key)

    # Analysis
    sentiment_analyzer = SentimentAnalyzer()
    sentiment_label, sentiment_scores = sentiment_analyzer.analyze(response)
        
    trade_recommender = TradeRecommender("Your_Key")
    trade_recommendation = trade_recommender.recommend_trade(ticker, sentiment_label)
    
 
    # Execute a market buy order for the ticker
    symbol = ticker
    qty = user_qty
    side = trade_recommendation
    alpaca.execute_trade(symbol, qty, side)

    # Return the results to be displayed on the website
    #should return the string from execute_trade
    return response, ticker, sentiment_label, sentiment_scores, trade_recommendation, alpaca.execute_trade(symbol, qty, side)

# ...

if __name__ == "__main__":
    
    main(example_tweet, user_qty)

