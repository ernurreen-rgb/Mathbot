# EsepBot Web Platform

Қазақстандық олимпиадалық математика платформасының веб-нұсқасы.

## Орнату және іске қосу

### 1. Bot серверін іске қосу

Веб-сайт жұмыс істеуі үшін bot сервері іске қосылуы керек:

```bash
cd bot
pip install -r requirements.txt
python main.py
```

Bot сервері `http://localhost:8000` портында іске қосылады.

### 2. Веб-сайтты іске қосу

Басқа терминалда:

```bash
cd web
npm install
npm run dev
```

Веб-сайт `http://localhost:3000` портында іске қосылады.

## API Endpoints

Bot сервері келесі API endpoints қамтамасыз етеді:

- `GET /api/task/random` - Кездейсоқ есеп алу
- `POST /api/task/check` - Жауапты тексеру
- `GET /api/rating?limit=20` - Рейтинг алу
- `GET /api/user/{user_id}` - Қолданушы статистикасын алу
- `GET /images/{filename}` - Есеп суреттерін көрсету
- `GET /solutions/{filename}` - Шешім суреттерін көрсету

## Environment Variables

Веб-сайт үшін `.env.local` файлын құрыңыз:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Production үшін:

```bash
NEXT_PUBLIC_API_URL=https://your-bot-server.com
```

## Deployment

### Vercel (Web)

1. Vercel-ге веб қалтасын deploy жасаңыз
2. Environment Variable қосыңыз: `NEXT_PUBLIC_API_URL=https://your-bot-server.com`

### Bot Server

Bot серверді кез келген хостингке deploy жасауға болады (Railway, Render, VPS және т.б.)

## Функционалдық

- ✅ Есептерді шешу (Quiz және қолмен енгізу)
- ✅ Рейтинг көрсету
- ✅ Жауаптарды тексеру
- ✅ Шешімдерді көрсету
- 🔄 Профиль (болашақта)
- 🔄 Telegram login (болашақта)
