import uuid
import os                                                                               # Для работы с путями папок диска
from decimal import Decimal                                                             # Для работы с денежными типами данных
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File         # Основные инструменты FastAPI и файлов
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update                                                           # Для пакетного обновления строк БД
from pydantic import BaseModel, Field                                                   # Для валидации входных данных Pydantic

from app.api.v1.deps import get_current_user
from app.database.session import get_db
from app.models.quest import Quest
from app.models.step import Step
from app.models.question import Question, QuizOption
from app.models.media import Media
from app.models.tag import Tag, QuestTag                                                 # Импортируем базовую модель тегов Tag
from app.models.user import User

router = APIRouter(prefix="/constructor", tags=["Author Constructor"])

# --- СХЕМЫ ВАЛИДАЦИИ ВХОДЯЩИХ ДАННЫХ ---
class QuestCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)                             # Название квеста
    description: str = Field(..., min_length=10)                                     # Детальное описание
    price: Decimal = Field(Decimal("0.00"), ge=0)                                     # Цена квеста

class StepCreate(BaseModel):
    step_order: int                                                                   # Порядок шага в квесте
    step_title: str = Field(..., min_length=3, max_length=255)                        # Название локации
    target_lat: float                                                                 # Широта для карты
    target_lon: float                                                                 # Долгота для карты
    proximity_radius: int = Field(30, ge=5)                                           # Радиус в метрах

class QuestionCreate(BaseModel):
    question_order: int                                                               # Порядок вопроса на шаге
    question_text: str                                                                # Текст вопроса
    question_type: str = Field("text", pattern="^(text|quiz)$")                       # Тип: текст или тест
    correct_answer: str                                                               # Правильный ответ
    points: int = Field(10, ge=1)                                                     # Очки за ответ
    timer: int = Field(60, ge=5)                                                      # Таймер автора в секундах

class MediaAttach(BaseModel):
    quest_id: uuid.UUID = None
    step_id: uuid.UUID = None
    question_id: uuid.UUID = None
    file_url: str = Field(..., min_length=5)
    file_type: str = Field("image", pattern="^(image|video|audio)$")                  # Заменили regex на pattern

# --- РЕАЛИЗАЦИЯ ЭНДПОИНТОВ (ЧАСТЬ 1) ---

