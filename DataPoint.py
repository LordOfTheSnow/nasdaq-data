from datetime import datetime

class DataPoint (object):
    def __init__(self, symbol, date, price):
        self.symbol = symbol
        self.date = date
        self.price = price
