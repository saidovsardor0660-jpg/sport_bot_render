import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from datetime import datetime
import config
import database

bot = Bot(token=config.TOKEN)
dp = Dispatcher()

# ══════════════════════════════════════════════════════════
#  SARDOR UCHUN AQLLI TRENER — 3 OYLIK PROGRESSIV PLAN
#  Vazn: 66-67 kg | Bo'y: 184 cm | Maqsad: Yaxshi forma
#  Hafta  1–4  → Moslashish  | Hafta 5–8  → O'rta
#  Hafta 9–12 → Intensiv
#  Protein norma: 120g/kun  (66kg × 1.8)
# ══════════════════════════════════════════════════════════

PROTEIN_NORMA = 120

# ──────────────────────────────────────────────
# PROTEIN MANBALARI — arzon, har kun turli xil
# ──────────────────────────────────────────────
PROTEIN_FOODS = [
    {"name": "Tuxum oqi (3 ta)",       "protein": 18, "tip": "Arzon, tez, har doim uyda."},
    {"name": "Tvorog 200g",             "protein": 28, "tip": "Kechqurun uxlashdan oldin ideal."},
    {"name": "Tovuq ko'kragi 150g",     "protein": 40, "tip": "Eng yaxshi manba. Qaynatib yeng."},
    {"name": "Tuna konservasi 1 banka", "protein": 26, "tip": "Arzon va tez. Bozorda ~8000 so'm."},
    {"name": "Sut 500ml",               "protein": 16, "tip": "Mashqdan keyin ichsang bo'ladi."},
    {"name": "Loviya (qaynatilgan) 200g","protein": 14,"tip": "Go'shtsiz kun uchun zo'r alternativ."},
    {"name": "Yer yong'oq 50g",         "protein": 13, "tip": "Snack sifatida, non bilan."},
    {"name": "Tvorog + sut shake",      "protein": 36, "tip": "150g tvorog + 200ml sut — aralashtirib ich."},
    {"name": "Qovoq urug'i 50g",        "protein": 15, "tip": "Mineral ham ko'p. Xushbo'y qovurish mumkin."},
    {"name": "Sardinа konservasi",       "protein": 22, "tip": "Omega-3 + protein. Narxi past."},
    {"name": "Mol go'shti 120g (qaynat)","protein": 26,"tip": "Haftada 1-2 marta yegan kifoya."},
    {"name": "Qo'y go'shti 120g",       "protein": 24, "tip": "Temirga ham boy. Qaynatish yaxshi."},
]

# Haftaning kuniga qarab protein manbasi tavsiyasi (takrorlanmasin)
def get_protein_menu_for_today() -> list:
    day = datetime.now().weekday()  # 0=Dush, 6=Yak
    # Kuniga 3-4 xil manba, har kun boshqacha kombinatsiya
    combos = [
        [0, 2, 5],   # Dushanba
        [1, 3, 6],   # Sеshanba
        [0, 4, 7],   # Chorshanba
        [2, 8, 9],   # Payshanba
        [1, 5, 10],  # Juma
        [3, 6, 11],  # Shanba
        [0, 7, 4],   # Yakshanba
    ]
    indices = combos[day % 7]
    return [PROTEIN_FOODS[i] for i in indices]


# ──────────────────────────────────────────────
# 3 OYLIK MASHQ PLANI — Takroriy mashqlar YO'Q
# Har faza uchun yangi, progressiv, xilma-xil
# ──────────────────────────────────────────────

