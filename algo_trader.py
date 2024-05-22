import requests
import pandas as pd
import yfinance as yf
# from ta.trend import SMAIndicator
import talib
import datetime
from tqdm import tqdm


def fetch_nse_stocks():
    # Fetch list of stocks from NSE
    response = requests.get('https://api.kite.trade/instruments')
    # Parse the response as a CSV file and create a pandas DataFrame
    stocks = pd.DataFrame([line.split(',') for line in response.text.split('\n')])
    stocks.columns = stocks.iloc[0]
    stocks = stocks[1:]
   
    
    nse_stocks = stocks[stocks.segment == 'NSE']
    return nse_stocks

def get_history_data(symbol):
    # Fetch historical data for the given symbol
    data = yf.download(symbol, start="2022-01-01", end="2024-12-31", progress=False)
    return data

def pattern_analysis(symbol):
    print(f"------------ Pattern analysis for symbol: {symbol} -----------------", end="\n")
    # Getting historical data from yahoo finance
    hist_data = get_history_data(symbol)
    print("Historical data size:", hist_data.shape)
    if hist_data.shape[0] < 90:
        print("Insufficient data for analysis: expected at least 90 days of data.")
        return None
    
    # Create a list to store the data
    patterns_recognised = []
    rsi_trend = ""
    macd_trend = ""
    sma_value = 0.0
    wma_value = 0.0
    obv_value = 0.0

    pattern_names = talib.get_function_groups()['Pattern Recognition']
    for pattern_name in pattern_names:
        pattern = getattr(talib, pattern_name)
        patterns = pattern(hist_data['Open'], hist_data['High'], hist_data['Low'], hist_data['Close'])
        pattern_dates = hist_data.index[patterns != 0]
        today = datetime.date.today()
        last_five_days = [today - datetime.timedelta(days=i) for i in range(5)]
        for pattern_date in pattern_dates:
            if pattern_date.date() in last_five_days:
                patterns_recognised.append(pattern_name)

    # Calculate MACD
    macd, signal, hist = talib.MACD(hist_data['Close'])
    if macd[-1] > signal[-1]:
        macd_trend = "UP"
    elif macd[-1] < signal[-1]:
        macd_trend = "DOWN"
    else:
        macd_trend = "Sideways"

    # Calculate RSI
    rsi = talib.RSI(hist_data['Close'])
    if rsi[-1] > 70:
        rsi_trend = "UP"
    elif rsi[-1] < 30:
        rsi_trend = "DOWN"
    else:
        rsi_trend = "Sideways"

    # Calculate SMA
    sma = talib.SMA(hist_data['Close'], timeperiod=14)
    sma_value = sma[-1]

    # Calculate WMA
    wma = talib.WMA(hist_data['Close'], timeperiod=14)
    wma_value = wma[-1]

    # Calculate OBV
    obv = talib.OBV(hist_data['Close'], hist_data['Volume'])
    obv_value = obv[-1]

    # Return the analysis results as a list
    return [symbol, patterns_recognised, rsi_trend, macd_trend, sma_value, wma_value, obv_value]


def pattern_analysis_old(symbol):
    print(f"------------ Pattern analysis for symbol: {symbol} -----------------", end="\n")
    hist_data = get_history_data(symbol)
    print("Historical data size:", hist_data.shape)
    if hist_data.shape[0] < 90:
        print("Insufficient data for analysis: expected at least 90 days of data.")
        return
    # patterns = talib.CDLDOJI(hist_data['Open'], hist_data['High'], hist_data['Low'], hist_data['Close']) 
    pattern_names = talib.get_function_groups()['Pattern Recognition']
    for pattern_name in pattern_names:
        # print("Analyzing pattern:", pattern_name)
        pattern = getattr(talib, pattern_name)
        patterns = pattern(hist_data['Open'], hist_data['High'], hist_data['Low'], hist_data['Close'])
        pattern_dates = hist_data.index[patterns != 0]
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        last_five_days = [today - datetime.timedelta(days=i) for i in range(5)]
        for pattern_date in pattern_dates:
            if pattern_date.date() in last_five_days:
                # pattern_description = talib.get_function_groups().get('Pattern Descriptions', {}).get(pattern_name, 'No description available')
                print("Pattern occurred on", pattern_date.date(), ":", pattern_name)
                last_day_closing_price = hist_data['Close'].loc[pattern_date]
                print("Last day closing price:", last_day_closing_price)
                # print("Pattern description:", pattern_description)
                
    # Calculate MACD
    macd, signal, hist = talib.MACD(hist_data['Close'])
    if macd[-1] > signal[-1]:
        macd_trend = "UP"
    elif macd[-1] < signal[-1]:
        macd_trend = "DOWN"
    else:
        macd_trend = "Sideways"
    print("MACD Trend:", macd_trend)

    # Calculate RSI
    rsi = talib.RSI(hist_data['Close'])
    if rsi[-1] > 70:
        rsi_trend = "UP"
    elif rsi[-1] < 30:
        rsi_trend = "DOWN"
    else:
        rsi_trend = "Sideways"
    print("RSI Trend:", rsi_trend)

    # Calculate STOCHRSI
    fastk, fastd = talib.STOCHRSI(hist_data['Close'])
    if fastk[-1] > fastd[-1]:
        stochrsi_trend = "UP"
    elif fastk[-1] < fastd[-1]:
        stochrsi_trend = "DOWN"
    else:
        stochrsi_trend = "Sideways"
    print("STOCHRSI Trend:", stochrsi_trend)

    # Calculate SMA
    sma = talib.SMA(hist_data['Close'], timeperiod=14)
    print("SMA:", sma[-1])

    # Calculate OBV
    obv = talib.OBV(hist_data['Close'], hist_data['Volume'])
    print("OBV:", obv[-1])

    # Calculate WMA
    wma = talib.WMA(hist_data['Close'], timeperiod=14)
    print("WMA:", wma[-1])
   

def main():
    # Fetch list of NSE stocks
    nse_stocks = fetch_nse_stocks()
    print("NSE Stocks size:", nse_stocks.shape[0])

    data_list = []
    for index, row in tqdm(nse_stocks.iterrows(), total=nse_stocks.shape[0]):
        # Skip symbols that endswith "-SG"
        if row['tradingsymbol'].endswith("-SG"):
            continue
        symbol = row['tradingsymbol'] + ".NS" #"RELIANCE.NS" 
        analysis_result = pattern_analysis(symbol)
        if analysis_result:
            data_list.append(analysis_result)

    # Create a pandas DataFrame from the data list
    data_df = pd.DataFrame(data_list, columns=['Symbol', 'Recognised Pattern Names', 'RSI Trend', 'MACD Trend', 'SMA', 'WMA', 'OBV'])

    # Export the DataFrame to a CSV file
    data_df.to_csv('analysis_data.csv', index=False)


if __name__ == "__main__":
    main()