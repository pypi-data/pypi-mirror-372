from datetime import datetime

from pydantic import BaseModel
from ul_api_utils.api_resource.api_response import JsonApiResponsePayload


class ApiBsTrafficStatsResponse(JsonApiResponsePayload):
    date: datetime
    raw_data_size: float


class ApiDeviceTrafficStatsQuery(BaseModel):
    start_at: datetime
    end_at: datetime
