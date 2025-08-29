from fastapi import Header, HTTPException

from sunpeek.common import utils
import sunpeek.db_utils.crud as crud_module


async def get_token_header(x_token: str = Header(...)):
    if x_token != "fake-super-secret-token":
        raise HTTPException(status_code=400, detail="X-Token header invalid")


async def get_query_token(token: str):
    if token != "harvestIT":
        raise HTTPException(status_code=400, detail="No harvestIT token provided")


def session():
    s = utils.S()
    try:
        yield s
    finally:
        s.close()


def crud():
    yield crud_module
