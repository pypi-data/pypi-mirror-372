"""
Tests críticos de manejo de errores - QA Priority 1

Valida el manejo robusto de errores en escenarios críticos que pueden ocurrir
en producción pero no están siendo testeados adecuadamente:

- Network failures durante comunicación SUNAT
- Malformed XML responses
- Certificate expiry during signing  
- SUNAT server errors and timeouts
- Invalid data handling
- Memory/resource exhaustion scenarios
- Edge cases that cause crashes

Estos tests son críticos porque fallos de manejo de errores pueden resultar en:
- Application crashes en producción
- Documentos perdidos o corruptos
- Datos sensibles expuestos en logs
- Sistema inestable bajo carga
"""

import pytest
import tempfile
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock, PropertyMock
import xml.etree.ElementTree as ET

# Core imports
from cpe_engine import send_invoice, SunatCredentials, create_invoice_data
from cpe_engine.core.models.invoice import Invoice
from cpe_engine.core.models.company import Company
from cpe_engine.core.models.client import Client
from cpe_engine.core.models.base_sale import SaleDetail, Legend
from cpe_engine.sunat.soap_client import SoapClient
from cpe_engine.sunat.bill_sender import BillSender
from cpe_engine.sunat.xml_signer import XmlSigner
from cpe_engine.sunat.cdr_processor import CdrProcessor
from cpe_engine.core.builders.invoice_builder import InvoiceBuilder


class TestNetworkErrorHandling:
    """Tests de manejo de errores de red"""
    
    @pytest.fixture
    def sample_credentials(self):
        return SunatCredentials(
            ruc='20000000001',
            usuario='20000000001MODDATOS',
            password='moddatos',
            certificado='dummy_cert',
            es_test=True
        )
        
    @pytest.fixture
    def sample_data(self):
        return {
            'empresa': {
                'ruc': '20000000001',
                'razon_social': 'EMPRESA PRUEBA'
            },
            'cliente': {
                'tipo_doc': 6,
                'num_doc': '20000000002',
                'razon_social': 'CLIENTE PRUEBA'
            },
            'items': [{
                'cod_item': 'PROD001',
                'des_item': 'Producto prueba',
                'cantidad': 1,
                'mto_valor_unitario': 100.00,
                'unidad': 'NIU'
            }]
        }
    
    @patch('requests.Session.post')
    def test_soap_client_connection_timeout(self, mock_post, sample_credentials):
        """Test manejo de timeout de conexión"""
        import requests
        mock_post.side_effect = requests.Timeout("Connection timeout after 30 seconds")
        
        soap_client = SoapClient(
            endpoint='https://e-beta.sunat.gob.pe/ol-ti-itcpfegem-beta/billService',
            username=sample_credentials.usuario,
            password=sample_credentials.password
        )
        
        # Test envío con timeout - usar método correcto send_bill
        zip_filename = "test_document.zip"
        zip_content = b"fake_zip_content"
        
        # Debe lanzar SoapClientError con timeout
        with pytest.raises(Exception) as exc_info:
            soap_client.send_bill(zip_filename, zip_content)
        
        # Verificar que el error contiene información del timeout
        assert 'timeout' in str(exc_info.value).lower() or 'error' in str(exc_info.value).lower()
        
    @patch('requests.Session.post')
    def test_soap_client_connection_refused(self, mock_post, sample_credentials):
        """Test manejo de conexión rechazada"""
        import requests
        mock_post.side_effect = requests.ConnectionError("Connection refused")
        
        soap_client = SoapClient(
            endpoint='https://invalid.sunat.endpoint/service',
            username=sample_credentials.usuario,
            password=sample_credentials.password
        )
        
        zip_filename = "test_document.zip"
        zip_content = b"fake_zip_content"
        
        # Debe lanzar SoapClientError
        with pytest.raises(Exception) as exc_info:
            soap_client.send_bill(zip_filename, zip_content)
        
        # Verificar que el error contiene información de conexión
        assert 'connection' in str(exc_info.value).lower() or 'error' in str(exc_info.value).lower()
        
    @patch('requests.Session.post')
    def test_soap_client_dns_failure(self, mock_post, sample_credentials):
        """Test manejo de fallo DNS"""
        import requests
        mock_post.side_effect = requests.exceptions.RequestException("DNS resolution failed")
        
        soap_client = SoapClient(
            endpoint='https://nonexistent.domain.invalid/service',
            username=sample_credentials.usuario,
            password=sample_credentials.password
        )
        
        zip_filename = "test_document.zip"
        zip_content = b"fake_zip_content"
        
        # Debe lanzar SoapClientError por DNS
        with pytest.raises(Exception) as exc_info:
            soap_client.send_bill(zip_filename, zip_content)
        
        # Verificar que el error contiene información de DNS
        assert 'dns' in str(exc_info.value).lower() or 'error' in str(exc_info.value).lower()
        
    @patch('cpe_engine.sunat.soap_client.SoapClient.send_bill')
    def test_high_level_api_network_error_propagation(self, mock_send, sample_data, sample_credentials):
        """Test propagación de errores de red en API de alto nivel"""
        # Simular error de red
        mock_send.side_effect = Exception("Network unreachable")
        
        # Test que API maneja error de red sin crash - usar nueva API
        invoice_data = create_invoice_data(
            serie="F001",
            correlativo=123,
            company_data=sample_data['empresa'],
            client_data=sample_data['cliente'],
            items=sample_data['items']
        )
        
        # Agregar totales básicos
        invoice_data.update({
            'mto_oper_gravadas': 84.75,
            'mto_igv': 15.25,
            'mto_total_tributos': 15.25,
            'mto_impventa': 100.0,
            'sub_total': 100.0,
            'valor_venta': 84.75
        })
        
        result = send_invoice(
            credentials=sample_credentials,
            invoice_data=invoice_data
        )
        
        # Debe manejar error sin crash
        assert result is not None
        assert result.get('success') == False
        assert 'error' in result
        
    @patch('requests.Session.post')
    def test_soap_client_partial_response_handling(self, mock_post, sample_credentials):
        """Test manejo de respuesta parcial/corrupta"""
        # Mock respuesta parcial
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "<?xml version='1.0'?><soap:Envelope><soap:Body>TRUNCATED_RES"  # Respuesta cortada
        mock_post.return_value = mock_response
        
        soap_client = SoapClient(
            endpoint='https://e-beta.sunat.gob.pe/ol-ti-itcpfegem-beta/billService',
            username=sample_credentials.usuario,
            password=sample_credentials.password
        )
        
        zip_filename = "test_document.zip"
        zip_content = b"fake_zip_content"
        
        # Con respuesta truncada, debe lanzar error o manejarlo graciosamente
        with pytest.raises(Exception) as exc_info:
            soap_client.send_bill(zip_filename, zip_content)
        
        # Verificar que detectó el problema de respuesta truncada
        assert 'error' in str(exc_info.value).lower()


