# Inverse-Cramer-Trader

Inverse-Cramer Trader is an algorithmic trading web application that uses natural language processing (Hugging Face roBERTa) to analyze inputed finnancial opinions on public companys through sentiment analysis to make trades on the stock market. The application is built with Python and utilizes the PyTorch and Transformers libraries for NLP, OpenAI API for initial analysis and ticker retrieval as well as the Alpaca API for trading.

## Installation

To use Inverse-Cramer Trader, first clone the repository:

```
git clone https://github.com/your_username/inverse-cramer-trader.git
```

Then navigate to the project directory and install the required packages:

```
cd inverse-cramer-trader
pip install -r requirements.txt
```
## Usage

To start the application, run the following command:
```
python application.py
```
This will start the Flask web server and present the index.html screen for user input

## Configuration 

Before using the application, you will need to configure it with your own Alpaca API and OpenAI credentials in the following lines.
```
API_KEY = "your_OpenAI_API_Key"
APCA_API_KEY_ID=<your_alpaca_api_key_id>
APCA_API_SECRET_KEY=<your_alpaca_api_secret_key>
APCA_API_BASE_URL=https://paper-api.alpaca.markets
```
Replace <your_alpaca_api_key_id> and <your_alpaca_api_secret_key> with your own API credentials. Note that this application is currently configured to use the Alpaca Paper Trading API, with the base url determining live/paper trades.

## Contributing

Contributions to Inverse-Cramer Trader are welcome! Please open an issue or pull request on the GitHub repository.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
