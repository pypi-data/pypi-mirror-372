import os
import json
from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import sqlalchemy.exc
import pint.errors
import traceback
import pytz
from fastapi.responses import FileResponse, ORJSONResponse

import sunpeek
from sunpeek.common.utils import sp_logger
from sunpeek.common import errors
import sunpeek.common.time_zone as tz
from sunpeek.api.routers import files, evaluations, config, plant, api_jobs
from sunpeek.api.dependencies import get_query_token, session
import sunpeek.serializable_models as smodels
import sunpeek.exporter

root_path = os.environ.get('SUNPEEK_API_ROOT_PATH', None)
sp_logger.info(f"HarvestIT API started with root_path set to {root_path}")

app = FastAPI(dependencies=[Depends(get_query_token)], title="SunPeek API", root_path=root_path,
              version=sunpeek.__version__, default_response_class=ORJSONResponse,
              responses={400: {"description": "Bad Request", "model": smodels.Error}})

app.include_router(files.files_router)
app.include_router(evaluations.evaluations_router)
# app.include_router(evaluations.stored_evaluations_router)
app.include_router(config.config_router)
app.include_router(plant.plants_router)
app.include_router(plant.plant_router)
app.include_router(plant.any_plant_router)
app.include_router(api_jobs.jobs_router)


@app.exception_handler(sqlalchemy.exc.NoResultFound)
def db_not_found(request, exc):
    sp_logger.warning(traceback.format_tb(exc.__traceback__))
    return JSONResponse(
        status_code=404,
        content={"error": "NoResultFound",
                 "message": exc.args[0],
                 "detail": "The requested object, or one of it's child objects, cannot be found in the database"}
    )


@app.exception_handler(errors.SunPeekError)
@app.exception_handler(AssertionError)
def general_hit_errors(request, exc):
    sp_logger.warning(traceback.format_tb(exc.__traceback__))
    response = smodels.Error(error=exc.__class__.__name__,
                             message="The syntax of this request was valid, but there was an error processing it "
                                     "further, see error detail",
                             detail=str(exc))
    return JSONResponse(
        status_code=400,
        content=response.dict()
    )


@app.exception_handler(pytz.exceptions.UnknownTimeZoneError)
def unknown_tz_err(request, exc):
    sp_logger.warning(traceback.format_tb(exc.__traceback__))
    response = smodels.Error(error=exc.__class__.__name__,
                             message="Unknown Timezone",
                             detail=f"{str(exc)} was not recognised as a valid timezone identifier")
    return JSONResponse(
        status_code=400,
        content=response.dict()
    )


@app.exception_handler(sqlalchemy.exc.IntegrityError)
def db_integrity_err(request, exc):
    if "duplicate key value violates unique constraint" in str(exc) or "UNIQUE constraint failed" in str(exc):
        sp_logger.warning(str(exc.orig))
        return JSONResponse(
            status_code=409,
            content={"error": "IntegrityError",
                     "message": "Item with duplicate identifier (e.g. name or id) exists",
                     "detail": str(exc.orig)}
        )
    if "is still referenced from table" in str(exc) or "FOREIGN KEY constraint failed" in str(exc):
        return JSONResponse(
            status_code=409,
            content={"error": "IntegrityError",
                     "message": "Cannot remove a component which is still referenced by other components",
                     "detail": str(exc.orig)}
        )

    else:
        return JSONResponse(content={"error": "IntegrityError",
                                     "message": "A database integrity error occurred",
                                     "detail": ''},
                            status_code=500)


@app.exception_handler(pint.errors.UndefinedUnitError)
def invalid_unit(_, exc):
    return JSONResponse(
        status_code=422,
        content={"error": "UndefinedUnitError",
                 "message": "One of the unit strings in your request was invalid",
                 "detail": str(exc)}
    )


origins = json.loads(os.environ.get('HIT_API_ALLOWED_ORIGINS',
                                    '["http://localhost", "http://127.0.0.1", "http://localhost:8080", \
                                    "http://127.0.0.1:8080", "http://localhost:8000"]')
                     )

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["content-disposition"]
)


@app.exception_handler(500)
def internal_server_error(request, exc):
    tb = traceback.format_tb(exc.__traceback__)
    sp_logger.error(exc, exc_info=exc)
    response = JSONResponse(content={"error": "Internal Server Error",
                                     "message": "Critical Error occurred in the backend!",
                                     "detail": f"A critical error occured: '{exc}'."}, status_code=500)

    # Since the CORSMiddleware is not executed when an unhandled server exception
    # occurs, we need to manually set the CORS headers ourselves if we want the FE
    # to receive a proper JSON 500, opposed to a CORS error.
    # Setting CORS headers on server errors is a bit of a philosophical topic of
    # discussion in many frameworks, and it is currently not handled in FastAPI.
    # See dotnet core for a recent discussion, where ultimately it was
    # decided to return CORS headers on server failures:
    # https://github.com/dotnet/aspnetcore/issues/2378
    origin = request.headers.get('origin')

    if origin:
        # Have the middleware do the heavy lifting for us to parse
        # all the config, then update our response headers
        cors = CORSMiddleware(
            app=app,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"])

        # Logic directly from Starlette's CORSMiddleware:
        # https://github.com/encode/starlette/blob/master/starlette/middleware/cors.py#L152

        response.headers.update(cors.simple_headers)
        has_cookie = "cookie" in request.headers

        # If request includes any cookie headers, then we must respond
        # with the specific origin instead of '*'.
        if cors.allow_all_origins and has_cookie:
            response.headers["Access-Control-Allow-Origin"] = origin

        # If we only allow specific origins, then we have to mirror back
        # the Origin header in the response.
        elif not cors.allow_all_origins and cors.is_allowed_origin(origin=origin):
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers.add_vary_header("Origin")

    return response


@app.get('/about')
def about(request: Request):
    content = {'version': sunpeek.__version__,
               'interactive_docs_url': str(request.url).split(request.url.path)[0] + app.docs_url,
               'redoc_docs_url': str(request.url).split(request.url.path)[0] + app.redoc_url}
    return JSONResponse(status_code=200, content=content)


@app.get('/debug_info', response_class=FileResponse, tags=["debug"])
def about(include_plants: bool = True, include_db_structure: bool = True, session=Depends(session)):
    content = sunpeek.exporter.dump_debug_info(include_plants, include_db_structure, session=session)
    return JSONResponse(status_code=200, content=content)


@app.get("/available_timezones", tags=["plant", "info", "timezones"],
         summary="Show a list of timezones, including plant local time without DST")
def list_timezones():
    return JSONResponse(status_code=200, content=tz.available_timezones)


# For Debugging
if __name__ == '__main__':
    import uvicorn

    uvicorn.run("main:app", host='0.0.0.0', port=8000)
