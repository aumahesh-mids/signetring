import logging
from typing import Any

from fastapi import APIRouter

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post('/', response_model=None)
async def verify() -> Any:
    pass