# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional

from ..._models import BaseModel

__all__ = ["HealthCheckServicesResponse", "Service"]


class Service(BaseModel):
    name: str

    status: str

    detail: Optional[str] = None

    service_info: Optional[Dict[str, object]] = None


class HealthCheckServicesResponse(BaseModel):
    services: List[Service]

    application: Optional[str] = None
