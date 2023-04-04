from transformers import AutoTokenizer, AutoModelForSequenceClassification
from scipy.special import softmax
import openai
import re
import alpaca_trade_api as tradeapi
from alpaca_trade_api.rest import REST

#Contains methods to make OpenAI API calls
#Methods: getResponse, getTicker
class GPT_Translator:
  
    def __init__(self, api_key):
        self.apiKey = api_key
        pass
    
    def getResponse(self, tweet):
  
        API_KEY = "YOUR-KEY"
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
        
     
        ticker_prompt = "Based on the following tweet, return only the ticker symbol of the company that is being discussed, do not include the $, all the characters must be capitalized, and it must be four characters long: " + tweet
        #while loop to run until a valid ticker is found
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
    
#Sentiment Analysis Section      
class SentimentAnalyzer:

    def __init__(self):
        self.roberta = "cardiffnlp/twitter-roberta-base-sentiment" #from Hugging Face: https://huggingface.co/cardiffnlp/twitter-roberta-base-sentiment
        #Load the model and tokenizer
        self.model = AutoModelForSequenceClassification.from_pretrained(self.roberta)
        self.tokenizer = AutoTokenizer.from_pretrained(self.roberta)
        #Labels for the sentiment analysis
        self.labels = ['Negative', 'Neutral', 'Positive']

    #Parameters: tweet - the tweet to be analyzed
    #Returns: the sentiment label and the scores for each label
    def analyze(self, response):
        # Preprocess the response
        response_words = []
        for word in response.split(' '):
            # Remove usernames
            if word.startswith('@') and len(word) > 1:
                word = '@user'
            #Remove the URL
            elif word.startswith('http'):
                word = "http"
            response_words.append(word)

        #Concatenate Processed Words into Processed Response
        response_proc = " ".join(response_words)
 
        #Encode the response, using Hugging Face's tokenizer
        encoded_response = self.tokenizer(response_proc, return_tensors='pt')
        #Get the sentiment scores from the model
        output = self.model(**encoded_response)
        #Get the scores for each label
        scores = output[0][0].detach().numpy()
        #Normalize the scores
        scores = softmax(scores)
        
        #Get the label with the lowest score
        minimum_score = scores.argmin()
        minimum_label = self.labels[minimum_score]
        #Return the label and scores
        return minimum_label, scores
    
class TradeRecommender:

    def __init__(self, api_key):
        self.api_key = api_key
        openai.api_key = self.api_key

    # Parameters: ticker - the ticker of the stock to be traded
    #             sentiment_label - the sentiment label of the stock
    # Returns: the trade recommendation: either "buy" or "sell"
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
        
    # Parameters: symbol - the ticker of the stock to be traded
    #             qty - the quantity of shares to be traded
    #             side - the side of the trade (either "buy" or "sell")
    # Returns: the result of the trade
    def execute_trade(self, symbol, qty, side):
        try:
            # Check if the quantity is greater than the maximum allowed (100)
            if qty > 100:
                return f"Error: Maximum shares per trade is 100. Please adjust the quantity."

            # Check if it's a sell order and if the user has enough shares
            if side == 'sell':
                position = self.api.get_position(symbol)
                if int(position.qty) < qty:
                    return f"Error: You don't have enough shares to sell. You have {position.qty} shares of {symbol}."

            # If both checks pass, submit the order
            market_order = self.api.submit_order(
                symbol=symbol,
                qty=qty,
                side=side,
                type='market',
                time_in_force='gtc'
            )
            return f"Order submitted: {market_order}"
        except Exception as e:
            return f"Error: {str(e)}"

    # Parameters: symbol - the ticker of the stock to be traded
    #             user_qty - the quantity of shares to be traded
    #             side - the side of the trade (either "buy" or "sell")
    # Returns: True if the trade is valid, False otherwise
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
    #Initiliaze Alpaca Credentials
    endPoint = "https://paper-api.alpaca.markets"
    api_key = "YOUR-KEY"
    secret_key = "YOUR-KEY"
    base_url = "https://paper-api.alpaca.markets"
    alpaca = Alpaca(api_key, secret_key, base_url)
    # GPT
    
    gpt_translator = GPT_Translator("YOUR-KEY")
    response = gpt_translator.getResponse(user_tweet)
    ticker = gpt_translator.getTicker(user_tweet, api_key, secret_key)

    # Analysis
    sentiment_analyzer = SentimentAnalyzer()
    sentiment_label, sentiment_scores = sentiment_analyzer.analyze(response)
        
    trade_recommender = TradeRecommender("YOUR-KEY")
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

