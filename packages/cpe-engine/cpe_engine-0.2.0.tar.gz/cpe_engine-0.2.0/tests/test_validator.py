"""
Tests para DocumentValidator - Validador opcional usando catálogos oficiales SUNAT.

Tests del validador completamente separado del core (como greenter/validator).
"""

import pytest
from datetime import datetime
from dataclasses import asdict

from cpe_engine.validator.document_validator import DocumentValidator, ValidationError
from cpe_engine.core.models.invoice import Invoice
from cpe_engine.core.models.note import Note
from cpe_engine.core.models.company import Company
from cpe_engine.core.models.client import Client
from cpe_engine.core.models.address import Address
from cpe_engine.core.models.base_sale import SaleDetail


class TestDocumentValidator:
    """Tests para el DocumentValidator principal."""
    
    def setup_method(self):
        """Configurar validator para cada test."""
        self.validator = DocumentValidator()
        
        # Datos válidos para usar en tests
        self.company_valida = Company(
            ruc="20123456789",
            razon_social="EMPRESA DE PRUEBA S.A.C.",
            address=Address(
                ubigeo="150101",
                departamento="Lima",
                provincia="Lima",
                distrito="Lima",
                direccion="Av. Test 123"
            )
        )
        
        self.client_valido = Client(
            tipo_doc=6,
            num_doc="20987654321",
            razon_social="CLIENTE PRUEBA S.A.C."
        )
        
        self.detalle_valido = SaleDetail(
            cod_item="PROD001",
            des_item="Producto de prueba",
            cantidad=1.0,
            mto_valor_unitario=100.00,
            mto_precio_unitario=118.00,
            mto_valor_venta=100.00,
            unidad="NIU",
            tip_afe_igv="10",
            porcentaje_igv=18.0,
            igv=18.0
        )
    
    def test_inicializacion_validator(self):
        """Test inicialización del validator."""
        validator = DocumentValidator()
        assert validator.version == "2.1"
        
        validator_custom = DocumentValidator(version="2.0")
        assert validator_custom.version == "2.0"
    
    def test_validar_documento_none(self):
        """Test validación de documento None."""
        errors = self.validator.validate(None)
        
        assert len(errors) == 1
        assert errors[0].field == "document"
        assert "requerido" in errors[0].message
    
    def test_validar_factura_valida(self):
        """Test validación de factura válida."""
        invoice = Invoice(
            tipo_doc="01",
            serie="F001",
            correlativo=123,
            fecha_emision=datetime.now(),
            tipo_moneda="PEN",
            tipo_operacion="01",  # Venta interna
            mto_oper_gravadas=100.00,
            mto_oper_inafectas=0.00,
            mto_oper_exoneradas=0.00,
            mto_impventa=118.00,
            company=self.company_valida,
            client=self.client_valido,
            details=[self.detalle_valido]
        )
        
        errors = self.validator.validate(invoice)
        assert len(errors) == 0
    
    def test_validar_factura_moneda_invalida(self):
        """Test validación de factura con moneda inválida."""
        invoice = Invoice(
            tipo_doc="01",
            serie="F001",
            correlativo=123,
            fecha_emision=datetime.now(),
            tipo_moneda="INVALID",  # ❌ Moneda inválida
            tipo_operacion="01",  # Venta interna
            mto_oper_gravadas=100.00,
            mto_oper_inafectas=0.00,
            mto_oper_exoneradas=0.00,
            mto_impventa=118.00,
            company=self.company_valida,
            client=self.client_valido,
            details=[self.detalle_valido]
        )
        
        errors = self.validator.validate(invoice)
        assert len(errors) > 0
        
        # Buscar error de moneda
        moneda_error = next((e for e in errors if "moneda" in e.message.lower()), None)
        assert moneda_error is not None
        assert "INVALID" in moneda_error.message
    
    def test_validar_factura_tipo_operacion_invalido(self):
        """Test validación de factura con tipo de operación inválido."""
        invoice = Invoice(
            tipo_doc="01",
            serie="F001",
            correlativo=123,
            fecha_emision=datetime.now(),
            tipo_moneda="PEN",
            tipo_operacion="9999",  # ❌ Tipo operación inválido
            mto_oper_gravadas=100.00,
            mto_oper_inafectas=0.00,
            mto_oper_exoneradas=0.00,
            mto_impventa=118.00,
            company=self.company_valida,
            client=self.client_valido,
            details=[self.detalle_valido]
        )
        
        errors = self.validator.validate(invoice)
        assert len(errors) > 0
        
        # Buscar error de tipo operación
        operacion_error = next((e for e in errors if "operación" in e.message.lower()), None)
        assert operacion_error is not None
        assert "9999" in operacion_error.message
    
    def test_validar_nota_credito_valida(self):
        """Test validación de nota de crédito válida."""
        note = Note(
            tipo_doc="07",
            serie="FC01",
            correlativo=1,
            fecha_emision=datetime.now(),
            tipo_moneda="PEN",
            tipo_operacion="08",  # Para notas de crédito
            tip_doc_afectado="01",
            num_doc_afectado="F001-123",
            cod_motivo="01",
            des_motivo="Anulación de la operación",
            mto_oper_gravadas=100.00,
            mto_oper_inafectas=0.00,
            mto_oper_exoneradas=0.00,
            mto_impventa=118.00,
            company=self.company_valida,
            client=self.client_valido,
            details=[self.detalle_valido]
        )
        
        errors = self.validator.validate(note)
        assert len(errors) == 0
    
    def test_validar_nota_motivo_invalido(self):
        """Test validación de nota con motivo inválido."""
        note = Note(
            tipo_doc="07",
            serie="FC01", 
            correlativo=1,
            fecha_emision=datetime.now(),
            tipo_moneda="PEN",
            tip_doc_afectado="01",
            num_doc_afectado="F001-123",
            cod_motivo="99",  # ❌ Código de motivo inválido para nota crédito
            des_motivo="Motivo inválido",
            mto_oper_gravadas=100.00,
            mto_oper_inafectas=0.00,
            mto_oper_exoneradas=0.00,
            mto_impventa=118.00,
            company=self.company_valida,
            client=self.client_valido,
            details=[self.detalle_valido]
        )
        
        errors = self.validator.validate(note)
        assert len(errors) > 0
        
        # Buscar error de motivo
        motivo_error = next((e for e in errors if "motivo" in e.message.lower()), None)
        assert motivo_error is not None
        assert "99" in motivo_error.message
    
    def test_validar_nota_documento_afectado_formato_invalido(self):
        """Test validación de nota con formato de documento afectado inválido."""
        note = Note(
            tipo_doc="07",
            serie="FC01",
            correlativo=1,
            fecha_emision=datetime.now(),
            tipo_moneda="PEN",
            tip_doc_afectado="01",
            num_doc_afectado="F001123",  # ❌ Sin guión separador
            cod_motivo="01",
            des_motivo="Anulación de la operación",
            mto_oper_gravadas=100.00,
            mto_oper_inafectas=0.00,
            mto_oper_exoneradas=0.00,
            mto_impventa=118.00,
            company=self.company_valida,
            client=self.client_valido,
            details=[self.detalle_valido]
        )
        
        errors = self.validator.validate(note)
        assert len(errors) > 0
        
        # Buscar error de formato
        formato_error = next((e for e in errors if "formato" in e.message.lower()), None)
        assert formato_error is not None
    
    def test_validar_company_valida_no_errores_adicionales(self):
        """Test que company válida no genera errores adicionales en validator."""
        # El core ya valida company, el validator no debería agregar errores adicionales
        invoice = Invoice(
            tipo_doc="01",
            serie="F001",
            correlativo=123,
            fecha_emision=datetime.now(),
            tipo_moneda="PEN",
            tipo_operacion="01",  # Venta interna
            mto_oper_gravadas=100.00,
            mto_oper_inafectas=0.00,
            mto_oper_exoneradas=0.00,
            mto_impventa=118.00,
            company=self.company_valida,  # Company ya validada por el core
            client=self.client_valido,
            details=[self.detalle_valido]
        )
        
        errors = self.validator.validate(invoice)
        # No debe haber errores de company ya que el core ya validó
        company_errors = [e for e in errors if "company" in e.field.lower()]
        assert len(company_errors) == 0
    
    def test_validar_detalle_unidad_invalida(self):
        """Test validación de detalle con unidad de medida inválida."""
        detalle_invalido = SaleDetail(
            cod_item="PROD001",
            des_item="Producto de prueba",
            cantidad=1.0,
            mto_valor_unitario=100.00,
            mto_precio_unitario=118.00,
            mto_valor_venta=100.00,
            unidad="INVALID",  # ❌ Unidad inválida
            tip_afe_igv="10",
            porcentaje_igv=18.0,
            igv=18.0
        )
        
        invoice = Invoice(
            tipo_doc="01",
            serie="F001",
            correlativo=123,
            fecha_emision=datetime.now(),
            tipo_moneda="PEN",
            tipo_operacion="01",  # Venta interna
            mto_oper_gravadas=100.00,
            mto_oper_inafectas=0.00,
            mto_oper_exoneradas=0.00,
            mto_impventa=118.00,
            company=self.company_valida,
            client=self.client_valido,
            details=[detalle_invalido]
        )
        
        errors = self.validator.validate(invoice)
        assert len(errors) > 0
        
        # Buscar error de unidad en detalles
        unidad_error = next((e for e in errors if "details" in e.field and "unidad" in e.message.lower()), None)
        assert unidad_error is not None
        assert "INVALID" in unidad_error.message
    
    def test_validar_detalle_afectacion_igv_invalida(self):
        """Test validación de detalle con afectación IGV inválida."""
        detalle_invalido = SaleDetail(
            cod_item="PROD001",
            des_item="Producto de prueba",
            cantidad=1.0,
            mto_valor_unitario=100.00,
            mto_precio_unitario=118.00,
            mto_valor_venta=100.00,
            unidad="NIU",
            tip_afe_igv="99",  # ❌ Afectación IGV inválida
            porcentaje_igv=18.0,
            igv=18.0
        )
        
        invoice = Invoice(
            tipo_doc="01",
            serie="F001",
            correlativo=123,
            fecha_emision=datetime.now(),
            tipo_moneda="PEN",
            tipo_operacion="01",  # Venta interna
            mto_oper_gravadas=100.00,
            mto_oper_inafectas=0.00,
            mto_oper_exoneradas=0.00,
            mto_impventa=118.00,
            company=self.company_valida,
            client=self.client_valido,
            details=[detalle_invalido]
        )
        
        errors = self.validator.validate(invoice)
        assert len(errors) > 0
        
        # Buscar error de afectación IGV
        igv_error = next((e for e in errors if "igv" in e.message.lower()), None)
        assert igv_error is not None
        assert "99" in igv_error.message
    
    def test_is_valid_method(self):
        """Test método is_valid()."""
        invoice_valida = Invoice(
            tipo_doc="01",
            serie="F001",
            correlativo=123,
            fecha_emision=datetime.now(),
            tipo_moneda="PEN",
            tipo_operacion="01",  # Venta interna
            mto_oper_gravadas=100.00,
            mto_oper_inafectas=0.00,
            mto_oper_exoneradas=0.00,
            mto_impventa=118.00,
            company=self.company_valida,
            client=self.client_valido,
            details=[self.detalle_valido]
        )
        
        assert self.validator.is_valid(invoice_valida) is True
        
        # Invoice inválida
        invoice_invalida = Invoice(
            tipo_doc="01",
            serie="F001",
            correlativo=123,
            fecha_emision=datetime.now(),
            tipo_moneda="INVALID",  # ❌ Moneda inválida
            tipo_operacion="01",  # Venta interna
            mto_oper_gravadas=100.00,
            mto_oper_inafectas=0.00,
            mto_oper_exoneradas=0.00,
            mto_impventa=118.00,
            company=self.company_valida,
            client=self.client_valido,
            details=[self.detalle_valido]
        )
        
        assert self.validator.is_valid(invoice_invalida) is False
    
    def test_get_errors_summary(self):
        """Test método get_errors_summary()."""
        # Sin errores
        summary = self.validator.get_errors_summary([])
        assert summary == "Sin errores"
        
        # Con errores
        errors = [
            ValidationError("field1", "Error 1"),
            ValidationError("field2", "Error 2")
        ]
        
        summary = self.validator.get_errors_summary(errors)
        assert "2 errores" in summary
        assert "field1: Error 1" in summary
        assert "field2: Error 2" in summary
    
    def test_documento_sin_loader(self):
        """Test validación de documento sin loader disponible."""
        class DocumentoDesconocido:
            """Tipo de documento no soportado."""
            pass
        
        doc = DocumentoDesconocido()
        errors = self.validator.validate(doc)
        
        # No debe generar errores si no hay loader
        assert len(errors) == 0


