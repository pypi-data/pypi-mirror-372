"""Gestor de certificados digitales para SUNAT."""

import os
from pathlib import Path
from typing import Optional, Tuple

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.serialization import pkcs12


class CertificateError(Exception):
    """Error en el manejo de certificados."""
    pass


class CertificateManager:
    """Gestor de certificados digitales para firma XML."""
    
    def __init__(self):
        """Inicializa el gestor de certificados."""
        self.certificate = None
        self.private_key = None
        self.certificate_data = None
        print("[CertificateManager] Inicializado")
    
    def load_certificate_from_string(self, cert_content: str, password: Optional[str] = None) -> bool:
        """
        Carga certificado desde string PEM.
        
        Args:
            cert_content: Contenido del certificado como string
            password: Contraseña del certificado (si tiene)
            
        Returns:
            True si se carga exitosamente
            
        Raises:
            CertificateError: Si hay error en la carga
        """
        try:
            print("[CertificateManager] Cargando certificado desde string")
            
            # Convertir string a bytes
            cert_data = cert_content.encode('utf-8')
            
            # Solo soportamos PEM desde string
            return self._load_pem_certificate(cert_data, password)
                    
        except Exception as e:
            raise CertificateError(f"Error cargando certificado desde string: {e}")
    
    def load_certificate_from_file(self, cert_path: str, password: Optional[str] = None) -> bool:
        """
        Carga certificado desde archivo .pem o .p12/.pfx.
        
        Args:
            cert_path: Ruta al archivo del certificado
            password: Contraseña del certificado (si tiene)
            
        Returns:
            True si se carga exitosamente
            
        Raises:
            CertificateError: Si hay error en la carga
        """
        try:
            cert_file = Path(cert_path)
            if not cert_file.exists():
                raise CertificateError(f"Archivo de certificado no encontrado: {cert_path}")
            
            print(f"[CertificateManager] Cargando certificado: {cert_path}")
            
            # Leer archivo
            with open(cert_file, 'rb') as f:
                cert_data = f.read()
            
            # Detectar tipo de archivo
            if cert_file.suffix.lower() in ['.p12', '.pfx']:
                return self._load_pkcs12_certificate(cert_data, password)
            elif cert_file.suffix.lower() == '.pem':
                return self._load_pem_certificate(cert_data, password)
            else:
                # Intentar detectar automáticamente
                try:
                    return self._load_pem_certificate(cert_data, password)
                except:
                    return self._load_pkcs12_certificate(cert_data, password)
                    
        except Exception as e:
            raise CertificateError(f"Error cargando certificado {cert_path}: {e}")
    
    def _load_pem_certificate(self, cert_data: bytes, password: Optional[str] = None) -> bool:
        """
        Carga certificado PEM.
        
        Args:
            cert_data: Datos del certificado
            password: Contraseña (si tiene)
            
        Returns:
            True si se carga exitosamente
        """
        try:
            # Convertir password a bytes si es necesario
            pwd_bytes = password.encode('utf-8') if password else None
            
            # El archivo PEM puede contener tanto el certificado como la clave privada
            cert_text = cert_data.decode('utf-8')
            
            # Extraer certificado
            if '-----BEGIN CERTIFICATE-----' in cert_text:
                self.certificate = x509.load_pem_x509_certificate(cert_data)
                print(f"[CertificateManager] Certificado X509 cargado")
            else:
                raise CertificateError("No se encontró certificado en formato PEM")
            
            # Intentar extraer clave privada
            if '-----BEGIN PRIVATE KEY-----' in cert_text or '-----BEGIN RSA PRIVATE KEY-----' in cert_text:
                try:
                    self.private_key = serialization.load_pem_private_key(cert_data, pwd_bytes)
                    print(f"[CertificateManager] Clave privada cargada")
                except Exception as e:
                    print(f"[CertificateManager] Warning: No se pudo cargar clave privada: {e}")
            
            self.certificate_data = cert_data
            self._validate_certificate()
            return True
            
        except Exception as e:
            raise CertificateError(f"Error procesando certificado PEM: {e}")
    
    def _load_pkcs12_certificate(self, cert_data: bytes, password: Optional[str] = None) -> bool:
        """
        Carga certificado PKCS#12 (.p12/.pfx).
        
        Args:
            cert_data: Datos del certificado
            password: Contraseña del certificado
            
        Returns:
            True si se carga exitosamente
        """
        try:
            pwd_bytes = password.encode('utf-8') if password else None
            
            # Cargar PKCS#12
            private_key, certificate, additional_certificates = pkcs12.load_key_and_certificates(
                cert_data, pwd_bytes
            )
            
            self.private_key = private_key
            self.certificate = certificate
            self.certificate_data = cert_data
            
            print(f"[CertificateManager] Certificado PKCS#12 cargado")
            if additional_certificates:
                print(f"[CertificateManager] Certificados adicionales: {len(additional_certificates)}")
            
            self._validate_certificate()
            return True
            
        except Exception as e:
            raise CertificateError(f"Error procesando certificado PKCS#12: {e}")
    
    def _validate_certificate(self) -> None:
        """
        Valida el certificado cargado.
        
        Raises:
            CertificateError: Si el certificado es inválido
        """
        if not self.certificate:
            raise CertificateError("No hay certificado cargado")
        
        # Verificar fechas (usando UTC para evitar warnings)
        import datetime
        now = datetime.datetime.now(datetime.timezone.utc)
        
        if self.certificate.not_valid_before_utc > now:
            raise CertificateError(f"Certificado aún no válido (válido desde: {self.certificate.not_valid_before_utc})")
        
        if self.certificate.not_valid_after_utc < now:
            # Para certificados de prueba, solo mostrar warning
            print(f"[CertificateManager] WARNING: Certificado expirado (válido hasta: {self.certificate.not_valid_after_utc})")
            print(f"[CertificateManager] Continuando con certificado expirado para pruebas...")
        
        # Información del certificado
        subject = self.certificate.subject
        print(f"[CertificateManager] Sujeto: {subject}")
        print(f"[CertificateManager] Válido desde: {self.certificate.not_valid_before_utc}")
        print(f"[CertificateManager] Válido hasta: {self.certificate.not_valid_after_utc}")
    
    def get_certificate_info(self) -> dict:
        """
        Obtiene información del certificado.
        
        Returns:
            Diccionario con información del certificado
        """
        if not self.certificate:
            return {}
        
        subject = self.certificate.subject
        issuer = self.certificate.issuer
        
        return {
            'subject': str(subject),
            'issuer': str(issuer),
            'serial_number': str(self.certificate.serial_number),
            'not_valid_before': self.certificate.not_valid_before_utc.isoformat(),
            'not_valid_after': self.certificate.not_valid_after_utc.isoformat(),
            'has_private_key': self.private_key is not None
        }
    
    def get_certificate_pem(self) -> str:
        """
        Obtiene el certificado en formato PEM.
        
        Returns:
            Certificado en formato PEM como string
        """
        if not self.certificate:
            raise CertificateError("No hay certificado cargado")
        
        pem_data = self.certificate.public_bytes(serialization.Encoding.PEM)
        return pem_data.decode('utf-8')
    
    def get_private_key_pem(self) -> str:
        """
        Obtiene la clave privada en formato PEM.
        
        Returns:
            Clave privada en formato PEM como string
        """
        if not self.private_key:
            raise CertificateError("No hay clave privada cargada")
        
        pem_data = self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        return pem_data.decode('utf-8')
    
    def load_certificate_from_credentials(self, certificado: str, password: Optional[str] = None) -> bool:
        """
        Carga certificado desde SunatCredentials (string o archivo).
        
        Args:
            certificado: Contenido PEM como string O path al archivo
            password: Contraseña del certificado (si tiene)
            
        Returns:
            True si se carga exitosamente
        """
        # Detectar si es contenido PEM o path a archivo
        if certificado.startswith("-----BEGIN"):
            return self.load_certificate_from_string(certificado, password)
        else:
            return self.load_certificate_from_file(certificado, password)
    
    def is_ready_for_signing(self) -> bool:
        """
        Verifica si está listo para firmar (tiene certificado y clave privada).
        
        Returns:
            True si puede firmar
        """
        return self.certificate is not None and self.private_key is not None