from aiogram_dialog import Window
from aiogram_dialog.widgets.text import Const, Format, List  # Добавьте List
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Button, Row, Back, Next, Cancel, Radio, Group

from .states import QuestionnaireStates
from .handlers import (
    on_age_selected, on_gender_selected, on_height_selected,
    on_weight_selected, on_target_weight_selected, on_body_type_selected,
    on_goal_selected, on_lifestyle_selected, on_sleep_hours_selected,
    on_genetics_selected, on_experience_selected, on_last_form_date_selected,
    on_training_focus_selected, on_training_location_selected, on_training_time_selected,
    on_training_days_selected, on_training_type_selected, on_training_difficulty_selected,
    on_injuries_selected, on_flexibility_selected, on_endurance_selected,
    on_confirmation_save, on_confirmation_edit, getter_summary
)

# Окно для вопроса о возрасте
age_window = Window(
    Const("📊 <b>Основные данные</b>\n\n"
          "1. <b>Сколько вам лет?</b>\n\n"
          "<i>Введите число от 14 до 100</i>"),
    TextInput(
        id="age_input",
        on_success=on_age_selected,
    ),
    Cancel(text=Const("❌ Отмена")),
    state=QuestionnaireStates.age,
)

# Окно для вопроса о поле
gender_window = Window(
    Const("👤 <b>Ваш пол?</b>\n\n"
          "<i>Выберите один из вариантов:</i>"),
    Radio(
        checked_text=Format("✅ {item[0]}"),
        unchecked_text=Format("{item[0]}"),
        id="gender_radio",  # ИЗМЕНЕНО!
        item_id_getter=lambda item: item[1],  # ИЗМЕНЕНО!
        items=[
            ("👨 Мужской", "male"),      # КОРТЕЖИ!
            ("👩 Женский", "female"),
        ],
        on_click=on_gender_selected,  # ИЗМЕНЕНО!
    ),
    Row(
        Back(text=Const("⬅️ Назад")),
        Cancel(text=Const("❌ Отмена")),
    ),
    state=QuestionnaireStates.gender,
)

# Окно для вопроса о росте
height_window = Window(
    Const("📏 <b>Ваш рост (в сантиметрах)?</b>\n\n"
          "<i>Введите число от 100 до 250 см</i>\n"
          "<i>Например: 175</i>"),
    TextInput(
        id="height_input",
        on_success=on_height_selected,
    ),
    Row(
        Back(text=Const("⬅️ Назад")),
        Cancel(text=Const("❌ Отмена")),
    ),
    state=QuestionnaireStates.height,
)

# Окно для вопроса о весе
weight_window = Window(
    Const("⚖️ <b>Ваш текущий вес (в кг)?</b>\n\n"
          "<i>Введите число от 30 до 300 кг</i>\n"
          "<i>Например: 70.5</i>"),
    TextInput(
        id="weight_input",
        on_success=on_weight_selected,
    ),
    Row(
        Back(text=Const("⬅️ Назад")),
        Cancel(text=Const("❌ Отмена")),
    ),
    state=QuestionnaireStates.weight,
)

# Окно для вопроса о целевом весе
target_weight_window = Window(
    Const("🎯 <b>Ваш целевой вес (в кг)?</b>\n\n"
          "<i>Введите желаемый вес</i>\n"
          "<i>Например: 65.0</i>"),
    TextInput(
        id="target_weight_input",
        on_success=on_target_weight_selected,
    ),
    Row(
        Back(text=Const("⬅️ Назад")),
        Cancel(text=Const("❌ Отмена")),
    ),
    state=QuestionnaireStates.target_weight,
)

# Окно для вопроса о типе телосложения
body_type_window = Window(
    Const("💪 <b>Ваш тип телосложения?</b>\n\n"
          "<i>Выберите наиболее подходящий вариант:</i>"),
    Group(
        Radio(
            checked_text=Format("✅ {item[0]}"),
            unchecked_text=Format("{item[0]}"),
            id="body_type_radio",
            item_id_getter=lambda item: item[1],  # ИЗМЕНЕНО!
            items=[
                ("📐 Эктоморф (худощавый)", "ectomorph"),  # КОРТЕЖИ!
                ("📦 Мезоморф (мускулистый)", "mesomorph"),
                ("📦 Эндоморф (склонный к полноте)", "endomorph"),
                ("❓ Не знаю", "unknown")
            ],
            on_click=on_body_type_selected,
        ),
        width=1,
    ),
    Row(
        Back(text=Const("⬅️ Назад")),
        Next(text=Const("➡️ Далее")),
        Cancel(text=Const("❌ Отмена")),
    ),
    state=QuestionnaireStates.body_type,
)

