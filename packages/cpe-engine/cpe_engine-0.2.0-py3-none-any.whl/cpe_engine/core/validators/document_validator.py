"""Validador de documentos usando catálogos SUNAT."""

from typing import List, Optional

from ...catalogs.sunat_catalogs import (
    CODIGOS_AFECTACION_IGV,
    MOTIVOS_NOTA_CREDITO,
    MOTIVOS_NOTA_DEBITO,
    TIPOS_DOCUMENTOS,
    TIPOS_DOCUMENTO_IDENTIDAD,
    TIPOS_MONEDA,
    TIPOS_OPERACION,
    UNIDADES_MEDIDA,
    validar_afectacion_igv,
    validar_motivo_nota_credito,
    validar_motivo_nota_debito,
    validar_tipo_documento,
    validar_tipo_documento_identidad,
    validar_tipo_moneda,
    validar_tipo_operacion,
    validar_unidad_medida,
)


class ValidationError(Exception):
    """Error de validación de documento."""
    pass


class DocumentValidator:
    """Validador de documentos electrónicos según normativas SUNAT."""
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def clear_errors(self) -> None:
        """Limpia errores y warnings previos."""
        self.errors.clear()
        self.warnings.clear()
    
    def add_error(self, message: str) -> None:
        """Agrega un error de validación."""
        self.errors.append(message)
        print(f"[Validator] ERROR: {message}")
    
    def add_warning(self, message: str) -> None:
        """Agrega un warning de validación."""
        self.warnings.append(message)
        print(f"[Validator] WARNING: {message}")
    
    def has_errors(self) -> bool:
        """Determina si hay errores de validación."""
        return len(self.errors) > 0
    
    def validate_company(self, company) -> bool:
        """Valida datos de la empresa."""
        print(f"[Validator] Validando empresa: {company.razon_social}")
        
        # Validar RUC
        if not company.ruc or len(company.ruc) != 11:
            self.add_error(f"RUC debe tener 11 dígitos: {company.ruc}")
            
        if not company.ruc.isdigit():
            self.add_error(f"RUC debe ser numérico: {company.ruc}")
            
        # Validar tipo de documento
        if not validar_tipo_documento_identidad(company.tipo_doc):
            self.add_error(f"Tipo documento empresa inválido: {company.tipo_doc}")
        elif company.tipo_doc != "6":
            self.add_warning(f"Empresa debería tener tipo documento 6 (RUC), actual: {company.tipo_doc}")
        
        # Validar razón social
        if not company.razon_social.strip():
            self.add_error("Razón social de empresa es requerida")
            
        return not self.has_errors()
    
    def validate_client(self, client) -> bool:
        """Valida datos del cliente."""
        print(f"[Validator] Validando cliente: {client.razon_social}")
        
        # Validar tipo de documento
        if not validar_tipo_documento_identidad(client.tipo_doc):
            self.add_error(f"Tipo documento cliente inválido: {client.tipo_doc}")
        
        # Validar número de documento según tipo
        if client.tipo_doc == "1":  # DNI
            if not client.num_doc or len(client.num_doc) != 8:
                self.add_error(f"DNI debe tener 8 dígitos: {client.num_doc}")
            if not client.num_doc.isdigit():
                self.add_error(f"DNI debe ser numérico: {client.num_doc}")
                
        elif client.tipo_doc == "6":  # RUC  
            if not client.num_doc or len(client.num_doc) != 11:
                self.add_error(f"RUC debe tener 11 dígitos: {client.num_doc}")
            if not client.num_doc.isdigit():
                self.add_error(f"RUC debe ser numérico: {client.num_doc}")
        
        # Validar razón social
        if not client.razon_social.strip():
            self.add_error("Razón social de cliente es requerida")
            
        return not self.has_errors()
    
    def validate_address(self, address, context: str = "") -> bool:
        """Valida datos de dirección."""
        if not address:
            return True  # Dirección es opcional
            
        print(f"[Validator] Validando dirección {context}")
        
        # Validar ubigeo si está presente
        if address.ubigeo:
            if len(address.ubigeo) != 6:
                self.add_error(f"Ubigeo debe tener 6 dígitos: {address.ubigeo}")
            if not address.ubigeo.isdigit():
                self.add_error(f"Ubigeo debe ser numérico: {address.ubigeo}")
                
        return not self.has_errors()
    
    def validate_sale_detail(self, detail) -> bool:
        """Valida detalle de venta."""
        print(f"[Validator] Validando detalle: {detail.descripcion}")
        
        # Validar descripción
        if not detail.descripcion.strip():
            self.add_error("Descripción del producto es requerida")
            
        # Validar cantidad
        if detail.cantidad <= 0:
            self.add_error(f"Cantidad debe ser mayor a 0: {detail.cantidad}")
            
        # Validar unidad de medida
        if not validar_unidad_medida(detail.unidad):
            self.add_error(f"Unidad de medida inválida: {detail.unidad}")
            
        # Validar código de afectación IGV
        if not validar_afectacion_igv(detail.tip_afe_igv):
            self.add_error(f"Código afectación IGV inválido: {detail.tip_afe_igv}")
            
        # Validar valores monetarios
        if detail.mto_valor_unitario < 0:
            self.add_error(f"Valor unitario no puede ser negativo: {detail.mto_valor_unitario}")
            
        if detail.mto_valor_venta < 0:
            self.add_error(f"Valor de venta no puede ser negativo: {detail.mto_valor_venta}")
            
        return not self.has_errors()
    
    def validate_invoice(self, invoice) -> bool:
        """Valida factura o boleta completa."""
        print(f"[Validator] Validando {invoice.get_tipo_comprobante_desc()}: {invoice.get_nombre()}")
        
        self.clear_errors()
        
        # Validar tipo de documento
        if not validar_tipo_documento(invoice.tipo_doc):
            self.add_error(f"Tipo de documento inválido: {invoice.tipo_doc}")
        
        # Validar serie y correlativo
        if not invoice.serie.strip():
            self.add_error("Serie es requerida")
        if not invoice.correlativo.strip():
            self.add_error("Correlativo es requerido")
            
        # Validar tipo de operación
        if not validar_tipo_operacion(invoice.tipo_operacion):
            self.add_error(f"Tipo de operación inválido: {invoice.tipo_operacion}")
            
        # Validar moneda
        if not validar_tipo_moneda(invoice.tipo_moneda):
            self.add_error(f"Tipo de moneda inválido: {invoice.tipo_moneda}")
            
        # Validar entidades
        if invoice.company:
            self.validate_company(invoice.company)
        else:
            self.add_error("Company es requerida")
            
        if invoice.client:
            self.validate_client(invoice.client)
        else:
            self.add_error("Client es requerido")
            
        # Validar direcciones
        if invoice.company and invoice.company.address:
            self.validate_address(invoice.company.address, "empresa")
            
        if invoice.client and invoice.client.address:
            self.validate_address(invoice.client.address, "cliente")
            
        # Validar detalles
        if not invoice.details:
            self.add_error("Debe tener al menos un detalle")
        else:
            for i, detail in enumerate(invoice.details):
                self.validate_sale_detail(detail)
                
        # Validar totales básicos
        if invoice.mto_impventa <= 0:
            self.add_error(f"Total debe ser mayor a 0: {invoice.mto_impventa}")
            
        # Validar coherencia tipo documento vs cliente
        if invoice.tipo_doc == "01" and invoice.client and not invoice.client.is_persona_juridica():
            self.add_warning("Factura (01) generalmente es para personas jurídicas (RUC)")
        elif invoice.tipo_doc == "03" and invoice.client and invoice.client.is_persona_juridica():
            self.add_warning("Boleta (03) generalmente es para personas naturales (DNI)")
            
        return not self.has_errors()
    
    def validate_note(self, note) -> bool:
        """Valida nota de crédito o débito completa."""
        print(f"[Validator] Validando {note.get_tipo_comprobante_desc()}: {note.get_nombre()}")
        
        self.clear_errors()
        
        # Validar tipo de documento
        if not validar_tipo_documento(note.tipo_doc):
            self.add_error(f"Tipo de documento inválido: {note.tipo_doc}")
            
        # Validar motivos según tipo de nota
        if note.tipo_doc == "07":  # Nota de crédito
            if not validar_motivo_nota_credito(note.cod_motivo):
                self.add_error(f"Motivo nota crédito inválido: {note.cod_motivo}")
        elif note.tipo_doc == "08":  # Nota de débito
            if not validar_motivo_nota_debito(note.cod_motivo):
                self.add_error(f"Motivo nota débito inválido: {note.cod_motivo}")
                
        # Validar documento afectado
        if not validar_tipo_documento(note.tip_doc_afectado):
            self.add_error(f"Tipo documento afectado inválido: {note.tip_doc_afectado}")
            
        if not note.num_doc_afectado.strip():
            self.add_error("Número de documento afectado es requerido")
            
        # Validar serie y correlativo
        if not note.serie.strip():
            self.add_error("Serie es requerida")
        if not note.correlativo.strip():
            self.add_error("Correlativo es requerido")
            
        # Validar entidades (usar misma lógica que factura)
        if note.company:
            self.validate_company(note.company)
        else:
            self.add_error("Company es requerida")
            
        if note.client:
            self.validate_client(note.client)
        else:
            self.add_error("Client es requerido")
            
        # Validar detalles
        if not note.details:
            self.add_error("Debe tener al menos un detalle")
        else:
            for detail in note.details:
                self.validate_sale_detail(detail)
                
        return not self.has_errors()