# Промпт для генерации копии Mathbot

## Как использовать
1. Скопируйте текст из блока «Готовый промпт» целиком и передайте его другому ИИ (например, в System или Developer prompt).
2. Попросите ИИ сгенерировать репозиторий в том же формате: файлы, папки, README и конфигурации должны совпадать с описанием.
3. После генерации убедитесь, что структура и инструкции соответствуют ожиданиям (бот, API, веб-приложение, render.yaml, лицензия).

## Готовый промпт
```
Ты — Senior fullstack инженер. Твоя задача — воссоздать открытый проект Mathbot, Telegram-бот с веб-интерфейсом для математических задач, сохраняя структуру и функциональность как в исходном репозитории.

Общее требование:
- Создай полноценный репозиторий с двумя сервисами: Python бот/API и Next.js веб-приложение. Добавь README и вспомогательные инструкции (DEPLOYMENT.md, DEPLOYMENT_RU.md, QUICKSTART.md) и раздел о лицензии MIT (как в README; LICENSE-файл добавь при необходимости).

Технологии:
- Backend: Python 3.11+, aiogram 3.0.0b7, FastAPI 0.109.x, uvicorn[standard] 0.27.x, aiosqlite 0.19.x, aiofiles 23.1.x, pydantic 1.10.x, python-multipart 0.0.6, aiohttp 3.8.x–<4.
- Frontend: Next.js 14 (App Router), React 18.3.x, TailwindCSS 3.4.x, NextAuth 4.24.x, KaTeX, mathlive, react-katex, TypeScript 5.6.x.

Структура каталогов (корень):
- bot/ — Telegram бот + FastAPI API. Основной файл main.py, database.py для aiosqlite, requirements.txt с указанными версиями, директории images/ (задачи) и solutions/ (решения).
- web/ — Next.js приложение (app router). package.json со скриптами dev/build/start, зависимости как выше. Использует Tailwind для стилизации и KaTeX для формул.
- render.yaml — Blueprint для Render, создающий два сервиса: mathbot-api (Python) и mathbot-web (Next.js).
- Документация: README.md (особенности, быстрый старт, env), DEPLOYMENT.md (EN), DEPLOYMENT_RU.md (RU), QUICKSTART.md (Render за 5 минут), AI_SOLUTION_FEATURE.md, DUOLINGO_LEAGUE_SYSTEM.md. .gitignore для Python/Node артефактов.

Функциональность бота/сервера:
- Команды: /start, /task (случайная задача), /profile, /league, /rating, /addtask, /alltasks, /edit {id}, /resetweek, /stats, /send {message}, /export.
- Лигалық система как в Duolingo: 5 лиг (Қола, Күміс, Алтын, Платина, Алмас), мини-группы 30–50 пользователей, еженедельные сбросы; топ 7 повышается, последние 5 понижаются.
- Поддержка задач в текстовом формате с LaTeX + опциональные изображения; автоматический рендер формул KaTeX.
- API эндпоинты (FastAPI):
  - GET /api/task/random?email=... — случайная задача
  - POST /api/task/check — проверить ответ
  - GET /api/rating?limit=10 — рейтинг
  - GET /api/user/web/{email} — статистика пользователя
  - POST /api/user/web/nickname — обновить никнейм
  - GET /images/{filename} и /solutions/{filename} — файлы
  - Админ AI endpoints: POST /api/admin/tasks/{task_id}/ai-solution, /retry, /approve, /reject; GET /api/admin/tasks/{task_id}/ai-solution
- База данных: aiosqlite, модели и миграции хранят задачи, пользователей, лиги и результаты.

Веб-приложение:
- Next.js 14 App Router, страницы: главная с кнопкой «Get Random Task», админ-панель /admin для добавления задач с LaTeX/текстом и изображениями.
- Аутентификация: NextAuth, Google OAuth опционально. Отрисовка формул KaTeX, ввод формул через mathlive.

Переменные окружения:
- Для bot/API: BOT_TOKEN, PORT=8000, OPENAI_API_KEY (опционально для AI решений), OPENAI_MODEL (по умолчанию gpt-4o-mini).
- Для web: NEXT_PUBLIC_API_URL, NEXTAUTH_URL, NEXTAUTH_SECRET, GOOGLE_CLIENT_ID/GOOGLE_CLIENT_SECRET (опционально).

Скрипты и запуск:
- bot: pip install -r requirements.txt; экспортируй BOT_TOKEN; python main.py (FastAPI + aiogram бот).
- web: npm install; создать .env.local с NEXT_PUBLIC_API_URL, NEXTAUTH_URL, NEXTAUTH_SECRET; npm run dev/build/start.

Деплой:
- Поддержи render.yaml Blueprint, который запускает два сервиса на Render; опиши шаги добавления переменных окружения.

Результат:
- Полный репозиторий с рабочим кодом, указанной структурой, документацией и указанием лицензии MIT (LICENSE-файл добавь при необходимости). Код должен быть самодостаточным без placeholder-файлов.
```
