# Green API

Green - проект, основанный на FastAPI

## Установка и настройка

1. Установите Docker и Docker Compose, если они еще не установлены в вашей системе.

2. Клонируйте репозиторий проекта:

```bash
git clone https://github.com/Djama1GIT/green.git
cd green
```

3. Настройте переменные окружения в файле .env
<small>Не требуется, если Вы не собираетесь использовать работу с почтой</small>

4. Запустите проект:

```bash
docker-compose up --build
```

## Пользовательский интерфейс

После запуска проекта вы можете получить доступ к пользовательскому интерфейсу Swagger по адресу: http://localhost:8080/docs. В Swagger вы можете просмотреть доступные эндпоинты и их параметры, а также выполнять запросы к API.

Также реализован небольшой пример использования API:

Главная страница фронт-енда: http://localhost/

Flower: http://localhost:5555/

## Используемые технологии

- Python - Язык программирования, на котором написан проект.
- REST - Архитектурный стиль для построения распределенных систем, используемый в проекте для создания API.
- FastAPI - Фреймворк для создания API на Python, используемый в проекте для реализации REST API.
- Redis - In-memory база данных, используемая в проекте для кэширования данных и хранения задач Celery.
- Celery - Библиотека для выполнения фоновых задач, используемая в проекте для обработки долгих операций в фоновом режиме.
- Flower - Веб-интерфейс для мониторинга состояния задач Celery, используемый в проекте для отслеживания выполнения задач.
- PostgreSQL - Реляционная база данных, используемая в проекте для хранения информации.
- SQLAlchemy - ORM (Object-Relational Mapping), используемый в проекте для работы с базой данных.
- alembic - Библиотека для миграции базы данных, используемая в проекте для обновления структуры базы данных при изменении моделей данных.
- Docker - Платформа для создания, развертывания и управления контейнерами, используемая в проекте для запуска приложения в изолированной среде.


