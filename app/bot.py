import os
import logging
import requests
import json
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from database_handler import DatabaseHandler
from agents import SwimmingAcademyAgents

# Load environment variables
load_dotenv()

# Initialize database handler
db_handler = DatabaseHandler()

# Ollama API endpoint
OLLAMA_API_URL = "http://localhost:11434/api/generate"

# Initialize agents
academy_agents = SwimmingAcademyAgents()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Excel file path
EXCEL_FILE = 'inquiries_data.xlsx'

# Conversation states
CHOOSING, BOOKING, NAME, EMAIL, PHONE, PROGRAM_CHOICE, CONFIRMATION, AI_QUERY = range(8)

# Program information
PROGRAMS = {
    'Kids Program': '4-14 years, 8 levels available',
    'Adults Program': '14+ years, 8 levels available',
    'Ladies-Only Aqua Fitness': '14+ years, Group classes',
    'Baby & Toddler Program': 'Early water introduction',
    'Special Needs Program': '4-14 years, Specialized coaching'
}

def load_or_create_df():
    """Load existing Excel file or create new DataFrame if it doesn't exist."""
    try:
        return pd.read_excel(EXCEL_FILE)
    except FileNotFoundError:
        return pd.DataFrame(columns=['timestamp', 'user_id', 'name', 'email', 'phone', 'inquiry_type', 'program'])

def save_user_data(user_data, user_id):
    """Save user data to Excel file."""
    df = load_or_create_df()
    
    new_row = {
        'timestamp': datetime.now(),
        'user_id': user_id,
        'name': user_data.get('name', ''),
        'email': user_data.get('email', ''),
        'phone': user_data.get('phone', ''),
        'inquiry_type': user_data.get('inquiry_type', ''),
        'program': user_data.get('program', '')
    }
    
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_excel(EXCEL_FILE, index=False)
    logger.info(f"Saved inquiry data for user {user_id}")

def get_program_info(program_name):
    """Get detailed information about a program."""
    program_details = {
        'Kids Program': (
            "🏊‍♂️ Kids Program (4-14 years)\n\n"
            "• 8 levels available\n"
            "• Each level: 8 classes\n"
            "• Available as group or private classes\n"
            "• Focus on water safety and confidence\n"
            "• Professional ASCA certified coaches\n\n"
            "Location: The Sustainable City, Dubai"
        ),
        'Adults Program': (
            "🏊‍♀️ Adults Program (14+ years)\n\n"
            "• 8 progressive levels\n"
            "• Each level: 8 classes\n"
            "• Group or private classes available\n"
            "• Customized to your goals\n"
            "• Focus on technique and fitness\n\n"
            "Location: The Sustainable City, Dubai"
        ),
        'Ladies-Only Aqua Fitness': (
            "💪 Ladies-Only Aqua Fitness\n\n"
            "• Exclusive women-only environment\n"
            "• Group classes available\n"
            "• Low-impact full-body workout\n"
            "• Focus on fitness and well-being\n"
            "• Professional female instructors\n\n"
            "Location: The Sustainable City, Dubai"
        ),
        'Baby & Toddler Program': (
            "👶 Baby & Toddler Program\n\n"
            "• Safe water introduction\n"
            "• Parent-child bonding\n"
            "• Certified infant swimming instructors\n"
            "• Focus on water familiarity\n"
            "• Fun and engaging activities\n\n"
            "Location: The Sustainable City, Dubai"
        ),
        'Special Needs Program': (
            "🌟 Special Needs Program (4-14 years)\n\n"
            "• Specialized coaching\n"
            "• 8 adaptive levels\n"
            "• Individual attention\n"
            "• Trained special needs instructors\n"
            "• Safe and supportive environment\n\n"
            "Location: The Sustainable City, Dubai"
        )
    }
    return program_details.get(program_name, "Program information not available")

# def get_ai_response(query: str, user_data: dict = None) -> str:
#     """Get response using CrewAI agents."""
#     try:
#         # Process query through CrewAI agents
#         response = academy_agents.process_query(query, user_data)
#         # Format response with navigation options
#         return academy_agents.format_response(response)
#     except Exception as e:
#         logger.error(f"Error in AI processing: {e}")
#         return "I encountered an error. Please try again or contact support."

