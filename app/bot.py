import os
import json
import logging
import requests
import pandas as pd
from typing import List
from datetime import datetime
from dotenv import load_dotenv
from langchain.chains import LLMChain
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from langchain_experimental.agents import create_pandas_dataframe_agent
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

CSV_FILE = "inquiries_data.csv"
df = pd.read_csv(CSV_FILE)

CHOOSING, BOOKING, NAME, EMAIL, PHONE, PROGRAM_CHOICE, CONFIRMATION, AI_QUERY = range(8)

PROGRAMS = {
    'Kids Program': '4-14 years, 8 levels available',
    'Adults Program': '14+ years, 8 levels available',
    'Ladies-Only Aqua Fitness': '14+ years, Group classes',
    'Baby & Toddler Program': 'Early water introduction',
    'Special Needs Program': '4-14 years, Specialized coaching'
}

def save_user_data(df, user_data, user_id):
    """Save user data to Excel file."""

    df = df

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
    df.to_csv(CSV_FILE, index=False)

    logger.info(f"Saved inquiry data for user {user_id}")

@tool
def fetch_general_knowledge(query: str) -> str:
    """Fetch general knowledge based on the query."""

    knowledge_base = {
        "swimming benefits": "Swimming improves cardiovascular health, strengthens muscles, and reduces stress.",
        "best swimming programs": "Our programs are tailored to different age groups and abilities, including kids, adults, and specialized programs.",
        "Aquasprint Academy details": (
            "🏊‍♂️ Aquasprint Swimming Academy\n\n"
            "📍 Location: The Sustainable City, Dubai\n\n"
            "⏰ Hours: Every day 6:00 AM - 10:00 PM\n\n"
            "📞 Phone: +971542502761\n"
            "📧 Email: info@aquasprint.ae"
        ),
    }
    
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

    if query.lower() in program_details:
        return program_details[query.lower()]
    
    response = knowledge_base.get(query.lower(), "Sorry, I don't have information on that topic.")
    return response


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


extra_context = (

    "You are an AI assistant specializing in answering questions about Aquasprint Swimming Academy. "
    "You have access to structured data and general knowledge. "
    "If the question is about swimming programs, pricing, schedules, or registration, respond with clear, structured details. "
    "If it's a general question, reply naturally. If data is missing, say so instead of guessing.\n\n"
    "Swimming Benefits:\n"
    "Swimming improves cardiovascular health, strengthens muscles, and reduces stress.\n\n"
    "Best Swimming Programs:\n"
    "Our programs are tailored to different age groups and abilities, including kids, adults, and specialized programs.\n\n"
    "Aquasprint Academy Details:\n"
    "🏊‍♂️ Aquasprint Swimming Academy\n"
    "📍 Location: The Sustainable City, Dubai\n"
    "⏰ Hours: Every day 6:00 AM - 10:00 PM\n"
    "📞 Phone: +971542502761\n"
    "📧 Email: info@aquasprint.ae\n\n"
    "Program Details:\n\n"
    
    "Kids Program (4-14 years):\n"
    "🏊‍♂️ 8 levels available\n"
    "• Each level: 8 classes\n"
    "• Available as group or private classes\n"
    "• Focus on water safety and confidence\n"
    "• Professional ASCA certified coaches\n"
    "Location: The Sustainable City, Dubai\n\n"
    
    "Adults Program (14+ years):\n"
    "🏊‍♀️ 8 progressive levels\n"
    "• Each level: 8 classes\n"
    "• Group or private classes available\n"
    "• Customized to your goals\n"
    "• Focus on technique and fitness\n"
    "Location: The Sustainable City, Dubai\n\n"
    
    "Ladies-Only Aqua Fitness:\n"
    "💪 Exclusive women-only environment\n"
    "• Group classes available\n"
    "• Low-impact full-body workout\n"
    "• Focus on fitness and well-being\n"
    "• Professional female instructors\n"
    "Location: The Sustainable City, Dubai\n\n"
    
    "Baby & Toddler Program:\n"
    "👶 Safe water introduction\n"
    "• Parent-child bonding\n"
    "• Certified infant swimming instructors\n"
    "• Focus on water familiarity\n"
    "• Fun and engaging activities\n"
    "Location: The Sustainable City, Dubai\n\n"
    
    "Special Needs Program (4-14 years):\n"
    "🌟 Specialized coaching\n"
    "• 8 adaptive levels\n"
    "• Individual attention\n"
    "• Trained special needs instructors\n"
    "• Safe and supportive environment\n"
    "Location: The Sustainable City, Dubai"
)

custom_prompt = PromptTemplate(
    input_variables=["query"],
    template=f"{extra_context}\n\nUser Query: {{query}}"
)

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

agent_executor = create_pandas_dataframe_agent(
    llm,
    df,
    agent_type="openai-tools",
    verbose=True,
    allow_dangerous_code=True,
    extra_tools=[fetch_general_knowledge]
)

def get_ai_response(query: str, user_data: dict = None) -> str:
    """Process query using LangChain Pandas agent."""

    try:

        formatted_query = custom_prompt.format(query=query)
        response = agent_executor.run(formatted_query)

        return response

    except Exception as e:

        logger.error(f"Error with LangChain agent: {e}")
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

    else:

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

        save_user_data(df, context.user_data, update.effective_user.id)
        
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

    response = get_ai_response(query)

    reply_keyboard = [['Ask Another Question', 'Back to Main Menu']]

    await update.message.reply_text(
        response,
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )

    return AI_QUERY
    
    user_data = {
        'user_id': update.effective_user.id,
        'name': context.user_data.get('name', ''),
        'email': context.user_data.get('email', ''),
        'phone': context.user_data.get('phone', ''),
        'program': context.user_data.get('program', '')
    }
    
    response = get_ai_response(query, user_data)
    
    reply_keyboard = [['Ask Another Question', 'Back to Main Menu']]
    await update.message.reply_text(
        response,
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )

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