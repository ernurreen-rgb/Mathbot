
import asyncio
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
from fastapi import FastAPI, HTTPException
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
    
    # Update progress for web users
    if submission.email:
        # Ensure web user exists (use email as name if not provided separately)
        await db.ensure_web_user(submission.email, submission.email, "")
        
        if is_correct:
            # Check if already solved
            if not await db.has_web_solved(submission.email, submission.task_id):
                await db.mark_web_solved_and_add_point(submission.email, submission.task_id)
        else:
            await db.mark_web_attempted(submission.email, submission.task_id)
    
    return {
        "correct": is_correct,
        "correct_answer": task["correct_option"] if not is_correct else None,
        "solution_image_path": convert_to_relative_path(task.get("solution_image_path"), "/solutions")
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


def get_dir_size(path: Path) -> float:
    total_size = 0
    try:
        for dirpath, dirnames, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if not os.path.islink(fp): total_size += os.path.getsize(fp)
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
        keyboard=[[KeyboardButton(text="/task")], [KeyboardButton(text="/profile"), KeyboardButton(text="/rating")]],
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
    await message.answer(f"👤 {name}\n💎 Ұпай: {stats['points']}\n🧩 Шешілгені: {stats['solved_count']}")


@dp.message(Command("rating"))
async def cmd_rating(message: Message):
    top = await db.get_top_users(10)
    lines = ["🏆 **Үздік қолданушылар:**"]
    for i, r in enumerate(top, 1):
        # Handle both Telegram and web users
        if r["source"] == "web":
            name = r["nickname"] or r["name"] or r["email"] or "Web User"
        else:
            name = r["username"] or r["full_name"] or str(r["user_id"])
        lines.append(f"{i}. {name} — {r['points']}")
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
    size = round(get_dir_size(IMAGES_DIR) + get_dir_size(SOLUTIONS_DIR), 2)
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

async def main():
    await db.init_db()
    dp.message.middleware(RegisterUserMiddleware())
    dp.callback_query.middleware(RegisterUserMiddleware())
    print("Bot and API started...")

    fastapi_task = asyncio.create_task(start_fastapi())
    await dp.start_polling(bot)
    await fastapi_task

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass