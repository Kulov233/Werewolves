# filename: fetch_ytd_gains.py
import yfinance as yf
import datetime

# Get the current date
current_date = datetime.date.today()

# Define the start of the year
start_of_year = datetime.date(current_date.year, 1, 1)

# Fetch data for META and TESLA
meta = yf.Ticker("META")
tesla = yf.Ticker("TSLA")

# Get historical market data
meta_history = meta.history(start=start_of_year, end=current_date)
tesla_history = tesla.history(start=start_of_year, end=current_date)

# Calculate YTD gains
meta_ytd_gain = (meta_history['Close'][-1] - meta_history['Close'][0]) / meta_history['Close'][0] * 100
tesla_ytd_gain = (tesla_history['Close'][-1] - tesla_history['Close'][0]) / tesla_history['Close'][0] * 100

print(f"YTD gain for META: {meta_ytd_gain:.2f}%")
print(f"YTD gain for TESLA: {tesla_ytd_gain:.2f}%")