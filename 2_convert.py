import os
import asyncio
import ffmpeg
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm  # добавлен tqdm

# === Константы ===
INPUT_DIR = Path(r"D:/Experiments/AnimateStickers/makes")        # Путь к директории с mp4-видео
OUTPUT_DIR = Path(r"D:/Experiments/AnimateStickers/astickers")   # Путь для сохранения .webm стикеров
MAX_WORKERS = 36  # максимальное число потоков конвертации

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def convert_file(input_path: Path) -> None:
    try:
        info = ffmpeg.probe(str(input_path))
        vs = [s for s in info['streams'] if s['codec_type'] == 'video']
        if not vs:
            print(f"[SKIP] {input_path.name} — не найден видео-поток")
            return
        stream = vs[0]
        width = int(stream.get('width', 0))
        height = int(stream.get('height', 0))
        duration = float(stream.get('duration', 0.0))
        fr_num, fr_den = stream.get('avg_frame_rate', '0/1').split('/')
        fps = float(fr_num) / float(fr_den) if float(fr_den) != 0 else 0.0

        if width >= height:
            target_w = 512
            target_h = round(height * 512 / width)
        else:
            target_h = 512
            target_w = round(width * 512 / height)

        if width <= 512 and height <= 512:
            if width >= height:
                target_w = 512
                target_h = round(height * 512 / width)
            else:
                target_h = 512
                target_w = round(width * 512 / height)

        output_path = OUTPUT_DIR / (input_path.stem + ".webm")

        video = ffmpeg.input(str(input_path)).video
        video = video.filter('scale', target_w, target_h, flags='lanczos')
        if fps > 30:
            video = video.filter('fps', fps=30, round='down')
        if duration > 3.0:
            speed = duration / 3.0
            video = video.filter('setpts', f"{1/speed}*PTS")

        attempts = range(18, 50)
        success = False
        max_size = 256 * 1024
        for crf in attempts:
            kwargs = {
                'format': 'webm',
                'c:v': 'libvpx-vp9',
                'pix_fmt': 'yuv420p',
                'an': None,
                'crf': str(crf),
                'b:v': '0'
            }
            ffmpeg.output(video, str(output_path), **kwargs).overwrite_output().run(quiet=True)
            size = output_path.stat().st_size
            if size <= max_size:
                print(f"[OK] {input_path.name} (CRF={crf}, {size} bytes)")
                success = True
                break
        if not success:
            print(f"[FAIL] {input_path.name} — не удалось уложиться в 256 КБ")
            if output_path.exists():
                output_path.unlink()
    except Exception as e:
        print(f"[ERROR] {input_path.name} — {e}")

def main():
    files = [p for p in INPUT_DIR.rglob("*.mp4") if p.is_file()]
    if not files:
        print("Нет .mp4 файлов для конвертации.")
        return

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(convert_file, f) for f in files]
        for _ in tqdm(as_completed(futures), total=len(futures), desc="Конвертация", ncols=80):
            pass

    print("Все файлы обработаны.")

if __name__ == "__main__":
    main()