def get_ai_response(query: str, user_data: dict = None) -> str:
    """Send query to n8n workflow and return response."""
    url = "https://twenty50.app.n8n.cloud/webhook-test/3fbdd969-73e9-42ea-9de6-d9fe30599baa"
    payload = {
        "query": query,
        "user_data": user_data
    }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()  # Raise an error for bad responses
        return response.json().get('message', 'No response from the AI agent.')  # Adjust based on your workflow output
    except requests.exceptions.RequestException as e:
        logger.error(f"Error connecting to n8n: {e}")
        return "Sorry, I couldn't process your request. Please try again later."


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the conversation and show main menu."""
    reply_keyboard = [
        ['Book a Class', 'Program Information'],
        ['Location & Hours', 'Contact Us'],
        ['Talk to our AI Agent!']
    ]
    
    await update.message.reply_text(
        "👋 Welcome to Aquasprint Swimming Academy!\n\n"
        "How can I assist you today?",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return CHOOSING

async def handle_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle the user's main menu choice."""
    choice = update.message.text
    
    if choice == 'Back to Main Menu':
        reply_keyboard = [
            ['Book a Class', 'Program Information'],
            ['Location & Hours', 'Contact Us'],
            ['Talk to our AI Agent!']
        ]
        await update.message.reply_text(
            "👋 Welcome back! How can I assist you today?",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        )
        return CHOOSING
    
    if choice == 'Talk to our AI Agent!':
        await update.message.reply_text(
            "Please type your question, and I'll do my best to help you.\n"
            "You can return to the main menu anytime by typing 'menu'.",
            reply_markup=ReplyKeyboardRemove()
        )
        return AI_QUERY
    
    if choice == 'Book This Program':
        # Set inquiry type to booking
        context.user_data['inquiry_type'] = 'Book a Class'
        await update.message.reply_text("Please provide your name:")
        return NAME
    
    context.user_data['inquiry_type'] = choice
    
    if choice == 'Book a Class':
        programs_keyboard = [[prog] for prog in PROGRAMS.keys()]
        programs_keyboard.append(['Back to Main Menu'])
        await update.message.reply_text(
            "Which program would you like to book?",
            reply_markup=ReplyKeyboardMarkup(programs_keyboard, one_time_keyboard=True)
        )
        return PROGRAM_CHOICE
    
    elif choice == 'Program Information':
        programs_keyboard = [[prog] for prog in PROGRAMS.keys()]
        programs_keyboard.append(['Back to Main Menu'])
        await update.message.reply_text(
            "Which program would you like to know more about?",
            reply_markup=ReplyKeyboardMarkup(programs_keyboard, one_time_keyboard=True)
        )
        return PROGRAM_CHOICE
    
    elif choice == 'Location & Hours':
        await update.message.reply_text(
            "🏊‍♂️ Aquasprint Swimming Academy\n\n"
            "📍 Location: The Sustainable City, Dubai\n\n"
            "⏰ Hours: Every day 6:00 AM - 10:00 PM\n\n"
            "📞 Phone: +971542502761\n"
            "📧 Email: info@aquasprint.ae",
            reply_markup=ReplyKeyboardMarkup([['Back to Main Menu']], one_time_keyboard=True)
        )
        return CHOOSING
    
    elif choice == 'Contact Us':
        await update.message.reply_text(
            "Please provide your name so we can assist you better:"
        )
        return NAME

async def handle_program_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle program selection."""
    program = update.message.text
    
    if program == 'Back to Main Menu':
        reply_keyboard = [
            ['Book a Class', 'Program Information'],
            ['Location & Hours', 'Contact Us'],
            ['Talk to our AI Agent!']
        ]
        await update.message.reply_text(
            "👋 Welcome back! How can I assist you today?",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        )
        return CHOOSING
        
    context.user_data['program'] = program
    
    if context.user_data['inquiry_type'] == 'Program Information':
        program_info = get_program_info(program)
        await update.message.reply_text(
            program_info,
            reply_markup=ReplyKeyboardMarkup([['Book This Program', 'Back to Main Menu']], one_time_keyboard=True)
        )
        return CHOOSING
    else:  # Book a Class flow
        await update.message.reply_text(
            f"You've selected: {program}\n\n"
            "Please provide your name to proceed with the booking:",
            reply_markup=ReplyKeyboardRemove()
        )
        return NAME

async def handle_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Save name and ask for email."""
    context.user_data['name'] = update.message.text
    await update.message.reply_text("Please provide your email address:")
    return EMAIL