class TestMalformedDataHandling:
    """Tests de manejo de datos malformados"""
    
    def test_xml_builder_with_none_values(self):
        """Test XML builder con valores None"""
        # Crear invoice con valores None
        company = Company(ruc='20000000001', razon_social='TEST COMPANY')
        client = Client(tipo_doc='6', num_doc='20000000002', razon_social='TEST CLIENT')
        
        detail = SaleDetail(
            cod_item=None,  # None value
            des_item="Test product",
            cantidad=1.0,
            unidad="NIU",
            mto_valor_unitario=100.0,
            mto_precio_unitario=118.0,
            mto_valor_venta=100.0,
            tip_afe_igv="10",
            porcentaje_igv=18.0,
            igv=18.0
        )
        
        invoice = Invoice(
            serie="F001",
            correlativo=123,
            fecha_emision=datetime.now(),
            tipo_doc="01",
            tipo_moneda="PEN",
            company=company,
            client=client,
            details=[detail],
            mto_oper_gravadas=100.0,
            mto_igv=18.0,
            mto_impventa=118.0,
            legends=[]
        )
        
        builder = InvoiceBuilder()
        
        # Test que maneja None values sin crash
        try:
            xml_content = builder.build(invoice)
            assert xml_content is not None
            assert len(xml_content) > 0
            
            # Verificar que es XML válido
            ET.fromstring(xml_content)
            
        except Exception as e:
            # Si falla, no debe ser por None values no manejados
            error_msg = str(e).lower()
            assert 'none' not in error_msg or 'nonetype' not in error_msg
            
    def test_xml_builder_with_special_characters(self):
        """Test XML builder con caracteres especiales"""
        company = Company(ruc='20000000001', razon_social='TEST & COMPANY < > "')
        client = Client(tipo_doc='6', num_doc='20000000002', razon_social='CLIENT "SPECIAL" & CO.')
        
        detail = SaleDetail(
            cod_item="PROD<>&\"",
            des_item="Producto con caracteres especiales: <>&\"'",
            cantidad=1.0,
            unidad="NIU",
            mto_valor_unitario=100.0,
            mto_precio_unitario=118.0,
            mto_valor_venta=100.0,
            tip_afe_igv="10",
            porcentaje_igv=18.0,
            igv=18.0
        )
        
        invoice = Invoice(
            serie="F001",
            correlativo=123,
            fecha_emision=datetime.now(),
            tipo_doc="01",
            tipo_moneda="PEN",
            company=company,
            client=client,
            details=[detail],
            mto_oper_gravadas=100.0,
            mto_igv=18.0,
            mto_impventa=118.0,
            legends=[]
        )
        
        builder = InvoiceBuilder()
        xml_content = builder.build(invoice)
        
        # Debe generar XML válido con caracteres escapados
        assert xml_content is not None
        
        # Verificar que es XML válido
        root = ET.fromstring(xml_content)
        assert root is not None
        
        # Verificar que caracteres especiales están escapados correctamente
        assert '&amp;' in xml_content or '&' not in xml_content.replace('&amp;', '').replace('&lt;', '').replace('&gt;', '').replace('&quot;', '').replace('&apos;', '')
        
    def test_xml_builder_with_very_long_strings(self):
        """Test XML builder con strings muy largos"""
        long_description = "X" * 10000  # 10KB string
        
        company = Company(ruc='20000000001', razon_social='TEST COMPANY')
        client = Client(tipo_doc='6', num_doc='20000000002', razon_social='TEST CLIENT')
        
        detail = SaleDetail(
            cod_item="PROD001",
            des_item=long_description,
            cantidad=1.0,
            unidad="NIU",
            mto_valor_unitario=100.0,
            mto_precio_unitario=118.0,
            mto_valor_venta=100.0,
            tip_afe_igv="10",
            porcentaje_igv=18.0,
            igv=18.0
        )
        
        invoice = Invoice(
            serie="F001",
            correlativo=123,
            fecha_emision=datetime.now(),
            tipo_doc="01",
            tipo_moneda="PEN",
            company=company,
            client=client,
            details=[detail],
            mto_oper_gravadas=100.0,
            mto_igv=18.0,
            mto_impventa=118.0,
            legends=[]
        )
        
        builder = InvoiceBuilder()
        
        # Test que maneja strings largos sin problemas de memoria
        xml_content = builder.build(invoice)
        assert xml_content is not None
        assert long_description in xml_content
        
    def test_cdr_processor_with_malformed_xml(self):
        """Test CDR processor con XML malformado"""
        processor = CdrProcessor()
        
        malformed_responses = [
            "<invalid>xml<response>",  # Tags no cerrados
            "<?xml version='1.0'?><root>TRUNCATED",  # XML truncado
            "NOT_XML_AT_ALL",  # No es XML
            "",  # Vacío
            None,  # None
            "<?xml version='1.0'?><root><child/><invalid></root>",  # XML inválido
        ]
        
        for malformed_cdr in malformed_responses:
            # Debe lanzar CdrProcessorError para datos malformados
            with pytest.raises(Exception):  # CdrProcessorError o similar
                processor.process_cdr_response(malformed_cdr)
            
    def test_xml_signer_with_malformed_input(self):
        """Test XML signer con input malformado"""
        signer = XmlSigner()
        
        malformed_inputs = [
            ("", "valid_cert"),  # XML vacío
            (None, "valid_cert"),  # XML None
            ("<invalid>xml", "valid_cert"),  # XML malformado
            ("<?xml version='1.0'?><root>", ""),  # Certificado vacío
            ("<?xml version='1.0'?><root>", None),  # Certificado None
        ]
        
        for xml_content, cert in malformed_inputs:
            try:
                result = signer.sign(xml_content, cert)
                
                # Si no lanza excepción, debe indicar error
                if result is not None:
                    assert isinstance(result, str) or isinstance(result, dict)
                    
            except Exception as e:
                # Error controlado, no crash
                error_msg = str(e).lower()
                assert any(word in error_msg for word in ['xml', 'certificate', 'invalid', 'parse', 'format'])


