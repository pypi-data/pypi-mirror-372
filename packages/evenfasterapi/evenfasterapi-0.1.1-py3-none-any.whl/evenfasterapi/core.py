import secrets
from typing import Any

from fastapi import APIRouter
from starlette.requests import Request
from starlette.responses import JSONResponse
from toomanythreads import ThreadedServer
from loguru import logger as log

JSON_RESP = {
    "request": {},
    "success": False,
    "error": "",
    "content": None,
}

class JSONAPIRouter(APIRouter):
    def __repr__(self):
        return f"[{self.__class__.__name__}]"

    def __init__(self, bearer_name: str = None):
        super().__init__()
        self.tokens = []
        self.bearer_prefix = self.__class__.__name__ or bearer_name
        self.bearer_name = f"{self.bearer_prefix}-bearer"
        self.admin_bearer_name = f"{self.bearer_prefix}-adminbearer"
        self.admin_bearer_pass = secrets.token_urlsafe(64)
        log.warning(f"{self}: Initialized with admin_bearer_pass='{self.admin_bearer_pass}' - Keep this safe!")

        @self.post("/give_token")
        async def give_token(request: Request):
            user_pass = request.headers.get(self.admin_bearer_name)
            if not self.admin_bearer_name in request.headers.keys():
                return self.json_error(request, "Admin bearer not detected", 401)
            else:
                if user_pass == self.admin_bearer_pass:
                    return self.json_success(request, self.give_token(user_pass), 200)
                else: return self.json_error(request, "Authorization denied")

    async def json_middleware(self, request: Request, call_next):
        if not "give_token" in request.url.path:
            bearer = request.headers.get(self.bearer_name)
            if bearer not in self.tokens:
                return self.json_error(request, "Authorization denied")
        return await call_next(request)

    def give_token(self, admin_pass):
        if admin_pass == self.admin_bearer_pass: return self.generate_token()

    def generate_token(self):
        token = secrets.token_urlsafe(64)
        self.tokens.append(token)
        return token

    def json_success(self, request: Request, content: Any, status_code=200):
        resp = JSON_RESP.copy()
        resp["request"] = {
            "method": request.method,
            "url": str(request.url),
            "query_params": dict(request.query_params),
            "headers": dict(request.headers)
        }
        resp["success"] = True
        resp["content"] = content
        log.debug(f"Returning success response with status {status_code}")
        return JSONResponse(content=resp, status_code=status_code)


    def json_error(self, request: Request, e: str | Exception, status_code=500):
        if isinstance(e, Exception):
            e = str(e)
        elif isinstance(e, str):
            pass
        else:
            raise TypeError(f"Only str or exception are accepted for 'e', got {type(e)} instead")
        resp = JSON_RESP.copy()
        resp["request"] = {
            "method": request.method,
            "url": str(request.url),
            "query_params": dict(request.query_params),
            "headers": dict(request.headers)
        }
        resp["success"] = False
        resp["error"] = str(e)
        log.debug(f"Returning error response with status {status_code}: {e}")
        return JSONResponse(content=resp, status_code=status_code)