class TestValidationError:
    """Tests para la clase ValidationError."""
    
    def test_crear_validation_error(self):
        """Test creación de ValidationError."""
        error = ValidationError("test_field", "Test message", "test_value")
        
        assert error.field == "test_field"
        assert error.message == "Test message"
        assert error.value == "test_value"
    
    def test_validation_error_str(self):
        """Test representación string de ValidationError."""
        error = ValidationError("test_field", "Test message")
        assert str(error) == "test_field: Test message"
    
    def test_validation_error_repr(self):
        """Test representación repr de ValidationError."""
        error = ValidationError("test_field", "Test message")
        assert repr(error) == "ValidationError(field='test_field', message='Test message')"
    
    def test_validation_error_to_dict(self):
        """Test conversión a diccionario."""
        error = ValidationError("test_field", "Test message", "test_value")
        result = error.to_dict()
        
        expected = {
            'field': 'test_field',
            'message': 'Test message',
            'value': 'test_value'
        }
        
        assert result == expected


class TestValidationIntegration:
    """Tests de integración del validador con documentos reales."""
    
    def setup_method(self):
        self.validator = DocumentValidator()
    
    def test_factura_exportacion_completa(self):
        """Test validación completa de factura de exportación."""
        company = Company(
            ruc="20123456789",
            razon_social="EXPORTADORA PERU S.A.C.",
            address=Address(
                ubigeo="150101",
                departamento="Lima",
                provincia="Lima",
                distrito="Lima",
                direccion="Av. Exportación 456"
            )
        )
        
        client = Client(
            tipo_doc=6,
            num_doc="20987654321",
            razon_social="CLIENTE EXTRANJERO S.A.C."
        )
        
        detalle_exportacion = SaleDetail(
            cod_item="EXP001",
            des_item="Producto de exportación",
            cantidad=10.0,
            mto_valor_unitario=50.00,
            mto_precio_unitario=50.00,  # Sin IGV
            mto_valor_venta=500.00,
            unidad="NIU",
            tip_afe_igv="40",  # Exportación
            porcentaje_igv=0.0,
            igv=0.0
        )
        
        invoice = Invoice(
            tipo_doc="01",
            serie="F001",
            correlativo=100,
            fecha_emision=datetime.now(),
            tipo_moneda="USD",  # Dólares para exportación
            tipo_operacion="02",  # Exportación de bienes
            mto_oper_gravadas=0.00,
            mto_oper_inafectas=0.00,
            mto_oper_exoneradas=0.00,
            mto_oper_exportacion=500.00,  # Total exportación
            mto_impventa=500.00,
            company=company,
            client=client,
            details=[detalle_exportacion]
        )
        
        errors = self.validator.validate(invoice)
        assert len(errors) == 0, f"Errores encontrados: {[str(e) for e in errors]}"
    
    def test_nota_debito_completa(self):
        """Test validación completa de nota de débito."""
        company = Company(
            ruc="20123456789",
            razon_social="EMPRESA PERU S.A.C.",
            address=Address(
                ubigeo="150101",
                departamento="Lima",
                provincia="Lima", 
                distrito="Lima",
                direccion="Av. Principal 789"
            )
        )
        
        client = Client(
            tipo_doc=6,
            num_doc="20987654321",
            razon_social="CLIENTE EMPRESA S.A.C."
        )
        
        detalle = SaleDetail(
            cod_item="SERV001",
            des_item="Intereses por mora",
            cantidad=1.0,
            mto_valor_unitario=50.00,
            mto_precio_unitario=59.00,
            mto_valor_venta=50.00,
            unidad="ZZ",
            tip_afe_igv="10",
            porcentaje_igv=18.0,
            igv=9.0
        )
        
        note = Note(
            tipo_doc="08",  # Nota de débito
            serie="FD01",
            correlativo=5,
            fecha_emision=datetime.now(),
            tipo_moneda="PEN",
            tipo_operacion="01",  # Para notas de débito
            tip_doc_afectado="01",
            num_doc_afectado="F001-100",
            cod_motivo="01",  # Intereses por mora
            des_motivo="Intereses por mora en el pago",
            mto_oper_gravadas=50.00,
            mto_oper_inafectas=0.00,
            mto_oper_exoneradas=0.00,
            mto_impventa=59.00,
            company=company,
            client=client,
            details=[detalle]
        )
        
        errors = self.validator.validate(note)
        assert len(errors) == 0, f"Errores encontrados: {[str(e) for e in errors]}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])