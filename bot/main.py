
import asyncio
import json
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, StateFilter, BaseFilter
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton, BufferedInputFile,
    FSInputFile, ReplyKeyboardMarkup, KeyboardButton, TelegramObject, User,
    Message, CallbackQuery
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.exceptions import TelegramBadRequest
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from pathlib import Path
from typing import Optional
import aiofiles
import os
import csv
import database as db

# === FastAPI HTTP API ===
from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnswerSubmission(BaseModel):
    task_id: int
    answer: str
    user_id: int = 0  # Default to anonymous user
    email: str = ""  # For web users

class WebUserInfo(BaseModel):
    email: str
    name: str
    google_id: str

class NicknameUpdate(BaseModel):
    email: str
    nickname: str

# Admin API models
class AdminTaskCreate(BaseModel):
    correct_option: str
    answer_type: str = "quiz"

class AdminTaskUpdate(BaseModel):
    correct_option: str = None
    answer_type: str = None


# Valid quiz options constant
VALID_QUIZ_OPTIONS = ["A", "B", "C", "D"]

# Admin emails that have access to admin panel (can be configured via environment variable)
# Format: comma-separated list of emails, e.g., "ernurreen@gmail.com"
_admin_emails_env = os.getenv("ADMIN_EMAILS", "ernurreen@gmail.com")
ADMIN_EMAILS = {email.strip().lower() for email in _admin_emails_env.split(",") if email.strip()}

def convert_to_relative_path(absolute_path: Optional[str], url_prefix: str) -> Optional[str]:
    """Convert an absolute file path to a relative URL path.
    
    Returns path without leading slash (e.g., 'images/task_1.jpg') so frontend
    can safely concatenate with apiUrl using a single slash.
    """
    if not absolute_path:
        return None
    # Remove leading slash from url_prefix to avoid double slashes in frontend
    prefix = url_prefix.lstrip('/')
    return f"{prefix}/{Path(absolute_path).name}"


def extract_filename(path: Optional[str]) -> Optional[str]:
    """Extract filename from a path string safely.
    
    Returns the filename part of the path, or None if path is empty/None.
    """
    if not path:
        return None
    return Path(path).name

@app.get("/api/task/random")
async def get_random_task(email: str = ""):
    """Get random unsolved task for user"""
    if email:
        task = await db.get_random_unsolved_task_web(email)
    else:
        task = await db.get_random_unsolved_task(0)  # user_id=0 — для публичного API
    if not task:
        raise HTTPException(status_code=404, detail="No tasks found")
    
    return {
        "id": task["id"],
        "image_path": convert_to_relative_path(task["image_path"], "/images"),
        "answer_type": task.get("answer_type", "quiz"),
        "solution_image_path": convert_to_relative_path(task.get("solution_image_path"), "/solutions"),
        "correct_option": task.get("correct_option"),  # For checking answers
    }

@app.get("/api/rating")
async def get_rating(limit: int = 10):
    """Get top users leaderboard"""
    users = await db.get_top_users(limit)
    return {"users": users}

@app.get("/api/user/{user_id}")
async def get_user_stats(user_id: int):
    """Get user statistics"""
    stats = await db.get_user_stats(user_id)
    if not stats:
        raise HTTPException(status_code=404, detail="User not found")
    return stats

