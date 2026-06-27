from customtkinter import *
from tkinter import PhotoImage
from pygame import mixer, event, USEREVENT
import pygame
from random import randint
import time

from threading import Thread
import json
import xdialog
from googletrans import Translator, LANGUAGES
import google.generativeai as genai
import requests
import os, re
import platform

pygame.init()
mixer.init()
MUSIC_END = USEREVENT+1
backsound_volume = 100
sfx_volume = 100
mixer.music.set_endevent(MUSIC_END)
mixer.music.set_volume(sfx_volume)
random_background_music = randint(1,4)
if random_background_music == 1:
    mixer.music.load('backsound/idle_music.mp3')
    mixer.music.play()
elif random_background_music == 2:
    mixer.music.load('backsound/Ever_Higher.mp3')
    mixer.music.play(loops=2)
elif random_background_music == 3:
    mixer.music.load('backsound/12am.mp3')
    mixer.music.play(loops=2)
elif random_background_music == 4:
    mixer.music.load('backsound/13am.mp3')
    mixer.music.play()

done_sfx = mixer.Sound('sound/done.wav')
done_sfx.set_volume(sfx_volume)

error_sfx = mixer.Sound('sound/error.wav')
error_sfx.set_volume(sfx_volume)

des = CTk()
des.title('Deltarune translator')
des.geometry('800x500')
des.resizable(False, False)

CTkLabel(des, image=PhotoImage(file='images/background.png'), text='').place(x=0,y=0)

action_start = 'translate'
music_looped = True
total_lines = 0
translated_lines = 0
translator = Translator()

translated_lines_math = 0

yandex_api = 'Enter'
yandex_folder_api = 'Enter'
gemini_api = 'Enter'

def music_loop():
    if music_looped == True:
        for eventd in event.get():
            if eventd.type == MUSIC_END:
                des.after(500)
                random_background_music = randint(1,4)
                if random_background_music == 1:
                    mixer.music.load('backsound/idle_music.mp3')
                    mixer.music.play()
                elif random_background_music == 2:
                    mixer.music.load('backsound/Ever_Higher.mp3')
                    mixer.music.play(loops=2)
                elif random_background_music == 3:
                    mixer.music.load('backsound/12am.mp3')
                    mixer.music.play(loops=2)
                elif random_background_music == 4:
                    mixer.music.load('backsound/13am.mp3')
                    mixer.music.play()
        des.after(1000, music_loop)  
    else:
        return False
des.after(50, music_loop)

def clopen_log():
    if log_button._text == 'Log':
        vol_button.configure(state='disabled')
        log_button.configure(text='/')
        des.update()
        des.after(200)
        log_button.configure(text='-')
        main_frame.place_forget()
        des.update()
        des.after(200)
        log_button.configure(text='X')
        log_frame.place(x=20,y=20)
        des.update()
    elif log_button._text == 'X':
        log_button.configure(text='/')
        des.update()
        des.after(200)
        log_button.configure(text='-')
        log_frame.place_forget()
        des.update()
        des.after(200)
        log_button.configure(text='Log')
        vol_button.configure(state='normal')
        main_frame.place(x=20,y=20)
        des.update()

def clopen_volume():
    if vol_button._text == 'Volume':
        log_button.configure(state='disabled')
        vol_button.configure(text='/')
        des.update()
        des.after(200)
        vol_button.configure(text='-')
        main_frame.place_forget()
        des.update()
        des.after(200)
        vol_button.configure(text='X')
        setvol_frame.place(x=20,y=20)
        des.update()
    elif vol_button._text == 'X':
        vol_button.configure(text='/')
        des.update()
        des.after(200)
        vol_button.configure(text='-')
        setvol_frame.place_forget()
        des.update()
        des.after(200)
        vol_button.configure(text='Volume')
        log_button.configure(state='normal')
        main_frame.place(x=20,y=20)
        des.update()

def change_background_volume(value):
    global backsound_volume
    
    backsound_volume = value
    mixer.music.set_volume(backsound_volume)

    setvol_background_music_int.configure(text=int(backsound_volume*100))
    des.update()

def change_effect_volume(value):
    global sfx_volume

    done_sfx.set_volume(sfx_volume)
    error_sfx.set_volume(sfx_volume)

    sfx_volume = value
    setvol_effect_music_int.configure(text=int(sfx_volume*100))
    des.update()

def change_source_lang():
    try:
        source_file_frame_textbox.delete()
    except:
        pass
    try:
        target_file_frame_textbox.delete()
    except:
        pass
    set_lang = xdialog.open_file('Open DELTARUNE Languages file', filetypes=[("Lang file", "*.json")])
    source_file_frame_textbox.delete(0, 'end')
    target_file_frame_textbox.delete(0, 'end')
    source_file_frame_textbox.insert('end', set_lang)

    dir_name, file_name = os.path.split(set_lang)
    target_name = f"{os.path.splitext(file_name)[0]}_translated.json"

    target_file_frame_textbox.insert('end', os.path.join(dir_name, target_name))

def change_target_lang():
    try:
        target_file_frame_textbox.delete()
    except:
        pass
    set_lang = xdialog.save_file('Open DELTARUNE Languages file', filetypes=[("Lang file", "*.json")])
    target_file_frame_textbox.delete(0, 'end')
    target_file_frame_textbox.insert('end', set_lang)

def detect_lang_simple(text):
    """
    Быстрое определение языка строки без внешних библиотек.
    Смотрит на Unicode-блоки символов в тексте.
    """
    # Убираем управляющие коды и знаки препинания — смотрим только на буквы
    clean = re.sub(r'\\[A-Za-z0-9]+|\^[0-9]+|[/\\%&^0-9\s\W]', '', text)
    if not clean:
        return None

    counts = {
        'ja': len(re.findall(r'[\u3040-\u309F\u30A0-\u30FF]', clean)),
        'ru': len(re.findall(r'[\u0400-\u04FF]', clean)),
        'ko': len(re.findall(r'[\uAC00-\uD7AF\u1100-\u11FF]', clean)),
        'ar': len(re.findall(r'[\u0600-\u06FF]', clean)),
        'zh': len(re.findall(r'[\u4E00-\u9FFF]', clean)),
        'el': len(re.findall(r'[\u0370-\u03FF]', clean)),
        'he': len(re.findall(r'[\u0590-\u05FF]', clean)),
        'th': len(re.findall(r'[\u0E00-\u0E7F]', clean)),
        'latin': len(re.findall(r'[A-Za-z\u00C0-\u024F]', clean)),
    }

    dominant = max(counts, key=counts.get)
    if counts[dominant] == 0:
        return None
    return dominant

