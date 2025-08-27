
from fastapi import FastAPI

from acex.constants import BASE_URL
import os

from pathlib import Path
import importlib

class Api: 

    def create_app(self, automation_engine):
        Api = FastAPI(
            title="ACE - Automation Controle Engine",
            openapi_url=f"{BASE_URL}/openapi.json",
            docs_url=f"{BASE_URL}/docs",
            version = os.getenv('VERSION') or "0.0.1",
            # middleware=middleware
        )

        routers = []
        routers_path = Path(__file__).parent / "routers"
        for file in routers_path.glob("*.py"):
            if file.name == "__init__.py":
                continue
            module_name = f"acex.api.routers.{file.stem}"
            try:
                module = importlib.import_module(module_name)

                if hasattr(module, "create_router"):
                    router = getattr(module, "create_router")(automation_engine)
                    routers.append(router)
            except Exception as e:
                print(f"Failed to import {module_name}: {e}")
                raise e

        for router in routers:
            Api.include_router(router)

        return Api