@app.post("/api/task/check")
async def check_answer(submission: AnswerSubmission):
    """Check if answer is correct and update user progress"""
    task = await db.get_task(submission.task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    user_answer = submission.answer.strip().lower().replace(',', '.')
    correct_answer = task["correct_option"].strip().lower().replace(',', '.')
    
    is_correct = user_answer == correct_answer
    newly_unlocked_achievements = []
    
    # Update progress for web users
    if submission.email:
        # Ensure web user exists (use email as name if not provided separately)
        await db.ensure_web_user(submission.email, submission.email, "")
        
        if is_correct:
            # Check if already solved
            if not await db.has_web_solved(submission.email, submission.task_id):
                await db.mark_web_solved_and_add_point(submission.email, submission.task_id)
                # Check for new achievements
                newly_unlocked_achievements = await db.check_and_unlock_achievements(submission.email)
        else:
            await db.mark_web_attempted(submission.email, submission.task_id)
    
    return {
        "correct": is_correct,
        "correct_answer": task["correct_option"] if not is_correct else None,
        "solution_image_path": convert_to_relative_path(task.get("solution_image_path"), "/solutions"),
        "newly_unlocked_achievements": newly_unlocked_achievements
    }

@app.post("/api/user/web")
async def create_or_update_web_user(user: WebUserInfo):
    """Create or update web user"""
    await db.ensure_web_user(user.email, user.name, user.google_id)
    stats = await db.get_web_user_stats(user.email)
    return stats

@app.get("/api/user/web/{email}")
async def get_web_user_stats_endpoint(email: str):
    """Get web user statistics"""
    stats = await db.get_web_user_stats(email)
    if not stats:
        # Create user if not exists (use email as name and empty google_id)
        await db.ensure_web_user(email, email, "")
        stats = await db.get_web_user_stats(email)
    return stats

@app.post("/api/user/web/nickname")
async def update_nickname(data: NicknameUpdate):
    """Update web user nickname"""
    try:
        await db.update_web_user_nickname(data.email, data.nickname)
        stats = await db.get_web_user_stats(data.email)
        return stats
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/league/{league}")
async def get_league_leaderboard_endpoint(league: str, limit: int = 30, group_id: int = None):
    """Get league leaderboard (weekly points)
    
    If group_id is provided, returns only users in that group.
    Otherwise returns all users in the league (for backward compatibility).
    """
    if league not in db.LEAGUES:
        raise HTTPException(status_code=400, detail="Invalid league")
    users = await db.get_league_leaderboard(league, limit, group_id=group_id)
    return {
        "league": league,
        "league_name": db.LEAGUE_NAMES.get(league, league),
        "group_id": group_id,
        "users": users
    }

@app.get("/api/user/web/{email}/league")
async def get_web_user_league(email: str):
    """Get web user league info including group"""
    league_info = await db.get_web_user_league_info(email)
    if not league_info:
        raise HTTPException(status_code=404, detail="User not found")
    return league_info

@app.get("/api/leagues")
async def get_all_leagues():
    """Get all available leagues"""
    return {
        "leagues": [
            {"id": league, "name": db.LEAGUE_NAMES.get(league, league)}
            for league in db.LEAGUES
        ]
    }

@app.get("/api/user/web/{email}/achievements")
async def get_web_user_achievements(email: str):
    """Get web user achievements"""
    achievements = await db.get_user_achievements(email)
    return {"achievements": achievements}

@app.post("/api/user/web/{email}/achievements/check")
async def check_achievements(email: str):
    """Check and unlock any new achievements for user"""
    newly_unlocked = await db.check_and_unlock_achievements(email)
    achievements = await db.get_user_achievements(email)
    return {
        "newly_unlocked": newly_unlocked,
        "achievements": achievements
    }

def validate_and_get_file_path(filename: str, base_dir: Path) -> Path:
    """
    Validate filename and return safe file path within base directory.
    Raises HTTPException if validation fails.
    """
    # Validate filename to prevent path traversal and empty filenames
    if not filename or '/' in filename or '\\' in filename or filename.startswith('..'):
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    file_path = base_dir / filename
    # Ensure the resolved path is still within base_dir (using resolve() to prevent symlink attacks)
    if not file_path.resolve().is_relative_to(base_dir.resolve()):
        raise HTTPException(status_code=400, detail="Invalid file path")
    
    return file_path

@app.get("/images/{filename}")
async def serve_image(filename: str):
    """Serve task images"""
    file_path = validate_and_get_file_path(filename, IMAGES_DIR)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(file_path)

@app.get("/solutions/{filename}")
async def serve_solution(filename: str):
    """Serve solution images"""
    file_path = validate_and_get_file_path(filename, SOLUTIONS_DIR)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Solution not found")
    return FileResponse(file_path)


# ========== ADMIN API ==========

def verify_admin_email(email: str = Header(None, alias="X-Admin-Email")) -> str:
    """Verify that the request is from an admin user"""
    if not email or email.lower() not in ADMIN_EMAILS:
        raise HTTPException(status_code=403, detail="Admin access required")
    return email


@app.get("/api/admin/tasks")
async def admin_get_all_tasks(
    page: int = 1,
    limit: int = 20,
    email: str = Header(None, alias="X-Admin-Email")
):
    """Get all tasks with pagination (admin only)"""
    verify_admin_email(email)
    
    # Get all tasks
    all_tasks = await db.list_tasks(limit=1000)
    
    # Calculate pagination
    total = len(all_tasks)
    start = (page - 1) * limit
    end = start + limit
    tasks = all_tasks[start:end]
    
    # Format tasks for frontend
    formatted_tasks = []
    for task in tasks:
        formatted_tasks.append({
            "id": task["id"],
            "image_path": convert_to_relative_path(task["image_path"], "/images"),
            "correct_option": task["correct_option"],
            "answer_type": task.get("answer_type", "quiz"),
            "solution_image_path": convert_to_relative_path(task.get("solution_image_path"), "/solutions"),
            "created_at": task.get("created_at"),
            "created_by": task.get("created_by"),
        })
    
    return {
        "tasks": formatted_tasks,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit if total > 0 else 1
    }


@app.get("/api/admin/tasks/{task_id}")
async def admin_get_task(
    task_id: int,
    email: str = Header(None, alias="X-Admin-Email")
):
    """Get a specific task (admin only)"""
    verify_admin_email(email)
    
    task = await db.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {
        "id": task["id"],
        "image_path": convert_to_relative_path(task["image_path"], "/images"),
        "correct_option": task["correct_option"],
        "answer_type": task.get("answer_type", "quiz"),
        "solution_image_path": convert_to_relative_path(task.get("solution_image_path"), "/solutions"),
        "created_at": task.get("created_at"),
        "created_by": task.get("created_by"),
    }


@app.post("/api/admin/tasks")
async def admin_create_task(
    task_image: UploadFile = File(...),
    solution_image: UploadFile = File(...),
    correct_option: str = Form(...),
    answer_type: str = Form("quiz"),
    email: str = Header(None, alias="X-Admin-Email")
):
    """Create a new task (admin only)"""
    verify_admin_email(email)
    
    # Validate answer type
    if answer_type not in ["quiz", "text"]:
        raise HTTPException(status_code=400, detail="Invalid answer type. Must be 'quiz' or 'text'")
    
    # Validate quiz answer
    if answer_type == "quiz" and correct_option.upper() not in VALID_QUIZ_OPTIONS:
        raise HTTPException(status_code=400, detail=f"Quiz answer must be one of: {', '.join(VALID_QUIZ_OPTIONS)}")
    
    # Create the task first to get the ID
    task_id = await db.add_task(
        image_path="",
        correct_option=correct_option.upper() if answer_type == "quiz" else correct_option,
        solution_image_path="",
        answer_type=answer_type,
        created_by=0  # Web admin
    )
    
    # Use absolute paths for file storage
    base_dir = Path(__file__).parent.absolute()
    images_dir = base_dir / "images"
    solutions_dir = base_dir / "solutions"
    images_dir.mkdir(parents=True, exist_ok=True)
    solutions_dir.mkdir(parents=True, exist_ok=True)
    
    # Save task image
    task_image_path = images_dir / f"task_{task_id}.jpg"
    try:
        content = await task_image.read()
        async with aiofiles.open(task_image_path, "wb") as f:
            await f.write(content)
        await db.update_task_image_path(task_id, str(task_image_path))
    except Exception as e:
        await db.delete_task(task_id)
        raise HTTPException(status_code=500, detail=f"Failed to save task image: {str(e)}")
    
    # Save solution image
    solution_image_path = solutions_dir / f"solution_{task_id}.jpg"
    try:
        content = await solution_image.read()
        async with aiofiles.open(solution_image_path, "wb") as f:
            await f.write(content)
        await db.update_task_solution_image_path(task_id, str(solution_image_path))
    except Exception as e:
        # Clean up task image if solution fails
        if task_image_path.exists():
            task_image_path.unlink()
        await db.delete_task(task_id)
        raise HTTPException(status_code=500, detail=f"Failed to save solution image: {str(e)}")
    
    return {
        "id": task_id,
        "image_path": convert_to_relative_path(str(task_image_path), "/images"),
        "correct_option": correct_option.upper() if answer_type == "quiz" else correct_option,
        "answer_type": answer_type,
        "solution_image_path": convert_to_relative_path(str(solution_image_path), "/solutions"),
        "message": "Task created successfully"
    }


@app.put("/api/admin/tasks/{task_id}")
async def admin_update_task(
    task_id: int,
    task_image: UploadFile = File(None),
    solution_image: UploadFile = File(None),
    correct_option: str = Form(None),
    answer_type: str = Form(None),
    email: str = Header(None, alias="X-Admin-Email")
):
    """Update an existing task (admin only)"""
    verify_admin_email(email)
    
    task = await db.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Use absolute paths for file storage
    base_dir = Path(__file__).parent.absolute()
    images_dir = base_dir / "images"
    solutions_dir = base_dir / "solutions"
    
    # Update correct_option if provided
    if correct_option is not None:
        effective_answer_type = answer_type if answer_type else task.get("answer_type", "quiz")
        if effective_answer_type == "quiz" and correct_option.upper() not in VALID_QUIZ_OPTIONS:
            raise HTTPException(status_code=400, detail=f"Quiz answer must be one of: {', '.join(VALID_QUIZ_OPTIONS)}")
        await db.update_task_correct_option(
            task_id, 
            correct_option.upper() if effective_answer_type == "quiz" else correct_option
        )
    
    # Update task image if provided
    if task_image:
        task_image_path = images_dir / f"task_{task_id}.jpg"
        try:
            content = await task_image.read()
            async with aiofiles.open(task_image_path, "wb") as f:
                await f.write(content)
            await db.update_task_image_path(task_id, str(task_image_path))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to save task image: {str(e)}")
    
    # Update solution image if provided
    if solution_image:
        solution_image_path = solutions_dir / f"solution_{task_id}.jpg"
        try:
            content = await solution_image.read()
            async with aiofiles.open(solution_image_path, "wb") as f:
                await f.write(content)
            await db.update_task_solution_image_path(task_id, str(solution_image_path))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to save solution image: {str(e)}")
    
    # Get updated task
    updated_task = await db.get_task(task_id)
    
    return {
        "id": updated_task["id"],
        "image_path": convert_to_relative_path(updated_task["image_path"], "/images"),
        "correct_option": updated_task["correct_option"],
        "answer_type": updated_task.get("answer_type", "quiz"),
        "solution_image_path": convert_to_relative_path(updated_task.get("solution_image_path"), "/solutions"),
        "message": "Task updated successfully"
    }


@app.delete("/api/admin/tasks/{task_id}")
async def admin_delete_task(
    task_id: int,
    email: str = Header(None, alias="X-Admin-Email")
):
    """Delete a task (admin only)"""
    verify_admin_email(email)
    
    task = await db.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Delete image files
    if task["image_path"] and Path(task["image_path"]).exists():
        Path(task["image_path"]).unlink(missing_ok=True)
    if task.get("solution_image_path") and Path(task["solution_image_path"]).exists():
        Path(task["solution_image_path"]).unlink(missing_ok=True)
    
    # Delete from database
    await db.delete_task(task_id)
    
    return {"message": f"Task {task_id} deleted successfully"}


@app.get("/api/admin/tasks/export")
async def admin_export_tasks(email: str = Header(None, alias="X-Admin-Email")):
    """Export all tasks as JSON for backup purposes (admin only)
    
    This endpoint exports task metadata. Images should be backed up separately.
    """
    verify_admin_email(email)
    
    tasks = await db.get_all_tasks_for_export()
    
    # Format tasks for export (exclude absolute paths, include relative paths)
    export_data = []
    for task in tasks:
        export_data.append({
            "id": task["id"],
            "correct_option": task["correct_option"],
            "answer_type": task.get("answer_type", "quiz"),
            "image_filename": extract_filename(task["image_path"]),
            "solution_filename": extract_filename(task.get("solution_image_path")),
            "created_at": task.get("created_at"),
            "created_by": task.get("created_by"),
        })
    
    return {
        "export_version": "1.0",
        "total_tasks": len(export_data),
        "note": "Images are not included in this export. Download them separately from /images/ and /solutions/ endpoints.",
        "tasks": export_data
    }


@app.get("/api/admin/verify")
async def admin_verify(email: str = Header(None, alias="X-Admin-Email")):
    """Verify if the user is an admin"""
    if not email or email.lower() not in ADMIN_EMAILS:
        # Debug logging for troubleshooting (check server console)
        print(f"Admin verify failed - Email: '{email}', Normalized: '{email.lower() if email else None}', Admin emails: {ADMIN_EMAILS}")
        return {"is_admin": False}
    return {"is_admin": True, "email": email}


# ========== НАСТРОЙКИ ==========
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN environment variable is required")
ADMIN_IDS = {5423071866}

# Директории - use absolute paths based on script location
BASE_DIR = Path(__file__).parent.absolute()
IMAGES_DIR = BASE_DIR / "images"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)
SOLUTIONS_DIR = BASE_DIR / "solutions"
SOLUTIONS_DIR.mkdir(parents=True, exist_ok=True)