# Таблица: код языка из googletrans -> что вернёт detect_lang_simple
LANG_TO_SCRIPT = {
    'ja': 'ja', 'zh-cn': 'zh', 'zh-tw': 'zh', 'ko': 'ko',
    'ru': 'ru', 'uk': 'ru', 'bg': 'ru',
    'ar': 'ar', 'he': 'he', 'el': 'el', 'th': 'th',
    # Все латинские языки (en, de, fr, es, it, pl, pt, nl, sv...):
    # отсутствие в таблице -> 'latin'
}

def should_translate(key, value, source_lang=None):
    if key == "date":
        return False
    if not isinstance(value, str):
        return False
    if not value.strip():
        return False

    if source_lang is None:
        return True

    detected = detect_lang_simple(value)
    if detected is None:
        # Строка состоит только из кодов/цифр/пунктуации — пропускаем
        return False

    expected_script = LANG_TO_SCRIPT.get(source_lang, 'latin')
    if expected_script == 'latin':
        # Если исходный язык латинский — переводим только латинские строки
        return detected == 'latin'
    else:
        return detected == expected_script

def update_progress():
    global translated_lines_math
    if total_lines > 0:
        translated_lines_math += 1
        if translated_lines_math == int(total_lines / 100):
            translated_lines_math = 0
            progress_progressbar.set(progress_progressbar.get() + 0.01)
        progress_text.configure(
            text=f"{translated_lines}/{total_lines}"
        )
        des.update_idletasks()

def extract_codes(text):
    """Извлекает все управляющие коды из строки."""
    return re.findall(r'\\[A-Za-z0-9]+|\^[0-9]+|/+%*|%%|&|\u3000|\\n', str(text))
 
def extract_critical_codes(text):
    """Извлекает только критичные коды, удаление которых ломает игру."""
    return re.findall(r'%%|&', str(text))

def restore_codes(original, translated):
    # Строгая проверка только критичных кодов (%% и &).
    # Остальные коды (^6, \M0 и т.д.) Gemini обычно сохраняет правильно,
    # поэтому требовать их точного совпадения слишком жёстко — это
    # была основная причина, по которой строки оставались японскими.
    orig_critical = extract_critical_codes(original)
    trans_critical = extract_critical_codes(translated)
    if orig_critical != trans_critical:
        return None
    return translated


def reassemble_text(original_structure, translated_texts_list):
    """
    Берет оригинальную структуру кодов и поочередно подставляет 
    переведенные куски текста вместо оригинальных.
    """
    result = ""
    text_idx = 0
    for item in original_structure:
        if item['type'] == 'code':
            result += item['val']
        else:
            if text_idx < len(translated_texts_list):
                result += translated_texts_list[text_idx]
                text_idx += 1
            else:
                result += item['val'] # Фолбэк на оригинал, если ИИ пропустил кусок
    return result

def safe_json_loads(text):
    """
    Парсит JSON из ответа Gemini, обрабатывая невалидные escape-последовательности.
    Gemini иногда возвращает \\M1, \\E0 и т.д. без двойного слеша,
    что является невалидным JSON. Эта функция исправляет это перед парсингом.
    """
    text = text.strip()
    # Убираем markdown-обёртку если есть
    if text.startswith("```"):
        text = re.sub(r'^```[a-z]*\n?', '', text)
        text = re.sub(r'\n?```$', '', text)
        text = text.strip()

    # Находим содержимое каждой JSON-строки и чиним невалидные backslash-escapes.
    # Валидные JSON escapes: \\ \" \/ \b \f \n \r \t \uXXXX — всё остальное экранируем.
    def fix_escapes(m):
        s = m.group(0)
        result = []
        i = 0
        while i < len(s):
            if s[i] == '\\' and i + 1 < len(s):
                nxt = s[i + 1]
                if nxt in '\\"' or nxt in '/bfnrtu':
                    result.append('\\')
                    result.append(nxt)
                    i += 2
                else:
                    result.append('\\\\')  # экранируем одиночный слеш
                    i += 1
            else:
                result.append(s[i])
                i += 1
        return ''.join(result)

    fixed = re.sub(r'(?<=": ")(?:[^\\"]|\\.)*(?=")', fix_escapes, text)
    result = json.loads(fixed)
    # Gemini иногда пишет буквально "\\u3000" как текст вместо реального символа.
    # Исправляем это после парсинга.
    if isinstance(result, dict):
        for k, v in result.items():
            if isinstance(v, str) and '\\u3000' in v:
                result[k] = v.replace('\\u3000', '\u3000')
    return result