async def handle_email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Save email and ask for phone number."""
    context.user_data['email'] = update.message.text
    await update.message.reply_text("Please provide your phone number:")
    return PHONE

async def handle_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Save phone number and show confirmation."""
    context.user_data['phone'] = update.message.text
    
    await update.message.reply_text(
        f"Please confirm your information:\n\n"
        f"Name: {context.user_data['name']}\n"
        f"Email: {context.user_data['email']}\n"
        f"Phone: {context.user_data['phone']}\n"
        f"Program: {context.user_data.get('program', 'General Inquiry')}\n\n"
        f"Is this correct? (yes/no)",
        reply_markup=ReplyKeyboardMarkup([['yes', 'no']], one_time_keyboard=True)
    )
    return CONFIRMATION

async def handle_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle the confirmation response."""
    if update.message.text.lower() == 'yes':
        save_user_data(context.user_data, update.effective_user.id)
        
        if context.user_data['inquiry_type'] == 'Book a Class':
            await update.message.reply_text(
                "Thank you for your booking request! Our team will contact you within 24 hours to confirm your booking and schedule.\n\n"
                "Type /start to return to the main menu.",
                reply_markup=ReplyKeyboardRemove()
            )
        else:
            await update.message.reply_text(
                "Thank you for your inquiry! Our team will contact you shortly.\n\n"
                "Type /start to return to the main menu.",
                reply_markup=ReplyKeyboardRemove()
            )
    else:
        await update.message.reply_text(
            "Let's start over. Type /start to begin again.",
            reply_markup=ReplyKeyboardRemove()
        )
    
    return ConversationHandler.END

async def handle_ai_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle AI queries."""
    query = update.message.text
    
    if query.lower() == 'menu' or query == 'Back to Main Menu':
        reply_keyboard = [
            ['Book a Class', 'Program Information'],
            ['Location & Hours', 'Contact Us'],
            ['Talk to our AI Agent!']
        ]
        await update.message.reply_text(
            "👋 Welcome back! How can I assist you today?",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        )
        return CHOOSING
        
    if query == 'Ask Another Question':
        await update.message.reply_text(
            "Sure! What would you like to know? You can ask me anything about our programs, schedules, or facilities.",
            reply_markup=ReplyKeyboardRemove()
        )
        return AI_QUERY
    
    # Get user data for database queries
    user_data = {
        'user_id': update.effective_user.id,
        'name': context.user_data.get('name', ''),
        'email': context.user_data.get('email', ''),
        'phone': context.user_data.get('phone', ''),
        'program': context.user_data.get('program', '')
    }
    
    # Get AI response with user data
    response = get_ai_response(query, user_data)
    
    # After getting response, provide options to continue
    reply_keyboard = [['Ask Another Question', 'Back to Main Menu']]
    await update.message.reply_text(
        response,
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    # Stay in AI_QUERY state to handle next question
    return AI_QUERY

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel the conversation."""
    await update.message.reply_text(
        "Operation cancelled. Type /start to begin again.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

def main() -> None:
    """Run the bot."""
    application = Application.builder().token(os.getenv('TELEGRAM_BOT_TOKEN')).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING: [
                MessageHandler(filters.Regex('^(Book a Class|Program Information|Location & Hours|Contact Us|Back to Main Menu|Talk to our AI Agent!)$'), handle_choice),
                MessageHandler(filters.Regex('^Book This Program$'), handle_choice)
            ],
            PROGRAM_CHOICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_program_choice)],
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_name)],
            EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_email)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_phone)],
            CONFIRMATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_confirmation)],
            AI_QUERY: [
                MessageHandler(filters.Regex('^Back to Main Menu$'), handle_ai_query),
                MessageHandler(filters.Regex('^Ask Another Question$'), handle_ai_query),
                MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.Regex('^(Back to Main Menu|Ask Another Question)$'), handle_ai_query)
            ],
        },
        fallbacks=[
            CommandHandler('cancel', cancel),
            CommandHandler('start', start),
            MessageHandler(filters.Regex('^menu$'), handle_ai_query),
        ],
    )

    application.add_handler(conv_handler)
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main() 