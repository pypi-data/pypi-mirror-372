# ekacare/__init__.py
from .client import EkaCareClient
from .utils.exceptions import (
    EkaCareError, 
    EkaCareAPIError, 
    EkaCareAuthError, 
    EkaCareValidationError,
    EkaCareResourceNotFoundError
)

__all__ = [
    "EkaCareClient",
    "EkaCareError",
    "EkaCareAPIError",
    "EkaCareAuthError",
    "EkaCareValidationError",
    "EkaCareResourceNotFoundError"
]

# ekacare/auth/__init__.py
from .auth.auth import Auth
__all__ = ["Auth"]

from .tools.files import EkaFileUploader
__all__ = ["EkaFileUploader"]


# ekacare/records/__init__.py
from .records.records import Records
__all__ = ["Records"]

# ekacare/vitals/__init__.py
from .vitals.vitals import Vitals
__all__ = ["Vitals"]

# ekacare/utils/__init__.py
from .utils.exceptions import (
    EkaCareError, 
    EkaCareAPIError, 
    EkaCareAuthError, 
    EkaCareValidationError,
    EkaCareResourceNotFoundError
)

__all__ = [
    "EkaCareError",
    "EkaCareAPIError",
    "EkaCareAuthError",
    "EkaCareValidationError", 
    "EkaCareResourceNotFoundError"
]

# ekacare/abdm/__init__.py
from .abdm.profile import Profile

__all__ = ["Profile", "Consents", "CareContexts", "Enrollment"]


#class Voice:
#    def __init__(self, client):
#        self.client = client

# ekacare/notifications/__init__.py
class Notifications:
    def __init__(self, client):
        self.client = client