def translate_process():
    global total_lines, translated_lines, music_looped, yandex_api, yandex_folder_api, gemini_api

    source_lang = lang_frame_source_combo.get()
    target_lang = lang_frame_target_combo.get()
    source_path = source_file_frame_textbox.get()
    target_path = target_file_frame_textbox.get()

    gemini_cache_keys = []
    gemini_cache_values = []

    if translator_api.get() == 1:
        inputer_api = CTkInputDialog(text="Yandex Translate API", title="Deltarune Translator")
        yandex_api = inputer_api.get_input()
        folder_id_api = CTkInputDialog(text="Yandex Translate Folder ID", title="Deltarune Translator")
        yandex_folder_api = folder_id_api.get_input()
    elif translator_api.get() == 2:
        inputer_api = CTkInputDialog(text="Gemini API Key\n(get free at aistudio.google.com)", title="Deltarune Translator")
        gemini_api = inputer_api.get_input()
        genai.configure(api_key=gemini_api)

    try:
        progress_text.configure(text='Checking lines from source file')
        des.update()
        with open(source_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        total_lines = 0
        translated_lines = 0

        for key, value in data.items():
            if should_translate(key, value, source_lang):
                total_lines += 1

        log_textbox.insert("0.0", f"Found {total_lines} lines to translate\n")
        update_progress()
        des.update()

        for key, value in data.items():
            if should_translate(key, value, source_lang):
                if translator_api.get() == 0:
                    try:
                        translated = translator.translate(
                        value,
                        src=source_lang,
                        dest=target_lang
                        ).text
                        data[key] = translated
                        translated_lines += 1

                        log_textbox.insert("0.0", f"{value} > {translated}\n")
                    except Exception as e:
                        error_sfx.play()
                        log_textbox.insert("0.0", f"Error translating {key}: {str(e)}\n")
                        translated_lines += 1
                elif translator_api.get() == 1:
                    try:
                        body = {
                            "targetLanguageCode": target_path,
                            "texts": value,
                            "folderId": yandex_folder_api,
                        }
                        headers = {
                            "Content-Type": "application/json",
                            "Authorization": "Api-Key {0}".format(yandex_api),
                        }
                        response = requests.post(
                            "https://translate.api.cloud.yandex.net/translate/v2/translate",
                            json=body,
                            headers=headers,
                        )
                        data[key] = response.text

                        translated_lines += 1

                        log_textbox.insert("0.0", f"{value} > {translated}\n")
                    except Exception as e:
                        error_sfx.play()
                        log_textbox.insert("0.0", f"Error translating {key}: {str(e)}\n")
                        translated_lines += 1
                elif translator_api.get() == 2:
                    gemini_cache_keys.append(key)
                    gemini_cache_values.append(value)
                    
                    log_textbox.insert("0.0", f"[В очереди] {value}\n")


                    if gemini_model_var.get() == 0:
                        if len(gemini_cache_values) >= 100 or (translated_lines + len(gemini_cache_values) >= total_lines):
                            try:
                                gemini_model = genai.GenerativeModel('gemini-3.1-flash-lite')
                                
                                # Подготавливаем структуры и чистый текст для отправки
                                batch_structures = []
                                texts_to_translate = []
                                
                                # Формируем словарь для отправки, чтобы ИИ видел контекст строк
                                payload = {f"str_{i}": val for i, val in enumerate(gemini_cache_values)}
                                
                                prompt = (
                                    f"You are a professional game translator specializing in Deltarune localization from {source_lang} to {target_lang}.\n"
                                    "CRITICAL RULES:\n"
                                    "- NEVER remove, alter, translate, or reorder ANY control codes. These include but are not limited to:\n"
                                    "  \\E0, \\E1, \\M0, \\M1, \\M2, ^0, ^1, ^2, ^3, ^4, ^5, ^6, ^7, ^8, ^9, /%, %%, %, &, /, \\n, \\t, and any other non-alphabetic sequences.\n"
                                    "- Control codes MUST retain their exact position relative to the surrounding text.\n"
                                    "- If a control code is at the start/end of a string, it MUST remain at the start/end in the translation.\n"
                                    "- If a control code is between words, it MUST stay between the translated words in the same order.\n\n"
                                    "TRANSLATION GUIDELINES:\n"
                                    "- Translate ONLY the human-readable text. Leave ALL codes untouched.\n"
                                    "- Preserve punctuation (？ → ?), spacing, and line breaks relative to the codes.\n"
                                    "- Character names MUST be translated as follows: \n"
                                    "  クリス=Крис, スージー=Сьюзи, ラルセイ=Ральсей, ノエル=Ноэль, ルルー=Рулу, ジャルグ=Джалг, ベリル=Берилл.\n"
                                    "- Maintain the original tone: casual, emotional, or formal, depending on the context.\n\n"
                                    "EXAMPLES:\n"
                                    'Original: "聞コエマスカ^6？\\M1 ^6 %"\n'
                                    'Correct: "Ты меня слышишь?^6?\\M1 ^6 %"\n'
                                    'Incorrect: "Ты меня слышишь? ^6? \\M1 ^6 %" (extra spaces) or "Ты меня слышишь?^6?\\M1 %" (missing code).\n\n'
                                    'Original: "^6 \\M0ワレワレハ^6& 接続サレテ& イマスカ^6？\\M1 ^6 ^6 %%"\n'
                                    'Correct: "^6 \\M0Мы^6& соединены?& Или нет?^6?\\M1 ^6 ^6 %%"\n'
                                    'Incorrect: "^6 \\M0 Мы ^6 & соединены & или нет? ^6? \\M1 ^6 ^6 %%" (spaces around codes).\n\n'
                                    "OUTPUT FORMAT:\n"
                                    "- Return ONLY a valid JSON object with the SAME keys as the input.\n"
                                    "- Do NOT add comments, explanations, or markdown formatting (e.g., no ```json).\n"
                                    "- Ensure the output is parseable as JSON. Escape special characters if necessary.\n\n"
                                    f"DATA TO TRANSLATE:\n{json.dumps(payload, ensure_ascii=False)}"
                                )
                                
                                response = gemini_model.generate_content(prompt)
                                response_text = response.text.strip()
                                
                                translated_obj = safe_json_loads(response_text)
                                
                                # Раскладываем перевод обратно в базу данных игры
                                for i, (b_key, orig_val) in enumerate(zip(gemini_cache_keys, gemini_cache_values)):
                                    key_id = f"str_{i}"
                                    trans_val = translated_obj.get(key_id, orig_val)
                                    
                                    # Финальная питоновская проверка на то, что ИИ не удалил важные коды (%% или &)
                                    fixed = restore_codes(orig_val, trans_val)
                                    if fixed is None:
                                        data[b_key] = orig_val
                                        log_textbox.insert("0.0", f"[!] Коды не совпали, оставлен оригинал: {orig_val}\n")
                                    else:
                                        data[b_key] = fixed
                                        log_textbox.insert("0.0", f"[Успех] {orig_val} -> {fixed}\n")
                                        
                                    translated_lines += 1

                                gemini_cache_keys = []
                                gemini_cache_values = []

                                if gemini_model_var.get() == 0:
                                    time.sleep(3.1)
                            except Exception as e:
                                error_sfx.play()
                                log_textbox.insert("0.0", f"Ошибка пакета Gemini: {str(e)}\nСкидываем пакет в оригиналы...\n")
                                for b_key, orig_val in zip(gemini_cache_keys, gemini_cache_values):
                                    data[b_key] = orig_val
                                    translated_lines += 1
                                gemini_cache_keys = []
                                gemini_cache_values = []
                                time.sleep(2.0)
                    else:
                        if len(gemini_cache_values) >= 600 or (translated_lines + len(gemini_cache_values) >= total_lines):
                            try:
                                gemini_model = genai.GenerativeModel('gemini-3.5-flash')
                                
                                # Формируем словарь для отправки, чтобы ИИ видел контекст строк
                                payload = {f"str_{i}": val for i, val in enumerate(gemini_cache_values)}
                                
                                prompt = (
                                    f"You are a professional game translator specializing in Deltarune localization from {source_lang} to {target_lang}.\n"
                                    "CRITICAL RULES:\n"
                                    "- NEVER remove, alter, translate, or reorder ANY control codes. These include but are not limited to:\n"
                                    "  \\E0, \\E1, \\M0, \\M1, \\M2, ^0, ^1, ^2, ^3, ^4, ^5, ^6, ^7, ^8, ^9, /%, %%, %, &, /, \\n, \\t, and any other non-alphabetic sequences.\n"
                                    "- Control codes MUST retain their exact position relative to the surrounding text.\n"
                                    "- If a control code is at the start/end of a string, it MUST remain at the start/end in the translation.\n"
                                    "- If a control code is between words, it MUST stay between the translated words in the same order.\n\n"
                                    "TRANSLATION GUIDELINES:\n"
                                    "- Translate ONLY the human-readable text. Leave ALL codes untouched.\n"
                                    "- Preserve punctuation (？ → ?), spacing, and line breaks relative to the codes.\n"
                                    "- Character names MUST be translated as follows: \n"
                                    "  クリス=Крис, スージー=Сьюзи, ラルセイ=Ральсей, ノエル=Ноэль, ルルー=Рулу, ジャルグ=Джалг, ベリル=Берилл.\n"
                                    "- Maintain the original tone: casual, emotional, or formal, depending on the context.\n\n"
                                    "EXAMPLES:\n"
                                    'Original: "聞コエマスカ^6？\\M1 ^6 %"\n'
                                    'Correct: "Ты меня слышишь?^6?\\M1 ^6 %"\n'
                                    'Incorrect: "Ты меня слышишь? ^6? \\M1 ^6 %" (extra spaces) or "Ты меня слышишь?^6?\\M1 %" (missing code).\n\n'
                                    'Original: "^6 \\M0ワレワレハ^6& 接続サレテ& イマスカ^6？\\M1 ^6 ^6 %%"\n'
                                    'Correct: "^6 \\M0Мы^6& соединены?& Или нет?^6?\\M1 ^6 ^6 %%"\n'
                                    'Incorrect: "^6 \\M0 Мы ^6 & соединены & или нет? ^6? \\M1 ^6 ^6 %%" (spaces around codes).\n\n'
                                    "OUTPUT FORMAT:\n"
                                    "- Return ONLY a valid JSON object with the SAME keys as the input.\n"
                                    "- Do NOT add comments, explanations, or markdown formatting (e.g., no ```json).\n"
                                    "- Ensure the output is parseable as JSON. Escape special characters if necessary.\n\n"
                                    f"DATA TO TRANSLATE:\n{json.dumps(payload, ensure_ascii=False)}"
                                )
                                
                                response = gemini_model.generate_content(prompt)
                                response_text = response.text.strip()
                                
                                translated_obj = safe_json_loads(response_text)
                                
                                # Раскладываем перевод обратно в базу данных игры
                                for i, (b_key, orig_val) in enumerate(zip(gemini_cache_keys, gemini_cache_values)):
                                    key_id = f"str_{i}"
                                    trans_val = translated_obj.get(key_id, orig_val)
                                    
                                    # Финальная питоновская проверка на то, что ИИ не удалил важные коды (%% или &)
                                    fixed = restore_codes(orig_val, trans_val)
                                    if fixed is None:
                                        data[b_key] = orig_val
                                        log_textbox.insert("0.0", f"[!] Коды не совпали, оставлен оригинал: {orig_val}\n")
                                    else:
                                        data[b_key] = fixed
                                        log_textbox.insert("0.0", f"[Успех] {orig_val} -> {fixed}\n")
                                        
                                    translated_lines += 1

                                gemini_cache_keys = []
                                gemini_cache_values = []

                                time.sleep(5.1)
                            except Exception as e:
                                error_sfx.play()
                                log_textbox.insert("0.0", f"Ошибка пакета Gemini: {str(e)}\nСкидываем пакет в оригиналы...\n")
                                for b_key, orig_val in zip(gemini_cache_keys, gemini_cache_values):
                                    data[b_key] = orig_val
                                    translated_lines += 1
                                gemini_cache_keys = []
                                gemini_cache_values = []
                                time.sleep(2.0)
                update_progress()
                des.update()

        with open(target_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        log_textbox.insert("0.0", "Translation completed successfully!\n")
        done_sfx.play()
        progress_text.configure(text="Translation completed!\n")
        des.after(500)
        mixer.music.pause()
        des.update()
        start_translate_button.configure(state='normal')
        lang_frame_source_combo.configure(state='normal')
        lang_frame_target_combo.configure(state='normal')
        source_file_frame_button.configure(state='normal')
        target_file_frame_button.configure(state='normal')
        source_file_frame_textbox.configure(state='normal')
        target_file_frame_textbox.configure(state='normal')
        tarnslator_frame_radio_google.configure(state='normal')
        tarnslator_frame_radio_yandex.configure(state='normal')
        tarnslator_frame_radio_libre.configure(state='normal')
        gemini_model_radio_fast.configure(state='normal')
        gemini_model_radio_accurate.configure(state='normal')
        des.update()
        des.after(1000)
        music_looped = True
        music_loop()
    except:
        mixer.music.pause()
        error_sfx.play()
        progress_text.configure(text='Read file error!!!')
        des.update()
        start_translate_button.configure(state='normal')
        lang_frame_source_combo.configure(state='normal')
        lang_frame_target_combo.configure(state='normal')
        source_file_frame_button.configure(state='normal')
        target_file_frame_button.configure(state='normal')
        source_file_frame_textbox.configure(state='normal')
        target_file_frame_textbox.configure(state='normal')
        tarnslator_frame_radio_google.configure(state='normal')
        tarnslator_frame_radio_yandex.configure(state='normal')
        tarnslator_frame_radio_libre.configure(state='normal')
        gemini_model_radio_fast.configure(state='normal')
        gemini_model_radio_accurate.configure(state='normal')
        des.update()
        des.after(1000)
        music_looped = True
        music_loop()

MAX_LINE_LEN = 20  # максимум символов на строку в Deltarune

PUNCT_START = set('.,!?…»)』】〕\'"')

def fix_hanging_punct(lines):
    """Присоединяет висячую пунктуацию в начале строки к предыдущей."""
    result = []
    for line in lines:
        stripped = line.lstrip('\u3000 ')
        if result and stripped and stripped[0] in PUNCT_START:
            result[-1] = result[-1].rstrip() + stripped[0]
            rest = stripped[1:]
            if rest.strip():
                result.append('\u3000 ' + rest.lstrip())
        else:
            result.append(line)
    return result


def reflow_value(value):
    """
    Перераспределяет переносы строк (\\n) в одной игровой строке так,
    чтобы видимый текст между кодами не превышал MAX_LINE_LEN символов.
    Управляющие коды (\\E0, ^1, &, %% и т.д.) не считаются в длину.
    """
    # Паттерн для управляющих кодов — они невидимы на экране
    code_pattern = re.compile(r'\\[A-Za-z0-9]+|\^[0-9]+|%%|/+%*|&|\u3000|~[0-9]|＊|\*|<!--.*?-->|#')

    def visible_len(s):
        return len(code_pattern.sub('', s))

    # Разбиваем по \n — каждый кусок это отдельная строка на экране
    segments = value.split('\n')
    result_segments = []

    for seg in segments:
        # Если уже влезает — не трогаем
        if visible_len(seg) <= MAX_LINE_LEN:
            result_segments.append(seg)
            continue

        # Разбиваем сегмент на токены: код или слово
        tokens = []
        last = 0
        for m in code_pattern.finditer(seg):
            if m.start() > last:
                # Текст между кодами — разбиваем по пробелам
                for word in seg[last:m.start()].split(' '):
                    if word:
                        tokens.append(('word', word))
                    tokens.append(('word', ' '))
                if tokens and tokens[-1] == ('word', ' '):
                    tokens.pop()
            tokens.append(('code', m.group(0)))
            last = m.end()
        if last < len(seg):
            for word in seg[last:].split(' '):
                if word:
                    tokens.append(('word', word))
                tokens.append(('word', ' '))
            if tokens and tokens[-1] == ('word', ' '):
                tokens.pop()

        # Собираем строки по MAX_LINE_LEN
        lines = []
        current = ''
        current_len = 0

        for ttype, tval in tokens:
            if ttype == 'code':
                current += tval
            else:
                word_len = len(tval)
                if current_len + word_len > MAX_LINE_LEN and current_len > 0:
                    lines.append(current.rstrip())
                    current = tval.lstrip()
                    current_len = len(current)
                else:
                    current += tval
                    current_len += word_len

        if current.strip():
            lines.append(current.rstrip())

        lines = fix_hanging_punct(lines)
        result_segments.append('\n　 '.join(lines))

    return '\n'.join(result_segments)


def reflow_value_by_segments(value, orig_value):
    """Делит перевод на столько же сегментов что в оригинале."""
    code_pattern = re.compile(r'\\[A-Za-z0-9]+|\^[0-9]+|%%|/+%*|&|\u3000|~[0-9]|＊|\*|<!--.*?-->|#')
    orig_segments = orig_value.split('\n')
    n = len(orig_segments)
    if n <= 1:
        return value
    flat = value.replace('\n', ' ').replace('\u3000', ' ')
    flat = re.sub(r' +', ' ', flat).strip()
    all_words = [w for p in code_pattern.split(flat) for w in p.split(' ') if w]
    total_words = len(all_words)
    if total_words == 0:
        return value
    words_per_seg = max(1, round(total_words / n))
    tokens = []
    pos = 0
    for m in code_pattern.finditer(flat):
        if m.start() > pos:
            tokens.append(('text', flat[pos:m.start()]))
        tokens.append(('code', m.group(0)))
        pos = m.end()
    if pos < len(flat):
        tokens.append(('text', flat[pos:]))
    segments = []
    current = ''
    word_count = 0
    seg_idx = 0
    for ttype, tval in tokens:
        if ttype == 'code':
            current += tval
        else:
            for word in tval.split(' '):
                if not word:
                    if current:
                        current += ' '
                    continue
                if current and not current.endswith(' '):
                    current += ' '
                current += word
                word_count += 1
                if word_count >= words_per_seg and seg_idx < n - 1:
                    segments.append(current.strip())
                    current = ''
                    word_count = 0
                    seg_idx += 1
    if current.strip():
        segments.append(current.strip())
    if not segments:
        return value
    segments = fix_hanging_punct(segments)
    result = segments[0]
    for s in segments[1:]:
        result += '\n\u3000 ' + s
    return result


def reflow_process():
    target_path = target_file_frame_textbox.get()
    if not target_path:
        progress_text.configure(text='Укажи Target file!')
        des.update()
        return
    try:
        progress_text.configure(text='Выравниваю...')
        des.update()
        with open(target_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        source_path = source_file_frame_textbox.get()
        source_data = {}
        if source_path:
            try:
                with open(source_path, 'r', encoding='utf-8') as f:
                    source_data = json.load(f)
            except Exception:
                pass

        changed = 0
        for key, value in data.items():
            if key == 'date' or not isinstance(value, str) or not value.strip():
                continue
            if '\\u3000' in value:
                value = value.replace('\\u3000', '\u3000')
                data[key] = value
                changed += 1
            if '\\n' in value:
                value = value.replace('\\n', '\n')
                data[key] = value
                changed += 1
            while '\n\n' in value:
                value = value.replace('\n\n', '\n')
                data[key] = value
                changed += 1
            if '＊' not in value:
                continue
            orig_value = source_data.get(key, '')
            if orig_value and '\n' in orig_value:
                new_val = reflow_value_by_segments(value, orig_value)
            else:
                new_val = reflow_value(value)
            if new_val != value:
                data[key] = new_val
                changed += 1

        dir_name, file_name = os.path.split(target_path)
        base, ext = os.path.splitext(file_name)
        output_path = os.path.join(dir_name, f"{base}_reflowed{ext}")

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        done_sfx.play()
        progress_text.configure(text=f'Готово! Исправлено строк: {changed}')
        log_textbox.insert('0.0', f'[Выравнивание] Сохранено в: {output_path}\nИсправлено строк: {changed}\n')
        des.update()
    except Exception as e:
        error_sfx.play()
        progress_text.configure(text=f'Ошибка: {str(e)}')
        des.update()
    finally:
        reflow_button.configure(state='normal')
        start_translate_button.configure(state='normal')


def extract_dialog_codes(text):
    """Коды завершения диалога/страницы: %%, /%, %, /"""
    # Порядок важен: сначала длинные паттерны
    return re.findall(r'%%|/%|(?<![/%])%|(?<![%\\/])/$', str(text))

def fix_dialog_codes(original, translated):
    """
    Берёт коды завершения из оригинала и вставляет их в конец перевода.
    Обрабатывает: %%, /%, %, / (одиночный слеш в конце строки)
    """
    orig_codes = extract_dialog_codes(original)
    trans_codes = extract_dialog_codes(translated)

    if orig_codes == trans_codes:
        return translated  # всё ок, не трогаем

    # Убираем из конца перевода все имеющиеся коды завершения
    cleaned = re.sub(r'(%%|/%|(?<![/%])%|(?<![%\\/])/)\s*$', '', translated).rstrip()

    # Берём суффикс завершения из оригинала
    orig_suffix_match = re.search(r'((?:%%|/%|(?<![/%])%|(?<![%\\/])/)[\s%%/%/]*$)', original)
    if orig_suffix_match:
        suffix = orig_suffix_match.group(1)
    else:
        suffix = ''.join(orig_codes)

    return cleaned + suffix


def check_codes_process(autofix=False):
    source_path = source_file_frame_textbox.get()
    target_path = target_file_frame_textbox.get()

    try:
        mode = 'Автоисправление' if autofix else 'Проверка кодов'
        progress_text.configure(text=f'{mode}...')
        des.update()

        with open(source_path, 'r', encoding='utf-8') as f:
            source_data = json.load(f)
        with open(target_path, 'r', encoding='utf-8') as f:
            target_data = json.load(f)

        broken = 0
        fixed = 0
        checked = 0

        for key, orig_val in source_data.items():
            if key == 'date' or not isinstance(orig_val, str) or not orig_val.strip():
                continue
            trans_val = target_data.get(key)
            if trans_val is None or not isinstance(trans_val, str):
                continue

            checked += 1
            orig_codes = extract_dialog_codes(orig_val)
            trans_codes = extract_dialog_codes(trans_val)

            if orig_codes != trans_codes:
                broken += 1
                if autofix:
                    corrected = fix_dialog_codes(orig_val, trans_val)
                    target_data[key] = corrected
                    fixed += 1
                    log_textbox.insert('0.0',
                        f'[fix] {key}\n'
                        f'      БЫЛ: {trans_val}\n'
                        f'      СТА: {corrected}\n'
                    )
                else:
                    missing = [c for c in orig_codes if c not in trans_codes]
                    extra = [c for c in trans_codes if c not in orig_codes]
                    log_textbox.insert('0.0',
                        f'[!] {key}\n'
                        f'    ОРИ: {orig_val}\n'
                        f'    ПЕР: {trans_val}\n'
                        f'    Нет: {missing}  Лишние: {extra}\n'
                    )
                des.update_idletasks()

        if autofix and fixed > 0:
            import os
            dir_name, file_name = os.path.split(target_path)
            base, ext = os.path.splitext(file_name)
            output_path = os.path.join(dir_name, f'{base}_fixed{ext}')
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(target_data, f, ensure_ascii=False, indent=4)
            done_sfx.play()
            progress_text.configure(text=f'Исправлено: {fixed} строк')
            log_textbox.insert('0.0', f'[OK] Сохранено в: {output_path}\nИсправлено: {fixed} из {checked} строк.\n')
        elif autofix and fixed == 0:
            done_sfx.play()
            progress_text.configure(text=f'Всё в порядке ({checked} строк)')
            log_textbox.insert('0.0', f'[OK] Проверено {checked} строк — исправлять нечего.\n')
        elif broken == 0:
            done_sfx.play()
            progress_text.configure(text=f'Все коды в порядке ({checked} строк)')
            log_textbox.insert('0.0', f'[OK] Проверено {checked} строк — ошибок нет.\n')
        else:
            error_sfx.play()
            progress_text.configure(text=f'Найдено проблем: {broken} из {checked}')
            log_textbox.insert('0.0', f'[!] Итого проблем: {broken} из {checked} строк.\n')

        des.update()
    except Exception as e:
        error_sfx.play()
        progress_text.configure(text=f'Ошибка: {str(e)}')
        des.update()
    finally:
        check_codes_button.configure(state='normal')
        autofix_codes_button.configure(state='normal')
        start_translate_button.configure(state='normal')
        reflow_button.configure(state='normal')


def start_check_codes():
    check_codes_button.configure(state='disabled')
    autofix_codes_button.configure(state='disabled')
    start_translate_button.configure(state='disabled')
    reflow_button.configure(state='disabled')
    Thread(target=lambda: check_codes_process(autofix=False)).start()


def start_autofix_codes():
    check_codes_button.configure(state='disabled')
    autofix_codes_button.configure(state='disabled')
    start_translate_button.configure(state='disabled')
    reflow_button.configure(state='disabled')
    Thread(target=lambda: check_codes_process(autofix=True)).start()


def start_reflow():
    reflow_button.configure(state='disabled')
    start_translate_button.configure(state='disabled')
    progress_progressbar.set(0)
    Thread(target=reflow_process).start()


def start_translate():
    global music_looped
    if action_start == 'translate':
        progress_text.configure(text='Translate Started')
        des.update()
        des.after(300)
        music_looped = False
        mixer.music.stop()
        mixer.music.load('sound/progress_music.ogg')
        mixer.music.play(-1)
        start_translate_button.configure(state='disabled')
        lang_frame_source_combo.configure(state='disabled')
        lang_frame_target_combo.configure(state='disabled')
        source_file_frame_button.configure(state='disabled')
        target_file_frame_button.configure(state='disabled')
        source_file_frame_textbox.configure(state='disabled')
        target_file_frame_textbox.configure(state='disabled')
        tarnslator_frame_radio_google.configure(state='disabled')
        tarnslator_frame_radio_yandex.configure(state='disabled')
        tarnslator_frame_radio_libre.configure(state='disabled')
        gemini_model_radio_fast.configure(state='disabled')
        gemini_model_radio_accurate.configure(state='disabled')

        Thread(target=translate_process).start()

main_frame = CTkFrame(des, width=760, height=400, fg_color='#1c1c1c',bg_color='#1c1c1c')

#Основной фрейм с файлами и прогрессами
source_file_frame = CTkFrame(main_frame, width=720, height=60, fg_color='#2e2e2e')
source_file_frame_header = CTkLabel(source_file_frame, text='Source file:', text_color='white', font=('Arial', 15))
source_file_frame_header.place(x=20,y=1)
source_file_frame_textbox = CTkEntry(source_file_frame, width=600, height=20, text_color='white', bg_color='#2e2e2e', fg_color="#2e2e2e", font=('Arial', 17))
source_file_frame_textbox.place(x=10, y=25)
source_file_frame_button = CTkButton(source_file_frame, text='File', height=30, width=90, text_color='white', bg_color='#1c1c1c', fg_color='#1c1c1c', hover_color='grey', font=('Arial', 15), command=change_source_lang)
source_file_frame_button.place(x=620, y=25.5)

target_file_frame = CTkFrame(main_frame, width=720, height=60, fg_color='#2e2e2e')
target_file_frame_header = CTkLabel(target_file_frame, text='Target file:', text_color='white', font=('Arial', 15))
target_file_frame_header.place(x=20,y=1)
target_file_frame_textbox = CTkEntry(target_file_frame, width=600, bg_color='#2e2e2e', fg_color="#2e2e2e", height=20, text_color='white', font=('Arial', 17))
target_file_frame_textbox.place(x=10, y=25)
target_file_frame_button = CTkButton(target_file_frame, text='File', height=30, width=90, text_color='white', bg_color='#1c1c1c', fg_color='#1c1c1c', hover_color='grey', font=('Arial', 15), command=change_target_lang)
target_file_frame_button.place(x=620, y=25.5)

source_file_frame.place(x=20, y=20)
target_file_frame.place(x=20, y=100)

lang_frame = CTkFrame(main_frame, width=350, height=100, bg_color='#2e2e2e', fg_color="#2e2e2e")
lang_frame_header = CTkLabel(lang_frame, text='Language', text_color='white', font=('Arial', 15))
lang_frame_header.place(x=20,y=1)

lang_frame_source_file = CTkLabel(lang_frame, text='Source language:', text_color='white', font=('Arial', 15))
lang_frame_source_file.place(x=10,y=30)
lang_frame_source_combo = CTkComboBox(lang_frame, text_color='white', bg_color='#2e2e2e', fg_color='#2e2e2e', width=190, values=list(LANGUAGES.keys()), variable=StringVar(lang_frame, value='en'), font=('Arial', 15))
lang_frame_source_combo.place(x=135,y=31)

lang_frame_target_file = CTkLabel(lang_frame, text='Target language:', text_color='white', font=('Arial', 15))
lang_frame_target_file.place(x=10,y=65)
lang_frame_target_combo = CTkComboBox(lang_frame, text_color='white', bg_color='#2e2e2e', fg_color='#2e2e2e', width=190, values=list(LANGUAGES.keys()), variable=StringVar(lang_frame, value='ru'), font=('Arial', 15))
lang_frame_target_combo.place(x=135,y=66)
lang_frame.place(x=20, y=175)


tarnslator_frame = CTkFrame(main_frame, width=350, height=140, bg_color='#2e2e2e', fg_color="#2e2e2e")
translator_api = IntVar(tarnslator_frame, value=0)

tarnslator_frame_header = CTkLabel(tarnslator_frame, text='Translate API', text_color='white', font=('Arial', 15))
tarnslator_frame_header.place(x=130,y=1)

tarnslator_frame_radio_google = CTkRadioButton(tarnslator_frame, text='Google', text_color='white', font=('Arial', 20), fg_color='white', value=0, variable=translator_api, hover_color='grey')
tarnslator_frame_radio_google.place(x=15, y=50)

tarnslator_frame_radio_yandex = CTkRadioButton(tarnslator_frame, text='Yandex', text_color='white', font=('Arial', 20), fg_color='white', value=1, variable=translator_api, hover_color='grey')
tarnslator_frame_radio_yandex.place(x=125, y=50)

tarnslator_frame_radio_libre = CTkRadioButton(tarnslator_frame, text='Gemini', text_color='white', font=('Arial', 20), fg_color='white', value=2, variable=translator_api, hover_color='grey')
tarnslator_frame_radio_libre.place(x=240, y=50)

gemini_model_var = IntVar(tarnslator_frame, value=0)
gemini_model_label = CTkLabel(tarnslator_frame, text='Gemini mode:', text_color='grey', font=('Arial', 13))
gemini_model_label.place(x=15, y=95)
gemini_model_radio_fast = CTkRadioButton(tarnslator_frame, text='Fast', text_color='white', font=('Arial', 15), fg_color='white', value=0, variable=gemini_model_var, hover_color='grey')
gemini_model_radio_fast.place(x=130, y=95)
gemini_model_radio_accurate = CTkRadioButton(tarnslator_frame, text='Accurate', text_color='white', font=('Arial', 15), fg_color='white', value=1, variable=gemini_model_var, hover_color='grey')
gemini_model_radio_accurate.place(x=210, y=95)
tarnslator_frame.place(x=390, y=175)


progress_header = CTkLabel(main_frame, text='Translate Progress:', text_color='white', font=('Arial', 15))
progress_header.place(x=20,y=300)
progress_text = CTkLabel(main_frame, text='Ready', text_color='white', font=('Arial', 15))
progress_text.place(x=230,y=300)
progress_var = IntVar(main_frame, value=0)
progress_progressbar = CTkProgressBar(main_frame, progress_color='white', fg_color='#2e2e2e', variable=progress_var, width=720, height=10)
progress_progressbar.place(x=20, y=330)
start_translate_button = CTkButton(main_frame, text='Translate!', height=30, width=100, text_color='white', bg_color='#2e2e2e', fg_color='#2e2e2e', hover_color='grey', font=('Arial', 15), command=start_translate)
start_translate_button.place(x=630, y=350)
reflow_button = CTkButton(main_frame, text='Выравнить', height=30, width=120, text_color='white', bg_color='#2e2e2e', fg_color='#2e2e2e', hover_color='grey', font=('Arial', 15), command=start_reflow)
reflow_button.place(x=495, y=350)
check_codes_button = CTkButton(main_frame, text='Проверить коды', height=30, width=150, text_color='white', bg_color='#2e2e2e', fg_color='#2e2e2e', hover_color='grey', font=('Arial', 15), command=start_check_codes)
check_codes_button.place(x=330, y=350)
autofix_codes_button = CTkButton(main_frame, text='Автоисправить', height=30, width=140, text_color='white', bg_color='#2e2e2e', fg_color='#2e2e2e', hover_color='grey', font=('Arial', 15), command=start_autofix_codes)
autofix_codes_button.place(x=175, y=350)

#Логи
log_frame = CTkFrame(des, width=760, height=400, fg_color="#3A3838",bg_color="#353535")
log_textbox = CTkTextbox(log_frame, width=720, height=360, bg_color='#2e2e2e', fg_color="#1c1c1c", text_color='white', font=('Arial', 20))
log_textbox.place(x=20,y=20)


option_frame = CTkFrame(des, width=140, height=50, fg_color='black', bg_color='black')
log_button = CTkButton(option_frame, text='Log', height=50, width=50, text_color='white', bg_color='black', fg_color='black', hover_color='#2e2e2e', font=('Arial', 20), command=clopen_log)
log_button.place(x=0, y=0)

vol_button = CTkButton(option_frame, text='Volume', height=50, width=50, text_color='white', bg_color='black', fg_color='black', hover_color='#2e2e2e', font=('Arial', 20), command=clopen_volume)
vol_button.place(x=60, y=0)

#Настройка громкости
setvol_frame = CTkFrame(des, width=760, height=400, fg_color="#3A3838",bg_color="#353535")
setvol_content = CTkFrame(setvol_frame, width=720, height=360, bg_color='#2e2e2e', fg_color="#1c1c1c")
setvol_content.place(x=20,y=20)

background_volume_var = IntVar(setvol_content, backsound_volume)
sfx_volume_var = IntVar(setvol_content, sfx_volume)

setvol_background_music = CTkLabel(setvol_content, text='Background music volume:', text_color='white', font=('Arial', 20))
setvol_background_music.place(x=250, y=15)
setvol_background_music_int = CTkLabel(setvol_content, text=backsound_volume, text_color='white', font=('Arial', 20))
setvol_background_music_int.place(x=500, y=15)
setvol_background_music_slider = CTkSlider(setvol_content, width=700, height=25, progress_color='white', variable=background_volume_var, button_color='#1c1c1c', button_hover_color='grey', command=change_background_volume)
setvol_background_music_slider.place(x=12.5, y=45)

setvol_effect_music = CTkLabel(setvol_content, text='Effect music volume:', text_color='white', font=('Arial', 20))
setvol_effect_music.place(x=270, y=80)
setvol_effect_music_int = CTkLabel(setvol_content, text=sfx_volume, text_color='white', font=('Arial', 20))
setvol_effect_music_int.place(x=500, y=80)
setvol_effect_music_slider = CTkSlider(setvol_content, width=700, height=25, progress_color='white', button_color='#1c1c1c', variable=sfx_volume_var, button_hover_color='grey', command=change_effect_volume)
setvol_effect_music_slider.place(x=12.5, y=120)

des.after(1000, lambda: option_frame.place(x=610, y=440))
des.after(1000, lambda: main_frame.place(x=20,y=20))

if platform.system() == 'Windows':
    des.iconbitmap('images/logo.ico')
elif platform.system() == 'Linux':
    icon = PhotoImage(file='images/logo.png')
    des.iconphoto(False, icon)

des.protocol("WM_DELETE_WINDOW", lambda: os._exit(2))

des.mainloop()
