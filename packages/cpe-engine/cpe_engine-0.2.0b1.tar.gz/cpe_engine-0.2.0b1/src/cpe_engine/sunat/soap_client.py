"""Cliente SOAP para servicios SUNAT."""

import base64
import zipfile
from io import BytesIO
from typing import Optional, Dict, Any
import requests
from requests.auth import HTTPBasicAuth
from lxml import etree

from .endpoints import SunatEndpoints


class SoapClientError(Exception):
    """Error en cliente SOAP."""
    pass


class SoapClient:
    """Cliente SOAP para comunicación con SUNAT."""
    
    def __init__(self, 
                 username: str,
                 password: str, 
                 endpoint: Optional[str] = None,
                 timeout: int = 30):
        """
        Inicializa cliente SOAP.
        
        Args:
            username: Usuario SUNAT (RUC + usuario)
            password: Contraseña SUNAT
            endpoint: URL del endpoint (por defecto BETA)
            timeout: Timeout en segundos
        """
        self.username = username
        self.password = password
        self.endpoint = endpoint or SunatEndpoints.get_facturacion_endpoint(es_test=True)
        self.timeout = timeout
        
        # Headers estándar para SOAP
        self.headers = {
            'Content-Type': 'text/xml; charset=utf-8',
            'SOAPAction': '',
            'User-Agent': 'cpe-sc-engine/1.0'
        }
        
        print(f"[SoapClient] Inicializado para endpoint: {self.endpoint}")
    
    def send_bill(self, zip_filename: str, zip_content: bytes) -> Dict[str, Any]:
        """
        Envía un comprobante a SUNAT usando sendBill.
        
        Args:
            zip_filename: Nombre del archivo ZIP
            zip_content: Contenido del ZIP en bytes
            
        Returns:
            Respuesta de SUNAT
        """
        print(f"[SoapClient] Enviando archivo: {zip_filename} ({len(zip_content)} bytes)")
        
        # Codificar ZIP en base64
        zip_base64 = base64.b64encode(zip_content).decode('utf-8')
        
        # Crear envelope SOAP para sendBill
        soap_body = self._build_send_bill_envelope(zip_filename, zip_base64)
        
        return self._send_soap_request(soap_body, 'sendBill')
    
    def send_summary(self, zip_filename: str, zip_content: bytes) -> Dict[str, Any]:
        """
        Envía un resumen diario a SUNAT usando sendSummary.
        
        Args:
            zip_filename: Nombre del archivo ZIP
            zip_content: Contenido del ZIP en bytes
            
        Returns:
            Respuesta de SUNAT
        """
        print(f"[SoapClient] Enviando resumen: {zip_filename} ({len(zip_content)} bytes)")
        
        # Codificar ZIP en base64
        zip_base64 = base64.b64encode(zip_content).decode('utf-8')
        
        # Crear envelope SOAP para sendSummary
        soap_body = self._build_send_summary_envelope(zip_filename, zip_base64)
        
        return self._send_soap_request(soap_body, 'sendSummary')
    
    def get_status(self, ticket: str) -> Dict[str, Any]:
        """
        Consulta el estado de un ticket usando getStatus.
        
        Args:
            ticket: Número de ticket de SUNAT
            
        Returns:
            Respuesta de SUNAT con estado
        """
        print(f"[SoapClient] Consultando ticket: {ticket}")
        
        # Crear envelope SOAP para getStatus
        soap_body = self._build_get_status_envelope(ticket)
        
        return self._send_soap_request(soap_body, 'getStatus')
    
    def _build_send_bill_envelope(self, filename: str, zip_base64: str) -> str:
        """
        Construye envelope SOAP para sendBill.
        
        Args:
            filename: Nombre del archivo
            zip_base64: ZIP codificado en base64
            
        Returns:
            XML del envelope SOAP
        """
        return f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" 
               xmlns:ser="http://service.sunat.gob.pe" 
               xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">
    <soap:Header>
        <wsse:Security>
            <wsse:UsernameToken>
                <wsse:Username>{self.username}</wsse:Username>
                <wsse:Password>{self.password}</wsse:Password>
            </wsse:UsernameToken>
        </wsse:Security>
    </soap:Header>
    <soap:Body>
        <ser:sendBill>
            <fileName>{filename}</fileName>
            <contentFile>{zip_base64}</contentFile>
        </ser:sendBill>
    </soap:Body>
