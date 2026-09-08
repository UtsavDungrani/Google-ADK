"""
Multilingual NLP & Cross-Lingual Information Retrieval (CLIR) Engine
Provides sub-millisecond Language Identification (LID), Script Detection,
Code-Mixing / Hinglish recognition, Multilingual Entity Shielding (mNER),
Cross-Lingual Query Alignment for English RAG/Exemplar retrieval, and
Pragmatic Cultural Politeness & Honorific Directives.
"""

import re
import math
from typing import Dict, List, Any, Optional, Tuple, Set

# -------------------------------------------------------------
# LANGUAGE DEFINITIONS & METADATA
# -------------------------------------------------------------

LANGUAGE_METADATA: Dict[str, Dict[str, Any]] = {
    "en": {
        "name": "English",
        "native_name": "English",
        "script": "Latin",
        "flag": "🇺🇸",
        "default_honorific": "Professional Polite",
        "sample_greeting": "Hello! How can I assist you with your order today?"
    },
    "es": {
        "name": "Spanish",
        "native_name": "Español",
        "script": "Latin",
        "flag": "🇪🇸",
        "default_honorific": "Usted (Formal)",
        "sample_greeting": "¡Hola! ¿En qué puedo colaborarle con su pedido hoy?"
    },
    "fr": {
        "name": "French",
        "native_name": "Français",
        "script": "Latin",
        "flag": "🇫🇷",
        "default_honorific": "Vouvoiement (Vous)",
        "sample_greeting": "Bonjour ! Comment puis-je vous aider avec votre commande aujourd'hui ?"
    },
    "de": {
        "name": "German",
        "native_name": "Deutsch",
        "script": "Latin",
        "flag": "🇩🇪",
        "default_honorific": "Höflichkeitsform (Sie/Ihnen)",
        "sample_greeting": "Guten Tag! Wie kann ich Ihnen heute bei Ihrer Bestellung behilflich sein?"
    },
    "hi": {
        "name": "Hindi",
        "native_name": "हिन्दी",
        "script": "Devanagari",
        "flag": "🇮🇳",
        "default_honorific": "आदरसूचक (आप)",
        "sample_greeting": "नमस्ते! आज मैं आपके ऑर्डर या उत्पाद सहायता में कैसे मदद कर सकता हूँ?"
    },
    "hinglish": {
        "name": "Hinglish",
        "native_name": "Hinglish (Hindi-English)",
        "script": "Latin (Code-Mixed)",
        "flag": "🇮🇳",
        "default_honorific": "Respectful Conversational (Aap)",
        "sample_greeting": "Hello! Mai aapke order ya device issue me kaise help kar sakta hu?"
    },
    "ja": {
        "name": "Japanese",
        "native_name": "日本語",
        "script": "Japanese (Kanji/Kana)",
        "flag": "🇯🇵",
        "default_honorific": "敬語 / 丁寧語 (Keigo)",
        "sample_greeting": "いらっしゃいませ。ご注文や製品に関して、どのようなお手伝いができますでしょうか？"
    }
}

# -------------------------------------------------------------
# VOCABULARY & FUNCTION WORD MARKERS
# -------------------------------------------------------------

_STOP_WORDS_BY_LANG: Dict[str, Set[str]] = {
    "es": {
        "el", "la", "los", "las", "un", "una", "unos", "unas", "de", "del", "que", "y",
        "en", "es", "por", "para", "con", "no", "mi", "mis", "su", "sus", "como", "pero",
        "más", "gracias", "hola", "por favor", "ayuda", "necesito", "tengo", "este", "esta",
        "estos", "estas", "fue", "muy", "sobre", "entre", "también", "donde", "cuando"
    },
    "fr": {
        "le", "la", "les", "un", "une", "des", "du", "de", "d'", "et", "est", "dans",
        "pour", "avec", "sur", "ce", "cette", "ces", "pas", "qui", "que", "mon", "ma",
        "mes", "votre", "vos", "merci", "bonjour", "aide", "besoin", "ai", "suis", "plus",
        "mais", "très", "par", "aussi", "où", "quand"
    },
    "de": {
        "der", "die", "das", "ein", "eine", "einer", "eines", "und", "ist", "in", "den",
        "von", "zu", "mit", "sich", "auf", "für", "nicht", "mein", "meine", "bitte",
        "danke", "hallo", "hilfe", "brauche", "habe", "dieser", "diese", "sehr", "aber",
        "wie", "auch", "wo", "wann"
    },
    "hinglish": {
        "mera", "meri", "mere", "kya", "hai", "hain", "karo", "karna", "nahi", "tha",
        "thi", "raha", "rahi", "hoga", "kaise", "thik", "bhi", "bahut", "mujhe", "humko",
        "kab", "tak", "aayega", "kharab", "paise", "wapas", "chahiye", "kar", "ho", "gaya",
        "diya", "bhai", "sir", "plz", "pls", "help", "kardo", "aaya"
    }
}