bot = Bot(token=TOKEN)
dp = Dispatcher()


# ========== MIDDLEWARE И ФИЛЬТРЫ ==========

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


class IsAdminFilter(BaseFilter):
    async def __call__(self, obj: TelegramObject, event_from_user: User) -> bool:
        return is_admin(event_from_user.id)


class RegisterUserMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        user = data.get("event_from_user")
        if user and user.id:
            await db.ensure_user(user.id, user.username, user.full_name)
        return await handler(event, data)


async def get_dir_size(path: Path) -> float:
    """Calculate directory size asynchronously to avoid blocking the event loop."""
    total_size = 0
    try:
        # Run blocking os.walk in a thread pool to avoid blocking the event loop
        import asyncio
        loop = asyncio.get_event_loop()
        
        def _calculate_size():
            size = 0
            for dirpath, dirnames, filenames in os.walk(path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    if not os.path.islink(fp): 
                        size += os.path.getsize(fp)
            return size
        
        total_size = await loop.run_in_executor(None, _calculate_size)
    except Exception:
        return 0.0
    return round(total_size / (1024 * 1024), 2)


# ========== FSM СОСТОЯНИЯ ==========
class AddTaskStates(StatesGroup):
    waiting_for_photo = State()
    waiting_for_type = State()
    waiting_for_correct = State()
    waiting_for_solution_photo = State()


class EditTaskStates(StatesGroup):
    waiting_for_id = State()
    waiting_for_action = State()
    waiting_for_new_data = State()


class UserStates(StatesGroup):
    solving_task = State()


# ========== КЛАВИАТУРЫ ==========
def make_main_reply_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="/task")], 
            [KeyboardButton(text="/profile"), KeyboardButton(text="/league")],
            [KeyboardButton(text="/rating")]
        ],
        resize_keyboard=True, one_time_keyboard=False
    )


