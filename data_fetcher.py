import yfinance as yf

def fetch_ticker_data(ticker: str, period: str):
    """
    Obtiene los datos históricos de un ticker.
    
    Args:
        ticker (str): Símbolo de la acción (e.g., "AAPL").
        period (str): El periodo de tiempo para los datos históricos (e.g., "1y").
    
    Returns:
        tuple: (datos históricos, información general del ticker)
    """
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(period=period)
        info = stock.info
        return data, info
    except Exception as e:
        print(f"Error al obtener datos para {ticker}: {e}")
        return None, None


def format_large_numbers(value):
    """
    Formatea números grandes (mayores a 1,000) en un formato legible (K, M, B).
    
    Args:
        value (float or int): El valor numérico a formatear.
    
    Returns:
        str: El valor formateado en una cadena legible.
    """
    if value is None:
        return "Dato no disponible"
    
    try:
        value = float(value)
        
        if value >= 1_000_000_000:  # Billones
            return f"{value / 1_000_000_000:.1f}B"
        elif value >= 1_000_000:  # Millones
            return f"{value / 1_000_000:.1f}M"
        elif value >= 1_000:  # Miles
            return f"{value / 1_000:.1f}K"
        else:
            return f"{value:.2f}"
    except ValueError:
        return "Dato no disponible"


def fetch_fundamental_data(ticker: str):
    """
    Obtiene los datos fundamentales para un ticker, incluyendo métricas clave de Peter Lynch.
    
    Args:
        ticker (str): Símbolo de la acción (e.g., "AAPL").
    
    Returns:
        dict: Métricas clave para el análisis fundamental.
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Función auxiliar para manejar el acceso a datos que pueden no estar disponibles
        def safe_get(data, field, default="Dato no disponible"):
            return data.get(field, default) if field in data else default
        
        dividend_yield = safe_get(info, "dividendYield")
        if dividend_yield != "Dato no disponible" and dividend_yield is not None:
            dividend_yield = dividend_yield * 100  # Convertir a porcentaje
        
        # Métricas fundamentales
        fundamental_data = {
            "P/E Ratio": safe_get(info, "trailingPE"),
            "P/B Ratio": safe_get(info, "priceToBook"),
            "Dividend Yield": f"{dividend_yield}%" if dividend_yield != "Dato no disponible" else "Dato no disponible",
            "ROE": safe_get(info, "returnOnEquity"),
            "Debt to Equity": safe_get(info, "debtToEquity"),
            "Beta": safe_get(info, "beta"),
            "Revenue Growth": safe_get(info, "revenueGrowth"),
            "Free Cash Flow": format_large_numbers(safe_get(info, "freeCashflow")),
            "Total Debt": format_large_numbers(safe_get(info, "totalDebt")),
            "Long-Term Debt": format_large_numbers(safe_get(info, "longTermDebt")),
            "Operating Income": format_large_numbers(safe_get(info, "operatingIncome")),
            "Net Income": format_large_numbers(safe_get(info, "netIncomeToCommon")),
            "EPS Growth (5Y)": safe_get(info, "earningsQuarterlyGrowth"),
            "EPS Growth (Next 5Y)": safe_get(info, "earningsGrowth"),
        }

        # Comparar deuda de años anteriores, si la información está disponible
        debt_comparison = {
            "Deuda Anterior": format_large_numbers(safe_get(info, "debtToEquity")),
        }
        
        # Añadir crecimiento de la deuda si los datos son accesibles
        if safe_get(info, "totalDebt", None) and safe_get(info, "debtToEquity", None):
            debt_comparison["Cambio Deuda"] = format_large_numbers(float(safe_get(info, "totalDebt", 0)) / float(safe_get(info, "debtToEquity", 1)))

        fundamental_data["Debt Comparison"] = debt_comparison
        
        return fundamental_data
    except Exception as e:
        print(f"Error al obtener datos fundamentales para {ticker}: {e}")
        return {}


def fetch_debt_comparison(ticker: str):
    """
    Obtiene y compara la deuda de una empresa entre el año actual y el anterior.
    
    Args:
        ticker (str): Símbolo de la acción (e.g., "AAPL").
    
    Returns:
        dict: Comparación de deuda entre los dos años.
    """
    try:
        stock = yf.Ticker(ticker)
        financials = stock.financials
        balance_sheet = stock.balance_sheet
        
        # Obtener datos de deuda total
        total_debt = balance_sheet.loc['Total Debt'] if 'Total Debt' in balance_sheet.index else None
        long_term_debt = balance_sheet.loc['Long Term Debt'] if 'Long Term Debt' in balance_sheet.index else None
        
        # Asegúrate de usar iloc para obtener las posiciones
        debt_last_year = total_debt.iloc[1] if total_debt is not None else None
        debt_this_year = total_debt.iloc[0] if total_debt is not None else None
        
        # Si tenemos deuda a largo plazo, usaremos esos valores
        long_term_debt_last_year = long_term_debt.iloc[1] if long_term_debt is not None else None
        long_term_debt_this_year = long_term_debt.iloc[0] if long_term_debt is not None else None
        
        # Comparar las deudas
        debt_comparison = {}
        if debt_last_year and debt_this_year:
            debt_comparison["Total Debt Last Year"] = format_large_numbers(debt_last_year)
            debt_comparison["Total Debt This Year"] = format_large_numbers(debt_this_year)
            debt_comparison["Debt Change"] = calculate_debt_change(debt_last_year, debt_this_year)
        
        if long_term_debt_last_year and long_term_debt_this_year:
            debt_comparison["Long Term Debt Last Year"] = format_large_numbers(long_term_debt_last_year)
            debt_comparison["Long Term Debt This Year"] = format_large_numbers(long_term_debt_this_year)
            debt_comparison["Long Term Debt Change"] = calculate_debt_change(long_term_debt_last_year, long_term_debt_this_year)
        
        return debt_comparison

    except Exception as e:
        print(f"Error al obtener la comparación de deuda para {ticker}: {e}")
        return {}


def calculate_debt_change(last_year_debt, this_year_debt):
    """
    Calcula el cambio en la deuda entre dos años.
    
    Args:
        last_year_debt (float): Deuda del año anterior.
        this_year_debt (float): Deuda del año actual.
    
    Returns:
        str: Indicador de si la deuda ha aumentado o disminuido, con el valor.
    """
    try:
        debt_change = this_year_debt - last_year_debt
        if debt_change > 0:
            return f"Aumento de {format_large_numbers(debt_change)}"
        elif debt_change < 0:
            return f"Disminución de {format_large_numbers(abs(debt_change))}"
        else:
            return "Sin cambio"
    except Exception as e:
        return f"Error en el cálculo: {e}"