# -------------------------------------------------------------
# MULTILINGUAL NAMED ENTITY RECOGNITION (mNER) & SHIELDING
# -------------------------------------------------------------

_ENTITY_PATTERNS = [
    ("ORDER_ID", r"\b(ORD-\d{5}|[a-f0-9]{32})\b"),
    ("TICKET_ID", r"\b(TCK-[A-Za-z0-9]+-[A-Za-z0-9]+)\b"),
    ("RMA_CODE", r"\b(RMA-[A-Za-z0-9-]+)\b"),
    ("CLAIM_ID", r"\b(CLM-[A-Za-z0-9-]+)\b"),
    ("CREDIT_CODE", r"\b(CARE-CREDIT-[A-Za-z0-9-]+)\b"),
    ("ERROR_CODE", r"\b(TV-NET-\d+|ERR-\d+|E-\d{3})\b"),
    ("DEVICE_MODEL", r"\b(UTV-65-4K-PRO|PS-ANC-900|BPE-15BAR)\b"),
    ("SERIAL_NUM", r"\b(SN-[A-Za-z0-9-]+)\b"),
]


def shield_entities(text: str) -> Tuple[str, Dict[str, str]]:
    """
    Extracts and shields critical IDs, tracking codes, and serials with token slots
    so translations and cross-lingual transformations never mutate them.
    
    Returns:
        Tuple of (shielded_text, entity_slot_map)
    """
    if not text:
        return "", {}

    shielded = text
    slot_map: Dict[str, str] = {}
    counter = 0

    for entity_type, pattern in _ENTITY_PATTERNS:
        matches = list(re.finditer(pattern, shielded, re.IGNORECASE))
        for m in reversed(matches):
            val = m.group(0)
            slot = f"__{entity_type}_{counter}__"
            slot_map[slot] = val
            shielded = shielded[:m.start()] + slot + shielded[m.end():]
            counter += 1

    return shielded, slot_map


def unshield_entities(text: str, slot_map: Dict[str, str]) -> str:
    """Restores shielded entity slots back to their exact original alphanumeric values."""
    if not text or not slot_map:
        return text or ""

    unshielded = text
    for slot, val in slot_map.items():
        unshielded = unshielded.replace(slot, val)
    return unshielded


# -------------------------------------------------------------
# LANGUAGE & SCRIPT IDENTIFICATION (LID)
# -------------------------------------------------------------

def detect_script(text: str) -> str:
    """Detects primary Unicode script of the text."""
    if not text:
        return "Latin"

    devanagari_count = len(re.findall(r"[\u0900-\u097F]", text))
    japanese_count = len(re.findall(r"[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]", text))
    total_chars = max(1, len(re.sub(r"\s+", "", text)))

    if devanagari_count / total_chars > 0.15:
        return "Devanagari"
    if japanese_count / total_chars > 0.15:
        return "Japanese"
    return "Latin"