def make_options_keyboard(task_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="A", callback_data=f"answer:{task_id}:A"),
         InlineKeyboardButton(text="B", callback_data=f"answer:{task_id}:B")],
        [InlineKeyboardButton(text="C", callback_data=f"answer:{task_id}:C"),
         InlineKeyboardButton(text="D", callback_data=f"answer:{task_id}:D")]
    ])


def make_task_type_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔠 Тест (A/B/C/D)", callback_data="type_quiz")],
        [InlineKeyboardButton(text="✍️ Қолмен енгізу", callback_data="type_text")]
    ])


def make_admin_task_keyboard(task_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="❌ Есепті жою", callback_data=f"delete_task:{task_id}")]])


def make_task_result_keyboard(task_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔎 Шешімін көру", callback_data=f"show_solution:{task_id}")],
        [InlineKeyboardButton(text="➡️ Келесі есеп", callback_data="next_task")]
    ])


def make_edit_options_keyboard(task_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Жауапты өзгерту", callback_data=f"edit_action:{task_id}:answer")],
        [InlineKeyboardButton(text="🏞️ Шешімнің фотосын ауыстыру", callback_data=f"edit_action:{task_id}:solution_photo")],
        [InlineKeyboardButton(text="🖼️ Есептің фотосын ауыстыру", callback_data=f"edit_action:{task_id}:task_photo")]
    ])


