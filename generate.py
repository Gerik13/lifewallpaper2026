# ================================================
# Импорт стандартных библиотек
# ================================================
from datetime import date
import calendar
import os

# ================================================
# Импорт PIL
# ================================================
from PIL import Image, ImageDraw, ImageFont


# ================================================
# ФУНКЦИЯ ДЛЯ МАКСИМАЛЬНОЙ ЧЁТКОСТИ ТЕКСТА
# ================================================
def draw_text_crisp(draw, pos, text, font, fill, bg):
    x, y = int(pos[0]), int(pos[1])
    # псевдо-hinting (микрообводка)
    draw.text((x-1, y), text, font=font, fill=bg)
    draw.text((x+1, y), text, font=font, fill=bg)
    draw.text((x, y-1), text, font=font, fill=bg)
    draw.text((x, y+1), text, font=font, fill=bg)
    draw.text((x, y), text, font=font, fill=fill)


# ================================================
# ФИНАЛЬНОЕ РАЗРЕШЕНИЕ (Xiaomi 12T)
# ================================================
FINAL_WIDTH = 1220
FINAL_HEIGHT = 2712

QUALITY_SCALE = 1.5

WIDTH = int(FINAL_WIDTH * QUALITY_SCALE)
HEIGHT = int(FINAL_HEIGHT * QUALITY_SCALE)


# ================================================
# ЦВЕТА
# ================================================
BG = "#0F1115"
WHITE = "#FFFFFF"
GRAY = "#8A8A95"
DARK = "#2A2D34"
ORANGE = "#FF9F1C"
RED = "#FF453A"


# ================================================
# КАЛЕНДАРЬ
# ================================================
YEAR = 2026
TOTAL_DAYS = 365


# ================================================
# МАСШТАБ
# ================================================
SCALE = 1.5
FOOTER_SCALE = 1.5
VERTICAL_SHIFT = int(220 * QUALITY_SCALE)


# ================================================
# ХОЛСТ
# ================================================
img = Image.new("RGB", (WIDTH, HEIGHT), BG)
draw = ImageDraw.Draw(img)


# ================================================
# ШРИФТ
# ================================================
FONT_PATH = "fonts/Roboto-Regular.ttf"

font_month = ImageFont.truetype(FONT_PATH, int(22 * SCALE * QUALITY_SCALE))
font_weekday = ImageFont.truetype(FONT_PATH, int(14 * SCALE * QUALITY_SCALE))
font_footer = ImageFont.truetype(
    FONT_PATH,
    int(16 * SCALE * FOOTER_SCALE * QUALITY_SCALE)
)


# ================================================
# ДАННЫЕ
# ================================================
months = [
    ("ЯНВАРЬ", 1), ("ФЕВРАЛЬ", 2), ("МАРТ", 3),
    ("АПРЕЛЬ", 4), ("МАЙ", 5), ("ИЮНЬ", 6),
    ("ИЮЛЬ", 7), ("АВГУСТ", 8), ("СЕНТЯБРЬ", 9),
    ("ОКТЯБРЬ", 10), ("НОЯБРЬ", 11), ("ДЕКАБРЬ", 12),
]

weekdays = ["ПН", "ВТ", "СР", "ЧТ", "ПТ", "СБ", "ВС"]


# ================================================
# РАСКЛАДКА
# ================================================
COLS = 3
ROWS = 4

DOT_SIZE = int(16 * SCALE * QUALITY_SCALE)
DOT_GAP = int(12 * SCALE * QUALITY_SCALE)
LINE_GAP = int(10 * SCALE * QUALITY_SCALE)

TITLE_HEIGHT = int(34 * SCALE * QUALITY_SCALE)
WEEKDAY_HEIGHT = int(18 * SCALE * QUALITY_SCALE)

H_GAP = int(36 * SCALE * QUALITY_SCALE)
V_GAP = int(44 * SCALE * QUALITY_SCALE)

MONTH_CONTENT_WIDTH = 7 * (DOT_SIZE + DOT_GAP)
CELL_WIDTH = MONTH_CONTENT_WIDTH
CELL_HEIGHT = int(200 * SCALE * QUALITY_SCALE)


# ================================================
# ЦЕНТРИРОВАНИЕ
# ================================================
GRID_WIDTH = COLS * CELL_WIDTH + (COLS - 1) * H_GAP
GRID_HEIGHT = ROWS * CELL_HEIGHT + (ROWS - 1) * V_GAP

START_X = int((WIDTH - GRID_WIDTH) // 2)
START_Y = int((HEIGHT - GRID_HEIGHT) // 2 + VERTICAL_SHIFT)


# ================================================
# ДАТА И ПРОГРЕСС
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
# ОТРИСОВКА
# ================================================
for i, (month_name, month_num) in enumerate(months):

    col = i % COLS
    row = i // COLS

    x0 = int(START_X + col * (CELL_WIDTH + H_GAP))
    y0 = int(START_Y + row * (CELL_HEIGHT + V_GAP))

    # Название месяца
    bbox = draw.textbbox((0, 0), month_name, font=font_month)
    title_w = bbox[2] - bbox[0]

    draw.text(
        (int(x0 + (CELL_WIDTH - title_w) // 2), y0),
        month_name,
        fill=WHITE,
        font=font_month
    )

    # Дни недели (ЧЁТКИЕ)
    wx = int(x0)
    wy = int(y0 + TITLE_HEIGHT)

    for idx, wd in enumerate(weekdays):
        color = RED if idx >= 5 else GRAY
        draw_text_crisp(
            draw,
            (wx, wy),
            wd,
            font_weekday,
            fill=color,
            bg=BG
        )
        wx += DOT_SIZE + DOT_GAP

    # Точки дней
    first_weekday, days_in_month = calendar.monthrange(YEAR, month_num)
    x = int(x0 + first_weekday * (DOT_SIZE + DOT_GAP))
    y = int(wy + WEEKDAY_HEIGHT)

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

        draw.ellipse((x, y, x + DOT_SIZE, y + DOT_SIZE), fill=color)

        x += DOT_SIZE + DOT_GAP
        if (first_weekday + day) % 7 == 0:
            x = int(x0)
            y += DOT_SIZE + LINE_GAP


# ================================================
# ПРОГРЕСС
# ================================================
text_left = f"Осталось {remaining_days} дней"
text_right = f" · {progress_percent}%"

bbox_l = draw.textbbox((0, 0), text_left, font=font_footer)
bbox_r = draw.textbbox((0, 0), text_right, font=font_footer)

total_w = bbox_l[2] - bbox_l[0] + bbox_r[2] - bbox_r[0]

fx = int((WIDTH - total_w) // 2)
fy = int(START_Y + GRID_HEIGHT + 48 * SCALE * QUALITY_SCALE)

draw.text((fx, fy), text_left, fill=ORANGE, font=font_footer)
draw.text((fx + (bbox_l[2] - bbox_l[0]), fy), text_right, fill=WHITE, font=font_footer)


# ================================================
# ФИНАЛЬНЫЙ DOWNSCALE + SAVE
# ================================================
output_dir = "output"
os.makedirs(output_dir, exist_ok=True)

final_img = img.resize(
    (FINAL_WIDTH, FINAL_HEIGHT),
    resample=Image.LANCZOS
)

output_path = os.path.join(output_dir, "wallpaper.png")
final_img.save(output_path, optimize=False)

print("Готово:", output_path)
