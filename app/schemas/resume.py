from datetime import datetime

from pydantic import BaseModel


class ResumeOut(BaseModel):
    id: int
    user_id: int
    filename: str
    file_path: str
    created_at: datetime

    model_config = {"from_attributes": True}
