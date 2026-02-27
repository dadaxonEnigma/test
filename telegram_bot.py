#!/usr/bin/env python3
import os
from pathlib import Path
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Configuration
DATA_DIR = Path(__file__).parent / "data"
TESTS = {}
USER_STATE = {}

class TestParser:
    @staticmethod
    def parse_test(content):
        """Parse test file content into questions and answers"""
        lines = content.split('\n')
        questions = []
        current_question = None

        for line in lines:
            line = line.strip()
            if not line:
                if current_question and current_question['options']:
                    questions.append(current_question)
                    current_question = None
                continue

            if not current_question:
                current_question = {
                    'text': line,
                    'options': [],
                    'correct': -1
                }
            else:
                is_correct = line.startswith('*')
                text = line[1:].strip() if is_correct else line

                if text:
                    if is_correct:
                        current_question['correct'] = len(current_question['options'])
                    current_question['options'].append(text)

        if current_question and current_question['options']:
            questions.append(current_question)

        return questions

    @staticmethod
    def load_tests():
        """Load all test files from data directory"""
        tests = {}
        if not DATA_DIR.exists():
            return tests

        for file_path in DATA_DIR.glob("*.txt"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    test_data = TestParser.parse_test(content)
                    if test_data:
                        tests[file_path.stem] = test_data
            except Exception as e:
                print(f"Ошибка загрузки {file_path}: {e}")

        return tests

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command - show test selection"""
    global TESTS
    if not TESTS:
        await update.message.reply_text(
            "❌ Тесты не найдены!\n"
            "Пожалуйста проверьте папку 'data' и убедитесь что там есть .txt файлы с тестами."
        )
        return

    keyboard = [
        [InlineKeyboardButton(f"📚 {name} ({len(tests)} вопросов)", callback_data=f"test_{name}")]
        for name, tests in sorted(TESTS.items())
    ]
    keyboard.append([InlineKeyboardButton("🔄 Обновить", callback_data="refresh")])

    await update.message.reply_text(
        "👋 Привет! Добро пожаловать в тест-бот!\n\n"
        "📚 Выбери тест:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show help message"""
    await update.message.reply_text(
        "📚 <b>Тест обучающий бот</b>\n\n"
        "/start - Главное меню\n"
        "/help - Эта справка\n\n"
        "<b>Как это работает:</b>\n"
        "1. /start выбери тест\n"
        "2. Выбери режим (с подсказкой или экзамен)\n"
        "3. Отвечай на вопросы\n"
        "4. В конце увидишь результат\n\n"
        "<b>Два режима:</b>\n"
        "📚 <b>С подсказкой</b> - видишь правильный ответ (✅)\n"
        "📝 <b>Экзамен</b> - ответы скрыты, показываем если ошибка",
        parse_mode="HTML"
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button presses"""
    global TESTS
    query = update.callback_query
    await query.answer()

    data = query.data
    user_id = query.from_user.id

    # Test selection - show mode selection
    if data.startswith("test_"):
        test_name = data[5:]
        if test_name not in TESTS:
            await query.edit_message_text("❌ Тест не найден!")
            return

        keyboard = [
            [InlineKeyboardButton("📚 С подсказкой", callback_data=f"mode_hint_{test_name}")],
            [InlineKeyboardButton("📝 Экзамен", callback_data=f"mode_exam_{test_name}")],
            [InlineKeyboardButton("← Назад", callback_data="back_to_tests")]
        ]

        await query.edit_message_text(
            f"<b>Выбери режим:</b>\n{test_name}\n\n"
            f"📚 <b>С подсказкой</b> - видишь правильный ответ\n"
            f"📝 <b>Экзамен</b> - ответы скрыты, показываем если ошибка",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML"
        )

    # Mode selection
    elif data.startswith("mode_hint_"):
        test_name = data[10:]
        await init_test(query, user_id, test_name, mode='hint')

    elif data.startswith("mode_exam_"):
        test_name = data[10:]
        await init_test(query, user_id, test_name, mode='exam')

    # Answer selection
    elif data.startswith("answer_"):
        if user_id not in USER_STATE:
            await query.edit_message_text("❌ Сессия истекла. Отправь /start")
            return

        answer_idx = int(data.split("_")[1])
        await show_answer_result(query, user_id, answer_idx)

    # Restart test
    elif data == "restart":
        if user_id in USER_STATE:
            state = USER_STATE[user_id]
            test_name = state['test_name']
            mode = state['mode']
            await init_test(query, user_id, test_name, mode=mode)

    # Back to menu
    elif data == "back_to_tests":
        if user_id in USER_STATE:
            del USER_STATE[user_id]
        keyboard = [
            [InlineKeyboardButton(f"📚 {name} ({len(tests)} вопросов)", callback_data=f"test_{name}")]
            for name, tests in sorted(TESTS.items())
        ]
        keyboard.append([InlineKeyboardButton("🔄 Обновить", callback_data="refresh")])
        await query.edit_message_text(
            "📚 Выбери тест:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # Refresh tests
    elif data == "refresh":
        TESTS = TestParser.load_tests()
        keyboard = [
            [InlineKeyboardButton(f"📚 {name} ({len(tests)} вопросов)", callback_data=f"test_{name}")]
            for name, tests in sorted(TESTS.items())
        ]
        keyboard.append([InlineKeyboardButton("🔄 Обновить", callback_data="refresh")])
        await query.edit_message_text(
            "✅ Тесты обновлены!\n\n📚 Выбери тест:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

async def init_test(query, user_id, test_name, mode):
    """Initialize test with selected mode"""
    global TESTS

    USER_STATE[user_id] = {
        'test_name': test_name,
        'mode': mode,
        'current_question': 0,
        'answers': [],
        'questions': TESTS[test_name]
    }

    await show_question(query, user_id)

async def show_question(query, user_id):
    """Display current question"""
    state = USER_STATE[user_id]
    question_idx = state['current_question']
    questions = state['questions']
    question = questions[question_idx]
    mode = state['mode']

    # Progress
    progress = f"Вопрос {question_idx + 1}/{len(questions)}"

    # Create answer buttons with full text
    keyboard = []
    for i, opt in enumerate(question['options']):
        prefix = f"{'✅ ' if mode == 'hint' and i == question['correct'] else ''}"

        btn = InlineKeyboardButton(
            f"{prefix}{opt}",
            callback_data=f"answer_{i}"
        )
        keyboard.append([btn])

    hint_text = "\n<i>✅ = Правильный ответ</i>" if mode == 'hint' else ""

    text = (
        f"<b>{progress}</b>\n\n"
        f"<b>❓ {question['text']}</b>\n{hint_text}\n"
        f"Выбери ответ:"
    )

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )

async def show_answer_result(query, user_id, selected_answer):
    """Save answer and move to next question"""
    state = USER_STATE[user_id]
    question = state['questions'][state['current_question']]
    mode = state['mode']

    # Save answer
    is_correct = selected_answer == question['correct']
    state['answers'].append({
        'selected': selected_answer,
        'correct': question['correct'],
        'is_correct': is_correct
    })

    # For exam mode, show correct answer if wrong
    if mode == 'exam' and not is_correct:
        correct_option = question['options'][question['correct']]
        selected_option = question['options'][selected_answer]

        text = (
            f"❌ <b>Неправильно!</b>\n\n"
            f"<b>Ты выбрал:</b>\n{selected_option}\n\n"
            f"<b>Правильный ответ:</b>\n{correct_option}"
        )

        keyboard = [[InlineKeyboardButton("➡️ Дальше", callback_data="next_question")]]

        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML"
        )
        return

    # For hint mode or correct answer, move to next immediately
    await move_to_next(query, user_id)

async def move_to_next(query, user_id):
    """Move to next question or show results"""
    state = USER_STATE[user_id]
    state['current_question'] += 1

    if state['current_question'] < len(state['questions']):
        await show_question(query, user_id)
    else:
        await show_results(query, user_id)

async def button_callback_next(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle next question button (for exam mode)"""
    query = update.callback_query
    await query.answer()

    if query.data == "next_question":
        user_id = query.from_user.id
        if user_id in USER_STATE:
            await move_to_next(query, user_id)

async def show_results(query, user_id):
    """Show test results"""
    state = USER_STATE[user_id]
    answers = state['answers']

    # Count correct answers
    correct_count = sum(1 for ans in answers if ans['is_correct'])
    total_count = len(answers)
    percentage = (correct_count / total_count * 100) if total_count > 0 else 0

    # Message based on score
    if percentage == 100:
        emoji = "🎉"
        message = "Отлично! Все правильно!"
    elif percentage >= 80:
        emoji = "👏"
        message = "Хорошо работаешь!"
    elif percentage >= 60:
        emoji = "📚"
        message = "Продолжай учиться!"
    else:
        emoji = "💪"
        message = "Повтори ошибки!"

    text = (
        f"{emoji} <b>{message}</b>\n\n"
        f"<b>Результаты:</b>\n"
        f"🎯 <b>{percentage:.0f}%</b>\n"
        f"✅ Правильно: {correct_count}/{total_count}\n"
    )

    keyboard = [
        [InlineKeyboardButton("🔄 Повторить", callback_data="restart")],
        [InlineKeyboardButton("📚 Другой тест", callback_data="back_to_tests")]
    ]

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )

def main():
    """Start the bot"""
    global TESTS

    # Load tests
    TESTS = TestParser.load_tests()

    if not TESTS:
        print("⚠️  Тесты не найдены! Пожалуйста проверьте папку 'data'")
        return

    print(f"✅ Загружено {len(TESTS)} тестов:")
    for name, tests in TESTS.items():
        print(f"   - {name}: {len(tests)} вопросов")

    # Get token
    TOKEN = "8633297005:AAGKa3jK6hyg1gM6D1G2TfYVUknLWUZPBbY"

    # Create application
    application = Application.builder().token(TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(button_callback_next, pattern="next_question"))
    application.add_handler(CallbackQueryHandler(button_callback))

    # Start bot
    print("🤖 Бот запущен!")
    print("Бот работает. Нажмите Ctrl+C для остановки.")
    application.run_polling()

if __name__ == '__main__':
    main()
