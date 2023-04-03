import flask
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from main import GPT_Translator, SentimentAnalyzer, TradeRecommender, Alpaca, main
from alpaca_trade_api import REST
from alpaca_trade_api.rest import TimeFrame  # Import TimeFrame
from datetime import datetime, timedelta

application = Flask(__name__)

# Alpaca Credentials
alpaca_api_key = "PKWQBRRQ0Q8NABKMHHBZ"
alpaca_secret_key = "QqBxn4wSV188r9SpejVcmGzzdOBaaCF4KZxoMLKQ"
alpaca_base_url = "https://paper-api.alpaca.markets"

api = REST(alpaca_api_key, alpaca_secret_key, alpaca_base_url, api_version='v2')

@application.route('/')
def index():
    return render_template('index.html')

@application.route('/get_portfolio_data', methods=['GET'])
def get_portfolio_data():
    end_date = datetime.now()
    time_span = end_date - timedelta(days=30)
    portfolio_data = []
    positions = api.list_positions()
    
    for position in positions:
        symbol = position.symbol
        # Format the start and end dates as ISO 8601 strings
        start_date_str = time_span.strftime('%Y-%m-%dT%H:%M:%SZ')
        end_date_str = end_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        # Use the formatted dates in the get_bars method call
        historical_data = api.get_bars(symbol, TimeFrame.Day, start_date_str, end_date_str, limit=1000).df
        
        dates = [date.strftime('%Y-%m-%d') for date in historical_data.index]
        closing_prices = historical_data['close'].tolist()
        
        portfolio_data.append({
            'label': symbol,
            'dates': dates,
            'values': closing_prices
        })
        
    return jsonify(portfolio_data)

@application.route('/process', methods=['POST'])
def process():
    user_tweet = request.form['tweet']
    try:
        user_qty = int(request.form['quantity'])
    except ValueError:
        flash("Please enter a valid integer for quantity.")
        return redirect(url_for('index'))

    if user_qty > 100:
        flash("The Maximum amount of Shares per trade is 100.")
        return redirect(url_for('index'))

    response, ticker, sentiment_label, sentiment_scores, trade_recommendation, execute_trade = main(user_tweet, user_qty)
    
    # Get portfolio data
    portfolio_data = get_portfolio_data().get_json()
    
    return render_template('result.html', tweet=user_tweet, response=response, ticker=ticker, sentiment_label=sentiment_label, sentiment_scores=sentiment_scores, trade_recommendation=trade_recommendation, execute_trade=execute_trade, portfolio_data=portfolio_data)

if __name__ == '__main__':
    application.run(debug=True)





