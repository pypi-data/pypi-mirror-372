"""Credenciales para servicios SUNAT."""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class SunatCredentials:
    """Credenciales para acceso a servicios SUNAT."""
    
    ruc: str
    usuario: str  # Usuario completo SUNAT (RUC + usuario, ej: 20123456789MODDATOS)
    password: str
    certificado: str  # Contenido PEM como string O path al archivo
    es_test: bool = True
    
    def __post_init__(self):
        """Validaciones post-inicialización."""
        if not self.ruc or len(self.ruc) != 11:
            raise ValueError("RUC debe tener 11 dígitos")
        
        if not self.usuario:
            raise ValueError("Usuario SUNAT es obligatorio")
        
        if not self.password:
            raise ValueError("Password es obligatorio")
        
        if not self.certificado:
            raise ValueError("Certificado es obligatorio")
    
    @property
    def es_certificado_archivo(self) -> bool:
        """Determina si el certificado es un path a archivo."""
        return not self.certificado.startswith("-----BEGIN")
    
    @property 
    def contenido_certificado(self) -> str:
        """Obtiene el contenido del certificado como string."""
        if self.es_certificado_archivo:
            return Path(self.certificado).read_text(encoding="utf-8")
        return self.certificado
    
    def validar_certificado(self) -> bool:
        """Valida que el certificado sea PEM válido."""
        try:
            contenido = self.contenido_certificado
            return (
                "-----BEGIN CERTIFICATE-----" in contenido
                and "-----END CERTIFICATE-----" in contenido
            )
        except Exception:
            return False