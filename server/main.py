from typing import Tuple, Dict, List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(
    title='News',
    version='0.11'
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

news = [
    {
        'id': 1,
        'title': '1. Lorem Ipsum',
        'description': 'Lorem Ipsum dolor sit amet',
        'content': 'Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industrys standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.',
        'views': 234
    },
    {
        'id': 2,
        'title': '2. Lorem Ipsum',
        'description': 'Lorem Ipsum dolor sit amet',
        'content': 'Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industrys standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.',
        'views': 2342
    },
    {
        'id': 3,
        'title': '3. Lorem Ipsum',
        'description': 'Lorem Ipsum dolor sit amet',
        'content': 'Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industrys standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.',
        'views': 234
    },
    {
        'id': 4,
        'title': '4. Lorem Ipsum',
        'description': 'Lorem Ipsum dolor sit amet',
        'content': 'Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industrys standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.',
        'views': 234
    }
]


class NewsItem(BaseModel):
    id: int = Field(ge=0)
    title: str
    description: str
    content: str
    views: int


class News(BaseModel):
    news: List[NewsItem]


@app.get("/", response_model=News)
async def root():
    return {'news': news}


@app.get('/news/{news_id}')
async def news_detail(news_id: int):
    """
    нужно менять эту ф-ю, искать айдишник по индексу так себе, ведь некоторые могут отсутствовать
    сделать валидацию
    :param news_id:
    :return:
    """
    return {'status': 200, 'news': news[news_id-1]}


class Currency(BaseModel):
    dollar: Tuple[str, float]
    euro: Tuple[str, float]
    FYM: Tuple[str, float]


@app.get('/currency_rates', response_model=Currency)
async def currency():
    return Currency(
        dollar=('$', 80.0),
        euro=('€', 99.85),
        FYM=('¥', 12.0)
    )


class Weather(BaseModel):
    city: str = Field(max_length=20)
    celsius: float
    weather: str = Field(max_length=20)


@app.get('/weather', response_model=Weather)
async def _weather():
    return Weather(
        city='Moscow',
        celsius=24.5,
        weather='Clear',
    )


class NewsId(BaseModel):
    news_id: int = Field(ge=0)


@app.post('/statistics')
async def statistics(news_id: NewsId):
    return {'status': 200,
            'id': news_id.news_id,
            'views': news[news_id.news_id-1]['views']}
