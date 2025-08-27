"""Tests para manejo de certificados."""

import pytest
from pathlib import Path

from cpe_engine.sunat.certificate_manager import CertificateManager, CertificateError
from cpe_engine.sunat.credentials import SunatCredentials


class TestCertificateManager:
    """Tests para CertificateManager."""
    
    def test_inicializacion(self):
        """Test inicialización básica."""
        cert_manager = CertificateManager()
        
        assert cert_manager.certificate is None
        assert cert_manager.private_key is None
        assert not cert_manager.is_ready_for_signing()
    
    def test_cargar_certificado_desde_string(self):
        """Test cargar certificado desde string PEM."""
        cert_manager = CertificateManager()
        
        # PEM de ejemplo (no válido, solo para test)
        pem_content = """-----BEGIN CERTIFICATE-----
MIICljCCAX4CAQEwDQYJKoZIhvcNAQELBQAwEjEQMA4GA1UEAwwHVGVzdCBDQTAe
Fw0yMzAxMDEwMDAwMDBaFw0yNDEyMzEyMzU5NTlaMBIxEDAOBgNVBAMMB1Rlc3Qg
Q0EwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQC5example
-----END CERTIFICATE-----
-----BEGIN PRIVATE KEY-----
MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC5example
-----END PRIVATE KEY-----"""
        
        # Debería manejar el error de certificado inválido
        with pytest.raises(CertificateError):
            cert_manager.load_certificate_from_string(pem_content)
    
    def test_cargar_certificado_archivo_inexistente(self):
        """Test cargar certificado de archivo que no existe."""
        cert_manager = CertificateManager()
        
        with pytest.raises(CertificateError, match="Archivo de certificado no encontrado"):
            cert_manager.load_certificate_from_file("archivo_inexistente.pem")
    
    def test_validaciones_credenciales(self):
        """Test validaciones de SunatCredentials."""
        # Certificado como string
        creds = SunatCredentials(
            ruc="20000000001",
            usuario="20000000001MODDATOS",
            password="test123",
            certificado="-----BEGIN CERTIFICATE-----\ntest\n-----END CERTIFICATE-----"
        )
        
        assert not creds.es_certificado_archivo
        assert creds.contenido_certificado.startswith("-----BEGIN")
        
        # Certificado como archivo
        creds_file = SunatCredentials(
            ruc="20000000001",
            usuario="20000000001MODDATOS", 
            password="test123",
            certificado="/path/to/cert.pem"
        )
        
        assert creds_file.es_certificado_archivo
    
    def test_cargar_desde_credenciales_string(self):
        """Test cargar certificado usando SunatCredentials con string."""
        cert_manager = CertificateManager()
        
        pem_content = "-----BEGIN CERTIFICATE-----\ninvalid\n-----END CERTIFICATE-----"
        
        # Debería detectar que es un string y intentar cargarlo
        with pytest.raises(CertificateError):
            cert_manager.load_certificate_from_credentials(pem_content)
    
    def test_cargar_desde_credenciales_archivo(self):
        """Test cargar certificado usando SunatCredentials con archivo."""
        cert_manager = CertificateManager()
        
        file_path = "/path/to/cert.pem"
        
        # Debería detectar que es un archivo e intentar cargarlo
        with pytest.raises(CertificateError):
            cert_manager.load_certificate_from_credentials(file_path)


class TestSunatCredentialsValidation:
    """Tests para validación de SunatCredentials."""
    
    def test_validacion_certificado_pem_valido(self):
        """Test validación de certificado PEM válido."""
        # Este es un certificado real de ejemplo (sin clave privada)
        pem_real = """-----BEGIN CERTIFICATE-----
MIICpjCCAY4CAQAwDQYJKoZIhvcNAQELBQAwEjEQMA4GA1UEAwwHVGVzdCBDQTAe
Fw0yMzEwMDEwMDAwMDBaFw0yNDEyMzEyMzU5NTlaMBIxEDAOBgNVBAMMB1Rlc3Qg
Q0EwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQDH1234567890abcdef
ghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890abcdef
-----END CERTIFICATE-----"""
        
        creds = SunatCredentials(
            ruc="20000000001",
            usuario="20000000001MODDATOS",
            password="test123",
            certificado=pem_real
        )
        
        # Debería reconocer el formato PEM básico
        assert creds.validar_certificado() is True
    
    def test_validacion_certificado_invalido(self):
        """Test validación de certificado inválido."""
        creds = SunatCredentials(
            ruc="20000000001",
            usuario="20000000001MODDATOS",
            password="test123",
            certificado="certificado_invalido"
        )
        
        assert creds.validar_certificado() is False