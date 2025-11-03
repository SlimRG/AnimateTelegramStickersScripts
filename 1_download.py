from telethon import TelegramClient
from telethon.tl.functions.messages import GetStickerSetRequest
from telethon.tl.types import InputStickerSetShortName
from PIL import Image
import os

# 🔑 Вставь свои данные с my.telegram.org
api_id = 12536658    # твои данные с my.telegram.org
api_hash = "***"

# 📂 Путь для сохранения стикеров (замени на нужный)
save_path = r"D:/Experiments/AnimateStickers/stickier_pack_name"

# Создаём клиент
client = TelegramClient("stickers", api_id, api_hash)

async def download_pack(url):
    # Создаём папку, если её нет
    os.makedirs(save_path, exist_ok=True)

    # Получаем имя пака (последняя часть URL)
    short_name = url.split("/")[-1]

    # Запрашиваем стикерпак
    pack = await client(GetStickerSetRequest(
        stickerset=InputStickerSetShortName(short_name=short_name),
        hash=0
    ))

    # Скачиваем все стикеры
    for i, doc in enumerate(pack.documents, 1):
        file_path = os.path.join(save_path, f"sticker_{i}.webp")
        await client.download_media(doc, file_path)

        # Конвертируем WEBP → PNG
        png_path = file_path.replace(".webp", ".png")
        with Image.open(file_path).convert("RGBA") as im:
            im.save(png_path)

        print(f"✅ {png_path}")

with client:
    client.loop.run_until_complete(download_pack("https://t.me/addstickers/ovsyaloid_price"))
