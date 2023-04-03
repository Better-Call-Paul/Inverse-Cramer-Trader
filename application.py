import flask
from flask import Flask, render_template, request, jsonify
# Import the necessary classes and functions from main.py
from main import GPT_Translator, SentimentAnalyzer, TradeRecommender, Alpaca, main
from alpaca_trade_api import REST as tradeapi
from datetime import datetime, timedelta

application = Flask(__name__)

#Alpaca Credentials

alpaca_api_key = #YOUR KEY
alpaca_secret_key = #YOUR CODE
alpaca_base_url = "https://paper-api.alpaca.markets"

api = tradeapi(alpaca_api_key, alpaca_secret_key, alpaca_base_url, api_version='v2')

@application.route('/')
def index():
    return render_template('index.html')

@application.route('/get_porfolio_data', methods = ['GET'])
def get_portfolio_data():
    end_date = datetime.now()
    time_span = end_date - timedelta(days=30)
    portfolio_data = []
    positions = api.list_positions()
    
    for position in positions:
        # Get the historical data for this stock
        #extract the ticker, quantity, initial buy price, current price, and current value
        symbol = position.symbol
        historical_data = api.get_barset(symbol, 'day', start=time_span, end=end_date).df
        
        dates = [date.strftime('%Y-%m-%d') for date in historical_data.index]
        closing_prices = historical_data[symbol]['close'].tolist()
        
        portfolio_data.append({
            'label': symbol,
            'dates': dates,
            'values': closing_prices
        })
        
    return jsonify(portfolio_data)
       


@application.route('/process', methods=['POST'])
def process():
    # Get the user's input tweet from the form
    user_tweet = request.form['tweet']
    
    user_qty = int(request.form['quantity'])
    
    try:
        user_qty = int(request.form['quantity'])
    except ValueError:
        flash("Please enter a valid integer for quantity.")
        return redirect(url_for('index'))

    if user_qty > 100:
        flash("The Maximum amount of Shares per trade is 100.")
        return redirect(url_for('index'))

    # Call the main function with the user's input tweet and user_qty
    response, ticker, sentiment_label, sentiment_scores, trade_recommendation, execute_trade = main(user_tweet, user_qty)
    
    # Render the result.html template and pass the variables to be displayed on the website, also return if the trade was successful or not, if not then display the error message: Insufficient Funds or Shares for this Trade
    
    return render_template('result.html', tweet=user_tweet, response=response, ticker=ticker, sentiment_label=sentiment_label, sentiment_scores=sentiment_scores, trade_recommendation=trade_recommendation, execute_trade=execute_trade) 



if __name__ == '__main__':
    application.run(debug=True)
    





