"""Procesador de CDR (Constancia de Recepción) de SUNAT."""

import base64
from datetime import datetime
from typing import Optional, Dict, List, Any
from lxml import etree

from .zip_helper import ZipHelper, ZipHelperError


class CdrProcessorError(Exception):
    """Error procesando CDR."""
    pass


class CdrProcessor:
    """Procesador de respuestas CDR de SUNAT."""
    
    @staticmethod
    def process_cdr_response(cdr_base64: str) -> Dict[str, Any]:
        """
        Procesa respuesta CDR codificada en base64.
        
        El CDR viene como ZIP con XML de respuesta de SUNAT.
        
        Args:
            cdr_base64: CDR codificado en base64
            
        Returns:
            Información estructurada del CDR
            
        Raises:
            CdrProcessorError: Si hay error procesando
        """
        try:
            print(f"[CdrProcessor] Procesando CDR base64 ({len(cdr_base64)} caracteres)")
            
            # Decodificar base64
            cdr_zip_bytes = base64.b64decode(cdr_base64)
            print(f"[CdrProcessor] CDR decodificado ({len(cdr_zip_bytes)} bytes)")
            
            # Extraer XML del ZIP
            cdr_xml = ZipHelper.extract_xml_from_zip(cdr_zip_bytes)
            if not cdr_xml:
                raise CdrProcessorError("CDR ZIP no contiene archivo XML")
            
            # Parsear XML del CDR
            cdr_data = CdrProcessor._parse_cdr_xml(cdr_xml)
            
            # Agregar información adicional
            cdr_data['raw_cdr_base64'] = cdr_base64
            cdr_data['raw_cdr_xml'] = cdr_xml
            cdr_data['processed_at'] = datetime.now().isoformat()
            
            print(f"[CdrProcessor] CDR procesado exitosamente - Estado: {cdr_data.get('response_code')}")
            return cdr_data
            
        except Exception as e:
            error_msg = f"Error procesando CDR: {e}"
            print(f"[CdrProcessor] ERROR: {error_msg}")
            raise CdrProcessorError(error_msg)
    
    @staticmethod
    def _parse_cdr_xml(cdr_xml: str) -> Dict[str, Any]:
        """
        Parsea el XML del CDR de SUNAT.
        
        Args:
            cdr_xml: XML del CDR
            
        Returns:
            Datos estructurados del CDR
        """
        try:
            print(f"[CdrProcessor] Parseando XML CDR ({len(cdr_xml)} caracteres)")
            
            # Parsear XML
            root = etree.fromstring(cdr_xml.encode('utf-8'))
            
            # Namespaces para CDR
            namespaces = {
                'ar': 'urn:oasis:names:specification:ubl:schema:xsd:ApplicationResponse-2',
                'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
                'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2'
            }
            
            # Extraer información básica
            cdr_data = {
                'document_type': 'ApplicationResponse',
                'ubl_version': CdrProcessor._get_text(root, './/cbc:UBLVersionID', namespaces),
                'customization_id': CdrProcessor._get_text(root, './/cbc:CustomizationID', namespaces),
                'id': CdrProcessor._get_text(root, './/cbc:ID', namespaces),
                'issue_date': CdrProcessor._get_text(root, './/cbc:IssueDate', namespaces),
                'issue_time': CdrProcessor._get_text(root, './/cbc:IssueTime', namespaces),
            }
            
            # Información del emisor (SUNAT)
            supplier_party = root.xpath('.//cac:SenderParty', namespaces=namespaces)
            if supplier_party:
                cdr_data['sender'] = {
                    'ruc': CdrProcessor._get_text(supplier_party[0], './/cbc:ID[@schemeID="6"]', namespaces),
                    'name': CdrProcessor._get_text(supplier_party[0], './/cbc:Name', namespaces),
                }
            
            # Información del receptor (emisor original)
            customer_party = root.xpath('.//cac:ReceiverParty', namespaces=namespaces)
            if customer_party:
                cdr_data['receiver'] = {
                    'ruc': CdrProcessor._get_text(customer_party[0], './/cbc:ID[@schemeID="6"]', namespaces),
                    'name': CdrProcessor._get_text(customer_party[0], './/cbc:Name', namespaces),
                }
            
            # Referencia al documento original
            doc_reference = root.xpath('.//cac:DocumentReference', namespaces=namespaces)
            if doc_reference:
                cdr_data['document_reference'] = {
                    'id': CdrProcessor._get_text(doc_reference[0], './/cbc:ID', namespaces),
                    'document_type_code': CdrProcessor._get_text(doc_reference[0], './/cbc:DocumentTypeCode', namespaces),
                }
            
            # Respuesta de SUNAT (lo más importante)
            cdr_data['responses'] = []
            document_responses = root.xpath('.//cac:DocumentResponse', namespaces=namespaces)
            
            for doc_response in document_responses:
                response_data = {
                    'response_code': CdrProcessor._get_text(doc_response, './/cac:Response/cbc:ResponseCode', namespaces),
                    'description': CdrProcessor._get_text(doc_response, './/cac:Response/cbc:Description', namespaces),
                }
                
                # Estado del documento
                doc_reference_resp = doc_response.xpath('.//cac:DocumentReference', namespaces=namespaces)
                if doc_reference_resp:
                    response_data['document_reference'] = {
                        'id': CdrProcessor._get_text(doc_reference_resp[0], './/cbc:ID', namespaces),
                        'document_type_code': CdrProcessor._get_text(doc_reference_resp[0], './/cbc:DocumentTypeCode', namespaces),
                    }
                
                cdr_data['responses'].append(response_data)
            
            # Determinar estado general
            cdr_data['success'] = CdrProcessor._determine_success(cdr_data['responses'])
            if cdr_data['responses']:
                cdr_data['response_code'] = cdr_data['responses'][0]['response_code']
                cdr_data['response_description'] = cdr_data['responses'][0]['description']
            
            # Notas adicionales
            notes = root.xpath('.//cbc:Note', namespaces=namespaces)
            if notes:
                cdr_data['notes'] = [note.text for note in notes if note.text]
            
            print(f"[CdrProcessor] CDR parseado - Código: {cdr_data.get('response_code')}, Éxito: {cdr_data.get('success')}")
            return cdr_data
            
        except Exception as e:
            raise CdrProcessorError(f"Error parseando XML CDR: {e}")
    
    @staticmethod
    def _get_text(element, xpath: str, namespaces: Dict[str, str]) -> Optional[str]:
        """
        Obtiene texto de elemento usando XPath.
        
        Args:
            element: Elemento XML
            xpath: XPath del elemento
            namespaces: Namespaces XML
            
        Returns:
            Texto del elemento o None
        """
        try:
            result = element.xpath(xpath, namespaces=namespaces)
            return result[0].text if result and result[0].text else None
        except:
            return None
    
    @staticmethod
    def _determine_success(responses: List[Dict[str, Any]]) -> bool:
        """
        Determina si el CDR indica éxito basado en códigos de respuesta.
        
        Códigos SUNAT:
        - 0: Aceptado
        - 98: En proceso
        - Otros: Error o rechazo
        
        Args:
            responses: Lista de respuestas del CDR
            
        Returns:
            True si es exitoso
        """
        if not responses:
            return False
        
        # Verificar códigos de éxito conocidos
        success_codes = ['0', '98']  # 0=Aceptado, 98=En proceso
        
        for response in responses:
            response_code = response.get('response_code', '')
            if response_code not in success_codes:
                return False
        
        return True
    
    @staticmethod
    def save_cdr(cdr_base64: str, output_path: str) -> None:
        """
        Guarda CDR como archivo ZIP.
        
        Args:
            cdr_base64: CDR codificado en base64
            output_path: Ruta donde guardar
            
        Raises:
            CdrProcessorError: Si hay error guardando
        """
        try:
            print(f"[CdrProcessor] Guardando CDR en: {output_path}")
            
            # Decodificar y guardar
            cdr_bytes = base64.b64decode(cdr_base64)
            ZipHelper.save_zip_file(cdr_bytes, output_path)
            
            print(f"[CdrProcessor] CDR guardado exitosamente")
            
        except Exception as e:
            error_msg = f"Error guardando CDR: {e}"
            print(f"[CdrProcessor] ERROR: {error_msg}")
            raise CdrProcessorError(error_msg)
    
    @staticmethod
    def extract_cdr_xml(cdr_base64: str, output_path: str) -> str:
        """
        Extrae y guarda XML del CDR.
        
        Args:
            cdr_base64: CDR codificado en base64
            output_path: Ruta donde guardar XML
            
        Returns:
            Contenido del XML
            
        Raises:
            CdrProcessorError: Si hay error extrayendo
        """
        try:
            print(f"[CdrProcessor] Extrayendo XML CDR a: {output_path}")
            
            # Decodificar ZIP
            cdr_bytes = base64.b64decode(cdr_base64)
            
            # Extraer XML
            cdr_xml = ZipHelper.extract_xml_from_zip(cdr_bytes)
            if not cdr_xml:
                raise CdrProcessorError("CDR no contiene archivo XML")
            
            # Guardar XML
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(cdr_xml)
            
            print(f"[CdrProcessor] XML CDR guardado exitosamente ({len(cdr_xml)} caracteres)")
            return cdr_xml
            
        except Exception as e:
            error_msg = f"Error extrayendo XML CDR: {e}"
            print(f"[CdrProcessor] ERROR: {error_msg}")
            raise CdrProcessorError(error_msg)
    
    @staticmethod
    def is_success_response(response_code: str) -> bool:
        """
        Verifica si un código de respuesta indica éxito.
        
        Args:
            response_code: Código de respuesta SUNAT
            
        Returns:
            True si indica éxito
        """
        success_codes = ['0', '98']  # 0=Aceptado, 98=En proceso
        return response_code in success_codes
    
    @staticmethod
    def get_response_description(response_code: str) -> str:
        """
        Obtiene descripción de código de respuesta.
        
        Args:
            response_code: Código de respuesta SUNAT
            
        Returns:
            Descripción del código
        """
        descriptions = {
            '0': 'Aceptado',
            '98': 'En proceso',
            '99': 'En proceso',
            '0001': 'Rechazado',
            '0002': 'Rechazado - Error en RUC del emisor',
            '0003': 'Rechazado - Error en tipo de documento',
            '0004': 'Rechazado - Error en número de documento'
        }
        
        return descriptions.get(response_code, f'Código desconocido: {response_code}')