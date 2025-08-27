# Centra SDK

The **Centra SDK** is a UNOFFICIAL FastAPI-based SDK designed to simplify the integration of third-party platforms with Guardicore's Centra platform. This SDK provides a standardized framework for building connectors that handle security policies, inventory management, operations monitoring, and more.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Router Modules](#router-modules)
- [Models and Data Types](#models-and-data-types)
- [API Documentation](#api-documentation)

## Overview

The Centra SDK serves as a bridge between external security platforms and Guardicore's centralized security management system. It provides:

- **Standardized API contracts** for consistent integration across different platforms
- **Comprehensive data models** generated from OpenAPI specifications

## Features

### 🔧 **Modular Architecture**
- Clean separation between routing, business logic, and data models
- Pluggable handler system for custom implementations
- FastAPI-based REST API with automatic documentation

### 🛡️ **Security Operations**
- **Enforcement**: Policy management and rule enforcement
- **Inventory**: Asset discovery and management
- **Operations**: Health monitoring and configuration management
- **Logging**: Centralized logging and audit trails

### 📊 **Comprehensive Monitoring**
- Health checks and status reporting
- Metrics collection and reporting
- Configuration management
- Onboarding process management

### 🔄 **Platform Integration**
- Support for multiple cloud platforms (Azure, AWS, etc.)
- Agent management and control
- Network topology discovery
- Asset lookup and classification

## Installation

### Prerequisites
- Python 3.12 or higher
- pip

### Using pip
```bash
pip install centra-sdk
```


## Quick Start

### 1. Create a Basic Connector

```python
from centra_sdk.main import app
from centra_sdk.routers.health import registry as health_registry, HealthHandler
from centra_sdk.models.connector.v1.operations.health import V1OperationsHealthGetResponse
import uvicorn

@health_registry.register()
class MyHealthHandler(HealthHandler):
    def get_integration_status(self) -> V1OperationsHealthGetResponse:
        return V1OperationsHealthGetResponse(
            overall_status="up",
            component_id="my-connector-id",
            component_type="custom_connector"
        )

# Run the server
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 2. Start the Development Server

```bash
# Using uvicorn directly
uvicorn centra_sdk.main:app --reload --host 0.0.0.0 --port 8000

# Access the API documentation
# http://localhost:8000/docs
```

### 3. Running with SSL Certificate

For production deployments or secure development environments, you can run uvicorn with SSL certificates:

```bash
# Using SSL certificates
uvicorn centra_sdk.main:app --host 0.0.0.0 --port 8443 \
  --ssl-keyfile /path/to/private.key \
  --ssl-certfile /path/to/certificate.crt

# Using self-signed certificates for development
# First, generate self-signed certificates:
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes

# Then run with SSL
uvicorn centra_sdk.main:app --host 0.0.0.0 --port 8443 \
  --ssl-keyfile key.pem \
  --ssl-certfile cert.pem

# Access the secure API documentation
# https://localhost:8443/docs
```

**SSL Configuration Options:**
- `--ssl-keyfile`: Path to the SSL private key file
- `--ssl-certfile`: Path to the SSL certificate file  
- `--ssl-ca-certs`: Path to CA certificates file (optional)
- `--ssl-ciphers`: SSL cipher suites to use (optional)

**Production Considerations:**
- Use certificates from a trusted Certificate Authority (CA)
- Ensure proper file permissions on certificate files (readable only by the application user)
- Consider using a reverse proxy (nginx, Apache) for SSL termination in production
- Use strong cipher suites and disable outdated TLS versions


## Router Modules

The SDK includes several router modules, each handling specific aspects of connector functionality:

### 🏥 **Health Router** (`routers/health.py`)
Manages connector health and status reporting:

```python
@health_registry.register()
class MyHealthHandler(HealthHandler):
    def get_integration_flags(self) -> V1OperationsFlagsGetResponse:
        """Return integration capability flags"""
        pass
    
    def get_integration_status(self) -> V1OperationsHealthGetResponse:
        """Return current health status"""
        pass
    
    def get_integration_metrics(self) -> V1OperationsMetricsGetResponse:
        """Return performance metrics"""
        pass
```

### 📦 **Inventory Router** (`routers/inventory.py`)
Handles asset discovery and inventory management:

```python
@inventory_registry.register()
class MyInventoryHandler(InventoryHandler):
    def get_labels(self, cursor: int = 0, page_size: int = 100) -> Labels:
        """Retrieve asset labels"""
        pass
    
    def get_inventory(self, cursor: int = 0, page_size: int = 100) -> Inventory:
        """Retrieve asset inventory"""
        pass
    
    def post_assets(self, inventory_id: str, asset_type: str, body: Any):
        """Create or update assets"""
        pass
```

### 🛡️ **Enforcement Router** (`routers/enforcement.py`)
Manages security policy enforcement:

```python
@enforcement_registry.register()
class MyEnforcementHandler(EnforcementHandler):
    def set_enforcement_policy(self, body: EnforcementPolicy):
        """Apply security policies"""
        pass
    
    def get_enforcement_policy_inventory(self) -> EnforcementPolicyInventory:
        """Retrieve current policy inventory"""
        pass
```

### 🎛️ **Operations Router** (`routers/operations.py`)
Handles operational tasks like configuration and logging:

```python
@operations_registry.register()
class MyOperationsHandler(OperationsHandler):
    def get_config_options(self) -> InternalConfigMetadata:
        """Get available configuration options"""
        pass
    
    def set_config(self, body: InternalConfig):
        """Update connector configuration"""
        pass
```

### 🔐 **Authentication Router** (`routers/authentication.py`)
Manages JWT-based authentication and token generation:

```python
from centra_sdk.routers.authentication import AuthenticationHandler, registry
from centra_sdk.models.connector.version import LoginRequest, LoginResponse
from starlette.requests import Request

@registry.register()
class MyAuthenticationHandler(AuthenticationHandler):
    def __init__(self):
        super().__init__()
        user_handler = GcUserDataHandler({
            "admin": "securePassword123",
            "user": "password456",
            "test": "testpass"
        })
        self._token_handler = BearerTokenHandler(24,
                                                 "your-secret-key-here",
                                                 user_handler)

    def login_user_json(self, body: LoginRequest) -> LoginResponse:
        """Handle JSON-based login requests"""
        username = body.username
        password = body.password.get_secret_value()  # SecretStr requires get_secret_value()
        
        # Generate access token using your token handler
        access_token = self._token_handler.generate_token(username, password)
        
        return LoginResponse(
            access_token=access_token,
            token_type="Bearer",
            expires_in=86400  # 24 hours in seconds
        )
    
    def login_user_form(self, request: Request) -> LoginResponse:
        """Handle form-based login requests"""
        # Parse form data asynchronously
        form_data = asyncio.run(self._parse_form_data(request))
        
        username = form_data.get("username")
        password = form_data.get("password")
        
        if not username or not password:
            raise HTTPException(status_code=400, detail="Missing credentials")
        
        # Generate access token
        access_token = self._token_handler.generate_token(username, password)
        
        return LoginResponse(
            access_token=access_token,
            token_type="Bearer",
            expires_in=86400
        )
```

Each handler that SDK user want to secure , should implement validation method. As an example
```python
class JwtValidator:
    def __init__(self):
        self._tokens = {
            "passing_token"
        }

    def validate_token(self, token: str):
        return token in self._tokens

# Include JwtValidator to subclass list and SDK would call validate_token() to validate token.
@agents_registry.register()
class GcAgentsHandler(AgentsHandler, JwtValidator):
    """Implementation of AgentsHandler for GuardiCore integration."""

    def __init__(self):
        AgentsHandler.__init__(self)
        JwtValidator.__init__(self)
```

**Authentication Features:**
- JWT token generation and validation using PyJWT library
- Configurable token expiration times
- Bearer token authentication scheme
- Abstract base class pattern for custom user data handlers
- Comprehensive error handling and security logging

**Security Considerations:**
- Use strong secret keys for JWT signing
- Implement proper password hashing in production
- Set appropriate token expiration times
- Validate tokens on each protected endpoint
- Log authentication attempts for security auditing

**Authentication Endpoints:**
- `POST /v1/login`: JSON-based login (requires `LoginRequest` body)
- `POST /v1/login-form`: Form-based login (requires form data with username/password)

**Usage Examples:**

```bash
# JSON login
curl -X POST "http://localhost:8000/v1/login" \
     -H "Content-Type: application/json" \
     -d '{"username": "admin", "password": "securePassword123"}'

# Form login  
curl -X POST "http://localhost:8000/v1/login-form" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=admin&password=securePassword123"
```

### Other Routers:
- **Agents Router**: Agent management and control
- **Control Router**: Connector control operations
- **Info Router**: Integration information and metadata
- **Logging Router**: Log management and collection
- **Onboarding Router**: Platform onboarding processes


## Models and Data Types

The SDK includes comprehensive data models generated from OpenAPI specifications. Key model categories include:

### **Common Models**
- `InventoryItem`: Represents discoverable assets
- `Label`: Key-value metadata for assets
- `NetworkTopology`: Network relationship data

### **Enforcement Models**
- `EnforcementPolicy`: Security policy definitions
- `PolicyRule`: Individual policy rules
- `Action`: Enforcement actions (allow, block, alert)

### **Operations Models**
- `ComponentHealth`: Health status information
- `InternalConfig`: Configuration data
- `LogStatus`: Logging status and metadata

### **Provider Models**
- `Inventory`: Asset inventory responses
- `NetworkTopology`: Network topology data
- `LookupRequest`: Asset lookup queries

#### It is possible to provide custom serialization and validation callbacks, for example
```python
from centra_sdk.models.connector.v1.k8s.k8s_inventory import K8SServicesSpec, KubernetesServicePort
from centra_sdk.gc_serializer import register_serializer, register_validator


@register_serializer(K8SServicesSpec)
def k8s_service_serialize(s):
    s.pop('kind', None)
    tuplify(('ports', 'selector', 'external_ips', 'load_balancer_ingress_ips'), s)
    return s


@register_validator(KubernetesServicePort)
def validate_k8s_service_port(v, handler, info):
    if 'target_port' in v and isinstance(v['target_port'], int):
        v['target_port'] = str(v['target_port'])
    return handler(v)

```

## API Documentation

Once your application is running, you can access:

- **Interactive API Documentation**: `http://localhost:8000/docs`
- **Alternative Documentation**: `http://localhost:8000/redoc`
- **OpenAPI Schema**: `http://localhost:8000/openapi.json`


## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions, issues:
- **Email**: ivasylen@akamai.com

---

**Built with ❤️ by the Guardicore Team**
