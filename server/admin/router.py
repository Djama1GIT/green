# from fastapi import APIRouter, Depends
# from main import fastapi_users
# from auth.models import User
#
# current_superuser = fastapi_users.current_user(active=True, superuser=True)
#
# router = APIRouter(
#     prefix='/admin',
#     tags=['Admin']
# )
#
#
# @router.get("/protected-route")
# def protected_route(user: User = Depends(current_superuser)):
#     return f"Hello, {user.email}"
#
# @router.get('/statistics/{news_id}')
# async def statistics(news_id: int, user: User = Depends(current_superuser)):
#     return {'status': 200,
#             'id': news_id,
#             'views': news[news_id - 1]['views']}
