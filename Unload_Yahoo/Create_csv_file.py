import pandas as pd

# Создаем список акций для анализа
stocks = {
    'Ticker': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA', 'NVDA', 'JPM', 'JNJ', 'WMT',
               'PG', 'DIS', 'NFLX'],
    'Company': ['Apple', 'Microsoft', 'Alphabet', 'Amazon', 'Meta', 'Tesla', 'NVIDIA',
                'JPMorgan Chase', 'Johnson & Johnson', 'Walmart', 'Procter & Gamble',
                'Disney', 'Netflix']
}

# Создаем DataFrame и сохраняем в CSV
df = pd.DataFrame(stocks)
df.to_csv('data/stock_list.csv', index=False)

print("Файл stock_list.csv успешно создан с следующими акциями:")
print(df)

