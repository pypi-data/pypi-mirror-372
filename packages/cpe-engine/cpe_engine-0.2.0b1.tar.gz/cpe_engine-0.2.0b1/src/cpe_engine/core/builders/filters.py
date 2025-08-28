"""Filtros esenciales para templates Jinja2 (equivalentes a Greenter)."""

from datetime import datetime
from typing import Union

# Import para funciones de tributo (equivalente a TributoFunction.php de Greenter)
from ..services.tributo_function import get_tributo_by_afectacion, get_tributo_by_code


def format_date(value: Union[datetime, str], format_str: str = "%Y-%m-%d") -> str:
    """
    Formatea fecha para XML (equivalente a |date('Y-m-d') de Greenter).
    
    Args:
        value: Fecha a formatear
        format_str: Formato de salida
        
    Returns:
        Fecha formateada como string
    """
    if isinstance(value, str):
        return value
        
    if isinstance(value, datetime):
        return value.strftime(format_str)
        
    return ""


def format_time(value: Union[datetime, str], format_str: str = "%H:%M:%S") -> str:
    """
    Formatea hora para XML (equivalente a |date('H:i:s') de Greenter).
    
    Args:
        value: Fecha/hora a formatear
        format_str: Formato de salida
        
    Returns:
        Hora formateada como string
    """
    if isinstance(value, str):
        return value
        
    if isinstance(value, datetime):
        return value.strftime(format_str)
        
    return ""


def format_decimal(value: Union[float, int, str], decimals: int = 2) -> str:
    """
    Formatea número decimal para XML (siempre con punto decimal).
    
    Args:
        value: Número a formatear
        decimals: Cantidad de decimales
        
    Returns:
        Número formateado como string
    """
    if value is None:
        return "0.00"
        
    try:
        num = float(value)
        return f"{num:.{decimals}f}"
    except (ValueError, TypeError):
        return "0.00"


# Diccionario de filtros esenciales (solo equivalentes a Greenter)
CUSTOM_FILTERS = {
    'format_date': format_date,
    'format_time': format_time,  
    'format_decimal': format_decimal,
    # Filtros para tributos (equivalentes a getTributoAfect de Greenter)
    'get_tributo_afect': get_tributo_by_afectacion,
    'get_tributo_code': get_tributo_by_code,
}