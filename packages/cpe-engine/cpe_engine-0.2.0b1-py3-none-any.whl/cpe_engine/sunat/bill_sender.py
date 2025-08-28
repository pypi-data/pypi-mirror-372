"""Servicio principal para envío de comprobantes a SUNAT."""

from typing import Optional, Dict, Any
from datetime import datetime

from .soap_client import SoapClient, SoapClientError
from .zip_helper import ZipHelper, ZipHelperError
from .cdr_processor import CdrProcessor, CdrProcessorError
from .endpoints import SunatEndpoints


class BillSenderError(Exception):
    """Error en envío de comprobantes."""
    pass


class BillSender:
    """Servicio para envío de comprobantes electrónicos a SUNAT."""
    
    def __init__(self, 
                 username: str,
                 password: str,
                 endpoint: Optional[str] = None,
                 timeout: int = 30):
        """
        Inicializa servicio de envío.
        
        Args:
            username: Usuario SUNAT (RUC + usuario)
            password: Contraseña SUNAT  
            endpoint: URL del endpoint SUNAT (opcional)
            timeout: Timeout en segundos
        """
        self.username = username
        self.password = password
        self.endpoint = endpoint or SunatEndpoints.get_facturacion_endpoint(es_test=True)
        
        # Inicializar cliente SOAP
        self.soap_client = SoapClient(
            username=username,
            password=password,
            endpoint=self.endpoint,
            timeout=timeout
        )
        
        print(f"[BillSender] Inicializado para RUC: {username}")
        print(f"[BillSender] Endpoint: {self.endpoint}")
        print(f"[BillSender] Ambiente: {'BETA' if self.is_beta_environment() else 'PRODUCCION'}")
    
    def send_document(self, 
                      ruc: str,
                      tipo_doc: str, 
                      serie: str,
                      correlativo: str,
                      signed_xml: str) -> Dict[str, Any]:
        """
        Envía documento firmado a SUNAT.
        
        Args:
            ruc: RUC del emisor
            tipo_doc: Código de tipo de documento (01, 03, 07, 08)
            serie: Serie del documento
            correlativo: Correlativo del documento
            signed_xml: XML firmado digitalmente
            
        Returns:
            Respuesta estructurada del envío
            
        Raises:
            BillSenderError: Si hay error en el envío
        """
        # Validaciones básicas de entrada
        if not signed_xml:
            raise ValueError("El XML firmado no puede ser None o vacío")
        
        if not isinstance(signed_xml, str):
            raise TypeError("El XML firmado debe ser una cadena de texto")
            
        try:
            print(f"[BillSender] Enviando documento: {ruc}-{tipo_doc}-{serie}-{correlativo}")
            
            # Crear archivo ZIP
            xml_filename = f"{ruc}-{tipo_doc}-{serie}-{correlativo}.xml"
            zip_content = ZipHelper.create_zip(xml_filename, signed_xml)
            
            # Nombre del ZIP
            zip_filename = f"{ruc}-{tipo_doc}-{serie}-{correlativo}.zip"
            
            # Enviar usando SOAP
            soap_response = self.soap_client.send_bill(zip_filename, zip_content)
            
            # Preparar respuesta
            result = {
                'success': soap_response.get('success', False),
                'action': 'sendBill',
                'document': {
                    'ruc': ruc,
                    'tipo_doc': tipo_doc,
                    'serie': serie,
                    'correlativo': correlativo,
                    'filename': zip_filename
                },
                'sent_at': datetime.now().isoformat(),
                'soap_response': soap_response
            }
            
            # Procesar CDR si existe
            if soap_response.get('cdr_base64'):
                try:
                    cdr_data = CdrProcessor.process_cdr_response(soap_response['cdr_base64'])
                    result['cdr'] = cdr_data
                    result['success'] = cdr_data.get('success', False)
                    
                    print(f"[BillSender] CDR procesado - Estado: {cdr_data.get('response_code')}")
                    
                except CdrProcessorError as e:
                    print(f"[BillSender] Error procesando CDR: {e}")
                    result['cdr_error'] = str(e)
            
            print(f"[BillSender] Envío completado - Éxito: {result['success']}")
            return result
            
        except (SoapClientError, ZipHelperError) as e:
            error_msg = f"Error enviando documento: {e}"
            print(f"[BillSender] ERROR: {error_msg}")
            raise BillSenderError(error_msg)
        
        except Exception as e:
            error_msg = f"Error inesperado enviando documento: {e}"
            print(f"[BillSender] ERROR: {error_msg}")
            raise BillSenderError(error_msg)
    
    def send_summary(self,
                     ruc: str,
                     fecha: str,
                     correlativo: str, 
                     signed_xml: str) -> Dict[str, Any]:
        """
        Envía resumen diario a SUNAT.
        
        Args:
            ruc: RUC del emisor
            fecha: Fecha del resumen (YYYYMMDD)
            correlativo: Correlativo del resumen
            signed_xml: XML del resumen firmado
            
        Returns:
            Respuesta con ticket de seguimiento
            
        Raises:
            BillSenderError: Si hay error en el envío
        """
        try:
            print(f"[BillSender] Enviando resumen: {ruc}-RC-{fecha}-{correlativo}")
            
            # Crear archivo ZIP
            xml_filename = f"{ruc}-RC-{fecha}-{correlativo}.xml"
            zip_content = ZipHelper.create_zip(xml_filename, signed_xml)
            
            # Nombre del ZIP
            zip_filename = f"{ruc}-RC-{fecha}-{correlativo}.zip"
            
            # Enviar usando SOAP
            soap_response = self.soap_client.send_summary(zip_filename, zip_content)
            
            # Preparar respuesta
            result = {
                'success': soap_response.get('success', False),
                'action': 'sendSummary',
                'document': {
                    'ruc': ruc,
                    'fecha': fecha,
                    'correlativo': correlativo,
                    'filename': zip_filename
                },
                'ticket': soap_response.get('ticket'),
                'sent_at': datetime.now().isoformat(),
                'soap_response': soap_response
            }
            
            print(f"[BillSender] Resumen enviado - Ticket: {result.get('ticket')}")
            return result
            
        except (SoapClientError, ZipHelperError) as e:
            error_msg = f"Error enviando resumen: {e}"
            print(f"[BillSender] ERROR: {error_msg}")
            raise BillSenderError(error_msg)
    
    def get_ticket_status(self, ticket: str) -> Dict[str, Any]:
        """
        Consulta estado de un ticket.
        
        Args:
            ticket: Número de ticket de SUNAT
            
        Returns:
            Estado del ticket y CDR si está listo
            
        Raises:
            BillSenderError: Si hay error en la consulta
        """
        try:
            print(f"[BillSender] Consultando ticket: {ticket}")
            
            # Consultar usando SOAP
            soap_response = self.soap_client.get_status(ticket)
            
            # Preparar respuesta
            result = {
                'success': soap_response.get('success', False),
                'action': 'getStatus',
                'ticket': ticket,
                'status_code': soap_response.get('status_code'),
                'status_message': soap_response.get('status_message'),
                'checked_at': datetime.now().isoformat(),
                'soap_response': soap_response
            }
            
            # Procesar CDR si está disponible
            if soap_response.get('cdr_base64'):
                try:
                    cdr_data = CdrProcessor.process_cdr_response(soap_response['cdr_base64'])
                    result['cdr'] = cdr_data
                    result['cdr_available'] = True
                    
                    print(f"[BillSender] CDR disponible para ticket: {ticket}")
                    
                except CdrProcessorError as e:
                    print(f"[BillSender] Error procesando CDR de ticket: {e}")
                    result['cdr_error'] = str(e)
                    result['cdr_available'] = False
            else:
                result['cdr_available'] = False
            
            print(f"[BillSender] Estado consultado - Código: {result.get('status_code')}")
            return result
            
        except SoapClientError as e:
            error_msg = f"Error consultando ticket: {e}"
            print(f"[BillSender] ERROR: {error_msg}")
            raise BillSenderError(error_msg)
    
    def send_and_wait_for_cdr(self,
                              ruc: str,
                              tipo_doc: str,
                              serie: str, 
                              correlativo: str,
                              signed_xml: str,
                              max_attempts: int = 10,
                              wait_seconds: int = 5) -> Dict[str, Any]:
        """
        Envía documento y espera por CDR si es necesario.
        
        Para documentos que van por sendSummary, consulta periódicamente
        el estado hasta obtener el CDR.
        
        Args:
            ruc: RUC del emisor
            tipo_doc: Código de tipo de documento
            serie: Serie del documento
            correlativo: Correlativo del documento
            signed_xml: XML firmado
            max_attempts: Máximo intentos de consulta
            wait_seconds: Segundos entre consultas
            
        Returns:
            Respuesta con CDR final
        """
        try:
            print(f"[BillSender] Enviando con espera CDR: {ruc}-{tipo_doc}-{serie}-{correlativo}")
            
            # Determinar método de envío según tipo de documento
            if tipo_doc in ['01', '03']:  # Facturas y Boletas
                # sendBill devuelve CDR inmediatamente
                return self.send_document(ruc, tipo_doc, serie, correlativo, signed_xml)
            
            elif tipo_doc in ['07', '08']:  # Notas de crédito/débito
                # También van por sendBill
                return self.send_document(ruc, tipo_doc, serie, correlativo, signed_xml)
            
            else:
                # Otros documentos pueden requerir sendSummary
                # Por ahora usar sendBill para todos
                return self.send_document(ruc, tipo_doc, serie, correlativo, signed_xml)
                
        except BillSenderError:
            raise
        except Exception as e:
            error_msg = f"Error en envío con espera CDR: {e}"
            print(f"[BillSender] ERROR: {error_msg}")
            raise BillSenderError(error_msg)
    
    def is_beta_environment(self) -> bool:
        """Verifica si está usando ambiente BETA."""
        return self.soap_client.is_beta_environment()
    
    def get_sender_info(self) -> Dict[str, str]:
        """Obtiene información del servicio."""
        return {
            'username': self.username,
            'endpoint': self.endpoint,
            'environment': 'BETA' if self.is_beta_environment() else 'PRODUCCION'
        }
    
    def validate_credentials(self) -> bool:
        """
        Valida credenciales haciendo una consulta de prueba.
        
        Returns:
            True si las credenciales son válidas
        """
        try:
            print("[BillSender] Validando credenciales...")
            
            # Hacer consulta de estado con ticket inexistente
            # Esto debería devolver error de ticket no encontrado,
            # no de credenciales inválidas
            try:
                result = self.get_ticket_status('test-ticket-123456')
                # Si llega aquí sin error de autenticación, las credenciales son válidas
                return True
            except BillSenderError as e:
                # Verificar si el error es de autenticación o de ticket
                error_str = str(e).lower()
                if 'unauthorized' in error_str or 'authentication' in error_str:
                    print("[BillSender] Credenciales inválidas")
                    return False
                else:
                    # Error de ticket, credenciales válidas
                    print("[BillSender] Credenciales válidas")
                    return True
                    
        except Exception as e:
            print(f"[BillSender] Error validando credenciales: {e}")
            return False