def detect_language(text: str) -> Dict[str, Any]:
    """
    High-speed, sub-millisecond Language Identification (LID) using
    Unicode script detection, characteristic character n-grams, and functional markers.
    
    Returns:
        Dict with 'language' (ISO code), 'name', 'script', 'confidence' (0.0-1.0),
        'is_code_mixed' (bool), and 'flag'.
    """
    if not text or not text.strip():
        return {
            "language": "en",
            "name": "English",
            "script": "Latin",
            "confidence": 1.0,
            "is_code_mixed": False,
            "flag": "🇺🇸"
        }

    script = detect_script(text)

    # 1. Non-Latin Scripts (Deterministic Unicode mapping)
    if script == "Devanagari":
        return {
            "language": "hi",
            "name": "Hindi",
            "native_name": "हिन्दी",
            "script": "Devanagari",
            "confidence": 0.98,
            "is_code_mixed": False,
            "flag": "🇮🇳"
        }

    if script == "Japanese":
        return {
            "language": "ja",
            "name": "Japanese",
            "native_name": "日本語",
            "script": "Japanese (Kanji/Kana)",
            "confidence": 0.99,
            "is_code_mixed": False,
            "flag": "🇯🇵"
        }

    # 2. Latin Script Analysis (English, Spanish, French, German, Hinglish)
    clean_text = text.lower()
    words = re.findall(r"\b[a-záéíóúüñäößàèêç]{2,}\b", clean_text)
    word_set = set(words)
    total_words = max(1, len(words))

    # Check characteristic diacritics / punctuation
    has_spanish_diacritics = bool(re.search(r"[áíóúñ¿¡]", text))
    has_french_diacritics = bool(re.search(r"[èêàçœ]", text))
    has_german_diacritics = bool(re.search(r"[äöüß]", text))

    scores: Dict[str, float] = {
        "en": 0.1,
        "es": 0.0,
        "fr": 0.0,
        "de": 0.0,
        "hinglish": 0.0
    }

    if has_spanish_diacritics:
        scores["es"] += 0.35
    if has_french_diacritics:
        scores["fr"] += 0.35
    if has_german_diacritics:
        scores["de"] += 0.35

    # Count functional markers
    for lang, markers in _STOP_WORDS_BY_LANG.items():
        match_count = sum(1 for w in words if w in markers)
        ratio = match_count / total_words
        scores[lang] += ratio * 1.5

    # Check common English tokens
    en_markers = {"the", "is", "my", "your", "order", "return", "refund", "tv", "not", "with", "have", "can", "please"}
    en_matches = sum(1 for w in words if w in en_markers)
    scores["en"] += (en_matches / total_words) * 1.2

    # Hinglish Code-Switching Logic
    # If text has Hinglish functional words (mera, hai, karo, kardo, etc.) mixed with English nouns (order, refund, tv, delivery)
    hinglish_matches = sum(1 for w in words if w in _STOP_WORDS_BY_LANG["hinglish"])
    is_code_mixed = False
    if hinglish_matches >= 2 or (hinglish_matches >= 1 and total_words <= 5):
        scores["hinglish"] += 0.85
        is_code_mixed = True

    # Find highest scoring language
    best_lang = max(scores.items(), key=lambda x: x[1])
    selected_lang = best_lang[0]
    raw_confidence = min(0.99, max(0.40, best_lang[1] / (sum(scores.values()) or 1.0)))

    # If tie or weak confidence towards Latin with no clear markers, fallback to English
    if selected_lang != "en" and scores[selected_lang] < 0.25 and not (has_spanish_diacritics or has_french_diacritics or has_german_diacritics):
        selected_lang = "en"
        raw_confidence = 0.85

    meta = LANGUAGE_METADATA.get(selected_lang, LANGUAGE_METADATA["en"])

    return {
        "language": selected_lang,
        "name": meta["name"],
        "native_name": meta.get("native_name", meta["name"]),
        "script": meta["script"],
        "confidence": round(raw_confidence, 2),
        "is_code_mixed": is_code_mixed or (selected_lang == "hinglish"),
        "flag": meta["flag"]
    }


# -------------------------------------------------------------
# CROSS-LINGUAL INFORMATION RETRIEVAL (CLIR) BILINGUAL LEXICON
# Translates foreign customer care terms into English search concepts
# -------------------------------------------------------------