# Isitish (warm-up) har mashq boshida majburiy
WARMUP = {
    "moslashish": {
        "cardio": "🏃 5 daq yugurish (treadmill, juda sekin, 6-7 km/h) — nafas tiklansin",
        "drills": [
            "Bilek aylantirish × 10",
            "Yelka aylantirish × 10",
            "Tizza ko'tarish joyida × 20",
            "Engashish (hamstring) × 10",
        ]
    },
    "orta": {
        "cardio": "🏃 8 daq yugurish (treadmill, 8-9 km/h) + 2 daq sekinlashish",
        "drills": [
            "Arm circles × 15",
            "Hip rotations × 10 har tomonga",
            "Bodyweight squat × 15",
            "Band pull-apart × 15 (lenta bo'lsa)",
        ]
    },
    "intensiv": {
        "cardio": "🏃 10 daq yugurish (9-10 km/h) — yurak chastotasi ko'tarilsin",
        "drills": [
            "Leg swings × 12 har oyoq",
            "Inchworm stretch × 8",
            "Shoulder dislocates × 10",
            "Goblet squat × 10 (yengil)",
        ]
    }
}

COOLDOWN = "🧘 Sovutish: 5 daq sekin yurish + 5 daq cho'zish (ishlagan mushaklarni 30 son ushlab turing)."

