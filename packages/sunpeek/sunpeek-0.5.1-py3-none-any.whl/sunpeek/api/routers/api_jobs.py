import uuid
import os
import datetime as dt
from fastapi import APIRouter, Depends, Request, BackgroundTasks
from fastapi.responses import FileResponse
from typing import List
from sqlalchemy.orm import Session

from sunpeek.api.dependencies import session, crud
import sunpeek.serializable_models as smodels


jobs_router = APIRouter(
    prefix="/jobs",
    tags=["jobs"],
)


def create_result_url(job, request):
    if job.result_path:
        job.result_url = str(request.url_for('result_file', id=job.id))
    return job


@jobs_router.get("/", response_model=List[smodels.Job], summary="List all jobs, or get one by id")
@jobs_router.get("/{id}", response_model=smodels.Job, summary="Get a job by id")
def jobs(request: Request, id: uuid.UUID = None, sess: Session=Depends(session), crd=Depends(crud)):
    jobs = crd.get_components(sess, "Job", id)
    if isinstance(jobs, list):
        jobs = [create_result_url(job, request) for job in jobs]
    else:
        jobs = create_result_url(jobs, request)
    return jobs


@jobs_router.get("/{id}/result_file", response_class=FileResponse, summary="Get a job result by id")
def result_file(id: uuid.UUID, background_tasks: BackgroundTasks, session: Session=Depends(session), crud=Depends(crud)):
    job = crud.get_components(session, "Job", id)
    if job.plant is not None:
        filename = f'export_{job.plant.name}_{dt.datetime.now().__format__("%Y-%m-%d_%H%M")}.tar.gz'
    else:
        filename = f'export_{dt.datetime.now().__format__("%Y-%m-%d_%H%M")}.tar.gz'
    background_tasks.add_task(os.remove, job.result_path)
    background_tasks.add_task(crud.delete_component, session, job)
    return FileResponse(job.result_path, filename=filename)