# Группа 2: Цели и образ жизни

# Окно для вопроса о цели
goal_window = Window(
    Const("🎯 <b>Цели и образ жизни</b>\n\n"
          "7. <b>Ваша основная цель?</b>\n\n"
          "<i>Выберите главную цель тренировок:</i>"),
    Group(
        Radio(
            checked_text=Format("✅ {item[0]}"),
            unchecked_text=Format("{item[0]}"),
            id="goal_radio",
            item_id_getter=lambda item: item[1],
            items=[
                ("⚖️ Похудеть", "lose_weight"),
                ("💪 Набрать мышечную массу", "gain_muscle"),
                ("🛡️ Поддерживать форму", "maintain"),
                ("❤️ Улучшить здоровье", "improve_health"),
                ("🏃 Увеличить выносливость", "improve_endurance"),
                ("🎨 Преобразить тело", "body_recomposition"),
            ],
            on_click=on_goal_selected,
        ),
        width=1,
    ),
    Row(
        Back(text=Const("⬅️ Назад")),
        Cancel(text=Const("❌ Отмена")),
    ),
    state=QuestionnaireStates.goal,
)

# Окно для вопроса об образе жизни
lifestyle_window = Window(
    Const("🏃 <b>Ваш образ жизни?</b>\n\n"
          "<i>Оцените уровень вашей ежедневной активности:</i>"),
    Group(
        Radio(
            checked_text=Format("✅ {item[0]}"),
            unchecked_text=Format("{item[0]}"),
            id="lifestyle_radio",
            item_id_getter=lambda item: item[1],
            items=[
                ("🪑 Сидячий (офисная работа)", "sedentary"),
                ("🚶 Легкая активность (прогулки)", "lightly_active"),
                ("🏃 Средняя активность (тренировки 2-3 раза/нед)", "moderately_active"),
                ("💪 Высокая активность (тренировки 4-5 раз/нед)", "very_active"),
                ("🏆 Экстремальная активность (профессиональный спорт)", "extremely_active"),
            ],
            on_click=on_lifestyle_selected,
        ),
        width=1,
    ),
    Row(
        Back(text=Const("⬅️ Назад")),
        Cancel(text=Const("❌ Отмена")),
    ),
    state=QuestionnaireStates.lifestyle,
)

# Окно для вопроса о сне
sleep_hours_window = Window(
    Const("😴 <b>Сколько часов в сутки вы спите?</b>\n\n"
          "<i>Введите среднее количество часов сна (4.0-12.0)</i>\n"
          "<i>Например: 8.0</i>"),
    TextInput(
        id="sleep_input",
        on_success=on_sleep_hours_selected,
    ),
    Row(
        Back(text=Const("⬅️ Назад")),
        Cancel(text=Const("❌ Отмена")),
    ),
    state=QuestionnaireStates.sleep_hours,
)

# Окно для вопроса о генетике
genetics_window = Window(
    Const("🧬 <b>Расскажите о вашей генетике</b>\n\n"
          "<i>Есть ли особенности телосложения, которые передались по наследству?</i>\n"
          "<i>Например: 'Мама полная, папа худой' или 'Все в семье худощавые'</i>\n\n"
          "<i>(Можно оставить пустым)</i>"),
    TextInput(
        id="genetics_input",
        on_success=on_genetics_selected,
    ),
    Row(
        Back(text=Const("⬅️ Назад")),
        Next(text=Const("➡️ Далее")),
        Cancel(text=Const("❌ Отмена")),
    ),
    state=QuestionnaireStates.genetics,
)

# Окно для вопроса об опыте тренировок
experience_window = Window(
    Const("🏋️ <b>У вас есть опыт тренировок?</b>\n\n"
          "<i>Регулярно ли вы занимались спортом раньше?</i>"),
    Radio(
        checked_text=Format("✅ {item[0]}"),
        unchecked_text=Format("{item[0]}"),
        id="experience_radio",
        item_id_getter=lambda item: item[1],
        items=[
            ("✅ Да, есть опыт", True),
            ("❌ Нет опыта", False),
        ],
        on_click=on_experience_selected,
    ),
    Row(
        Back(text=Const("⬅️ Назад")),
        Cancel(text=Const("❌ Отмена")),
    ),
    state=QuestionnaireStates.training_experience,
)

