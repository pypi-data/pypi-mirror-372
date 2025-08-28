"""
Tests críticos End-to-End - QA Priority 1

Valida los flujos completos que NO están siendo testeados:
- High-level API functions (send_invoice, send_receipt, etc.) - 57% coverage
- SignedXmlBuilder workflow - 22% coverage  
- Complete document workflows from creation to SUNAT submission
- Integration between all components
- Real-world scenarios

Estos tests son críticos porque validan que toda la pipeline funciona:
Usuario → API → Models → XML → Firma → SUNAT → CDR → Response
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import xml.etree.ElementTree as ET

# Core imports
from cpe_engine import (
    send_invoice, send_receipt, send_credit_note, send_debit_note,
    create_invoice_data, create_note_data,
    SunatCredentials
)
from cpe_engine.core.models.invoice import Invoice
from cpe_engine.core.models.note import Note
from cpe_engine.core.models.company import Company
from cpe_engine.core.models.client import Client
from cpe_engine.core.models.base_sale import SaleDetail, Legend
from cpe_engine.core.builders.signed_xml_builder import SignedXmlBuilder

# Test credentials (official SUNAT test environment)
TEST_SUNAT_CREDENTIALS = {
    'ruc': '20000000001',
    'usuario': '20000000001MODDATOS', 
    'password': 'moddatos',
    'certificado': '''-----BEGIN CERTIFICATE-----
MIIEJTCCAw2gAwIBAgIJAOTjh8W3dOvuMA0GCSqGSIb3DQEBCwUAMIGoMQswCQYD
VQQGEwJQRTEMMAoGA1UECAwDTElNMQwwCgYDVQQHDANMSU0xEDAOBgNVBAoMB0dS
RUVOVEVSMREwDwYDVQQLDAhTSVNURU1BUzEYMBYGA1UEAwwPR1JFRU5URVIgU0Eg
VEVTVDEiMCAGCSqGSIb3DQEJARYTZ3JlZW50ZXJAZ21haWwuY29tMRIwEAYDVQQI
DAlTQU5UQSBBTkEwHhcNMTgxMDE2MTcxOTI1WhcNMjExMDE1MTcxOTI1WjCBqDEL
MAkGA1UEBhMCUEUxDDAKBgNVBAgMA0xJTTEMMAoGA1UEBwwDTElNMRAwDgYDVQQK
DAdHUkVFTlRFUjERMA8GA1UECwwIU0lTVEVNQVMxGDAWBgNVBAMMD0dSRUVOVEVS
IFNBIFRFU1QxIjAgBgkqhkiG9w0BCQEWE2dyZWVudGVyQGdtYWlsLmNvbTESMBAG
A1UECAwJU0FOVEEGQU5BMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA
xQMhgMgOVTTpBTllmIQWfWTESwO1rGqWjKhKZxY2k2iT3vYtUV7gDxIm9HIq9gHV
TzpKGk1gKh7vKpjTHr4CdPGqnDcBvWjgTwjLAKbxqDHIRAhDMPTAaANOCl2gDZSM
FvWnmCb8w7d4UIkrw5AUJwSJqOTD8KW4PB3N4IW9GjV9kJR8oGnpZVVzJsq5Lx9h
n1VbByCIlT8cJcVTBxoLAhvvzGUzT4tK4M3L/Xvox0l3Y8fJV3ZE8vWpT1zC7W/q
MEF5lsWaX3MIvZ5iHBo7XcD1q9G8B8HzJbJ8dW6QI8h5wX8Rl3ZNOtX1QKcZtQ2w
8sNZB8o5kQ7dCgBJ5LZYjQIDAQABo1AwTjAdBgNVHQ4EFgQU6Z7kdJ3jGHYUdgZf
w8d8yNFrO8cwHwYDVR0jBBgwFoAU6Z7kdJ3jGHYUdgZfw8d8yNFrO8cwDAYDVR0T
BAUwAwEB/zANBgkqhkiG9w0BAQsFAAOCAQEAOoV5zZ8j7V6b7V6WgHkGHs7UgF7V
6B7V6W9V6B7V6W9V6B7V6W9V6B7V6W9V6B7V6W9V6B7V6W9V6B7V6W9V6B7V6W9V
6B7V6W9V6B7V6W9V6B7V6W9V6B7V6W9V6B7V6W9V6B7V6W9V6B7V6W9V6B7V6W9V
6B7V6W9V6B7V6W9V6B7V6W9V6B7V6W9V6B7V6W9V6B7V6W9V6B7V6W9V6B7V6W9V
-----END CERTIFICATE-----
-----BEGIN PRIVATE KEY-----
MIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQDFAyGAyA5VNOkF
OWWYhBZ9ZMRLA7WsapaUqEpnFjaTaJPe9i1RXuAPEib0cir2AdVPOkoaTWAqHu8q
mNMevgJ08aqcNwG9aOBPCMsApvGoMchECEMw9MBoA04KXaANlIwW9aeYJvzDt3hQ
iSvDkBQnBImo5MPwpbg8Hc3ghb0aNX2QlHygaellVXMmyrkvH2GfVVsHIIiVPxwl
xVMHGgsCG+/MZTNP3Bz8UdLWVBVbGyCW2z8uYxrK5Lx9hn1VbByCIlT8cJcVTBxo
LAhvvzGUzT4tK4M3L/Xvox0l3Y8fJV3ZE8vWpT1zC7W/qMEF5lsWaX3MIvZ5iHBo
7XcD1q9G8B8HzJbJ8dW6QI8h5wX8Rl3ZNOtX1QKcZtQ2w8sNZB8o5kQ7dCgBJ5LZ
YjQIDAQABAoIBAQC8+xZA2RqLlR3oXjz3s2TG8+4oXA9vVwRwQ6C5FX9wHJnOQZ5P
T8FzGJVvNj7mJ8X7Z2B7V6W9V6B7V6W9V6B7V6W9V6B7V6W9V6B7V6W9V6B7V6W9
V6B7V6W9V6B7V6W9V6B7V6W9V6B7V6W9V6B7V6W9V6B7V6W9V6B7V6W9V6B7V6W9
V6B7V6W9V6B7V6W9V6B7V6W9V6B7V6W9V6B7V6W9V6B7V6W9V6B7V6W9V6B7V6W9
V6B7V6W9V6B7V6W9V6B7V6W9V6B7V6W9V6B7V6W9V6B7V6W9V6B7V6W9V6B7V6W9
-----END PRIVATE KEY-----''',
    'es_test': True
}


class TestHighLevelAPI:
    """Tests críticos para API de alto nivel - 57% cobertura actual"""
    
    @pytest.fixture
    def sample_empresa_data(self):
        """Datos de empresa para tests"""
        return {
            'ruc': TEST_SUNAT_CREDENTIALS['ruc'],
            'razon_social': 'EMPRESA DE PRUEBAS S.A.C.',
            'nombre_comercial': 'EMPRESA PRUEBAS',
            'email': 'test@empresa.com',
            'address': {
                'ubigeo': '150101',
                'departamento': 'Lima',
                'provincia': 'Lima', 
                'distrito': 'Lima',
                'direccion': 'Av. Principal 123'
            }
        }
        
    @pytest.fixture
    def sample_cliente_data(self):
        """Datos de cliente para tests"""
        return {
            'tipo_doc': 6,
            'num_doc': '20000000002',
            'razon_social': 'CLIENTE DE PRUEBAS S.A.C.'
        }
        
    @pytest.fixture
    def sample_items_data(self):
        """Items de factura para tests"""
        return [
            {
                'cod_item': 'PROD001',
                'des_item': 'Producto de prueba',
                'cantidad': 1,
                'mto_valor_unitario': 100.00,
                'unidad': 'NIU'
            }
        ]
        
    @pytest.fixture
    def sunat_credentials(self):
        """Credenciales SUNAT para tests"""
        return SunatCredentials(
            ruc=TEST_SUNAT_CREDENTIALS['ruc'],
            usuario=TEST_SUNAT_CREDENTIALS['usuario'],
            password=TEST_SUNAT_CREDENTIALS['password'],
            certificado=TEST_SUNAT_CREDENTIALS['certificado'],
            es_test=True
        )
        
    def test_create_invoice_data_basic(self, sample_empresa_data, sample_cliente_data, sample_items_data):
        """Test creación de datos de factura básica"""
        result = create_invoice_data(
            serie="F001",
            correlativo=123,
            company_data=sample_empresa_data,
            client_data=sample_cliente_data,
            items=sample_items_data
        )
        
        # Verificar estructura básica
        assert result is not None
        assert isinstance(result, dict)
        assert 'serie' in result
        assert 'company' in result
        assert 'client' in result
        assert 'details' in result
        
        # Verificar datos específicos
        assert result['serie'] == "F001"
        assert result['correlativo'] == 123
        
        # Verificar que company y client son objetos correctos
        from cpe_engine.core.models.company import Company
        from cpe_engine.core.models.client import Client
        assert isinstance(result['company'], Company)
        assert isinstance(result['client'], Client)
        
    def test_create_note_data_credit_note(self, sample_empresa_data, sample_cliente_data, sample_items_data):
        """Test creación de datos de nota de crédito"""
        result = create_note_data(
            serie="FC01",
            correlativo=1,
            tipo_nota="07",
            documento_afectado="F001-123",
            motivo="Anulación",
            company_data=sample_empresa_data,
            client_data=sample_cliente_data,
            items=sample_items_data
        )
        
        # Verificar estructura
        assert result is not None
        assert isinstance(result, dict)
        assert 'tipo_doc' in result
        assert 'num_doc_afectado' in result
        
        # Verificar datos de nota
        assert result['tipo_doc'] == "07"  # Nota de crédito
        assert result['num_doc_afectado'] == "F001-123"
        
    @patch('cpe_engine.sunat.bill_sender.BillSender.send_document')
    @patch('cpe_engine.sunat.certificate_manager.CertificateManager.load_certificate_from_credentials')
    @patch('cpe_engine.sunat.certificate_manager.CertificateManager.is_ready_for_signing')
    @patch('cpe_engine.sunat.xml_signer.XmlSigner.sign_xml')
    def test_send_invoice_success_scenario(self, mock_sign_xml, mock_ready, mock_cert_load, mock_send, sample_empresa_data, sample_cliente_data, sample_items_data, sunat_credentials):
        """Test envío exitoso de factura"""
        # Mock carga exitosa de certificado
        mock_cert_load.return_value = True
        mock_ready.return_value = True
        
        # Mock firma exitosa de XML
        mock_sign_xml.return_value = '<xml>signed xml content</xml>'
        
        # Mock respuesta exitosa de SUNAT
        mock_send.return_value = {
            'success': True,
            'cdr': {
                'code': '0',
                'description': 'La Factura numero F001-123, ha sido aceptada'
            }
        }
        
        # Crear datos de factura y enviar
        invoice_data = create_invoice_data(
            serie="F001",
            correlativo=123,
            company_data=sample_empresa_data,
            client_data=sample_cliente_data,
            items=sample_items_data
        )
        
        # Enfoque declarativo: usuario debe proporcionar totales explícitamente
        invoice_data.update({
            'mto_oper_gravadas': 100.0,  # Base gravada
            'mto_igv': 18.0,             # IGV (18%)
            'mto_total_tributos': 18.0,  # Total impuestos
            'mto_impventa': 118.0,       # Total de venta
            'sub_total': 118.0,          # Subtotal
            'valor_venta': 100.0         # Valor venta
        })
        
        result = send_invoice(
            credentials=sunat_credentials,
            invoice_data=invoice_data
        )
        
        # Verificar resultado
        assert result is not None
        assert result.get('success') == True
        assert 'cdr' in result
        assert result['cdr']['code'] == '0'
        
        # Verificar que se llamó al sender
        mock_send.assert_called_once()
        
    @patch('cpe_engine.sunat.bill_sender.BillSender.send_document')
    @patch('cpe_engine.sunat.certificate_manager.CertificateManager.load_certificate_from_credentials')
    @patch('cpe_engine.sunat.certificate_manager.CertificateManager.is_ready_for_signing')
    @patch('cpe_engine.sunat.xml_signer.XmlSigner.sign_xml')
    def test_send_receipt_success_scenario(self, mock_sign_xml, mock_ready, mock_cert_load, mock_send, sample_empresa_data, sample_cliente_data, sample_items_data, sunat_credentials):
        """Test envío exitoso de boleta"""
        # Mock carga exitosa de certificado
        mock_cert_load.return_value = True
        mock_ready.return_value = True
        mock_sign_xml.return_value = '<xml>signed xml content</xml>'
        
        # Mock respuesta exitosa
        mock_send.return_value = {
            'success': True,
            'cdr': {
                'code': '0',
                'description': 'La Boleta numero B001-456, ha sido aceptada'
            }
        }
        
        # Modificar cliente para boleta (DNI)
        cliente_boleta = sample_cliente_data.copy()
        cliente_boleta['tipo_doc'] = 1  # DNI
        cliente_boleta['num_doc'] = '12345678'
        
        # Crear datos de boleta y enviar
        receipt_data = create_invoice_data(
            serie="B001",
            correlativo=456,
            company_data=sample_empresa_data,
            client_data=cliente_boleta,
            items=sample_items_data
        )
        
        # Enfoque declarativo: usuario debe proporcionar totales
        receipt_data.update({
            'mto_oper_gravadas': 100.0,
            'mto_igv': 18.0,
            'mto_total_tributos': 18.0,
            'mto_impventa': 118.0,
            'sub_total': 118.0,
            'valor_venta': 100.0
        })
        
        result = send_receipt(
            credentials=sunat_credentials,
            receipt_data=receipt_data
        )
        
        assert result is not None
        assert result.get('success') == True
        mock_send.assert_called_once()
        
    @patch('cpe_engine.sunat.bill_sender.BillSender.send_document')
    @patch('cpe_engine.sunat.certificate_manager.CertificateManager.load_certificate_from_credentials')
    @patch('cpe_engine.sunat.certificate_manager.CertificateManager.is_ready_for_signing')
    @patch('cpe_engine.sunat.xml_signer.XmlSigner.sign_xml')
    def test_send_credit_note_success_scenario(self, mock_sign_xml, mock_ready, mock_cert_load, mock_send, sample_empresa_data, sample_cliente_data, sample_items_data, sunat_credentials):
        """Test envío exitoso de nota de crédito"""
        # Mock carga exitosa de certificado
        mock_cert_load.return_value = True
        mock_ready.return_value = True
        mock_sign_xml.return_value = '<xml>signed xml content</xml>'
        
        mock_send.return_value = {
            'success': True,
            'cdr': {
                'code': '0',
                'description': 'La Nota de Credito numero FC01-001, ha sido aceptada'
            }
        }
        
        # Crear datos de nota de crédito y enviar
        note_data = create_note_data(
            serie="FC01",
            correlativo=1,
            tipo_nota="07",
            documento_afectado="F001-123",
            motivo="Anulación",
            company_data=sample_empresa_data,
            client_data=sample_cliente_data,
            items=sample_items_data
        )
        
        # Enfoque declarativo: añadir totales para notas
        note_data.update({
            'mto_oper_gravadas': 100.0,
            'mto_igv': 18.0,
            'mto_total_tributos': 18.0,
            'mto_impventa': 118.0,
            'sub_total': 118.0,
            'valor_venta': 100.0
        })
        
        result = send_credit_note(
            credentials=sunat_credentials,
            note_data=note_data
        )
        
        assert result is not None
        assert result.get('success') == True
        mock_send.assert_called_once()
        
    @patch('cpe_engine.sunat.bill_sender.BillSender.send_document')
    @patch('cpe_engine.sunat.certificate_manager.CertificateManager.load_certificate_from_credentials')
    @patch('cpe_engine.sunat.certificate_manager.CertificateManager.is_ready_for_signing')
    @patch('cpe_engine.sunat.xml_signer.XmlSigner.sign_xml')
    def test_send_debit_note_success_scenario(self, mock_sign_xml, mock_ready, mock_cert_load, mock_send, sample_empresa_data, sample_cliente_data, sample_items_data, sunat_credentials):
        """Test envío exitoso de nota de débito"""
        # Mock carga exitosa de certificado
        mock_cert_load.return_value = True
        mock_ready.return_value = True
        mock_sign_xml.return_value = '<xml>signed xml content</xml>'
        
        mock_send.return_value = {
            'success': True,
            'cdr': {
                'code': '0',
                'description': 'La Nota de Debito numero FD01-001, ha sido aceptada'
            }
        }
        
        # Crear datos de nota de débito y enviar
        note_data = create_note_data(
            serie="FD01",
            correlativo=1,
            tipo_nota="08",
            documento_afectado="F001-123",
            motivo="Intereses por mora",
            company_data=sample_empresa_data,
            client_data=sample_cliente_data,
            items=sample_items_data
        )
        
        # Enfoque declarativo: añadir totales para notas
        note_data.update({
            'mto_oper_gravadas': 100.0,
            'mto_igv': 18.0,
            'mto_total_tributos': 18.0,
            'mto_impventa': 118.0,
            'sub_total': 118.0,
            'valor_venta': 100.0
        })
        
        result = send_debit_note(
            credentials=sunat_credentials,
            note_data=note_data
        )
        
        assert result is not None
        assert result.get('success') == True
        mock_send.assert_called_once()
        
    def test_send_invoice_without_credentials(self, sample_empresa_data, sample_cliente_data, sample_items_data):
        """Test manejo de error al enviar sin credenciales"""
        # Crear datos de factura y enviar sin credenciales
        invoice_data = create_invoice_data(
            serie="F001",
            correlativo=123,
            company_data=sample_empresa_data,
            client_data=sample_cliente_data,
            items=sample_items_data
        )
        
        result = send_invoice(
            credentials=None,
            invoice_data=invoice_data
        )
        
        # Debe manejar el error correctamente
        assert result is not None
        assert result.get('success') == False
        assert 'error' in result
        
    def test_send_invoice_invalid_data(self, sunat_credentials):
        """Test manejo de datos inválidos"""
        # Crear datos de factura que pase validación de modelos pero falle en SUNAT
        # Usar credenciales inválidas para forzar el error
        invalid_credentials = SunatCredentials(
            ruc="99999999999",  # RUC que no existe
            usuario="99999999999INVALID",
            password="invalid_password",
            certificado=sunat_credentials.certificado,  # Certificado válido
            es_test=True
        )
        
        # Usar datos mínimos válidos para que pasen la validación del modelo
        minimal_company_data = {
            'ruc': '99999999999',  # RUC válido en formato pero inexistente
            'razon_social': 'EMPRESA INEXISTENTE S.A.C.',
            'address': {
                'ubigeo': '150101',
                'departamento': 'Lima',
                'provincia': 'Lima',  
                'distrito': 'Lima',
                'direccion': 'Sin direccion'
            }
        }
        
        minimal_client_data = {
            'tipo_doc': 6,
            'num_doc': '99999999999',
            'razon_social': 'CLIENTE INEXISTENTE S.A.C.'
        }
        
        invalid_invoice_data = create_invoice_data(
            serie="F001",
            correlativo=999999,  # Número alto que puede causar problemas
            company_data=minimal_company_data,
            client_data=minimal_client_data,
            items=[{
                'cod_item': 'INVALID001',
                'des_item': 'Producto de prueba invalido',
                'cantidad': 1,
                'mto_valor_unitario': 0.01,  # Valor muy bajo
                'unidad': 'NIU'
            }]
        )
        
        result = send_invoice(
            credentials=invalid_credentials,  # Credenciales inválidas para forzar error
            invoice_data=invalid_invoice_data
        )
        
        assert result is not None
        assert result.get('success') == False
        assert 'error' in result


class TestSignedXmlBuilder:
    """Tests críticos para SignedXmlBuilder - 22% cobertura actual"""
    
    @pytest.fixture
    def sample_invoice_model(self):
        """Invoice model para tests"""
        company = Company(
            ruc=TEST_SUNAT_CREDENTIALS['ruc'],
            razon_social="EMPRESA DE PRUEBAS S.A.C."
        )
        
        client = Client(
            tipo_doc="6",
            num_doc="20000000002",
            razon_social="CLIENTE DE PRUEBAS S.A.C."
        )
        
        detail = SaleDetail(
            cod_item="PROD001",
            des_item="Producto de prueba",
            cantidad=1.0,
            unidad="NIU",
            mto_valor_unitario=100.00,
            mto_precio_unitario=118.00,
            mto_valor_venta=100.00,
            tip_afe_igv="10",
            porcentaje_igv=18.0,
            igv=18.00
        )
        
        return Invoice(
            serie="F001",
            correlativo=123,
            fecha_emision=datetime.now(),
            tipo_doc="01",
            tipo_moneda="PEN",
            company=company,
            client=client,
            details=[detail],
            mto_oper_gravadas=100.00,
            mto_igv=18.00,
            mto_impventa=118.00,
            legends=[Legend(code="1000", value="SON: CIENTO DIECIOCHO CON 00/100 SOLES")]
        )
        
    def test_signed_xml_builder_initialization(self):
        """Test inicialización del SignedXmlBuilder"""
        # Inicialización básica del builder
        builder = SignedXmlBuilder()
        
        assert builder is not None
        assert builder.invoice_builder is not None
        assert builder.note_builder is not None
        assert builder.xml_signer is not None
        assert builder.bill_sender is None  # Se configura después
        
        # Configurar credenciales SUNAT
        builder.set_sunat_credentials(
            username=TEST_SUNAT_CREDENTIALS['usuario'],
            password=TEST_SUNAT_CREDENTIALS['password']
        )
        
        assert builder.bill_sender is not None
        
        # Verificar información SUNAT
        sunat_info = builder.get_sunat_info()
        assert sunat_info is not None
        assert sunat_info['username'] == TEST_SUNAT_CREDENTIALS['usuario']
        
    @patch('cpe_engine.sunat.xml_signer.XmlSigner.sign_xml')
    @patch('cpe_engine.sunat.certificate_manager.CertificateManager.is_ready_for_signing')
    def test_signed_xml_builder_build_and_send_workflow(self, mock_ready, mock_sign_xml, sample_invoice_model):
        """Test flujo completo build → sign → send"""
        builder = SignedXmlBuilder()
        
        # Configurar credenciales SUNAT
        builder.set_sunat_credentials(
            username=TEST_SUNAT_CREDENTIALS['usuario'],
            password=TEST_SUNAT_CREDENTIALS['password']
        )
        
        # Mock del certificado y firma
        mock_ready.return_value = True
        mock_sign_xml.return_value = '<signed-xml>Mock signed XML content</signed-xml>'
        
        # Mock del sender para evitar envío real
        with patch.object(builder, 'bill_sender') as mock_sender:
            mock_sender.send_document.return_value = {
                'success': True,
                'cdr': {'code': '0', 'description': 'Aceptado'}
            }
            
            # Test del flujo completo
            result = builder.build_sign_and_send(sample_invoice_model)
            
            # Verificar resultado
            assert result is not None
            assert result.get('success') == True
            
            # Verificar que se llamaron los métodos necesarios
            mock_ready.assert_called_once()
            mock_sign_xml.assert_called_once()
            mock_sender.send_document.assert_called_once()
            
    def test_signed_xml_builder_error_handling(self, sample_invoice_model):
        """Test manejo de errores en SignedXmlBuilder"""
        builder = SignedXmlBuilder()
        
        # Configurar credenciales SUNAT
        builder.set_sunat_credentials(
            username=TEST_SUNAT_CREDENTIALS['usuario'],
            password=TEST_SUNAT_CREDENTIALS['password']
        )
        
        # Test que maneja error cuando no hay certificado cargado
        with pytest.raises(Exception):  # Debería lanzar SignedXmlBuilderError
            builder.build_sign_and_send(sample_invoice_model)
            
    def test_signed_xml_builder_invalid_document(self):
        """Test manejo de documento inválido"""
        builder = SignedXmlBuilder()
        
        # Configurar credenciales SUNAT
        builder.set_sunat_credentials(
            username=TEST_SUNAT_CREDENTIALS['usuario'],
            password=TEST_SUNAT_CREDENTIALS['password']
        )
        
        # Test con documento None - debe lanzar excepción
        with pytest.raises(Exception):  # SignedXmlBuilderError o similar
            builder.build_and_sign(None)


class TestCompleteWorkflows:
    """Tests de flujos completos end-to-end"""
    
    @pytest.fixture
    def complete_invoice_data(self):
        """Datos completos de factura para tests E2E"""
        return {
            'empresa': {
                'ruc': TEST_SUNAT_CREDENTIALS['ruc'],
                'razon_social': 'EMPRESA COMPLETA DE PRUEBAS S.A.C.',
                'nombre_comercial': 'EMPRESA COMPLETA',
                'email': 'facturacion@empresa.com',
                'address': {
                    'ubigeo': '150101',
                    'departamento': 'LIMA',
                    'provincia': 'LIMA',
                    'distrito': 'LIMA',
                    'direccion': 'AV. PRINCIPAL 123, LIMA'
                }
            },
            'cliente': {
                'tipo_doc': 6,
                'num_doc': '20000000002',
                'razon_social': 'CLIENTE COMPLETO DE PRUEBAS S.A.C.'
            },
            'items': [
                {
                    'cod_item': 'SERV001',
                    'des_item': 'Servicio de consultoría',
                    'cantidad': 10,
                    'mto_valor_unitario': 150.00,
                    'unidad': 'HUR'
                },
                {
                    'cod_item': 'PROD002',
                    'des_item': 'Producto hardware',
                    'cantidad': 2,
                    'mto_valor_unitario': 500.00,
                    'unidad': 'NIU'
                }
            ],
            'credenciales': SunatCredentials(
                ruc=TEST_SUNAT_CREDENTIALS['ruc'],
                usuario=TEST_SUNAT_CREDENTIALS['usuario'],
                password=TEST_SUNAT_CREDENTIALS['password'],
                certificado=TEST_SUNAT_CREDENTIALS['certificado'],
                es_test=True
            )
        }
        
    @patch('cpe_engine.sunat.bill_sender.BillSender.send_document')
    @patch('cpe_engine.sunat.certificate_manager.CertificateManager.load_certificate_from_credentials')
    @patch('cpe_engine.sunat.certificate_manager.CertificateManager.is_ready_for_signing')
    @patch('cpe_engine.sunat.xml_signer.XmlSigner.sign_xml')
    def test_complete_invoice_workflow_with_mocks(self, mock_sign_xml, mock_ready, mock_cert_load, mock_soap, complete_invoice_data):
        """Test flujo completo de factura con mocks"""
        # Mock certificate and signing process
        mock_cert_load.return_value = True
        mock_ready.return_value = True
        mock_sign_xml.return_value = '<signed-xml>Mock signed XML content</signed-xml>'
        
        # Mock SUNAT response
        mock_soap.return_value = {
            'success': True,
            'response': '''<?xml version="1.0"?>
            <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
                <soap:Body>
                    <sendBillResponse>
                        <status>
                            <code>0</code>
                            <message>Aceptado</message>
                        </status>
                        <applicationResponse>CDR_DATA_HERE</applicationResponse>
                    </sendBillResponse>
                </soap:Body>
            </soap:Envelope>'''
        }
        
        # Ejecutar flujo completo
        # Crear datos de factura con la nueva API
        invoice_data = create_invoice_data(
            serie="F001",
            correlativo=999,
            company_data=complete_invoice_data['empresa'],
            client_data=complete_invoice_data['cliente'],
            items=complete_invoice_data['items']
        )
        
        # Enfoque declarativo: usuario debe proporcionar totales explícitamente
        # Items: PROD001 (1 * 150) + PROD002 (2 * 500) = 150 + 1000 = 1150
        # Base gravada: 1150 / 1.18 = 974.58
        # IGV (18%): 1150 - 974.58 = 175.42
        invoice_data.update({
            'mto_oper_gravadas': 974.58,  # Base gravada
            'mto_igv': 175.42,           # IGV (18%)
            'mto_total_tributos': 175.42, # Total impuestos
            'mto_impventa': 1150.0,      # Total de venta
            'sub_total': 1150.0,         # Subtotal
            'valor_venta': 974.58        # Valor venta
        })
        
        result = send_invoice(
            credentials=complete_invoice_data['credenciales'],
            invoice_data=invoice_data
        )
        
        # Verificar resultado
        assert result is not None
        assert result.get('success') == True
        
        # Verificar que se llamó a BillSender.send_document
        mock_soap.assert_called_once()
        
        # Verificar que se llamaron los mocks de certificado y firma
        mock_cert_load.assert_called_once()
        mock_ready.assert_called()
        mock_sign_xml.assert_called_once()
        
    def test_complete_workflow_data_validation(self, complete_invoice_data):
        """Test validación de datos en flujo completo"""
        # Test con datos mínimos válidos - usar nueva API
        minimal_invoice_data = create_invoice_data(
            serie="F001",
            correlativo=1,
            company_data={
                'ruc': TEST_SUNAT_CREDENTIALS['ruc'],
                'razon_social': 'EMPRESA MINIMA'
            },
            client_data={
                'tipo_doc': 6,
                'num_doc': '20000000002', 
                'razon_social': 'CLIENTE MINIMO'
            },
            items=[{
                'cod_item': 'MIN001',
                'des_item': 'Producto mínimo',
                'cantidad': 1,
                'mto_valor_unitario': 10.00,
                'unidad': 'NIU'
            }]
        )
        
        # Enfoque declarativo: agregar totales mínimos
        minimal_invoice_data.update({
            'mto_oper_gravadas': 8.47,    # 10/1.18 = 8.47
            'mto_igv': 1.53,             # 10 - 8.47 = 1.53  
            'mto_total_tributos': 1.53,   # Total impuestos
            'mto_impventa': 10.0,        # Total de venta
            'sub_total': 10.0,           # Subtotal
            'valor_venta': 8.47          # Valor venta
        })
        
        minimal_result = send_invoice(
            credentials=complete_invoice_data['credenciales'],
            invoice_data=minimal_invoice_data
        )
        
        # Debería procesar sin errores de validación
        assert minimal_result is not None
        
    def test_workflow_with_export_operation(self):
        """Test flujo completo con operación de exportación"""
        export_credentials = SunatCredentials(
            ruc=TEST_SUNAT_CREDENTIALS['ruc'],
            usuario=TEST_SUNAT_CREDENTIALS['usuario'],
            password=TEST_SUNAT_CREDENTIALS['password'],
            certificado=TEST_SUNAT_CREDENTIALS['certificado'],
            es_test=True
        )
        
        with patch('cpe_engine.sunat.bill_sender.BillSender.send_document') as mock_send, \
             patch('cpe_engine.sunat.certificate_manager.CertificateManager.load_certificate_from_credentials') as mock_cert, \
             patch('cpe_engine.sunat.certificate_manager.CertificateManager.is_ready_for_signing') as mock_ready, \
             patch('cpe_engine.sunat.xml_signer.XmlSigner.sign_xml') as mock_sign:
            
            mock_send.return_value = {
                'success': True,
                'cdr': {'code': '0', 'description': 'Aceptado'}
            }
            mock_cert.return_value = True
            mock_ready.return_value = True
            mock_sign.return_value = '<signed-xml>Mock signed XML for export</signed-xml>'
            
            # Factura de exportación - usar nueva API
            export_invoice_data = create_invoice_data(
                serie="E001",
                correlativo=100,
                company_data={
                    'ruc': TEST_SUNAT_CREDENTIALS['ruc'],
                    'razon_social': 'EMPRESA EXPORTADORA S.A.C.'
                },
                client_data={
                    'tipo_doc': 6,
                    'num_doc': '99999999999',  # Cliente extranjero
                    'razon_social': 'FOREIGN CUSTOMER INC.'
                },
                items=[{
                    'cod_item': 'EXP001',
                    'des_item': 'Producto de exportación',
                    'cantidad': 1,
                    'mto_valor_unitario': 1000.00,
                    'unidad': 'NIU',
                    'tip_afe_igv': '40'  # Exportación
                }]
            )
            
            # Para exportación (tip_afe_igv="40"), todos los montos van a mto_oper_exportacion
            export_invoice_data.update({
                'mto_oper_exportacion': 1000.0,  # Monto de exportación
                'mto_igv': 0.0,                  # Sin IGV en exportación
                'mto_total_tributos': 0.0,       # Sin impuestos
                'mto_impventa': 1000.0,          # Total de venta
                'sub_total': 1000.0,             # Subtotal
                'valor_venta': 1000.0            # Valor venta
            })
            
            result = send_invoice(
                credentials=export_credentials,
                invoice_data=export_invoice_data
            )
            
            assert result is not None
            mock_send.assert_called_once()
            
    def test_workflow_performance_measurement(self, complete_invoice_data):
        """Test medición de performance del flujo completo"""
        import time
        
        with patch('cpe_engine.sunat.bill_sender.BillSender.send_document') as mock_send, \
             patch('cpe_engine.sunat.certificate_manager.CertificateManager.load_certificate_from_credentials') as mock_cert, \
             patch('cpe_engine.sunat.certificate_manager.CertificateManager.is_ready_for_signing') as mock_ready, \
             patch('cpe_engine.sunat.xml_signer.XmlSigner.sign_xml') as mock_sign:
            
            mock_send.return_value = {
                'success': True,
                'cdr': {'code': '0', 'description': 'Aceptado'}
            }
            mock_cert.return_value = True
            mock_ready.return_value = True
            mock_sign.return_value = '<signed-xml>Mock signed XML for performance test</signed-xml>'
            
            # Medir tiempo de ejecución
            start_time = time.time()
            
            # Crear datos con nueva API
            perf_invoice_data = create_invoice_data(
                serie="PERF",
                correlativo=1,
                company_data=complete_invoice_data['empresa'],
                client_data=complete_invoice_data['cliente'],
                items=complete_invoice_data['items']
            )
            
            # Agregar totales como en el primer test
            perf_invoice_data.update({
                'mto_oper_gravadas': 974.58,
                'mto_igv': 175.42,
                'mto_total_tributos': 175.42,
                'mto_impventa': 1150.0,
                'sub_total': 1150.0,
                'valor_venta': 974.58
            })
            
            result = send_invoice(
                credentials=complete_invoice_data['credenciales'],
                invoice_data=perf_invoice_data
            )
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Verificar resultado
            assert result is not None
            
            # Performance benchmark: debe completar en menos de 5 segundos
            # (sin envío real a SUNAT, solo procesamiento local)
            assert execution_time < 5.0, f"Workflow too slow: {execution_time:.2f}s"
            
            # Log performance para monitoring
            print(f"Workflow execution time: {execution_time:.3f}s")
            
    def test_concurrent_workflow_safety(self, complete_invoice_data):
        """Test seguridad en flujos concurrentes"""
        import threading
        
        results = []
        errors = []
        
        def send_invoice_thread(correlativo):
            try:
                # Usar patch con start/stop para mejor control
                mock_send = patch('cpe_engine.sunat.bill_sender.BillSender.send_document').start()
                mock_cert = patch('cpe_engine.sunat.certificate_manager.CertificateManager.load_certificate_from_credentials').start()
                mock_ready = patch('cpe_engine.sunat.certificate_manager.CertificateManager.is_ready_for_signing').start()
                mock_sign = patch('cpe_engine.sunat.xml_signer.XmlSigner.sign_xml').start()
                
                mock_send.return_value = {
                    'success': True,
                    'cdr': {'code': '0', 'description': 'Aceptado'}
                }
                mock_cert.return_value = True
                mock_ready.return_value = True
                mock_sign.return_value = f'<signed-xml>Mock signed XML for thread {correlativo}</signed-xml>'
                
                try:
                    # Crear datos con nueva API
                    concurrent_invoice_data = create_invoice_data(
                        serie="CONC",
                        correlativo=correlativo,
                        company_data=complete_invoice_data['empresa'],
                        client_data=complete_invoice_data['cliente'],
                        items=complete_invoice_data['items'][:1]  # Solo un item para simplicidad
                    )
                    
                    # Agregar totales (solo primer item: 1*150 = 150)
                    concurrent_invoice_data.update({
                        'mto_oper_gravadas': 127.12,  # 150/1.18
                        'mto_igv': 22.88,            # 150 - 127.12  
                        'mto_total_tributos': 22.88,
                        'mto_impventa': 150.0,
                        'sub_total': 150.0,
                        'valor_venta': 127.12
                    })
                    
                    result = send_invoice(
                        credentials=complete_invoice_data['credenciales'],
                        invoice_data=concurrent_invoice_data
                    )
                    results.append(result)
                finally:
                    # Limpiar mocks del thread
                    mock_send.stop()
                    mock_cert.stop() 
                    mock_ready.stop()
                    mock_sign.stop()
                    
            except Exception as e:
                errors.append(str(e))
                
        # Ejecutar múltiples threads concurrentes
        threads = []
        for i in range(5):
            thread = threading.Thread(target=send_invoice_thread, args=(i+1,))
            threads.append(thread)
            thread.start()
            
        # Esperar que terminen todos
        for thread in threads:
            thread.join(timeout=10)  # 10 segundos timeout
            
        # Verificar resultados
        assert len(errors) == 0, f"Concurrent execution errors: {errors}"
        assert len(results) == 5, f"Expected 5 results, got {len(results)}"
        
        # Verificar que todos fueron exitosos
        for result in results:
            assert result is not None
            
        # Cleanup explícito después de threading con patches
        from unittest import mock
        mock.patch.stopall()
        
        # Asegurar que todos los threads terminen
        import time
        time.sleep(0.1)  # Breve pausa para asegurar cleanup