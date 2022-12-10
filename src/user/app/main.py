import logging.config
import logging
import string
import random
import time

import uvicorn
from fastapi import FastAPI

from user.app.config.settings import settings
from user.app.routers.router import api_router

app = FastAPI(
    title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

logging.config.fileConfig(
    '/Users/aumahesh/code/mids/233-PrivacyEngineering/workdir/w233-project/src/user/app/config/logging.conf',
    disable_existing_loggers=False)

logger = logging.getLogger(__name__)


@app.middleware("http")
async def log_requests(request, call_next):
    idem = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    logger.info(f"rid={idem} start request path={request.url.path}")
    start_time = time.time()

    response = await call_next(request)

    process_time = (time.time() - start_time) * 1000
    formatted_process_time = '{0:.2f}'.format(process_time)
    logger.info(f"rid={idem} completed_in={formatted_process_time}ms status_code={response.status_code}")

    return response

app.include_router(api_router, prefix=settings.API_V1_STR)

if __name__ == '__main__':
    uvicorn.run(app, host="localhost", port=9000, log_level=logging.DEBUG)
