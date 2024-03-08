from aiogram.dispatcher.filters.state import StatesGroup, State


class Form(StatesGroup):
    login_id = State()
    password = State()
    teacher_rating = State()
    feedback = State()
    feedback_message = State()
    waiting_for_news = State()
