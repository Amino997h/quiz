import os
import sys
import json
import time
import random
import wave
import struct
import math
import subprocess
import requests
import numpy as np
from PIL import Image, ImageDraw, ImageFont

import cv2

sys.stdout.reconfigure(encoding='utf-8')

# --- 1. الإعدادات ---
def load_config():
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    default_config = {
        "api_urls": [
            "http://127.0.0.1:8008/v1/chat/completions",
            "https://tartness-plating-subside.ngrok-free.dev/v1/chat/completions"
        ],
        "api_url": "http://127.0.0.1:8008/v1/chat/completions",
        "api_key": "sk-chatgpt-local-secret-key",
        "bot_token": "8951711275:AAFpZH-GfdFxEMO-oCb4iJQz1eBASYGBdCQ",
        "channel_id": "-1004247712091",
        "voice": "en-US-GuyNeural",
        "gameplay_sources": [
            r"C:\Users\User\OneDrive\Desktop\resilt\document_5936256664112996112.mp4",
            r"C:\Users\User\OneDrive\Desktop\resilt\videoplayback.mp4"
        ],
        "outro_video": r"C:\Users\User\OneDrive\Desktop\resilt\6993530118_tk_2x.mp4"
    }
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                default_config.update(user_config)
        except Exception as e:
            print(f"Error loading config: {e}")
    return default_config

CONFIG = load_config()

# الخط المميز للكتابة والمطابق للمشروع السابق
FONT_FILE = os.path.join(os.path.dirname(__file__), "theboldfont.ttf")
if not os.path.exists(FONT_FILE):
    FONT_FILE = "arialbd.ttf"

# --- 2. محرك الصوت السريع والذكي (Edge-TTS صوت Guy العصبي) ---
def generate_speech(text, output_path, rate="+0%"):
    for attempt in range(1, 4):
        try:
            import edge_tts.communicate
            import edge_tts.constants
            import asyncio

            edge_tts.communicate.WSS_URL = (
                "wss://api.msedgeservices.com/tts/cognitiveservices/websocket/v1"
                f"?Ocp-Apim-Subscription-Key={edge_tts.constants.TRUSTED_CLIENT_TOKEN}"
            )

            comm = edge_tts.Communicate(text, "en-US-GuyNeural", rate=rate)
            asyncio.run(comm.save(output_path))
            if os.path.exists(output_path) and os.path.getsize(output_path) > 800:
                return True
        except Exception as e:
            time.sleep(1)

    # بديل gTTS
    try:
        from gtts import gTTS
        tts = gTTS(text=text, lang='en', slow=False)
        tts.save(output_path)
        return True
    except:
        pass

    # بديل pyttsx3
    try:
        import pyttsx3
        eng = pyttsx3.init()
        eng.setProperty('rate', 170 if rate != "+0%" else 145)
        eng.save_to_file(text, output_path)
        eng.runAndWait()
        return True
    except:
        return False