</soap:Envelope>"""
    
    def _build_send_summary_envelope(self, filename: str, zip_base64: str) -> str:
        """
        Construye envelope SOAP para sendSummary.
        
        Args:
            filename: Nombre del archivo
            zip_base64: ZIP codificado en base64
            
        Returns:
            XML del envelope SOAP
        """
        return f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" 
               xmlns:ser="http://service.sunat.gob.pe" 
               xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">
    <soap:Header>
        <wsse:Security>
            <wsse:UsernameToken>
                <wsse:Username>{self.username}</wsse:Username>
                <wsse:Password>{self.password}</wsse:Password>
            </wsse:UsernameToken>
        </wsse:Security>
    </soap:Header>
    <soap:Body>
        <ser:sendSummary>
            <fileName>{filename}</fileName>
            <contentFile>{zip_base64}</contentFile>
        </ser:sendSummary>
    </soap:Body>
</soap:Envelope>"""
    
    def _build_get_status_envelope(self, ticket: str) -> str:
        """
        Construye envelope SOAP para getStatus.
        
        Args:
            ticket: Número de ticket
            
        Returns:
            XML del envelope SOAP
        """
        return f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" 
               xmlns:ser="http://service.sunat.gob.pe" 
               xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">
    <soap:Header>
        <wsse:Security>
            <wsse:UsernameToken>
                <wsse:Username>{self.username}</wsse:Username>
                <wsse:Password>{self.password}</wsse:Password>
            </wsse:UsernameToken>
        </wsse:Security>
    </soap:Header>
    <soap:Body>
        <ser:getStatus>
            <ticket>{ticket}</ticket>
        </ser:getStatus>
    </soap:Body>