# ========== ЛОГИКА ЗАДАЧИ (ГИБРИДНАЯ) ==========
async def send_random_task_to_user(bot: Bot, chat_id: int, user_id: int, state: FSMContext):
    task = await db.get_random_unsolved_task(user_id)

    if not task:
        msg = "🎉 Құттықтаймыз! Сіз барлық қолжетімді есептерді шештіңіз."
        if not await db.list_tasks(limit=1): msg = "Әзірге есептер жоқ."
        await bot.send_message(chat_id, msg)
        return

    img_path = Path(task["image_path"])
    if not img_path.exists():
        await bot.send_message(chat_id, f"Қате: ID {task['id']} файлы табылмады.")
        return

    try:
        async with aiofiles.open(img_path, "rb") as f:
            input_file = BufferedInputFile(await f.read(), filename=img_path.name)

        answer_type = task.get("answer_type", "quiz")

        if answer_type == "text":
            await bot.send_photo(
                chat_id=chat_id, photo=input_file,
                caption="✍️ **Бұл есеп қолмен енгізуді талап етеді.**\nЖауапты хабарламамен енгізіңіз (сан немесе мәтін).",
                parse_mode="Markdown"
            )
            await state.update_data(current_task_id=task["id"])
            await state.set_state(UserStates.solving_task)
        else:
            keyboard = make_options_keyboard(task["id"])
            await bot.send_photo(
                chat_id=chat_id, photo=input_file,
                caption="Дұрыс жауапты таңдаңыз:", reply_markup=keyboard
            )
    except Exception as e:
        await bot.send_message(chat_id, f"Жіберу қатесі: {e}")


# ========== ОБРАБОТЧИКИ ПОЛЬЗОВАТЕЛЕЙ ==========
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Сәлеметсіз бе! Мен — математикалық есептерге арналған ботпын.", reply_markup=make_main_reply_keyboard())


@dp.message(Command("task"))
async def cmd_task(message: Message, state: FSMContext):
    await state.clear()
    await send_random_task_to_user(bot, message.chat.id, message.from_user.id, state)


