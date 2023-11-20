from yahoo_fin import stock_info as si
import time
import mysql.connector

conn = mysql.connector.connect(
        user="root",
        password="###",
        host="127.0.0.1",
        database="stock_project",
    )

def my_periodic_function(stock_symbols):
    cur=conn.cursor()
    for symbol in stock_symbols:
        price = si.get_live_price(symbol)
        price=round(price,4)
        print(price)
        cur.execute("UPDATE stocks SET price = %s WHERE stock_id = %s", (price, symbol))

    conn.commit()
    




interval_seconds = 10 
stock_symbols = ["GOOG", "IDEA", "AAPL", "AMZN", "LMT", "NVDA", "ADANIPORTS.NS", "PAC", "ZS","CRSP","GLOB","GPS"]
while True:
    my_periodic_function(stock_symbols)
    time.sleep(interval_seconds)