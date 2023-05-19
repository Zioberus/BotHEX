from binance.client import Client
from binance.enums import *
#łączenie z serwerem api
api_key ='YOUR_ API_KEY'
api_secret = 'YOUR_API_SECRET"
import time
from binance.client import Client
symbol = 'BTCUSDT'
quantity = 0.004
leverage = 50


client = Client(api_key, api_secret)



def place_futures_order(side, order_type, quantity, stop_price=None):
    try:
        order = client.futures_create_order(
            symbol=symbol,
            side=side,
            type=order_type,
            quantity=quantity,
            stopPrice=stop_price,
            leverage=leverage
        )
        print(f"Zlecenie {order_type} {side} na {symbol} z dźwignią {leverage} dodane pomyślnie.")
        return order
    except Exception as e:
        print("Wystąpił błąd podczas dodawania zlecenia: {}".format(str(e)))
        return None


def get_current_price():
    try:
        ticker = client.futures_ticker(symbol=symbol)
        return float(ticker['lastPrice'])
    except Exception as e:
        print("Wystąpił błąd podczas pobierania ceny: {}".format(str(e)))
        return None


def monitor_trade():
    global entry_price
    place_futures_order('BUY', 'MARKET', quantity)
    entry_price = get_current_price()
    wielkosc_pozycji = 0.004
    wartosc_pozycji = wielkosc_pozycji*entry_price
    srednia_cena = wartosc_pozycji/wielkosc_pozycji
    take_profit_price = entry_price + (entry_price * 0.01)
    print("cena wejscia", entry_price)
    while True:
        current_price = get_current_price()
        print("wielkosc pozycji: ", wielkosc_pozycji,"Obcena cena BTC w USDT: ",round(current_price),"Cena następnego BUY zlecenia",entry_price-150, "Cena następnego SELL zlecenia",take_profit_price, "Wymagany spadek do BUY LUB SELL: ", round(current_price-entry_price-150),round((take_profit_price-current_price)), "Średnia cena wejśćia; ",srednia_cena, "wartosc pozycji: ", wartosc_pozycji/leverage)
        if current_price <= (entry_price - 150):
            entry_price = current_price
            place_futures_order('BUY', 'MARKET', quantity)
            print("Otworzono pozycję kupna.")
            wielkosc_pozycji = wielkosc_pozycji + quantity
            wartosc_pozycji = wartosc_pozycji + quantity*current_price
            srednia_cena = wielkosc_pozycji/wartosc_pozycji
            take_profit_price = entry_price + (entry_price * 0.33)
            entry_price = entry_price - 150
            print("cena wejscia",entry_price)
        if current_price >= take_profit_price:
            close_quantity = quantity/2
            place_futures_order('SELL', 'MARKET', close_quantity)
            wartosc_pozycji = wartosc_pozycji - (close_quantity*current_price)
            wielkosc_pozycji = wielkosc_pozycji-close_quantity
            srednia_cena = wartosc_pozycji/wielkosc_pozycji
            entry_price=current_price-150
            print("Zamknięto pozycję sprzedaży w wysokosci: ", close_quantity, "za cene: ", get_current_price())


        time.sleep(3)  # Czekaj 3 sekund przed kolejnym sprawdzeniem ceny


def get_entry_price():
    candles = client.futures_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_1MINUTE, limit=2)
monitor_trade()
