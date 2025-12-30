from aiogram_dialog import Window
from aiogram_dialog.widgets.text import Const, Format, List  # Добавьте List
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Button, Row, Back, Next, Cancel, Radio, Group

from .states import QuestionnaireStates
from .handlers import (
    on_age_selected, on_gender_selected, on_height_selected,
    on_weight_selected, on_target_weight_selected, on_body_type_selected,
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