# --- 3. توليد المؤثرات الصوتية برمجياً (تكتكة سريعة + نغمة حماسية لكشف الإجابة) ---
def generate_fast_tick_sound(output_wav):
    """صوت تكتكة عداد سريع جداً وحاد ومثير للحماس (Fast Ticking)"""
    sr = 44100
    dur = 0.04
    n_samples = int(sr * dur)
    t = np.linspace(0, dur, n_samples, False)
    decay = np.exp(-t * 120)
    tone = np.sin(2 * np.pi * 1650 * t) * decay * 0.55
    audio_data = (tone * 32767).astype(np.int16).tobytes()
    with wave.open(output_wav, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(audio_data)

def generate_energetic_reveal_sound(output_wav):
    """نغمة حماسية خاطفة ومبهرة للإجابة الصحيحة (Fanfare / Winning Chord)"""
    sr = 44100
    dur = 0.65
    n_samples = int(sr * dur)
    t = np.linspace(0, dur, n_samples, False)
    chord = (
        0.32 * np.sin(2 * np.pi * 523.25 * t) +
        0.28 * np.sin(2 * np.pi * 659.25 * t) +
        0.26 * np.sin(2 * np.pi * 783.99 * t) +
        0.22 * np.sin(2 * np.pi * 1046.50 * t)
    )
    envelope = np.exp(-t * 3.8)
    tone = chord * envelope
    audio_data = (tone * 32767).astype(np.int16).tobytes()
    with wave.open(output_wav, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(audio_data)

def generate_suspense_bgm(output_wav, duration_sec):
    """توليد موسيقى خلفية إيقاعية حماسية مشوقة جداً (Upbeat Suspenseful Lo-Fi BGM)"""
    sr = 44100
    n_samples = int(sr * duration_sec)
    t = np.linspace(0, duration_sec, n_samples, False)
    
    # 1. إيقاع بيز عميق متكرر (Deep Sub Pulse / Kick) كل 0.5 ثانية (120 BPM)
    beat_period = 0.5
    beat_phase = (t % beat_period) / beat_period
    kick = np.sin(2 * np.pi * (65 - 35 * beat_phase) * beat_phase) * np.exp(-beat_phase * 9.0)
    
    # 2. نغمة سنث غامضة ومحفزة (Hypnotic Arp Chords: D minor progression)
    notes = [146.83, 174.61, 220.00, 261.63, 196.00, 220.00, 146.83, 174.61]
    step_duration = 0.25
    note_idx = (t / step_duration).astype(int) % len(notes)
    note_freqs = np.array(notes)[note_idx]
    sub_t = (t % step_duration) / step_duration
    synth = 0.5 * np.sin(2 * np.pi * note_freqs * t) * np.exp(-sub_t * 3.5)
    
    # 3. صوت لمعان خفيف وإيقاعي (Hi-hat click) كل 0.25 ثانية
    noise = np.random.uniform(-0.15, 0.15, n_samples)
    hi_hat = noise * np.exp(-sub_t * 40.0)
    
    mix = (kick * 0.45) + (synth * 0.35) + (hi_hat * 0.20)
    # خفض الصوت الإجمالي ليكون خلفية موسيقية هادئة تحت صوت المعلق والمؤثرات
    mix = mix * 0.22
    audio_data = (np.clip(mix, -0.99, 0.99) * 32767).astype(np.int16).tobytes()
    with wave.open(output_wav, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(audio_data)
    return output_wav

def generate_countdown_bar_video(output_mp4, duration=2.0, fps=30, width=1000, height=14):
    """توليد مقطع فيديو متحرك بدقة 30fps لشريط العداد التنازلي مع تدرج لوني سلس جداً (أخضر ➔ أصفر ➔ أحمر)"""
    n_frames = int(duration * fps)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_mp4, fourcc, float(fps), (width, height), isColor=True)
    
    # نقاط الألوان الأساسية بنظام BGR:
    # أخضر زمردي مشرق: [46, 204, 64] (#40CC2E)
    # أصفر تحذيري نابض: [0, 215, 255] (#FFD700)
    # أحمر قرمزي ناري:  [20, 20, 245] (#F51414)
    color_green = np.array([46, 204, 64], dtype=np.float32)
    color_yellow = np.array([0, 215, 255], dtype=np.float32)
    color_red = np.array([20, 20, 245], dtype=np.float32)

    for i in range(n_frames):
        fraction = 1.0 - (i / float(n_frames))
        active_w = int(width * max(0.0, fraction))
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        # خلفية المسار الداكن (Dark Track #1E2333 -> BGR: [51, 35, 30])
        frame[:, :] = [51, 35, 30]

        if active_w > 0:
            # انتقال لوني تدريجي وناعم تماماً (Smooth Linear Interpolation):
            # من fraction = 1.0 إلى 0.5: يتدرج بسلاسة من الأخضر إلى الأصفر
            # من fraction = 0.5 إلى 0.0: يتدرج بسلاسة من الأصفر إلى الأحمر
            if fraction >= 0.5:
                t_sub = (fraction - 0.5) / 0.5
                c = color_yellow + t_sub * (color_green - color_yellow)
            else:
                t_sub = fraction / 0.5
                c = color_red + t_sub * (color_yellow - color_red)

            bar_color = np.clip(np.round(c), 0, 255).astype(np.uint8).tolist()
            frame[:, :active_w] = bar_color

        out.write(frame)
    out.release()
    return output_mp4

# --- 4. توليد الأسئلة 100% حول الموضوع المطلوب (Topic-Adherent LLM Engine) ---
def clean_llm_json_response(raw_text):
    """تنظيف وتجريد رد الذكاء الاصطناعي من أي علامات Markdown أو هروب أسطر"""
    cleaned = raw_text.strip()
    if cleaned.startswith("```json"): cleaned = cleaned[7:-3].strip()
    elif cleaned.startswith("```"): cleaned = cleaned[3:-3].strip()
    # إزالة أي علامات هروب markdown شائعة
    cleaned = cleaned.replace(r'\_', '_').replace(r'\[', '[').replace(r'\]', ']').replace(r'\*', '*')
    
    # محاولة التحليل عبر json القياسي
    try:
        return json.loads(cleaned)
    except Exception:
        pass
    
    # محاولة الإصلاح التلقائي عبر json_repair
    try:
        import json_repair
        repaired = json_repair.repair_json(cleaned, return_objects=True)
        if isinstance(repaired, list) and len(repaired) > 0:
            return repaired
    except Exception:
        pass
    return None

def generate_4_levels_quiz(topic=""):
    api_urls = CONFIG.get("api_urls", [])
    if not api_urls:
        api_urls = [CONFIG.get("api_url", "http://127.0.0.1:8008/v1/chat/completions")]
    
    # التأكد من شمول الرابطين (المحلي ورابط ngrok الثابت)
    fallback_endpoints = [
        "http://127.0.0.1:8008/v1/chat/completions",
        "https://tartness-plating-subside.ngrok-free.dev/v1/chat/completions"
    ]
    for ep in fallback_endpoints:
        if ep not in api_urls:
            api_urls.append(ep)

    api_key = CONFIG.get("api_key", "sk-chatgpt-local-secret-key")
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    topic_clean = topic.strip() if topic else "General Knowledge"
    print(f"\n🧠 Generating 4 fun, concise & engaging trivia questions for: [{topic_clean}]...")

    prompt = f"""
You are an elite viral trivia creator for YouTube Shorts and TikTok.
Your task is to generate 4 fun, punchy, engaging multiple-choice trivia questions strictly about the following TOPIC:
>>> TOPIC: "{topic_clean}" <<<

CRITICAL CONTENT RULES:
1. ALL questions, options, titles, and explanations MUST BE IN ENGLISH ONLY.
2. KEEP QUESTIONS SHORT AND SIMPLE: Maximum 8 to 12 words per question! No long, complicated, or boring paragraphs. It must fit easily on screen and be read quickly.
3. KEEP OPTIONS VERY SHORT: 1 to 3 words per option.
4. MAKE IT FUN & VIRAL: Interesting, engaging facts that make people want to guess and comment.
5. PROGRESSIVE DIFFICULTY:
   - Level 1 (EASY): Fun, accessible fact that most casual fans know.
   - Level 2 (MEDIUM): Interesting trivia fact that tests knowledge.
   - Level 3 (HARD): Clever fact that challenges enthusiastic fans.
   - Level 4 (IMPOSSIBLE): A surprising, mind-blowing twist question that tricks 90% of people, but STILL SHORT AND SIMPLE!

CRITICAL FORMAT REQUIREMENT:
Respond ONLY with a valid JSON array of 4 objects. No conversational text, no markdown wrappers.
[
  {{
    "level_name": "EASY LEVEL",
    "level_title": "LEVEL 1: EASY",
    "level_announcement": "Level one! Easy level.",
    "question": "Short fun question about {topic_clean}?",
    "options": {{"A": "Short1", "B": "Short2", "C": "Short3", "D": "Short4"}},
    "correct": "A"
  }},
  {{
    "level_name": "MEDIUM LEVEL",
    "level_title": "LEVEL 2: MEDIUM",
    "level_announcement": "Level two! Medium level.",
    "question": "Short fun question about {topic_clean}?",
    "options": {{"A": "Short1", "B": "Short2", "C": "Short3", "D": "Short4"}},
    "correct": "B"
  }},
  {{
    "level_name": "HARD LEVEL",
    "level_title": "LEVEL 3: HARD",
    "level_announcement": "Level three! Hard level.",
    "question": "Short fun question about {topic_clean}?",
    "options": {{"A": "Short1", "B": "Short2", "C": "Short3", "D": "Short4"}},
    "correct": "C"
  }},
  {{
    "level_name": "IMPOSSIBLE LEVEL",
    "level_title": "LEVEL 4: IMPOSSIBLE",
    "level_announcement": "Level four! The impossible level.",
    "question": "Short tricky question about {topic_clean}?",
    "options": {{"A": "Short1", "B": "Short2", "C": "Short3", "D": "Short4"}},
    "correct": "D"
  }}
]
"""

    candidate_models = ["gpt-4o", "gpt-3.5-turbo", "gpt-4"]
    for current_url in api_urls:
        for model_name in candidate_models:
            payload = {"model": model_name, "messages": [{"role": "user", "content": prompt}], "stream": False}
            try:
                resp = requests.post(current_url, headers=headers, json=payload, timeout=45)
                if resp.status_code == 200:
                    raw = resp.json()['choices'][0]['message']['content'].strip()
                    parsed = clean_llm_json_response(raw)
                    if isinstance(parsed, list) and len(parsed) == 4:
                        norm_levels = []
                        for item in parsed:
                            clean_item = {}
                            for k, v in item.items():
                                clean_k = k.replace('\\_', '_').strip()
                                clean_item[clean_k] = v
                            norm_levels.append(clean_item)
                        print(f"   ✓ تم توليد 4 أسئلة احترافية وحصرية بنسبة 100% حول موضوع [{topic_clean}] بنجاح عبر ({current_url} | {model_name})!")
                        return norm_levels
            except Exception as e:
                continue

    # إذا لم يستجب الـ API بعد كل المحاولات: لا نستخدم أي نموذج تجريبي أو بنك أسئلة ثابت
    raise RuntimeError(
        f"❌ فشل الاتصال بالـ API ولم يتم استلام رد من النماذج المتاحة.\n"
        f"يرجى التأكد من تشغيل السيرفر عبر Start_ChatGPT_API.bat والاتصال بالإنترنت."
    )

# --- 5. استخراج توقيت الكلمات بدقة (Faster-Whisper) ---
def get_word_timestamps(audio_path):
    try:
        from faster_whisper import WhisperModel
        model = WhisperModel("base", device="cpu", compute_type="int8")
        segments, _ = model.transcribe(audio_path, word_timestamps=True, language="en")
        words = []
        for segment in segments:
            for w in segment.words:
                words.append({
                    "word": w.word.strip().upper(),
                    "start": w.start,
                    "end": w.end
                })
        return words
    except Exception as e:
        return []

# --- 6. رندرة نصوص الهوك والكاريوكي ونصوص الأسئلة الملونة كلمة بكلمة ---
def wrap_text(text, font, max_width, draw):
    words = text.split()
    lines = []
    cur_line = []
    for w in words:
        test = " ".join(cur_line + [w])
        bbox = draw.textbbox((0, 0), test, font=font)
        if (bbox[2] - bbox[0]) <= max_width:
            cur_line.append(w)
        else:
            if cur_line: lines.append(" ".join(cur_line))
            cur_line = [w]
    if cur_line: lines.append(" ".join(cur_line))
    return lines

def split_words_into_single_line_chunks(words, max_w=850):
    """
    تقسيم الجملة الطويلة إلى أشطار (شطر أول ثم شطر ثانٍ) بحيث يظهر كل شطر في سطر واحد فقط
    دون تقليص حجم الخط، وبما يضمن البقاء ضمن حدود الشاشة (max_w).
    """
    try:
        font = ImageFont.truetype(FONT_FILE, 64)
    except:
        font = ImageFont.load_default()

    space_w = font.getlength(" ")
    chunks = []
    cur_chunk = []

    for w_obj in words:
        test_words = [x["word"] for x in cur_chunk] + [w_obj["word"]]
        test_len = sum(font.getlength(w) for w in test_words) + space_w * (len(test_words) - 1)
        est_width = (test_len + 60) * 1.15 + 45
        if est_width <= max_w or not cur_chunk:
            cur_chunk.append(w_obj)
        else:
            chunks.append(cur_chunk)
            cur_chunk = [w_obj]
    if cur_chunk:
        chunks.append(cur_chunk)
    return chunks

def render_chunk_karaoke_frame(chunk_words, active_idx_in_chunk, total_w=1080, total_h=260):
    """
    رندرة شطر سطر واحد فقط بحجم الخط الأصلي الكامل (TheBoldFont 64)
    مع تأثير الإمالة والشدو الكثيف، وتلوين الكلمة المنطوقة حالياً بالأصفر المشع.
    """
    try:
        font = ImageFont.truetype(FONT_FILE, 64)
    except:
        font = ImageFont.load_default()

    words_text = [w["word"] for w in chunk_words]
    space_w = font.getlength(" ")
    word_lens = [font.getlength(w) for w in words_text]
    total_text_w = sum(word_lens) + space_w * (len(words_text) - 1)

    box_w = max(int(total_text_w) + 120, 300)
    box_h = 240
    box = Image.new('RGBA', (box_w, box_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(box)

    start_x = (box_w - int(total_text_w)) // 2
    y = 70

    cur_x = start_x
    for idx, w_text in enumerate(words_text):
        is_active = (idx == active_idx_in_chunk)
        color = "#FFFF00" if is_active else "#FFFFFF"

        # 1. شادو عميق لعزل النص تماماً
        draw.text((cur_x + 7, y + 9), w_text, font=font, fill=(0, 0, 0, 240), stroke_width=8, stroke_fill=(0, 0, 0, 240))
        # 2. نص الكاريوكي
        draw.text((cur_x, y), w_text, font=font, fill=color, stroke_width=7, stroke_fill="black")
        cur_x += word_lens[idx] + space_w

    # جعل الكلام أعرض قليلاً كالمشروع الأصلي
    wider_w = int(box_w * 1.15)
    wider = box.resize((wider_w, box_h), Image.Resampling.LANCZOS)

    # إمالة السطر (Italic slant عبر Affine Transformation)
    shear_extra = 45
    sheared = wider.transform(
        (wider_w + shear_extra, box_h),
        Image.AFFINE,
        (1, -0.16, 0, 0, 1, 0),
        resample=Image.Resampling.BICUBIC
    )

    canvas = Image.new('RGBA', (total_w, total_h), (0, 0, 0, 0))
    pos_x = (total_w - sheared.width) // 2
    pos_y = (total_h - box_h) // 2
    canvas.paste(sheared, (pos_x, pos_y), sheared)
    return canvas

def create_question_card_frame(level_title, question_text, active_word_index=-1):
    """
    رسم بطاقة السؤال في أعلى الشاشة بنفس مظهر الخط الفخم (TheBoldFont):
    - تصميم ثابت لا يتزحزح
    - الكلمة المنطوقة حالياً تتلون بالأصفر المشع #FFFF00
    - باقي الكلمات تظل بالأبيض الناصع #FFFFFF مع ستورك أسود وظل
    """
    img = Image.new('RGBA', (1080, 520), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # كارد زجاجي مظلم
    card_box = [35, 15, 1045, 500]
    draw.rounded_rectangle(card_box, radius=26, fill=(16, 18, 26, 240), outline=(55, 65, 95, 255), width=3)

    # شارة المستوى
    badge_color = (239, 68, 68, 255) if "IMPOSSIBLE" in level_title else (
        (249, 115, 22, 255) if "HARD" in level_title else (
            (234, 179, 8, 255) if "MEDIUM" in level_title else (34, 197, 94, 255)
        )
    )

    try:
        lvl_font = ImageFont.truetype(FONT_FILE, 28)
        q_font = ImageFont.truetype(FONT_FILE, 44)
    except:
        lvl_font = ImageFont.load_default()
        q_font = ImageFont.load_default()

    lvl_str = f"⚡ {level_title.upper()} ⚡"
    bbox_lvl = draw.textbbox((0, 0), lvl_str, font=lvl_font)
    lvl_w = bbox_lvl[2] - bbox_lvl[0] + 40
    lvl_x = (1080 - lvl_w) // 2
    draw.rounded_rectangle([lvl_x, 35, lvl_x + lvl_w, 82], radius=16, fill=badge_color)
    draw.text((lvl_x + 20, 44), lvl_str, fill=(255, 255, 255), font=lvl_font)

    # تقسيم السؤال إلى أسطر وكلمات
    words_all = question_text.split()
    space_w = q_font.getlength(" ")

    lines = []
    cur_line = []
    for w in words_all:
        test = " ".join([item["text"] for item in cur_line] + [w])
        if q_font.getlength(test) <= 940:
            cur_line.append({"text": w, "global_idx": len(lines_flat := [x for l in lines for x in l]) + len(cur_line)})
        else:
            if cur_line: lines.append(cur_line)
            cur_line = [{"text": w, "global_idx": len(lines_flat := [x for l in lines for x in l]) + len(cur_line)}]
    if cur_line: lines.append(cur_line)

    line_h = 60
    total_h = len(lines) * line_h
    start_y = 115 + max(0, (350 - total_h) // 2)

    for i, line_words in enumerate(lines):
        line_w = sum(q_font.getlength(w["text"]) for w in line_words) + space_w * (len(line_words) - 1)
        cur_x = (1080 - line_w) // 2
        y = start_y + i * line_h

        for w_obj in line_words:
            w_str = w_obj["text"]
            w_idx = w_obj["global_idx"]
            w_len = q_font.getlength(w_str)

            is_active = (w_idx == active_word_index)
            txt_color = "#FFFF00" if is_active else "#FFFFFF"

            # شادو أسود عميق
            draw.text((cur_x + 3, y + 4), w_str, font=q_font, fill=(0, 0, 0, 230), stroke_width=6, stroke_fill=(0, 0, 0, 230))
            # النص الأساسي (ملون بالأصفر أثناء النطق)
            draw.text((cur_x, y), w_str, font=q_font, fill=txt_color, stroke_width=5, stroke_fill="black")

            cur_x += w_len + space_w

    return img

def create_options_card(options, revealed=False, correct_opt="", output_png=""):
    img = Image.new('RGBA', (1080, 540), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    card_w = 485
    card_h = 215
    gap_x = 30
    left_m = (1080 - (2 * card_w + gap_x)) // 2

    coords = {
        "A": (left_m, 20),
        "B": (left_m + card_w + gap_x, 20),
        "C": (left_m, 265),
        "D": (left_m + card_w + gap_x, 265),
    }

    try:
        letter_font = ImageFont.truetype(FONT_FILE, 36)
        text_font = ImageFont.truetype(FONT_FILE, 30)
    except:
        letter_font = ImageFont.load_default()
        text_font = ImageFont.load_default()

    for letter, (x, y) in coords.items():
        opt_text = options.get(letter, "")
        is_correct = (revealed and letter == correct_opt)
        is_wrong = (revealed and letter != correct_opt)

        if is_correct:
            bg = (34, 197, 94, 250)
            border = (255, 255, 255, 255)
            badge_bg = (20, 83, 45, 255)
            text_color = (255, 255, 255)
            border_w = 6
        elif is_wrong:
            bg = (22, 23, 30, 200)
            border = (50, 52, 65, 160)
            badge_bg = (35, 36, 48, 255)
            text_color = (130, 135, 150)
            border_w = 2
        else:
            bg = (26, 28, 40, 240)
            border = (65, 75, 110, 255)
            badge_bg = (59, 130, 246, 255)
            text_color = (255, 255, 255)
            border_w = 3

        draw.rounded_rectangle([x, y, x + card_w, y + card_h], radius=22, fill=bg, outline=border, width=border_w)

        bx = x + 42
        by = y + card_h // 2
        draw.ellipse([bx - 28, by - 28, bx + 28, by + 28], fill=badge_bg)
        lb = draw.textbbox((0, 0), letter, font=letter_font)
        draw.text((bx - (lb[2]-lb[0])//2, by - (lb[3]-lb[1])//2 - 2), letter, fill=(255, 255, 255), font=letter_font)

        opt_lines = wrap_text(opt_text, text_font, card_w - 110, draw)
        total_opt_h = len(opt_lines) * 36
        start_opt_y = y + (card_h - total_opt_h) // 2
        for idx, line in enumerate(opt_lines):
            draw.text((x + 85, start_opt_y + idx * 36), line, fill=text_color, font=text_font)

    img.save(output_png, 'PNG')

# --- 7. رفع الفيديو إلى تيليجرام ---
def upload_to_telegram(video_path, topic=""):
    print("\n[تيليجرام]: جاري نشر الفيديو على القناة...")
    
    # تحويل وتنظيف العنوان إلى الإنجليزية لضمان تطابق الوصف والهاشتاغات
    import re
    topic_clean = topic.strip()
    # إذا كان الموضوع بالعربي، نحاول استخلاص كلمة إنجليزية أو استخدام تصنيف أنيق
    has_arabic = bool(re.search(r'[\u0600-\u06FF]', topic_clean))
    if has_arabic:
        # ترجمة سريعة أو اسم تصنيفي افتراضي أنيق بالإنجليزية
        en_topic = "Ultimate Trivia"
    elif topic_clean:
        en_topic = topic_clean.title()
    else:
        en_topic = "General Knowledge"

    hashtag_topic = re.sub(r'[^a-zA-Z0-9]', '', en_topic)
    if not hashtag_topic:
        hashtag_topic = "TriviaChallenge"

    # العنوان والوصف والهاشتاغات 100% باللغة الإنجليزية حصرياً
    caption = (
        f"🔥 The Ultimate 4-Level Quiz: {en_topic}! 🧠\n\n"
        f"Can you answer all 4 questions correctly, especially the IMPOSSIBLE one? 😱\n\n"
        f"1️⃣ Level 1: Easy\n"
        f"2️⃣ Level 2: Medium\n"
        f"3️⃣ Level 3: Hard\n"
        f"4️⃣ Level 4: Impossible 💀\n\n"
        f"How many questions did you get right? Drop your score below! 👇\n\n"
        f"#Quiz #Trivia #Challenge #ViralShorts #BrainTeaser #ImpossibleQuiz #{hashtag_topic}"
    )

    bot_token = CONFIG.get("bot_token")
    channel_id = CONFIG.get("channel_id")
    url = f"https://api.telegram.org/bot{bot_token}/sendVideo"

    file_size_mb = os.path.getsize(video_path) / (1024 * 1024)
    upload_file = video_path
    temp_comp = None

    if file_size_mb > 24.0:
        print(f"   ⚙️ تجهيز نسخة سريعة للرفع لضمان الوصول الفوري...")
        temp_comp = os.path.join(os.path.dirname(video_path), "tele_quiz_upload.mp4")
        comp_cmd = [
            "ffmpeg", "-y", "-loglevel", "error",
            "-i", video_path,
            "-c:v", "libx264", "-crf", "23", "-preset", "fast",
            "-c:a", "copy",
            temp_comp
        ]
        try:
            subprocess.run(comp_cmd, check=True)
            upload_file = temp_comp
        except Exception:
            upload_file = video_path

    for attempt in range(1, 4):
        try:
            print(f"   🚀 جاري الرفع (المحاولة {attempt}/3)...")
            with open(upload_file, 'rb') as vf:
                resp = requests.post(
                    url,
                    data={'chat_id': channel_id, 'caption': caption},
                    files={'video': vf},
                    timeout=180
                )
                if resp.json().get("ok"):
                    print("   ✓ تم النشر بنجاح على قناة تيليجرام! 🎉")
                    if temp_comp and os.path.exists(temp_comp):
                        try: os.remove(temp_comp)
                        except: pass
                    return True
        except Exception as e:
            print(f"   ⚠️ تعثر الرفع ({e})...")
            time.sleep(3)
    if temp_comp and os.path.exists(temp_comp):
        try: os.remove(temp_comp)
        except: pass
    return False

# --- 8. دورة الإنتاج الشاملة والمونتاج الدقيق ---
def build_4_levels_quiz_video(custom_topic=""):
    start_time = time.time()
    workspace = os.path.join(os.path.dirname(__file__), "quiz_workspace")
    os.makedirs(workspace, exist_ok=True)

    print("\n" + "="*60)
    print("🎯 [1/5]: جلب الأسئلة والمستويات الأربعة المتوافقة مع الموضوع...")
    print("="*60)
    levels = generate_4_levels_quiz(custom_topic)
    for idx, lvl in enumerate(levels, 1):
        print(f"   Level {idx}: {lvl['level_title']} ➔ {lvl['question']}")

    # تجهيز المؤثرات الصوتية
    fast_tick_wav = os.path.join(workspace, "fast_tick.wav")
    energetic_ding_wav = os.path.join(workspace, "energetic_ding.wav")
    generate_fast_tick_sound(fast_tick_wav)
    generate_energetic_reveal_sound(energetic_ding_wav)

    from pydub import AudioSegment
    tick_audio = AudioSegment.from_file(fast_tick_wav)
    ding_audio = AudioSegment.from_file(energetic_ding_wav)

    print("\n" + "="*60)
    print("🎙️ [2/5]: توليد التعليق الصوتي والهوك الافتتاحي وخاتمة النتيجة...")
    print("="*60)

    # 1. الهوك الافتتاحي (بسرعة 1.2x / +20%)
    intro_text = "Can you answer all four questions correctly, especially the last one?"
    intro_audio_path = os.path.join(workspace, "intro_hook.mp3")
    generate_speech(intro_text, intro_audio_path, rate="+20%")
    intro_audio = AudioSegment.from_file(intro_audio_path)
    intro_dur = intro_audio.duration_seconds

    # استخراج توقيت كلمات الهوك
    intro_words = get_word_timestamps(intro_audio_path)
    if not intro_words:
        tokens = intro_text.replace(",", "").replace("?", "").split()
        tok_dur = intro_dur / len(tokens)
        intro_words = [{"word": w.upper(), "start": i*tok_dur, "end": (i+1)*tok_dur} for i, w in enumerate(tokens)]

    intro_frames_dir = os.path.join(workspace, "intro_frames")
    os.makedirs(intro_frames_dir, exist_ok=True)
    intro_frame_paths = []

    # تقسيم الهوك الافتتاحي إلى شطرين/أشطار من سطر واحد فقط بحجم الخط الكامل
    intro_chunks = split_words_into_single_line_chunks(intro_words, max_w=850)
    print(f"   ✓ تم تقسيم الهوك الافتتاحي إلى {len(intro_chunks)} أشطار كل شطر بسطر واحد دون تصغير الخط.")

    for ch_idx, chunk in enumerate(intro_chunks):
        for w_idx_in_ch, w in enumerate(chunk):
            fpath = os.path.join(intro_frames_dir, f"hook_ch_{ch_idx}_w_{w_idx_in_ch}.png")
            img = render_chunk_karaoke_frame(chunk, w_idx_in_ch)
            img.save(fpath, 'PNG')
            intro_frame_paths.append((fpath, float(w["start"]), float(w["end"])))

    # 2. توليد خط الصوت لكل مستوى ومزامنة نطق الكلمات كلمة بكلمة
    level_audio_blocks = []
    timeline_markers = []
    current_time_offset = intro_dur

    for idx, lvl in enumerate(levels, 1):
        # فصل صوت إعلان المستوى عن صوت السؤال لضمان توقيت ومزامنة متطابقة بنسبة 100%
        ann_file = os.path.join(workspace, f"lvl_{idx}_ann.mp3")
        q_file = os.path.join(workspace, f"lvl_{idx}_q.mp3")
        
        generate_speech(lvl['level_announcement'], ann_file, rate="+10%")
        generate_speech(lvl['question'], q_file, rate="+5%")
        
        ann_audio = AudioSegment.from_file(ann_file)
        q_speech_audio = AudioSegment.from_file(q_file)
        mid_pause = AudioSegment.silent(duration=250)
        
        # استخراج توقيتات الكلمات الدقيقة لنطق السؤال فقط عبر Whisper
        q_whisper_words = get_word_timestamps(q_file)
        if not q_whisper_words:
            raw_tokens = lvl['question'].replace("?", "").replace(",", "").split()
            tok_d = q_speech_audio.duration_seconds / max(1, len(raw_tokens))
            q_whisper_words = [{"word": w.upper(), "start": i*tok_d, "end": (i+1)*tok_d} for i, w in enumerate(raw_tokens)]

        lvl_speech_audio = ann_audio + mid_pause + q_speech_audio
        speech_dur = lvl_speech_audio.duration_seconds
        ann_offset_seconds = ann_audio.duration_seconds + 0.25  # إزاحة بداية نطق السؤال

        # فترة الانتظار: 2.0 ثانية بالتحديد
        wait_dur = 2.0
        countdown_silence = AudioSegment.silent(duration=int(wait_dur * 1000))
        # تكتكة سريعة مكثفة كل 250ms (4 تكتكات في الثانية)
        for t_step in range(0, int(wait_dur * 1000), 250):
            countdown_silence = countdown_silence.overlay(tick_audio, position=t_step)

        # نغمة الإعلان الحماسية فقط بدون أي كلام إضافي
        reveal_block = ding_audio
        post_reveal_silence = AudioSegment.silent(duration=1200)

        combined_lvl = lvl_speech_audio + countdown_silence + reveal_block + post_reveal_silence
        lvl_total_dur = len(combined_lvl) / 1000.0

        q_start = current_time_offset
        timer_start = q_start + speech_dur
        reveal_time = timer_start + wait_dur
        lvl_end = q_start + lvl_total_dur

        timeline_markers.append({
            "index": idx,
            "level": lvl,
            "q_start": q_start,
            "timer_start": timer_start,
            "reveal_time": reveal_time,
            "lvl_end": lvl_end,
            "q_whisper_words": q_whisper_words,
            "ann_offset": ann_offset_seconds,
            "speech_dur": speech_dur
        })

        level_audio_blocks.append(combined_lvl)
        current_time_offset = lvl_end

    # 3. الخاتمة الصوتية (سؤال الجمهور: How many questions did you manage to get right?)
    outro_text = "How many questions did you manage to get right? Drop your score in the comments!"
    outro_audio_file = os.path.join(workspace, "outro_voice.mp3")
    generate_speech(outro_text, outro_audio_file, rate="+10%")
    raw_outro_audio = AudioSegment.from_file(outro_audio_file)

    outro_words = get_word_timestamps(outro_audio_file)
    if outro_words:
        # تحديد اللحظة الدقيقة لنهاية آخر كلمة منطوقة في الخاتمة
        last_spoken_time = max(float(w["end"]) for w in outro_words)
        # اقتطاع الصوت فوراً بعد نهاية الكلمة المنطوقة مع مهلة 0.3 ثانية بالضبط (بدون أي صمت صامت مريب)
        trimmed_dur_ms = int((last_spoken_time + 0.30) * 1000)
        outro_audio = raw_outro_audio[:trimmed_dur_ms]
    else:
        otokens = outro_text.replace("?", "").replace("!", "").split()
        ot_d = raw_outro_audio.duration_seconds / len(otokens)
        outro_words = [{"word": w.upper(), "start": i*ot_d, "end": (i+1)*ot_d} for i, w in enumerate(otokens)]
        outro_audio = raw_outro_audio

    outro_dur = outro_audio.duration_seconds
    outro_start = current_time_offset
    outro_end = outro_start + outro_dur

    outro_frame_paths = []
    outro_frames_dir = os.path.join(workspace, "outro_frames")
    os.makedirs(outro_frames_dir, exist_ok=True)

    outro_chunks = split_words_into_single_line_chunks(outro_words, max_w=850)
    for ch_idx, chunk in enumerate(outro_chunks):
        for w_idx_in_ch, w in enumerate(chunk):
            fpath = os.path.join(outro_frames_dir, f"outro_ch_{ch_idx}_w_{w_idx_in_ch}.png")
            img = render_chunk_karaoke_frame(chunk, w_idx_in_ch)
            img.save(fpath, 'PNG')
            outro_frame_paths.append((fpath, outro_start + float(w["start"]), outro_start + float(w["end"])))

    # دمج الصوت الكلي النهائي
    speech_track = intro_audio
    for blk in level_audio_blocks:
        speech_track += blk
    speech_track += outro_audio

    total_track_dur = len(speech_track) / 1000.0

    # توليد ودمج الموسيقى الخلفية الحماسية (Upbeat Suspense BGM)
    bgm_wav = os.path.join(workspace, "suspense_bgm.wav")
    generate_suspense_bgm(bgm_wav, duration_sec=total_track_dur)
    bgm_audio = AudioSegment.from_file(bgm_wav)
    # مزج الموسيقى الخلفية مع خط التعليق الصوتي والمؤثرات
    full_audio = speech_track.overlay(bgm_audio)

    full_audio_path = os.path.join(workspace, "final_4levels_audio.mp3")
    full_audio.export(full_audio_path, format="mp3")
    total_video_dur = round(len(full_audio) / 1000.0, 3)
    print(f"   ✓ مدة الفيديو الإجمالية حتى نهاية الصوت (+0.3s): {total_video_dur}s (شاملة الموسيقى التصويرية).")

    # --- 4. تجهيز صور الأسئلة والخيارات والكلمات المنطوقة ---
    print("\n" + "="*60)
    print("🎨 [3/5]: توليد بطاقات السؤال مع تلوين الكلمة المنطوقة بالأصفر...")
    print("="*60)
    ui_assets = []
    q_frames_dir = os.path.join(workspace, "q_frames")
    os.makedirs(q_frames_dir, exist_ok=True)

    for m in timeline_markers:
        idx = m["index"]
        lvl = m["level"]
        q_text = lvl["question"]
        lvl_title = lvl["level_title"]

        # بطاقة السؤال الافتراضية الثابتة
        q_card_default = os.path.join(workspace, f"ui_q_{idx}_default.png")
        img_def = create_question_card_frame(lvl_title, q_text, active_word_index=-1)
        img_def.save(q_card_default, 'PNG')

        # توليد إطارات تلوين الكلمات بالأصفر المتزامنة 100% مع نطق السؤال
        q_words_list = q_text.split()
        whisper_tokens = m.get("q_whisper_words", [])
        ann_offset = m.get("ann_offset", 0.0)
        q_base_time = m["q_start"] + ann_offset

        word_frames = []
        for w_idx in range(len(q_words_list)):
            fpath = os.path.join(q_frames_dir, f"q_{idx}_w_{w_idx}.png")
            img_w = create_question_card_frame(lvl_title, q_text, active_word_index=w_idx)
            img_w.save(fpath, 'PNG')

            if w_idx < len(whisper_tokens):
                w_tok = whisper_tokens[w_idx]
                w_start = q_base_time + float(w_tok["start"])
                w_end = q_base_time + float(w_tok["end"])
            else:
                last_end = whisper_tokens[-1]["end"] if whisper_tokens else 0.0
                step = 0.35
                w_start = q_base_time + float(last_end) + (w_idx - len(whisper_tokens)) * step
                w_end = w_start + step

            word_frames.append((fpath, w_start, w_end))

        opt_normal = os.path.join(workspace, f"ui_opt_normal_{idx}.png")
        opt_revealed = os.path.join(workspace, f"ui_opt_revealed_{idx}.png")
        create_options_card(lvl["options"], revealed=False, correct_opt=lvl["correct"], output_png=opt_normal)
        create_options_card(lvl["options"], revealed=True, correct_opt=lvl["correct"], output_png=opt_revealed)

        # توليد مقطع فيديو متحرك لشريط العداد التنازلي التفاعلي لهذا المستوى (2 ثانية بـ 30 إطار/ثانية)
        timer_clip_path = os.path.join(workspace, f"timer_bar_lvl_{idx}.mp4")
        generate_countdown_bar_video(timer_clip_path, duration=2.0, fps=30, width=1000, height=14)

        ui_assets.append({
            "idx": idx,
            "q_card_default": q_card_default,
            "word_frames": word_frames,
            "opt_normal": opt_normal,
            "opt_revealed": opt_revealed,
            "timer_clip": timer_clip_path,
            "marker": m
        })

    # --- 5. تجهيز فيديو الجيم بلاي في المنتصف ---
    print("\n" + "="*60)
    print("🎮 [4/5]: اقتطاع وتجهيز فيديو الجيم بلاي بدقة عالية للمنتصف...")
    print("="*60)
    gameplay_path = next((p for p in CONFIG.get("gameplay_sources", []) if os.path.exists(p)), None)
    slice_path = os.path.join(workspace, "gameplay_middle.mp4")

    if gameplay_path:
        probe = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", gameplay_path],
            stdout=subprocess.PIPE, text=True
        )
        src_dur = float(probe.stdout.strip())
        max_start = max(0, src_dur - total_video_dur - 4.0)
        start_cut = random.uniform(5.0, max_start) if max_start > 5.0 else 0.0
        cut_cmd = [
            "ffmpeg", "-y", "-loglevel", "error",
            "-ss", f"{start_cut:.2f}", "-t", f"{total_video_dur:.2f}",
            "-i", gameplay_path,
            "-vf", "scale=1386:780:force_original_aspect_ratio=increase,crop=1080:780,setsar=1,fps=30",
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18",
            "-an", slice_path
        ]
        subprocess.run(cut_cmd, check=True)
    else:
        gen_cmd = [
            "ffmpeg", "-y", "-loglevel", "error",
            "-f", "lavfi", "-i", f"color=c=0x10131E:s=1080x780:r=30:d={total_video_dur:.2f}",
            "-c:v", "libx264", "-preset", "ultrafast", slice_path
        ]
        subprocess.run(gen_cmd, check=True)

    # --- 6. المونتاج المتزامن لخط العداد والطبقات (FFmpeg Pipeline) ---
    print("\n" + "="*60)
    print("🎬 [5/5]: رندرة الطبقات، شريط العداد التنازلي التفاعلي، والخاتمة...")
    print("="*60)
    final_output = os.path.join(workspace, f"Quiz_4Levels_{int(time.time())}.mp4")

    # قائمة المدخلات الأساسية
    inputs = [
        "-f", "lavfi", "-i", f"color=c=0x0B0D13:s=1080x1920:r=30:d={total_video_dur:.2f}",
        "-i", slice_path,
        "-i", full_audio_path
    ]

    # إضافة فريمات الهوك الافتتاحي
    hook_input_start = 3
    for fpath, _, _ in intro_frame_paths:
        inputs.extend(["-i", fpath])

    # إضافة فريمات الخاتمة (Outro)
    outro_input_start = hook_input_start + len(intro_frame_paths)
    for fpath, _, _ in outro_frame_paths:
        inputs.extend(["-i", fpath])

    # إضافة صور المستويات (بطاقة السؤال الأساسية، الخيارات العادية، الخيارات المضيئة)
    level_cards_start = outro_input_start + len(outro_frame_paths)
    for u in ui_assets:
        inputs.extend(["-i", u["q_card_default"], "-i", u["opt_normal"], "-i", u["opt_revealed"]])

    # إضافة إطارات الكلمات المنطوقة للسؤال
    word_frames_start = level_cards_start + (len(ui_assets) * 3)
    all_word_frame_entries = []
    for u in ui_assets:
        for fpath, st, et in u["word_frames"]:
            inputs.extend(["-i", fpath])
            all_word_frame_entries.append((len(all_word_frame_entries), st, et))

    # إضافة مقاطع فيديو شريط العداد التنازلي التفاعلي لكل مستوى
    timer_clips_start = word_frames_start + len(all_word_frame_entries)
    for u in ui_assets:
        inputs.extend(["-i", u["timer_clip"]])

    filter_chains = []
    # وضع فيديو الجيم بلاي في المنتصف
    filter_chains.append("[1:v]setpts=PTS-STARTPTS[gp]; [0:v][gp]overlay=0:560[v_base]")
    cur_v = "v_base"

    # 1. طبقات الهوك الافتتاحي
    for idx_f, (_, w_st, w_et) in enumerate(intro_frame_paths):
        in_idx = hook_input_start + idx_f
        next_v = f"v_hk_{idx_f}"
        filter_chains.append(f"[{cur_v}][{in_idx}:v]overlay=0:980:enable='between(t,{w_st:.2f},{w_et:.2f})'[{next_v}]")
        cur_v = next_v

    # 2. طبقات بطاقات المستويات الأربعة
    for idx_u, u in enumerate(ui_assets):
        m = u["marker"]
        q_idx = level_cards_start + (idx_u * 3)
        opt_norm_idx = q_idx + 1
        opt_rev_idx = q_idx + 2

        v_q = f"v_q_{idx_u}"
        v_opt_norm = f"v_optn_{idx_u}"
        v_opt_rev = f"v_optr_{idx_u}"

        # كارد السؤال الثابت يظهر طوال فترة المستوى
        filter_chains.append(f"[{cur_v}][{q_idx}:v]overlay=0:20:enable='between(t,{m['q_start']:.2f},{m['lvl_end']:.2f})'[{v_q}]")
        # الخيارات العادية تظهر من بداية السؤال حتى كشف الإجابة (انتظار 2 ثانية)
        filter_chains.append(f"[{v_q}][{opt_norm_idx}:v]overlay=0:1360:enable='between(t,{m['q_start']:.2f},{m['reveal_time']:.2f})'[{v_opt_norm}]")
        # الخيار المضيء بالأخضر يظهر من لحظة الكشف حتى نهاية المستوى
        filter_chains.append(f"[{v_opt_norm}][{opt_rev_idx}:v]overlay=0:1360:enable='between(t,{m['reveal_time']:.2f},{m['lvl_end']:.2f})'[{v_opt_rev}]")
        cur_v = v_opt_rev

    # 3. إظهار تلوين الكلمة المنطوقة بالأصفر فوق كارد السؤال
    for wf_idx, st, et in all_word_frame_entries:
        input_file_idx = word_frames_start + wf_idx
        next_vw = f"v_qw_{wf_idx}"
        filter_chains.append(f"[{cur_v}][{input_file_idx}:v]overlay=0:20:enable='between(t,{st:.2f},{et:.2f})'[{next_vw}]")
        cur_v = next_vw

    # 4. طبقات الخاتمة وسؤال الجمهور في النهاية
    for idx_o, (_, o_st, o_et) in enumerate(outro_frame_paths):
        in_idx = outro_input_start + idx_o
        next_v = f"v_outr_{idx_o}"
        filter_chains.append(f"[{cur_v}][{in_idx}:v]overlay=0:980:enable='between(t,{o_st:.2f},{o_et:.2f})'[{next_v}]")
        cur_v = next_v

    # 5. خطوط الفواصل وخط العداد التنازلي التفاعلي الممتد بالتزامن مع فترة الانتظار (2s)
    v_lines = "v_dividers"
    filter_chains.append(f"[{cur_v}]drawbox=x=0:y=558:w=1080:h=4:color=0x28314A:t=fill[v_d1]; [v_d1]drawbox=x=0:y=1340:w=1080:h=4:color=0x28314A:t=fill[{v_lines}]")
    cur_v = v_lines

    for idx_u, u in enumerate(ui_assets):
        m = u["marker"]
        t_s = m["timer_start"]
        t_e = m["reveal_time"]
        timer_in_idx = timer_clips_start + idx_u
        v_timer_delayed = f"v_tdelay_{idx_u}"
        v_bar = f"v_bar_{idx_u}"

        # تأخير زمن مقطع العداد ليبدأ عند t_s بدقة متناهية
        filter_chains.append(f"[{timer_in_idx}:v]setpts=PTS-STARTPTS+{t_s:.2f}/TB[{v_timer_delayed}]")
        # دمج شريط العداد التنازلي التفاعلي المتحرك بسلاسة كاملة طوال فترة الـ 2 ثانية
        filter_chains.append(f"[{cur_v}][{v_timer_delayed}]overlay=40:1344:enable='between(t,{t_s:.2f},{t_e:.2f})'[{v_bar}]")
        cur_v = v_bar

    full_filter = ";".join(filter_chains)

    render_cmd = [
        "ffmpeg", "-y", "-loglevel", "info"
    ] + inputs + [
        "-filter_complex", full_filter,
        "-map", f"[{cur_v}]", "-map", "2:a",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        final_output
    ]

    print("   ⚡ جاري الرندرة والتصدير عالي الدقة عبر FFmpeg...")
    subprocess.run(render_cmd, check=True)

    # --- 7. دمج فيديو الخاتمة الدائمة في النهاية (Permanent Outro Video) ---
    outro_video_path = CONFIG.get("outro_video", r"C:\Users\User\OneDrive\Desktop\resilt\6993530118_tk_2x.mp4")
    video_to_upload = final_output

    if outro_video_path and os.path.exists(outro_video_path):
        print("\n" + "="*60)
        print("🎬 [خاتمة الفيديو]: دمج فيديو النهاية الإضافي بسلاسة تامة...")
        print("="*60)
        with_outro_path = os.path.join(workspace, f"Quiz_4Levels_Complete_{int(time.time())}.mp4")
        stitch_cmd = [
            "ffmpeg", "-y", "-loglevel", "error",
            "-i", final_output,
            "-i", outro_video_path,
            "-filter_complex",
            "[0:v]scale=1080:1920,setsar=1,fps=30[v0]; [0:a]aresample=44100,aformat=channel_layouts=stereo[a0]; "
            "[1:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30[v1]; [1:a]aresample=44100,aformat=channel_layouts=stereo[a1]; "
            "[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a]",
            "-map", "[v]", "-map", "[a]",
            "-c:v", "libx264", "-preset", "fast", "-crf", "18",
            "-c:a", "aac", "-b:a", "192k",
            with_outro_path
        ]
        try:
            subprocess.run(stitch_cmd, check=True)
            if os.path.exists(with_outro_path) and os.path.getsize(with_outro_path) > 1000:
                video_to_upload = with_outro_path
                print("   ✓ تم دمج فيديو النهاية بنجاح تام!")
        except Exception as e_stitch:
            print(f"   ⚠️ تعذر دمج فيديو النهاية ({e_stitch})، سيتم اعتماد المقطع الأساسي.")

    elapsed = round(time.time() - start_time, 2)
    print("\n" + "="*60)
    print(f"🎉 تم إنتاج فيديو الكويز بالمزامنة والتلوين التفاعلي والخاتمة بنجاح!")
    print(f"⏱️ استغرقت العملية: {elapsed} ثانية.")
    print(f"📁 مسار الفيديو: {video_to_upload}")
    print("="*60)

    # النشر التلقائي السريع على تيليجرام
    upload_to_telegram(video_to_upload, custom_topic)

    # فتح المقطع تلقائياً للمعاينة
    try:
        os.startfile(video_to_upload)
    except:
        pass

    return video_to_upload

def main():
    import argparse
    parser = argparse.ArgumentParser(description="AI 4-Level Quiz Maker")
    parser.add_argument("--topic", type=str, default="", help="Topic of the quiz")
    args, _ = parser.parse_known_args()

    topic = args.topic.strip()
    if not topic:
        print("\n=== 🎯 مولد تحدي الـ 4 مستويات (4-Level Quiz & Gameplay Shorts) 🎯 ===")
        print("المستويات: 1. Easy | 2. Medium | 3. Hard | 4. Impossible")
        topic = input("\nما هو موضوع التحدي؟ (مثال: Football, Space, Geography, History) > ").strip()

    build_4_levels_quiz_video(topic)

if __name__ == "__main__":
    main()
