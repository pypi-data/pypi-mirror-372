from typing import Any
from fastapi import Request
from fastapi.routing import Match
from ..client_db.client_db import load_access_token


class Params:
    def __init__(self, req) -> None:
        self.req: Request = req
        # self.path_params = self.get_path_params()

    @property
    def path_params(self) -> dict:
        path_params: dict = {}
        routes = self.req.app.router.routes
        for route in routes:
            match, scope = route.matches(self.req)
            if match == Match.FULL:
                path_params = scope["path_params"]
        return path_params

    @property
    def query_params(self) -> dict:
        return self.req.query_params._dict

    def get_param(self, paramname):
        params: str = self.query_params | self.path_params
        return params[paramname] if paramname in params else None


def match_key(recived_key, key):
    return key == recived_key


def get_access_token(client_id: str):
    return load_access_token(client_id=client_id)