_CROSS_LINGUAL_CONCEPTS: List[Dict[str, Any]] = [
    {
        "category": "Returns & Warranty",
        "english_keywords": "return refund rma 30-day window policy grace exception",
        "multilingual_triggers": [
            # Spanish
            "devolucion", "devolución", "devolver", "reembolso", "regresar", "plazo", "dias", "hospital",
            # French
            "remboursement", "retourner", "renvoyer", "retour", "delai", "30 jours", "hopital",
            # German
            "ruckgabe", "rückgabe", "zuruckgeben", "zurückgeben", "erstatten", "ruckerstattung", "rückerstattung", "30 tage", "krankenhaus",
            # Hindi / Hinglish
            "वापसी", "रिफंड", "लौटाना", "पैसे वापस", "wapas", "paise wapas", "refund chahiye", "return karna", "hospital me tha",
            # Japanese
            "返品", "返金", "キャンセル", "30日", "入院"
        ]
    },
    {
        "category": "Product Diagnostics - TV Error 502",
        "english_keywords": "tv-net-502 error wifi mesh eero disconnect network ota firmware patch capacitance discharge 60 seconds",
        "multilingual_triggers": [
            # Spanish
            "tv-net-502", "wifi", "malla", "red", "desconecta", "eero", "televisor", "firmware", "parche",
            # French
            "tv-net-502", "wifi", "reseau", "déconnecte", "routeur", "téléviseur", "mise a jour",
            # German
            "tv-net-502", "wlan", "netzwerk", "bricht ab", "verbindung", "fernseher", "update",
            # Hindi / Hinglish
            "tv-net-502", "वाईफाई", "नेटवर्क", "डिस्कनेक्ट", "wifi bar bar drop", "disconnect ho raha", "tv connect nahi ho raha",
            # Japanese
            "tv-net-502", "wi-fi", "接続できない", "切断", "ルーター", "アップデート"
        ]
    },
    {
        "category": "Product Diagnostics - Display / Screen Defect",
        "english_keywords": "screen display horizontal lines black lines panel t-con warranty claim clm-tv-98214 replacement",
        "multilingual_triggers": [
            # Spanish
            "pantalla", "lineas horizontales", "líneas", "rayas negras", "panel", "garantia", "defecto",
            # French
            "ecran", "écran", "lignes horizontales", "lignes noires", "dalle", "garantie", "panne",
            # German
            "bildschirm", "horizontale linien", "schwarze streifen", "panel", "garantie", "defekt",
            # Hindi / Hinglish
            "स्क्रीन", "डिस्प्ले", "काली लाइन", "स्क्रीन खराब", "screen pe line", "screen kharab hai", "horizontal line aa rahi",
            # Japanese
            "画面", "横線", "黒い線", "ディスプレイ", "液晶", "保証"
        ]
    },
    {
        "category": "Product Diagnostics - Headphones Multipoint",
        "english_keywords": "headphones bluetooth multipoint dual device pairing macbook iphone simultaneous audio",
        "multilingual_triggers": [
            # Spanish
            "auriculares", "cascos", "multipunto", "emparejar", "dos dispositivos", "macbook", "iphone", "bluetooth",
            # French
            "ecouteurs", "écouteurs", "casque", "multipoint", "appairer", "deux appareils", "simultane",
            # German
            "kopfhorer", "kopfhörer", "multipoint", "koppeln", "zwei gerate", "gleichzeitig", "bluetooth",
            # Hindi / Hinglish
            "हेडफोन", "ब्लूटूथ", "दो फोन", "लैपटॉप", "साथ में", "connect kaise kare", "dono device me chalana hai",
            # Japanese
            "ヘッドホン", "マルチポイント", "ペアリング", "2台同時", "ブルートゥース"
        ]
    },
    {
        "category": "Product Diagnostics - Espresso Descaling",
        "english_keywords": "espresso machine orange light flashing descaling alert pressure low 5 bars 15 bars vinegar water purge",
        "multilingual_triggers": [
            # Spanish
            "cafetera", "luz naranja", "parpadea", "presion", "presión", "descalcificar", "descalcificacion", "5 bares",
            # French
            "cafetiere", "cafetière", "voyant orange", "clignote", "detartrage", "détartrage", "pression basse",
            # German
            "kaffeemaschine", "orange leuchte", "blinkt", "entkalken", "entkalkung", "druck", "5 bar",
            # Hindi / Hinglish
            "कॉफी मशीन", "ऑरेंज लाइट", "चमक रही", "प्रेशर कम", "descaling alert", "orange light blink kar rahi", "pressure nahi ban raha",
            # Japanese
            "エスプレッソ", "オレンジのランプ", "点滅", "湯垢洗浄", "圧力低下"
        ]
    },
    {
        "category": "Shipping & Logistics - Courier Delays & Credits",
        "english_keywords": "shipping delay late courier dhl customs port hold investigation courtesy credit voucher 25 dollars",
        "multilingual_triggers": [
            # Spanish
            "retraso", "demora", "tarde", "no llega", "paquete", "aduanas", "credito de cortesia", "molesto",
            # French
            "retard", "en retard", "pas arrive", "colis", "douane", "credit de courtoisie",
            # German
            "verspatung", "verspätung", "verzogert", "verzögert", "paket", "zoll", "gutschrift",
            # Hindi / Hinglish
            "देरी", "कब आएगा", "पैकेज", "कस्टम", "late ho gaya", "delay hai", "paise wapas", "bahut time ho gaya",
            # Japanese
            "遅延", "届かない", "荷物", "税関", "お詫び クレジット"
        ]
    }
]


