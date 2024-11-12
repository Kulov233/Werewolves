# filename: get_current_date.py
import datetime

current_date = datetime.datetime.now()
print("Today's date is:", current_date.strftime("%Y-%m-%d"))