# ── Mashqlar ──────────────────────────────────────────────
# Har faza uchun A/B/C kunlari to'liq o'zgaradi
# ──────────────────────────────────────────────────────────
WORKOUTS = {

    # ═══ KUN A: Ko'krak + Triceps ═══
    "A": {
        "moslashish": {
            "day": "DUSHANBA | Ko'krak & Triceps",
            "phase_label": "🟢 Hafta 1-4 — Moslashish",
            "exercises": [
                {
                    "num": "1️⃣",
                    "name": "Tekis Leja (Barbell Bench Press)",
                    "equipment": "Shtanga + tekis skameyka",
                    "sets": "3 × 12",
                    "weight": "Yengil (40% 1RM — taxminan 30-35 kg)",
                    "tip": "Ko'krak to'liq cho'zilsin, shtangani sekin tushiring (2 son), tepaga bir harakatda."
                },
                {
                    "num": "2️⃣",
                    "name": "Dumbbell Chest Fly",
                    "equipment": "Gantellar + tekis skameyka",
                    "sets": "3 × 15",
                    "weight": "8-10 kg gantellar",
                    "tip": "Qo'llar sal bukilgan holatda — ko'krak cho'zilishini his qiling, tirsakni bukmang."
                },
                {
                    "num": "3️⃣",
                    "name": "Triceps Rope Pushdown",
                    "equipment": "Krossover yuqori blok + arqon",
                    "sets": "3 × 15",
                    "weight": "Yengil — texnikaga e'tibor",
                    "tip": "Tirsaklar yon tomonda qimirlamasin. Pastga tortganda kaft tashqariga aylansin."
                },
            ],
            "img": "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=600"
        },
        "orta": {
            "day": "DUSHANBA | Ko'krak & Triceps",
            "phase_label": "🟡 Hafta 5-8 — O'rta nagruzka",
            "exercises": [
                {
                    "num": "1️⃣",
                    "name": "Incline Barbell Press",
                    "equipment": "Shtanga + 30° qiya skameyka",
                    "sets": "4 × 10",
                    "weight": "O'rta (60% 1RM)",
                    "tip": "Yuqori ko'krakni shakllantiradi. 184 cm bo'y uchun qiya press juda muhim."
                },
                {
                    "num": "2️⃣",
                    "name": "Cable Crossover",
                    "equipment": "Krossover — ikki blok",
                    "sets": "4 × 12",
                    "weight": "O'rta",
                    "tip": "Ko'krak o'rtasiga tortish. Ko'z hizasidan pastdan birlashtirib, 1 son ushlab turing."
                },
                {
                    "num": "3️⃣",
                    "name": "Skull Crushers",
                    "equipment": "EZ-bar + tekis skameyka",
                    "sets": "3 × 12",
                    "weight": "Yengil-o'rta",
                    "tip": "Shtangani peshona ustiga tushirmasdan, bosh orqasiga. Tirsak tez og'rimasligi uchun sekin bajaring."
                },
                {
                    "num": "4️⃣",
                    "name": "Dips (Triceps)",
                    "equipment": "Parallel tutqichlar (брусья)",
                    "sets": "3 × max",
                    "weight": "Tana vazni",
                    "tip": "Tana tik tursin (oldinga egilsang ko'krak ishlaydi). Tricepsni his qiling."
                },
            ],
            "img": "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=600"
        },
        "intensiv": {
            "day": "DUSHANBA | Ko'krak & Triceps",
            "phase_label": "🔴 Hafta 9-12 — Intensiv",
            "exercises": [
                {
                    "num": "1️⃣",
                    "name": "Flat Barbell Bench Press (og'ir)",
                    "equipment": "Shtanga + tekis skameyka",
                    "sets": "5 × 5",
                    "weight": "Og'ir (80-85% 1RM) — spotterdan so'rang",
                    "tip": "Har haftada +2.5 kg. Progressive overload — bu faza asosi."
                },
                {
                    "num": "2️⃣",
                    "name": "Incline Dumbbell Press",
                    "equipment": "Og'ir gantellar + qiya skameyka",
                    "sets": "4 × 8",
                    "weight": "Og'ir",
                    "tip": "Shtangadan keyin o'tkaziladi — mushaklari charchagan bo'ladi, shuning uchun samarali."
                },
                {
                    "num": "3️⃣",
                    "name": "Weighted Dips",
                    "equipment": "Brусья + bel zanjiri (og'irlik)",
                    "sets": "4 × 8",
                    "weight": "10-20 kg qo'shib",
                    "tip": "Compound harakat — triceps, ko'krak, yelka birga."
                },
                {
                    "num": "4️⃣",
                    "name": "Single-Arm Cable Pushdown",
                    "equipment": "Krossover — bir qo'l",
                    "sets": "3 × 15",
                    "weight": "O'rta",
                    "tip": "Superset qiling: o'ng → chap. Dam yo'q."
                },
            ],
            "img": "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=600"
        },
    },

    # ═══ KUN B: Orqa + Biceps ═══
    "B": {
        "moslashish": {
            "day": "CHORSHANBA | Orqa & Biceps",
            "phase_label": "🟢 Hafta 1-4 — Moslashish",
            "exercises": [
                {
                    "num": "1️⃣",
                    "name": "Lat Pulldown (keng grip)",
                    "equipment": "Yuqori blok trenajyor (Lat machine)",
                    "sets": "3 × 12",
                    "weight": "Yengil — texnika birinchi",
                    "tip": "Ko'kragingizga tortib 1 son ushlab turing. Orqa (lat) mushaklarini his qiling, qo'l emas."
                },
                {
                    "num": "2️⃣",
                    "name": "Seated Cable Row",
                    "equipment": "Pastki blok + V-bar",
                    "sets": "3 × 12",
                    "weight": "Yengil",
                    "tip": "Bel tekis, tirsak orqaga — qorin devoriga tegsin. Ko'krak ochiq bo'lsin."
                },
                {
                    "num": "3️⃣",
                    "name": "Dumbbell Curl (alternating)",
                    "equipment": "Gantellar",
                    "sets": "3 × 12 har qo'l",
                    "weight": "8-10 kg",
                    "tip": "Gavdani silkimang. Faqat biceps kuchi. Ko'tarishda qo'lni ichkariga bura."
                },
            ],
            "img": "https://images.unsplash.com/photo-1581009146145-b5ef050c2e1e?w=600"
        },
        "orta": {
            "day": "CHORSHANBA | Orqa & Biceps",
            "phase_label": "🟡 Hafta 5-8 — O'rta nagruzka",
            "exercises": [
                {
                    "num": "1️⃣",
                    "name": "Barbell Bent-Over Row",
                    "equipment": "Shtanga (engashib tortish)",
                    "sets": "4 × 10",
                    "weight": "O'rta (60% 1RM)",
                    "tip": "Bel burchagi 45°. Shtanga kindikka tekkanda orqa siqilsin. 184 cm uchun bel kuchini his qiling."
                },
                {
                    "num": "2️⃣",
                    "name": "Pull-Ups (tana vazni)",
                    "equipment": "Turnik (keng grip)",
                    "sets": "4 × max",
                    "weight": "Tana vazni",
                    "tip": "Har set orasida 2 daq dam. Ko'krakni turnikka yaqinlashtiring — yelkangiz pastga qarasin."
                },
                {
                    "num": "3️⃣",
                    "name": "EZ-Bar Bicep Curl",
                    "equipment": "EZ-bar (bukilgan shtanga)",
                    "sets": "4 × 10",
                    "weight": "O'rta",
                    "tip": "To'liq amplitudada. Pastga tushirishni ham sekin bajaring (eccentric)."
                },
                {
                    "num": "4️⃣",
                    "name": "Hammer Curl",
                    "equipment": "Gantellar (neytral tutish)",
                    "sets": "3 × 12",
                    "weight": "10-12 kg",
                    "tip": "Bilak va brachialis ham ishlaydi — qo'l qalinligi uchun."
                },
            ],
            "img": "https://images.unsplash.com/photo-1581009146145-b5ef050c2e1e?w=600"
        },
        "intensiv": {
            "day": "CHORSHANBA | Orqa & Biceps",
            "phase_label": "🔴 Hafta 9-12 — Intensiv",
            "exercises": [
                {
                    "num": "1️⃣",
                    "name": "Deadlift (klassik)",
                    "equipment": "Shtanga — yerdan ko'tarish",
                    "sets": "4 × 5",
                    "weight": "Og'ir (80% 1RM) ⚠️",
                    "tip": "Eng ko'p mushakni birga ishlatadi. Bel tekis, qorin kuchlansin, tizza oldga emas."
                },
                {
                    "num": "2️⃣",
                    "name": "Weighted Pull-Ups",
                    "equipment": "Turnik + og'irlik (bel zanjiri)",
                    "sets": "4 × 6-8",
                    "weight": "10+ kg qo'shib",
                    "tip": "Kuch bosqichida — progressiv og'irlashtirish shart."
                },
                {
                    "num": "3️⃣",
                    "name": "T-Bar Row",
                    "equipment": "T-bar yoki landmine grip",
                    "sets": "4 × 8",
                    "weight": "Og'ir",
                    "tip": "Orqa yo'g'onligi (thickness) uchun. Bel g'oz, tirsak yuqoriga."
                },
                {
                    "num": "4️⃣",
                    "name": "Preacher Curl",
                    "equipment": "EZ-bar + preacher skameyka",
                    "sets": "4 × 10",
                    "weight": "O'rta-og'ir",
                    "tip": "To'liq izolyatsiya — gavdani silkitish imkoni yo'q. Biceps piki uchun."
                },
            ],
            "img": "https://images.unsplash.com/photo-1581009146145-b5ef050c2e1e?w=600"
        },
    },

    # ═══ KUN C: Oyoq + Yelka + Press ═══
    "C": {
        "moslashish": {
            "day": "JUMA | Oyoq & Yelka & Press",
            "phase_label": "🟢 Hafta 1-4 — Moslashish",
            "exercises": [
                {
                    "num": "1️⃣",
                    "name": "Goblet Squat",
                    "equipment": "Bitta og'ir gantell yoki kettlebell",
                    "sets": "3 × 15",
                    "weight": "16-20 kg gantell",
                    "tip": "184 cm uchun: tovon ostiga kichik plita qo'ying — chuqurroq o'tiriladi. Tizzalar oyoq barmoqlariga qarasin."
                },
                {
                    "num": "2️⃣",
                    "name": "Leg Press",
                    "equipment": "Oyoq pressi mashina",
                    "sets": "3 × 15",
                    "weight": "Yengil — oyoq o'ta kengroq",
                    "tip": "Oyoq yelka kengligidan keng qo'ysang ichki son ishlaydi. Tizzalar to'g'ri yo'nalsin."
                },
                {
                    "num": "3️⃣",
                    "name": "Dumbbell Lateral Raise",
                    "equipment": "Yengil gantellar",
                    "sets": "3 × 15",
                    "weight": "5-6 kg",
                    "tip": "Yelka kengligini beradi. Qo'lni yelka hizasigacha ko'taring, yuqoriga emas."
                },
                {
                    "num": "4️⃣",
                    "name": "Crunch (roman skameyka)",
                    "equipment": "Roman skameyka / Ab bench",
                    "sets": "3 × 20",
                    "weight": "Tana vazni",
                    "tip": "Bel yerdan uzilib ketmasin. Bosh orqaga yotmang — bel siqilib qoladi."
                },
            ],
            "img": "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?w=600"
        },
        "orta": {
            "day": "JUMA | Oyoq & Yelka & Press",
            "phase_label": "🟡 Hafta 5-8 — O'rta nagruzka",
            "exercises": [
                {
                    "num": "1️⃣",
                    "name": "Barbell Back Squat",
                    "equipment": "Shtanga yelkada — Smith machine yoki free squat rack",
                    "sets": "4 × 10",
                    "weight": "O'rta (60% 1RM)",
                    "tip": "Asosiy mashq! Chuqur o'tiring. 184 cm uchun grip keng, tizzalar oyoqqa parallel."
                },
                {
                    "num": "2️⃣",
                    "name": "Romanian Deadlift (RDL)",
                    "equipment": "Shtanga — oyoq orqasi (hamstring)",
                    "sets": "3 × 12",
                    "weight": "O'rta",
                    "tip": "Tizzalar biroz bukilgan, bel tekis, orqa cho'zilishini his qiling."
                },
                {
                    "num": "3️⃣",
                    "name": "Seated Dumbbell Press",
                    "equipment": "Gantellar + tik skameyka",
                    "sets": "4 × 10",
                    "weight": "16-18 kg gantellar",
                    "tip": "Yelkani shakllantiradi. Qo'llar yelka hizasida boshlansin."
                },
                {
                    "num": "4️⃣",
                    "name": "Hanging Leg Raise",
                    "equipment": "Turnikda osilib oyoq ko'tarish",
                    "sets": "4 × 15",
                    "weight": "Tana vazni",
                    "tip": "Oyoqlar to'g'ri bo'lsa og'irroq. Tiz bukilsa osonroq. Pastga tushirishni ham boshqaring."
                },
            ],
            "img": "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?w=600"
        },
        "intensiv": {
            "day": "JUMA | Oyoq & Yelka & Press",
            "phase_label": "🔴 Hafta 9-12 — Intensiv",
            "exercises": [
                {
                    "num": "1️⃣",
                    "name": "Heavy Back Squat",
                    "equipment": "Shtanga yelkada (og'ir, free squat rack)",
                    "sets": "5 × 5",
                    "weight": "Og'ir (80-85% 1RM)",
                    "tip": "Har haftada +2.5 kg. Bu faza kuch rekordlarini yangilash vaqti."
                },
                {
                    "num": "2️⃣",
                    "name": "Bulgarian Split Squat",
                    "equipment": "Gantellar + orqa skameyka",
                    "sets": "4 × 8 har oyoq",
                    "weight": "16-20 kg gantellar",
                    "tip": "Muvozanat va oyoq kuchini birga oshiradi. Ehtiyotkorlik bilan bajaring."
                },
                {
                    "num": "3️⃣",
                    "name": "Barbell Overhead Press (OHP)",
                    "equipment": "Shtanga — bosh ustida ko'tarish",
                    "sets": "4 × 8",
                    "weight": "O'rta-og'ir",
                    "tip": "Yelka va triceps. Bel ortga bukilmasin — qorin kuchlansin."
                },
                {
                    "num": "4️⃣",
                    "name": "Cable Crunch",
                    "equipment": "Krossover yuqori blok + arqon",
                    "sets": "4 × 15",
                    "weight": "O'rta og'irlik bilan",
                    "tip": "Press uchun eng samarali mashq. Og'irlik qo'shib borish mumkin."
                },
            ],
            "img": "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?w=600"
        },
    }
}


