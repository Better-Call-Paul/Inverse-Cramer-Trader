#TODO: Make FrontEnd Look Nice
#TODO: Make the program return the insufficient reccomendation if encountered 
#TODO: Deploy on AWS

import flask
from flask import Flask, render_template, request
# Import the necessary classes and functions from main.py
from Main import GPT_Translator, SentimentAnalyzer, TradeRecommender, Alpaca, main

application = Flask(__name__)

@application.route('/')
def index():
    return render_template('index.html')

@application.route('/process', methods=['POST'])
def process():
    # Get the user's input tweet from the form
    user_tweet = request.form['tweet']
    
    # Get the user's input quantity from the form
    user_qty = int(request.form['quantity'])
    
    # Call the main function with the user's input tweet and user_qty
    response, ticker, sentiment_label, sentiment_scores, trade_recommendation = main(user_tweet, user_qty)
    
    # Render the result.html template and pass the variables to be displayed on the website, also return if the trade was successful or not, if not then display the error message: Insufficient Funds or Shares for this Trade
    
    return render_template('result.html', tweet=user_tweet, response=response, ticker=ticker, sentiment_label=sentiment_label, sentiment_scores=sentiment_scores, trade_recommendation=trade_recommendation)

if __name__ == '__main__':
    application.run(debug=True)
    




