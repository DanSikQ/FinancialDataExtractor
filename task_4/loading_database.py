import os
import psycopg2
import pandas as pd

DB_CONFIG = {
    'host': 'localhost',
    'port': '5433',
    'database': 'postgres',
    'user': 'postgres',
    'password': '123'
}


def create_tables(conn):
    """Создание таблиц в БД"""
    with conn.cursor() as cursor:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS stock_data (
            date DATE, open NUMERIC(10, 2), high NUMERIC(10, 2),
            low NUMERIC(10, 2), close NUMERIC(10, 2), volume NUMERIC(10,2),
            dividends NUMERIC(10, 2), stock_splits NUMERIC(10, 2),
            ticker VARCHAR(10), company VARCHAR(100)
        )""")

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS financial_metrics (
            pe NUMERIC(10, 2), pb NUMERIC(10, 2), eps NUMERIC(10, 2),
            market_cap NUMERIC(20, 2), dividend_yield NUMERIC(10, 2),
            sector VARCHAR(100), industry VARCHAR(100),
            ticker VARCHAR(10), company VARCHAR(100)
        )""")

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS all_crypto_data (
            symbol VARCHAR(20), date DATE, open NUMERIC(20, 8),
            high NUMERIC(20, 8), low NUMERIC(20, 8), close NUMERIC(20, 8),
            volume NUMERIC(20, 2), macd NUMERIC(20, 8), macd_signal NUMERIC(20, 8),
            macd_hist NUMERIC(20, 8), ao NUMERIC(20, 8), ac NUMERIC(20, 8)
        )""")
        conn.commit()


def get_data_path(filename):
    """Формирование пути к файлу данных"""
    current_dir = os.getcwd()
    project_root = os.path.dirname(current_dir)
    if 'crypto' in filename.lower():
        return os.path.join(project_root, 'task_1', 'data_about_crypto', filename)
    return os.path.join(project_root, 'task_2', 'data', filename)


def load_data_to_db(conn, table_name, file_path):
    """Универсальная функция загрузки данных в БД"""
    df = pd.read_csv(get_data_path(file_path))
    df.columns = df.columns.str.lower().str.replace(' ', '_')

    numeric_cols = df.select_dtypes(include=['float64']).columns
    df[numeric_cols] = df[numeric_cols].round(8 if 'crypto' in file_path.lower() else 2)
    df = df.where(pd.notnull(df), None)

    if 'financial_metrics' in table_name:
        df = df.rename(columns={
            'marketcap': 'market_cap',
            'dividendyield': 'dividend_yield'
        })

    # Формирование SQL запроса
    columns = ', '.join(df.columns)
    placeholders = ', '.join(['%s'] * len(df.columns))

    with conn.cursor() as cursor:
        for _, row in df.iterrows():
            cursor.execute(
                f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})",
                tuple(row)
            )
        conn.commit()


def main():
    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            create_tables(conn)

            # Загрузка данных
            load_data_to_db(conn, 'stock_data', 'stock_prices.csv')
            load_data_to_db(conn, 'financial_metrics', 'financial_metrics.csv')
            load_data_to_db(conn, 'all_crypto_data', 'all_crypto_data.csv')

            print("Все данные успешно загружены в БД")

    except Exception as e:
        print(f"Ошибка: {e}")


if __name__ == "__main__":
    main()