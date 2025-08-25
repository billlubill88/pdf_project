import os
import json
import fitz  # PyMuPDF
import torch
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageDraw, ImageFont
from tqdm import tqdm
from transformers import LayoutLMv3Processor, LayoutLMv3ForTokenClassification
from timer import Timer

MODEL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "layoutlmv3-trained"))
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "outputs_selected")
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def select_files():
    root = tk.Tk()
    root.withdraw()
    file_paths = filedialog.askopenfilenames(
        title="Выберите PDF или PNG для инференса",
        filetypes=[("PDF/PNG files", "*.pdf *.png *.jpg *.jpeg")]
    )
    return list(file_paths)

import os
import fitz  # PyMuPDF
from PIL import Image
import time

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "outputs_selected")

def pdf_to_images(pdf_path, dpi=200):
    """
    Конвертирует все страницы PDF в PNG, очищая старые tmp-файлы.
    Возвращает список путей к изображениям.
    """
    pdf_base = os.path.splitext(os.path.basename(pdf_path))[0]
    if os.path.exists(OUTPUT_DIR):
        # Очищаем только старые tmp-файлы, относящиеся к текущему PDF
        for fname in os.listdir(OUTPUT_DIR):
            if fname.startswith(f"tmp_{pdf_base}_page_") and fname.endswith(".png"):
                try:
                    os.remove(os.path.join(OUTPUT_DIR, fname))
                except Exception:
                    pass  # Иногда Windows блокирует файл — пропускаем

    # Рендер новых страниц
    doc = fitz.open(pdf_path)
    page_imgs = []
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for i in range(doc.page_count):
        page = doc[i]
        pix = page.get_pixmap(dpi=dpi)
        img_path = os.path.join(
            OUTPUT_DIR,
            f"tmp_{pdf_base}_page_{i}.png"
        )
        # Чтобы избежать блокировки, делаем несколько действий:
        pix.save(img_path)  # сохраняем на диск
        time.sleep(0.05)    # ждём освобождения файла (Windows fix)
        # Открываем и сразу закрываем (это полностью выгружает из файловой системы)
        try:
            with Image.open(img_path) as im:
                im.load()
        except Exception as ex:
            print(f"Не удалось полностью выгрузить {img_path}: {ex}")
        page_imgs.append(img_path)
    doc.close()  # обязательно закрываем pdf-документ
    return page_imgs

def extract_words_and_boxes(image_path):
    import pytesseract
    with Image.open(image_path) as img:
        data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT, lang="eng+rus")
    data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT, lang="eng+rus")
    words, boxes = [], []
    for i, word in enumerate(data['text']):
        if word.strip() != "":
            x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
            bbox = [x, y, x + w, y + h]
            words.append(word)
            boxes.append(bbox)
    return words, boxes

def normalize_box(box, width, height):
    return [
        int(1000 * box[0] / width),
        int(1000 * box[1] / height),
        int(1000 * box[2] / width),
        int(1000 * box[3] / height),
    ]

def color_for_label(label):
    import random
    random.seed(hash(label) % 10000)
    return (random.randint(80,255), random.randint(80,255), random.randint(80,255))

