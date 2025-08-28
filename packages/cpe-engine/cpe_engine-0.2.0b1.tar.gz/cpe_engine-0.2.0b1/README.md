# cpe-engine

Sistema de Emisión del Contribuyente - Facturación Electrónica Peruana

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](#testing)
[![Production Ready](https://img.shields.io/badge/status-production%20ready-success.svg)](#production-status)

> **🎉 Status: Production Ready** - Comprehensive testing, complete documentation, and verified greenter compatibility.

## Descripción

**cpe-engine** es una librería completa de Python para facturación electrónica peruana que integra con SUNAT. Es un port completo de la librería PHP Greenter, proporcionando funcionalidades end-to-end para generación de documentos, firma digital, y envío a SUNAT.

### Características

- ✅ **Facturas (01)** y **Boletas (03)** - Facturas y recibos
- ✅ **Notas de Crédito (07)** y **Notas de Débito (08)**
- ✅ **35 Catálogos SUNAT oficiales** - Todos los códigos validados contra fuentes oficiales
- ✅ **Validador opcional** - DocumentValidator separado del core (como Greenter/validator)
- ✅ **Mapeo dinámico de tributos** - XML correcto según tipo de operación (gravado, exonerado, exportación)
- ✅ **Arquitectura declarativa** - Compatible 100% con Greenter (no cálculos automáticos)
- ✅ Generación XML UBL 2.1 con templates Jinja2
- ✅ Firmas digitales usando SHA-256 (certificados X.509)
- ✅ Integración SOAP con servicios web SUNAT y procesamiento CDR
- ✅ Compresión ZIP para transmisión de documentos
- ✅ Soporte para ambientes TEST y PRODUCCIÓN
- ✅ API de alto nivel con funciones simples
- ✅ **100% compatible con Greenter** con validaciones adicionales opcionales

## 📚 Documentación de Referencia

**Para desarrolladores y contribuidores:**

- **[API_REFERENCE.md](./API_REFERENCE.md)** - Documentación completa de APIs con firmas exactas y tipos de datos
- **[TEST_PATTERNS.md](./TEST_PATTERNS.md)** - Patrones de testing verificados (usar exactamente estos patrones) 
- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - Arquitectura del sistema y principios de diseño
- **[CLAUDE.md](./CLAUDE.md)** - Guía específica para desarrollo con Claude Code
- **[CHANGELOG.md](./CHANGELOG.md)** - Registro de cambios, mejoras y correcciones por versión

> ⚠️ **Importante**: Lee estos archivos antes de contribuir para evitar errores comunes y patrones incorrectos.

## Instalación

```bash
pip install cpe-engine
```

## Uso Rápido

### 1. Configurar Credenciales

```python
from cpe_engine import SunatCredentials

# Para ambiente de pruebas
credentials = SunatCredentials(
    ruc="20000000001",
    usuario="20000000001MODDATOS",
    password="moddatos",
    certificado=certificado_pem_content,  # Contenido PEM como string
    es_test=True
)

# Para producción
credentials = SunatCredentials(
    ruc="20123456789",
    usuario="20123456789USUARIO1", 
    password="mi_password",
    certificado="/path/to/certificado.pem",  # O path al archivo
    es_test=False
)
```

### 2. Enviar Factura

```python
from cpe_engine import create_invoice_data, send_invoice

# Datos de la empresa
company_data = {
    'ruc': '20000000001',
    'razon_social': 'MI EMPRESA S.A.C.',
    'email': 'facturacion@miempresa.com',
    'address': {
        'ubigeo': '150101',
        'departamento': 'Lima',
        'provincia': 'Lima', 
        'distrito': 'Lima',
        'direccion': 'Av. Principal 123'
    }
}

# Datos del cliente
client_data = {
    'tipo_doc': 6,  # RUC
    'num_doc': '20000000002',
    'razon_social': 'CLIENTE EMPRESA S.A.C.'
}

# Items de la factura
items = [
    {
        'cod_item': 'PROD001',
        'des_item': 'Producto de ejemplo',
        'cantidad': 2,
        'mto_valor_unitario': 100.00,
        'unidad': 'NIU'
    }
]

# Crear datos de factura
invoice_data = create_invoice_data(
    serie='F001',
    correlativo=123,
    company_data=company_data,
    client_data=client_data,
    items=items
)

# Enviar a SUNAT
result = send_invoice(credentials, invoice_data)

if result.get('success'):
    print(f"Factura enviada exitosamente: {result}")
else:
    print(f"Error: {result['error']}")
```

### 3. Enviar Nota de Crédito

```python
from cpe_engine import create_note_data, send_credit_note

# Crear datos de nota de crédito
note_data = create_note_data(
    serie='FC01',
    correlativo=1,
    tipo_nota='07',  # Crédito
    documento_afectado='F001-123',
    motivo='Anulación de la operación',
    company_data=company_data,
    client_data=client_data,
    items=items
)

# Enviar a SUNAT
result = send_credit_note(credentials, note_data)
```

## Catálogos SUNAT

La librería incluye **35 catálogos oficiales de SUNAT** descargados directamente de fuentes gubernamentales:

### Importación Directa

```python
# Importar catálogos directamente desde el paquete principal
from cpe_engine import (
    CODIGOS_AFECTACION_IGV,
    TIPOS_MONEDA,
    UNIDADES_MEDIDA,
    TIPOS_OPERACION,
    MOTIVOS_NOTA_CREDITO,
    MOTIVOS_NOTA_DEBITO,
    validar_afectacion_igv,
    validar_tipo_moneda
)
```

### Consultar Catálogos

```python
from cpe_engine import CODIGOS_AFECTACION_IGV, TIPOS_OPERACION

# Ver códigos de afectación IGV disponibles
print("Códigos de afectación IGV:")
for codigo, descripcion in CODIGOS_AFECTACION_IGV.items():
    print(f"  {codigo}: {descripcion}")
# 10: Gravado - Operación Onerosa
# 20: Exonerado - Operación Onerosa  
# 30: Inafecto - Operación Onerosa
# 40: Exportación
# ... y más

# Ver tipos de operación
print("Tipos de operación:")
for codigo, descripcion in TIPOS_OPERACION.items():
    print(f"  {codigo}: {descripcion}")
# 0101: Venta interna
# 0200: Exportación de bienes
# ... y más
```

### Validación de Códigos

```python
from cpe_engine import validar_afectacion_igv, validar_tipo_moneda

# Validar antes de usar
if validar_afectacion_igv("40"):
    print("Código 40 (exportación) es válido")

if validar_tipo_moneda("USD"):
    print("USD es una moneda válida")

# La librería valida automáticamente al crear documentos
try:
    item = SaleDetail(
        cod_item="PROD001",
        des_item="Producto",
        cantidad=1,
        mto_valor_unitario=100.00,
        unidad="INVALID_UNIT",  # ❌ Código inválido
        tip_afe_igv="10"
    )
except ValueError as e:
    print(f"Error de validación: {e}")
    # Error: Código de unidad de medida inválido: 'INVALID_UNIT'
```

### Catálogos Disponibles (35 Catálogos Oficiales)

| Catálogo | Descripción | Fuente Oficial |
|----------|-------------|----------------|
| `TIPOS_DOCUMENTO_IDENTIDAD` | Tipos de documento (DNI, RUC, etc.) | Catálogo 06 |
| `TIPOS_MONEDA` | Monedas (PEN, USD, EUR) | Catálogo 02 |
| `UNIDADES_MEDIDA` | Unidades de medida (NIU, ZZ, KGM, etc.) | Catálogo 03 |
| `CODIGOS_AFECTACION_IGV` | Códigos de afectación del IGV | Catálogo 07 |
| `MOTIVOS_NOTA_CREDITO` | Motivos de notas de crédito | Catálogo 09 |
| `MOTIVOS_NOTA_DEBITO` | Motivos de notas de débito | Catálogo 10 |
| `TIPOS_OPERACION` | Tipos de operación (venta interna, exportación, etc.) | Catálogo 17 |
| `TIPOS_CARGOS_DESCUENTOS` | Tipos de cargos y descuentos | Catálogo 53 |
| `TIPOS_DOCUMENTOS` | Tipos de comprobantes (01, 03, 07, etc.) | Catálogo 01 |
| **+26 catálogos adicionales** | Regímenes, percepciones, tributos, etc. | Catálogos 04-59 |

### Ejemplo: Factura de Exportación

```python
from cpe_engine import create_invoice_data, CODIGOS_AFECTACION_IGV, TIPOS_OPERACION

# Consultar códigos antes de usar
print("Código para exportación:", CODIGOS_AFECTACION_IGV["40"])
print("Operación de exportación:", TIPOS_OPERACION["0200"])

# Crear factura de exportación
items_exportacion = [
    {
        'cod_item': 'EXP001',
        'des_item': 'Producto de exportación',
        'cantidad': 10,
        'mto_valor_unitario': 50.00,
        'unidad': 'NIU',
        'tip_afe_igv': '40'  # Exportación (sin IGV)
    }
]

invoice_data = create_invoice_data(
    serie='F001',
    correlativo=100,
    company_data={...},
    client_data={...},
    items=items_exportacion
)

# El XML generado tendrá automáticamente:
# <cbc:TaxExemptionReasonCode>40</cbc:TaxExemptionReasonCode>
# <cbc:ID>9995</cbc:ID>
# <cbc:Name>EXP</cbc:Name>  
# <cbc:TaxTypeCode>FRE</cbc:TaxTypeCode>
```

### 4. Ejemplo Completo

```python
from cpe_engine import send_invoice, SunatCredentials

def main():
    # Configurar credenciales (ejemplo con ambiente de prueba)
    credenciales = SunatCredentials(
        ruc="20000000001",
        usuario="20000000001MODDATOS",
        password="moddatos", 
        certificado="""-----BEGIN CERTIFICATE-----
        ...tu certificado PEM aquí...
        -----END CERTIFICATE-----""",
        es_test=True  # Cambiar a False para producción
    )
    
    # Datos de la empresa
    empresa_data = {
        'ruc': '20000000001',
        'razon_social': 'MI EMPRESA S.A.C.',
        'nombre_comercial': 'Mi Empresa',
        'email': 'facturacion@miempresa.com',
        'address': {
            'ubigeo': '150101',
            'departamento': 'Lima',
            'provincia': 'Lima',
            'distrito': 'Lima',
            'direccion': 'Av. Principal 123'
        }
    }
    
    # Datos del cliente
    cliente_data = {
        'tipo_doc': 6,  # 6=RUC, 1=DNI, 4=Carné extranjería, etc.
        'num_doc': '20000000002',
        'razon_social': 'CLIENTE EMPRESA S.A.C.'
    }
    
    # Productos/servicios
    items = [
        {
            'cod_item': 'PROD001',
            'des_item': 'Producto ejemplo',
            'cantidad': 2,
            'mto_valor_unitario': 100.00,
            'unidad': 'NIU'  # NIU=Unidad, ZZ=Servicio, etc.
        },
        {
            'cod_item': 'SERV001', 
            'des_item': 'Servicio ejemplo',
            'cantidad': 1,
            'mto_valor_unitario': 50.00,
            'unidad': 'ZZ'
        }
    ]
    
    # Enviar factura
    resultado = send_invoice(
        serie="F001",
        correlativo=123,
        empresa_data=empresa_data,
        cliente_data=cliente_data, 
        items=items,
        credenciales=credenciales
    )
    
    # Procesar resultado
    if resultado.get('success'):
        print("✅ Factura enviada exitosamente")
        
        # Información del CDR (Constancia de Recepción)
        if resultado.get('cdr'):
            cdr = resultado['cdr']
            print(f"Código SUNAT: {cdr.get('response_code')}")
            print(f"Descripción: {cdr.get('description')}")
            
            if cdr.get('notes'):
                print(f"Observaciones: {cdr.get('notes')}")
                
        print(f"XML generado guardado en: {resultado.get('xml_path')}")
    else:
        print("❌ Error al enviar factura:")
        print(f"Error: {resultado.get('error')}")

if __name__ == "__main__":
    main()
```

## API de Bajo Nivel

Para mayor control, puedes usar las clases directamente:

```python
from cpe_engine import Invoice, Company, Client, Address, SaleDetail
from cpe_engine import SignedXmlBuilder
from datetime import datetime

# Crear modelos
company = Company(
    ruc="20000000001",
    razon_social="MI EMPRESA S.A.C.",
    # ...
)

invoice = Invoice(
    serie="F001",
    correlativo=123,
    fecha_emision=datetime.now(),
    # ...
)

# Generar XML, firmar y enviar
builder = SignedXmlBuilder()
result = builder.build_sign_and_send(invoice, credentials)
```

## Configuración

### Certificados Digitales

La librería soporta certificados en dos formatos:

```python
# Como contenido PEM (recomendado para BD)
certificado_string = """-----BEGIN CERTIFICATE-----
MIICljCCAX4CAQEwDQYJKoZIhvcNAQELBQAwEjEQMA4GA1UEAwwHVGVzdCBDQTAe...
-----END CERTIFICATE-----
-----BEGIN PRIVATE KEY-----
MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC5example...
-----END PRIVATE KEY-----"""

# Como path a archivo
certificado_path = "/path/to/certificado.pem"
```

### Ambientes SUNAT

```python
# TEST (Beta)
credentials = SunatCredentials(..., es_test=True)
# Endpoints: https://e-beta.sunat.gob.pe/...

# PRODUCCIÓN  
credentials = SunatCredentials(..., es_test=False)
# Endpoints: https://e-factura.sunat.gob.pe/...
```

## Validación Opcional

La librería incluye un **DocumentValidator opcional** completamente separado del core (igual que Greenter/validator):

```python
from cpe_engine import DocumentValidator, Invoice, Company, Client
from datetime import datetime

# Crear validador (opcional)
validator = DocumentValidator()

# Crear documento (core siempre funciona sin validador)
invoice = Invoice(
    serie="F001",
    correlativo=123,
    fecha_emision=datetime.now(),
    # ... otros campos
)

# Validar opcionalmente usando catálogos oficiales SUNAT
errores = validator.validate(invoice)

if errores:
    print(f"❌ {len(errores)} errores encontrados:")
    for error in errores:
        print(f"  - {error.field}: {error.message}")
else:
    print("✅ Documento válido según catálogos SUNAT")

# El documento se puede usar independientemente del validador
xml_content = invoice.build_xml()  # Siempre funciona
```

### Ventajas del Validador Opcional

- ✅ **Separado del core** - Los documentos se crean sin validar (como Greenter)
- ✅ **35 catálogos oficiales** - Validación contra fuentes gubernamentales SUNAT
- ✅ **Mensajes descriptivos** - Errores con códigos válidos sugeridos
- ✅ **Totalmente opcional** - El core funciona independientemente
- ✅ **Compatible con Greenter** - Misma arquitectura que PHP Greenter/validator

## Testing

La librería incluye tests completos que **no requieren configuración adicional**:

```bash
# Ejecutar todos los tests (incluye credenciales oficiales de SUNAT)
python -m pytest -v

# Tests específicos  
python -m pytest tests/test_models.py -v      # Tests de modelos (declarativo como Greenter)
python -m pytest tests/test_validator.py -v   # Tests del validador opcional
python -m pytest tests/test_api.py -v         # Tests de API de alto nivel
python -m pytest tests/test_certificate.py -v # Tests de certificados
python -m pytest tests/test_xml_generation.py -v # Tests de XML y mapeo dinámico
```

### Funcionalidades Validadas en Tests

- ✅ **Arquitectura declarativa** - Sin cálculos automáticos (compatible con Greenter)
- ✅ **35 catálogos SUNAT** - Validación opcional usando códigos oficiales
- ✅ **Mapeo dinámico de tributos** - XML correcto según tipo de operación  
- ✅ **Facturas de exportación** - Soporte completo para operaciones sin IGV
- ✅ **DocumentValidator** - Validación opcional separada del core
- ✅ **Compatibilidad total** - Mismos resultados que Greenter PHP

### Credenciales de Test

Los tests usan automáticamente las **credenciales oficiales de prueba de SUNAT**:
- RUC: `20000000001`
- Usuario: `20000000001MODDATOS`  
- Password: `moddatos`
- Certificado: Hardcodeado (no requiere archivos externos)

### Personalizar Credenciales (Opcional)

Si necesitas usar tus propias credenciales para testing:

```bash
export SUNAT_TEST_RUC="tu_ruc"
export SUNAT_TEST_USER="tu_usuario"
export SUNAT_TEST_PASSWORD="tu_password"
export SUNAT_TEST_CERT="/path/to/tu/cert.pem"
export SUNAT_TEST_PRODUCTION="false"  # true para producción

python -m pytest
```

## Desarrollo

```bash
# Instalar en modo desarrollo
pip install -e ".[dev]"

# Formatear código
black src/
isort src/

# Verificar tipos
mypy src/
```

## Arquitectura

La librería sigue el **mismo diseño declarativo que Greenter** con 4 fases:

1. **Fase 1 - Modelos**: `Invoice`, `Company`, `Client` declarativos (sin cálculos automáticos)
2. **Fase 2 - XML**: Generación UBL 2.1 con templates Jinja2 y mapeo dinámico de tributos
3. **Fase 3 - Firma**: Firma digital X.509 con SHA-256
4. **Fase 4 - SUNAT**: Envío SOAP autenticado y procesamiento CDR

### Componentes Adicionales (Opcionales)

- **DocumentValidator**: Validador opcional usando 35 catálogos oficiales SUNAT
- **Catálogos SUNAT**: 35 catálogos oficiales descargados de fuentes gubernamentales
- **API de Alto Nivel**: Funciones simplificadas para casos de uso comunes

### Compatibilidad con Greenter

- ✅ **Arquitectura declarativa**: Sin cálculos automáticos (como Greenter)
- ✅ **Modelos equivalentes**: Mismos campos y comportamiento
- ✅ **Templates XML**: Generación idéntica de UBL 2.1
- ✅ **Validador separado**: DocumentValidator opcional (como Greenter/validator)
- ✅ **Mapeo de tributos**: TributoFunction equivalente al PHP original

## Testing

La librería incluye una suite completa de tests que valida todas las funcionalidades críticas:

### Test Coverage

| Categoría | Archivos | Descripción |
|-----------|----------|-------------|
| **API Tests** | `test_api.py`, `test_models.py` | APIs de alto nivel y modelos core |
| **SUNAT Integration** | `test_sunat_integration.py` | Cliente SOAP, envío de documentos, CDR |
| **Digital Signature** | `test_digital_signature.py` | Gestión certificados y firma XML |
| **End-to-End** | `test_end_to_end.py` | Flujos completos desde creación hasta envío |
| **Error Handling** | `test_error_handling.py` | Manejo de errores de red y datos malformados |
| **XML Generation** | `test_xml_generation.py` | Generación de XML UBL 2.1 |
| **Certificate Management** | `test_certificate.py` | Carga y validación de certificados |
| **Validation** | `test_validator.py` | Validador opcional con catálogos SUNAT |

### Ejecutar Tests

```bash
# Tests completos
python -m pytest

# Tests específicos
python -m pytest tests/test_api.py -v

# Con coverage
python -m pytest --cov=cpe_engine

# Tests de integración con SUNAT (requiere credenciales)
export SUNAT_TEST_RUC="20000000001"
export SUNAT_TEST_USER="20000000001MODDATOS"
export SUNAT_TEST_PASSWORD="moddatos"
python -m pytest tests/test_sunat_integration.py -v
```

### Official SUNAT Test Credentials

Los tests incluyen credenciales oficiales de SUNAT (hardcodeadas) que funcionan sin configuración adicional:

- **RUC**: 20000000001
- **Usuario**: 20000000001MODDATOS  
- **Password**: moddatos
- **Ambiente**: BETA (pruebas)

## Production Status

### ✅ Ready for Production Use

La librería ha sido probada extensivamente y está lista para uso en producción:

**Verified Components:**
- ✅ **Core Models**: Todos los modelos validados contra Greenter
- ✅ **XML Generation**: Templates UBL 2.1 probadas con SUNAT
- ✅ **Digital Signatures**: Firma SHA-256 funcionando correctamente
- ✅ **SUNAT Communication**: Cliente SOAP probado con servicios reales
- ✅ **Error Handling**: Manejo robusto de errores de red y datos
- ✅ **Data Validation**: 35 catálogos oficiales SUNAT integrados

**Performance & Security:**
- ✅ **Thread-Safe**: Soporte para procesamiento concurrente
- ✅ **Security**: SHA-256 signatures, secure certificate handling
- ✅ **Memory Efficient**: Procesamiento optimizado para documentos grandes
- ✅ **Error Recovery**: Reintentos automáticos para errores transitorios

**Production Deployment:**
- ✅ **Environment Support**: TEST y PRODUCTION endpoints
- ✅ **Certificate Management**: Soporte para certificados reales y prueba  
- ✅ **Monitoring**: Logging detallado para auditoría
- ✅ **Scalability**: Arquitectura stateless para alta disponibilidad

## Licencia

MIT License. Ver [LICENSE](LICENSE) para más detalles.

## Contribuir

1. Fork el proyecto
2. Crear branch para feature (`git checkout -b feature/amazing-feature`)
3. Commit cambios (`git commit -m 'Add amazing feature'`)
4. Push al branch (`git push origin feature/amazing-feature`)
5. Abrir Pull Request

## Soporte

- 📖 [Documentación](https://github.com/tu-repo/cpe-engine)
- 🐛 [Issues](https://github.com/tu-repo/cpe-engine/issues)
- 💬 [Discusiones](https://github.com/tu-repo/cpe-engine/discussions)

---

**Nota**: Esta librería es un port de [Greenter](https://greenter.dev/) de PHP a Python. Agradecimientos al equipo original por su excelente trabajo.