def get_week_phase(week: int) -> str:
    if week <= 4:
        return "moslashish"
    elif week <= 8:
        return "orta"
    else:
        return "intensiv"


# ══════════════════════════════════════════════
#  MENYU
# ══════════════════════════════════════════════
def get_main_menu():
    kb = [
        [KeyboardButton(text="🏋️‍♂️ Bugungi Mashg'ulot"), KeyboardButton(text="⏱ Taymerni Boshlash")],
        [KeyboardButton(text="🍽 Bugungi Protein Menyu"), KeyboardButton(text="🥚 Tuxum (+18g)")],
        [KeyboardButton(text="🍗 Tovuq (+40g)"), KeyboardButton(text="📊 Kunlik Hisobot")],
        [KeyboardButton(text="📅 3 Oylik Rejam"), KeyboardButton(text="✅ Mashg'ulot Tugadi")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


# ══════════════════════════════════════════════
#  HANDLERLAR
# ══════════════════════════════════════════════

@dp.message(F.text == "/start")
async def start_cmd(message: Message):
    database.register_user(message.from_user.id)
    await message.answer(
        "💪 Salom Sardor! Sizning *Aqlli Trener* botingiz tayyor.\n\n"
        "📋 *Parametrlaringiz:*\n"
        "   ⚖️ Vazn: 66-67 kg | 📏 Bo'y: 184 cm\n"
        "   🎯 Maqsad: Yaxshi forma\n"
        "   🥩 Kunlik protein: *120g* (66 × 1.8)\n\n"
        "🗓 *3 OYLIK REJA:*\n"
        "   🟢 1–4 hafta → Moslashish\n"
        "   🟡 5–8 hafta → O'rta nagruzka\n"
        "   🔴 9–12 hafta → Intensiv\n\n"
        "⏰ Zal vaqti: *19:30 – 21:00*\n\n"
        "Hech qanday shoshma — birinchi hafta texnikani o'rganamiz!",
        reply_markup=get_main_menu(),
        parse_mode="Markdown"
    )


@dp.message(F.text == "🏋️‍♂️ Bugungi Mashg'ulot")
async def show_workout(message: Message):
    uid = message.from_user.id
    current_day = database.get_workout_day(uid)      # 'A', 'B', yoki 'C'
    week = getattr(database, 'get_current_week', lambda x: 1)(uid)
    phase = get_week_phase(week)

    w = WORKOUTS[current_day][phase]
    warmup = WARMUP[phase]

    lines = [
        f"🏋️‍♂️ *{w['day']}*",
        f"{w['phase_label']} | Hafta {week}/12",
        "",
        "━━━━━━━━━━━━━━━━━━━━",
        "🔥 *ISITISH (10-15 daqiqa) — MAJBURIY!*",
        f"• {warmup['cardio']}",
    ]
    for d in warmup["drills"]:
        lines.append(f"• {d}")
    lines += ["", "━━━━━━━━━━━━━━━━━━━━", "🏋️ *ASOSIY MASHQLAR:*", ""]

    for ex in w["exercises"]:
        lines += [
            f"{ex['num']} *{ex['name']}*",
            f"   🔧 _{ex['equipment']}_",
            f"   📊 {ex['sets']} | {ex['weight']}",
            f"   💬 {ex['tip']}",
            "",
        ]

    lines += ["━━━━━━━━━━━━━━━━━━━━", f"{COOLDOWN}"]
    caption = "\n".join(lines)

    await message.answer_photo(photo=w["img"], caption=caption, parse_mode="Markdown")


@dp.message(F.text == "⏱ Taymerni Boshlash")
async def start_timer(message: Message):
    now = datetime.now().strftime("%H:%M")
    uid = message.from_user.id
    week = getattr(database, 'get_current_week', lambda x: 1)(uid)
    phase = get_week_phase(week)
    warmup_time = {"moslashish": "10-12", "orta": "12-15", "intensiv": "15"}[phase]
    await message.answer(
        f"🚀 *Taymer ishga tushdi!* — {now}\n\n"
        f"📋 *Bugungi tartib:*\n"
        f"• 🔥 Isitish: {warmup_time} daqiqa\n"
        f"• 💪 Mashqlar: ~50-60 daqiqa\n"
        f"• 🧘 Sovutish: 5-8 daqiqa\n\n"
        f"⏰ Jami: 19:30 → 21:00 gacha yetib turadi.\n"
        f"💧 Har set orasida 2-3 yutak suv iching!",
        parse_mode="Markdown"
    )


@dp.message(F.text == "🍽 Bugungi Protein Menyu")
async def protein_menu(message: Message):
    uid = message.from_user.id
    import sqlite3
    conn = sqlite3.connect("smart_coach.db")
    cur = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    cur.execute("SELECT protein FROM nutrition WHERE user_id=? AND date=?", (uid, today))
    row = cur.fetchone()
    conn.close()
    eaten = row[0] if row else 0
    deficit = max(0, PROTEIN_NORMA - eaten)

    foods = get_protein_menu_for_today()
    day_names = ["Dushanba", "Seshanba", "Chorshanba", "Payshanba", "Juma", "Shanba", "Yakshanba"]
    day_name = day_names[datetime.now().weekday()]

    lines = [
        f"🍽 *{day_name}gi Protein Menyu*",
        f"Bugungi holat: *{eaten}g / {PROTEIN_NORMA}g*",
        f"Yetishmaydi: *{deficit}g*",
        "",
        "━━━━━━━━━━━━━━━━━━━━",
        "💡 *Bugun quyidagilardan protein oling:*",
        "(Har kuni yangi kombinatsiya — bir xillik yo'q!)",
        "",
    ]
    total_available = 0
    for f in foods:
        lines += [
            f"✅ *{f['name']}* — {f['protein']}g oqsil",
            f"   💬 _{f['tip']}_",
            "",
        ]
        total_available += f["protein"]

    lines += [
        "━━━━━━━━━━━━━━━━━━━━",
        f"📊 Bu kombinatsiyadan jami: *~{total_available}g* oqsil",
        "",
        "🔑 *Qoida:* Go'sht yeya olmasangiz ham norma to'liq bajariladi!",
        "Tuxum + tvorog + loviya = yetarli.",
    ]
    await message.answer("\n".join(lines), parse_mode="Markdown")


@dp.message(F.text == "✅ Mashg'ulot Tugadi")
async def workout_done(message: Message):
    database.complete_workout(message.from_user.id)
    await message.answer(
        "🏆 *Mashg'ulot yakunlandi!*\n\n"
        "✅ Keyingi kun dasturi avtomatik yangilandi.\n"
        "🧘 Sovutishni unutmadingizmi? 5 daq cho'zing!\n"
        "🍽 Mashqdan 30-60 daqiqa ichida protein yeng.\n\n"
        "💪 Har kun bir qadam oldinga — bu yetarli!",
        parse_mode="Markdown"
    )


@dp.message(F.text == "🥚 Tuxum (+18g)")
async def add_egg(message: Message):
    uid = message.from_user.id
    total = database.add_protein_data(uid, 18)
    pct = min(int(total / PROTEIN_NORMA * 10), 10)
    bar = "🟩" * pct + "⬜" * (10 - pct)
    await message.answer(f"✅ *+18g oqsil* yozildi (3 ta tuxum)\n{bar} *{total}g / {PROTEIN_NORMA}g*", parse_mode="Markdown")


@dp.message(F.text == "🍗 Tovuq (+40g)")
async def add_chicken(message: Message):
    uid = message.from_user.id
    total = database.add_protein_data(uid, 40)
    pct = min(int(total / PROTEIN_NORMA * 10), 10)
    bar = "🟩" * pct + "⬜" * (10 - pct)
    await message.answer(f"✅ *+40g oqsil* yozildi (tovuq ko'kragi)\n{bar} *{total}g / {PROTEIN_NORMA}g*", parse_mode="Markdown")


@dp.message(F.text == "📊 Kunlik Hisobot")
async def daily_report(message: Message):
    import sqlite3
    uid = message.from_user.id
    conn = sqlite3.connect("smart_coach.db")
    cur = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    cur.execute("SELECT protein FROM nutrition WHERE user_id=? AND date=?", (uid, today))
    row = cur.fetchone()
    conn.close()

    protein = row[0] if row else 0
    week = getattr(database, 'get_current_week', lambda x: 1)(uid)
    phase = get_week_phase(week)
    pct = min(int(protein / PROTEIN_NORMA * 10), 10)
    bar = "🟩" * pct + "⬜" * (10 - pct)

    phase_labels = {"moslashish": "🟢 Moslashish", "orta": "🟡 O'rta", "intensiv": "🔴 Intensiv"}
    phase_tips = {
        "moslashish": "Texnikaga e'tibor bering — og'irlik ikkinchi o'rinda.",
        "orta": "Har mashqda +2.5 kg qo'shib borish vaqti.",
        "intensiv": "Dam olish ham mashq — uxlash sifatini buzmaing."
    }

    deficit = max(0, PROTEIN_NORMA - protein)
    if deficit > 0:
        tuxum = round(deficit / 6)
        smart_advice = f"💡 Yetishmayapti {deficit}g → Uxlashdan oldin {tuxum} ta tuxum oqi yoki 150g tvorog."
    else:
        smart_advice = "🏆 Bugun protein norma bajarildi! Ajoyib!"

    await message.answer(
        f"📊 *Kunlik Hisobot*\n\n"
        f"🥩 Oqsil: {bar} *{protein}g / {PROTEIN_NORMA}g*\n\n"
        f"🗓 Hafta: *{week}/12* | {phase_labels[phase]}\n"
        f"💬 _{phase_tips[phase]}_\n\n"
        f"{smart_advice}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🎒 *Eslatma:*\n"
        f"• Sumkada: sport kiyim, sochiq, banan\n"
        f"• Kun davomida: 2+ litr suv\n"
        f"• Zal: 19:30 – 21:00",
        parse_mode="Markdown"
    )


@dp.message(F.text == "📅 3 Oylik Rejam")
async def show_plan(message: Message):
    uid = message.from_user.id
    week = getattr(database, 'get_current_week', lambda x: 1)(uid)
    phase = get_week_phase(week)
    phase_labels = {"moslashish": "🟢 Moslashish", "orta": "🟡 O'rta", "intensiv": "🔴 Intensiv"}
    await message.answer(
        "📅 *3 OYLIK PROGRESSIV PLAN*\n\n"
        "🟢 *1–4 hafta — Moslashish:*\n"
        "• Og'irlik: 40-50% maksimaldan\n"
        "• 3 set × 12-15 takror\n"
        "• Isitish: 10-12 daqiqa yugurish\n"
        "• Maqsad: Texnika, bo'g'imlar mustahkamlash\n\n"
        "🟡 *5–8 hafta — O'rta nagruzka:*\n"
        "• Og'irlik: 60-70% maksimaldan\n"
        "• 4 set × 10 takror\n"
        "• Isitish: 12-15 daqiqa yugurish\n"
        "• Maqsad: Kuch va hajm oshirish\n\n"
        "🔴 *9–12 hafta — Intensiv:*\n"
        "• Og'irlik: 75-85% maksimaldan\n"
        "• 4-5 set × 5-8 takror\n"
        "• Isitish: 15 daqiqa yugurish\n"
        "• Maqsad: Reljef, maksimal kuch\n\n"
        f"📍 *Hozir: {week}-hafta* — {phase_labels[phase]}\n\n"
        "🗓 *Zal kunlari:* Dushanba | Chorshanba | Juma\n"
        "🥩 *Kunlik protein:* 120g (go'shtsiz kun ham mumkin!)",
        parse_mode="Markdown"
    )


async def main():
    config.init_db()
    print("✅ Aqlli Trener bot muvaffaqiyatli ishga tushdi...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
