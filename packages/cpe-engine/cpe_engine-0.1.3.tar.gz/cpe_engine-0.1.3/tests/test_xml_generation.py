"""Tests para generación de XML."""

import pytest
from xml.etree import ElementTree as ET

from cpe_engine.core.builders.invoice_builder import InvoiceBuilder
from cpe_engine.core.builders.note_builder import NoteBuilder


class TestInvoiceXmlGeneration:
    """Tests para generación XML de facturas."""
    
    def test_generar_xml_factura(self, factura_simple):
        """Test generación de XML básico de factura."""
        builder = InvoiceBuilder()
        xml_content = builder.build(factura_simple)
        
        assert xml_content is not None
        assert len(xml_content) > 0
        
        # Validar que sea XML válido
        root = ET.fromstring(xml_content)
        assert root is not None
        
        # Validar elementos básicos
        assert "Invoice" in root.tag
    
    def test_xml_contiene_datos_empresa(self, factura_simple):
        """Test que el XML contiene datos de la empresa."""
        builder = InvoiceBuilder()
        xml_content = builder.build(factura_simple)
        
        # Buscar RUC de la empresa en el XML
        assert "20000000001" in xml_content
        assert "EMPRESA PRUEBA S.A.C." in xml_content
    
    def test_xml_contiene_datos_cliente(self, factura_simple):
        """Test que el XML contiene datos del cliente."""
        builder = InvoiceBuilder()
        xml_content = builder.build(factura_simple)
        
        # Buscar datos del cliente en el XML
        assert "20000000002" in xml_content
        assert "CLIENTE EMPRESA S.A.C." in xml_content
    
    def test_xml_contiene_totales(self, factura_simple):
        """Test que el XML contiene los totales correctos."""
        builder = InvoiceBuilder()
        xml_content = builder.build(factura_simple)
        
        # Verificar que contiene los montos
        assert "200.00" in xml_content  # mtoOperGravadas
        assert "36.00" in xml_content   # mtoIGV
        assert "236.00" in xml_content  # mtoImpVenta


class TestNoteXmlGeneration:
    """Tests para generación XML de notas."""
    
    def test_generar_xml_nota_credito(self, empresa_prueba, cliente_juridica, detalle_producto):
        """Test generación de XML de nota de crédito."""
        from cpe_engine.core.models import Note
        from datetime import datetime
        
        nota = Note(
            serie="FC01",
            correlativo=1,
            fecha_emision=datetime.now(),
            tipo_doc="07",  # Nota de crédito
            tipo_moneda="PEN",
            company=empresa_prueba,
            client=cliente_juridica,
            # Datos específicos de nota de crédito
            tip_doc_afectado="01",  # Factura
            num_doc_afectado="F001-123",
            cod_motivo="01",
            des_motivo="Anulación de la operación"
        )
        
        nota.details = [detalle_producto]
        # Totales declarativos como greenter (no automáticos)
        nota.mto_oper_gravadas = 200.00
        nota.mto_igv = 36.00
        nota.mto_impventa = 236.00
        nota.mto_total_tributos = 36.00
        
        builder = NoteBuilder()
        xml_content = builder.build(nota)
        
        assert xml_content is not None
        assert len(xml_content) > 0
        
        # Validar que sea XML válido
        root = ET.fromstring(xml_content)
        assert root is not None
        
        # Validar elementos específicos de nota de crédito
        assert "CreditNote" in root.tag or "07" in xml_content


class TestXmlBuilder:
    """Tests para funcionalidad base de XML builder."""
    
    def test_filtros_sunat_disponibles(self):
        """Test que los filtros SUNAT estén disponibles."""
        from cpe_engine.core.builders.invoice_builder import InvoiceBuilder
        
        builder = InvoiceBuilder()
        filters = builder.jinja_env.filters
        
        # Verificar que los filtros esenciales estén presentes (solo equivalentes a Greenter)
        assert "format_decimal" in filters
        assert "format_date" in filters
        assert "format_time" in filters
        assert "get_tributo_afect" in filters