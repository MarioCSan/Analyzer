from data_fetcher import fetch_ticker_data, fetch_fundamental_data, fetch_debt_comparison
from exchange_mapping import EXCHANGE_MAPPING

def main():
    print("=== Análisis de Tickers ===")
    ticker = input("Introduce el ticker de la empresa (e.g., AAPL): ").strip().upper()
    period = input("Introduce el periodo de análisis (por defecto: 1y): ").strip() or "1y"
    
    print(f"Obteniendo datos para {ticker}...")
    data, info = fetch_ticker_data(ticker, period)
    
    if data is not None and info is not None:
        # Obtener el nombre del mercado
        market_code = info.get('exchange', 'N/D')
        market_name = EXCHANGE_MAPPING.get(market_code, market_code)
        
        # Mostrar información básica del ticker
        print(f"\n=== Información del Ticker ===")
        print(f"Símbolo: ${info.get('symbol', 'N/D')}")
        print(f"Nombre: {info.get('longName', 'N/D')}")
        print(f"Mercado: {market_name}")
        print(f"Sector: {info.get('sector', 'N/D')}")
        print(f"Industria: {info.get('industry', 'N/D')}")
        print(f"País: {info.get('country', 'N/D')}")
        print(f"Divisa: {info.get('currency', 'N/D')}")

        # Mostrar últimas filas de datos históricos
        print("\n=== Últimos Datos Históricos ===")
        print(data.tail())  # Mostrar las últimas 5 filas como prueba.

        # Obtener y mostrar datos fundamentales
        print("\n=== Análisis Fundamental ===")
        fundamental_data = fetch_fundamental_data(ticker)
        for key, value in fundamental_data.items():
            print(f"{key}: {value}")

        # Obtener y mostrar la comparación de deuda
        print("\n=== Comparación de Deuda ===")
        debt_comparison = fetch_debt_comparison(ticker)
        if debt_comparison:
            for key, value in debt_comparison.items():
                print(f"{key}: {value}")

    else:
        print("No se pudieron obtener datos para el ticker especificado. Verifica el símbolo e intenta de nuevo.")

if __name__ == "__main__":
    main()