def draw_legend(img, label2color, max_width):
    font_size = 20
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()
    padding = 8
    margin = 10
    x, y = margin, margin
    max_h = font_size + 2 * padding
    items = sorted(label2color.items())
    blocks = []
    line_h = max_h
    for label, color in items:
        text = str(label)
        box_w = font_size + 2*padding
        text_w = font.getbbox(text)[2]
        block_w = box_w + 5 + text_w + margin
        if x + block_w > max_width:
            x = margin
            y += line_h + margin
        blocks.append((x, y, color, text, box_w, text_w))
        x += block_w
    legend_h = y + line_h + margin
    new_img = Image.new("RGBA", (img.width, img.height + legend_h), "white")
    new_img.paste(img, (0,0))
    draw = ImageDraw.Draw(new_img)
    for x, y, color, text, box_w, text_w in blocks:
        draw.rectangle([x, y + img.height, x + box_w, y + img.height + font_size + padding], fill=color)
        draw.text((x + box_w + 5, y + img.height + padding // 2), text, fill="black", font=font)
    return new_img

def predict_selected_files():
    selected_files = select_files()
    if not selected_files:
        print("Файлы не выбраны.")
        return

    with Timer("Время выполнения гадания"):
        print(f"Загружаю модель из {MODEL_DIR}")
        processor = LayoutLMv3Processor.from_pretrained(MODEL_DIR)
        model = LayoutLMv3ForTokenClassification.from_pretrained(MODEL_DIR).to(DEVICE)
        id2label = model.config.id2label

        os.makedirs(OUTPUT_DIR, exist_ok=True)

        for file_path in tqdm(selected_files, desc="Документы"):
            file_name = os.path.splitext(os.path.basename(file_path))[0]
            print(f"\nДокумент: {file_name}")

            # --- Получаем список изображений-страниц
            created_temp_files = []
            if file_path.lower().endswith(".pdf"):
                page_imgs = pdf_to_images(file_path)
                created_temp_files.extend(page_imgs)
            else:
                page_imgs = [file_path]

            print(f"Всего страниц: {len(page_imgs)}")
            for page_num, img_path in tqdm(list(enumerate(page_imgs)), total=len(page_imgs), desc=f"Страницы в {file_name}", leave=False):
                print(f"  [Страница {page_num+1}/{len(page_imgs)}] Обработка начата...")
                img = Image.open(img_path)
                width, height = img.size

                # --- OCR
                words, boxes = extract_words_and_boxes(img_path)
                if not words:
                    print(f"    Нет текста на странице {page_num} файла {file_name}")
                    continue
                norm_boxes = [normalize_box(box, width, height) for box in boxes]
                labels = ["O"] * len(words)

                # --- Нарезка на чанки <=512 токенов (по словам, а не по токенам)
                max_words_in_chunk = 200  # безопасно до 512 токенов
                chunks = []
                for i in range(0, len(words), max_words_in_chunk):
                    chunks.append((words[i:i+max_words_in_chunk],
                                   norm_boxes[i:i+max_words_in_chunk],
                                   list(range(i, min(i+max_words_in_chunk, len(words))))))
                    print(f"===> Новый чанк (total {len(chunks)}): {len(words[i:i+max_words_in_chunk])} слов. Индексы слов: {i}-{min(i+max_words_in_chunk-1, len(words)-1)}")

                print(f"    Нарезано {len(chunks)} чанков, слов на странице: {len(words)}")

                # --- Инференс по чанкам (прогресс)
                preds_by_word = {}
                for i, (chunk_words, chunk_boxes, chunk_word_ids) in enumerate(chunks):
                    print(f"      Инференс чанка {i+1}/{len(chunks)} ({len(chunk_words)} слов)")
                    encoding = processor(
                        text=chunk_words,
                        images=img,
                        boxes=chunk_boxes,
                        word_labels=None,
                        truncation=True,
                        padding="max_length",
                        max_length=512,
                        return_tensors="pt"
                    )
                    for k in encoding:
                        encoding[k] = encoding[k].to(DEVICE)
                    with torch.no_grad():
                        outputs = model(**encoding)
                        logits = outputs.logits
                        predictions = torch.argmax(logits, dim=-1).cpu().numpy()[0]
                    word_ids = encoding.word_ids(batch_index=0)
                    already_labeled = set()
                    for idx, word_id in enumerate(word_ids):
                        if word_id is not None and word_id not in already_labeled and word_id < len(chunk_word_ids):
                            pred_label_id = predictions[idx]
                            pred_label = id2label[pred_label_id]
                            preds_by_word[chunk_word_ids[word_id]] = pred_label
                            already_labeled.add(word_id)

                # --- Визуализация всей страницы
                vis_img = img.convert("RGBA")
                draw = ImageDraw.Draw(vis_img)
                found_labels = set()
                label2color = {}
                for idx, box in enumerate(boxes):
                    label = preds_by_word.get(idx, "O")
                    if label != "O":
                        found_labels.add(label)
                        if label not in label2color:
                            label2color[label] = color_for_label(label)
                        color = label2color[label]
                        draw.rectangle(box, outline=color, width=3)
                        try:
                            draw.text((box[0]+2, box[1]+2), label, fill=color)
                        except Exception:
                            pass
                # --- Легенда
                if found_labels:
                    vis_img = draw_legend(vis_img, label2color, max_width=img.width)

                # --- Сохраняем PNG и JSON
                vis_path = os.path.join(OUTPUT_DIR, f"{file_name}_page_{page_num}_pred.png")
                vis_img.save(vis_path)
                print(f"    Визуализация сохранена: {vis_path} (найдено сущностей: {len(found_labels)})")

                results_json = {
                    "file": file_path,
                    "page": page_num,
                    "image_path": img_path,
                    "width": width,
                    "height": height,
                    "words": words,
                    "bboxes": boxes,
                    "labels": [preds_by_word.get(idx, "O") for idx in range(len(words))]
                }
                json_path = os.path.join(OUTPUT_DIR, f"{file_name}_page_{page_num}_pred.json")
                with open(json_path, "w", encoding="utf-8") as f:
                    json.dump(results_json, f, ensure_ascii=False, indent=2)
                print(f"    JSON с результатами: {json_path}")

            # --- Удаляем ВСЕ временные изображения
            for temp_file in created_temp_files:
                try:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                        print(f"Удалено временное изображение: {temp_file}")
                except Exception as e:
                    print(f"Не удалось удалить временный файл: {temp_file} ({e})")

        print(f"\nГотово! Итоги смотри в {OUTPUT_DIR}/")

def crop_and_save_block(img, box, save_path):
    x0, y0, x1, y1 = map(int, box)
    cropped = img.crop((x0, y0, x1, y1))
    cropped.save(save_path)

def visualize_full_ml_predictions(img_path, words, boxes, preds_by_word, id2label, save_path):
    from PIL import ImageDraw, ImageFont
    img = Image.open(img_path).convert("RGBA")
    draw = ImageDraw.Draw(img)
    found_labels = set()
    label2color = {}
    for idx, box in enumerate(boxes):
        label = preds_by_word.get(idx, "O")
        if label != "O":
            found_labels.add(label)
            if label not in label2color:
                label2color[label] = color_for_label(label)
            color = label2color[label]
            draw.rectangle(box, outline=color, width=3)
            try:
                draw.text((box[0]+2, box[1]+2), str(label), fill=color)
            except Exception:
                pass
    if found_labels:
        img = draw_legend(img, label2color, max_width=img.width)
    img.save(save_path)
    return save_path

if __name__ == "__main__":
    predict_selected_files()
