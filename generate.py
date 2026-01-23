# =================================================
# Импорт стандартных библиотек Python
# =================================================
from datetime import date, datetime, time, timedelta, timezone
import calendar
import os
from PIL.PngImagePlugin import PngInfo

# =================================================
# Импорт PIL (Pillow) для работы с изображениями
# =================================================
from PIL import Image, ImageDraw, ImageFont


# =================================================
# ФУНКЦИЯ: ЧЁТКАЯ ОТРИСОВКА МЕЛКОГО ТЕКСТА
# =================================================
def draw_text_crisp(draw, pos, text, font, fill, bg):
    x, y = int(pos[0]), int(pos[1])

    draw.text((x - 1, y), text, font=font, fill=bg)
    draw.text((x + 1, y), text, font=font, fill=bg)
    draw.text((x, y - 1), text, font=font, fill=bg)
    draw.text((x, y + 1), text, font=font, fill=bg)

    draw.text((x, y), text, font=font, fill=fill)


# =================================================
# ФИНАЛЬНОЕ РАЗРЕШЕНИЕ УСТРОЙСТВА
# =================================================
FINAL_WIDTH = 1220
FINAL_HEIGHT = 2712

QUALITY_SCALE = 1.6

WIDTH = int(FINAL_WIDTH * QUALITY_SCALE)
HEIGHT = int(FINAL_HEIGHT * QUALITY_SCALE)


# =================================================
# ЦВЕТОВАЯ ПАЛИТРА
# =================================================
BG = "#000000"
WHITE = "#FFFFFF"
GRAY = "#8A8A95"
DARK = "#2A2D34"
ORANGE = "#9FBF3B"
RED = "#FF453A"


# =================================================
# НАСТРОЙКА КАЛЕНДАРЯ
# =================================================
YEAR = 2026
TOTAL_DAYS = 365


# =================================================
# ОБЩИЙ МАСШТАБ И ПОЗИЦИЯ СЕТКИ
# =================================================
SCALE = 1.50
FOOTER_SCALE = 1.7
VERTICAL_SHIFT = int(140 * QUALITY_SCALE)


# =================================================
# СОЗДАНИЕ ХОЛСТА
# =================================================
img = Image.new("RGB", (WIDTH, HEIGHT), BG)
draw = ImageDraw.Draw(img)


# =================================================
# ШРИФТЫ
# =================================================
FONT_PATH = "fonts/Roboto-Regular.ttf"

font_month = ImageFont.truetype(
    FONT_PATH,
    int(23 * SCALE * QUALITY_SCALE)
)

font_weekday = ImageFont.truetype(
    FONT_PATH,
    int(15 * SCALE * QUALITY_SCALE)
)

font_footer = ImageFont.truetype(
    FONT_PATH,
    int(16 * SCALE * FOOTER_SCALE * QUALITY_SCALE)
)


# =================================================
# ДАННЫЕ МЕСЯЦЕВ И ДНЕЙ НЕДЕЛИ
# =================================================
months = [
    ("ЯНВАРЬ", 1), ("ФЕВРАЛЬ", 2), ("МАРТ", 3),
    ("АПРЕЛЬ", 4), ("МАЙ", 5), ("ИЮНЬ", 6),
    ("ИЮЛЬ", 7), ("АВГУСТ", 8), ("СЕНТЯБРЬ", 9),
    ("ОКТЯБРЬ", 10), ("НОЯБРЬ", 11), ("ДЕКАБРЬ", 12),
]

weekdays = ["ПН", "ВТ", "СР", "ЧТ", "ПТ", "СБ", "ВС"]


# =================================================
# ПАРАМЕТРЫ СЕТКИ
# =================================================
COLS = 3
ROWS = 4

DOT_SIZE = int(14 * SCALE * QUALITY_SCALE)
DOT_GAP = int(12 * SCALE * QUALITY_SCALE)
LINE_GAP = int(10 * SCALE * QUALITY_SCALE)

TITLE_HEIGHT = int(34 * SCALE * QUALITY_SCALE)
WEEKDAY_HEIGHT = int(20 * SCALE * QUALITY_SCALE)

H_GAP = int(36 * SCALE * QUALITY_SCALE)
V_GAP = int(44 * SCALE * QUALITY_SCALE)

