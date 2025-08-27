"""
cpe-sc-engine: Sistema de Emision del Contribuyente - Facturacion Electronica Peruana

Libreria completa para facturacion electronica peruana con integracion SUNAT.
"""

from datetime import datetime
from typing import Dict, Any, Optional

# Importar modelos principales
from .core.models import (
    Invoice,
    Note, 
    Company,
    Client,
    Address,
    SaleDetail
)

# Importar builders
from .core.builders.invoice_builder import InvoiceBuilder
from .core.builders.note_builder import NoteBuilder
from .core.builders.signed_xml_builder import SignedXmlBuilder

# Importar servicios SUNAT
from .sunat.credentials import SunatCredentials
from .sunat.endpoints import SunatEndpoints
from .sunat.bill_sender import BillSender
from .sunat.certificate_manager import CertificateManager
from .sunat.xml_signer import XmlSigner

# Importar catálogos oficiales SUNAT para uso directo
from .catalogs import (
    # Catálogos principales (ahora oficiales)
    TIPOS_DOC_IDENTIDAD as TIPOS_DOCUMENTO_IDENTIDAD,  # Compatibilidad
    MONEDAS as TIPOS_MONEDA,                           # Compatibilidad
    UNIDADES_MEDIDA,
    TIPOS_TRIBUTO as TIPOS_TRIBUTOS,                   # Compatibilidad
    TIPOS_DOCUMENTO as TIPOS_DOCUMENTOS,               # Compatibilidad
    CODIGOS_AFECTACION_IGV,
    CODIGOS_NOTA_CREDITO as MOTIVOS_NOTA_CREDITO,      # Compatibilidad
    CODIGOS_NOTA_DEBITO as MOTIVOS_NOTA_DEBITO,        # Compatibilidad
    TIPOS_OPERACION,
    
    # Funciones de validación (remapeadas)
    validar_pais as validar_tipo_documento_identidad,      # Compatibilidad
    validar_moneda as validar_tipo_moneda,                 # Compatibilidad
    validar_unidad_medida,
    validar_tipo_documento,
    validar_afectacion_igv,
    validar_nota_credito as validar_motivo_nota_credito,   # Compatibilidad
    validar_nota_debito as validar_motivo_nota_debito,     # Compatibilidad
    validar_tipo_operacion,
    get_catalog_description as get_descripcion_catalogo,   # Compatibilidad
)

# Constantes por defecto (definir localmente para compatibilidad)
IGV_PORCENTAJE_DEFAULT = 18.0
MONEDA_DEFAULT = "PEN"
UNIDAD_DEFAULT = "NIU" 
AFECTACION_IGV_DEFAULT = "10"

__version__ = "0.1.0"
__author__ = "Quanta Solutions"
__email__ = "suma@bequanta.com"

# Exportar clases principales
__all__ = [
    # Modelos
    "Invoice",
    "Note", 
    "Company", 
    "Client",
    "Address",
    "SaleDetail",
    # Builders
    "InvoiceBuilder",
    "NoteBuilder", 
    "SignedXmlBuilder",
    # SUNAT
    "SunatCredentials",
    "SunatEndpoints",
    "BillSender",
    "CertificateManager",
    "XmlSigner",
    # Funciones de alto nivel
    "send_invoice",
    "send_receipt", 
    "send_credit_note",
    "send_debit_note",
    "create_invoice_data",
    "create_note_data",
    # Catálogos SUNAT
    "TIPOS_DOCUMENTO_IDENTIDAD",
    "TIPOS_MONEDA", 
    "UNIDADES_MEDIDA",
    "TIPOS_TRIBUTOS",
    "TIPOS_DOCUMENTOS",
    "CODIGOS_AFECTACION_IGV",
    "MOTIVOS_NOTA_CREDITO",
    "MOTIVOS_NOTA_DEBITO", 
    "TIPOS_OPERACION",
    # Funciones de validación
    "validar_tipo_documento_identidad",
    "validar_tipo_moneda",
    "validar_unidad_medida", 
    "validar_tipo_documento",
    "validar_afectacion_igv",
    "validar_motivo_nota_credito",
    "validar_motivo_nota_debito",
    "validar_tipo_operacion",
    "get_descripcion_catalogo",
    # Constantes por defecto
    "IGV_PORCENTAJE_DEFAULT",
    "MONEDA_DEFAULT",
    "UNIDAD_DEFAULT", 
    "AFECTACION_IGV_DEFAULT"
]