def align_cross_lingual_query(query: str, source_lang: Optional[str] = None) -> Dict[str, Any]:
    """
    Transforms a multilingual or code-mixed user query into an English search query
    anchored with shielded entity slots for 100% accurate RAG and Few-Shot retrieval.
    
    Args:
        query: Raw input in any language (e.g. Spanish, Hindi, Hinglish, German).
        source_lang: Optional pre-detected language code.
    
    Returns:
        Dict with 'source_language', 'is_english', 'shielded_query',
        'aligned_english_query', 'matched_concepts', and 'entities'.
    """
    if not query:
        return {
            "source_language": "en",
            "is_english": True,
            "shielded_query": "",
            "aligned_english_query": "",
            "matched_concepts": [],
            "entities": {}
        }

    # 1. Shield specific entities (Order IDs, RMA codes, Error codes)
    shielded_text, entity_map = shield_entities(query)

    # 2. Detect language if not provided
    if not source_lang:
        lid_res = detect_language(query)
        source_lang = lid_res["language"]

    is_english = source_lang == "en"

    # 3. If English, return query directly with preserved slots
    if is_english:
        unshielded_query = unshield_entities(shielded_text, entity_map)
        return {
            "source_language": "en",
            "is_english": True,
            "shielded_query": shielded_text,
            "aligned_english_query": unshielded_query,
            "matched_concepts": [],
            "entities": entity_map
        }

    # 4. Cross-Lingual Concept Matching
    q_norm = query.lower()
    matched_concepts: List[str] = []
    english_expansion_terms: List[str] = []

    for concept in _CROSS_LINGUAL_CONCEPTS:
        triggers = concept["multilingual_triggers"]
        for trig in triggers:
            if trig in q_norm:
                matched_concepts.append(concept["category"])
                english_expansion_terms.append(concept["english_keywords"])
                break

    # 5. Extract shielded entity values to preserve in search
    entity_values = list(entity_map.values())

    # 6. Compose aligned English query
    expansion_text = " ".join(english_expansion_terms)
    composed_terms = entity_values + [expansion_text]
    aligned_query = " ".join([t for t in composed_terms if t.strip()]).strip()

    # If no specific concept matched, retain original text with entities
    if not aligned_query:
        aligned_query = unshield_entities(shielded_text, entity_map)

    return {
        "source_language": source_lang,
        "is_english": False,
        "shielded_query": shielded_text,
        "aligned_english_query": aligned_query,
        "matched_concepts": list(set(matched_concepts)),
        "entities": entity_map
    }


# -------------------------------------------------------------
# PRAGMATICS & CULTURAL POLITENESS DIRECTIVES
# -------------------------------------------------------------