@dp.callback_query(F.data == "next_task")
async def handle_next_task_button(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.clear()
    await send_random_task_to_user(bot, call.message.chat.id, call.from_user.id, state)


@dp.message(Command("profile"))
async def cmd_profile(message: Message):
    stats = await db.get_user_stats(message.from_user.id)
    if not stats: return
    
    name = stats.get('username') or stats.get('full_name', 'Пользователь')
    league = stats.get('league', 'bronze')
    league_name = db.LEAGUE_NAMES.get(league, league)
    weekly_points = stats.get('weekly_points', 0)
    
    # Лигадағы орын
    league_info = await db.get_user_league_info(message.from_user.id)
    rank = league_info.get('rank', '?') if league_info else '?'
    
    text = (
        f"👤 **{name}**\n\n"
        f"🏆 Лига: {league_name}\n"
        f"📊 Орын: #{rank}\n\n"
        f"⚡ Апталық ұпай: {weekly_points}\n"
        f"💎 Жалпы ұпай: {stats['points']}\n"
        f"🧩 Шешілгені: {stats['solved_count']}"
    )
    await message.answer(text, parse_mode="Markdown")


@dp.message(Command("league"))
async def cmd_league(message: Message):
    """Лигадағы рейтингті көрсету (өз тобыңызда)"""
    league_info = await db.get_user_league_info(message.from_user.id)
    if not league_info:
        await message.answer("Профиль табылмады.")
        return
    
    league = league_info['league']
    league_name = db.LEAGUE_NAMES.get(league, league)
    group_id = league_info.get('league_group_id')
    
    # Өз тобының рейтингін алу
    if group_id:
        leaderboard = await db.get_league_leaderboard(league, limit=30, group_id=group_id)
        group_info = f" (Топ #{group_id})"
    else:
        leaderboard = await db.get_league_leaderboard(league, limit=30)
        group_info = ""
    
    lines = [f"🏆 **{league_name} лигасы{group_info}**\n"]
    
    if not leaderboard:
        lines.append("Әзірше қолданушылар жоқ.")
    else:
        for i, r in enumerate(leaderboard, 1):
            emoji = "👑" if i == 1 else f"{i}."
            if r["source"] == "web":
                name = r["nickname"] or r["name"] or "Web User"
            else:
                name = r["username"] or r["full_name"] or str(r["user_id"])
            
            # Highlight current user
            if r.get("user_id") == message.from_user.id:
                name = f"**{name} (Сіз)**"
            
            lines.append(f"{emoji} {name} — ⚡{r['weekly_points']}")
    
    lines.append(f"\n💡 Топ {db.PROMOTION_THRESHOLD} көтеріледі, соңғы {db.DEMOTION_THRESHOLD} түседі")
    if not group_id:
        lines.append("⚠️ Топқа қосылу үшін алғаш есеп шешіңіз!")
    
    await message.answer("\n".join(lines), parse_mode="Markdown")


@dp.message(Command("rating"))
async def cmd_rating(message: Message):
    top = await db.get_top_users(10)
    lines = ["🏆 **Жалпы рейтинг (барлық уақыт):**\n"]
    for i, r in enumerate(top, 1):
        # Handle both Telegram and web users
        if r["source"] == "web":
            name = r["nickname"] or r["name"] or r["email"] or "Web User"
        else:
            name = r["username"] or r["full_name"] or str(r["user_id"])
        lines.append(f"{i}. {name} — 💎{r['points']}")
    lines.append("\n💡 /league - Лигадағы апталық рейтинг")
    await message.answer("\n".join(lines), parse_mode="Markdown")


# ========== ОБРАБОТКА ОТВЕТОВ (ТЕСТ) ==========
@dp.callback_query(lambda c: c.data and c.data.startswith("answer:"))
async def handle_answer_quiz(call: CallbackQuery):
    await call.answer()
    _, task_id_s, selected = call.data.split(":")
    task_id = int(task_id_s)

    task = await db.get_task(task_id)
    if not task: return

    if await db.has_solved(call.from_user.id, task_id):
        await call.answer("Бұрыннан шешілген.", show_alert=True)
        return

    correct = task["correct_option"].upper()
    next_kb = make_task_result_keyboard(task_id)

    try:
        if selected.upper() == correct:
            await db.mark_solved_and_add_point(call.from_user.id, task_id)
            await call.message.edit_reply_markup(reply_markup=None)
            await call.message.reply(f"✅ Дұрыс! +1 ұпай.", reply_markup=next_kb)
        else:
            await db.mark_attempted(call.from_user.id, task_id)
            await call.message.edit_reply_markup(reply_markup=None)
            await call.message.reply(f"❌ Қате. Дұрыс жауап: {correct}", reply_markup=next_kb)
    except TelegramBadRequest:
        pass


# ========== ОБРАБОТКА ОТВЕТОВ (РУЧНОЙ ВВОД) ==========
@dp.message(StateFilter(UserStates.solving_task))
async def handle_text_answer(message: Message, state: FSMContext):
    if message.text.startswith("/"): return

    data = await state.get_data()
    task_id = data.get("current_task_id")
    if not task_id:
        await state.clear()
        return

    task = await db.get_task(task_id)
    if not task: return

    user_ans = message.text.strip().lower().replace(',', '.')
    correct = task["correct_option"].strip().lower().replace(',', '.')

    next_kb = make_task_result_keyboard(task_id)

    if user_ans == correct:
        await db.mark_solved_and_add_point(message.from_user.id, task_id)
        await message.answer(f"✅ **Дұрыс!** Сіздің жауабыңыз: {message.text}\n+1 ұпай.", reply_markup=next_kb,
                             parse_mode="Markdown")
        await state.clear()
    else:
        await db.mark_attempted(message.from_user.id, task_id)
        await message.answer(f"❌ **Қате.**\nДұрыс жауап: {task['correct_option']}", reply_markup=next_kb,
                             parse_mode="Markdown")
        await state.clear()


@dp.callback_query(lambda c: c.data and c.data.startswith("show_solution:"))
async def handle_solution_request(call: CallbackQuery):
    await call.answer()
    task_id = int(call.data.split(":")[1])
    task = await db.get_task(task_id)

    path = task.get('solution_image_path')
    if not path or not Path(path).exists():
        await call.message.reply("Шешім суреті табылмады.")
        return

    async with aiofiles.open(Path(path), "rb") as f:
        await call.message.reply_photo(
            photo=BufferedInputFile(await f.read(), filename="solution.jpg"),
            caption=f"**📝 Шешімі (ID {task_id})**", parse_mode="Markdown"
        )


# ========== АДМИН: ДОБАВЛЕНИЕ ЗАДАЧИ (ГИБРИД) ==========
@dp.message(Command("addtask"), IsAdminFilter())
async def cmd_addtask(message: Message, state: FSMContext):
    await message.answer("1. Есептің фотосын жіберіңіз.")
    await state.set_state(AddTaskStates.waiting_for_photo)


@dp.message(F.photo, StateFilter(AddTaskStates.waiting_for_photo))
async def handle_photo(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id): return
    await state.update_data(file_id=message.photo[-1].file_id)
    await message.answer("2. Есептің түрін таңдаңыз:", reply_markup=make_task_type_keyboard())
    await state.set_state(AddTaskStates.waiting_for_type)


@dp.callback_query(lambda c: c.data.startswith("type_"), StateFilter(AddTaskStates.waiting_for_type))
async def handle_task_type(call: CallbackQuery, state: FSMContext):
    await call.answer()
    task_type = "quiz" if call.data == "type_quiz" else "text"
    await state.update_data(answer_type=task_type)

    prompt = "Дұрыс әріпті енгізіңіз (A/B/C/D):" if task_type == "quiz" else "Дұрыс жауапты енгізіңіз (сан немесе мәтін):"
    await call.message.edit_text(f"Түрі: {task_type}.\n3. {prompt}")
    await state.set_state(AddTaskStates.waiting_for_correct)


@dp.message(StateFilter(AddTaskStates.waiting_for_correct))
async def process_task_correct(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id): return

    data = await state.get_data()
    task_type = data.get("answer_type")
    text = message.text.strip()

    if task_type == "quiz" and text.upper() not in ("A", "B", "C", "D"):
        await message.answer("Тест үшін бір әріп енгізіңіз: A, B, C немесе D.")
        return

    await state.update_data(correct_option=text.upper() if task_type == "quiz" else text)
    await message.answer("4. Шешімнің фотосын жіберіңіз.")
    await state.set_state(AddTaskStates.waiting_for_solution_photo)


@dp.message(F.photo, StateFilter(AddTaskStates.waiting_for_solution_photo))
async def process_task_solution_final(message: Message, state: FSMContext, bot: Bot):
    if not is_admin(message.from_user.id): return
    data = await state.get_data()

    task_id = await db.add_task(
        image_path="", correct_option=data["correct_option"],
        solution_image_path="", answer_type=data["answer_type"],
        created_by=message.from_user.id
    )

    f_task = IMAGES_DIR / f"task_{task_id}.jpg"
    f_sol = SOLUTIONS_DIR / f"solution_{task_id}.jpg"

    try:
        await bot.download(data["file_id"], destination=f_task)
        await db.update_task_image_path(task_id, str(f_task))
        await bot.download(message.photo[-1].file_id, destination=f_sol)
        await db.update_task_solution_image_path(task_id, str(f_sol))
    except Exception:
        await db.delete_task(task_id)
        await message.answer("Жүктеу кезінде қате шықты.")
        await state.clear()
        return

    await message.answer(
        f"✅ Есеп қосылды!\nID: {task_id}\nТүрі: {data['answer_type']}\nЖауап: {data['correct_option']}")
    await state.clear()


# ========== АДМИНСКИЕ УТИЛИТЫ ==========

@dp.message(Command("stats"), IsAdminFilter())
async def cmd_stats(message: Message):
    stats = await db.get_bot_statistics()
    images_size = await get_dir_size(IMAGES_DIR)
    solutions_size = await get_dir_size(SOLUTIONS_DIR)
    size = round(images_size + solutions_size, 2)
    text = f"📊 **Статистика:**\n👥 Қолданушы: {stats['total_users']}\n🧩 Есептер: {stats['total_tasks']}\n💾 Орын: {size} MB"
    await message.answer(text, parse_mode="Markdown")


@dp.message(Command("send"), IsAdminFilter())
async def cmd_broadcast(message: Message):
    if len(message.text.split()) < 2: return
    users = await db.get_all_users()
    count = 0
    for user in users:
        try:
            await bot.send_message(user['user_id'], message.text.split(maxsplit=1)[1])
            count += 1
            await asyncio.sleep(0.05)
        except:
            pass
    await message.answer(f"Тарату аяқталды: {count} жеткізілді.")


@dp.message(Command("export"), IsAdminFilter())
async def cmd_export(message: Message):
    users = await db.get_all_users()
    file_name = "users_stats.csv"
    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(["ID", "Name", "Username", "Points", "Solved"])
        for u in users: writer.writerow([u['user_id'], u['full_name'], u['username'], u['points'], u['solved_count']])
    await message.answer_document(FSInputFile(file_name))
    try:
        os.remove(file_name)
    except:
        pass


@dp.message(Command("exporttasks"), IsAdminFilter())
async def cmd_export_tasks(message: Message):
    """Есептерді экспорттау (бэкап үшін)"""
    tasks = await db.get_all_tasks_for_export()
    if not tasks:
        await message.answer("Есептер жоқ.")
        return
    
    # Create JSON export
    export_data = {
        "export_version": "1.0",
        "total_tasks": len(tasks),
        "note": "Суреттерді бөлек сақтаңыз! /images/ және /solutions/ қалталарындағы файлдарды көшіріңіз.",
        "tasks": []
    }
    
    for task in tasks:
        export_data["tasks"].append({
            "id": task["id"],
            "correct_option": task["correct_option"],
            "answer_type": task.get("answer_type", "quiz"),
            "image_filename": extract_filename(task["image_path"]),
            "solution_filename": extract_filename(task.get("solution_image_path")),
            "created_at": task.get("created_at"),
            "created_by": task.get("created_by"),
        })
    
    file_name = "tasks_backup.json"
    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, ensure_ascii=False, indent=2)
    
    await message.answer_document(
        FSInputFile(file_name),
        caption=f"📦 Экспорттау аяқталды!\n"
                f"Есептер саны: {len(tasks)}\n\n"
                f"⚠️ Маңызды: Суреттерді бөлек сақтауды ұмытпаңыз!\n"
                f"images/ және solutions/ қалталарындағы файлдарды көшіріңіз."
    )
    try:
        os.remove(file_name)
    except OSError:
        pass


