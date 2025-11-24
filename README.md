# Mathbot - Telegram Bot для математических олимпиад

Платформа для решения математических задач с Telegram ботом и веб-интерфейсом.

## 🌟 Особенности

- 🤖 Telegram бот для решения задач
- 🌐 Веб-интерфейс (Next.js)
- 📊 Система рейтинга
- ✅ Проверка ответов (тесты и ручной ввод)
- 🔐 Google OAuth авторизация
- 📝 Просмотр решений задач

## 🚀 Быстрый старт

### Получение Telegram Bot Token

Перед началом вам нужен токен от [@BotFather](https://t.me/botfather):
1. Напишите `/newbot` в [@BotFather](https://t.me/botfather)
2. Следуйте инструкциям для создания бота
3. Скопируйте полученный токен

### Локальная разработка

1. **Установите зависимости для бота:**
```bash
cd bot
pip install -r requirements.txt
```

2. **Запустите бот/API сервер:**
```bash
cd bot
export BOT_TOKEN="your_telegram_bot_token"
python main.py
```

3. **В отдельном терминале установите зависимости для веб:**
```bash
cd web
npm install
```

4. **Создайте файл `web/.env.local`:**
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-secret-key
```

5. **Запустите веб-сервер:**
```bash
cd web
npm run dev
```

Откройте http://localhost:3000 в браузере.

## 🌍 Деплой на Render

Проект готов к деплою на [Render.com](https://render.com) одним кликом!

### Быстрый деплой

1. Форкните этот репозиторий
2. Зарегистрируйтесь на [Render.com](https://render.com)
3. Создайте новый Blueprint из вашего репозитория
4. Render автоматически обнаружит `render.yaml` и создаст оба сервиса
5. Добавьте переменные окружения (BOT_TOKEN и другие)

📖 **Подробная инструкция**: См. [DEPLOYMENT.md](./DEPLOYMENT.md)

## 📁 Структура проекта

```
Mathbot/
├── bot/                    # Python Telegram бот + FastAPI API
│   ├── main.py            # Основной файл бота
│   ├── database.py        # Работа с БД
│   ├── requirements.txt   # Python зависимости
│   ├── images/           # Изображения задач
│   └── solutions/        # Изображения решений
├── web/                   # Next.js веб-приложение
│   ├── app/              # Next.js App Router
│   ├── components/       # React компоненты
│   └── package.json      # Node.js зависимости
├── render.yaml           # Конфигурация Render
├── DEPLOYMENT.md         # Инструкции по деплою
└── .env.example         # Пример переменных окружения
```

## 🔧 API Endpoints

Bot/API сервис предоставляет следующие endpoints:

- `GET /api/task/random?email=user@example.com` - Получить случайную задачу
- `POST /api/task/check` - Проверить ответ
- `GET /api/rating?limit=10` - Получить рейтинг
- `GET /api/user/web/{email}` - Статистика пользователя
- `POST /api/user/web/nickname` - Обновить никнейм
- `GET /images/{filename}` - Изображения задач
- `GET /solutions/{filename}` - Изображения решений

## 🔐 Переменные окружения

### Bot/API Service

```env
BOT_TOKEN=your_telegram_bot_token
PORT=8000
```

### Web Service

```env
NEXT_PUBLIC_API_URL=https://your-api-url.onrender.com
NEXTAUTH_URL=https://your-web-url.onrender.com
NEXTAUTH_SECRET=generate-with-openssl-rand-base64-32
GOOGLE_CLIENT_ID=optional-for-oauth
GOOGLE_CLIENT_SECRET=optional-for-oauth
```

## 🛠 Технологии

- **Backend**: Python 3.11, aiogram 3.0, FastAPI, aiosqlite
- **Frontend**: Next.js 14, React 18, TailwindCSS, NextAuth
- **Deployment**: Render.com (с поддержкой Blueprint)

## 📝 Команды Telegram бота

- `/start` - Начать работу с ботом
- `/task` - Получить новую задачу
- `/profile` - Ваша статистика
- `/rating` - Топ пользователей

### Админские команды

- `/addtask` - Добавить новую задачу
- `/alltasks` - Список всех задач
- `/edit {id}` - Редактировать задачу
- `/stats` - Статистика бота
- `/send {message}` - Рассылка сообщения
- `/export` - Экспорт данных

## 🤝 Вклад

Приветствуются Pull Requests и Issues!

## 📄 Лицензия

MIT License

## 🙋‍♂️ Поддержка

Если у вас возникли вопросы:
- Откройте Issue в этом репозитории
- См. [DEPLOYMENT.md](./DEPLOYMENT.md) для инструкций по деплою
- Проверьте [документацию Render](https://render.com/docs)
