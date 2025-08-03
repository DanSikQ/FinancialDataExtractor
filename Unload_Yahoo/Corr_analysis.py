import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def analyze_data(prices_file):

    prices = pd.read_csv(prices_file, parse_dates=['Date'])

    # Расчет дневных изменений
    prices['Price_Change'] = prices.groupby('Ticker')['Close'].pct_change()
    prices['Volume_Change'] = prices.groupby('Ticker')['Volume'].pct_change()
    prices['Intraday_Range'] = (prices['High'] - prices['Low']) / prices['Open']

    # Корреляция между изменением цены и объемом
    corr = prices.groupby(['Ticker', 'Company'])[['Price_Change', 'Volume_Change', 'Intraday_Range']].corr().unstack()
    corr_df = corr.loc[:, ('Price_Change', ['Volume_Change', 'Intraday_Range'])]
    corr_df.columns = ['Price-Volume_Corr', 'Price-Intraday_Corr']

    print("\nСредняя корреляция по всем акциям:")
    print(corr_df.mean())

    corr_price_volume = prices['Price_Change'].corr(prices['Volume_Change'])
    corr_intraday_volume = prices['Intraday_Range'].corr(prices['Volume_Change'])

    plt.figure(figsize=(14, 6))

    plt.subplot(1, 2, 1)
    sns.regplot(data=prices, x='Volume_Change', y='Price_Change', line_kws={'color': 'red'})
    plt.title(f'Изменение цены vs Изменение объема\n(Корреляция: {corr_price_volume:.2f})')
    plt.xlabel('Изменение объема (%)')
    plt.ylabel('Изменение цены (%)')

    plt.subplot(1, 2, 2)
    sns.regplot(data=prices, x='Intraday_Range', y='Volume_Change', line_kws={'color': 'red'})
    plt.title(f'Внутридневной диапазон vs Изменение объема\n(корреляция: {corr_intraday_volume:.2f})')
    plt.xlabel('Внутридневной диапазон (% от открытия)')
    plt.ylabel('Изменение объема (%)')

    plt.tight_layout()
    plt.savefig('graph/price_volume_analysis.png')
    plt.show()

analyze_data('data/stock_prices.csv')