from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi


class FastauthOpenAPI:
    def __init__(
        self,
        app: FastAPI,
        title: str = "Fastauth API",
        version: str = "0.0.0",
        description="Custom OpenAPI schema with token authorization",
    ):
        self.app: FastAPI = app
        self.title: str = title
        self.version: str = version
        self.description: str = description

    def __call__(self):
        if self.app.openapi_schema:
            return self.app.openapi_schema

        openapi_schema = get_openapi(
            title=self.title,
            version=self.version,
            description=self.description,
            routes=self.app.routes,
        )

        openapi_schema["components"]["securitySchemes"] = {
            "AccessTokenHeader": {
                "type": "apiKey",
                "name": "ACCESS-TOKEN",
                "in": "header",
            },
            "MasterTokenHeader": {
                "type": "apiKey",
                "name": "MASTER-TOKEN",
                "in": "header",
            },
        }

        for path in openapi_schema["paths"].values():
            for method in path.values():
                method["security"] = [
                    {
                        "AccessTokenHeader": [],
                        "MasterTokenHeader": [],
                    }
                ]

        self.app.openapi_schema = openapi_schema
        return self.app.openapi_schema