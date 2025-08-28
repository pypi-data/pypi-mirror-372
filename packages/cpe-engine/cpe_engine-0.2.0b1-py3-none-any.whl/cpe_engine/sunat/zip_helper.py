"""Utilidades para compresión ZIP de documentos SUNAT."""

import zipfile
from io import BytesIO
from typing import Optional


class ZipHelperError(Exception):
    """Error en utilidades ZIP."""
    pass


class ZipHelper:
    """Utilidad para crear archivos ZIP según formato SUNAT."""
    
    @staticmethod
    def create_zip(xml_filename: str, xml_content: str) -> bytes:
        """
        Crea un archivo ZIP con el XML firmado.
        
        SUNAT requiere que los XMLs se envíen comprimidos en ZIP.
        
        Args:
            xml_filename: Nombre del archivo XML (ej: 20123456789-01-F001-123.xml)
            xml_content: Contenido del XML firmado
            
        Returns:
            Contenido del ZIP en bytes
            
        Raises:
            ZipHelperError: Si hay error creando el ZIP
        """
        try:
            print(f"[ZipHelper] Creando ZIP: {xml_filename} ({len(xml_content)} caracteres)")
            
            # Crear ZIP en memoria
            zip_buffer = BytesIO()
            
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zipf:
                # Agregar XML al ZIP
                zipf.writestr(xml_filename, xml_content.encode('utf-8'))
            
            # Obtener contenido del ZIP
            zip_content = zip_buffer.getvalue()
            zip_buffer.close()
            
            print(f"[ZipHelper] ZIP creado exitosamente ({len(zip_content)} bytes)")
            print(f"[ZipHelper] Ratio compresión: {len(xml_content)}/{len(zip_content)} = {len(xml_content)/len(zip_content):.2f}x")
            
            return zip_content
            
        except Exception as e:
            error_msg = f"Error creando ZIP: {e}"
            print(f"[ZipHelper] ERROR: {error_msg}")
            raise ZipHelperError(error_msg)
    
    @staticmethod
    def extract_xml_from_zip(zip_content: bytes) -> Optional[str]:
        """
        Extrae el primer archivo XML de un ZIP.
        
        Útil para procesar CDRs que vienen en ZIP desde SUNAT.
        
        Args:
            zip_content: Contenido del ZIP en bytes
            
        Returns:
            Contenido del XML como string, None si no hay XML
            
        Raises:
            ZipHelperError: Si hay error extrayendo
        """
        try:
            print(f"[ZipHelper] Extrayendo XML de ZIP ({len(zip_content)} bytes)")
            
            # Crear ZIP desde bytes
            zip_buffer = BytesIO(zip_content)
            
            with zipfile.ZipFile(zip_buffer, 'r') as zipf:
                # Listar archivos en el ZIP
                file_list = zipf.namelist()
                print(f"[ZipHelper] Archivos en ZIP: {file_list}")
                
                # Buscar primer archivo XML
                xml_filename = None
                for filename in file_list:
                    if filename.lower().endswith('.xml'):
                        xml_filename = filename
                        break
                
                if not xml_filename:
                    print("[ZipHelper] No se encontró archivo XML en el ZIP")
                    return None
                
                # Extraer contenido XML
                xml_content = zipf.read(xml_filename).decode('utf-8')
                
                print(f"[ZipHelper] XML extraído: {xml_filename} ({len(xml_content)} caracteres)")
                return xml_content
            
        except Exception as e:
            error_msg = f"Error extrayendo XML de ZIP: {e}"
            print(f"[ZipHelper] ERROR: {error_msg}")
            raise ZipHelperError(error_msg)
    
    @staticmethod
    def validate_zip_structure(zip_content: bytes) -> bool:
        """
        Valida que el ZIP tenga estructura válida para SUNAT.
        
        Args:
            zip_content: Contenido del ZIP en bytes
            
        Returns:
            True si la estructura es válida
        """
        try:
            print(f"[ZipHelper] Validando estructura ZIP ({len(zip_content)} bytes)")
            
            zip_buffer = BytesIO(zip_content)
            
            with zipfile.ZipFile(zip_buffer, 'r') as zipf:
                # Verificar que no esté corrupto
                test_result = zipf.testzip()
                if test_result:
                    print(f"[ZipHelper] ZIP corrupto en archivo: {test_result}")
                    return False
                
                # Verificar que contenga al menos un archivo
                file_list = zipf.namelist()
                if not file_list:
                    print("[ZipHelper] ZIP vacío")
                    return False
                
                # Verificar que contenga al menos un XML
                has_xml = any(f.lower().endswith('.xml') for f in file_list)
                if not has_xml:
                    print("[ZipHelper] ZIP no contiene archivos XML")
                    return False
                
                print(f"[ZipHelper] ZIP válido con {len(file_list)} archivo(s)")
                return True
            
        except Exception as e:
            print(f"[ZipHelper] Error validando ZIP: {e}")
            return False
    
    @staticmethod
    def get_zip_filename(ruc: str, tipo_doc: str, serie: str, correlativo: str) -> str:
        """
        Genera nombre de archivo ZIP según formato SUNAT.
        
        Args:
            ruc: RUC del emisor
            tipo_doc: Código de tipo de documento (01, 03, 07, 08)
            serie: Serie del documento
            correlativo: Correlativo del documento
            
        Returns:
            Nombre del archivo ZIP (ej: 20123456789-01-F001-123.zip)
        """
        return f"{ruc}-{tipo_doc}-{serie}-{correlativo}.zip"
    
    @staticmethod
    def get_xml_filename_from_zip_name(zip_filename: str) -> str:
        """
        Obtiene nombre de XML a partir del nombre de ZIP.
        
        Args:
            zip_filename: Nombre del ZIP (ej: 20123456789-01-F001-123.zip)
            
        Returns:
            Nombre del XML (ej: 20123456789-01-F001-123.xml)
        """
        if zip_filename.lower().endswith('.zip'):
            return zip_filename[:-4] + '.xml'
        return zip_filename + '.xml'
    
    @staticmethod
    def save_zip_file(zip_content: bytes, output_path: str) -> None:
        """
        Guarda contenido ZIP en archivo.
        
        Args:
            zip_content: Contenido del ZIP en bytes
            output_path: Ruta donde guardar
            
        Raises:
            ZipHelperError: Si hay error guardando
        """
        try:
            print(f"[ZipHelper] Guardando ZIP en: {output_path}")
            
            with open(output_path, 'wb') as f:
                f.write(zip_content)
            
            print(f"[ZipHelper] ZIP guardado exitosamente ({len(zip_content)} bytes)")
            
        except Exception as e:
            error_msg = f"Error guardando ZIP: {e}"
            print(f"[ZipHelper] ERROR: {error_msg}")
            raise ZipHelperError(error_msg)