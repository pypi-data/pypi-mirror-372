"""Builder que integra generación y firma de XML."""

from pathlib import Path
from typing import Optional, Dict, Any

from ...sunat.certificate_manager import CertificateManager
from ...sunat.xml_signer import XmlSigner, XmlSignerError
from ...sunat.bill_sender import BillSender, BillSenderError
from ..models.invoice import Invoice
from ..models.note import Note
from .invoice_builder import InvoiceBuilder
from .note_builder import NoteBuilder
from .xml_builder import XmlBuilderError


class SignedXmlBuilderError(Exception):
    """Error en la construcción y firma de XML."""
    pass


class SignedXmlBuilder:
    """Builder que genera, firma y envía XMLs a SUNAT."""
    
    def __init__(self, cert_path: Optional[str] = None, cert_password: Optional[str] = None):
        """
        Inicializa el builder con firma.
        
        Args:
            cert_path: Ruta al certificado
            cert_password: Contraseña del certificado
        """
        self.invoice_builder = InvoiceBuilder()
        self.note_builder = NoteBuilder()
        self.xml_signer = XmlSigner()
        self.bill_sender = None  # Se inicializa con set_sunat_credentials
        
        # Cargar certificado si se proporciona
        if cert_path:
            self.load_certificate(cert_path, cert_password)
        
        print("[SignedXmlBuilder] Inicializado")
    
    def load_certificate(self, cert_path: str, password: Optional[str] = None) -> bool:
        """
        Carga certificado para firma.
        
        Args:
            cert_path: Ruta al certificado
            password: Contraseña del certificado
            
        Returns:
            True si se carga exitosamente
        """
        try:
            success = self.xml_signer.load_certificate(cert_path, password)
            if success:
                print(f"[SignedXmlBuilder] Certificado cargado: {cert_path}")
            return success
        except Exception as e:
            raise SignedXmlBuilderError(f"Error cargando certificado: {e}")
    
    def build_and_sign(self, document) -> str:
        """
        Genera y firma XML en un solo paso.
        
        Args:
            document: Documento a procesar (Invoice, Note)
            
        Returns:
            XML firmado como string
            
        Raises:
            SignedXmlBuilderError: Si hay error en generación o firma
        """
        try:
            print(f"[SignedXmlBuilder] Procesando: {document.get_nombre()}")
            
            # Paso 1: Generar XML sin firmar
            xml_unsigned = self._generate_xml(document)
            print(f"[SignedXmlBuilder] XML generado: {len(xml_unsigned)} caracteres")
            
            # Paso 2: Firmar XML
            xml_signed = self._sign_xml(xml_unsigned)
            print(f"[SignedXmlBuilder] XML firmado: {len(xml_signed)} caracteres")
            
            return xml_signed
            
        except Exception as e:
            error_msg = f"Error procesando documento {document.get_nombre()}: {e}"
            print(f"[SignedXmlBuilder] ERROR: {error_msg}")
            raise SignedXmlBuilderError(error_msg)
    
    def _generate_xml(self, document) -> str:
        """
        Genera XML sin firmar según el tipo de documento.
        
        Args:
            document: Documento a procesar
            
        Returns:
            XML sin firmar
        """
        try:
            if isinstance(document, Invoice):
                return self.invoice_builder.build(document)
            elif isinstance(document, Note):
                return self.note_builder.build(document)
            else:
                raise SignedXmlBuilderError(f"Tipo de documento no soportado: {type(document)}")
                
        except XmlBuilderError as e:
            raise SignedXmlBuilderError(f"Error generando XML: {e}")
    
    def _sign_xml(self, xml_content: str) -> str:
        """
        Firma el XML generado.
        
        Args:
            xml_content: XML a firmar
            
        Returns:
            XML firmado
        """
        try:
            if not self.xml_signer.certificate_manager.is_ready_for_signing():
                raise SignedXmlBuilderError("No hay certificado cargado para firma")
            
            return self.xml_signer.sign_xml(xml_content)
            
        except XmlSignerError as e:
            raise SignedXmlBuilderError(f"Error firmando XML: {e}")
    
    def build_sign_and_save(self, document, output_path: str) -> str:
        """
        Genera, firma y guarda XML en un archivo.
        
        Args:
            document: Documento a procesar
            output_path: Ruta donde guardar el XML firmado
            
        Returns:
            XML firmado como string
        """
        try:
            # Generar y firmar
            xml_signed = self.build_and_sign(document)
            
            # Crear directorio si no existe
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Guardar archivo
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(xml_signed)
            
            print(f"[SignedXmlBuilder] XML firmado guardado en: {output_path}")
            return xml_signed
            
        except Exception as e:
            raise SignedXmlBuilderError(f"Error guardando XML firmado: {e}")
    
    def verify_signed_xml(self, signed_xml: str) -> bool:
        """
        Verifica la firma de un XML.
        
        Args:
            signed_xml: XML firmado a verificar
            
        Returns:
            True si la firma es válida
        """
        try:
            return self.xml_signer.verify_xml_signature(signed_xml)
        except XmlSignerError as e:
            raise SignedXmlBuilderError(f"Error verificando firma: {e}")
    
    def get_certificate_info(self) -> dict:
        """
        Obtiene información del certificado cargado.
        
        Returns:
            Información del certificado
        """
        return self.xml_signer.get_certificate_info()
    
    def is_ready_for_signing(self) -> bool:
        """
        Verifica si está listo para firmar documentos.
        
        Returns:
            True si puede firmar
        """
        return self.xml_signer.certificate_manager.is_ready_for_signing()
    
    def set_sunat_credentials(self, username: str, password: str, endpoint: Optional[str] = None) -> None:
        """
        Configura credenciales para envío a SUNAT.
        
        Args:
            username: Usuario SUNAT (RUC + usuario)
            password: Contraseña SUNAT
            endpoint: URL del endpoint (opcional)
        """
        try:
            self.bill_sender = BillSender(username, password, endpoint)
            print(f"[SignedXmlBuilder] Credenciales SUNAT configuradas para: {username}")
        except Exception as e:
            raise SignedXmlBuilderError(f"Error configurando credenciales SUNAT: {e}")
    
    def build_sign_and_send(self, document) -> Dict[str, Any]:
        """
        Genera, firma y envía documento a SUNAT en un solo proceso.
        
        Args:
            document: Documento a procesar (Invoice, Note)
            
        Returns:
            Respuesta del envío incluyendo CDR
            
        Raises:
            SignedXmlBuilderError: Si hay error en cualquier paso
        """
        try:
            if not self.bill_sender:
                raise SignedXmlBuilderError("Credenciales SUNAT no configuradas. Use set_sunat_credentials()")
            
            print(f"[SignedXmlBuilder] Procesando y enviando: {document.get_nombre()}")
            
            # Paso 1: Generar y firmar XML
            xml_signed = self.build_and_sign(document)
            
            # Paso 2: Enviar a SUNAT
            result = self.bill_sender.send_document(
                ruc=document.company.ruc,
                tipo_doc=document.tipo_doc,
                serie=document.serie,
                correlativo=document.correlativo,
                signed_xml=xml_signed
            )
            
            # Agregar información del documento
            result['document_info'] = {
                'name': document.get_nombre(),
                'xml_size': len(xml_signed),
                'xml_signed': xml_signed
            }
            
            print(f"[SignedXmlBuilder] Envío completado - Éxito: {result.get('success')}")
            return result
            
        except (BillSenderError, SignedXmlBuilderError):
            raise
        except Exception as e:
            error_msg = f"Error en proceso completo para {document.get_nombre()}: {e}"
            print(f"[SignedXmlBuilder] ERROR: {error_msg}")
            raise SignedXmlBuilderError(error_msg)
    
    def build_sign_save_and_send(self, document, output_path: str) -> Dict[str, Any]:
        """
        Genera, firma, guarda y envía documento completo.
        
        Args:
            document: Documento a procesar
            output_path: Ruta donde guardar XML firmado
            
        Returns:
            Respuesta del envío incluyendo CDR
        """
        try:
            # Paso 1: Generar, firmar y guardar
            xml_signed = self.build_sign_and_save(document, output_path)
            
            # Paso 2: Enviar si hay credenciales configuradas
            if self.bill_sender:
                result = self.bill_sender.send_document(
                    ruc=document.company.ruc,
                    tipo_doc=document.tipo_doc,
                    serie=document.serie,
                    correlativo=document.correlativo,
                    signed_xml=xml_signed
                )
                
                result['document_info'] = {
                    'name': document.get_nombre(),
                    'xml_size': len(xml_signed),
                    'saved_path': output_path,
                    'xml_signed': xml_signed
                }
                
                return result
            else:
                return {
                    'success': True,
                    'action': 'build_sign_save',
                    'document_info': {
                        'name': document.get_nombre(),
                        'xml_size': len(xml_signed),
                        'saved_path': output_path,
                        'xml_signed': xml_signed
                    },
                    'message': 'XML generado y guardado. Configure credenciales SUNAT para enviar.'
                }
                
        except Exception as e:
            error_msg = f"Error en proceso completo con guardado para {document.get_nombre()}: {e}"
            print(f"[SignedXmlBuilder] ERROR: {error_msg}")
            raise SignedXmlBuilderError(error_msg)
    
    def is_ready_for_sending(self) -> bool:
        """
        Verifica si está listo para enviar a SUNAT.
        
        Returns:
            True si puede enviar
        """
        return (self.is_ready_for_signing() and 
                self.bill_sender is not None)
    
    def get_sunat_info(self) -> Optional[Dict[str, str]]:
        """
        Obtiene información de configuración SUNAT.
        
        Returns:
            Información de SUNAT o None si no está configurado
        """
        if self.bill_sender:
            return self.bill_sender.get_sender_info()
        return None
    
    def validate_sunat_connection(self) -> bool:
        """
        Valida conexión y credenciales SUNAT.
        
        Returns:
            True si la conexión es válida
        """
        try:
            if not self.bill_sender:
                print("[SignedXmlBuilder] No hay credenciales SUNAT configuradas")
                return False
            
            return self.bill_sender.validate_credentials()
            
        except Exception as e:
            print(f"[SignedXmlBuilder] Error validando conexión SUNAT: {e}")
            return False