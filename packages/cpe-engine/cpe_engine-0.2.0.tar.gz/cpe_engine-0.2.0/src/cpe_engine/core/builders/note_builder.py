"""Builder específico para notas de crédito y débito."""

from typing import Dict

from ..models.note import Note
from .xml_builder import XmlBuilder, XmlBuilderError


class NoteBuilder(XmlBuilder):
    """Builder para generar XMLs de notas de crédito y débito (UBL 2.1)."""
    
    def get_template_name(self, document: Note) -> str:
        """
        Obtiene el nombre del template según el tipo de nota.
        
        Args:
            document: Note (nota de crédito o débito)
            
        Returns:
            Nombre del template
        """
        # Determinar template según tipo de documento como greenter
        if document.tipo_doc == "07":  # Nota de crédito
            return "credit_note_21.xml"
        elif document.tipo_doc == "08":  # Nota de débito
            return "debit_note_21.xml"
        else:
            raise XmlBuilderError(f"Tipo de documento inválido para NoteBuilder: {document.tipo_doc}")
    
    def prepare_context(self, document: Note) -> Dict:
        """
        Prepara el contexto para el template de notas.
        
        Args:
            document: Note (nota de crédito o débito)
            
        Returns:
            Diccionario con contexto para template
        """
        # Validar documento primero
        self.validate_document(document)
        
        # Validar que sea nota de crédito o débito
        if document.tipo_doc not in ["07", "08"]:
            raise XmlBuilderError(f"Tipo documento inválido para NoteBuilder: {document.tipo_doc}")
        
        print(f"[NoteBuilder] Preparando contexto para {document.get_tipo_comprobante_desc()}")
        
        # Preparar contexto básico
        context = {
            'doc': document,
        }
        
        # Agregar información adicional útil para el template
        context.update({
            'is_nota_credito': document.is_nota_credito(),
            'is_nota_debito': document.is_nota_debito(),
            'total_details': len(document.details),
            'total_legends': len(document.legends),
            'motivo_descripcion': document.get_motivo_desc(),
        })
        
        # Validaciones específicas
        self._validate_note_specific(document)
        
        print(f"[NoteBuilder] Contexto preparado - Motivo: {document.cod_motivo}, Doc. Afectado: {document.num_doc_afectado}")
        
        return context
    
    def _validate_note_specific(self, document: Note) -> None:
        """
        Validaciones específicas para notas.
        
        Args:
            document: Note a validar
            
        Raises:
            XmlBuilderError: Si hay errores de validación
        """
        # Validar información del documento afectado
        if not document.num_doc_afectado.strip():
            raise XmlBuilderError("Número de documento afectado es requerido")
            
        if not document.tip_doc_afectado.strip():
            raise XmlBuilderError("Tipo de documento afectado es requerido")
            
        # Validar motivo
        if not document.cod_motivo.strip():
            raise XmlBuilderError("Código de motivo es requerido")
            
        if not document.des_motivo.strip():
            raise XmlBuilderError("Descripción de motivo es requerida")
        
        # Validar coherencia de motivos según catálogos
        motivos_validos_credito = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10"]
        motivos_validos_debito = ["01", "02", "03", "10"]
        
        if document.is_nota_credito() and document.cod_motivo not in motivos_validos_credito:
            raise XmlBuilderError(f"Código motivo inválido para nota crédito: {document.cod_motivo}")
            
        if document.is_nota_debito() and document.cod_motivo not in motivos_validos_debito:
            raise XmlBuilderError(f"Código motivo inválido para nota débito: {document.cod_motivo}")
        
        # Validar formato del documento afectado (Serie-Correlativo)
        if "-" not in document.num_doc_afectado:
            raise XmlBuilderError(f"Formato inválido para documento afectado: {document.num_doc_afectado} (debe ser Serie-Correlativo)")
            
        # Validar totales coherentes
        if document.mto_impventa <= 0:
            raise XmlBuilderError(f"Total de nota debe ser mayor a 0: {document.mto_impventa}")
            
        # Validar que los detalles tengan información mínima
        for i, detail in enumerate(document.details):
            if not detail.des_item.strip():
                raise XmlBuilderError(f"Detalle {i+1}: descripción requerida")
            if detail.cantidad <= 0:
                raise XmlBuilderError(f"Detalle {i+1}: cantidad debe ser mayor a 0")
            if detail.mto_valor_unitario < 0:
                raise XmlBuilderError(f"Detalle {i+1}: valor unitario no puede ser negativo")
    
    def build(self, document: Note) -> str:
        """
        Construye XML específico para nota de crédito/débito.
        
        Args:
            document: Note (nota de crédito o débito)
            
        Returns:
            XML UBL 2.1 válido
            
        Raises:
            XmlBuilderError: Si hay errores en la generación
        """
        if not isinstance(document, Note):
            raise XmlBuilderError(f"NoteBuilder solo acepta objetos Note, recibido: {type(document)}")
            
        print(f"[NoteBuilder] Construyendo XML para {document.get_tipo_comprobante_desc()}: {document.get_nombre()}")
        
        # Construir XML personalizado
        try:
            print(f"[NoteBuilder] Iniciando construcción XML personalizada")
            
            # Obtener template dinámicamente
            template_name = self.get_template_name(document)
            template = self.jinja_env.get_template(template_name)
            print(f"[NoteBuilder] Template cargado: {template_name}")
            
            # Preparar contexto
            context = self.prepare_context(document)
            print(f"[NoteBuilder] Contexto preparado con {len(context)} variables")
            
            # Generar XML
            xml_content = template.render(context)
            print(f"[NoteBuilder] XML generado: {len(xml_content)} caracteres")
            
            # Validar que se generó contenido
            if not xml_content.strip():
                raise XmlBuilderError("Template no generó contenido")
                
        except Exception as e:
            raise XmlBuilderError(f"Error construyendo XML para nota: {str(e)}") from e
        
        # Validaciones básicas post-generación
        if not xml_content.startswith('<?xml'):
            raise XmlBuilderError("XML no tiene declaración XML válida")
        if document.is_nota_credito() and '<CreditNote' not in xml_content:
            raise XmlBuilderError("XML de nota crédito no contiene elemento CreditNote raíz")
        elif document.is_nota_debito() and '<DebitNote' not in xml_content:
            raise XmlBuilderError("XML de nota débito no contiene elemento DebitNote raíz")
        
        print(f"[NoteBuilder] XML validado exitosamente - {len(xml_content)} caracteres")
        
        return xml_content
    
    def _validate_generated_xml(self, xml_content: str, document: Note) -> None:
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
            
        # Validar elemento raíz según tipo de nota
        if document.is_nota_credito():
            if '<CreditNote' not in xml_content:
                raise XmlBuilderError("XML de nota crédito no contiene elemento CreditNote raíz")
        else:
            if '<DebitNote' not in xml_content:
                raise XmlBuilderError("XML de nota débito no contiene elemento DebitNote raíz")
            
        # Validar que contenga información crítica
        critical_elements = [
            f'<cbc:ID>{document.serie}-{document.correlativo}</cbc:ID>',
            f'<cbc:DocumentCurrencyCode>{document.tipo_moneda}</cbc:DocumentCurrencyCode>',
            f'<cac:DiscrepancyResponse>',
            f'<cbc:ReferenceID>{document.num_doc_afectado}</cbc:ReferenceID>',
            f'<cbc:ResponseCode>{document.cod_motivo}</cbc:ResponseCode>',
            f'<cac:BillingReference>',
            f'<cac:AccountingSupplierParty>',
            f'<cac:AccountingCustomerParty>',
        ]
        
        for element in critical_elements:
            if element not in xml_content:
                raise XmlBuilderError(f"XML no contiene elemento crítico: {element}")
                
        print(f"[NoteBuilder] XML validado exitosamente - {len(xml_content)} caracteres")