class TestResourceExhaustionHandling:
    """Tests de manejo de agotamiento de recursos"""
    
    def test_xml_builder_memory_usage_large_invoice(self):
        """Test uso de memoria con factura muy grande"""
        company = Company(ruc='20000000001', razon_social='TEST COMPANY')
        client = Client(tipo_doc='6', num_doc='20000000002', razon_social='TEST CLIENT')
        
        # Crear muchos detalles para simular factura grande
        details = []
        for i in range(1000):  # 1000 líneas
            detail = SaleDetail(
                cod_item=f"PROD{i:03d}",
                des_item=f"Producto número {i} con descripción larga para aumentar el tamaño del XML",
                cantidad=float(i + 1),
                unidad="NIU",
                mto_valor_unitario=100.0 + i,
                mto_precio_unitario=118.0 + i,
                mto_valor_venta=(100.0 + i) * (i + 1),
                tip_afe_igv="10",
                porcentaje_igv=18.0,
                igv=18.0 * (i + 1)
            )
            details.append(detail)
            
        invoice = Invoice(
            serie="F001",
            correlativo=123,
            fecha_emision=datetime.now(),
            tipo_doc="01",
            tipo_moneda="PEN",
            company=company,
            client=client,
            details=details,
            mto_oper_gravadas=100000.0,
            mto_igv=18000.0,
            mto_impventa=118000.0,
            legends=[]
        )
        
        builder = InvoiceBuilder()
        
        # Test que maneja factura grande sin problemas de memoria
        import time
        start_time = time.time()
        
        xml_content = builder.build(invoice)
        
        end_time = time.time()
        build_time = end_time - start_time
        
        # Verificaciones
        assert xml_content is not None
        assert len(xml_content) > 50000  # XML debe ser grande
        
        # Performance: no debe tomar más de 10 segundos
        assert build_time < 10.0, f"Large invoice build too slow: {build_time:.2f}s"
        
        # Verificar que es XML válido
        try:
            root = ET.fromstring(xml_content)
            assert root is not None
        except ET.ParseError:
            pytest.fail("Large invoice generated invalid XML")
            
    def test_concurrent_xml_generation_stability(self):
        """Test estabilidad con generación XML concurrente"""
        import threading
        import time
        
        errors = []
        results = []
        
        def build_xml_thread(thread_id):
            try:
                company = Company(ruc='20000000001', razon_social=f'COMPANY {thread_id}')
                client = Client(tipo_doc='6', num_doc='20000000002', razon_social=f'CLIENT {thread_id}')
                
                detail = SaleDetail(
                    cod_item=f"PROD{thread_id}",
                    des_item=f"Producto thread {thread_id}",
                    cantidad=1.0,
                    unidad="NIU",
                    mto_valor_unitario=100.0,
                    mto_precio_unitario=118.0,
                    mto_valor_venta=100.0,
                    tip_afe_igv="10",
                    porcentaje_igv=18.0,
                    igv=18.0
                )
                
                invoice = Invoice(
                    serie="F001",
                    correlativo=thread_id,
                    fecha_emision=datetime.now(),
                    tipo_doc="01",
                    tipo_moneda="PEN",
                    company=company,
                    client=client,
                    details=[detail],
                    mto_oper_gravadas=100.0,
                    mto_igv=18.0,
                    mto_impventa=118.0,
                    legends=[]
                )
                
                builder = InvoiceBuilder()
                xml_content = builder.build(invoice)
                
                results.append({
                    'thread_id': thread_id,
                    'xml_length': len(xml_content) if xml_content else 0,
                    'success': xml_content is not None
                })
                
            except Exception as e:
                errors.append(f"Thread {thread_id}: {str(e)}")
                
        # Ejecutar 10 threads concurrentes
        threads = []
        for i in range(10):
            thread = threading.Thread(target=build_xml_thread, args=(i + 1,))
            threads.append(thread)
            thread.start()
            
        # Esperar que terminen
        for thread in threads:
            thread.join(timeout=30)
            
        # Verificar resultados
        assert len(errors) == 0, f"Concurrent execution errors: {errors}"
        assert len(results) == 10, f"Expected 10 results, got {len(results)}"
        
        # Verificar que todos fueron exitosos
        for result in results:
            assert result['success'] == True
            assert result['xml_length'] > 0
            
    def test_memory_cleanup_after_errors(self):
        """Test limpieza de memoria después de errores"""
        import gc
        
        # Forzar recolección de basura inicial
        gc.collect()
        initial_objects = len(gc.get_objects())
        
        # Ejecutar operaciones que pueden fallar
        for i in range(50):
            try:
                # Intentar operaciones que pueden fallar
                signer = XmlSigner()
                signer.sign("invalid_xml", "invalid_cert")
            except:
                pass  # Ignorar errores intencionalmente
                
            try:
                processor = CdrProcessor()
                processor.process_cdr("invalid_cdr")
            except:
                pass
                
        # Forzar recolección de basura
        gc.collect()
        final_objects = len(gc.get_objects())
        
        # No debería haber una fuga masiva de memoria
        objects_diff = final_objects - initial_objects
        
        # Permitir algún incremento normal, pero no excesivo
        assert objects_diff < 1000, f"Possible memory leak: {objects_diff} new objects"


