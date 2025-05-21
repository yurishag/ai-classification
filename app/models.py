"""
app/models.py

Interfaces for the API Request and Response
"""

from pydantic import BaseModel
from typing import Any

class ClassificationRequest(BaseModel):
    text: str

class ClassificationResponse(BaseModel):
    task: str
    label: str
    raw: Any