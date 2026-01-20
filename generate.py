# ================================================
# Импорт стандартных библиотек
# ================================================
from datetime import date
import calendar
import os

# ================================================
# Импорт библиотеки для работы с изображениями
# ================================================
from PIL import Image, ImageDraw, ImageFont


# ================================================
# РАЗМЕР ЭКРАНА (Xiaomi 12T)
# ================================================
WIDTH, HEIGHT = 1220, 2712


# ================================================
# ЦВЕТА (единый источник правды)
# ================================================
BG = "#0F1115"        # фон
WHITE = "#FFFFFF"    # прошедшие дни / проценты
GRAY = "#8A8A95"     # вторичный текст
DARK = "#2A2D34"     # будущие дни
ORANGE = "#FF9F1C"   # текущий день / текст прогресса
RED = "#FF453A"      # выходные (только текст)


# ================================================
# КАЛЕНДАРНЫЙ ГОД
# ================================================
YEAR = 2026
TOTAL_DAYS = 365


# ================================================
# МАСШТАБ И ПОЗИЦИЯ СЕТКИ
# ================================================
SCALE = 1.3               # масштаб ВСЕЙ сетки
FOOTER_SCALE = 1.5        # масштаб ТОЛЬКО прогресс-бара
VERTICAL_SHIFT = 200       # сдвиг сетки вниз


# ================================================
# СОЗДАНИЕ ХОЛСТА
# ================================================
img = Image.new("RGB", (WIDTH, HEIGHT), BG)
draw = ImageDraw.Draw(img)


# ================================================
# СИСТЕМНЫЙ ШРИФТ (поддерживает кириллицу)
# ================================================
FONT_PATH = "fonts/Roboto-Regular.ttf"


font_month = ImageFont.truetype(FONT_PATH, int(22 * SCALE))
font_weekday = ImageFont.truetype(FONT_PATH, int(13 * SCALE))
font_footer = ImageFont.truetype(
    FONT_PATH,
    int(16 * SCALE * FOOTER_SCALE)
)


# ================================================
# ДАННЫЕ О МЕСЯЦАХ
# ================================================
months = [
    ("ЯНВАРЬ", 1), ("ФЕВРАЛЬ", 2), ("МАРТ", 3),
    ("АПРЕЛЬ", 4), ("МАЙ", 5), ("ИЮНЬ", 6),
    ("ИЮЛЬ", 7), ("АВГУСТ", 8), ("СЕНТЯБРЬ", 9),
    ("ОКТЯБРЬ", 10), ("НОЯБРЬ", 11), ("ДЕКАБРЬ", 12),
]

weekdays = ["ПН", "ВТ", "СР", "ЧТ", "ПТ", "СБ", "ВС"]


# ================================================
# ПАРАМЕТРЫ РАСКЛАДКИ (умножены на SCALE)
# ================================================
COLS = 3
ROWS = 4

DOT_SIZE = int(16 * SCALE)
DOT_GAP = int(12 * SCALE)
LINE_GAP = int(10 * SCALE)

TITLE_HEIGHT = int(34 * SCALE)
WEEKDAY_HEIGHT = int(18 * SCALE)

H_GAP = int(36 * SCALE)
V_GAP = int(44 * SCALE)

MONTH_CONTENT_WIDTH = 7 * (DOT_SIZE + DOT_GAP)
CELL_WIDTH = MONTH_CONTENT_WIDTH
CELL_HEIGHT = int(200 * SCALE)


# ================================================
# ВЫЧИСЛЕНИЕ ЦЕНТРА СЕТКИ
# ================================================
GRID_WIDTH = COLS * CELL_WIDTH + (COLS - 1) * H_GAP
GRID_HEIGHT = ROWS * CELL_HEIGHT + (ROWS - 1) * V_GAP

START_X = (WIDTH - GRID_WIDTH) // 2
START_Y = (HEIGHT - GRID_HEIGHT) // 2 + VERTICAL_SHIFT


# ================================================
# ТЕКУЩАЯ ДАТА И ПРОГРЕСС ГОДА
# ================================================
today = date.today()

if today.year < YEAR:
    day_of_year = 0
elif today.year > YEAR:
    day_of_year = TOTAL_DAYS
else:
    day_of_year = today.timetuple().tm_yday

remaining_days = TOTAL_DAYS - day_of_year
progress_percent = int((day_of_year / TOTAL_DAYS) * 100)


# ================================================
# ОТРИСОВКА МЕСЯЦЕВ
# ================================================
for i, (month_name, month_num) in enumerate(months):

    col = i % COLS
    row = i // COLS

    x0 = START_X + col * (CELL_WIDTH + H_GAP)
    y0 = START_Y + row * (CELL_HEIGHT + V_GAP)

    # ---- Название месяца (по центру ячейки)
    bbox = draw.textbbox((0, 0), month_name, font=font_month)
    title_w = bbox[2] - bbox[0]

    draw.text(
        (x0 + (CELL_WIDTH - title_w) // 2, y0),
        month_name,
        fill=WHITE,
        font=font_month
    )

    # ---- Дни недели (СБ / ВС красные)
    wx = x0
    wy = y0 + TITLE_HEIGHT

    for idx, wd in enumerate(weekdays):
        color = RED if idx >= 5 else GRAY
        draw.text((wx, wy), wd, fill=color, font=font_weekday)
        wx += DOT_SIZE + DOT_GAP

    # ---- Точки дней месяца
    first_weekday, days_in_month = calendar.monthrange(YEAR, month_num)
    x = x0 + first_weekday * (DOT_SIZE + DOT_GAP)
    y = wy + WEEKDAY_HEIGHT

    for day in range(1, days_in_month + 1):

        is_today = (
            today.year == YEAR and
            today.month == month_num and
            today.day == day
        )

        is_past = (
            today.year > YEAR or
            (today.year == YEAR and (
                month_num < today.month or
                (month_num == today.month and day < today.day)
            ))
        )

        if is_today:
            color = ORANGE
        elif is_past:
            color = WHITE
        else:
            color = DARK

        draw.ellipse(
            (x, y, x + DOT_SIZE, y + DOT_SIZE),
            fill=color
        )

        x += DOT_SIZE + DOT_GAP

        if (first_weekday + day) % 7 == 0:
            x = x0
            y += DOT_SIZE + LINE_GAP


# ================================================
# ПРОГРЕСС-БАР (текстовый)
# ================================================
text_left = f"Осталось {remaining_days} дней"
text_right = f" · {progress_percent}%"

bbox_l = draw.textbbox((0, 0), text_left, font=font_footer)
bbox_r = draw.textbbox((0, 0), text_right, font=font_footer)

total_width = (bbox_l[2] - bbox_l[0]) + (bbox_r[2] - bbox_r[0])
footer_x = (WIDTH - total_width) // 2
footer_y = START_Y + GRID_HEIGHT + int(48 * SCALE)

draw.text((footer_x, footer_y), text_left, fill=ORANGE, font=font_footer)
draw.text(
    (footer_x + (bbox_l[2] - bbox_l[0]), footer_y),
    text_right,
    fill=WHITE,
    font=font_footer
)


# ================================================
# СОХРАНЕНИЕ ФАЙЛА
# ================================================
# ================================================
# SAVE RESULT TO /output
# ================================================
output_dir = "output"
os.makedirs(output_dir, exist_ok=True)

output = os.path.join(output_dir, "wallpaper.png")
img.save(output)

print("Готово:", output)
