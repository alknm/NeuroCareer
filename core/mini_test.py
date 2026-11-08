"""Короткий онлайн-тест на трёх языках (RU / KZ / EN).

18 вопросов Гарднера + 10 вопросов MBTI. Каждый вопрос имеет три перевода;
маппинг ответов в признаки не зависит от языка.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .data_loader import (GARDNER_FEATURES, ID_COL, MBTI_SCALE_FEATURES,
                          MBTI_TYPE_COL, NEIRY_FEATURES, ROLE_FEATURES,
                          load_pilot)


# ---------------------------------------------------------------------------
# Likert scale labels
# ---------------------------------------------------------------------------

LIKERT_LABELS = {
    "ru": [
        "1 — совсем не про меня",
        "2 — скорее нет",
        "3 — отчасти",
        "4 — скорее да",
        "5 — очень про меня",
    ],
    "kz": [
        "1 — мен туралы емес",
        "2 — жоқ деуге болады",
        "3 — ішінара",
        "4 — иә деуге болады",
        "5 — дәл мен туралы",
    ],
    "en": [
        "1 — not me at all",
        "2 — rather not",
        "3 — partly",
        "4 — rather yes",
        "5 — very much me",
    ],
}


def _likert_to_unit(value: int) -> float:
    return (max(1, min(5, int(value))) - 1) / 4.0


# ---------------------------------------------------------------------------
# Gardner questions (2 per intelligence)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class GardnerQuestion:
    intelligence: str
    texts: dict[str, str]  # {ru, kz, en}

    def text(self, lang: str = "ru") -> str:
        return self.texts.get(lang) or self.texts.get("ru", "")


def _g(intelligence: str, ru: str, kz: str, en: str) -> GardnerQuestion:
    return GardnerQuestion(intelligence, {"ru": ru, "kz": kz, "en": en})


GARDNER_QUESTIONS: list[GardnerQuestion] = [
    _g("Натуралистический интеллект",
       "Мне интересно наблюдать за растениями, животными и природными явлениями.",
       "Маған өсімдіктерді, жануарларды және табиғат құбылыстарын бақылау қызық.",
       "I enjoy observing plants, animals and natural phenomena."),
    _g("Натуралистический интеллект",
       "Я легко замечаю различия между похожими видами, породами или сортами.",
       "Ұқсас түрлер, тұқымдар немесе сұрыптар арасындағы айырмашылықты оңай аңғарамын.",
       "I easily notice differences between similar species, breeds or varieties."),

    _g("Внутриличностный интеллект",
       "Я хорошо понимаю свои эмоции, мотивы и реакции в разных ситуациях.",
       "Әртүрлі жағдайларда өз эмоцияларымды, түрткілерімді және реакцияларымды жақсы түсінемін.",
       "I understand my own emotions, motives and reactions well in various situations."),
    _g("Внутриличностный интеллект",
       "Мне комфортно проводить время в одиночестве, размышляя над своими целями и ценностями.",
       "Жалғыздықта мақсаттарым мен құндылықтарым туралы ойлану маған жайлы.",
       "I am comfortable spending time alone reflecting on my goals and values."),

    _g("Логико-математический интеллект",
       "Мне нравится решать задачи с числами, формулами и логическими построениями.",
       "Маған сандармен, формулалармен және логикалық құрылымдармен есеп шығару ұнайды.",
       "I enjoy solving problems involving numbers, formulas and logical reasoning."),
    _g("Логико-математический интеллект",
       "Я люблю разбираться, как устроены сложные системы, и искать причинно-следственные связи.",
       "Күрделі жүйелердің құрылымын түсіну және себеп-салдар байланыстарын іздеу маған ұнайды.",
       "I like understanding how complex systems work and finding cause-effect relationships."),

    _g("Лингвистический интеллект",
       "Мне нравится играть со словами, придумывать тексты, изучать языки.",
       "Маған сөздермен ойнау, мәтіндер құрастыру, тілдер үйрену ұнайды.",
       "I enjoy playing with words, composing texts and learning languages."),
    _g("Лингвистический интеллект",
       "Я хорошо подбираю формулировки и легко излагаю мысли вслух или письменно.",
       "Тұжырымдамаларды жақсы таңдаймын, ойды ауызша немесе жазбаша жеткізу маған оңай.",
       "I phrase things well and easily express thoughts aloud or in writing."),

    _g("Телесно-кинестетический интеллект",
       "У меня хорошо развита координация движений, я люблю физическую активность.",
       "Қозғалыс координациям жақсы дамыған, маған дене белсенділігі ұнайды.",
       "I have well-developed motor coordination and enjoy physical activity."),
    _g("Телесно-кинестетический интеллект",
       "Я быстро осваиваю новые двигательные навыки — танцы, спорт, ремесло.",
       "Жаңа қимыл дағдыларын — би, спорт, қолөнерді жылдам меңгеремін.",
       "I quickly pick up new motor skills — dance, sport, craft."),

    _g("Пространственно-визуальный интеллект",
       "Я легко представляю объекты в трёх измерениях и хорошо ориентируюсь по картам.",
       "Объектілерді үш өлшемде елестетемін және картамен жақсы бағдарланамын.",
       "I easily picture objects in three dimensions and navigate well by maps."),
    _g("Пространственно-визуальный интеллект",
       "Мне нравится рисовать, чертить, проектировать визуальные композиции.",
       "Маған сурет салу, сызбалар жасау, визуалды композициялар құрастыру ұнайды.",
       "I enjoy drawing, sketching and designing visual compositions."),

    _g("Музыкальный интеллект",
       "Я хорошо чувствую ритм и мелодию, легко запоминаю музыку на слух.",
       "Ырғақ пен әуенді жақсы сезінемін, музыканы есту арқылы оңай есте сақтаймын.",
       "I have a strong sense of rhythm and melody and easily memorise music by ear."),
    _g("Музыкальный интеллект",
       "Мне интересно сочинять или исполнять музыку, петь, играть на инструменте.",
       "Музыка шығару немесе орындау, ән айту, аспапта ойнау маған қызық.",
       "I am interested in composing or performing music, singing, playing an instrument."),

    _g("Экзистенциальный интеллект",
       "Меня волнуют фундаментальные вопросы — смысл жизни, природа сознания, место человека в мире.",
       "Мені іргелі сұрақтар толғандырады — өмірдің мәні, сананың табиғаты, адамның әлемдегі орны.",
       "I am moved by fundamental questions — the meaning of life, the nature of consciousness, the place of humans in the world."),
    _g("Экзистенциальный интеллект",
       "Я люблю обсуждать философские и мировоззренческие темы.",
       "Маған философиялық және дүниетанымдық тақырыптарды талқылау ұнайды.",
       "I enjoy discussing philosophical and worldview topics."),

    _g("Межличностный интеллект",
       "Я легко понимаю настроение и мотивы других людей.",
       "Басқа адамдардың көңіл-күйі мен түрткілерін оңай түсінемін.",
       "I easily understand other people's moods and motives."),
    _g("Межличностный интеллект",
       "Мне нравится организовывать совместную работу, помогать другим находить общий язык.",
       "Бірлескен жұмысты ұйымдастыру, басқаларға ортақ тіл табысуға көмектесу ұнайды.",
       "I enjoy organising joint work and helping others find common ground."),
]


# ---------------------------------------------------------------------------
# MBTI questions
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class MBTIQuestion:
    pole_a_col: str
    pole_b_col: str
    texts: dict[str, str]
    points_to: str  # 'a' or 'b'

    def text(self, lang: str = "ru") -> str:
        return self.texts.get(lang) or self.texts.get("ru", "")


def _m(pole_a, pole_b, points_to, ru, kz, en) -> MBTIQuestion:
    return MBTIQuestion(pole_a, pole_b, {"ru": ru, "kz": kz, "en": en}, points_to)


MBTI_DICHOTOMY_PAIRS = [
    ("MBTIЭкстраверт",  "MBTIИнтроверт",    "E", "I"),
    ("MBTIИнтуитивные", "MBTIРеалистичные", "N", "S"),
    ("MBTIЛогика",      "MBTIПринципы",     "T", "F"),
    ("MBTIПланирующие", "MBTIИщущие",       "J", "P"),
    ("MBTIУверенные",   "MBTIОсторожные",   "A", "T"),
]

MBTI_QUESTIONS: list[MBTIQuestion] = [
    # E vs I
    _m("MBTIЭкстраверт", "MBTIИнтроверт", "a",
       "В большой шумной компании я заряжаюсь энергией.",
       "Үлкен шулы компанияда мен энергияға толамын.",
       "Big noisy gatherings energise me."),
    _m("MBTIЭкстраверт", "MBTIИнтроверт", "b",
       "После активного общения мне нужно побыть одному, чтобы восстановиться.",
       "Белсенді қарым-қатынастан кейін қалпына келу үшін жалғыздық қажет.",
       "After intense socialising I need time alone to recover."),

    # N vs S
    _m("MBTIИнтуитивные", "MBTIРеалистичные", "a",
       "Меня больше увлекают идеи, концепции и возможности, чем конкретные факты.",
       "Мені нақты деректерден гөрі идеялар, концепциялар мен мүмкіндіктер көбірек қызықтырады.",
       "Ideas, concepts and possibilities engage me more than concrete facts."),
    _m("MBTIИнтуитивные", "MBTIРеалистичные", "b",
       "Я предпочитаю опираться на проверенный опыт и наблюдаемые факты, а не на догадки.",
       "Болжамдарға емес, тексерілген тәжірибе мен байқалатын фактілерге сүйенгенді жөн көремін.",
       "I prefer relying on tested experience and observable facts rather than guesses."),

    # T vs F
    _m("MBTIЛогика", "MBTIПринципы", "a",
       "При принятии решений я в первую очередь опираюсь на логику и анализ.",
       "Шешім қабылдағанда ең алдымен логика мен талдауға сүйенемін.",
       "When deciding I rely primarily on logic and analysis."),
    _m("MBTIЛогика", "MBTIПринципы", "b",
       "Мне важно учитывать чувства и ценности людей, даже если это нелогично.",
       "Қисынсыз болса да адамдардың сезімдері мен құндылықтарын ескеру маңызды.",
       "It matters to me to consider people's feelings and values, even when it is illogical."),

    # J vs P
    _m("MBTIПланирующие", "MBTIИщущие", "a",
       "Мне комфортно жить по плану и расписанию.",
       "Жоспар мен кестемен өмір сүру маған жайлы.",
       "I am comfortable living by a plan and schedule."),
    _m("MBTIПланирующие", "MBTIИщущие", "b",
       "Я люблю оставлять выбор открытым и решать по ситуации.",
       "Таңдауды ашық қалдырып, жағдайға қарай шешуді ұнатамын.",
       "I prefer keeping options open and deciding situationally."),

    # A vs T
    _m("MBTIУверенные", "MBTIОсторожные", "a",
       "Я обычно уверен в своих решениях и редко переживаю задним числом.",
       "Мен әдетте өз шешімдеріме сенімдімін және сирек өкінемін.",
       "I usually feel confident in my decisions and rarely second-guess them."),
    _m("MBTIУверенные", "MBTIОсторожные", "b",
       "Я часто беспокоюсь о возможных ошибках и анализирую свои действия после факта.",
       "Мен ықтимал қателер туралы жиі алаңдаймын және өз әрекеттерімді кейін талдаймын.",
       "I often worry about possible mistakes and analyse my actions after the fact."),
]


# ---------------------------------------------------------------------------
# Building a pilot-format row from answers
# ---------------------------------------------------------------------------

@dataclass
class MiniTestResult:
    profile_row: pd.Series
    synthetic_eeg: bool
    has_role_data: bool


def _avg_likert_to_score(answers: list[int]) -> float:
    if not answers:
        return 50.0
    return float(np.mean([_likert_to_unit(a) for a in answers]) * 100.0)


def _build_gardner_scores(answers: list[int]) -> dict[str, float]:
    if len(answers) != len(GARDNER_QUESTIONS):
        raise ValueError(
            f"Expected {len(GARDNER_QUESTIONS)} Gardner answers, got {len(answers)}"
        )
    bucket: dict[str, list[int]] = {k: [] for k in GARDNER_FEATURES}
    for q, ans in zip(GARDNER_QUESTIONS, answers):
        bucket[q.intelligence].append(ans)
    return {k: _avg_likert_to_score(v) for k, v in bucket.items()}


def _build_mbti_scores_and_type(answers: list[int]) -> tuple[dict[str, float], str]:
    if len(answers) != len(MBTI_QUESTIONS):
        raise ValueError(
            f"Expected {len(MBTI_QUESTIONS)} MBTI answers, got {len(answers)}"
        )
    pole_a_unit: dict[str, list[float]] = {}
    for q, ans in zip(MBTI_QUESTIONS, answers):
        unit = _likert_to_unit(ans)
        if q.points_to == "b":
            unit = 1.0 - unit
        pole_a_unit.setdefault(q.pole_a_col, []).append(unit)

    scores: dict[str, float] = {col: 0.0 for col in MBTI_SCALE_FEATURES}
    abbrev_chars: list[str] = []
    for pole_a, pole_b, letter_a, letter_b in MBTI_DICHOTOMY_PAIRS:
        vals = pole_a_unit.get(pole_a, [])
        a_score = float(np.mean(vals)) * 100.0 if vals else 50.0
        scores[pole_a] = a_score
        scores[pole_b] = 100.0 - a_score
        abbrev_chars.append(letter_a if a_score >= 50.0 else letter_b)

    main_four = "".join(abbrev_chars[:4])
    suffix = abbrev_chars[4]
    return scores, f"{main_four}-{suffix}"


def _default_neiry_and_roles() -> tuple[dict[str, float], dict[str, float]]:
    pilot = load_pilot()
    neiry = {col: float(pilot[col].mean()) for col in NEIRY_FEATURES}
    roles = {col: float(pilot[col].mean()) for col in ROLE_FEATURES}
    return neiry, roles


def build_mini_test_profile(
    gardner_answers: list[int],
    mbti_answers: list[int],
    display_name: str = "Mini-test user",
) -> MiniTestResult:
    gardner = _build_gardner_scores(gardner_answers)
    mbti_scores, mbti_abbrev = _build_mbti_scores_and_type(mbti_answers)
    neiry, roles = _default_neiry_and_roles()

    row: dict[str, object] = {ID_COL: display_name}
    row.update(gardner)
    row[MBTI_TYPE_COL] = mbti_abbrev
    row.update(mbti_scores)
    row.update(roles)
    row.update(neiry)

    return MiniTestResult(
        profile_row=pd.Series(row),
        synthetic_eeg=True,
        has_role_data=False,
    )


# ---------------------------------------------------------------------------
# Intro / disclaimer
# ---------------------------------------------------------------------------

TOTAL_QUESTIONS = len(GARDNER_QUESTIONS) + len(MBTI_QUESTIONS)

_MINI_TEST_INTRO = {
    "ru": (
        f"Короткий онлайн-тест из {TOTAL_QUESTIONS} утверждений "
        f"({len(GARDNER_QUESTIONS)} по Гарднеру, {len(MBTI_QUESTIONS)} по MBTI). "
        "На каждое утверждение нужно выбрать степень согласия по пятибалльной "
        "шкале. После прохождения система формирует профиль и сразу выводит "
        "ранжирование 64 профессий из базы знаний."
    ),
    "kz": (
        f"{TOTAL_QUESTIONS} тұжырымнан тұратын қысқа онлайн-тест "
        f"({len(GARDNER_QUESTIONS)} Гарднер бойынша, "
        f"{len(MBTI_QUESTIONS)} MBTI бойынша). Әр тұжырымға бес балдық "
        "шкалада келісім дәрежесін таңдау керек. Аяқтағаннан кейін жүйе "
        "профильді құрастырады және білім қорындағы 64 кәсіптің рейтингін "
        "бірден шығарады."
    ),
    "en": (
        f"A short online test of {TOTAL_QUESTIONS} statements "
        f"({len(GARDNER_QUESTIONS)} Gardner, {len(MBTI_QUESTIONS)} MBTI). "
        "Rate each statement on a five-point scale. Once finished, the system "
        "builds your profile and immediately ranks 64 professions from its "
        "knowledge base."
    ),
}

_MINI_TEST_DISCLAIMER = {
    "ru": (
        "Внимание: мини-тест — упрощённая версия. Без ЭЭГ-гарнитуры Neiry "
        "нейрофизиологические маркеры подставляются средними значениями "
        "пилотной выборки, а предсказание ролевого профиля опирается только "
        "на психометрику. Рекомендации в этом режиме носят ориентировочный "
        "характер и менее точны, чем при наличии всех 65 признаков."
    ),
    "kz": (
        "Назар аударыңыз: мини-тест — жеңілдетілген нұсқа. Neiry ЭЭГ-"
        "гарнитурасынсыз нейрофизиологиялық маркерлер пилоттық таңдаманың "
        "орташа мәндерімен ауыстырылады, ал рөлдік профильді болжау тек "
        "психометрикаға сүйенеді. Бұл режимдегі ұсыныстар бағдарлы сипатта "
        "және барлық 65 белгіге қарағанда дәлдігі төмен."
    ),
    "en": (
        "Note: the mini-test is a simplified version. Without the Neiry EEG "
        "headset, neurophysiological markers are substituted with pilot-"
        "sample averages and the role-profile prediction relies only on "
        "psychometrics. Recommendations in this mode are advisory and less "
        "accurate than with all 65 features."
    ),
}


def mini_test_intro(lang: str = "ru") -> str:
    return _MINI_TEST_INTRO.get(lang) or _MINI_TEST_INTRO["ru"]


def mini_test_disclaimer(lang: str = "ru") -> str:
    return _MINI_TEST_DISCLAIMER.get(lang) or _MINI_TEST_DISCLAIMER["ru"]


def likert_labels(lang: str = "ru") -> list[str]:
    return LIKERT_LABELS.get(lang) or LIKERT_LABELS["ru"]
