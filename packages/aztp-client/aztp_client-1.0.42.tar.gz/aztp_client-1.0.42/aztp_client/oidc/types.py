from typing import Optional, TypedDict, Dict

class OIDCLoginOptions(TypedDict, total=False):
    callback_url: Optional[str]
    return_url: Optional[str]
    stateless: Optional[bool]

class OIDCLoginResponse(TypedDict):
    success: bool
    message: str
    redirect_url: str
    state: str
    token: Optional[str]

class UserInfo(TypedDict):
    sub: str
    email: str
    name: str
    provider: str
    agent: str

class ValidateTokenRequest(TypedDict):
    token: str

class ValidateTokenResponse(TypedDict):
    success: bool
    valid: bool
    user: UserInfo
    token_type: str
    message: str 