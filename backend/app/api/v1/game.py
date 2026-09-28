import uuid
import random                                                                           # Модуль для случайного выбора вопросов
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.v1.deps import get_current_user
from app.database.session import get_db
from app.models.quest import Quest
from app.models.purchase import UserPurchase
from app.models.progress import UserProgress
from app.models.step import Step
from app.models.question import Question, QuizOption
from app.models.user import User

from app.schemas.game import (
    CurrentStepResponse, 
    VerifyRequest, 
    VerifyResponse
)
from app.services.geo import check_proximity

router = APIRouter(prefix="/game", tags=["Game Engine"])


@router.post("/start/{quest_id}")
async def start_quest(quest_id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    РУЧКА СТАРТА: Проверяет оплату квеста, лимиты на одновременные игры,
    находит стартовую локацию и создает запись игрового прогресса в БД.
    """
    quest = await db.get(Quest, quest_id)                                               # Ищем квест в базе данных
    if not quest:
        raise HTTPException(status_code=404, detail="Квест не найден")

    if quest.price > 0:                                                                 # Если квест платный
        p_query = select(UserPurchase).where(UserPurchase.user_id == current_user.id, UserPurchase.quest_id == quest_id)
        p_res = await db.execute(p_query)
        if not p_res.scalar_one_or_none():
            raise HTTPException(status_code=402, detail="Payment Required")             # Блокируем, если квест не куплен

    limit_query = select(UserProgress).where(UserProgress.user_id == current_user.id, UserProgress.status == "in_progress")
    limit_res = await db.execute(limit_query)
    if limit_res.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Завершите текущий квест")          # Запрещаем играть в два квеста сразу

    step_query = select(Step).where(Step.quest_id == quest_id, Step.step_order == 1)    # Ищем самый первый шаг квеста
    step_res = await db.execute(step_query)
    first_step = step_res.scalar_one_or_none()
    if not first_step:
        raise HTTPException(status_code=400, detail="У квеста нет шагов")

    new_progress = UserProgress(
        user_id=current_user.id,
        quest_id=quest_id,
        current_step_id=first_step.id,
        status="in_progress",
        total_score=0,
        started_at=datetime.now(timezone.utc)                                           # Фиксируем точное время старта
    )
    db.add(new_progress)
    return {"status": "started", "message": "Квест успешно запущен"}


@router.get("/current")
async def get_current_step(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    РУЧКА ТЕКУЩЕГО ШАГА: Находит активный шаг, выбирает случайные N вопросов
    из базы данных для этого шага, подтягивает варианты ответов и
    фиксирует время выдачи вопроса для контроля таймера.
    """
    p_query = select(UserProgress).where(UserProgress.user_id == current_user.id, UserProgress.status == "in_progress")
    p_res = await db.execute(p_query)
    progress = p_res.scalar_one_or_none()                                               # Проверяем, играет ли юзер сейчас
    if not progress:
        raise HTTPException(status_code=404, detail="Нет активных квестов")

    step = await db.get(Step, progress.current_step_id)                                 # Достаем данные текущей локации

    # Выбираем абсолютно все вопросы, которые автор привязал к этой локации
    q_query = select(Question).where(Question.step_id == step.id)
    q_res = await db.execute(q_query)
    all_questions = list(q_res.scalars().all())
    if not all_questions:
        raise HTTPException(status_code=404, detail="Вопросы для шага не найдены")

    # РАНДОМИЗАЦИЯ: Перемешиваем список вопросов случайным образом
    random.shuffle(all_questions)
    
    # Берем первый случайный вопрос из перемешанного пула (или можно отдавать массив из 3-х штук)
    current_question = all_questions[0]

    # Загружаем из БД варианты ответов (для тестов типа Quiz)
    options_list = []
    if current_question.question_type == "quiz":
        opt_query = select(QuizOption).where(QuizOption.question_id == current_question.id)
        opt_res = await db.execute(opt_query)
        options_list = [{"id": o.id, "option_text": o.option_text} for o in opt_res.scalars().all()]

    # ТАЙМЕР: Обновляем started_at текущим временем, чтобы засечь время старта ответа на этот вопрос
    progress.started_at = datetime.now(timezone.utc)

    # ДЛЯ MVP/ПРОЕКТА: Предположим, что автор задает таймер в поле вопроса (например, 60 секунд)
    # Если в твоей модели нет поля timer, мы берем стандартные 60 секунд как значение по умолчанию
    question_timer_seconds = getattr(current_question, "timer", 60)

    return {
        "step_title": step.step_title,
        "target_lat": step.target_lat,
        "target_lon": step.target_lon,
        "timer_limit": question_timer_seconds,                                          # Передаем фронтенду лимит времени в сек.
        "question": {
            "id": current_question.id,
            "question_order": current_question.question_order,
            "question_text": current_question.question_text,
            "question_type": current_question.question_type,
            "options": options_list                                                     # Передаем список вариантов ответов
        }
    }


@router.post("/pause")
async def toggle_pause(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    РУЧКА ПАУЗЫ: Замораживает игровой процесс. Защищена ограничением:
    поставить игру на паузу можно не чаще, чем один раз в 5 минут.
    """
    query = select(UserProgress).where(UserProgress.user_id == current_user.id, UserProgress.status == "in_progress")
    res = await db.execute(query)
    progress = res.scalar_one_or_none()                                                 # Ищем запущенную сессию игры
    if not progress:
        raise HTTPException(status_code=404, detail="Активный квест не найден")

    now = datetime.now(timezone.utc)
    # Защита от спама: проверяем, прошло ли 5 минут с момента последнего обновления таймера
    if progress.started_at and (now - progress.started_at.replace(tzinfo=timezone.utc)) < timedelta(minutes=5):
        raise HTTPException(status_code=429, detail="Пауза доступна раз в 5 минут")     # Отклоняем слишком частые паузы

    progress.started_at = now                                                           # Сбрасываем метку времени на текущую
    return {"status": "paused", "message": "Игра приостановлена"}


@router.post("/skip")
async def skip_question(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    РУЧКА ПРОПУСКА: Позволяет пропустить текущую локацию/вопрос без начисления очков
    и автоматически переводит игрока на следующую точку по порядку (или завершает квест).
    """
    query = select(UserProgress).where(UserProgress.user_id == current_user.id, UserProgress.status == "in_progress")
    res = await db.execute(query)
    progress = res.scalar_one_or_none()                                                 # Проверяем наличие активной игры
    if not progress:
        raise HTTPException(status_code=404, detail="У вас нет активной игры")

    step = await db.get(Step, progress.current_step_id)                                 # Узнаем, на каком мы сейчас шаге
    
    # Ищем в PostgreSQL следующий шаг квеста (текущий порядок + 1)
    next_step_query = select(Step).where(Step.quest_id == progress.quest_id, Step.step_order == step.step_order + 1)
    next_step_res = await db.execute(next_step_query)
    next_step = next_step_res.scalar_one_or_none()

    if next_step:
        progress.current_step_id = next_step.id                                         # Переключаем игрока на новый шаг в БД
        return {"status": "skipped", "message": "Шаг пропущен. Очки не начислены.", "game_status": "NEW_STEP"}
    else:
        progress.status = "completed"                                                   # Если это был финал, закрываем квест
        progress.finished_at = datetime.now(timezone.utc)                               # Пишем точное время завершения квеста
        return {"status": "completed", "message": "Квест завершен пропуском шага", "game_status": "QUEST_COMPLETED"}


@router.post("/cancel")
async def cancel_quest(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    РУЧКА ОТМЕНЫ: Полностью уничтожает текущую игровую сессию из базы данных,
    позволяя игроку начать этот или другой квест с чистого листа.
    """
    query = select(UserProgress).where(UserProgress.user_id == current_user.id, UserProgress.status == "in_progress")
    res = await db.execute(query)
    progress = res.scalar_one_or_none()
    if not progress:
        raise HTTPException(status_code=404, detail="Активный квест не найден")

    await db.delete(progress)                                                           # Стираем запись прогресса из базы данных
    return {"status": "cancelled", "message": "Квест успешно отменен"}


@router.post("/verify", response_model=VerifyResponse)
async def verify_answer(
    payload: VerifyRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    РУЧКА ПРОВЕРКИ: Проверяет таймер ответа, GPS-радиус игрока через формулу Гаверсинусов,
    сверяет текст ответа и переводит на новый шаг либо закрывает квест с победой.
    """
    # 1. Ищем запущенную игровую сессию пользователя в базе данных
    p_query = select(UserProgress).where(UserProgress.user_id == current_user.id, UserProgress.status == "in_progress")
    p_res = await db.execute(p_query)
    progress = p_res.scalar_one_or_none()
    if not progress:
        raise HTTPException(status_code=404, detail="Активная игра не найдена")

    # 2. Вытаскиваем из PostgreSQL текущую гео-локацию (шаг)
    step = await db.get(Step, progress.current_step_id)

    # 3. Ищем вопрос, на который сейчас отвечает игрок (для проверки ответа)
    q_query = select(Question).where(Question.step_id == step.id)                       # Ищем вопросы этого шага
    q_res = await db.execute(q_query)
    all_questions = q_res.scalars().all()                                              # Выгружаем список в память
    if not all_questions:
        raise HTTPException(status_code=404, detail="Вопрос базы данных не найден")
    
    # Так как на прошлом шаге мы выбирали вопрос, здесь для MVP берем целевой вопрос
    current_question = all_questions[0]                                                 # Берём активный вопрос шага

    # 4. ПРОВЕРКА ТАЙМЕРА: Считаем, сколько секунд прошло с момента выдачи вопроса
    now = datetime.now(timezone.utc)
    time_spent = (now - progress.started_at.replace(tzinfo=timezone.utc)).total_seconds()
    question_timer_seconds = getattr(current_question, "timer", 60)                     # Узнаем лимит времени автора
    
    if time_spent > question_timer_seconds:                                             # Если игрок не уложился во время
        return {
            "success": False,
            "message": f"Время вышло! Вы отвечали {time_spent:.0f} сек. Лимит: {question_timer_seconds} сек.",
            "status": "NEW_STEP",                                                       # Штрафуем и принудительно шлем на новый шаг
            "total_score": progress.total_score
        }

    # 5. ПРОВЕРКА ГЕОПОЗИЦИИ: Сверяем «живой» GPS игрока с точкой цели через Гаверсинус
    is_near = check_proximity(
        lat1=payload.latitude,                                                          # Широта со смартфона игрока
        lon1=payload.longitude,                                                         # Долгота со смартфона игрока
        lat2=step.target_lat,                                                           # Широта цели из нашей базы
        lon2=step.target_lon,                                                           # Долгота цели из нашей базы
        radius_meters=step.proximity_radius                                             # Радиус шага (например, 30 метров)
    )
    if not is_near:                                                                     # Если игрок схитрил и сидит дома
        return {
            "success": False,
            "message": "Вы слишком далеко от нужного места! Подойдите ближе.",
            "status": "SAME_STEP",                                                      # Оставляем на этом же шаге
            "total_score": progress.total_score
        }

    # 6. ПРОВЕРКА ОТВЕТА: Сверяем текст ответа (без учета регистра и пробелов)
    user_ans_clean = payload.user_answer.strip().lower()                                # Чистим ответ игрока
    correct_ans_clean = current_question.correct_answer.strip().lower()                 # Чистим правильный ответ из базы
    
    if user_ans_clean != correct_ans_clean:                                             # Если ответ не совпал
        return {
            "success": False,
            "message": "Ответ неверный! Попробуйте еще раз или подумайте.",
            "status": "SAME_STEP",                                                      # Даем игроку еще попытку на месте
            "total_score": progress.total_score
        }

    # 7. НАЧИСЛЕНИЕ ОЧКОВ: Если таймер, гео и ответ совпали — начисляем баллы
    progress.total_score += current_question.points                                     # Прибавляем очки за вопрос в БД

    # 8. ПЕРЕХОД НА СЛЕДУЮЩИЙ ШАГ: Ищем, есть ли следующий шаг по порядку (order + 1)
    next_step_query = select(Step).where(Step.quest_id == progress.quest_id, Step.step_order == step.step_order + 1)
    next_step_res = await db.execute(next_step_query)
    next_step = next_step_res.scalar_one_or_none()

    if next_step:
        progress.current_step_id = next_step.id                                         # Меняем ID шага в прогрессе игрока
        await db.commit()                                                               # Записываем изменения в PostgreSQL
        return {
            "success": True,
            "message": "Правильно! Отличная работа. Двигайтесь к следующей точке.",
            "status": "NEW_STEP",                                                       # Фронтенд перерисует экран под новую точку
            "total_score": progress.total_score
        }
    else:
        # 9. ФИНАЛ КВЕСТА: Если шагов больше нет, закрываем игру с победой
        progress.status = "completed"                                                   # Меняем статус сессии на завершенный
        progress.finished_at = datetime.now(timezone.utc)                               # Пишем точное время триумфа
        await db.commit()                                                               # Фиксируем всё в базе данных
        return {
            "success": True,
            "message": "Поздравляем! Вы полностью прошли этот квест!",
            "status": "QUEST_COMPLETED",                                                # Сигнал фронтенду открыть экран победы
            "total_score": progress.total_score
        }
