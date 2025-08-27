# gig/lib.py
from typing import Dict, Any, List
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt import exceptions as jwt_exceptions
import httpx

from .settings import get_settings, get_public_key


settings = get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def decode_jwt(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]: # Decodifica el JWT y devuelve el payload
    """
    Dependencia para validar y decodificar el JWT.
    Lanza 401 si el token es inválido o expirado.
    """
    settings = get_settings()
    try:
        return jwt.decode(
            token,
            get_public_key(),
            algorithms=[settings.algorithm]
        )
    except jwt_exceptions.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

# --------------   VERIFICACIONES DE ROLES SUPERUSER/SUPERADMIN  --------------

def verify_superuser(payload: Dict[str, Any] = Depends(decode_jwt)) -> Dict[str, Any]: # SUPERUSER en cualquier app
    for user in payload.get("usuario_meta", []):
        for comp in user.get("app-meta", []):
            if comp.get("empresa") == "GIG" and "SUPERUSER" in comp.get("roles", []):
                return payload
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permisos insuficientes") 

def verify_superadmin_gig(payload: Dict[str, Any] = Depends(decode_jwt)) -> Dict[str, Any]: # SUPERADMIN en app GIG
    for app in payload.get("usuario_meta", []):
        if app.get("nombre-app") != "GIG":
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Permisos insuficientes, se necesita ser SUPERADMIN de GIG")
        for comp in app.get("app-meta", []):
            if comp.get("empresa") == "GIG" and "SUPERADMIN" in comp.get("roles", []):
                return payload
    raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Permisos insuficientes, se necesita ser SUPERADMIN")

def verify_superuser_gig(payload: Dict[str, Any] = Depends(decode_jwt)) -> Dict[str, Any]: # SUPERUSER en app GIG
    for app in payload.get("usuario_meta", []):
        if app.get("nombre-app") != "GIG":
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Permisos insuficientes, se necesita ser SUPERUSER de GIG")
        for comp in app.get("app-meta", []):
            if comp.get("empresa") == "GIG" and "SUPERUSER" in comp.get("roles", []):
                return payload
    raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Permisos insuficientes, se necesita ser SUPERUSER de GIG")

def verify_access_gig(payload: Dict[str, Any] = Depends(decode_jwt)) -> Dict[str, Any]: # SUPERUSER/SUPERADMIN en GIG
    for app in payload.get("usuario_meta", []):
        if app.get("nombre-app") != "GIG":
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Permisos insuficientes, se necesita ser SUPERUSER o SUPERADMIN de GIG")
        for comp in app.get("app-meta", []):
            if comp.get("empresa") == "GIG" and ("SUPERUSER" in comp.get("roles", []) or "SUPERADMIN" in comp.get("roles", [])):
                return payload
    raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Permisos insuficientes, se necesita ser SUPERUSER o SUPERADMIN de GIG")

def verify_supers(payload: Dict[str, Any] = Depends(decode_jwt)) -> Dict[str, Any]:# SUPERUSER/SUPERADMIN en cualquier app
    for app in payload.get("usuario_meta", []):
        if app.get("nombre-app") != "GIG":
            for comp in app.get("app-meta", []):
                if "SUPERUSER" in comp.get("roles", []):
                    return payload
        else:
            for comp in app.get("app-meta", []):
                if "SUPERADMIN" in comp.get("roles", []) or "SUPERUSER" in comp.get("roles", []):
                    return payload
    raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Permisos insuficientes, se necesita ser algun SUPER")

# --------------   VERIFICACIONES PROPIAS DE ACCESO  --------------

def require_role(required_roles: List[str]): # Verifica que el usuario tenga al menos uno de los roles indicados.
    """
    Crea una dependencia que verifica que el usuario tenga al menos
    uno de los roles indicados.

    Uso:
        @router.get(..., dependencies=[require_role(["ADMIN"])])
    """
    def checker(payload: Dict[str, Any] = Depends(decode_jwt)) -> Dict[str, Any]:
        usuario_meta = payload.get("usuario_meta", [])
        has_role = any(
            role in comp.get("roles", [])
            for um in usuario_meta
            for comp in um.get("app-meta", [])
            for role in required_roles
        )
        if not has_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Se requiere uno de estos roles: {required_roles}",
            )
        return payload

    return Depends(checker)

def require_app(required_app: str): # Verifica que el usuario tenga acceso a la app indicada.
    """
    Crea una dependencia que valida que el usuario tenga acceso a la app indicada.

    Uso:
        @router.get(..., dependencies=[require_app("GIG")])
    """
    def checker(payload: Dict[str, Any] = Depends(decode_jwt)) -> Dict[str, Any]:
        apps = [
            um.get("nombre-app")
            for um in payload.get("usuario_meta", [])
        ]
        if required_app not in apps:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Se requiere acceso a la aplicación '{required_app}'"
            )
        return payload

    return Depends(checker)

# --------------   OBTENCION DE DATOS DE USUARIO --------------

def user_name(correo: str) -> dict: # Obtiene el nombre del usuario en Azure mediante el servicio externo.
    url = "https://reverseproxy-dxfpbehna7cah9cz.eastus-01.azurewebsites.net/autenticador/auth/name"
    payload = {"user_email": correo}
    try:
        response = httpx.post(url, json=payload, timeout=5.0)
        response.raise_for_status()
        return response.json()
    except (httpx.RequestError, httpx.HTTPStatusError, ValueError):
        return {
            "detalle": "Error al obtener el nombre del usuario",
        }

def user_id(payload: Dict[str, Any] = Depends(decode_jwt)) -> int: # Retorna el idUsuario del payload
    return payload["idUsuario"]

# --------------   OTRAS VERIFICACIONES --------------

def verify_user(correo: str) -> bool: # Verifica si el usuario en Azure mediante el servicio externo.
    url = "https://reverseproxy-dxfpbehna7cah9cz.eastus-01.azurewebsites.net/autenticador/auth/verify-azure-user"
    payload = {"user_email": correo}
    try:
        response = httpx.post(url, json=payload, timeout=5.0)
        response.raise_for_status()
        return bool(response.json())
    except (httpx.RequestError, httpx.HTTPStatusError, ValueError):
        return False

