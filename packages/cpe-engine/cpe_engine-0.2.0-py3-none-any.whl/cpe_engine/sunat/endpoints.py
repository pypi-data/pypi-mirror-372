"""Endpoints de SUNAT para servicios de facturación electrónica."""


class SunatEndpoints:
    """Endpoints oficiales de SUNAT."""
    
    # SERVICIOS DE FACTURACIÓN - TEST
    FE_BETA = "https://e-beta.sunat.gob.pe/ol-ti-itcpfegem-beta/billService"
    FE_BETA_WSDL = "https://e-beta.sunat.gob.pe/ol-ti-itcpfegem-beta/billService?wsdl"
    
    # SERVICIOS DE RETENCIÓN Y PERCEPCIÓN - TEST
    RETENCION_BETA = "https://e-beta.sunat.gob.pe/ol-ti-itemision-otroscpe-gem-beta/billService"
    RETENCION_BETA_WSDL = "https://e-beta.sunat.gob.pe/ol-ti-itemision-otroscpe-gem-beta/billService?wsdl"
    
    # SERVICIOS DE FACTURACIÓN - PRODUCCIÓN
    FE_PRODUCCION = "https://e-factura.sunat.gob.pe/ol-ti-itcpfegem/billService"
    FE_PRODUCCION_WSDL = "https://e-factura.sunat.gob.pe/ol-ti-itcpfegem/billService?wsdl"
    
    # SERVICIOS DE RETENCIÓN Y PERCEPCIÓN - PRODUCCIÓN
    RETENCION_PRODUCCION = "https://e-factura.sunat.gob.pe/ol-ti-itemision-otroscpe-gem/billService"
    RETENCION_PRODUCCION_WSDL = "https://e-factura.sunat.gob.pe/ol-ti-itemision-otroscpe-gem/billService?wsdl"
    
    # SERVICIOS DE CONSULTA - PRODUCCIÓN (para futuras versiones)
    CONSULTA_VALIDEZ = "https://e-factura.sunat.gob.pe/ol-it-wsconsvalidcpe/billValidService"
    CONSULTA_VALIDEZ_WSDL = "https://e-factura.sunat.gob.pe/ol-it-wsconsvalidcpe/billValidService?wsdl"
    CONSULTA_CDR = "https://e-factura.sunat.gob.pe/ol-it-wsconscpegem/billConsultService"
    CONSULTA_CDR_WSDL = "https://e-factura.sunat.gob.pe/ol-it-wsconscpegem/billConsultService?wsdl"
    
    # SERVICIOS DEPRECADOS (mantener para compatibilidad)
    FE_HOMOLOGACION = "https://www.sunat.gob.pe/ol-ti-itcpgem-sqa/billService"
    GUIA_BETA = "https://e-beta.sunat.gob.pe/ol-ti-itemision-guia-gem-beta/billService"
    GUIA_PRODUCCION = "https://e-guiaremision.sunat.gob.pe/ol-ti-itemision-guia-gem/billService"
    
    @classmethod
    def get_facturacion_endpoint(cls, es_test: bool = True) -> str:
        """Obtiene el endpoint de facturación según el ambiente."""
        return cls.FE_BETA if es_test else cls.FE_PRODUCCION
    
    @classmethod
    def get_facturacion_wsdl(cls, es_test: bool = True) -> str:
        """Obtiene el WSDL de facturación según el ambiente."""
        return cls.FE_BETA_WSDL if es_test else cls.FE_PRODUCCION_WSDL
    
    @classmethod
    def get_retencion_endpoint(cls, es_test: bool = True) -> str:
        """Obtiene el endpoint de retenciones según el ambiente."""
        return cls.RETENCION_BETA if es_test else cls.RETENCION_PRODUCCION
    
    @classmethod
    def get_retencion_wsdl(cls, es_test: bool = True) -> str:
        """Obtiene el WSDL de retenciones según el ambiente."""
        return cls.RETENCION_BETA_WSDL if es_test else cls.RETENCION_PRODUCCION_WSDL
    
    @classmethod
    def is_test_endpoint(cls, endpoint: str) -> bool:
        """Determina si un endpoint es de ambiente TEST."""
        return "beta" in endpoint.lower()
    
    @classmethod
    def is_production_endpoint(cls, endpoint: str) -> bool:
        """Determina si un endpoint es de producción."""
        return "e-factura.sunat.gob.pe" in endpoint.lower()