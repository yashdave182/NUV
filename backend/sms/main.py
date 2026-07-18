from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from google import genai
from groq import Groq
import re
import json
import os
import uuid
import threading
import math
import hashlib
from datetime import datetime, timedelta

app = FastAPI()

# ---- Dynamic API Keys ----
GROQ_API_KEYS = []
i = 1
while True:
    key = os.getenv(f"GROQ_API_KEY_{i}")
    if not key:
        break
    GROQ_API_KEYS.append(key)
    i += 1
print(f"Loaded {len(GROQ_API_KEYS)} Groq API key(s).")

GEMINI_API_KEYS = []
i = 1
while True:
    key = os.getenv(f"GEMINI_API_KEY_{i}")
    if not key:
        break
    GEMINI_API_KEYS.append(key)
    i += 1
print(f"Loaded {len(GEMINI_API_KEYS)} Gemini API key(s).")

GROQ_MODEL   = "llama-3.3-70b-versatile"
GEMINI_MODEL = "gemini-2.0-flash"

REPLIES_FILE = "replies.json"
HISTORY_FILE = "chat_history.json"
REPORTS_DIR  = "reports"

MAX_HISTORY_PER_USER    = 10
SESSION_TIMEOUT_MINUTES = 30

os.makedirs(REPORTS_DIR, exist_ok=True)
print(f"Reports directory: {os.path.abspath(REPORTS_DIR)}")

replies_lock = threading.Lock()
history_lock = threading.Lock()

recent_messages      = {}
recent_messages_lock = threading.Lock()
DEDUP_WINDOW_SECONDS = 10

bot_sent_replies = set()
bot_sent_lock    = threading.Lock()

def remember_bot_reply(message):
    with bot_sent_lock:
        bot_sent_replies.add(message.strip())
        if len(bot_sent_replies) > 500:
            bot_sent_replies.pop()

def is_bot_echo(message):
    with bot_sent_lock:
        return message.strip() in bot_sent_replies

BLACKLISTED_SENDERS = ["VZ-ViCARE-S","VM-","VZ-","AD-","TM-","TA-","ALERT","NOTIF"]

def is_blacklisted_sender(phone):
    for prefix in BLACKLISTED_SENDERS:
        if str(phone).startswith(prefix) or str(phone).upper().startswith(prefix.upper()):
            return True
    return False

def is_duplicate(phone, message):
    key = f"{phone}|{message}"
    now = datetime.utcnow().timestamp()
    with recent_messages_lock:
        expired = [k for k, t in recent_messages.items() if now - t > DEDUP_WINDOW_SECONDS]
        for k in expired:
            del recent_messages[k]
        if key in recent_messages:
            return True
        recent_messages[key] = now
        return False

def safe_read_json(path, default):
    try:
        with open(path, "r") as f:
            content = f.read().strip()
            if not content:
                return default
            return json.loads(content)
    except (json.JSONDecodeError, FileNotFoundError):
        return default

def init_file(path, default):
    if not os.path.exists(path):
        with open(path, "w") as f:
            json.dump(default, f)

init_file(REPLIES_FILE, {"queue": []})
init_file(HISTORY_FILE, {})


# ============================================================
# LANGUAGE DETECTION
# ============================================================

LANGUAGE_MODES = {
    "Hindi":     "Hindi (pure Devanagari)",
    "Gujarati":  "Gujarati (pure Gujarati script)",
    "English":   "English",
    "Hinglish":  "Hinglish (Hindi in Roman letters)",
    "Gujlish":   "Gujlish (Gujarati in Roman letters)",
    "Marathish": "Marathish (Marathi in Roman letters)",
    "Punjabish": "Punjabish (Punjabi in Roman letters)",
    "Tamilish":  "Tamilish (Tamil in Roman letters)",
    "Teluguish": "Teluguish (Telugu in Roman letters)",
    "Kannadish": "Kannadish (Kannada in Roman letters)",
    "Bengalish": "Bengalish (Bengali in Roman letters)",
    "Marathi":   "Marathi (Devanagari script)",
    "Punjabi":   "Punjabi (Gurmukhi script)",
    "Tamil":     "Tamil script",
    "Telugu":    "Telugu script",
    "Kannada":   "Kannada script",
    "Bengali":   "Bengali script",
    "Odia":      "Odia script",
    "Urdu":      "Urdu script",
}

# Unique Gujarati Roman words — not present in Hindi
GUJLISH_UNIQUE = {
    "kem","cho","chhe","che","kemcho","kemo","kevi","kevo","kevu","keva",
    "shu","su","kyare","kyarey","kyan","nathi","thayu","thashe","thase",
    "chadvo","chadvu","chadyo","chadhu","karvu","karvanu","javu","jaiye","javanu",
    "aavvu","aavshe","aavyo","levu","lidhu","lese","devu","didhu","dese",
    "joie","joia","jovu","joyu","kahvu","malvu","malse","malyu","samjvu","samjyo",
    "shikhvu","shikhvo","hatu","hati","hathu","tame","tamne","tamaro","tamari",
    "tamara","tamaru","ame","amne","apde","ene","ena","eni","enu","maru","mara",
    "pote","rite","reete","pachi","pachhi","agau","have","havey",
    "badhu","badha","badhi","ghanu","ghanuj","ochhu","saras","mathi",
    "ama","tema","jema","pahad","pahaad","dungar","pak","pako","khaad",
    "vij","yojna","rupiya","aabhar","aavjo","mare","mane","pan","joi",
    "ben","bhen","bapu","kaka","kaki","vaav","talavdi","talav","sheri",
    "mun","dukhaave","taav","tav","vaid","aushadh","varsha","mokanu","vavtar",
    "lani","aaje","aje","parchhe","parmothe","saanje","sanje","ratre","tran",
    "kalaak","bhaat","shaak","dudh","mirchu","subsidi","karj","vima",
}

# Unique Hindi Roman words — not present in Gujarati
HINGLISH_UNIQUE = {
    "kya","hai","hain","nahi","nahin","mera","meri","mujhe","tumhe",
    "aap","tum","yeh","woh","kaise","kyun","kab","kahan",
    "chahiye","karein","batao","samjho","accha","theek","galat",
    "bijli","sadak","yojana","subsidy","matlab","samajh","bahut","zyada",
    "behen","chacha","shukriya","parso","subah","shaam","rupee",
    "pehle","fasal","khad","phir","thoda","dawai",
}