</soap:Envelope>"""
    
    def _send_soap_request(self, soap_body: str, action: str) -> Dict[str, Any]:
        """
        Envía petición SOAP a SUNAT.
        
        Args:
            soap_body: XML del envelope SOAP
            action: Acción SOAP (sendBill, getStatus, etc.)
            
        Returns:
            Respuesta procesada de SUNAT
        """
        try:
            # Configurar headers específicos para la acción
            headers = self.headers.copy()
            headers['SOAPAction'] = f'urn:{action}'
            
            print(f"[SoapClient] Enviando petición SOAP: {action}")
            print(f"[SoapClient] URL: {self.endpoint}")
            print(f"[SoapClient] Usuario: {self.username}")
            
            # Realizar petición HTTP POST con sesión nueva para cada llamada
            # SUNAT requiere conexiones independientes - no reutilizar conexiones
            with requests.Session() as session:
                response = session.post(
                    self.endpoint,
                    data=soap_body,
                    headers=headers,
                    timeout=self.timeout,
                    verify=True  # Verificar SSL
                )
            
            print(f"[SoapClient] Respuesta HTTP: {response.status_code}")
            
            # Verificar código de respuesta
            if response.status_code != 200:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                print(f"[SoapClient] ERROR: {error_msg}")
                raise SoapClientError(error_msg)
            
            # Procesar respuesta XML
            return self._parse_soap_response(response.text, action)
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Error de red: {e}"
            print(f"[SoapClient] ERROR: {error_msg}")
            raise SoapClientError(error_msg)
        
        except Exception as e:
            error_msg = f"Error inesperado: {e}"
            print(f"[SoapClient] ERROR: {error_msg}")
            raise SoapClientError(error_msg)
    
    def _parse_soap_response(self, response_xml: str, action: str) -> Dict[str, Any]:
        """
        Parsea la respuesta SOAP de SUNAT.
        
        Args:
            response_xml: XML de respuesta
            action: Acción que se ejecutó
            
        Returns:
            Datos estructurados de la respuesta
        """
        try:
            print(f"[SoapClient] Parseando respuesta SOAP para: {action}")
            
            # Parsear XML de respuesta
            root = etree.fromstring(response_xml.encode('utf-8'))
            
            # Definir namespaces SOAP
            namespaces = {
                'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
                'ser': 'http://service.sunat.gob.pe'
            }
            
            # Verificar si hay fault
            fault = root.xpath('//soap:Fault', namespaces=namespaces)
            if fault:
                fault_code = root.xpath('//faultcode/text()', namespaces=namespaces)
                fault_string = root.xpath('//faultstring/text()', namespaces=namespaces)
                
                error_msg = f"SOAP Fault: {fault_code[0] if fault_code else 'Unknown'} - {fault_string[0] if fault_string else 'Unknown error'}"
                print(f"[SoapClient] SOAP Fault: {error_msg}")
                raise SoapClientError(error_msg)
            
            # Parsear según la acción
            if action == 'sendBill':
                return self._parse_send_bill_response(root, namespaces)
            elif action == 'sendSummary':
                return self._parse_send_summary_response(root, namespaces)
            elif action == 'getStatus':
                return self._parse_get_status_response(root, namespaces)
            else:
                raise SoapClientError(f"Acción no soportada: {action}")
                
        except etree.XMLSyntaxError as e:
            error_msg = f"XML de respuesta inválido: {e}"
            print(f"[SoapClient] ERROR: {error_msg}")
            raise SoapClientError(error_msg)
    
    def _parse_send_bill_response(self, root, namespaces: Dict[str, str]) -> Dict[str, Any]:
        """Parsea respuesta de sendBill."""
        try:
            # Buscar elementos de respuesta
            application_response = root.xpath('//ser:applicationResponse/text()', namespaces=namespaces)
            
            result = {
                'success': True,
                'action': 'sendBill',
                'cdr_base64': application_response[0] if application_response else None,
                'raw_response': etree.tostring(root, encoding='unicode')
            }
            
            if result['cdr_base64']:
                print("[SoapClient] sendBill exitoso - CDR recibido")
            else:
                print("[SoapClient] sendBill sin CDR en respuesta")
            
            return result
            
        except Exception as e:
            raise SoapClientError(f"Error parseando respuesta sendBill: {e}")
    
    def _parse_send_summary_response(self, root, namespaces: Dict[str, str]) -> Dict[str, Any]:
        """Parsea respuesta de sendSummary."""
        try:
            # sendSummary devuelve un ticket
            ticket = root.xpath('//ser:ticket/text()', namespaces=namespaces)
            
            result = {
                'success': True,
                'action': 'sendSummary',
                'ticket': ticket[0] if ticket else None,
                'raw_response': etree.tostring(root, encoding='unicode')
            }
            
            if result['ticket']:
                print(f"[SoapClient] sendSummary exitoso - Ticket: {result['ticket']}")
            else:
                print("[SoapClient] sendSummary sin ticket en respuesta")
            
            return result
            
        except Exception as e:
            raise SoapClientError(f"Error parseando respuesta sendSummary: {e}")
    
    def _parse_get_status_response(self, root, namespaces: Dict[str, str]) -> Dict[str, Any]:
        """Parsea respuesta de getStatus."""
        try:
            # getStatus puede devolver CDR o estado
            status_code = root.xpath('//ser:statusCode/text()', namespaces=namespaces)
            status_message = root.xpath('//ser:statusMessage/text()', namespaces=namespaces)
            cdr_response = root.xpath('//ser:content/text()', namespaces=namespaces)
            
            result = {
                'success': True,
                'action': 'getStatus',
                'status_code': status_code[0] if status_code else None,
                'status_message': status_message[0] if status_message else None,
                'cdr_base64': cdr_response[0] if cdr_response else None,
                'raw_response': etree.tostring(root, encoding='unicode')
            }
            
            print(f"[SoapClient] getStatus - Código: {result['status_code']}, Mensaje: {result['status_message']}")
            
            return result
            
        except Exception as e:
            raise SoapClientError(f"Error parseando respuesta getStatus: {e}")
    
    def is_beta_environment(self) -> bool:
        """Determina si se está usando ambiente BETA."""
        return SunatEndpoints.is_test_endpoint(self.endpoint)
    
    def get_endpoint_info(self) -> Dict[str, str]:
        """Obtiene información del endpoint actual."""
        return {
            'endpoint': self.endpoint,
            'environment': 'BETA' if self.is_beta_environment() else 'PRODUCCION',
            'username': self.username
        }