@router.post("/quests")
async def create_quest(payload: QuestCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """ Создать новый квест (черновик) """
    new_quest = Quest(author_id=current_user.id, title=payload.title, description=payload.description, price=payload.price, is_published=False)
    db.add(new_quest)
    await db.flush()
    return {"status": "created", "quest_id": new_quest.id}

@router.get("/my-quests")
async def get_my_quests(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """ ДОБАВЛЕНО: Дашборд автора — получить список всех своих созданных квестов и черновиков """
    query = select(Quest).where(Quest.author_id == current_user.id).order_by(Quest.title) # Ищем квесты автора
    res = await db.execute(query)
    return res.scalars().all()                                                          # Отдаем список квестов автору

@router.get("/quests/{quest_id}")
async def get_quest_structure(quest_id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """ Получить полную структуру черновика квеста со всеми его шагами для автора """
    quest = await db.get(Quest, quest_id)
    if not quest or quest.author_id != current_user.id: raise HTTPException(status_code=403, detail="Нет прав доступа")
    s_query = select(Step).where(Step.quest_id == quest_id).order_by(Step.step_order)
    s_res = await db.execute(s_query)
    return {"quest": quest, "steps": s_res.scalars().all()}

@router.patch("/quests/{quest_id}")
async def edit_quest(quest_id: uuid.UUID, title: str = None, description: str = None, price: Decimal = None, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """ Редактирование метаданных черновика квеста автором """
    quest = await db.get(Quest, quest_id)
    if not quest or quest.author_id != current_user.id: raise HTTPException(status_code=403, detail="Нет прав")
    if title: quest.title = title
    if description: quest.description = description
    if price is not None: quest.price = price
    await db.commit()
    return {"status": "updated", "message": "Данные изменены"}

@router.post("/quests/{quest_id}/steps")
async def create_step(quest_id: uuid.UUID, payload: StepCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """ ИСПРАВЛЕНО: Вложенный путь для добавления шага/локации к конкретному квесту с проверкой прав """
    quest = await db.get(Quest, quest_id)                                               # Проверяем существование квеста
    if not quest or quest.author_id != current_user.id: raise HTTPException(status_code=403, detail="Нет прав")
    new_step = Step(quest_id=quest_id, step_order=payload.step_order, step_title=payload.step_title, target_lat=payload.target_lat, target_lon=payload.target_lon, proximity_radius=payload.proximity_radius)
    db.add(new_step)
    await db.flush()
    return {"status": "created", "step_id": new_step.id}

@router.delete("/quests/{quest_id}/steps/{step_id}")
async def delete_step(quest_id: uuid.UUID, step_id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """ ИСПРАВЛЕНО: Вложенный путь для удаления шага автором с автоматическим пересчетом порядка """
    step = await db.get(Step, step_id)
    if not step or step.quest_id != quest_id: raise HTTPException(status_code=404, detail="Шаг не найден в этом квесте")
    quest = await db.get(Quest, quest_id)
    if quest.author_id != current_user.id: raise HTTPException(status_code=403, detail="Нет прав")
    deleted_order = step.step_order
    await db.delete(step)
    shift_query = update(Step).where(Step.quest_id == quest.id, Step.step_order > deleted_order).values(step_order=Step.step_order - 1)
    await db.execute(shift_query)
    await db.commit()
    return {"status": "deleted", "message": "Шаг удален, порядок пересчитан"}
@router.post("/quests/{quest_id}/steps/{step_id}/questions")
async def create_question(quest_id: uuid.UUID, step_id: uuid.UUID, payload: QuestionCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """ ИСПРАВЛЕНО: Вложенный путь для привязки вопроса к шагу конкретного квеста с проверкой прав автора """
    step = await db.get(Step, step_id)                                                  # Ищем шаг в базе данных
    if not step or step.quest_id != quest_id: raise HTTPException(status_code=404, detail="Шаг не найден в этом квесте")
    quest = await db.get(Quest, quest_id)                                               # Проверяем сам квест
    if quest.author_id != current_user.id: raise HTTPException(status_code=403, detail="Нет прав доступа")
    
    new_q = Question(
        step_id=step_id,
        question_order=payload.question_order,
        question_text=payload.question_text,
        question_type=payload.question_type,
        correct_answer=payload.correct_answer,
        points=payload.points,
        timer=payload.timer
    )
    db.add(new_q)
    await db.flush()                                                                    # Генерируем ID для вопроса
    return {"status": "created", "question_id": new_q.id}


@router.post("/quests/{quest_id}/steps/{step_id}/questions/{question_id}/options")
async def add_quiz_option(quest_id: uuid.UUID, step_id: uuid.UUID, question_id: uuid.UUID, option_text: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """ ИСПРАВЛЕНО: Вложенный путь для добавления вариантов ответа к тестам (Quiz) """
    question = await db.get(Question, question_id)                                      # Проверяем существование вопроса
    if not question or question.step_id != step_id: raise HTTPException(status_code=404, detail="Вопрос не найден")
    new_opt = QuizOption(question_id=question_id, option_text=option_text)
    db.add(new_opt)
    await db.commit()                                                                   # Сохраняем вариант ответа в базу
    return {"status": "created", "message": "Вариант добавлен"}


@router.post("/quests/{quest_id}/publish")
async def publish_quest(quest_id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """ Опубликовать квест (сделать видимым в общем каталоге) """
    quest = await db.get(Quest, quest_id)
    if not quest or quest.author_id != current_user.id: raise HTTPException(status_code=403, detail="Нет прав")
    quest.is_published = True                                                           # Переключаем флаг публикации в БД
    await db.commit()
    return {"status": "published", "message": "Квест опубликован"}


# --- МЕНЕДЖМЕНТ МЕДИАФАЙЛОВ И ЗАГРУЗКА НА СЕРВЕР ---
UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)                                                  # Защита: создаем папку для картинок

@router.post("/media/upload")
async def upload_media_file(quest_id: uuid.UUID = None, step_id: uuid.UUID = None, question_id: uuid.UUID = None, file: UploadFile = File(...), db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """ Принимает реальный файл с фронтенда, сохраняет его на диск сервера и делает запись в БД """
    file_extension = os.path.splitext(file.filename)[1]                                 # Вытаскиваем расширение файла (.png/.jpg)
    unique_filename = f"{uuid.uuid4()}{file_extension}"                                 # Делаем уникальное UUID-имя файлу
    file_path = os.path.join(UPLOAD_DIR, unique_filename)                               # Собираем путь для сохранения на диск
    with open(file_path, "wb") as buffer:
        content = await file.read()                                                     # Читаем байты прилетевшего файла
        buffer.write(content)                                                           # Физически пишем картинку на диск
    web_url = f"/static/uploads/{unique_filename}"                                      # Ссылка для фронтенда на React
    new_media = Media(quest_id=quest_id, step_id=step_id, question_id=question_id, file_url=web_url, file_type="image")
    db.add(new_media)
    await db.commit()                                                                   # Сохраняем путь в PostgreSQL
    return {"status": "uploaded", "file_url": web_url}


# --- СВЯЗЫВАНИЕ ТЕГОВ С КВЕСТАМИ ---
@router.post("/quests/{quest_id}/tags/{tag_id}")
async def attach_tag_to_quest(quest_id: uuid.UUID, tag_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """ Привязать тег/категорию к квесту """
    check_q = select(QuestTag).where(QuestTag.quest_id == quest_id, QuestTag.tag_id == tag_id)
    res = await db.execute(check_q)
    if res.scalar_one_or_none(): return {"status": "exists", "message": "Тег уже привязан"}
    db.add(QuestTag(quest_id=quest_id, tag_id=tag_id))                                  # Привязываем категорию к квесту
    await db.commit()
    return {"status": "success", "message": "Тег добавлен к квесту"}

@router.delete("/quests/{quest_id}/tags/{tag_id}")
async def detach_tag_from_quest(quest_id: uuid.UUID, tag_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """ Удалить связь тега с квестом """
    query = select(QuestTag).where(QuestTag.quest_id == quest_id, QuestTag.tag_id == tag_id)
    res = await db.execute(query)
    link = res.scalar_one_or_none()
    if not link: raise HTTPException(status_code=404, detail="Связь не найдена")
    await db.delete(link)
    await db.commit()                                                                   # Стираем связь из PostgreSQL
    return {"status": "success", "message": "Тег отвязан от квеста"}


# --- СОЗДАНИЕ И УДАЛЕНИЕ САМИХ ТЕГОВ В СИСТЕМЕ ---
@router.post("/tags")
async def create_global_tag(tag_name: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """ Добавить новый глобальный тег/категорию в базу данных """
    check_q = select(Tag).where(Tag.name == tag_name)                                   # Ищем дубликат названия тега
    res = await db.execute(check_q)
    if res.scalar_one_or_none(): raise HTTPException(status_code=400, detail="Тег уже существует")
    new_tag = Tag(name=tag_name)
    db.add(new_tag)
    await db.commit()                                                                   # Сохраняем новый тег глобально
    return {"status": "created", "tag_name": tag_name}

@router.delete("/tags/{tag_id}")
async def delete_global_tag(tag_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """ Полностью удалить тег/категорию из системы по его ID """
    tag = await db.get(Tag, tag_id)
    if not tag: raise HTTPException(status_code=404, detail="Тег не найден")
    await db.delete(tag)
    await db.commit()                                                                   # Удаляем тег из PostgreSQL
    return {"status": "deleted", "message": f"Тег '{tag.name}' успешно удален из системы"}
