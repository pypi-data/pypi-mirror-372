from fastapi import Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import HTTPException
import logging
from typing import Callable, Any, Optional

from .jwt_functions import JWTFunctions
from .auth_functions import get_user_by_attribute
from abs_exception_core.exceptions import UnauthorizedError, AuthError
from fastapi.security.utils import get_authorization_scheme_param

class CustomHTTPBearer(HTTPBearer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    async def __call__(self, request: Request) -> Optional[HTTPAuthorizationCredentials]:
        authorization = request.headers.get("Authorization")
        scheme, credentials = get_authorization_scheme_param(authorization)
        
        if not (authorization and scheme and credentials):
            if self.auto_error:
                raise UnauthorizedError(detail="Invalid authentication credentials")
            else:
                return None
        
        if scheme.lower() != "bearer":
            if self.auto_error:
                raise UnauthorizedError(detail="Invalid authentication credentials")
            else:
                return None
        
        return HTTPAuthorizationCredentials(scheme=scheme, credentials=credentials)

security = CustomHTTPBearer()
# security = HTTPBearer()
logger = logging.getLogger(__name__)


# Dependency acting like per-route middleware
def auth_middleware(
    db_session: Callable[...,Any],
    jwt_secret_key:str,
    jwt_algorithm:str
):
    """
    This middleware is used for authentication of the user.
    Args:
        db_session: Callable[...,Any]: Session of the SQLAlchemy database engine
        jwt_secret_key: Secret key of the JWT for jwt functions
        jwt_algorithm: Algorithm used for JWT

    Returns:
    """
    async def get_auth(request: Request, token: HTTPAuthorizationCredentials = Depends(security)):
        jwt_functions = JWTFunctions(secret_key=jwt_secret_key,algorithm=jwt_algorithm)
        try:
            if not token or not token.credentials:
                raise UnauthorizedError(detail="Invalid authentication credentials")

            payload = jwt_functions.get_data(token=token.credentials)
            uuid = payload.get("uuid")

            user = get_user_by_attribute(db_session=db_session,attribute="uuid", value=uuid)
            
            if not user:
                logger.error(f"Authentication failed: User with id {uuid} not found")
                raise UnauthorizedError(detail="Authentication failed")

            # Attach user to request state
            request.state.user = user
            return user 

        except UnauthorizedError as e:
            logger.error(e)
            raise
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}", exc_info=True)
            raise UnauthorizedError(detail="Authentication failed")
    
    return get_auth