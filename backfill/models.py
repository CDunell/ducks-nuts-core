from enum import Enum
from pydantic import BaseModel
from datetime import datetime

class BackfillStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"

class BackfillJob(BaseModel):
    id: str
    exchange: str
    symbol: str
    start_time: datetime
    end_time: datetime
    status: BackfillStatus

class BackfillChunk(BaseModel):
    id: str
    job_id: str
    chunk_start: datetime
    chunk_end: datetime
    status: BackfillStatus
