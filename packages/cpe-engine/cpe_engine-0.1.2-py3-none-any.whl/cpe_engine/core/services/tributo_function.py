"""
TributoFunction - Mapeo de códigos de afectación IGV a códigos de tributo SUNAT.
Equivalente al TributoFunction.php de Greenter.
"""

from typing import Optional, Dict, Any


class TributoFunction:
    """Maneja el mapeo entre códigos de afectación IGV y códigos de tributo SUNAT."""
    
    # Mapeo de códigos de tributo basado en Greenter
    # [código_tributo] => [TaxTypeCode, Name]
    _tributos = {
        '1000': ['VAT', 'IGV'],        # IGV - Impuesto General a las Ventas
        '1016': ['VAT', 'IVAP'],       # IVAP - Impuesto a la Venta de Arroz Pilado
        '2000': ['EXC', 'ISC'],        # ISC - Impuesto Selectivo al Consumo
        '7152': ['OTH', 'ICBPER'],     # ICBPER - Impuesto a las bolsas de plástico
        '9995': ['FRE', 'EXP'],        # Exportación
        '9996': ['FRE', 'GRA'],        # Gratuitas
        '9997': ['VAT', 'EXO'],        # Exonerado
        '9998': ['FRE', 'INA'],        # Inafecto
        '9999': ['OTH', 'OTROS'],      # Otros conceptos de pago
    }
    
    @classmethod
    def get_by_tributo(cls, code: str) -> Optional[Dict[str, str]]:
        """
        Obtiene información del tributo por código.
        
        Args:
            code: Código del tributo (ej: '1000')
            
        Returns:
            Dict con id, code, name del tributo o None si no existe
        """
        if code in cls._tributos:
            values = cls._tributos[code]
            return {
                'id': code,
                'code': values[0],
                'name': values[1],
            }
        return None
    
    @classmethod
    def get_by_afectacion(cls, afectacion: str) -> Optional[Dict[str, str]]:
        """
        Obtiene información del tributo por código de afectación IGV.
        
        Args:
            afectacion: Código de afectación IGV (ej: '10', '20', '40')
            
        Returns:
            Dict con id, code, name del tributo o None si no existe
        """
        code = cls._get_code_by_afectacion(afectacion)
        return cls.get_by_tributo(code)
    
    @classmethod
    def _get_code_by_afectacion(cls, afectacion: str) -> str:
        """
        Mapea código de afectación IGV a código de tributo.
        Basado en el switch del TributoFunction.php original.
        
        Args:
            afectacion: Código de afectación IGV
            
        Returns:
            Código de tributo correspondiente
        """
        try:
            value = int(afectacion)
        except (ValueError, TypeError):
            return '9996'  # Default: Gratuitas
        
        # Mapeo basado en Greenter TributoFunction.php
        mapping = {
            10: '1000',  # Gravado - Operación Onerosa → IGV
            11: '1000',  # Gravado - Retiro por premio → IGV  
            12: '1000',  # Gravado - Retiro por donación → IGV
            13: '1000',  # Gravado - Retiro → IGV
            14: '1000',  # Gravado - Retiro por publicidad → IGV
            15: '1000',  # Gravado - Bonificaciones → IGV
            16: '1000',  # Gravado - Retiro por entrega a trabajadores → IGV
            17: '1016',  # Gravado - IVAP → IVAP
            20: '9997',  # Exonerado - Operación Onerosa → EXO
            21: '9997',  # Exonerado - Transferencia Gratuita → EXO
            30: '9998',  # Inafecto - Operación Onerosa → INA
            31: '9998',  # Inafecto - Retiro por Bonificación → INA
            32: '9998',  # Inafecto - Retiro → INA
            33: '9998',  # Inafecto - Retiro por Muestras Médicas → INA
            34: '9998',  # Inafecto - Retiro por Convenio Colectivo → INA
            35: '9998',  # Inafecto - Retiro por premio → INA
            36: '9998',  # Inafecto - Retiro por publicidad → INA
            40: '9995',  # Exportación → EXP
        }
        
        return mapping.get(value, '9996')  # Default: Gratuitas


# Funciones de conveniencia para usar en templates
def get_tributo_by_afectacion(afectacion: str) -> Dict[str, str]:
    """
    Función de conveniencia para usar en templates Jinja2.
    
    Args:
        afectacion: Código de afectación IGV
        
    Returns:
        Dict con información del tributo (siempre retorna algo válido)
    """
    result = TributoFunction.get_by_afectacion(str(afectacion))
    if result is None:
        # Fallback seguro para casos no contemplados
        return {
            'id': '9999',
            'code': 'OTH', 
            'name': 'OTROS'
        }
    return result


def get_tributo_by_code(code: str) -> Dict[str, str]:
    """
    Función de conveniencia para obtener tributo por código.
    
    Args:
        code: Código del tributo
        
    Returns:
        Dict con información del tributo (siempre retorna algo válido)
    """
    result = TributoFunction.get_by_tributo(str(code))
    if result is None:
        return {
            'id': '9999',
            'code': 'OTH',
            'name': 'OTROS'
        }
    return result