MONTH_CONTENT_WIDTH = 7 * (DOT_SIZE + DOT_GAP)
CELL_WIDTH = MONTH_CONTENT_WIDTH
CELL_HEIGHT = int(200 * SCALE * QUALITY_SCALE)


# =================================================
# ЦЕНТРИРОВАНИЕ ВСЕЙ СЕТКИ
# =================================================
GRID_WIDTH = COLS * CELL_WIDTH + (COLS - 1) * H_GAP
GRID_HEIGHT = ROWS * CELL_HEIGHT + (ROWS - 1) * V_GAP

START_X = int((WIDTH - GRID_WIDTH) // 2)
START_Y = int((HEIGHT - GRID_HEIGHT) // 2 + VERTICAL_SHIFT)


# =================================================
# ТЕКУЩАЯ ДАТА С TZ И РАННИМ ПЕРЕКЛЮЧЕНИЕМ ДНЯ
# =================================================
TZ = timezone(timedelta(hours=3))  # ← поменяй при необходимости
CUTOFF = time(23, 55)

now = datetime.now(TZ)

if now.time() >= CUTOFF:
    today = (now + timedelta(days=1)).date()
else:
    today = now.date()

print("SERVER NOW:", now.isoformat())
print("EFFECTIVE DAY:", today.isoformat())


# =================================================
# ПРОГРЕСС ГОДА
# =================================================
if today.year < YEAR:
    day_of_year = 0
elif today.year > YEAR:
    day_of_year = TOTAL_DAYS
else:
    day_of_year = today.timetuple().tm_yday

remaining_days = TOTAL_DAYS - day_of_year
progress_percent = int((day_of_year / TOTAL_DAYS) * 100)


# =================================================
# ОТРИСОВКА КАЛЕНДАРЯ
# =================================================
for i, (month_name, month_num) in enumerate(months):

    col = i % COLS
    row = i // COLS

    x0 = int(START_X + col * (CELL_WIDTH + H_GAP))
    y0 = int(START_Y + row * (CELL_HEIGHT + V_GAP))

    bbox = draw.textbbox((0, 0), month_name, font=font_month)
    title_w = bbox[2] - bbox[0]

    draw.text(
        (int(x0 + (CELL_WIDTH - title_w) // 2), y0),
        month_name,
        fill=WHITE,
        font=font_month
    )

    wx = int(x0)
    wy = int(y0 + TITLE_HEIGHT)

    for idx, wd in enumerate(weekdays):
        color = RED if idx >= 5 else WHITE
        draw_text_crisp(draw, (wx, wy), wd, font_weekday, color, BG)
        wx += DOT_SIZE + DOT_GAP

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


# =================================================
# ПРОГРЕСС ГОДА (НИЗ ЭКРАНА)
# =================================================
def plural_days(n: int) -> str:
    if 11 <= n % 100 <= 14:
        return "дней"
    last = n % 10
    if last == 1:
        return "день"
    if 2 <= last <= 4:
        return "дня"
    return "дней"


text_left = f"Осталось {remaining_days} {plural_days(remaining_days)}"
text_right = f" · {progress_percent}%"

bbox_l = draw.textbbox((0, 0), text_left, font=font_footer)
bbox_r = draw.textbbox((0, 0), text_right, font=font_footer)

total_w = bbox_l[2] - bbox_l[0] + bbox_r[2] - bbox_r[0]

fx = int((WIDTH - total_w) // 2)
fy = int(START_Y + GRID_HEIGHT + 48 * SCALE * QUALITY_SCALE)

draw.text((fx, fy), text_left, fill=WHITE, font=font_footer)
draw.text((fx + (bbox_l[2] - bbox_l[0]), fy), text_right, fill=WHITE, font=font_footer)


# =================================================
# ФИНАЛЬНЫЙ DOWNSCALE + СОХРАНЕНИЕ
# =================================================
final_img = img.resize(
    (FINAL_WIDTH, FINAL_HEIGHT),
    resample=Image.LANCZOS
)

output_dir = "output"
os.makedirs(output_dir, exist_ok=True)

output_path = os.path.join(output_dir, "wallpaper.png")

meta = PngInfo()
meta.add_text("generated_at", now.isoformat())
meta.add_text("effective_day", today.isoformat())

final_img.save(
    output_path,
    pnginfo=meta,
    optimize=False
)

print("Готово:", output_path)
