import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import time

def fetch_with_delay(ticker, start_date, end_date, delay=0.5):
    time.sleep(delay)  # Задержка между запросами
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(start=start_date, end=end_date)

        info = stock.info
        metrics = {
            'PE': info.get('trailingPE', None),
            'PB': info.get('priceToBook', None),
            'EPS': info.get('trailingEps', None),
            'MarketCap': info.get('marketCap', None),
            'DividendYield': info.get('dividendYield', None),
            'Sector': info.get('sector', None),
            'Industry': info.get('industry', None)
        }

        return hist, metrics
    except Exception as e:
        print(f"Ошибка при получении данных для {ticker}: {e}")
        return None, None

# Основная функция
def main():

    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)  # Данные за последний год

    # Загрузка списка акций
    stocks = pd.read_csv('data/stock_list.csv')

    # Создание DataFrame для хранения всех данных
    all_data = pd.DataFrame()
    metrics_data = []

    # Получение данных для каждой акции
    for _, row in stocks.iterrows():
        ticker = row['Ticker']
        print(f"Получаем данные для {ticker} ({row['Company']})...")

        data, metrics = fetch_with_delay(ticker, start_date, end_date)

        # Добавляем идентификаторы
        data['Ticker'] = ticker
        data['Company'] = row['Company']
        data.reset_index(inplace=True)
        # Добавляем данные в общий DataFrame
        all_data = pd.concat([all_data, data], ignore_index=True)
        # Добавляем метрики
        metrics.update({
            'Ticker': ticker,
            'Company': row['Company']
        })
        metrics_data.append(metrics)

    # Сохранение данных
    if not all_data.empty:
        all_data.to_csv('data/stock_prices.csv', index=False, encoding='utf-8')
        print("Данные по ценам сохранены в stock_prices.csv")

    if metrics_data:
        pd.DataFrame(metrics_data).to_csv('data/financial_metrics.csv', index=False)
        print("Финансовые показатели сохранены в financial_metrics.csv")

if __name__ == "__main__":
    main()