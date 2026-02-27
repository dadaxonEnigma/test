# 🚀 Полный Деплой (Веб + Бот на Railway)

Инструкция по развертыванию веб-сайта И Telegram бота на одном хостинге!

## ✨ Что будет работать:

✅ **Веб-сайт:** http://твой-сайт.railway.app (24/7)
✅ **Telegram бот:** работает в Telegram (24/7)
✅ **Оба используют одни и те же тесты** из папки `data/`

## 📋 Что нужно подготовить:

- ✅ GitHub аккаунт (бесплатно)
- ✅ Railway аккаунт (бесплатно)
- ✅ Файлы в папке:
  - `app.py` - веб приложение
  - `telegram_bot.py` - бот
  - `templates/index.html` - интерфейс
  - `requirements.txt` - зависимости
  - `Procfile` - инструкции для Railway
  - `runtime.txt` - версия Python
  - папка `data/` с тестами

## 🎯 Шаг 1: Подготовить GitHub

### 1️⃣ Создать репозиторий

1. Перейди: https://github.com/new
2. Назови: `test-bot-app`
3. Выбери "Public"
4. Нажми "Create repository"

### 2️⃣ Загрузить код

**Способ A - GitHub Desktop (проще):**

1. Скачай: https://desktop.github.com
2. Установи и авторизуйся
3. Нажми "File" → "Clone repository"
4. Выбери свой репо `test-bot-app`
5. Выбери папку `c:\Users\User\Desktop\azot`
6. Скопируй ВСЕ файлы из `azot` в папку репо
7. В GitHub Desktop:
   - Нажми "Commit to main"
   - Напиши сообщение: "Initial commit"
   - Нажми "Push origin"

**Способ B - Команда (если GitHub Desktop не нравится):**

```bash
cd C:\Users\User\Desktop\azot
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/ТВО_USERNAME/test-bot-app.git
git push -u origin main
```

(Замени `ТВО_USERNAME` на свой username GitHub)

## 🌐 Шаг 2: Развернуть на Railway

### 1️⃣ Создать проект на Railway

1. Перейди: https://railway.app
2. Нажми "Sign up"
3. Выбери "Sign up with GitHub"
4. Авторизуйся
5. Нажми "New Project"
6. Выбери "Deploy from GitHub repo"
7. Найди репо `test-bot-app`
8. Нажми "Deploy"

**Railway начнет разворачивать автоматически!**

### 2️⃣ Подождать развертывания

- Посмотри логи в Railway
- Статус должен быть "Running" (зелёный)
- Это займет 2-5 минут

### 3️⃣ Получить URL веб-сайта

На странице Railway:
1. Нажми на "web" процесс (иконка с браузером)
2. Копируй URL вроде: `https://test-bot-app-production.up.railway.app`
3. Открой в браузере - готово! 🎉

## 🤖 Шаг 3: Запустить Telegram бота

Railway позволяет запускать несколько процессов. В Procfile указано:

```
web: python app.py      ← веб-сайт
worker: python telegram_bot.py  ← Telegram бот
```

### Активировать worker процесс:

1. На странице Railway нажми "Add service"
2. Нажми "Create new"
3. Назови: `telegram-bot-worker`
4. В "Start command" напиши: `python telegram_bot.py`
5. Нажми "Create"

**Готово! Оба процесса работают одновременно!**

## 📊 Мониторинг на Railway

На странице Railway видишь:

```
Services:
├── web (Flask сайт)
│   ├── Status: Running ✅
│   ├── URL: https://test-bot-app-production.up.railway.app
│   └── Logs: просмотр логов
│
└── worker (Telegram бот)
    ├── Status: Running ✅
    └── Logs: просмотр логов
```

## ✅ Проверить что всё работает

### Веб-сайт:
1. Открой Railway URL
2. Выбери тест
3. Отвечай на вопросы

### Telegram бот:
1. Найди бота в Telegram (по username)
2. Отправь `/start`
3. Выбери тест
4. Работает! 🎉

## 💾 Обновить код

Когда захочешь изменить код:

```bash
cd C:\Users\User\Desktop\azot

# Отредактируй файлы в редакторе

# Загрузи на GitHub:
git add .
git commit -m "Описание изменений"
git push
```

Railway автоматически перезагрузит оба процесса!

## 🐛 Решение проблем

### Веб-сайт не открывается
- Посмотри логи web процесса на Railway
- Убедись что Procfile содержит: `web: python app.py`
- Перезагрузи процесс в Railway

### Бот не работает
- Посмотри логи worker процесса
- Убедись что TOKEN правильный в telegram_bot.py
- Проверь что worker процесс запущен (Status: Running)

### Тесты не загружаются
- Убедись что папка `data/` в GitHub репо
- В папке должны быть .txt файлы
- Нажми "Redeploy" в Railway

### Ошибка "worker процесс не запускается"
- Railway может требовать платный план для нескольких процессов
- Или запусти бота отдельно (смотри DEPLOY_24_7.md)

## 💡 Советы

- **Локальное тестирование:**
  ```bash
  python app.py
  # Отдельная вкладка:
  python telegram_bot.py
  ```

- **Добавить новые тесты:**
  1. Добавь .txt файл в папку `data/`
  2. Загрузи на GitHub (git push)
  3. Railway автоматически перезагрузится

- **Настроить бота:**
  - TOKEN хардкодирован в telegram_bot.py
  - Если нужно изменить - отредактируй и push

## 📞 Быстрая помощь

```bash
# Проверить файлы
ls -la          # Windows: dir

# Проверить Git статус
git status

# Просмотреть логи локально
python app.py   # Веб
python telegram_bot.py  # Бот

# Отменить последний коммит
git reset --soft HEAD~1
```

## 🎉 Результат

После деплоя у тебя есть:

```
Telegram Bot (@test_bot):
- /start → выбор теста
- Два режима: подсказка и экзамен
- Работает 24/7

Веб-сайт (railway.app):
- Красивый интерфейс
- Та же логика что бот
- Мобильный дизайн
- Работает 24/7
```

## 🚀 Готово!

Оба приложения работают одновременно, используют одни тесты, развернуты на бесплатном хостинге Railway!

---

**Нужна помощь?**
- Railway docs: https://docs.railway.app
- GitHub docs: https://docs.github.com
- Telegram Bot API: https://core.telegram.org/bots/api
