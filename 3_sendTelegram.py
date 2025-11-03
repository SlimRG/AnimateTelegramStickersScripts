import os
import math
import requests
import ffmpeg  # ffmpeg-python library
from pathlib import Path

# === Конфигурационные константы (заполните под свои условия) ===
INPUT_DIR = r"D:/Experiments/AnimateStickers/astickers"       # Путь для сохранения .webm стикеров

# !!! ВЫ ДОЛЖНЫ СПЕРВА ЗАЙТИ В БОТ и ВВЕСТИ /start !!!!
BOT_TOKEN = "****"              # Токен Telegram-бота

USER_ID = 12345678                            # Ваш Telegram User ID (целое число)
PACK_NAME = "animated_ovsa"           # Короткое имя стикерпакета (должно заканчиваться на _by_имябота)
PACK_TITLE = "Animated Стикеры с Овсянкой"           # Заголовок набора стикеров
STICKER_EMOJI = "🎞️"                          # Эмоджи, присваиваемый по умолчанию всем стикерам

# Создаём выходную директорию, если не существует
Path(INPUT_DIR).mkdir(parents=True, exist_ok=True)

# Получаем список всех MKV-файлов в директории
input_paths = [p for p in Path(INPUT_DIR).glob("**/*.webm") if p.is_file()]
if not input_paths:
    print("Нет файлов .webm в директории:", INPUT_DIR)
    exit(1)

# Optionally: получаем имя бота (для проверки имени пакета)
bot_username = None
try:
    resp = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getMe", timeout=10)
    data = resp.json()
    if data.get("ok"):
        bot_username = data["result"]["username"]
except Exception as e:
    print("Предупреждение: не удалось получить имя бота через getMe:", e)

# Проверка соответствия PACK_NAME требуемому формату
if bot_username:
    required_suffix = f"_by_{bot_username}".lower()
    if not PACK_NAME.lower().endswith(required_suffix):
        print(f"Имя набора '{PACK_NAME}' не оканчивается на {required_suffix}! Исправляем автоматически.")
        PACK_NAME = (PACK_NAME + required_suffix) if not PACK_NAME.endswith(required_suffix) else PACK_NAME
# Ограничение длины имени набора
if len(PACK_NAME) > 64:
    PACK_NAME = PACK_NAME[:64]
    print("Предупреждение: PACK_NAME урезано до 64 символов:", PACK_NAME)

# Конвертируем все файлы в директории
sticker_files = input_paths

# Создаём новый стикерпак через Bot API
api_url = f"https://api.telegram.org/bot{BOT_TOKEN}"
# Первым запросом – создаём набор с первым стикером
first_sticker = sticker_files[0]
try:
    with open(first_sticker, "rb") as f:
        files = {"webm_sticker": f}
        data = {
            "user_id": USER_ID,
            "name": PACK_NAME,
            "title": PACK_TITLE,
            "emojis": STICKER_EMOJI
        }
        resp = requests.post(api_url + "/createNewStickerSet", data=data, files=files, timeout=20)
        result = resp.json()
        if not result.get("ok"):
            print("Ошибка при создании набора стикеров:", result)
            exit(1)
        else:
            print("Стикерпак успешно создан:", PACK_NAME)
except Exception as e:
    print("Исключение при создании стикерпакета:", e)
    exit(1)

# Добавляем остальные стикеры в набор
for sticker_path in sticker_files[1:]:
    try:
        with open(sticker_path, "rb") as f:
            files = {"webm_sticker": f}
            data = {
                "user_id": USER_ID,
                "name": PACK_NAME,
                "emojis": STICKER_EMOJI
            }
            resp = requests.post(api_url + "/addStickerToSet", data=data, files=files, timeout=20)
            result = resp.json()
            if not result.get("ok"):
                print(f"Ошибка при добавлении стикера {sticker_path.name}: {result}")
            else:
                print(f"Добавлен стикер: {sticker_path.name}")
    except Exception as e:
        print(f"Исключение при добавлении стикера {sticker_path.name}:", e)

print("Готово! Добавьте новый набор в Telegram по ссылке:")
print(f"https://t.me/addstickers/{PACK_NAME}")