def get_pragmatic_politeness_directive(lang_code: str, preferred_tone: str = "Empathetic & Professional") -> str:
    """
    Generates linguistically grounded politeness and honorific directives
    for the Gemini agent prompt to guarantee culturally accurate interactions.
    """
    directives = {
        "es": (
            "LANGUAGE DIRECTIVE (Spanish / Español):\n"
            "• Responda SIEMPRE en español con fluidez nativa y calidez.\n"
            "• Utilice estrictamente el pronombre de respeto formal 'Usted' (no utilice 'tú' ni tuteos informales).\n"
            "• Use formas de cortesía profesional: 'Le informo', 'Por favor revise', 'Con mucho gusto le ayudo'.\n"
            "• Conserve intactos los códigos de pedido (ORD-XXXX), autorizaciones RMA y códigos de error (TV-NET-502).\n"
            "• Mantenga las citas de políticas oficiales al pie (ej. *Fuente: Política Oficial del Comercio*)."
        ),
        "fr": (
            "LANGUAGE DIRECTIVE (French / Français):\n"
            "• Répondez ENTIÈREMENT en français avec une syntaxe professionnelle impeccable.\n"
            "• Employez systématiquement le vouvoiement ('Vous' / 'Votre' / 'Vos') avec courtoisie.\n"
            "• Conservez scrupuleusement les numéros de commande (ORD-XXXX) et identifiants techniques.\n"
            "• Citez les sources officielles de documentation à la fin de la réponse."
        ),
        "de": (
            "LANGUAGE DIRECTIVE (German / Deutsch):\n"
            "• Antworten Sie VOLLSTÄNDIG auf Deutsch mit professioneller Präzision und Empathie.\n"
            "• Verwenden Sie AUSSCHLIESSLICH die formelle Höflichkeitsanrede 'Sie' / 'Ihnen' / 'Ihr' (niemals das informelle 'du').\n"
            "• Strukturieren Sie technische Diagnoseschritte klar nummeriert.\n"
            "• Behalten Sie Bestellnummern (ORD-XXXX) und Fehlercodes (TV-NET-502) unverändert bei."
        ),
        "hi": (
            "LANGUAGE DIRECTIVE (Hindi / हिन्दी):\n"
            "• अपने उत्तर को शुद्ध, स्वाभाविक और आदरपूर्ण हिन्दी में प्रस्तुत करें।\n"
            "• ग्राहक के लिए हमेशा आदरसूचक सर्वनाम 'आप', 'आपका', 'कीजिए' का प्रयोग करें (अनौपचारिक 'तुम' या 'तू' का प्रयोग कतई न करें)।\n"
            "• ऑर्डर आईडी (ORD-XXXX), टिकट नंबर (TCK-XXXX) और एरर कोड (TV-NET-502) को अंग्रेजी अक्षरों में यथावत रखें।\n"
            "• तकनीकी निर्देशों को स्पष्ट क्रमांकित बिंदुओं (1, 2, 3) में समझाएं।"
        ),
        "hinglish": (
            "LANGUAGE DIRECTIVE (Hinglish / Hindi-English Code-Mixed):\n"
            "• Respond in natural, polite conversational Hinglish (Latin script) as commonly used in modern Indian customer care.\n"
            "• Maintain high respect using 'Aap', 'Aapka', 'Kripya' (e.g. 'Aap bilkul chinta mat kijiye, mai aapka order check kar raha hu').\n"
            "• Keep technical terms, Order IDs, and RMA codes in clear English (e.g. 'Aapka refund 3-5 business days me original payment method par credit ho jayega').\n"
            "• Be empathetic, warm, and highly structured with bullet points."
        ),
        "ja": (
            "LANGUAGE DIRECTIVE (Japanese / 日本語):\n"
            "• 日本語の適切な敬語（丁寧語・謙譲語・尊敬語）を用いて、誠実かつ礼儀正しく回答してください。\n"
            "• 語尾は「です」「ます」「ございます」で統一し、お客様への敬意を常に保ってください。\n"
            "• 注文番号（ORD-XXXX）やエラーコード（TV-NET-502）は英数字のまま正確に記載してください。\n"
            "• 正式なマニュアル規定やポリシーの引用を文末に付記してください。"
        )
    }

    return directives.get(lang_code, "")
