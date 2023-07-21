from fastapi import APIRouter, Depends
from db import get_async_session

from .repository import AdminRepository
from .dependencies import get_admin_repository
from utils.dependencies import Paginator

router = APIRouter(
    prefix='/admin',
    tags=['Admin']
)


@router.get('/statistics/', name="admin_statistics")
async def statistics(paginator: Paginator = Depends(),
                     admin_repo: AdminRepository = Depends(get_admin_repository(get_async_session))):
    return await admin_repo.get_statistics(**paginator.dict())


@router.get('/statistics/{news_id}', name="admin_statistics_by_id")
async def statistics(news_id: int,
                     admin_repo: AdminRepository = Depends(get_admin_repository(get_async_session))):
    return await admin_repo.get_statistics_by_id(news_id)


@router.post('/reg_editor/', name="reg_editor")
async def reg_editor(email: str,
                     admin_repo: AdminRepository = Depends(get_admin_repository(get_async_session))):
    return await admin_repo.create_editor(email)
