from dotenv import load_dotenv
import os
from binance.client import Client
from binance.exceptions import BinanceAPIException


class BBot:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, "initialized"):
            return

        load_dotenv()

        api_key = os.getenv("API_KEY")
        api_secret = os.getenv("API_SECRET")

        # Binance Testnet
        self.client = Client(api_key, api_secret, testnet=True)

        # Sync time
        self.client.get_server_time()

        self.initialized = True


    # ==============================
    # 📊 Market Data
    # ==============================
    def get_price(self, symbol):
        try:
            price = self.client.get_symbol_ticker(symbol=symbol)
            return float(price['price'])
        except BinanceAPIException as err:
            print(f"Error: {err}")
            return None


    def get_klines(self, symbol, interval="1m", limit=20):
        try:
            klines = self.client.get_klines(symbol=symbol, interval=interval, limit=limit)
            return [float(k[4]) for k in klines]
        except Exception as e:
            print(f"Error fetching klines: {e}")
            return []


    # ==============================
    # 📈 Analysis
    # ==============================
    def moving_average(self, prices):
        if not prices:
            return None
        return sum(prices) / len(prices)


    def analyze(self, symbol):
        prices = self.get_klines(symbol)

        if not prices:
            return

        current_price = prices[-1]
        avg_price = self.moving_average(prices)

        print(f"{symbol} Current: {current_price}")
        print(f"{symbol} Avg: {avg_price}")

        if current_price > avg_price:
            print(f"{symbol} → UP Trend 📈")
        else:
            print(f"{symbol} → DOWN Trend 📉")


    # ==============================
    # 💰 Wallet
    # ==============================
    def get_balance(self, asset):
        try:
            balance = self.client.get_asset_balance(asset=asset)
            return float(balance['free'])
        except Exception as e:
            print("Balance error:", e)
            return 0


    # ==============================
    # 💰 Orders
    # ==============================
    def place_buy_order(self, symbol, quantity):
        try:
            quantity = round(quantity, 3)

            order = self.client.order_market_buy(
                symbol=symbol,
                quantity=quantity,
                recvWindow=10000
            )

            print("✅ BUY Order:", order)
            return order

        except BinanceAPIException as e:
            print("❌ Binance Buy Error:", e.message)

        except Exception as e:
            print("❌ Buy Error:", e)

        return None


    def place_sell_order(self, symbol, quantity):
        try:
            quantity = round(quantity, 3)

            order = self.client.order_market_sell(
                symbol=symbol,
                quantity=quantity,
                recvWindow=10000
            )

            print("✅ SELL Order:", order)
            return order

        except BinanceAPIException as e:
            print("❌ Binance Sell Error:", e.message)

        except Exception as e:
            print("❌ Sell Error:", e)

        return None


    # ==============================
    # 🤖 Interactive Trade
    # ==============================
    def trade(self):

        symbol = input("Enter symbol (e.g. BTCUSDT): ").upper()
        buy_price = float(input("Enter BUY price: "))
        sell_price = float(input("Enter SELL price: "))
        quantity = float(input("Enter quantity: "))

        price = self.get_price(symbol)

        if price is None:
            return

        print(f"{symbol} Current Price: {price}")

        asset = symbol.replace("USDT", "")
        balance = self.get_balance(asset)

        if price <= buy_price:
            print("📉 BUY Condition Met")
            self.place_buy_order(symbol, quantity)

        elif price >= sell_price:

            if balance < quantity:
                print("❌ Not enough balance to sell")
                return

            print("📈 SELL Condition Met")
            self.place_sell_order(symbol, quantity)

        else:
            print("⏳ No trade condition met")


# ==============================
# Run Bot
# ==============================
