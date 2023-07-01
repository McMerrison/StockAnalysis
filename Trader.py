
import pandas as pd
import talib
import http.client
import json
import time
import datetime
import hmac
import hashlib
import base64
import requests
import smtplib
import yfinance as yf
from yahooquery import Ticker
import numpy as np



# BUY SIGNALS
def buy_signal_rsi(df, rsi_period=14, rsi_lower=30):
    df['rsi'] = talib.RSI(df['close'], timeperiod=rsi_period)
    df = df.dropna(subset=['rsi'])
    if (df.empty):
        return False
    buy_signal = df['rsi'].iloc[-1] < rsi_lower
    return buy_signal

def buy_signal_macd(df, fast_period=12, slow_period=26, signal_period=9):
    df['macd'], df['macd_signal'], df['macd_hist'] = talib.MACD(df['close'], fastperiod=fast_period, slowperiod=slow_period, signalperiod=signal_period)
    df = df.dropna(subset=['macd'])
    df = df.dropna(subset=['macd_signal'])
    df = df.dropna(subset=['macd_hist'])
    if (df.empty):
        return False
    buy_signal = df['macd'].iloc[-1] > df['macd_signal'].iloc[-1] and df['macd'].iloc[-2] <= df['macd_signal'].iloc[-2]
    return buy_signal

def buy_signal_bollinger_bands(df, bb_period=20, bb_std_dev=2):
    df['upper_band'], df['middle_band'], df['lower_band'] = talib.BBANDS(df['close'], timeperiod=bb_period, nbdevup=bb_std_dev, nbdevdn=bb_std_dev, matype=0)
    df = df.dropna(subset=['upper_band'])
    df = df.dropna(subset=['middle_band'])
    df = df.dropna(subset=['lower_band'])
    if (df.empty):
        return False
    buy_signal = df['close'].iloc[-1] < df['lower_band'].iloc[-1]
    return buy_signal


# SELL SIGNALS
def sell_signal_rsi(df, rsi_period=14, rsi_upper=70):
    df['rsi'] = talib.RSI(df['close'], timeperiod=rsi_period)
    df = df.dropna(subset=['rsi'])
    if (df.empty):
        return False
    sell_signal = df['rsi'].iloc[-1] > rsi_upper
    return sell_signal

def sell_signal_macd(df, fast_period=12, slow_period=26, signal_period=9):
    df['macd'], df['macd_signal'], df['macd_hist'] = talib.MACD(df['close'], fastperiod=fast_period, slowperiod=slow_period, signalperiod=signal_period)
    df = df.dropna(subset=['macd'])
    df = df.dropna(subset=['macd_signal'])
    df = df.dropna(subset=['macd_hist'])
    if (df.empty):
        return False
    sell_signal = df['macd'].iloc[-1] < df['macd_signal'].iloc[-1] and df['macd'].iloc[-2] >= df['macd_signal'].iloc[-2]
    return sell_signal

def sell_signal_bollinger_bands(df, bb_period=20, bb_std_dev=2):
    df['upper_band'], df['middle_band'], df['lower_band'] = talib.BBANDS(df['close'], timeperiod=bb_period, nbdevup=bb_std_dev, nbdevdn=bb_std_dev, matype=0)
    df = df.dropna(subset=['upper_band'])
    df = df.dropna(subset=['middle_band'])
    df = df.dropna(subset=['lower_band'])
    if (df.empty):
        return False
    sell_signal = df['close'].iloc[-1] > df['upper_band'].iloc[-1]
    return sell_signal

def send_email(subject, body, to_email, from_email, password):
    message = f"Subject: {subject}\n\n{body}"

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(from_email, password)
        server.sendmail(from_email, to_email, message)
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print("Error sending email:", e)
        