@dp.message(Command("resetweek"), IsAdminFilter())
async def cmd_reset_week(message: Message):
    """Апталық ұпайларды нөлге тастау (админ әмірі)"""
    await message.answer("⏳ Апталық ұпайларды нөлге тастау басталды...")
    try:
        await db.reset_weekly_points()
        await message.answer("✅ Апталық ұпайлар нөлге тасталды! Лигалар жаңартылды.")
    except Exception as e:
        await message.answer(f"❌ Қате: {e}")


@dp.message(Command("alltasks"), IsAdminFilter())
async def cmd_alltasks(message: Message):
    rows = await db.list_tasks(200)
    if not rows: await message.answer("Есептер жоқ.")
    for r in rows:
        await message.answer(f"ID: {r['id']} | Жауап: {r['correct_option']} | Түрі: {r.get('answer_type', 'quiz')}",
                             reply_markup=make_admin_task_keyboard(r['id']))


@dp.callback_query(lambda c: c.data.startswith("delete_task:"), IsAdminFilter())
async def handle_delete(call: CallbackQuery):
    await call.answer()
    tid = int(call.data.split(":")[1])
    t = await db.get_task(tid)
    if t:
        if Path(t["image_path"]).exists(): Path(t["image_path"]).unlink(missing_ok=True)
        if t["solution_image_path"] and Path(t["solution_image_path"]).exists(): Path(t["solution_image_path"]).unlink(
            missing_ok=True)
        await db.delete_task(tid)
        try:
            await call.message.edit_text(f"✅ ID {tid} жойылды.")
        except:
            pass