# Окно для вопроса о последней идеальной форме
last_form_date_window = Window(
    Const("📅 <b>Когда вы были в идеальной форме?</b>\n\n"
          "<i>Введите дату в формате ДД.ММ.ГГГГ</i>\n"
          "<i>Или напишите 'никогда', если никогда не были</i>\n\n"
          "<i>Пример: 01.01.2020</i>"),
    TextInput(
        id="last_form_input",
        on_success=on_last_form_date_selected,
    ),
    Row(
        Back(text=Const("⬅️ Назад")),
        Next(text=Const("➡️ Далее")),
        Cancel(text=Const("❌ Отмена")),
    ),
    state=QuestionnaireStates.last_ideal_form,
)

# Группа 3: Тренировки

# Окно для вопроса о фокусе тренировок
training_focus_window = Window(
    Const("🎯 <b>Тренировки</b>\n\n"
          "13. <b>На каких частях тела хотите сосредоточиться?</b>\n\n"
          "<i>Выберите приоритеты:</i>"),
    Group(
        Radio(
            checked_text=Format("✅ {item[0]}"),
            unchecked_text=Format("{item[0]}"),
            id="training_focus_radio",
            item_id_getter=lambda item: item[1],
            items=[
                ("💪 Всё тело", "full_body"),
                ("🏋️ Верхняя часть тела", "upper_body"),
                ("🦵 Нижняя часть тела", "lower_body"),
                ("🍖 Ягодицы и бёдра", "glutes_legs"),
                ("🦾 Руки и плечи", "arms_shoulders"),
                ("🔥 Живот и талия", "core"),
                ("❓ Не уверен", "unsure"),
            ],
            on_click=on_training_focus_selected,
        ),
        width=1,
    ),
    Row(
        Back(text=Const("⬅️ Назад")),
        Cancel(text=Const("❌ Отмена")),
    ),
    state=QuestionnaireStates.training_focus,
)

# Окно для вопроса о месте тренировок
training_location_window = Window(
    Const("🏠 <b>Где вы будете тренироваться?</b>\n\n"
          "<i>Выберите основное место:</i>"),
    Group(
        Radio(
            checked_text=Format("✅ {item[0]}"),
            unchecked_text=Format("{item[0]}"),
            id="training_location_radio",
            item_id_getter=lambda item: item[1],
            items=[
                ("🏋️ Зал (с оборудованием)", "gym"),
                ("🏠 Дом (с гантелями/без)", "home"),
                ("🌳 Улица/парк", "outdoor"),
                ("💻 Онлайн-тренировки", "online"),
                ("❓ Другое", "other"),
            ],
            on_click=on_training_location_selected,
        ),
        width=1,
    ),
    Row(
        Back(text=Const("⬅️ Назад")),
        Cancel(text=Const("❌ Отмена")),
    ),
    state=QuestionnaireStates.training_location,
)

# Окно для вопроса о времени тренировок
training_time_window = Window(
    Const("⏱️ <b>Сколько времени на тренировку?</b>\n\n"
          "<i>Введите время в минутах (30-120)</i>\n"
          "<i>Например: 60</i>"),
    TextInput(
        id="training_time_input",
        on_success=on_training_time_selected,
    ),
    Row(
        Back(text=Const("⬅️ Назад")),
        Cancel(text=Const("❌ Отмена")),
    ),
    state=QuestionnaireStates.training_time,
)

# Окно для вопроса о днях тренировок
training_days_window = Window(
    Const("📅 <b>Сколько дней в неделю тренировки?</b>\n\n"
          "<i>Введите количество дней (1-7)</i>\n"
          "<i>Например: 3</i>"),
    TextInput(
        id="training_days_input",
        on_success=on_training_days_selected,
    ),
    Row(
        Back(text=Const("⬅️ Назад")),
        Cancel(text=Const("❌ Отмена")),
    ),
    state=QuestionnaireStates.training_days,
)

# Окно для вопроса о типе тренировок
training_type_window = Window(
    Const("🎪 <b>Предпочитаемый тип тренировок?</b>\n\n"
          "<i>Выберите стиль:</i>"),
    Group(
        Radio(
            checked_text=Format("✅ {item[0]}"),
            unchecked_text=Format("{item[0]}"),
            id="training_type_radio",
            item_id_getter=lambda item: item[1],
            items=[
                ("🏋️ Силовые тренировки", "strength"),
                ("🏃 Кардио", "cardio"),
                ("🤸 Йога/пилатес", "yoga_pilates"),
                ("🥊 Бокс/боевые искусства", "combat"),
                ("🏊 Плавание", "swimming"),
                ("🚴 Велоспорт", "cycling"),
                ("❓ Не знаю", "unsure"),
            ],
            on_click=on_training_type_selected,
        ),
        width=1,
    ),
    Row(
        Back(text=Const("⬅️ Назад")),
        Cancel(text=Const("❌ Отмена")),
    ),
    state=QuestionnaireStates.training_type,
)

# Окно для вопроса о сложности
training_difficulty_window = Window(
    Const("📊 <b>Предпочитаемая сложность?</b>\n\n"
          "<i>Выберите уровень:</i>"),
    Group(
        Radio(
            checked_text=Format("✅ {item[0]}"),
            unchecked_text=Format("{item[0]}"),
            id="training_difficulty_radio",
            item_id_getter=lambda item: item[1],
            items=[
                ("🟢 Начальный", "beginner"),
                ("🟡 Средний", "intermediate"),
                ("🔴 Продвинутый", "advanced"),
                ("⚫ Профессиональный", "expert"),
            ],
            on_click=on_training_difficulty_selected,
        ),
        width=1,
    ),
    Row(
        Back(text=Const("⬅️ Назад")),
        Next(text=Const("➡️ Далее")),
        Cancel(text=Const("❌ Отмена")),
    ),
    state=QuestionnaireStates.training_difficulty,
)

# Группа 4: Здоровье

# Окно для вопроса о травмах
injuries_window = Window(
    Const("🏥 <b>Здоровье</b>\n\n"
          "19. <b>Есть ли травмы или ограничения?</b>\n\n"
          "<i>Опишите имеющиеся травмы, боли или медицинские ограничения</i>\n"
          "<i>Например: 'Боль в колене, проблемы со спиной'</i>\n\n"
          "<i>(Можно оставить пустым, если нет)</i>"),
    TextInput(
        id="injuries_input",
        on_success=on_injuries_selected,
    ),
    Row(
        Back(text=Const("⬅️ Назад")),
        Cancel(text=Const("❌ Отмена")),
    ),
    state=QuestionnaireStates.injuries,
)

# Окно для вопроса о гибкости
flexibility_window = Window(
    Const("🤸 <b>Ваш уровень гибкости?</b>\n\n"
          "<i>Оцените гибкость тела:</i>"),
    Group(
        Radio(
            checked_text=Format("✅ {item[0]}"),
            unchecked_text=Format("{item[0]}"),
            id="flexibility_radio",
            item_id_getter=lambda item: item[1],
            items=[
                ("🟢 Отличная гибкость", "excellent"),
                ("🟡 Хорошая", "good"),
                ("🟠 Средняя", "average"),
                ("🔴 Плохая", "poor"),
                ("⚫ Очень плохая", "very_poor"),
            ],
            on_click=on_flexibility_selected,
        ),
        width=1,
    ),
    Row(
        Back(text=Const("⬅️ Назад")),
        Cancel(text=Const("❌ Отмена")),
    ),
    state=QuestionnaireStates.flexibility,
)

# Окно для вопроса о выносливости
endurance_window = Window(
    Const("🏃 <b>Ваш уровень выносливости?</b>\n\n"
          "<i>Оцените физическую выносливость:</i>"),
    Group(
        Radio(
            checked_text=Format("✅ {item[0]}"),
            unchecked_text=Format("{item[0]}"),
            id="endurance_radio",
            item_id_getter=lambda item: item[1],
            items=[
                ("🟢 Отличная выносливость", "excellent"),
                ("🟡 Хорошая", "good"),
                ("🟠 Средняя", "average"),
                ("🔴 Плохая", "poor"),
                ("⚫ Очень плохая", "very_poor"),
            ],
            on_click=on_endurance_selected,
        ),
        width=1,
    ),
    Row(
        Back(text=Const("⬅️ Назад")),
        Next(text=Const("➡️ Далее")),
        Cancel(text=Const("❌ Отмена")),
    ),
    state=QuestionnaireStates.endurance,
)

# Окно подтверждения данных
confirmation_window = Window(
    Const("📋 <b>Подтверждение данных</b>\n\n"
          "Проверьте введённые данные:\n"),
    
    List(
        field=Format("{item[0]}: <b>{item[1]}</b>"),
        items="summary_items",
    ),
    
    Const("\n\n<b>Всё верно?</b>"),
    
    Row(
        Button(
            text=Const("✅ Да, сохранить"),
            id="confirm_save",
            on_click=on_confirmation_save,
        ),
        Button(
            text=Const("✏️ Нет, исправить"),
            id="edit_data",
            on_click=on_confirmation_edit,
        ),
    ),
    
    Cancel(text=Const("❌ Отменить анкету")),
    getter=getter_summary, 
    state=QuestionnaireStates.confirmation,
)