def fibonacci_bands(data, period=14):
    # Calculate the middle band (SMA)
    data['Middle_Band'] = data['close'].rolling(window=period).mean()

    # Calculate the high and low price difference
    high_low_diff = data['high'].rolling(window=period).max() - data['low'].rolling(window=period).min()

    # Calculate the Fibonacci ratios
    fibonacci_ratios = [0.236, 0.382, 0.5, 0.618, 0.786]

    # Calculate the Fibonacci Bands
    for ratio in fibonacci_ratios:
        data[f'Upper_Band_{ratio}'] = data['Middle_Band'] + high_low_diff * ratio
        data[f'Lower_Band_{ratio}'] = data['Middle_Band'] - high_low_diff * ratio

    return data
        


    

# Define parameters for candlestick data
#tickers = ['SPY', 'QQQ', 'AAPL', 'PTON', 'UBER', 'GOOG', 'DIS', 'NFLX', 'META', 'PYPL', 'CHGG']
#tickers = ["SPY"]
granularity = 3600     # 1 minute granularity
#granularity = 60 * 30  # 30 minute granularity
#granularity = 60 * 60  # 1H minute granularity
# num_periods = 1        # On hour
num_hours = 24 * 14  # One week
# num_periods = 1      # One day

# Start/End Times
current_time_unix = int(time.time())
#current_time_unix = i
time_1_hour_ago_unix = current_time_unix - (num_hours * 60 * 60)  # Subtract one week in seconds



tickers = [
    'AAPL', 'MSFT', 'AMZN', 'GOOGL', 'GOOG', 'FB', 'TSLA', 'BRK-B', 'NVDA', 'JPM',
    'JNJ', 'UNH', 'V', 'HD', 'PG', 'PYPL', 'MA', 'BAC', 'DIS', 'CMCSA',
    'ADBE', 'CRM', 'XOM', 'NFLX', 'PFE', 'VZ', 'ABT', 'T', 'AVGO', 'KO',
    'CVX', 'MRK', 'PEP', 'INTC', 'ACN', 'WMT', 'CSCO', 'LLY', 'MCD', 'TXN',
    'NEE', 'DHR', 'HON', 'PM', 'IBM', 'UNP', 'LIN', 'QCOM', 'ABBV', 'C',
    'COST', 'BMY', 'TMO', 'SBUX', 'AMGN', 'AMT', 'BA', 'MMM', 'MDT', 'GS',
    'LOW', 'ORCL', 'CHTR', 'LMT', 'CAT', 'RTX', 'BLK', 'CVS', 'GE', 'GILD',
    'TJX', 'AXP', 'FIS', 'ANTM', 'VRTX', 'ISRG', 'BKNG', 'CI', 'DUK', 'SYK',
    'ZTS', 'D', 'CME', 'SPGI', 'PLD', 'EOG', 'NOW', 'SCHW', 'MO', 'ADP', 'SPY',
    
]

#tickers = ['ABBV']


# TODO: EMAIL NOTIFICAITON OF SIGNAL


to_email = EMAIL  # Replace with your email address
from_email = EMAIL  # Replace with your email address
password = EMAIL_PASSWORD  


#while True:
#for i in range(time_1_hour_ago_unix, current_time_unix, granularity):
    
current_time_unix = int(time.time()+(5*60*60))
#current_time_unix = i
time_1_hour_ago_unix = current_time_unix - (num_hours * 60 * 60)  # Subtract one week in seconds

end = datetime.datetime.fromtimestamp(current_time_unix)
hour = end.strftime("%H")
hour = int(hour)
minute = end.strftime("%M")
minute = int(minute)

end = end.strftime('%Y-%m-%d %H:%M:%S')
start = datetime.datetime.fromtimestamp(time_1_hour_ago_unix)
start = start.strftime('%Y-%m-%d %H:%M:%S')

