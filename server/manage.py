import asyncio
import json
import os
import sys

from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_users.password import PasswordHelper
from db import async_session_maker
from news.models import News
from auth.models import User
from admin.chemas import UserRegister


async def create_superuser(method=None, session: AsyncSession = async_session_maker()):
    if method == '--auto':
        email = "testmail@mail.mail"
        password = 'password'
    elif not method:
        email = input(f"[Create SuperUser]: Enter email: ")
        password = input(f"[Create SuperUser]: Enter password: ")
    else:
        raise Exception(f'Unexpected argument {method}')

    password_helper = PasswordHelper()
    statement = insert(User).values(UserRegister(
        email=email,
        hashed_password=password_helper.hash(password),
        is_active=True,
        is_superuser=True,
        is_verified=True
    ).dict())
    try:
        await session.execute(statement)
        await session.commit()
        print("[Create SuperUser]: Successful")
    except:
        await session.rollback()
        raise Exception("[Create SuperUser]: Failed to register superuser")
    finally:
        await session.close()


async def add_initial_data(session: AsyncSession = async_session_maker()):
    try:
        with open("news.json", 'r') as news_list:
            news_list = json.load(news_list)
            for news_item in news_list:
                statement = insert(News).values(**news_item)
                await session.execute(statement)
            await session.commit()
            print("[Add initial data]: Successful")
    except:
        await session.rollback()
        raise Exception("[Add initial data]: Failed to add initial data")
    finally:
        await session.close()


async def main():
    if len(sys.argv) < 2:
        raise Exception("Usage: python manage.py run --[c(create superuser) and/or a(add inital data)] [--auto]")
    else:
        if len(sys.argv) > 2:
            arg = sys.argv[2]
            if arg == '--a':
                await add_initial_data()
            elif arg == '--c':
                await create_superuser(sys.argv[3] if len(sys.argv) == 4 else None)
            elif arg in ['--ac', '--ca']:
                await create_superuser(sys.argv[3] if len(sys.argv) == 4 else None)
                await add_initial_data()
            else:
                raise Exception(f'Unexpected argument {arg}')

        arg = sys.argv[1]
        if arg == 'run':
            os.system("gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000")
        else:
            raise Exception("Usage: python manage.py run --[c(create superuser) and/or a(add inital data)]")


asyncio.run(main())