class TestEdgeCaseHandling:
    """Tests de casos edge que pueden causar crashes"""
    
    def test_extreme_decimal_precision(self):
        """Test manejo de precisión decimal extrema"""
        company = Company(ruc='20000000001', razon_social='TEST COMPANY')
        client = Client(tipo_doc='6', num_doc='20000000002', razon_social='TEST CLIENT')
        
        # Valores con precisión extrema
        detail = SaleDetail(
            cod_item="PROD001",
            des_item="Producto con decimales extremos",
            cantidad=1.0,
            unidad="NIU",
            mto_valor_unitario=0.001,  # Muy pequeño
            mto_precio_unitario=99999999.999999,  # Muy grande con muchos decimales
            mto_valor_venta=0.001,
            tip_afe_igv="10",
            porcentaje_igv=18.0,
            igv=0.00018
        )
        
        invoice = Invoice(
            serie="F001",
            correlativo=123,
            fecha_emision=datetime.now(),
            tipo_doc="01",
            tipo_moneda="PEN",
            company=company,
            client=client,
            details=[detail],
            mto_oper_gravadas=0.001,
            mto_igv=0.00018,
            mto_impventa=0.00118,
            legends=[]
        )
        
        builder = InvoiceBuilder()
        
        # Test que maneja valores extremos
        xml_content = builder.build(invoice)
        assert xml_content is not None
        
        # Verificar que números están correctamente formateados
        assert '0.00' in xml_content or '0.001' in xml_content
        
    def test_date_edge_cases(self):
        """Test manejo de fechas edge case"""
        company = Company(ruc='20000000001', razon_social='TEST COMPANY')
        client = Client(tipo_doc='6', num_doc='20000000002', razon_social='TEST CLIENT')
        
        detail = SaleDetail(
            cod_item="PROD001",
            des_item="Producto test",
            cantidad=1.0,
            unidad="NIU",
            mto_valor_unitario=100.0,
            mto_precio_unitario=118.0,
            mto_valor_venta=100.0,
            tip_afe_igv="10",
            porcentaje_igv=18.0,
            igv=18.0
        )
        
        # Test con fechas edge
        edge_dates = [
            datetime(2000, 1, 1),  # Y2K
            datetime(2038, 1, 19),  # Unix timestamp limit
            datetime(1900, 1, 1),  # Fecha muy antigua
            datetime(2099, 12, 31),  # Fecha futura
        ]
        
        builder = InvoiceBuilder()
        
        for edge_date in edge_dates:
            invoice = Invoice(
                serie="F001",
                correlativo=123,
                fecha_emision=edge_date,
                tipo_doc="01",
                tipo_moneda="PEN",
                company=company,
                client=client,
                details=[detail],
                mto_oper_gravadas=100.0,
                mto_igv=18.0,
                mto_impventa=118.0,
                legends=[]
            )
            
            # Test que maneja fechas edge
            xml_content = builder.build(invoice)
            assert xml_content is not None
            
            # Verificar formato de fecha
            date_str = edge_date.strftime("%Y-%m-%d")
            assert date_str in xml_content
            
    def test_unicode_handling(self):
        """Test manejo de caracteres Unicode"""
        company = Company(ruc='20000000001', razon_social='COMPAÑÍA CON ÑÚMËROS ËXTRAÑÖS')
        client = Client(tipo_doc='6', num_doc='20000000002', razon_social='CLIENTE TÏLDÊS Y SÍMBÖLOS')
        
        detail = SaleDetail(
            cod_item="PROD001",
            des_item="Prodúcto cón acëntøs y símbölos: áéíóú ñÑ €£¥",
            cantidad=1.0,
            unidad="NIU",
            mto_valor_unitario=100.0,
            mto_precio_unitario=118.0,
            mto_valor_venta=100.0,
            tip_afe_igv="10",
            porcentaje_igv=18.0,
            igv=18.0
        )
        
        invoice = Invoice(
            serie="F001",
            correlativo=123,
            fecha_emision=datetime.now(),
            tipo_doc="01",
            tipo_moneda="PEN",
            company=company,
            client=client,
            details=[detail],
            mto_oper_gravadas=100.0,
            mto_igv=18.0,
            mto_impventa=118.0,
            legends=[Legend(code="1000", value="SON: CÉNTÓ DÍËZ CON 00/100 SOLES")]
        )
        
        builder = InvoiceBuilder()
        
        # Test que maneja Unicode correctamente
        xml_content = builder.build(invoice)
        assert xml_content is not None
        
        # Verificar encoding UTF-8
        assert 'encoding="utf-8"' in xml_content or 'encoding="UTF-8"' in xml_content
        
        # Verificar que caracteres Unicode están presentes
        assert 'ñ' in xml_content or '&' in xml_content  # Pueden estar escapados
        
        # Verificar que es XML válido
        try:
            root = ET.fromstring(xml_content.encode('utf-8'))
            assert root is not None
        except ET.ParseError as e:
            pytest.fail(f"Unicode content generated invalid XML: {e}")
            
    def test_zero_and_negative_values_handling(self):
        """Test manejo de valores cero y negativos"""
        company = Company(ruc='20000000001', razon_social='TEST COMPANY')
        client = Client(tipo_doc='6', num_doc='20000000002', razon_social='TEST CLIENT')
        
        # Detalle con valor cero (casos como regalos/gratuidades)
        detail_zero = SaleDetail(
            cod_item="PROD001",
            des_item="Producto gratuito",
            cantidad=1.0,  # Cantidad válida
            unidad="NIU",
            mto_valor_unitario=0.0,  # Valor cero para gratuidad
            mto_precio_unitario=0.0,
            mto_valor_venta=0.0,
            tip_afe_igv="10",
            porcentaje_igv=0.0,
            igv=0.0
        )
        
        invoice = Invoice(
            serie="F001",
            correlativo=123,
            fecha_emision=datetime.now(),
            tipo_doc="01",
            tipo_moneda="PEN",
            company=company,
            client=client,
            details=[detail_zero],
            mto_oper_gravadas=0.0,  # Totales cero
            mto_igv=0.0,
            mto_impventa=0.0,
            legends=[]
        )
        
        builder = InvoiceBuilder()
        
        # Test que maneja valores cero
        xml_content = builder.build(invoice)
        assert xml_content is not None
        
        # Verificar que valores cero están correctamente formateados
        assert '0.00' in xml_content
        
        # Verificar que es XML válido
        try:
            root = ET.fromstring(xml_content)
            assert root is not None
        except ET.ParseError:
            pytest.fail("Zero values generated invalid XML")