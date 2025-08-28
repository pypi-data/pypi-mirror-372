"""Builder específico para facturas y boletas."""

from typing import Dict

from ..models.invoice import Invoice
from .xml_builder import XmlBuilder, XmlBuilderError


class InvoiceBuilder(XmlBuilder):
    """Builder para generar XMLs de facturas y boletas (UBL 2.1)."""
    
    def get_template_name(self) -> str:
        """Obtiene el nombre del template para facturas/boletas."""
        return "invoice_21.xml"
    
    def prepare_context(self, document: Invoice) -> Dict:
        """
        Prepara el contexto para el template de facturas.
        
        Args:
            document: Invoice (factura o boleta)
            
        Returns:
            Diccionario con contexto para template
        """
        # Validar documento primero
        self.validate_document(document)
        
        # Validar que sea factura o boleta
        if document.tipo_doc not in ["01", "03"]:
            raise XmlBuilderError(f"Tipo documento inválido para InvoiceBuilder: {document.tipo_doc}")
        
        print(f"[InvoiceBuilder] Preparando contexto para {document.get_tipo_comprobante_desc()}")
        
        # Preparar contexto básico
        context = {
            'doc': document,
        }
        
        # Agregar información adicional útil para el template
        context.update({
            'is_factura': document.is_factura(),
            'is_boleta': document.is_boleta(),
            'total_details': len(document.details),
            'total_legends': len(document.legends),
        })
        
        # Validaciones específicas
        self._validate_invoice_specific(document)
        
        print(f"[InvoiceBuilder] Contexto preparado - Detalles: {len(document.details)}, Leyendas: {len(document.legends)}")
        
        return context
    
    def _validate_invoice_specific(self, document: Invoice) -> None:
        """
        Validaciones específicas para facturas/boletas.
        
        Args:
            document: Invoice a validar
            
        Raises:
            XmlBuilderError: Si hay errores de validación
        """
        # Validar tipo documento cliente - Greenter permite cualquier tipo válido
        tipos_validos = ["0", "1", "4", "6", "7", "A"]
        if str(document.client.tipo_doc) not in tipos_validos:
            raise XmlBuilderError(f"Tipo documento cliente no válido: {document.client.tipo_doc}. Válidos: {tipos_validos}")
        
        # Validar que tenga tipo de operación
        if not document.tipo_operacion:
            raise XmlBuilderError("Tipo de operación es requerido")
            
        # Validar totales coherentes
        if document.mto_impventa < 0:
            raise XmlBuilderError(f"Total de venta no puede ser negativo: {document.mto_impventa}")
            
        # Validar que los detalles tengan información mínima
        for i, detail in enumerate(document.details):
            if not detail.des_item.strip():
                raise XmlBuilderError(f"Detalle {i+1}: descripción requerida")
            if detail.cantidad <= 0:
                raise XmlBuilderError(f"Detalle {i+1}: cantidad debe ser mayor a 0")
            if detail.mto_valor_unitario < 0:
                raise XmlBuilderError(f"Detalle {i+1}: valor unitario no puede ser negativo")
    
    def build(self, document: Invoice) -> str:
        """
        Construye XML específico para factura/boleta.
        
        Args:
            document: Invoice (factura o boleta)
            
        Returns:
            XML UBL 2.1 válido
            
        Raises:
            XmlBuilderError: Si hay errores en la generación
        """
        if not isinstance(document, Invoice):
            raise XmlBuilderError(f"InvoiceBuilder solo acepta objetos Invoice, recibido: {type(document)}")
            
        print(f"[InvoiceBuilder] Construyendo XML para {document.get_tipo_comprobante_desc()}: {document.get_nombre()}")
        
        # Usar el método base
        xml_content = super().build(document)
        
        # Validaciones post-generación
        self._validate_generated_xml(xml_content, document)
        
        return xml_content
    
    def _validate_generated_xml(self, xml_content: str, document: Invoice) -> None:
        """
        Valida el XML generado.
        
        Args:
            xml_content: XML generado
            document: Documento original
            
        Raises:
            XmlBuilderError: Si el XML es inválido
        """
        # Validaciones básicas
        if not xml_content.startswith('<?xml'):
            raise XmlBuilderError("XML no tiene declaración XML válida")
            
        if '<Invoice' not in xml_content:
            raise XmlBuilderError("XML no contiene elemento Invoice raíz")
            
        # Validar que contenga información crítica
        critical_elements = [
            f'<cbc:ID>{document.serie}-{document.correlativo}</cbc:ID>',
            f'<cbc:InvoiceTypeCode',
            f'<cbc:DocumentCurrencyCode>{document.tipo_moneda}</cbc:DocumentCurrencyCode>',
            f'<cac:AccountingSupplierParty>',
            f'<cac:AccountingCustomerParty>',
        ]
        
        for element in critical_elements:
            if element not in xml_content:
                raise XmlBuilderError(f"XML no contiene elemento crítico: {element}")
                
        print(f"[InvoiceBuilder] XML validado exitosamente - {len(xml_content)} caracteres")