@dp.message(Command("edit"), IsAdminFilter())
async def cmd_edit(message: Message, state: FSMContext):
    try:
        tid = int(message.text.split()[1])
    except:
        await message.answer("/edit ID")
        return
    t = await db.get_task(tid)
    if not t: return
    async with aiofiles.open(t["image_path"], "rb") as f:
        await message.answer_photo(BufferedInputFile(await f.read(), "t.jpg"),
                                   caption=f"ID: {tid}\nОтвет: {t['correct_option']}",
                                   reply_markup=make_edit_options_keyboard(tid))
    await state.update_data(task_id_to_edit=tid)
    await state.set_state(EditTaskStates.waiting_for_action)


@dp.callback_query(lambda c: c.data.startswith("edit_action:"), StateFilter(EditTaskStates.waiting_for_action))
async def edit_action(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id): return
    act = call.data.split(":")[2]
    await state.update_data(action_type=act)
    msg = "Жаңа жауап:" if act == "answer" else "Жаңа фото:"
    await call.message.edit_caption(caption=msg)
    await state.set_state(EditTaskStates.waiting_for_new_data)


@dp.message(StateFilter(EditTaskStates.waiting_for_new_data))
async def edit_data(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id): return
    d = await state.get_data()
    tid, act = d["task_id_to_edit"], d["action_type"]

    if act == "answer":
        await db.update_task_correct_option(tid, message.text.strip())
    elif act == "task_photo" and message.photo:
        path = IMAGES_DIR / f"task_{tid}.jpg"
        await bot.download(message.photo[-1].file_id, path)
        await db.update_task_image_path_only(tid, str(path))
    elif act == "solution_photo" and message.photo:
        path = SOLUTIONS_DIR / f"solution_{tid}.jpg"
        await bot.download(message.photo[-1].file_id, path)
        await db.update_task_solution_image_path(tid, str(path))

    await message.answer("✅ Жаңартылды.")
    await state.clear()


# ========== START ==========

# === Одновременный запуск aiogram и FastAPI ===

async def start_fastapi():
    port = int(os.getenv("PORT", 8000))
    config = uvicorn.Config(app, host="0.0.0.0", port=port, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


async def weekly_reset_task():
    """Апталық ұпайларды нөлге тастау (жексенбі сайын)"""
    import datetime
    while True:
        now = datetime.datetime.now()
        # Келесі жексенбі 00:00
        days_until_sunday = (6 - now.weekday()) % 7 or 7
        next_sunday = now + datetime.timedelta(days=days_until_sunday)
        next_sunday = next_sunday.replace(hour=0, minute=0, second=0, microsecond=0)
        
        wait_seconds = (next_sunday - now).total_seconds()
        print(f"Next weekly reset: {next_sunday} (in {wait_seconds/3600:.1f} hours)")
        
        await asyncio.sleep(wait_seconds)
        
        print("Resetting weekly points and updating leagues...")
        try:
            await db.reset_weekly_points()
            print("Weekly reset completed successfully!")
        except Exception as e:
            print(f"Error during weekly reset: {e}")


async def main():
    await db.init_db()
    dp.message.middleware(RegisterUserMiddleware())
    dp.callback_query.middleware(RegisterUserMiddleware())
    print("Bot and API started...")

    fastapi_task = asyncio.create_task(start_fastapi())
    weekly_task = asyncio.create_task(weekly_reset_task())
    polling_task = asyncio.create_task(dp.start_polling(bot))
    
    # Run all tasks concurrently
    await asyncio.gather(fastapi_task, weekly_task, polling_task)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass