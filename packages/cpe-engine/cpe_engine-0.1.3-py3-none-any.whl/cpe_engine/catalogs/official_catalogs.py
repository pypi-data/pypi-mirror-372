"""Catálogos oficiales de SUNAT para validación.

Carga y procesa los catálogos oficiales descargados desde:
https://github.com/EliuTimana/SunatCatalogos

Estos catálogos son la fuente oficial para validación en el DocumentValidator.
"""

import json
from pathlib import Path
from typing import Dict, Set, List, Optional

# Ruta a los catálogos oficiales
CATALOGS_DIR = Path(__file__).parent / "sunat_official"


def load_catalog(catalog_number: str) -> List[Dict[str, str]]:
    """Carga un catálogo específico desde archivo JSON.
    
    Args:
        catalog_number: Número del catálogo (ej: '01', '07', '59')
        
    Returns:
        Lista de diccionarios con código y descripción
        
    Raises:
        FileNotFoundError: Si el catálogo no existe
        json.JSONDecodeError: Si el JSON es inválido
    """
    catalog_file = CATALOGS_DIR / f"catalogo_{catalog_number}.json"
    
    if not catalog_file.exists():
        raise FileNotFoundError(f"Catálogo {catalog_number} no encontrado: {catalog_file}")
        
    with open(catalog_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_catalog_codes(catalog_number: str) -> Set[str]:
    """Obtiene solo los códigos de un catálogo como set.
    
    Args:
        catalog_number: Número del catálogo
        
    Returns:
        Set con los códigos válidos
    """
    catalog_data = load_catalog(catalog_number)
    return {item['codigo'] for item in catalog_data}


def get_catalog_dict(catalog_number: str) -> Dict[str, str]:
    """Obtiene catálogo como diccionario código -> descripción.
    
    Args:
        catalog_number: Número del catálogo
        
    Returns:
        Dict con códigos como keys y descripciones como values
    """
    catalog_data = load_catalog(catalog_number)
    return {item['codigo']: item['descripcion'] for item in catalog_data}


def validate_code(catalog_number: str, code: str) -> bool:
    """Valida si un código existe en el catálogo especificado.
    
    Args:
        catalog_number: Número del catálogo
        code: Código a validar
        
    Returns:
        True si el código es válido
    """
    try:
        valid_codes = get_catalog_codes(catalog_number)
        return code in valid_codes
    except (FileNotFoundError, json.JSONDecodeError):
        return False  # Si hay error, no validar


# Funciones especiales para catálogos con estructura diferente
def get_catalog_02_currencies() -> Dict[str, str]:
    """Obtiene catálogo 02 (monedas) con estructura especial."""
    try:
        catalog_data = load_catalog('02')
        # Estructura: Currency -> CurrencyName
        result = {}
        for item in catalog_data:
            currency_code = item.get('Currency', '')
            currency_name = item.get('CurrencyName', '')
            if currency_code and currency_name:
                # Solo tomar la primera ocurrencia para evitar duplicados
                if currency_code not in result:
                    result[currency_code] = currency_name
        return result
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def get_catalog_04_countries() -> Dict[str, str]:
    """Obtiene catálogo 04 (países) con estructura especial."""
    try:
        catalog_data = load_catalog('04')
        # Estructura: A2 -> Country (código ISO 2 letras)
        result = {}
        for item in catalog_data:
            country_code = item.get('A2', '')  # Código ISO de 2 letras (PE, US, etc.)
            country_name = item.get('Country', '')
            if country_code and country_name:
                result[country_code] = country_name
        return result
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


# Catálogos más utilizados (cargados al import para performance)
TIPOS_DOCUMENTO = get_catalog_dict('01')  # 01, 03, etc.
MONEDAS = get_catalog_02_currencies()     # PEN, USD, EUR, etc. (estructura especial)
UNIDADES_MEDIDA = get_catalog_dict('03')  # NIU, ZZ, etc.
PAISES = get_catalog_04_countries()       # PE, US, etc. (estructura especial)
TIPOS_TRIBUTO = get_catalog_dict('05')    # 1000, 2000, etc.
TIPOS_DOC_IDENTIDAD = get_catalog_dict('06')  # 1, 4, 6, etc.
CODIGOS_AFECTACION_IGV = get_catalog_dict('07')  # 10, 20, 30, etc.
CODIGOS_NOTA_CREDITO = get_catalog_dict('09')    # 01, 02, etc.
CODIGOS_NOTA_DEBITO = get_catalog_dict('10')     # 01, 02, etc.
TIPOS_OPERACION = get_catalog_dict('17')          # 0101, 0102, etc.
MEDIOS_PAGO = get_catalog_dict('59')              # 001, 002, etc.

# Sets para validación rápida
TIPOS_DOCUMENTO_CODES = set(TIPOS_DOCUMENTO.keys())
MONEDAS_CODES = set(MONEDAS.keys())
UNIDADES_MEDIDA_CODES = set(UNIDADES_MEDIDA.keys())
PAISES_CODES = set(PAISES.keys()) 
CODIGOS_AFECTACION_IGV_CODES = set(CODIGOS_AFECTACION_IGV.keys())
TIPOS_OPERACION_CODES = set(TIPOS_OPERACION.keys())


def get_available_catalogs() -> List[str]:
    """Lista los catálogos disponibles en el directorio.
    
    Returns:
        Lista de números de catálogos disponibles
    """
    catalog_files = CATALOGS_DIR.glob("catalogo_*.json")
    return sorted([f.stem.replace('catalogo_', '') for f in catalog_files])


def get_catalog_description(catalog_number: str) -> Optional[str]:
    """Obtiene la descripción de un catálogo.
    
    Args:
        catalog_number: Número del catálogo
        
    Returns:
        Descripción del catálogo o None si no se encuentra
    """
    catalog_descriptions = {
        '01': 'Tipo de documento',
        '02': 'Tipo de monedas',
        '03': 'Tipo de unidad de medida comercial',
        '04': 'Código de país',
        '05': 'Código de tipos de tributos y otros conceptos',
        '06': 'Código de tipo de documento de identidad', 
        '07': 'Código de tipo de afectación del IGV',
        '08': 'Código de tipos de sistema de cálculo del ISC',
        '09': 'Códigos de tipo de nota de crédito electrónica',
        '10': 'Códigos de tipo de nota de débito electrónica',
        '11': 'Códigos de tipo de valor de venta (Resumen diario)',
        '12': 'Código de documentos relacionados tributarios',
        '14': 'Código de otros conceptos tributarios',
        '15': 'Códigos de elementos adicionales en la factura y boleta',
        '16': 'Código de tipo de precio de venta unitario',
        '17': 'Código de tipo de operación',
        '18': 'Código de modalidad de transporte',
        '19': 'Código de estado del ítem (resumen diario)',
        '20': 'Código de motivo de traslado',
        '21': 'Código de documentos relacionados (guía de remisión)',
        '22': 'Código de regimen de percepciones',
        '23': 'Código de regimen de retenciones', 
        '24': 'Código de tarifa de servicios públicos',
        '26': 'Tipo de préstamo (créditos hipotecarios)',
        '27': 'Indicador de primera vivienda',
        '51': 'Código de tipo de operación',
        '52': 'Códigos de leyendas',
        '53': 'Códigos de cargos, descuentos y otras deducciones',
        '54': 'Códigos de bienes y servicios sujetos a detracciones',
        '55': 'Código de identificación del concepto tributario',
        '56': 'Código de tipo de servicio público',
        '57': 'Código de tipo de servicio públicos - telecomunicaciones',
        '58': 'Código de tipo de medidor (recibo de luz)',
        '59': 'Medios de Pago',
        '60': 'Código de tipo de dirección',
    }
    
    return catalog_descriptions.get(catalog_number)


# Funciones de validación específicas (para uso en validators)
def validar_tipo_documento(codigo: str) -> bool:
    """Valida código de tipo de documento (catálogo 01)."""
    return codigo in TIPOS_DOCUMENTO_CODES


def validar_unidad_medida(codigo: str) -> bool:
    """Valida código de unidad de medida (catálogo 03).""" 
    return codigo in UNIDADES_MEDIDA_CODES


def validar_afectacion_igv(codigo: str) -> bool:
    """Valida código de afectación IGV (catálogo 07)."""
    return codigo in CODIGOS_AFECTACION_IGV_CODES


def validar_tipo_operacion(codigo: str) -> bool:
    """Valida código de tipo de operación (catálogo 17)."""
    return codigo in TIPOS_OPERACION_CODES


def validar_nota_credito(codigo: str) -> bool:
    """Valida código de motivo de nota de crédito (catálogo 09)."""
    return validate_code('09', codigo)


def validar_nota_debito(codigo: str) -> bool:
    """Valida código de motivo de nota de débito (catálogo 10)."""
    return validate_code('10', codigo)


def validar_moneda(codigo: str) -> bool:
    """Valida código de moneda (catálogo 02)."""
    return codigo in MONEDAS_CODES


def validar_pais(codigo: str) -> bool:
    """Valida código de país (catálogo 04)."""
    return codigo in PAISES_CODES