def detect_language(text: str) -> dict:
    script_counts = {
        "Gujarati":0,"Hindi":0,"Punjabi":0,"Bengali":0,
        "Tamil":0,"Telugu":0,"Kannada":0,"Odia":0,"Urdu":0,
    }
    for char in text:
        cp = ord(char)
        if   0x0A80 <= cp <= 0x0AFF: script_counts["Gujarati"] += 1
        elif 0x0900 <= cp <= 0x097F: script_counts["Hindi"]    += 1
        elif 0x0A00 <= cp <= 0x0A7F: script_counts["Punjabi"]  += 1
        elif 0x0980 <= cp <= 0x09FF: script_counts["Bengali"]  += 1
        elif 0x0B80 <= cp <= 0x0BFF: script_counts["Tamil"]    += 1
        elif 0x0C00 <= cp <= 0x0C7F: script_counts["Telugu"]   += 1
        elif 0x0C80 <= cp <= 0x0CFF: script_counts["Kannada"]  += 1
        elif 0x0B00 <= cp <= 0x0B7F: script_counts["Odia"]     += 1
        elif 0x0600 <= cp <= 0x06FF: script_counts["Urdu"]     += 1

    max_script = max(script_counts, key=script_counts.get)
    if script_counts[max_script] > 0:
        return {"mode":max_script,"label":LANGUAGE_MODES.get(max_script,max_script),
                "script":"native","base":max_script}

    words         = set(re.findall(r'\b[a-zA-Z]+\b', text.lower()))
    gujlish_hits  = len(words & GUJLISH_UNIQUE)
    hinglish_hits = len(words & HINGLISH_UNIQUE)

    print(f"[LANG] guj={gujlish_hits} hin={hinglish_hits} words={words}")

    if gujlish_hits == 0 and hinglish_hits == 0:
        return {"mode":"English","label":LANGUAGE_MODES["English"],"script":"roman","base":"English"}
    if gujlish_hits > hinglish_hits:
        return {"mode":"Gujlish","label":LANGUAGE_MODES["Gujlish"],"script":"roman","base":"Gujarati"}
    if hinglish_hits > gujlish_hits:
        return {"mode":"Hinglish","label":LANGUAGE_MODES["Hinglish"],"script":"roman","base":"Hindi"}
    return {"mode":"Gujlish","label":LANGUAGE_MODES["Gujlish"],"script":"roman","base":"Gujarati"}

def get_reply_language_instruction(lang_info: dict) -> str:
    mode = lang_info["mode"]
    instructions = {
        "Hindi":     "Reply in Hindi using Devanagari script. Simple and clear.",
        "Gujarati":  "Reply in Gujarati using Gujarati script. Simple and clear.",
        "Marathi":   "Reply in Marathi using Devanagari script.",
        "Punjabi":   "Reply in Punjabi using Gurmukhi script.",
        "Bengali":   "Reply in Bengali using Bengali script.",
        "Tamil":     "Reply in Tamil using Tamil script.",
        "Telugu":    "Reply in Telugu using Telugu script.",
        "Kannada":   "Reply in Kannada using Kannada script.",
        "Odia":      "Reply in Odia using Odia script.",
        "Urdu":      "Reply in Urdu using Roman script.",
        "Hinglish":  "User writes Hinglish (Hindi in Roman). Reply in SAME Hinglish. NO Devanagari. Example: 'Fasal ke liye urea khad use karo, 2 bag per bigha.'",
        "Gujlish":   "User writes Gujlish (Gujarati in Roman). Reply in SAME Gujlish. NO Gujarati script. Example: 'Pak mate urea khaad vapro, bigha ma 2 bag kaafi chhe.'",
        "Marathish": "Reply in Marathi Roman letters only.",
        "Punjabish": "Reply in Punjabi Roman letters only.",
        "Tamilish":  "Reply in Tamil Roman letters only.",
        "Teluguish": "Reply in Telugu Roman letters only.",
        "Kannadish": "Reply in Kannada Roman letters only.",
        "Bengalish": "Reply in Bengali Roman letters only.",
        "English":   "Reply in simple clear English.",
    }
    return instructions.get(mode, f"Reply in {mode}. Keep it simple.")

# Map language mode to its full native script name for report header
LANGUAGE_DISPLAY_NAME = {
    "Hindi":     "हिंदी",
    "Gujarati":  "ગુજરાતી",
    "Marathi":   "मराठी",
    "Punjabi":   "ਪੰਜਾਬੀ",
    "Bengali":   "বাংলা",
    "Tamil":     "தமிழ்",
    "Telugu":    "తెలుగు",
    "Kannada":   "ಕನ್ನಡ",
    "Odia":      "ଓଡ଼ିଆ",
    "Urdu":      "اردو",
    "Hinglish":  "Hinglish",
    "Gujlish":   "Gujlish",
    "Marathish": "Marathish",
    "Punjabish": "Punjabish",
    "Tamilish":  "Tamilish",
    "Teluguish": "Teluguish",
    "Kannadish": "Kannadish",
    "Bengalish": "Bengalish",
    "English":   "English",
}


# ---- SMS Cleaner ----
def clean_for_sms(text, limit=155):
    text = re.sub(r"[*_`#]+", "", text)
    text = text.replace("\r\n"," ").replace("\n"," ").replace("\r"," ").replace("\t"," ")
    text = re.sub(r"\s*[-•●]\s*", " ", text)
    text = re.sub(r" +", " ", text).strip()
    if len(text) <= limit:
        return text
    for punct in ["।",".",  "!", "?", ";", ","]:
        idx = text.rfind(punct, 0, limit)
        if idx != -1:
            return text[:idx+1].strip()
    idx = text.rfind(" ", 0, limit)
    return text[:idx].strip() if idx != -1 else text[:limit]


# ---- Session Helpers ----
def load_history():
    with history_lock:
        return safe_read_json(HISTORY_FILE, {})

def save_history(history):
    with history_lock:
        with open(HISTORY_FILE, "w") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

