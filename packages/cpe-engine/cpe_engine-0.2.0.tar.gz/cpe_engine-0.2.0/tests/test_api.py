"""Tests para API pública de alto nivel."""

import pytest
from datetime import datetime

import cpe_engine
from cpe_engine import (
    create_invoice_data,
    create_note_data,
    send_invoice,
    SunatCredentials
)


class TestPublicAPI:
    """Tests para funciones públicas de la API."""
    
    def test_create_invoice_data(self):
        """Test creación de datos de factura."""
        company_data = {
            'ruc': '20000000001',
            'razon_social': 'EMPRESA TEST S.A.C.',
            'email': 'test@empresa.com',
            'address': {
                'ubigeo': '150101',
                'departamento': 'Lima',
                'provincia': 'Lima',
                'distrito': 'Lima',
                'direccion': 'Av. Test 123'
            }
        }
        
        client_data = {
            'tipo_doc': 6,
            'num_doc': '20000000002',
            'razon_social': 'CLIENTE TEST S.A.C.'
        }
        
        items = [
            {
                'cod_item': 'PROD001',
                'des_item': 'Producto Test',
                'cantidad': 2,
                'mto_valor_unitario': 100.00,
                'unidad': 'NIU'
            }
        ]
        
        invoice_data = create_invoice_data(
            serie='F001',
            correlativo=123,
            company_data=company_data,
            client_data=client_data,
            items=items
        )
        
        assert invoice_data['serie'] == 'F001'
        assert invoice_data['correlativo'] == 123
        assert invoice_data['company'].ruc == '20000000001'
        assert invoice_data['client'].num_doc == '20000000002'
        assert len(invoice_data['details']) == 1
        assert invoice_data['details'][0].cod_item == 'PROD001'
    
    def test_create_note_data(self):
        """Test creación de datos de nota de crédito."""
        company_data = {
            'ruc': '20000000001',
            'razon_social': 'EMPRESA TEST S.A.C.'
        }
        
        client_data = {
            'tipo_doc': 6,
            'num_doc': '20000000002',
            'razon_social': 'CLIENTE TEST S.A.C.'
        }
        
        items = [
            {
                'cod_item': 'PROD001',
                'des_item': 'Producto Test',
                'cantidad': 1,
                'mto_valor_unitario': 100.00
            }
        ]
        
        note_data = create_note_data(
            serie='FC01',
            correlativo=1,
            tipo_nota='07',
            documento_afectado='F001-123',
            motivo='Anulación de operación',
            company_data=company_data,
            client_data=client_data,
            items=items
        )
        
        assert note_data['serie'] == 'FC01'
        assert note_data['tipo_doc'] == '07'
        assert note_data['num_doc_afectado'] == 'F001-123'
        assert note_data['des_motivo'] == 'Anulación de operación'
    
    def test_send_invoice_sin_credenciales(self):
        """Test envío de factura sin credenciales válidas."""
        # Credenciales de prueba (no válidas)
        credentials = SunatCredentials(
            ruc="20000000001",
            usuario="20000000001MODDATOS",
            password="test123",
            certificado="-----BEGIN CERTIFICATE-----\ntest\n-----END CERTIFICATE-----",
            es_test=True
        )
        
        invoice_data = {
            'serie': 'F001',
            'correlativo': 123,
            'fecha_emision': datetime.now(),
            'company': None,  # Datos inválidos a propósito
            'client': None,
            'details': []
        }
        
        result = send_invoice(credentials, invoice_data)
        
        # Debe retornar error
        assert result['success'] is False
        assert 'error' in result
    
    def test_version_disponible(self):
        """Test que la versión esté disponible."""
        assert hasattr(cpe_engine, '__version__')
        assert cpe_engine.__version__ == '0.1.0'
    
    def test_imports_principales(self):
        """Test que las clases principales estén disponibles."""
        # Debe poder importar las clases principales
        assert hasattr(cpe_engine, 'Invoice')
        assert hasattr(cpe_engine, 'Company')
        assert hasattr(cpe_engine, 'Client')
        assert hasattr(cpe_engine, 'SunatCredentials')
        assert hasattr(cpe_engine, 'send_invoice')
        assert hasattr(cpe_engine, 'send_credit_note')


class TestCredentialsIntegration:
    """Tests de integración con SunatCredentials."""
    
    def test_credenciales_test_ambiente(self):
        """Test credenciales para ambiente de test."""
        creds = SunatCredentials(
            ruc="20000000001",
            usuario="20000000001MODDATOS",
            password="moddatos",
            certificado="-----BEGIN CERTIFICATE-----\ntest\n-----END CERTIFICATE-----",
            es_test=True
        )
        
        assert creds.es_test is True
        assert creds.ruc == "20000000001"
        assert "MODDATOS" in creds.usuario
    
    def test_credenciales_produccion_ambiente(self):
        """Test credenciales para ambiente de producción."""
        creds = SunatCredentials(
            ruc="20123456789",
            usuario="20123456789USUARIO1",
            password="password_real",
            certificado="-----BEGIN CERTIFICATE-----\nreal_cert\n-----END CERTIFICATE-----",
            es_test=False
        )
        
        assert creds.es_test is False
        assert creds.ruc == "20123456789"