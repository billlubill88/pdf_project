import os
from PIL import Image
from core.ml_predictor import (
    pdf_to_images,
    extract_words_and_boxes,
    normalize_box,
    crop_and_save_block,
    MODEL_DIR,
    DEVICE,
)
from transformers import LayoutLMv3Processor, LayoutLMv3ForTokenClassification
import torch

RIDER_LABELS = {
    12: "Container Numbers",
    13: "Description of Goods",
    14: "Gross Weight",
    15: "No OF PCKGS",
    16: "No of pallets"
}

def extract_ml_title_blocks(pred_blocks, page_num):
    """
    Возвращает только title-блоки (num от 0 до 11 включительно)
    """
    title_blocks = []
    for block in pred_blocks:
        if block.get('num') is not None and 0 <= int(block['num']) <= 11:
            block['page'] = page_num
            title_blocks.append(block)
    return title_blocks

def extract_ml_rider_blocks(pred_blocks, page_num):
    """
    Возвращает только rider-блоки (num == 12, 13, 14, 15, 16)
    """
    rider_blocks = []
    for block in pred_blocks:
        num = block.get('num')
        if num is not None and int(num) in RIDER_LABELS:
            block['page'] = page_num
            block['name'] = RIDER_LABELS[int(num)] + f" ({page_num})"
            rider_blocks.append(block)
    return rider_blocks

def extract_blocks_from_pdf_page(pdf_path, page_num=0, crop_dir="output/cropped_blocks", visualize=True, visualize_full_page=True):
    """
    Возвращает список блоков ML для одной страницы PDF (без json).
    Аргумент visualize отвечает за сохранение PNG-обрезок блоков.
    Аргумент visualize_full_page — сохранять ли визуализацию всех предсказаний на целой странице.
    """
    from core.ml_predictor import visualize_full_ml_predictions  # импорт здесь для избежания циклов

    img_paths = pdf_to_images(pdf_path)
    img_path = img_paths[page_num]
    with Image.open(img_path).convert("RGB") as img:
        width, height = img.size
        
        # 2. OCR и боксы (absolute)
        words, boxes = extract_words_and_boxes(img_path)
        norm_boxes = [normalize_box(box, width, height) for box in boxes]

        # 3. Инициализация модели
        processor = LayoutLMv3Processor.from_pretrained(MODEL_DIR)
        model = LayoutLMv3ForTokenClassification.from_pretrained(MODEL_DIR).to(DEVICE)
        id2label = model.config.id2label

        # 4. Инференс чанками
        max_words_in_chunk = 200
        preds_by_word = {}
        for i in range(0, len(words), max_words_in_chunk):
            chunk_words = words[i:i+max_words_in_chunk]
            chunk_boxes = norm_boxes[i:i+max_words_in_chunk]
            chunk_word_ids = list(range(i, min(i+max_words_in_chunk, len(words))))
            encoding = processor(
                text=chunk_words,
                images=[img],
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

        # --- Сохраняем полную визуализацию страницы
        if visualize and visualize_full_page:
            file_base = os.path.splitext(os.path.basename(pdf_path))[0]
            save_path = os.path.join(os.path.dirname(img_path), f"{file_base}_page_{page_num}_pred.png")
            visualize_full_ml_predictions(img_path, words, boxes, preds_by_word, id2label, save_path)

        # 5. Группируем слова с одинаковыми лейблами в один блок
        label_blocks = {}
        for idx, (word, bbox) in enumerate(zip(words, boxes)):
            label = preds_by_word.get(idx, "O")
            if label == "O":
                continue
            try:
                label_id = int(label)
            except Exception:
                continue  # skip нечисловые лейблы
            if label_id not in label_blocks:
                label_blocks[label_id] = {"words": [], "bboxes": []}
            label_blocks[label_id]["words"].append(word)
            label_blocks[label_id]["bboxes"].append(bbox)

        # 6. Формируем список блоков
        results = []
        if visualize:
            os.makedirs(crop_dir, exist_ok=True)
        for label_id in sorted(label_blocks.keys()):
            group = label_blocks[label_id]
            if 0 <= label_id <= 11:
                page_type = "TITLE"
            elif 12 <= label_id <= 16:
                page_type = "RIDER"
            else:
                continue
            num = label_id

            x0 = min([b[0] for b in group["bboxes"]])
            y0 = min([b[1] for b in group["bboxes"]])
            x1 = max([b[2] for b in group["bboxes"]])
            y1 = max([b[3] for b in group["bboxes"]])
            coordinates = (x0, y0, x1, y1)
            text = " ".join(group["words"])

            crop_path = None
            if visualize:
                crop_name = f"{page_type}_block_{num}_page_{page_num+1}.png"
                crop_path = os.path.join(crop_dir, crop_name)
                try:
                    crop_and_save_block(img, coordinates, crop_path)
                except Exception:
                    crop_path = None

            left_pct = x0 * 100 / width
            top_pct = y0 * 100 / height
            right_pct = x1 * 100 / width
            bottom_pct = y1 * 100 / height

            block = {
                "name": f"{page_type}_{num}" if num not in RIDER_LABELS else RIDER_LABELS[num],
                "num": num,
                "value": text,
                "coordinates": coordinates,
                "page_type": page_type,
                "page": page_num + 1,
                "image_path": crop_path,
                "left_pct": left_pct,
                "top_pct": top_pct,
                "right_pct": right_pct,
                "bottom_pct": bottom_pct
            }
            results.append(block)

        return results