def get_user_session(phone):
    history   = load_history()
    user_data = history.get(phone)
    if user_data:
        last_active = datetime.fromisoformat(user_data["last_active"])
        if datetime.utcnow() - last_active > timedelta(minutes=SESSION_TIMEOUT_MINUTES):
            del history[phone]
            save_history(history)
            return {"messages":[],"last_active":datetime.utcnow().isoformat(),"language":"English"}
        return user_data
    return {"messages":[],"last_active":datetime.utcnow().isoformat(),"language":"English"}

def update_user_session(phone, user_message, bot_reply, language_mode):
    history = load_history()
    session = history.get(phone, {"messages":[],"last_active":None,"language":language_mode})
    session["messages"].append({"role":"user","text":user_message})
    session["messages"].append({"role":"assistant","text":bot_reply})
    session["last_active"] = datetime.utcnow().isoformat()
    session["language"]    = language_mode
    max_entries = MAX_HISTORY_PER_USER * 2
    if len(session["messages"]) > max_entries:
        session["messages"] = session["messages"][-max_entries:]
    history[phone] = session
    save_history(history)

def build_conversation_context(messages):
    if not messages:
        return "No previous conversation."
    return "\n".join(
        f"{'User' if e['role']=='user' else 'Assistant'}: {e['text']}"
        for e in messages
    )


# ---- AI Providers ----
def try_groq(prompt, max_tokens=80):
    for index, api_key in enumerate(GROQ_API_KEYS):
        try:
            print(f"[Groq] Trying key #{index+1}...")
            client   = Groq(api_key=api_key)
            response = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[{"role":"user","content":prompt}],
                max_tokens=max_tokens,
            )
            raw = response.choices[0].message.content
            print(f"[Groq] OK #{index+1}")
            return raw
        except Exception as e:
            msg = str(e)
            if "429" in msg or "quota" in msg.lower() or "rate" in msg.lower() or "limit" in msg.lower():
                print(f"[Groq] Key #{index+1} rate limited.")
            else:
                print(f"[Groq] Key #{index+1} error: {msg}")
    return None

def try_gemini(prompt):
    for index, api_key in enumerate(GEMINI_API_KEYS):
        try:
            print(f"[Gemini] Trying key #{index+1}...")
            client   = genai.Client(api_key=api_key)
            response = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
            raw      = response.text
            print(f"[Gemini] OK #{index+1}")
            return raw
        except Exception as e:
            msg = str(e)
            if "429" in msg or "quota" in msg.lower() or "rate" in msg.lower():
                print(f"[Gemini] Key #{index+1} quota exceeded.")
            else:
                print(f"[Gemini] Key #{index+1} error: {msg}")
    return None

FALLBACK_MESSAGES = {
    "Hindi":     "क्षमा करें, सेवा अभी उपलब्ध नहीं है।",
    "Gujarati":  "માફ કરશો, સેવા હાલ ઉપલબ્ધ નથી.",
    "Marathi":   "माफ करा, सेवा उपलब्ध नाही.",
    "Punjabi":   "ਮਾਫ਼ ਕਰਨਾ, ਸੇਵਾ ਉਪਲਬਧ ਨਹੀਂ।",
    "Bengali":   "দুঃখিত, পরিষেবা নেই।",
    "Tamil":     "மன்னிக்கவும், சேவை இல்லை.",
    "Telugu":    "క్షమించండి, సేవ లేదు.",
    "Kannada":   "ಕ್ಷಮಿಸಿ, ಸೇವೆ ಲಭ್ಯವಿಲ್ಲ.",
    "Odia":      "କ୍ଷମା, ସେବା ଉପଲବ୍ଧ ନୁହେଁ।",
    "Urdu":      "Maafi, service nahi hai.",
    "Hinglish":  "Sorry bhai, service nahi. Baad mein try karo.",
    "Gujlish":   "Maaf karo, service nathi. Pachhi try karo.",
    "Marathish": "Sorry, service nahi. Nantare try kara.",
    "Punjabish": "Sorry, service nahi. Baad vich try karo.",
    "Tamilish":  "Sorry, service illai. Apuram try pannunga.",
    "Teluguish": "Sorry, service ledu. Tarvata try cheyandi.",
    "Kannadish": "Sorry, service illa. Nachche try madi.",
    "Bengalish": "Sorry, service nei. Pore try koro.",
    "English":   "Sorry, service unavailable. Please try again later.",
}

def generate_reply(prompt, language_mode, max_tokens=80):
    if GROQ_API_KEYS:
        result = try_groq(prompt, max_tokens=max_tokens)
        if result:
            return clean_for_sms(result)
    if GEMINI_API_KEYS:
        result = try_gemini(prompt)
        if result:
            return clean_for_sms(result)
    return FALLBACK_MESSAGES.get(language_mode, FALLBACK_MESSAGES["English"])


# ---- Reply Queue ----
def load_queue():
    with replies_lock:
        return safe_read_json(REPLIES_FILE, {"queue":[]}).get("queue",[])

def save_queue(queue):
    with replies_lock:
        with open(REPLIES_FILE, "w") as f:
            json.dump({"queue":queue}, f, ensure_ascii=False, indent=2)

def enqueue_reply(phone, message, language_mode):
    queue = load_queue()
    queue.append({
        "id":str(uuid.uuid4()), "phone":phone, "message":message,
        "language":language_mode, "created_at":datetime.utcnow().isoformat(), "sent":False
    })
    save_queue(queue)

def dequeue_unsent_replies():
    queue    = load_queue()
    unsent   = [r for r in queue if not r["sent"]]
    sent_ids = {r["id"] for r in unsent}
    for item in queue:
        if item["id"] in sent_ids:
            item["sent"] = True
    sent             = [r for r in queue if r["sent"]]
    unsent_remaining = [r for r in queue if not r["sent"]]
    save_queue(unsent_remaining + sent[-100:])
    return unsent


# ============================================================
# SVG VISUAL BUILDERS — Only render when data is meaningful
# ============================================================