def create_invoice_data(
    serie: str,
    correlativo: int,
    company_data: Dict[str, Any],
    client_data: Dict[str, Any],
    items: list,
    fecha_emision: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Crea datos de factura desde diccionarios simples.
    
    Args:
        serie: Serie de la factura (ej: 'F001')
        correlativo: Numero correlativo
        company_data: Datos de la empresa {'ruc': '...', 'razon_social': '...', ...}
        client_data: Datos del cliente {'tipo_doc': 6, 'numero_doc': '...', ...}
        items: Lista de items [{'codigo': '...', 'descripcion': '...', 'cantidad': 1, ...}]
        fecha_emision: Fecha de emision (default: ahora)
        
    Returns:
        Diccionario con datos estructurados para Invoice
    """
    if fecha_emision is None:
        fecha_emision = datetime.now()
    
    # Crear modelos desde diccionarios
    company_address = Address(**company_data.get('address', {
        'ubigeo': '150101',
        'departamento': 'Lima',
        'provincia': 'Lima',
        'distrito': 'Lima',
        'direccion': 'Sin direccion'
    }))
    
    company = Company(
        ruc=company_data['ruc'],
        razon_social=company_data['razon_social'],
        nombre_comercial=company_data.get('nombre_comercial', company_data['razon_social']),
        address=company_address,
        email=company_data.get('email', '')
    )
    
    client = Client(
        tipo_doc=client_data['tipo_doc'],
        numero_doc=client_data['numero_doc'],
        razon_social=client_data['razon_social'],
        address=Address(**client_data['address']) if 'address' in client_data else None
    )
    
    # Crear detalles
    details = []
    for item in items:
        detail = SaleDetail(
            cod_item=item['codigo'],
            des_item=item['descripcion'],
            cantidad=item['cantidad'],
            unidad=item.get('unidad', 'NIU'),
            mto_valor_unitario=item['precio_unitario'],
            tip_afe_igv=item.get('tip_afe_igv', '10'),  # Gravado por defecto
            porcentaje_igv=item.get('porcentaje_igv', 18.0)
        )
        details.append(detail)
    
    return {
        'serie': serie,
        'correlativo': correlativo,
        'fecha_emision': fecha_emision,
        'company': company,
        'client': client,
        'details': details
    }


def create_note_data(
    serie: str,
    correlativo: int,
    tipo_nota: str,  # '07' para credito, '08' para debito
    documento_afectado: str,  # 'F001-123'
    motivo: str,
    company_data: Dict[str, Any],
    client_data: Dict[str, Any], 
    items: list,
    fecha_emision: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Crea datos de nota de credito/debito desde diccionarios simples.
    
    Args:
        serie: Serie de la nota (ej: 'FC01')
        correlativo: Numero correlativo
        tipo_nota: '07' para credito, '08' para debito
        documento_afectado: Documento que afecta (ej: 'F001-123')
        motivo: Motivo de la nota
        company_data: Datos de la empresa
        client_data: Datos del cliente
        items: Lista de items
        fecha_emision: Fecha de emision (default: ahora)
        
    Returns:
        Diccionario con datos estructurados para Note
    """
    base_data = create_invoice_data(serie, correlativo, company_data, client_data, items, fecha_emision)
    
    # Agregar datos especificos de nota
    base_data.update({
        'tipo_doc': tipo_nota,
        'tipDocAfectado': '01' if documento_afectado.startswith('F') else '03',
        'numDocfectado': documento_afectado,
        'codMotivo': '01' if tipo_nota == '07' else '01', 
        'desMotivo': motivo
    })
    
    return base_data


def send_invoice(credentials: SunatCredentials, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Envia factura a SUNAT.
    
    Args:
        credentials: Credenciales SUNAT
        invoice_data: Datos de la factura (usar create_invoice_data)
        
    Returns:
        Respuesta completa de SUNAT
    """
    try:
        # Crear factura con todos los datos proporcionados
        invoice_args = {
            'serie': invoice_data['serie'],
            'correlativo': invoice_data['correlativo'],
            'fecha_emision': invoice_data['fecha_emision'],
            'tipo_operacion': "0101",
            'tipo_doc': "01",
            'tipo_moneda': "PEN",
            'company': invoice_data['company'],
            'client': invoice_data['client']
        }
        
        # Agregar campos opcionales si están presentes (enfoque declarativo)
        optional_fields = [
            'mto_oper_gravadas', 'mto_oper_inafectas', 'mto_oper_exoneradas',
            'mto_oper_exportacion', 'mto_oper_gratuitas', 'mto_igv_gratuitas',
            'mto_igv', 'mto_isc', 'mto_otros_tributos', 'mto_total_tributos',
            'mto_base_isc', 'mto_base_otros_tributos', 'mto_impventa',
            'sub_total', 'valor_venta', 'sum_dscto_global', 'mto_descuentos',
            'sum_otros_descuentos', 'sum_otros_cargos', 'total_anticipos',
            'observacion'
        ]
        
        for field in optional_fields:
            if field in invoice_data:
                invoice_args[field] = invoice_data[field]
        
        invoice = Invoice(**invoice_args)
        
        invoice.details = invoice_data['details']
        
        # Enviar con SignedXmlBuilder
        builder = SignedXmlBuilder()
        builder.xml_signer.certificate_manager.load_certificate_from_credentials(credentials.certificado)
        builder.set_sunat_credentials(credentials.usuario, credentials.password)
        result = builder.build_sign_and_send(invoice)
        
        return result
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'error_type': type(e).__name__
        }


def send_receipt(credentials: SunatCredentials, receipt_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Envia boleta a SUNAT.
    
    Args:
        credentials: Credenciales SUNAT
        receipt_data: Datos de la boleta (usar create_invoice_data)
        
    Returns:
        Respuesta completa de SUNAT
    """
    try:
        # Crear boleta con todos los datos proporcionados
        receipt_args = {
            'serie': receipt_data['serie'],  # No cambiar automáticamente 
            'correlativo': receipt_data['correlativo'],
            'fecha_emision': receipt_data['fecha_emision'],
            'tipo_operacion': "0101",
            'tipo_doc': "03",  # Boleta
            'tipo_moneda': "PEN",
            'company': receipt_data['company'],
            'client': receipt_data['client']
        }
        
        # Agregar campos opcionales si están presentes (enfoque declarativo)
        optional_fields = [
            'mto_oper_gravadas', 'mto_oper_inafectas', 'mto_oper_exoneradas',
            'mto_oper_exportacion', 'mto_oper_gratuitas', 'mto_igv_gratuitas',
            'mto_igv', 'mto_isc', 'mto_otros_tributos', 'mto_total_tributos',
            'mto_base_isc', 'mto_base_otros_tributos', 'mto_impventa',
            'sub_total', 'valor_venta', 'sum_dscto_global', 'mto_descuentos',
            'sum_otros_descuentos', 'sum_otros_cargos', 'total_anticipos',
            'observacion'
        ]
        
        for field in optional_fields:
            if field in receipt_data:
                receipt_args[field] = receipt_data[field]
        
        receipt = Invoice(**receipt_args)
        
        receipt.details = receipt_data['details']
        
        # Enviar
        builder = SignedXmlBuilder()
        builder.xml_signer.certificate_manager.load_certificate_from_credentials(credentials.certificado)
        builder.set_sunat_credentials(credentials.usuario, credentials.password)
        result = builder.build_sign_and_send(receipt)
        
        return result
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'error_type': type(e).__name__
        }


def send_credit_note(credentials: SunatCredentials, note_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Envia nota de credito a SUNAT.
    
    Args:
        credentials: Credenciales SUNAT
        note_data: Datos de la nota (usar create_note_data)
        
    Returns:
        Respuesta completa de SUNAT
    """
    try:
        # Crear nota de crédito con todos los datos proporcionados
        note_args = {
            'serie': note_data['serie'],
            'correlativo': note_data['correlativo'],
            'fecha_emision': note_data['fecha_emision'],
            'tipo_doc': "07",
            'tipo_moneda': "PEN",
            'company': note_data['company'],
            'client': note_data['client'],
            'tipDocAfectado': note_data['tipDocAfectado'],
            'numDocfectado': note_data['numDocfectado'],
            'codMotivo': note_data['codMotivo'],
            'desMotivo': note_data['desMotivo']
        }
        
        # Agregar campos opcionales si están presentes (enfoque declarativo)
        optional_fields = [
            'mto_oper_gravadas', 'mto_oper_inafectas', 'mto_oper_exoneradas',
            'mto_oper_exportacion', 'mto_oper_gratuitas', 'mto_igv_gratuitas',
            'mto_igv', 'mto_isc', 'mto_otros_tributos', 'mto_total_tributos',
            'mto_base_isc', 'mto_base_otros_tributos', 'mto_impventa',
            'sub_total', 'valor_venta', 'sum_dscto_global', 'mto_descuentos',
            'sum_otros_descuentos', 'sum_otros_cargos', 'total_anticipos',
            'observacion'
        ]
        
        for field in optional_fields:
            if field in note_data:
                note_args[field] = note_data[field]
        
        note = Note(**note_args)
        
        note.details = note_data['details']
        
        # Enviar
        builder = SignedXmlBuilder()
        builder.xml_signer.certificate_manager.load_certificate_from_credentials(credentials.certificado)
        builder.set_sunat_credentials(credentials.usuario, credentials.password)
        result = builder.build_sign_and_send(note)
        
        return result
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'error_type': type(e).__name__
        }


def send_debit_note(credentials: SunatCredentials, note_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Envia nota de debito a SUNAT.
    
    Args:
        credentials: Credenciales SUNAT
        note_data: Datos de la nota (usar create_note_data con tipo '08')
        
    Returns:
        Respuesta completa de SUNAT
    """
    try:
        # Crear nota de débito con todos los datos proporcionados
        note_args = {
            'serie': note_data['serie'],
            'correlativo': note_data['correlativo'],
            'fecha_emision': note_data['fecha_emision'],
            'tipo_doc': "08",  # Debito
            'tipo_moneda': "PEN",
            'company': note_data['company'],
            'client': note_data['client'],
            'tipDocAfectado': note_data['tipDocAfectado'],
            'numDocfectado': note_data['numDocfectado'],
            'codMotivo': note_data['codMotivo'],
            'desMotivo': note_data['desMotivo']
        }
        
        # Agregar campos opcionales si están presentes (enfoque declarativo)
        optional_fields = [
            'mto_oper_gravadas', 'mto_oper_inafectas', 'mto_oper_exoneradas',
            'mto_oper_exportacion', 'mto_oper_gratuitas', 'mto_igv_gratuitas',
            'mto_igv', 'mto_isc', 'mto_otros_tributos', 'mto_total_tributos',
            'mto_base_isc', 'mto_base_otros_tributos', 'mto_impventa',
            'sub_total', 'valor_venta', 'sum_dscto_global', 'mto_descuentos',
            'sum_otros_descuentos', 'sum_otros_cargos', 'total_anticipos',
            'observacion'
        ]
        
        for field in optional_fields:
            if field in note_data:
                note_args[field] = note_data[field]
        
        note = Note(**note_args)
        
        note.details = note_data['details']
        
        # Enviar
        builder = SignedXmlBuilder()
        builder.xml_signer.certificate_manager.load_certificate_from_credentials(credentials.certificado)
        builder.set_sunat_credentials(credentials.usuario, credentials.password)
        result = builder.build_sign_and_send(note)
        
        return result
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'error_type': type(e).__name__
        }