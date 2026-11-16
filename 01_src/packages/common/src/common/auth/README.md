En packages/common/auth coloca solo piezas reutilizables (no dependientes de un framework concreto) que te sirvan tanto en API .NET / FastAPI como en Functions/Workers. Lo que no sea común (p. ej., el componente MSAL del front) queda fuera.

Qué sí meter en common/auth

1) Config & constantes (agnóstico)

TenantId, ClientId (de la App Registration), Audience/API AppIdUri, Scopes/Roles.

Mapeo de roles y grupos a permisos de negocio:

AuthzPolicies = { "CanSubmitTasks": ["role:Tasks.Submitter", "group:ab12-..."] }.

2) Validación de tokens (back/funciones)

Utilidades para descubrir JWKS y validar JWT (issuer, aud, firma, expiración).

Extracción de claims comunes: oid, sub, preferred_username, roles, groups.

Helpers para autZ por rol/grupo:

require_role("Tasks.Admin"), require_any(["Tasks.Reader","Tasks.Admin"]).

3) Adquisición de tokens (service-to-service)

Client Credentials (daemon → Entra ID) con caché en memoria/redis.

On-Behalf-Of (OBO): intercambiar token de usuario por token a otro API.

Retries con backoff y manejo de clock skew.

4) Firma/verificación de callbacks

Generación y verificación HMAC para proteger callback_url.

Función sign(body, secret) / verify(signature, body, secret).

5) Key Vault & configuración segura

Helper para resolver secretos (KV/ENV) y exponerlos de modo consistente.

Carga de configuración por entorno (DEV/QA/PROD) con validación.

6) Decoradores / middleware ligeros

Decoradores para proteger endpoints (FastAPI) o attributes (en .NET) que lean de las utilidades anteriores.

Estructura sugerida
packages/common/auth/
  __init__.py
  config.py              # tenant, audience, scopes, roles, groups
  jwks.py                # descarga/rotación de JWKS, validación firmas
  jwt_validator.py       # validate(token) -> Claims
  claims.py              # helpers: get_user_id(), has_role(), has_group()
  token_client.py        # client credentials & OBO + caché
  policies.py            # require_role/require_any/require_policy
  hmac_signing.py        # sign/verify para callbacks
  keyvault.py            # (opcional) helper KV/ENV
  exceptions.py


(Si usas .NET, el equivalente sería un proyecto Common.Auth con: Options, JwtValidator, TokenClient, AuthorizationPolicies, HmacSigning, y middleware/attributes minimalistas.)