def build_svg_bar_chart(labels, values, unit="", title="", width=340, height=220):
    if not values or len(values) < 2 or max(values) == 0:
        return ""
    max_val   = max(values)
    n         = len(values)
    bar_width = min(44, (width - 70) // n)
    gap       = max(6, (width - 70 - bar_width * n) // (n + 1))
    colors    = ["#2E7D32","#1565C0","#E65100","#AD1457","#6A1B9A","#00695C"]

    bars = ""
    for i, (label, value) in enumerate(zip(labels, values)):
        bar_h = max(4, int((value / max_val) * (height - 70)))
        x     = 55 + gap + i * (bar_width + gap)
        y     = height - 50 - bar_h
        color = colors[i % len(colors)]
        bars += (
            f'<rect x="{x}" y="{y}" width="{bar_width}" height="{bar_h}" '
            f'fill="{color}" rx="5" opacity="0.9"/>'
            f'<text x="{x+bar_width//2}" y="{y-6}" text-anchor="middle" '
            f'font-size="11" font-weight="bold" fill="{color}">{value}{unit}</text>'
            f'<text x="{x+bar_width//2}" y="{height-30}" text-anchor="middle" '
            f'font-size="10" fill="#555">{str(label)[:10]}</text>'
        )

    grid = ""
    for step in range(5):
        y_pos = height - 50 - int((step / 4) * (height - 70))
        val   = int((step / 4) * max_val)
        grid += (
            f'<line x1="50" y1="{y_pos}" x2="{width-10}" y2="{y_pos}" '
            f'stroke="#e0e0e0" stroke-width="1" stroke-dasharray="4,3"/>'
            f'<text x="45" y="{y_pos+4}" text-anchor="end" font-size="9" fill="#999">{val}</text>'
        )

    title_el = f'<text x="{width//2}" y="18" text-anchor="middle" font-size="12" font-weight="bold" fill="#333">{title}</text>' if title else ""

    return (
        f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" '
        f'style="width:100%;max-width:{width}px;display:block;margin:12px auto">'
        f'{title_el}{grid}{bars}'
        f'<line x1="50" y1="15" x2="50" y2="{height-50}" stroke="#ccc" stroke-width="1.5"/>'
        f'<line x1="50" y1="{height-50}" x2="{width-10}" y2="{height-50}" stroke="#ccc" stroke-width="1.5"/>'
        f'</svg>'
    )


def build_svg_pie_chart(labels, values, title="", width=300):
    if not values or len(values) < 2:
        return ""
    total = sum(values)
    if total == 0:
        return ""
    colors = ["#2E7D32","#1565C0","#E65100","#AD1457","#6A1B9A","#00695C","#F57F17","#37474F"]
    cx, cy = width // 2, width // 2
    r      = width // 2 - 35
    angle  = -math.pi / 2
    slices = ""
    legends = ""

    for i, (label, value) in enumerate(zip(labels, values)):
        sweep     = (value / total) * 2 * math.pi
        x1, y1    = cx + r * math.cos(angle), cy + r * math.sin(angle)
        x2, y2    = cx + r * math.cos(angle + sweep), cy + r * math.sin(angle + sweep)
        large_arc = 1 if sweep > math.pi else 0
        color     = colors[i % len(colors)]
        pct       = round(value / total * 100)
        slices += (
            f'<path d="M{cx},{cy} L{x1:.1f},{y1:.1f} '
            f'A{r},{r} 0 {large_arc},1 {x2:.1f},{y2:.1f} Z" '
            f'fill="{color}" stroke="white" stroke-width="2.5"/>'
        )
        mid = angle + sweep / 2
        lx  = cx + (r * 0.62) * math.cos(mid)
        ly  = cy + (r * 0.62) * math.sin(mid)
        if pct > 7:
            slices += (
                f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="middle" '
                f'font-size="11" fill="white" font-weight="bold">{pct}%</text>'
            )
        legends += (
            f'<rect x="10" y="{width+14+i*24}" width="14" height="14" fill="{color}" rx="3"/>'
            f'<text x="30" y="{width+25+i*24}" font-size="11" fill="#444">'
            f'{str(label)[:20]} — {value}</text>'
        )
        angle += sweep

    total_h = width + 20 + len(labels) * 24
    title_el = f'<text x="{width//2}" y="18" text-anchor="middle" font-size="12" font-weight="bold" fill="#333">{title}</text>' if title else ""

    return (
        f'<svg viewBox="0 0 {width} {total_h}" xmlns="http://www.w3.org/2000/svg" '
        f'style="width:100%;max-width:{width}px;display:block;margin:12px auto">'
        f'{title_el}{slices}{legends}</svg>'
    )


def build_svg_flowchart(steps, title="", width=340):
    """Vertical step-by-step flowchart — ideal for processes like farming steps"""
    if not steps or len(steps) < 2:
        return ""
    box_h    = 44
    box_w    = width - 40
    gap      = 28
    colors   = ["#1B5E20","#1A237E","#BF360C","#880E4F","#4A148C","#006064"]
    total_h  = len(steps) * (box_h + gap) + 30

    boxes = ""
    for i, step in enumerate(steps):
        y     = 30 + i * (box_h + gap)
        color = colors[i % len(colors)]
        label = str(step)[:45]
        # Box
        boxes += (
            f'<rect x="20" y="{y}" width="{box_w}" height="{box_h}" '
            f'rx="10" fill="{color}" opacity="0.9"/>'
            # Step number circle
            f'<circle cx="44" cy="{y+box_h//2}" r="13" fill="white" opacity="0.25"/>'
            f'<text x="44" y="{y+box_h//2+5}" text-anchor="middle" '
            f'font-size="13" font-weight="bold" fill="white">{i+1}</text>'
            # Step label
            f'<text x="64" y="{y+box_h//2+5}" font-size="12" fill="white" font-weight="500">{label}</text>'
        )
        # Arrow between steps
        if i < len(steps) - 1:
            arrow_y = y + box_h + 2
            mid_x   = width // 2
            boxes += (
                f'<line x1="{mid_x}" y1="{arrow_y}" x2="{mid_x}" y2="{arrow_y+gap-4}" '
                f'stroke="#999" stroke-width="2"/>'
                f'<polygon points="{mid_x-5},{arrow_y+gap-8} {mid_x+5},{arrow_y+gap-8} {mid_x},{arrow_y+gap-2}" '
                f'fill="#999"/>'
            )

    title_el = f'<text x="{width//2}" y="18" text-anchor="middle" font-size="12" font-weight="bold" fill="#333">{title}</text>' if title else ""

    return (
        f'<svg viewBox="0 0 {width} {total_h}" xmlns="http://www.w3.org/2000/svg" '
        f'style="width:100%;max-width:{width}px;display:block;margin:12px auto">'
        f'{title_el}{boxes}</svg>'
    )


def build_svg_comparison(items, title="", width=340):
    """
    Visual comparison card — for comparing options side by side.
    items = [{"label":"Option A","score":80,"note":"Good for sandy soil"},...]
    """
    if not items or len(items) < 2:
        return ""
    bar_h   = 28
    gap     = 14
    colors  = ["#2E7D32","#1565C0","#E65100","#AD1457"]
    total_h = 40 + len(items) * (bar_h + gap)
    max_score = max(it.get("score", 50) for it in items)

    bars = ""
    for i, item in enumerate(items):
        y      = 34 + i * (bar_h + gap)
        score  = item.get("score", 50)
        label  = str(item.get("label",""))[:18]
        note   = str(item.get("note",""))[:30]
        color  = colors[i % len(colors)]
        bw     = int((score / max_score) * (width - 120))
        bars += (
            f'<text x="10" y="{y+20}" font-size="11" font-weight="bold" fill="#333">{label}</text>'
            f'<rect x="100" y="{y+6}" width="{bw}" height="{bar_h-8}" rx="5" fill="{color}" opacity="0.85"/>'
            f'<text x="{100+bw+6}" y="{y+20}" font-size="10" fill="{color}" font-weight="bold">{score}</text>'
            f'<text x="10" y="{y+bar_h+2}" font-size="9" fill="#888">{note}</text>'
        )

    title_el = f'<text x="{width//2}" y="18" text-anchor="middle" font-size="12" font-weight="bold" fill="#333">{title}</text>' if title else ""

    return (
        f'<svg viewBox="0 0 {width} {total_h}" xmlns="http://www.w3.org/2000/svg" '
        f'style="width:100%;max-width:{width}px;display:block;margin:12px auto">'
        f'{title_el}{bars}</svg>'
    )


def render_visual(section: dict) -> str:
    """
    Renders the correct visual based on section type.
    Only renders if data is present and meaningful.
    """
    vtype = section.get("visual_type","")

    if vtype == "bar_chart":
        return build_svg_bar_chart(
            section.get("labels",[]),
            section.get("values",[]),
            section.get("unit",""),
            section.get("visual_title",""),
        )
    elif vtype == "pie_chart":
        return build_svg_pie_chart(
            section.get("labels",[]),
            section.get("values",[]),
            section.get("visual_title",""),
        )
    elif vtype == "flowchart":
        return build_svg_flowchart(
            section.get("steps",[]),
            section.get("visual_title",""),
        )
    elif vtype == "comparison":
        return build_svg_comparison(
            section.get("items",[]),
            section.get("visual_title",""),
        )
    return ""


# ============================================================
# SMART REPORT PROMPT
# ============================================================

def generate_detailed_prompt(message: str, language_mode: str, short_reply: str) -> str:
    """
    Instructs AI to:
    1. Write ALL content in the user's exact language
    2. Only add visuals when they genuinely add value
    3. Choose the RIGHT type of visual for the content
    4. Be detailed, practical, and helpful — not vague
    """

    lang_instruction = {
        "Hindi":     "Write EVERYTHING in Hindi using Devanagari script (हिंदी में लिखें).",
        "Gujarati":  "Write EVERYTHING in Gujarati using Gujarati script (ગુજરાતીમાં લખો).",
        "Marathi":   "Write EVERYTHING in Marathi using Devanagari script.",
        "Punjabi":   "Write EVERYTHING in Punjabi using Gurmukhi script.",
        "Bengali":   "Write EVERYTHING in Bengali script.",
        "Tamil":     "Write EVERYTHING in Tamil script.",
        "Telugu":    "Write EVERYTHING in Telugu script.",
        "Kannada":   "Write EVERYTHING in Kannada script.",
        "Odia":      "Write EVERYTHING in Odia script.",
        "Urdu":      "Write EVERYTHING in Urdu Roman script.",
        "Hinglish":  "Write EVERYTHING in Hinglish (Hindi words in Roman/English letters). No Devanagari.",
        "Gujlish":   "Write EVERYTHING in Gujlish (Gujarati words in Roman/English letters). No Gujarati script.",
        "Marathish": "Write EVERYTHING in Marathi Roman letters.",
        "Punjabish": "Write EVERYTHING in Punjabi Roman letters.",
        "Tamilish":  "Write EVERYTHING in Tamil Roman letters.",
        "Teluguish": "Write EVERYTHING in Telugu Roman letters.",
        "Kannadish": "Write EVERYTHING in Kannada Roman letters.",
        "Bengalish": "Write EVERYTHING in Bengali Roman letters.",
        "English":   "Write EVERYTHING in simple clear English.",
    }.get(language_mode, "Write in English.")

    return f"""You are an expert rural assistant for Indian villagers and farmers.

USER QUESTION: "{message}"
SHORT SMS ANSWER ALREADY SENT: "{short_reply}"

LANGUAGE RULE (CRITICAL): {lang_instruction}
Every single word in title, summary, content, labels, tips — ALL must be in {language_mode}.
Only exception: numbers and units (kg, ml, %, Rs) can stay as-is.

YOUR TASK: Create a DETAILED, PRACTICAL, HELPFUL report that a rural Indian user can actually use.
The report must feel like advice from a knowledgeable, caring local expert — not a generic textbook.

VISUAL RULES (VERY IMPORTANT):
- Only add a visual if it genuinely helps understanding. NOT every section needs one.
- For step-by-step processes (how to do something): use "flowchart"
- For comparing quantities or amounts over time/categories: use "bar_chart"  
- For showing proportions or share of something: use "pie_chart"
- For comparing 2-4 options with scores: use "comparison"
- For plain explanations with no data: set visual_type to "none"
- NEVER add a chart just to fill space. If data is not meaningful, set visual_type to "none".

Return ONLY a valid JSON object. No markdown, no explanation text before or after.

JSON STRUCTURE:
{{
  "title": "specific descriptive title in {language_mode}",
  "summary": "3-4 sentence genuinely helpful summary in {language_mode} — include key facts, numbers, and actionable advice",
  "sections": [
    {{
      "heading": "section heading in {language_mode}",
      "content": "detailed, practical paragraph in {language_mode} — include real numbers, timing, dosage, method etc. Minimum 3-4 sentences.",
      "visual_type": "flowchart | bar_chart | pie_chart | comparison | none",
      "visual_title": "chart title in {language_mode} (only if visual_type is not none)",
      "steps": ["step 1", "step 2", "step 3"],
      "labels": ["label1", "label2"],
      "values": [10, 20],
      "unit": "kg",
      "items": [{{"label": "Option A", "score": 80, "note": "short note"}}]
    }}
  ],
  "tips": [
    "Practical tip 1 in {language_mode} — be specific",
    "Practical tip 2 in {language_mode} — be specific",
    "Practical tip 3 in {language_mode} — be specific"
  ],
  "warning": "Important caution or warning in {language_mode} (if relevant, else empty string)",
  "language": "{language_mode}"
}}

SECTION GUIDELINES based on question type:
- Farming/agriculture: sections = [preparation, method/process with flowchart, quantities with bar_chart, timeline, expected yield]
- Health: sections = [symptoms/cause, remedy, dosage, when to see doctor]
- Machine/repair: sections = [diagnosis, repair steps with flowchart, tools needed, prevention]
- Government scheme: sections = [eligibility, documents needed, how to apply with flowchart, benefit amount with bar_chart]
- General knowledge: sections = [explanation, examples, practical use]

Include 3-5 sections. Make each section GENUINELY USEFUL with specific numbers, timings, and local context for Indian rural users."""


# ============================================================
# HTML REPORT BUILDER
# ============================================================

def build_report_html(data: dict, report_id: str, language_mode: str) -> str:
    lang_display = LANGUAGE_DISPLAY_NAME.get(language_mode, language_mode)

    # Determine text direction
    rtl_langs = {"Urdu"}
    dir_attr  = 'dir="rtl"' if language_mode in rtl_langs else ''

    # Build sections
    sections_html = ""
    for section in data.get("sections", []):
        heading     = section.get("heading", "")
        content     = section.get("content", "")
        visual_type = section.get("visual_type", "none")

        # Render visual only if meaningful
        visual_html = ""
        if visual_type and visual_type != "none":
            svg = render_visual(section)
            if svg:
                visual_html = f'<div class="visual-wrap">{svg}</div>'

        sections_html += f"""
        <div class="card" {dir_attr}>
            <h2>{heading}</h2>
            <p>{content}</p>
            {visual_html}
        </div>"""

    # Tips
    tips     = data.get("tips", [])
    tips_html = ""
    if tips:
        items = "".join(
            f'<li><span class="tip-num">{i+1}</span>{tip}</li>'
            for i, tip in enumerate(tips)
        )
        tips_html = f"""
        <div class="card tips" {dir_attr}>
            <h2>💡 {'Useful Tips' if language_mode=='English' else 'Tips'}</h2>
            <ul>{items}</ul>
        </div>"""

    # Warning box
    warning     = data.get("warning", "").strip()
    warning_html = ""
    if warning:
        warning_html = f"""
        <div class="warning-box" {dir_attr}>
            <span class="warn-icon">⚠️</span>
            <p>{warning}</p>
        </div>"""

    title   = data.get("title", "Report")
    summary = data.get("summary", "")
    date_str = datetime.utcnow().strftime("%d %b %Y")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>{title}</title>
<style>
  /* Reset */
  *{{box-sizing:border-box;margin:0;padding:0}}

  /* Base */
  body{{
    font-family:system-ui,-apple-system,'Segoe UI',sans-serif;
    background:#F1F8E9;
    color:#1a1a1a;
    padding:0;
    margin:0;
    font-size:15px;
    line-height:1.7;
  }}

  /* Header */
  .header{{
    background:linear-gradient(135deg,#1B5E20 0%,#2E7D32 50%,#388E3C 100%);
    color:white;
    padding:24px 20px 20px;
    position:relative;
    overflow:hidden;
  }}
  .header::before{{
    content:'';
    position:absolute;
    top:-40px;right:-40px;
    width:160px;height:160px;
    background:rgba(255,255,255,0.06);
    border-radius:50%;
  }}
  .header::after{{
    content:'';
    position:absolute;
    bottom:-30px;left:-20px;
    width:120px;height:120px;
    background:rgba(255,255,255,0.04);
    border-radius:50%;
  }}
  .header-inner{{position:relative;z-index:1}}
  .lang-badge{{
    display:inline-block;
    background:rgba(255,255,255,0.18);
    border:1px solid rgba(255,255,255,0.3);
    padding:3px 12px;
    border-radius:20px;
    font-size:12px;
    margin-bottom:10px;
    letter-spacing:0.5px;
  }}
  .header h1{{
    font-size:1.35em;
    font-weight:700;
    margin-bottom:10px;
    line-height:1.3;
  }}
  .header .summary{{
    font-size:0.92em;
    opacity:0.92;
    line-height:1.6;
    background:rgba(0,0,0,0.12);
    padding:12px 14px;
    border-radius:10px;
    margin-top:10px;
  }}
  .meta{{
    display:flex;
    gap:12px;
    margin-top:14px;
    font-size:11px;
    opacity:0.75;
    flex-wrap:wrap;
  }}
  .meta span{{
    background:rgba(255,255,255,0.12);
    padding:3px 10px;
    border-radius:12px;
  }}

  /* Content wrapper */
  .content{{padding:16px;max-width:720px;margin:0 auto}}

  /* Print button */
  .btn-print{{
    display:block;
    width:100%;
    padding:14px;
    background:linear-gradient(135deg,#2E7D32,#1B5E20);
    color:white;
    border:none;
    border-radius:14px;
    font-size:15px;
    cursor:pointer;
    margin-bottom:16px;
    font-weight:600;
    letter-spacing:0.3px;
    box-shadow:0 3px 10px rgba(46,125,50,0.3);
  }}
  .btn-print:active{{transform:scale(0.98)}}

  /* Cards */
  .card{{
    background:white;
    border-radius:16px;
    padding:20px;
    margin-bottom:14px;
    box-shadow:0 2px 12px rgba(0,0,0,0.06);
    border-left:4px solid #2E7D32;
  }}
  .card h2{{
    color:#1B5E20;
    font-size:1.05em;
    font-weight:700;
    margin-bottom:10px;
    padding-bottom:8px;
    border-bottom:1px solid #E8F5E9;
  }}
  .card p{{
    color:#333;
    line-height:1.75;
    font-size:14.5px;
  }}

  /* Visual wrapper */
  .visual-wrap{{
    margin-top:16px;
    background:#FAFAFA;
    border-radius:12px;
    padding:12px 8px;
    border:1px solid #E8F5E9;
  }}

  /* Table */
  .table-wrap{{overflow-x:auto;margin-top:12px}}
  table{{width:100%;border-collapse:collapse;font-size:13.5px}}
  th{{
    background:#E8F5E9;
    color:#1B5E20;
    padding:10px 12px;
    text-align:left;
    font-weight:600;
  }}
  td{{padding:10px 12px;border-bottom:1px solid #F1F8E9;color:#333}}
  tr:last-child td{{border-bottom:none}}
  tr:hover td{{background:#F9FBE7}}

  /* Tips */
  .tips h2{{color:#E65100}}
  .tips{{border-left-color:#E65100}}
  .tips ul{{list-style:none;padding:0}}
  .tips li{{
    padding:10px 0 10px 0;
    border-bottom:1px solid #FBE9E7;
    color:#333;
    display:flex;
    gap:10px;
    align-items:flex-start;
    font-size:14px;
  }}
  .tips li:last-child{{border-bottom:none}}
  .tip-num{{
    min-width:26px;
    height:26px;
    background:#E65100;
    color:white;
    border-radius:50%;
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:12px;
    font-weight:700;
    margin-top:2px;
  }}

  /* Warning */
  .warning-box{{
    background:#FFF8E1;
    border:1px solid #FFD54F;
    border-left:4px solid #F57F17;
    border-radius:12px;
    padding:14px 16px;
    margin-bottom:14px;
    display:flex;
    gap:12px;
    align-items:flex-start;
  }}
  .warn-icon{{font-size:20px;margin-top:1px}}
  .warning-box p{{color:#5D4037;font-size:14px;line-height:1.6}}

  /* Footer */
  .footer{{
    text-align:center;
    color:#999;
    font-size:12px;
    padding:20px 0 30px;
  }}
  .footer strong{{color:#2E7D32}}

  /* Print styles */
  @media print{{
    body{{background:white;font-size:13px}}
    .btn-print{{display:none}}
    .header{{background:#2E7D32 !important;-webkit-print-color-adjust:exact}}
    .card{{box-shadow:none;border:1px solid #e0e0e0;break-inside:avoid}}
    .content{{padding:0}}
  }}

  /* Mobile */
  @media(max-width:400px){{
    .header h1{{font-size:1.2em}}
    .card{{padding:16px}}
  }}
</style>
</head>
<body>

<div class="header">
  <div class="header-inner">
    <div class="lang-badge">🌐 {lang_display}</div>
    <h1>{title}</h1>
    <div class="summary">{summary}</div>
    <div class="meta">
      <span>📅 {date_str}</span>
      <span>🆔 {report_id}</span>
      <span>🤖 VaaniAI</span>
    </div>
  </div>
</div>

<div class="content">

  <button class="btn-print" onclick="window.print()">
    🖨️ Save as PDF / Print
  </button>

  {warning_html}
  {sections_html}
  {tips_html}

  <div class="footer">
    Generated by <strong>VaaniAI</strong> •
    Helping rural India with knowledge in every language •
    {date_str}
  </div>

</div>
</body>
</html>"""


def generate_report_id(phone, message):
    raw = f"{phone}|{message}|{datetime.utcnow().date()}"
    return hashlib.md5(raw.encode()).hexdigest()[:10]

def save_report(report_id: str, html: str):
    os.makedirs(REPORTS_DIR, exist_ok=True)
    path = os.path.join(REPORTS_DIR, f"{report_id}.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[REPORT] Saved → {os.path.abspath(path)} ({len(html)} bytes)")

def fix_base_url(base_url: str) -> str:
    """Final safety net — cleans any remaining URL issues"""
    url = base_url.strip().rstrip("/")
    url = url.replace(" ", "-")           # spaces in HF space name
    url = re.sub(r"([^:])//+", r"\1/", url)  # double slashes
    if "hf.space" in url and url.startswith("http://"):
        url = "https://" + url[7:]
    return url

def generate_and_save_report(phone, message, language_mode, short_reply, report_id, base_url):
    raw = None
    try:
        print(f"\n[REPORT] ▶ Starting {report_id} | lang={language_mode}")

        prompt = generate_detailed_prompt(message, language_mode, short_reply)

        if GROQ_API_KEYS:
            raw = try_groq(prompt, max_tokens=2000)
        if not raw and GEMINI_API_KEYS:
            raw = try_gemini(prompt)

        if not raw:
            print("[REPORT] All AI providers failed.")
            return

        print(f"[REPORT] Raw (first 400): {raw[:400]}")

        # Strip markdown fences
        clean = re.sub(r"```json\s*|```\s*", "", raw).strip()

        # Extract JSON object
        json_start = clean.find("{")
        json_end   = clean.rfind("}") + 1
        if json_start == -1 or json_end == 0:
            print("[REPORT] No JSON found.")
            return
        clean = clean[json_start:json_end]

        report_data = json.loads(clean)
        print(f"[REPORT] JSON OK. Title: {report_data.get('title','?')}")
        print(f"[REPORT] Sections: {len(report_data.get('sections',[]))}")

        html = build_report_html(report_data, report_id, language_mode)
        save_report(report_id, html)

        clean_url  = fix_base_url(base_url)
        report_url = f"{clean_url}/report/{report_id}"
        second_sms = clean_for_sms(f"📊 Detailed report: {report_url}", limit=155)

        print(f"[REPORT] Queuing SMS: {second_sms}")
        enqueue_reply(phone, second_sms, language_mode)
        remember_bot_reply(second_sms)
        print(f"[REPORT] ✅ Done → {report_url}")

    except json.JSONDecodeError as e:
        print(f"[REPORT] JSON error: {e}")
        print(f"[REPORT] Raw: {raw[:600] if raw else 'None'}")
    except Exception as e:
        print(f"[REPORT] Error: {e}")
        import traceback
        traceback.print_exc()


# ============================================================
# MAIN WEBHOOK
# ============================================================
@app.post("/sms-webhook")
async def sms_webhook(request: Request):
    data    = await request.json()
    phone   = data["phone"]
    message = data["message"]

    print(f"\n{'='*50}\nSMS from {phone}: {message}")

    if is_blacklisted_sender(phone): return {"status":"blacklisted sender ignored"}
    if is_bot_echo(message):         return {"status":"echo ignored"}
    if is_duplicate(phone, message): return {"status":"duplicate ignored"}

    lang_info     = detect_language(message)
    language_mode = lang_info["mode"]
    print(f"Language: {language_mode}")

    session              = get_user_session(phone)
    conversation_context = build_conversation_context(session["messages"])
    lang_instruction     = get_reply_language_instruction(lang_info)
    previous_language    = session.get("language", language_mode)
    language_note        = (f"Note: User switched from {previous_language} to {language_mode}.\n"
                            if previous_language != language_mode else "")

    prompt = (
        f"You are a helpful SMS assistant for rural villagers and farmers in India.\n\n"
        f"LANGUAGE (strictly follow):\n{lang_instruction}\n{language_note}\n"
        f"RULES:\n"
        f"- ONE single line. NO newlines.\n"
        f"- NO bullets, NO markdown.\n"
        f"- Max 155 characters.\n"
        f"- Warm and helpful.\n\n"
        f"History:\n{conversation_context}\n\n"
        f"User ({language_mode}): {message}\n"
        f"Reply (one line, max 155 chars):"
    )

    reply_text = generate_reply(prompt, language_mode)
    print(f"SMS Reply: {reply_text}")

    update_user_session(phone, message, reply_text, language_mode)
    remember_bot_reply(reply_text)
    enqueue_reply(phone, reply_text, language_mode)

    # Fix HF Spaces URL — request.base_url returns "http://omgy sms.hf.space/"
    # with a literal space in the space name. Fix it immediately at capture.
    base_url  = str(request.base_url).rstrip("/").replace(" ", "-")
    if "hf.space" in base_url and base_url.startswith("http://"):
        base_url = "https://" + base_url[7:]
    report_id = generate_report_id(phone, message)

    threading.Thread(
        target=generate_and_save_report,
        args=(phone, message, language_mode, reply_text, report_id, base_url),
        daemon=True
    ).start()

    return {
        "status":            "reply queued",
        "detected_language": language_mode,
        "script_type":       lang_info["script"],
        "base_language":     lang_info["base"],
        "report_id":         report_id
    }


# ============================================================
# ENDPOINTS
# ============================================================

@app.get("/get-replies")
def get_replies():
    unsent = dequeue_unsent_replies()
    return {"replies": unsent, "count": len(unsent)}


@app.get("/report/{report_id}", response_class=HTMLResponse)
def get_report(report_id: str):
    report_id = re.sub(r"[^a-zA-Z0-9_\-]", "", report_id)
    path      = os.path.join(REPORTS_DIR, f"{report_id}.html")
    if not os.path.exists(path):
        return HTMLResponse(
            "<html><body style='font-family:system-ui;padding:40px;text-align:center;"
            "background:#F1F8E9'>"
            "<div style='background:white;padding:30px;border-radius:16px;"
            "max-width:400px;margin:auto;box-shadow:0 2px 12px rgba(0,0,0,.08)'>"
            "<h2 style='color:#2E7D32'>⏳ Report not ready yet</h2>"
            "<p style='color:#666;margin-top:12px'>Wait a few seconds and refresh.</p>"
            f"<p style='color:#aaa;font-size:12px;margin-top:16px'>ID: {report_id}</p>"
            "</div></body></html>",
            status_code=404
        )
    with open(path, "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())


@app.get("/reports-list")
def list_reports():
    files = os.listdir(REPORTS_DIR) if os.path.exists(REPORTS_DIR) else []
    return {
        "reports_dir": os.path.abspath(REPORTS_DIR),
        "count":       len(files),
        "files":       sorted(files, reverse=True)[:20]
    }


@app.get("/history/{phone}")
def get_history(phone: str):
    return {"phone": phone, "session": get_user_session(phone)}


@app.delete("/history/{phone}")
def clear_history(phone: str):
    history = load_history()
    if phone in history:
        del history[phone]
        save_history(history)
    return {"status": "cleared", "phone": phone}


@app.get("/languages")
def list_languages():
    return {
        "total":         len(LANGUAGE_MODES),
        "native_script": ["Hindi","Gujarati","Marathi","Punjabi","Bengali","Tamil","Telugu","Kannada","Odia","Urdu"],
        "roman_mixed":   ["Hinglish","Gujlish","Marathish","Punjabish","Tamilish","Teluguish","Kannadish","Bengalish"],
        "pure":          ["English"],
        "all_modes":     LANGUAGE_MODES
    }


@app.get("/")
def root():
    queue = load_queue()
    return {
        "status":  "VaaniAI SMS Backend Running",
        "version": "4.0 — Smart Reports + Native Language",
        "providers": {
            "groq_keys":   len(GROQ_API_KEYS),
            "gemini_keys": len(GEMINI_API_KEYS),
            "order":       "Groq → Gemini fallback"
        },
        "features": [
            "19 language modes",
            "Native language reports (Hindi/Gujarati/etc)",
            "Smart visuals — only when relevant (flowchart/bar/pie/comparison)",
            "Conflict-free Gujlish vs Hinglish detection",
            "Conversation memory per user",
            "100% offline HTML reports",
            "Warning boxes for health/safety topics",
            "Background report generation",
            "HF Spaces URL auto-fix"
        ],
        "reports_generated":       len(os.listdir(REPORTS_DIR)) if os.path.exists(REPORTS_DIR) else 0,
        "unsent_replies_in_queue": sum(1 for r in queue if not r["sent"])
    }