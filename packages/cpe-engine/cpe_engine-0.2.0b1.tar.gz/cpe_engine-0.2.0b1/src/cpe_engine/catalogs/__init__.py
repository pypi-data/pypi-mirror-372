"""Catalogos SUNAT para validaciones.

IMPORTANTE: Los catalogos oficiales (official_catalogs.py) han reemplazado 
a los catalogos antiguos (sunat_catalogs.py). Los catalogos oficiales contienen
todos los datos de SUNAT actualizados y completos.

Para migrar tu codigo:
- Antes: from cpe_engine.catalogs.sunat_catalogs import CODIGOS_AFECTACION_IGV
- Ahora: from cpe_engine.catalogs import CODIGOS_AFECTACION_IGV (funciona igual)
"""

import warnings

# Deprecar sunat_catalogs.py con warning
def _deprecated_import():
    warnings.warn(
        "sunat_catalogs.py esta deprecado. Usa official_catalogs.py que tiene "
        "datos oficiales completos de SUNAT. Los imports desde 'from cpe_engine.catalogs import ...' "
        "funcionan igual pero ahora usan datos oficiales.",
        DeprecationWarning,
        stacklevel=3
    )

# Exportar catalogos oficiales (reemplazan a sunat_catalogs)
from .official_catalogs import (
    # Diccionarios completos (35 catalogos oficiales)
    TIPOS_DOCUMENTO,
    MONEDAS,              # NUEVO - Catalogo 02 completo
    UNIDADES_MEDIDA,
    PAISES,               # NUEVO - Catalogo 04 completo  
    TIPOS_TRIBUTO,
    TIPOS_DOC_IDENTIDAD,
    CODIGOS_AFECTACION_IGV,
    CODIGOS_NOTA_CREDITO,
    CODIGOS_NOTA_DEBITO,
    TIPOS_OPERACION,
    MEDIOS_PAGO,
    
    # Sets para validacion rapida
    TIPOS_DOCUMENTO_CODES,
    MONEDAS_CODES,        # NUEVO
    UNIDADES_MEDIDA_CODES,
    PAISES_CODES,         # NUEVO
    CODIGOS_AFECTACION_IGV_CODES,
    TIPOS_OPERACION_CODES,
    
    # Funciones de validacion
    validar_tipo_documento,
    validar_moneda,       # NUEVO
    validar_unidad_medida,
    validar_pais,         # NUEVO
    validar_afectacion_igv,
    validar_tipo_operacion,
    validar_nota_credito,
    validar_nota_debito,
    
    # Funciones de acceso
    load_catalog,
    get_catalog_codes,
    get_catalog_dict,
    validate_code,
    get_available_catalogs,
    get_catalog_description,
)