if hour >= 1 and minute >= 1:

    #print(start + " to " + end)
    
    print("TESTING TIME: " + str(datetime.datetime.fromtimestamp(current_time_unix-4*60*60)))
    
    body = ""
    subject = "Signals for " + str(datetime.datetime.fromtimestamp(current_time_unix))



    for t in tickers:
    
    
        
        print("TICKER: " + t)
        
        rsi_buy_signals = 0
        boll_buy_signals = 0
        macd_buy_signals = 0
        
        
        rsi_sell_signals = 0
        boll_sell_signals = 0
        macd_sell_signals = 0
        
        stock = Ticker(t)
        
        
        
        # get historical market data
        data = stock.history(interval="1h", start=start, end=end, adj_ohlc=True)
        
        if data.empty:
            continue
        
        
        # Convert candlestick data to Pandas DataFrame
        df = pd.DataFrame(data)
        #df.drop(df.tail(1).index,inplace=True) # drop last n rows
        df.drop(df.head(1).index,inplace=True) # drop last n rows
        #print(df)
        
        
        
        rsis = [7, 9, 14, 21, 25]
        
        # print("Testing RSIs...")
        for i in rsis:
            rsi_buy = buy_signal_rsi(df, i)
            if rsi_buy:
                rsi_buy_signals += 1
                #print("Buy signal for RSI period " + str(i) + f": {rsi_buy}")
            rsi_sell = sell_signal_rsi(df, i)
            if rsi_sell:
                rsi_sell_signals += 1
                #print("Sell signal for RSI period " + str(i) + f": {rsi_sell}")  
                
        
                
        settings = [[12, 26, 9], [8, 17, 9], [5, 34, 5], [21, 50, 9]]
        # print("Testing MACD...")
        for s in settings:
            macd_buy = buy_signal_macd(df, s[0], s[1], s[2])
            if macd_buy:
                macd_buy_signals += 1
                #print("Buy signal for settings " + str(s) + f": {macd_buy}")
            macd_sell = sell_signal_macd(df, s[0], s[1], s[2])
            if macd_sell:
                macd_sell_signals += 1
                #print("Sell signal for settings " + str(i) + f": {macd_sell}")
                
        
        bb = [20, 10, 50]
        
        # print("Testing BBs...")
        for b in bb:
            bollinger_bands_buy = buy_signal_bollinger_bands(df, b)
            if bollinger_bands_buy:
                boll_buy_signals += 1
                #print("Buy signal for BB period " + str(b) + f": {bollinger_bands_buy}")
            bollinger_bands_sell = sell_signal_bollinger_bands(df, b)
            if bollinger_bands_sell:
                boll_sell_signals += 1
                #print("Sell signal for BB period " + str(i) + f": {bollinger_bands_sell}")
                
                
        thold = 3
        buy_signals = rsi_buy_signals + macd_buy_signals + boll_buy_signals
        sell_signals = rsi_sell_signals + macd_sell_signals + boll_sell_signals
        
        if (rsi_buy_signals > 0 and macd_buy_signals > 0 and boll_buy_signals > 0):
            body += "Buy signals: " + str(buy_signals) + "\nSell signals: " + str(sell_signals) + "\n\n"
            print("STRONG BUY SIGNAL!")
            print("RSI buy signals: " + str(rsi_buy_signals))
            print("MACD buy signals: " + str(macd_buy_signals))
            print("Boll buy signals: " + str(boll_buy_signals))
        #else:
            #print("No strong buy signals.")
        if (rsi_sell_signals > 0 and macd_sell_signals > 0 and boll_sell_signals > 0):
            body += "Buy signals: " + str(buy_signals) + "\nSell signals: " + str(sell_signals) + "\n\n"
            print("STRONG SELL SIGNAL!")
            print("RSI sell signals: " + str(rsi_sell_signals))
            print("MACD sell signals: " + str(macd_sell_signals))
            print("Boll sell signals: " + str(boll_sell_signals))
            
            #else:
                #print("No strong sell signals")
    #send_email(subject, body, to_email, from_email, password) 
        
    
    #print("Testing again in 1 hour...") 
    #time.sleep(granularity)
    
else:
    print("Try again during market hours!")
                    
            
    
    


