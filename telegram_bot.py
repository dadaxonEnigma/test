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
                print(f"Error loading {file_path}: {e}")

        return tests

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command - show test selection"""
    global TESTS
    if not TESTS:
        await update.message.reply_text(
            "❌ Тестлар топилмади!\n"
            "Пожалуйста проверьте папку 'data' и убедитесь что там есть .txt файлы с тестами."
        )
        return

    keyboard = [
        [InlineKeyboardButton(f"📚 {name} ({len(tests)} сўрав)", callback_data=f"test_{name}")]
        for name, tests in sorted(TESTS.items())
    ]
    keyboard.append([InlineKeyboardButton("🔄 Обновить", callback_data="refresh")])

    await update.message.reply_text(
        "👋 Салом! Тест ўқув ўйинига хўш келибсиз!\n\n"
        "📚 Тестни танлаңиз:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show help message"""
    await update.message.reply_text(
        "📚 <b>Тест ўқув ўйини</b>\n\n"
        "/start - Асосий меню\n"
        "/help - Бу маълумот\n\n"
        "<b>Қондай ишлаташ:</b>\n"
        "1. /start браузерни танлаңиз\n"
        "2. Har bir savollarga javob beringiz\n"
        "3. Охирида натижалари кўринади\n\n"
        "🎨 <b>Рангни маъноси:</b>\n"
        "🟦 Сизнинг жавобингиз\n"
        "🟩 Тўғри жавоб\n"
        "🟥 Нотўғри жавоб",
        parse_mode="HTML"
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button presses"""
    global TESTS
    query = update.callback_query
    await query.answer()

    data = query.data
    user_id = query.from_user.id

    # Test selection
    if data.startswith("test_"):
        test_name = data[5:]
        if test_name not in TESTS:
            await query.edit_message_text("❌ Тест топилмади!")
            return

        # Initialize user state
        USER_STATE[user_id] = {
            'test_name': test_name,
            'current_question': 0,
            'answers': [],
            'questions': TESTS[test_name]
        }

        await show_question(query, user_id)

    # Answer selection
    elif data.startswith("answer_"):
        if user_id not in USER_STATE:
            await query.edit_message_text("❌ Сессия истека. /start браузерни яна басинг")
            return

        answer_idx = int(data.split("_")[1])

        # Move to next question
        await show_answer_result(query, user_id, answer_idx)

    # Restart test
    elif data == "restart":
        if user_id in USER_STATE:
            state = USER_STATE[user_id]
            test_name = state['test_name']
            USER_STATE[user_id] = {
                'test_name': test_name,
                'current_question': 0,
                'answers': [],
                'questions': TESTS[test_name]
            }
            await show_question(query, user_id)

    # Go to menu
    elif data == "menu":
        if user_id in USER_STATE:
            del USER_STATE[user_id]
        await query.edit_message_text(
            "👋 Салом! Тест ўқув ўйинига хўш келибсиз!\n\n"
            "📚 Тестни танлаңиз:",
            reply_markup=await get_test_menu_keyboard()
        )

    # Refresh tests
    elif data == "refresh":
        TESTS = TestParser.load_tests()
        await query.edit_message_text(
            "✅ Тестлар янгиланди!\n\n📚 Тестни танлаңиз:",
            reply_markup=await get_test_menu_keyboard()
        )

async def get_test_menu_keyboard():
    """Get keyboard with test selection"""
    global TESTS
    keyboard = [
        [InlineKeyboardButton(f"📚 {name} ({len(tests)} сўрав)", callback_data=f"test_{name}")]
        for name, tests in sorted(TESTS.items())
    ]
    keyboard.append([InlineKeyboardButton("🔄 Обновить", callback_data="refresh")])
    return InlineKeyboardMarkup(keyboard)

async def show_question(query, user_id):
    """Display current question"""
    state = USER_STATE[user_id]
    question_idx = state['current_question']
    questions = state['questions']
    question = questions[question_idx]

    # Progress
    progress = f"Сўрав {question_idx + 1}/{len(questions)}"

    # Create answer buttons - mark correct answer with ✅
    keyboard = [
        [InlineKeyboardButton(
            f"{'✅ ' if i == question['correct'] else '   '}{opt}",
            callback_data=f"answer_{i}"
        )]
        for i, opt in enumerate(question['options'])
    ]

    text = (
        f"<b>{progress}</b>\n\n"
        f"<b>❓ {question['text']}</b>\n\n"
        f"<i>✅ = Тўғри жавоб</i>\n"
        f"Жавобни танлаңиз:"
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

    # Save answer
    is_correct = selected_answer == question['correct']
    state['answers'].append({
        'selected': selected_answer,
        'correct': question['correct'],
        'is_correct': is_correct
    })

    # Move to next question
    state['current_question'] += 1

    if state['current_question'] < len(state['questions']):
        await show_question(query, user_id)
    else:
        await show_results(query, user_id)

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
        message = "Шамоллиқ! Барчаси тўғри!"
    elif percentage >= 80:
        emoji = "👏"
        message = "Яхши ишлай!"
    elif percentage >= 60:
        emoji = "📚"
        message = "Яна ўқишни давом этинг"
    else:
        emoji = "💪"
        message = "Сўртсинг, хатоларни ўрганинг"

    text = (
        f"{emoji} <b>{message}</b>\n\n"
        f"<b>Натижалар:</b>\n"
        f"🎯 <b>{percentage:.0f}%</b>\n"
        f"✅ Тўғри: {correct_count}/{total_count}\n"
    )

    keyboard = [
        [InlineKeyboardButton("🔄 Қайта синаш", callback_data="restart")],
        [InlineKeyboardButton("📚 Бошқа тест", callback_data="menu")]
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
        print("⚠️  Тестлар топилмади! Пожалуйста проверьте папку 'data'")
        return

    print(f"✅ Юкланди {len(TESTS)} та тест:")
    for name, tests in TESTS.items():
        print(f"   - {name}: {len(tests)} сўрав")

    # Get token
    TOKEN = "8633297005:AAGKa3jK6hyg1gM6D1G2TfYVUknLWUZPBbY"

    # Create application
    application = Application.builder().token(TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(button_callback))

    # Start bot
    print("🤖 Бот ишга тушди...")
    print("Бот ишлаб турганда Ctrl+C'ни басинг узмотиш учун.")
    application.run_polling()

if __name__ == '__main__':
    main()
