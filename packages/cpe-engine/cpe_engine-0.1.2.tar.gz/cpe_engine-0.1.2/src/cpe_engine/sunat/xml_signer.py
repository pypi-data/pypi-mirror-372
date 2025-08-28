"""Firmador de XML usando signxml para SUNAT."""

from typing import Optional

from lxml import etree
from signxml import XMLSigner, XMLVerifier
from signxml.algorithms import SignatureConstructionMethod, SignatureMethod, DigestAlgorithm, CanonicalizationMethod
import hashlib
import base64

from .certificate_manager import CertificateManager, CertificateError


class XmlSignerError(Exception):
    """Error en la firma de XML."""
    pass


class XmlSigner:
    """Firmador de XML para documentos electrónicos SUNAT."""
    
    def __init__(self, certificate_manager: Optional[CertificateManager] = None):
        """
        Inicializa el firmador XML.
        
        Args:
            certificate_manager: Gestor de certificados
        """
        self.certificate_manager = certificate_manager or CertificateManager()
        print("[XmlSigner] Inicializado")
    
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
            return self.certificate_manager.load_certificate_from_file(cert_path, password)
        except CertificateError as e:
            raise XmlSignerError(f"Error cargando certificado: {e}")
    
    def sign_xml(self, xml_content: str) -> str:
        """
        Firma un XML usando el certificado cargado.
        Enfoque simplificado: Firma tradicional con SHA-1 como espera SUNAT.

        Args:
            xml_content: XML a firmar como string
            
        Returns:
            XML firmado como string
            
        Raises:
            XmlSignerError: Si hay error en la firma
        """
        try:
            if not self.certificate_manager.is_ready_for_signing():
                raise XmlSignerError("No hay certificado o clave privada cargada")
            
            print(f"[XmlSigner] Iniciando firma de XML ({len(xml_content)} caracteres)")
            
            # Parsear XML original
            try:
                xml_doc = etree.fromstring(xml_content.encode('utf-8'))
            except etree.XMLSyntaxError as e:
                raise XmlSignerError(f"XML inválido: {e}")
            
            # Encontrar ExtensionContent
            extension_content = xml_doc.find('.//{urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2}ExtensionContent')
            if extension_content is None:
                raise XmlSignerError("No se encontró elemento ExtensionContent en el XML")
            
            # Limpiar ExtensionContent
            extension_content.clear()
            
            # Configurar firmador con SHA-1 como usa Greenter
            try:
                # Intentar habilitar algoritmos legacy
                from signxml.util import force_enable_legacy_algorithms
                force_enable_legacy_algorithms()
                
                signer = XMLSigner(
                    method=SignatureConstructionMethod.enveloped,
                    signature_algorithm=SignatureMethod.RSA_SHA1,
                    digest_algorithm=DigestAlgorithm.SHA1,
                    c14n_algorithm=CanonicalizationMethod.CANONICAL_XML_1_0
                )
                print("[XmlSigner] Usando SHA-1 (legacy) como Greenter")
            except Exception as e:
                # SHA-1 no disponible, usando SHA-256 (más seguro)
                signer = XMLSigner(
                    method=SignatureConstructionMethod.enveloped,
                    signature_algorithm=SignatureMethod.RSA_SHA256,
                    digest_algorithm=DigestAlgorithm.SHA256,
                    c14n_algorithm=CanonicalizationMethod.CANONICAL_XML_1_0
                )
            
            # Preparar certificado
            cert_chain = [self.certificate_manager.certificate]
            
            # Firmar el documento
            signed_doc = signer.sign(
                xml_doc,
                key=self.certificate_manager.private_key,
                cert=cert_chain
            )
            
            # Buscar la firma generada
            signature_elem = signed_doc.find('.//{http://www.w3.org/2000/09/xmldsig#}Signature')
            if signature_elem is None:
                raise XmlSignerError("No se pudo generar la firma")
            
            # Configurar ID correcto
            signature_elem.set('Id', 'GreenterSign')
            
            # Mover la firma a ExtensionContent
            signature_parent = signature_elem.getparent()
            if signature_parent is not None:
                signature_parent.remove(signature_elem)
            
            # Encontrar ExtensionContent en documento firmado
            ext_content = signed_doc.find('.//{urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2}ExtensionContent')
            if ext_content is not None:
                ext_content.clear()
                ext_content.append(signature_elem)
            
            print("[XmlSigner] Firma movida a ExtensionContent")
            
            # Convertir a string
            signed_xml = etree.tostring(
                signed_doc, 
                encoding='utf-8', 
                xml_declaration=True,
                pretty_print=False
            ).decode('utf-8')
            
            print(f"[XmlSigner] XML firmado exitosamente ({len(signed_xml)} caracteres)")
            
            # Validar estructura básica
            self._validate_signed_xml(signed_xml)
            
            return signed_xml
            
        except Exception as e:
            error_msg = f"Error firmando XML: {e}"
            print(f"[XmlSigner] ERROR: {error_msg}")
            raise XmlSignerError(error_msg)
    
    def _validate_signed_xml(self, signed_xml: str) -> None:
        """
        Valida que el XML esté correctamente firmado.

        Args:
            signed_xml: XML firmado
            
        Raises:
            XmlSignerError: Si la validación falla
        """
        try:
            # Verificar que contiene elementos de firma
            if '<ds:Signature' not in signed_xml:
                raise XmlSignerError("XML no contiene elemento Signature")
            
            if '<ds:SignedInfo' not in signed_xml:
                raise XmlSignerError("XML no contiene elemento SignedInfo")
                
            if '<ds:SignatureValue' not in signed_xml:
                raise XmlSignerError("XML no contiene elemento SignatureValue")
                
            print("[XmlSigner] Validación básica de firma: OK")
            
        except Exception as e:
            raise XmlSignerError(f"Error validando XML firmado: {e}")
    
    def verify_xml_signature(self, signed_xml: str) -> bool:
        """
        Verifica la firma de un XML.

        Args:
            signed_xml: XML firmado a verificar
            
        Returns:
            True si la firma es válida
            
        Raises:
            XmlSignerError: Si hay error en la verificación
        """
        try:
            print(f"[XmlSigner] Verificando firma XML ({len(signed_xml)} caracteres)")
            
            # Parsear XML firmado
            signed_doc = etree.fromstring(signed_xml.encode('utf-8'))
            
            # Crear verificador
            verifier = XMLVerifier()
            
            # Verificar firma
            verified_data = verifier.verify(signed_doc)
            
            print("[XmlSigner] Firma verificada exitosamente")
            return True
            
        except Exception as e:
            error_msg = f"Error verificando firma XML: {e}"
            print(f"[XmlSigner] ERROR: {error_msg}")
            raise XmlSignerError(error_msg)
    
    def sign_xml_file(self, input_path: str, output_path: str) -> str:
        """
        Firma un archivo XML y guarda el resultado.

        Args:
            input_path: Ruta al XML sin firmar
            output_path: Ruta donde guardar XML firmado
            
        Returns:
            XML firmado como string
        """
        try:
            # Leer archivo de entrada
            with open(input_path, 'r', encoding='utf-8') as f:
                xml_content = f.read()
            
            # Firmar XML
            signed_xml = self.sign_xml(xml_content)
            
            # Guardar archivo firmado
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(signed_xml)
            
            print(f"[XmlSigner] XML firmado guardado en: {output_path}")
            return signed_xml
            
        except Exception as e:
            raise XmlSignerError(f"Error procesando archivo XML: {e}")
    
    def get_certificate_info(self) -> dict:
        """
        Obtiene información del certificado cargado.

        Returns:
            Información del certificado
        """
        return self.certificate_manager.get_certificate_info()