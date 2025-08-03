import requests
import pandas as pd
import matplotlib.pyplot as plt
import talib
import numpy as np
from matplotlib import gridspec

# Выгрузка данных будет проводиться из сайта Binance. Для получения основных данных о криптовалюты,
# я воспользуюсь открытым API и выгружу данные в виде "свечей".

# Klines ("свечные данные") — это формат представления ценовых данных на финансовых рынках, включая криптовалюты.

# Примеры криптовалют, для анализа
# - BTCUSD - Bitcoin к доллару
# - ETHUSD - Ethereum к доллару
# - LTCUSD - Litecoin к доллару
# - XRPUSD - Ripple к доллару
# - ADAUSD - Cardano к доллару


# Функция для загрузки данных с Binance API
def get_binance_data(symbol, interval, start_time, end_time):
    url = "https://api.binance.com/api/v3/klines"
    start_timestamp = int(pd.Timestamp(start_time).timestamp() * 1000)
    end_timestamp = int(pd.Timestamp(end_time).timestamp() * 1000)

    params = {
        'symbol': symbol,
        'interval': interval,
        'limit': 1000,
        'startTime': start_timestamp,
        'endTime': end_timestamp
    }

    data = requests.get(url, params=params).json()

    df = pd.DataFrame(data, columns=[
        'Open time', 'Open', 'High', 'Low', 'Close', 'Volume',
        'Close time', 'Quote asset volume', 'Number of trades',
        'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore'
    ])

    df['Open time'] = pd.to_datetime(df['Open time'], unit='ms')
    df['Close time'] = pd.to_datetime(df['Close time'], unit='ms')
    numeric_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, axis=1)
    df['Symbol'] = symbol

    return df[['Symbol','Open time', 'Open', 'High', 'Low', 'Close', 'Volume']].rename(columns={'Open time': 'Date'})


# Функция для добавления индикаторов
def add_indicators(df):

    # MACD (Схождение-Расхождение Скользящих Средних) — это трендовый индикатор, который показывает взаимосвязь между двумя скользящими средними цены.
    # SMA - скользящее среднее, просто среднее за определённый период (если SMA5, то за период в 5 дней берётся среднее цена криптовалюты и делится на 5)

    macd, macdsignal, macdhist = talib.MACD(df['Close'], fastperiod=12, slowperiod=26, signalperiod=9)
    df['MACD'] = macd
    df['MACD_Signal'] = macdsignal
    df['MACD_Hist'] = macdhist # Разница MACD - SIGNAL

    # MACD > Signal → Бычий сигнал(покупка)
    # MACD < Signal → Медвежий сигнал(продажа)

    #Бычий и медвежий сигналы — это сигналы, указывающие на направление тренда: восходящий (бычий) или нисходящий (медвежий)


    # Awesome Oscillator (AO) — это осциллятор, который измеряет рыночный импульс, сравнивая краткосрочную и долгосрочную динамику цены.
    # Цвет столбцов:
    # Зеленый(AO > 0) — бычий импульс.
    # Красный(AO < 0) — медвежий импульс.

    df['AO'] = talib.SMA(df['Close'], timeperiod=5) - talib.SMA(df['Close'], timeperiod=34)

    # Acceleration/Deceleration (AC) — это осциллятор, измеряющий ускорение или замедление текущей рыночной силы (импульса) перед изменением цены.

    # Положительные значения (зеленые столбцы): Ускоряющийся восходящий импульс.
    # Отрицательные значения (красные столбцы): Ускоряющийся нисходящий импульс.
    # Нулевая линия: Смена тренда или замедление движения.
    median_price = (df['High'] + df['Low']) / 2
    ao = talib.SMA(median_price, 5) - talib.SMA(median_price, 34)
    df['AC'] = ao - talib.SMA(ao, 5)

    return df


# Функция для визуализации данных
def visualize_data(df, symbol):
    fig = plt.figure(figsize=(10, 8))
    gs = gridspec.GridSpec(4, 1, height_ratios=[3, 3, 2, 2])

    # График цен
    ax0 = plt.subplot(gs[0])
    ax0.plot(df['Date'], df['Close'], label='Close Price', linewidth=2)
    ax0.set_title(f'{symbol} Price and Indicators')
    ax0.set_ylabel('Price')
    ax0.grid(True)
    ax0.legend()

    # MACD
    ax1 = plt.subplot(gs[1])
    ax1.plot(df['Date'], df['MACD'], label='MACD', color='blue')
    ax1.plot(df['Date'], df['MACD_Signal'], label='Signal', color='orange')
    ax1.bar(df['Date'], df['MACD_Hist'], label='Histogram', color=np.where(df['MACD_Hist'] > 0, 'g', 'r'))
    ax1.set_ylabel('MACD')
    ax1.grid(True)
    ax1.legend()

    # Awesome Oscillator
    ax2 = plt.subplot(gs[2])
    ax2.bar(df['Date'], df['AO'], label='AO', color=np.where(df['AO'] > 0, 'g', 'r'))
    ax2.set_ylabel('AO')
    ax2.grid(True)


    # Acceleration/Deceleration
    ax3 = plt.subplot(gs[3])
    ax3.bar(df['Date'], df['AC'], label='AC', color=np.where(df['AC'] > 0, 'g', 'r'))
    ax3.set_ylabel('AC')
    ax3.grid(True)


    plt.tight_layout()
    plt.savefig(f'graph_crypto/{symbol}_analysis.png')
    plt.close()


def main():
    start_date = '2025-01-01'
    end_date = '2025-06-01'
    interval = '1d'

    try:
        symbols_df = pd.read_csv('crypto_symbols.csv')
        symbols = symbols_df['Symbol'].tolist()
    except FileNotFoundError:
        symbols = ['BTCUSDT', 'ETHUSDT', 'LTCUSDT', 'XRPUSDT', 'ADAUSDT']
        pd.DataFrame({'Symbol': symbols}).to_csv('crypto_symbols.csv', index=False)
        print("Создан пример файла crypto_symbols.csv с символами по умолчанию")

    # Создаем пустой DataFrame для объединенных данных
    all_data = pd.DataFrame()

    print(f'Анализ за временной промежуток от {start_date} до {end_date}')

    for symbol in symbols:
        try:
            df = get_binance_data(symbol, interval, start_date, end_date)
            df = add_indicators(df)

            all_data = pd.concat([all_data, df], ignore_index=True)

            visualize_data(df, symbol)

            print(f"\nАнализ для {symbol}:")
            print(f"Средняя цена за период: {df['Close'].mean():.2f}")
            print(f"Максимальная цена: {df['Close'].max():.2f}")
            print(f"Минимальная цена: {df['Close'].min():.2f}")

        except Exception as e:
            print(f"Ошибка при обработке {symbol}: {str(e)}")

    # Сохраняем все данные в один файл
    all_data.to_csv('data_about_crypto/all_crypto_data.csv', index=False)

    print("\nОбработка завершена. Все данные сохранены в all_crypto_data.csv")

if __name__ == "__main__":
    main()