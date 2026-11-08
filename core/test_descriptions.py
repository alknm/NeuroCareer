"""Описания тестов и метрики оценивания на трёх языках (RU / KZ / EN).

Каждая строка хранится как dict {"ru","kz","en"}. Геттер `get_test_info(test_id, lang)`
возвращает локализованную копию `TestInfo`.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TestInfo:
    name: str
    short: str
    strengths: str
    weaknesses: str
    use_in_system: str
    link: str
    link_label: str


def _pick(d: dict[str, str], lang: str) -> str:
    return d.get(lang) or d.get("ru", "")


# ---------------------------------------------------------------------------
# Gardner
# ---------------------------------------------------------------------------

_GARDNER = {
    "name": {
        "ru": "Тест множественного интеллекта Г. Гарднера",
        "kz": "Гарднердің көпсалалы интеллект тесті",
        "en": "H. Gardner's multiple-intelligence test",
    },
    "short": {
        "ru": "Девятимерный профиль способностей: вербально-лингвистический, "
              "логико-математический, пространственно-визуальный, телесно-"
              "кинестетический, музыкально-ритмический, межличностный, "
              "внутриличностный, натуралистический, экзистенциальный.",
        "kz": "Тоғыз өлшемді қабілеттер профилі: вербалды-лингвистикалық, "
              "логикалық-математикалық, кеңістіктік-визуалды, тәндік-"
              "кинестетикалық, музыкалық-ырғақтық, тұлғааралық, "
              "ішкітұлғалық, натуралистік, экзистенциалдық.",
        "en": "A nine-dimensional ability profile: verbal-linguistic, "
              "logical-mathematical, spatial-visual, bodily-kinesthetic, "
              "musical-rhythmic, interpersonal, intrapersonal, naturalist, "
              "existential.",
    },
    "strengths": {
        "ru": "Содержательно богатая многомерная модель: показывает не одну "
              "«общую способность», а профиль сильных и слабых сторон. "
              "Интуитивно понятна пользователю и хорошо ложится на сопоставление "
              "с описаниями профессий.",
        "kz": "Көпөлшемді мазмұнды модель: бір ғана «жалпы қабілетті» емес, "
              "күшті және әлсіз жақтардың профилін көрсетеді. Пайдаланушыға "
              "түсінікті және кәсіп сипаттамасымен жақсы үйлеседі.",
        "en": "A rich multi-dimensional model: not a single \"general "
              "ability\" but a profile of strengths and weaknesses. Intuitive "
              "for users and maps well onto profession descriptions.",
    },
    "weaknesses": {
        "ru": "Психометрика модели обсуждаема: ряд факторов слабо отделим друг "
              "от друга, нет общепринятой нормативной выборки. Результаты "
              "чувствительны к самоотчёту.",
        "kz": "Модельдің психометрикасы талқыланады: бірнеше фактор бір-бірінен "
              "әлсіз ажыратылады, жалпыға бірдей норма жоқ. Нәтижелер "
              "өзіндік есепке сезімтал.",
        "en": "The model's psychometrics are debated: some factors are weakly "
              "separable and there is no agreed normative sample. Results are "
              "sensitive to self-report.",
    },
    "use_in_system": {
        "ru": "В системе вектор Гарднера — основной психометрический источник "
              "ранжирования профессий: компонент matcher.gardner (вес 0.30).",
        "kz": "Жүйеде Гарднер векторы — кәсіптерді рейтингтеудің негізгі "
              "психометрикалық көзі: matcher.gardner компоненті (салмағы 0.30).",
        "en": "In the system, the Gardner vector is the main psychometric "
              "source for profession ranking: the matcher.gardner component "
              "(weight 0.30).",
    },
    "link": {
        "ru": "https://en.wikipedia.org/wiki/Theory_of_multiple_intelligences",
        "kz": "https://en.wikipedia.org/wiki/Theory_of_multiple_intelligences",
        "en": "https://en.wikipedia.org/wiki/Theory_of_multiple_intelligences",
    },
    "link_label": {
        "ru": "о теории множественного интеллекта",
        "kz": "көпсалалы интеллект теориясы туралы",
        "en": "about the theory of multiple intelligences",
    },
}


# ---------------------------------------------------------------------------
# MBTI
# ---------------------------------------------------------------------------

_MBTI = {
    "name": {
        "ru": "Индикатор типов И. Майерс — К. Бриггс (MBTI)",
        "kz": "Майерс — Бриггс типтер индикаторы (MBTI)",
        "en": "Myers — Briggs Type Indicator (MBTI)",
    },
    "short": {
        "ru": "Четыре биполярные дихотомии (E–I, S–N, T–F, J–P) плюс шкала "
              "ассертивности (A–T). Сочетание полюсов формирует 16 типов "
              "личности.",
        "kz": "Төрт биполярлы дихотомия (E–I, S–N, T–F, J–P) және ассертивтілік "
              "шкаласы (A–T). Полюстердің тіркесімі 16 тұлға типін құрайды.",
        "en": "Four bipolar dichotomies (E–I, S–N, T–F, J–P) plus an "
              "assertiveness scale (A–T). The combination of poles forms 16 "
              "personality types.",
    },
    "strengths": {
        "ru": "Широко распространён, есть большая интерпретационная база. "
              "Удобен для быстрой типологической ориентации и понимания "
              "когнитивного стиля пользователя.",
        "kz": "Кең таралған, үлкен түсіндірме базасы бар. Жылдам типологиялық "
              "бағдарлау және пайдаланушының когнитивтік стилін түсіну үшін "
              "ыңғайлы.",
        "en": "Widely used with a large interpretive base. Useful for quick "
              "typological orientation and understanding the user's cognitive "
              "style.",
    },
    "weaknesses": {
        "ru": "Биполярность шкал упрощает реальную непрерывную структуру черт. "
              "Ретестовая надёжность по ряду исследований оценивается как "
              "умеренная — тип может «плавать» от прохождения к прохождению.",
        "kz": "Шкалалардың биполярлығы белгілердің нақты үздіксіз құрылымын "
              "жеңілдетеді. Ретест сенімділігі бірқатар зерттеулерде орташа "
              "деп бағаланған — тип қайта тапсырғанда «жылжуы» мүмкін.",
        "en": "The bipolar scales simplify the true continuous trait "
              "structure. Test-retest reliability is moderate in several "
              "studies — the type can drift between sessions.",
    },
    "use_in_system": {
        "ru": "В системе MBTI используется как корректирующий компонент: "
              "matcher.mbti (вес 0.20). Сравниваются непрерывные значения "
              "пяти независимых шкал с предпочтениями профессии.",
        "kz": "Жүйеде MBTI түзетуші компонент ретінде қолданылады: matcher.mbti "
              "(салмағы 0.20). Бес тәуелсіз шкаланың үздіксіз мәндері кәсіптің "
              "қалауларымен салыстырылады.",
        "en": "In the system, MBTI is used as a corrective component: "
              "matcher.mbti (weight 0.20). The continuous values of the five "
              "independent scales are compared to the profession's "
              "preferences.",
    },
    "link": {
        "ru": "https://en.wikipedia.org/wiki/Myers%E2%80%93Briggs_Type_Indicator",
        "kz": "https://en.wikipedia.org/wiki/Myers%E2%80%93Briggs_Type_Indicator",
        "en": "https://en.wikipedia.org/wiki/Myers%E2%80%93Briggs_Type_Indicator",
    },
    "link_label": {
        "ru": "о MBTI",
        "kz": "MBTI туралы",
        "en": "about MBTI",
    },
}


# ---------------------------------------------------------------------------
# Neiry / EEG
# ---------------------------------------------------------------------------

_NEIRY = {
    "name": {
        "ru": "ЭЭГ-маркеры Neiry (нейрогарнитура с сухими электродами)",
        "kz": "Neiry ЭЭГ-маркерлері (құрғақ электродты нейрогарнитура)",
        "en": "Neiry EEG markers (dry-electrode headset)",
    },
    "short": {
        "ru": "Спектральные характеристики ЭЭГ: индивидуальная альфа-пиковая "
              "частота, относительная мощность тета/альфа/бета-диапазонов, "
              "индексы концентрации, релаксации и утомления, эмоциональные "
              "маркеры (Chill, Stress, Focus, Anger, Self-control).",
        "kz": "ЭЭГ спектрлік сипаттамалары: жеке альфа-шыңдық жиілігі, "
              "тета/альфа/бета диапазондарының салыстырмалы қуаты, концентрация, "
              "релаксация және шаршау индекстері, эмоциялық маркерлер "
              "(Chill, Stress, Focus, Anger, Self-control).",
        "en": "EEG spectral features: individual alpha-peak frequency, "
              "relative power of theta/alpha/beta bands, concentration, "
              "relaxation and fatigue indices, emotion markers (Chill, "
              "Stress, Focus, Anger, Self-control).",
    },
    "strengths": {
        "ru": "Объективный канал: данные не опираются на самоотчёт, "
              "регистрируют физиологическое состояние мозга в момент сессии. "
              "Современная литература связывает индивидуальные альфа-частоты "
              "со скоростью обработки информации и когнитивным контролем.",
        "kz": "Объективті арна: деректер өзіндік есепке сүйенбейді, ми "
              "физиологиялық күйін сессия кезінде тіркейді. Заманауи "
              "әдебиет жеке альфа-жиіліктерді ақпаратты өңдеу жылдамдығымен "
              "және когнитивтік бақылаумен байланыстырады.",
        "en": "An objective channel: data do not rely on self-report and "
              "capture the brain's physiological state at the moment of the "
              "session. Modern literature links individual alpha frequencies "
              "to information-processing speed and cognitive control.",
    },
    "weaknesses": {
        "ru": "Требует наличия гарнитуры — без неё канал недоступен. Запись "
              "чувствительна к контексту (стресс, усталость, кофеин), есть "
              "артефакты. Связь со «способностью к профессии» носит "
              "вероятностный характер, а не диагностический.",
        "kz": "Гарнитураны қажет етеді — онсыз арна қол жетімсіз. Жазба "
              "контекстке сезімтал (күйзеліс, шаршау, кофеин), артефактілер "
              "бар. «Кәсіпке қабілеттілікпен» байланыс ықтималдық сипатта, "
              "диагностикалық емес.",
        "en": "Requires the headset — without it the channel is unavailable. "
              "Recordings are sensitive to context (stress, fatigue, "
              "caffeine) and contain artefacts. The link to \"profession "
              "aptitude\" is probabilistic, not diagnostic.",
    },
    "use_in_system": {
        "ru": "В системе ЭЭГ-маркеры формируют когнитивный кластер "
              "(matcher.cluster, вес 0.10) и обучают супервайзерный слой "
              "ранжирования 20 ролей, который влияет на matcher.roles "
              "(вес 0.40).",
        "kz": "Жүйеде ЭЭГ-маркерлер когнитивтік кластерді (matcher.cluster, "
              "салмағы 0.10) қалыптастырады және 20 рөлдің рейтингін "
              "болжайтын супервайзерлік қабатты үйретеді, ол matcher.roles "
              "(салмағы 0.40) компонентіне әсер етеді.",
        "en": "In the system, EEG markers form the cognitive cluster "
              "(matcher.cluster, weight 0.10) and train the supervised layer "
              "that ranks the 20 roles, which feeds the matcher.roles "
              "component (weight 0.40).",
    },
    "link": {
        "ru": "https://neiry.tech/",
        "kz": "https://neiry.tech/",
        "en": "https://neiry.tech/",
    },
    "link_label": {
        "ru": "о ЭЭГ-гарнитуре Neiry",
        "kz": "Neiry ЭЭГ-гарнитурасы туралы",
        "en": "about the Neiry EEG headset",
    },
}


_TESTS = {"gardner": _GARDNER, "mbti": _MBTI, "neiry": _NEIRY}


def get_test_info(test_id: str, lang: str = "ru") -> TestInfo:
    """Return a localized `TestInfo` for the given test id ('gardner'|'mbti'|'neiry')."""
    raw = _TESTS[test_id]
    return TestInfo(
        name=_pick(raw["name"], lang),
        short=_pick(raw["short"], lang),
        strengths=_pick(raw["strengths"], lang),
        weaknesses=_pick(raw["weaknesses"], lang),
        use_in_system=_pick(raw["use_in_system"], lang),
        link=_pick(raw["link"], lang),
        link_label=_pick(raw["link_label"], lang),
    )


def all_tests(lang: str = "ru") -> tuple[TestInfo, TestInfo, TestInfo]:
    return (
        get_test_info("gardner", lang),
        get_test_info("mbti", lang),
        get_test_info("neiry", lang),
    )


# ---------------------------------------------------------------------------
# Critère итоговой оценки
# ---------------------------------------------------------------------------

SCORING_FORMULA = "score = 0.30 · Gardner + 0.20 · MBTI + 0.10 · Cluster + 0.40 · Roles"

_SCORING_DETAILS = {
    "Gardner": {
        "ru": "Похожесть профиля интеллектов пользователя на идеальный профиль "
              "профессии. Считается как 100 минус среднее отклонение по тем "
              "интеллектам, которые профессия объявила значимыми.",
        "kz": "Пайдаланушының интеллект профилінің кәсіптің мінсіз профиліне "
              "ұқсастығы. 100 минус кәсіп маңызды деп жариялаған интеллекттер "
              "бойынша орташа ауытқу ретінде есептеледі.",
        "en": "Similarity of the user's intelligence profile to the "
              "profession's ideal profile. Computed as 100 minus the mean "
              "deviation across intelligences the profession marks as "
              "important.",
    },
    "MBTI": {
        "ru": "Согласованность пяти непрерывных шкал MBTI пользователя с "
              "знаковыми предпочтениями профессии. Если профессия не задаёт "
              "предпочтения по дихотомии, она просто не учитывается.",
        "kz": "Пайдаланушының бес үздіксіз MBTI шкаласының кәсіптің таңбалы "
              "қалауларымен үйлесімділігі. Егер кәсіп дихотомия бойынша "
              "қалау қоймаса, ол ескерілмейді.",
        "en": "Agreement between the user's five continuous MBTI scales and "
              "the profession's signed preferences. If the profession sets no "
              "preference on a dichotomy, it is simply skipped.",
    },
    "Cluster": {
        "ru": "Совпадение когнитивного кластера пользователя (balanced / "
              "mobilized / depleted) с требованием профессии. Принимает "
              "дискретные значения 0, 50 или 100.",
        "kz": "Пайдаланушының когнитивтік кластерінің (balanced / mobilized "
              "/ depleted) кәсіп талабымен сәйкестігі. 0, 50 немесе 100 "
              "дискретті мәндерді қабылдайды.",
        "en": "Match between the user's cognitive cluster (balanced / "
              "mobilized / depleted) and the profession's requirement. Takes "
              "discrete values of 0, 50, or 100.",
    },
    "Roles": {
        "ru": "Средняя нормированная позиция top-ролей профессии в "
              "предсказанном ранжировании 20 ролей пользователя. Чем выше "
              "предсказанный ранг профессионально значимых ролей — тем "
              "выше компонент.",
        "kz": "Кәсіптің top-рөлдерінің пайдаланушының болжалған 20 рөлінің "
              "рейтингіндегі орташа нормаланған орны. Маңызды рөлдердің "
              "болжалған рангі неғұрлым жоғары болса, компонент де "
              "соғұрлым жоғары.",
        "en": "Average normalised position of the profession's top roles in "
              "the user's predicted 20-role ranking. The higher the predicted "
              "rank of professionally relevant roles, the higher the "
              "component.",
    },
}

_SCORING_NOTES = {
    "ru": "Веса задаются в боковой панели и могут быть изменены — при сумме "
          "не равной 1 они нормализуются автоматически. Итоговая оценка — "
          "число в диапазоне 0–100 и используется только для ранжирования: "
          "абсолютная разница между двумя профессиями в 5 баллов не имеет "
          "клинического смысла, но порядок мест устойчив.",
    "kz": "Салмақтар бүйір панелінде орнатылады және өзгертілуі мүмкін — "
          "қосынды 1-ге тең болмаса, олар автоматты түрде қалыпқа "
          "келтіріледі. Қорытынды балл 0–100 диапазонында және тек "
          "рейтингтеу үшін қолданылады: екі кәсіп арасындағы 5 баллдық "
          "айырмашылықтың клиникалық мәні жоқ, бірақ орындар тұрақты.",
    "en": "Weights are set in the sidebar and may be changed — if they do "
          "not sum to 1 they are auto-normalised. The total score is a 0–100 "
          "number used only for ranking: an absolute 5-point gap between two "
          "professions has no clinical meaning, but the order is stable.",
}


def scoring_details(lang: str = "ru") -> list[tuple[str, str]]:
    return [(name, _pick(d, lang)) for name, d in _SCORING_DETAILS.items()]


def scoring_notes(lang: str = "ru") -> str:
    return _pick(_SCORING_NOTES, lang)


# ---------------------------------------------------------------------------
# About blocks
# ---------------------------------------------------------------------------

_ABOUT_FUNC = {
    "ru": "NeuroCareer — гибридная система профориентации. По профилю "
          "пользователя из трёх источников (тест Гарднера, MBTI, ЭЭГ-маркеры) "
          "система:\n\n"
          "1. определяет когнитивный кластер;\n"
          "2. предсказывает ранжирование 20 профессиональных ролей;\n"
          "3. рассчитывает оценку соответствия 64 профессиям из базы знаний;\n"
          "4. формирует естественно-языковое объяснение топ-рекомендаций;\n"
          "5. экспортирует персональный PDF-отчёт.",
    "kz": "NeuroCareer — кәсіптік бағдарлаудың гибридтік жүйесі. Үш көзден "
          "(Гарднер тесті, MBTI, ЭЭГ-маркерлер) пайдаланушы профилі бойынша:\n\n"
          "1. когнитивтік кластерді анықтайды;\n"
          "2. 20 кәсіптік рөлдің рейтингін болжайды;\n"
          "3. білім қорындағы 64 кәсіпке сәйкестік бағасын есептейді;\n"
          "4. топ-ұсыныстарға табиғи тілді түсіндірме жасайды;\n"
          "5. жеке PDF-есепті экспорттайды.",
    "en": "NeuroCareer is a hybrid career-guidance system. Given a user "
          "profile from three sources (Gardner test, MBTI, EEG markers), it:"
          "\n\n"
          "1. detects the cognitive cluster;\n"
          "2. predicts the ranking of 20 professional roles;\n"
          "3. computes fit scores for 64 professions in the knowledge base;\n"
          "4. generates a natural-language explanation for top "
          "recommendations;\n"
          "5. exports a personal PDF report.",
}

_ABOUT_DATA = {
    "ru": "Пилотный набор данных — 47 респондентов × 65 признаков, собранных в "
          "ходе НИРМ магистранта. Для обучения супервайзерного слоя выборка "
          "расширена методом гауссовских копул (SDV) до 500 синтетических "
          "респондентов; синтез валидирован критерием Колмогорова — Смирнова "
          "(35 из 38 признаков прошли тест) и сохраняет корреляционную "
          "структуру оригинала.",
    "kz": "Пилоттық деректер жиыны — магистранттың ҒЗЖ барысында жиналған "
          "47 респондент × 65 белгі. Супервайзерлік қабатты үйрету үшін "
          "таңдама гаусс копулалары (SDV) әдісімен 500 синтетикалық "
          "респондентке кеңейтілді; синтез Колмогоров — Смирнов критерийімен "
          "тексерілді (38 белгінің 35-і өтті) және түпнұсқаның "
          "корреляциялық құрылымын сақтайды.",
    "en": "The pilot dataset has 47 respondents × 65 features, collected "
          "during the candidate's master's research. To train the supervised "
          "layer, the sample is expanded to 500 synthetic respondents via "
          "Gaussian copulas (SDV); the synthesis passes the Kolmogorov–"
          "Smirnov test on 35 of 38 features and preserves the original "
          "correlation structure.",
}

_ABOUT_MODEL = {
    "ru": "Супервайзерный слой — 20 регрессоров Random Forest, по одному на "
          "профессиональную роль. Качество (Спирмен): +0,823 в режиме "
          "«синтетика → реальные данные», +0,354 в честной CV. Объяснитель — "
          "локальная LLM Qwen2.5-7B через Ollama (с автоматическим fallback "
          "на детерминированный шаблон). Все компоненты работают на ноутбуке "
          "без платных внешних сервисов.",
    "kz": "Супервайзерлік қабат — 20 Random Forest регрессоры, әр кәсіптік "
          "рөлге біреуден. Сапа (Spearman): «синтетика → нақты деректер» "
          "режимінде +0,823, шынайы CV-да +0,354. Түсіндірмеші — Ollama "
          "арқылы жергілікті LLM Qwen2.5-7B (детерминирленген үлгіге "
          "автоматты түрде ауысумен). Барлық компоненттер ноутбукте ақылы "
          "сыртқы сервистерсіз жұмыс істейді.",
    "en": "The supervised layer is 20 Random Forest regressors, one per "
          "professional role. Quality (Spearman): +0.823 in the "
          "\"synthetic → real\" regime, +0.354 in honest CV. The explainer "
          "is a local Qwen2.5-7B LLM via Ollama, with automatic fallback to "
          "a deterministic template. All components run on a single laptop "
          "without paid external services.",
}

_ABOUT_DEV = {
    "ru": "Магистрант: Ғайни Әлихан Саятұлы, ОП 7M06103 «Машинное обучение и "
          "анализ данных», КарТУ им. Абылкаса Сагинова, 2024–2026. Научные "
          "руководители: к.т.н., доцент Томилова Н.И. и м.т.н., ст. "
          "преподаватель Кожанов М.Г.",
    "kz": "Магистрант: Ғайни Әлихан Саятұлы, 7M06103 «Машиналық оқыту және "
          "деректерді талдау» ББ, Абылқас Сағынов атындағы ҚарТУ, "
          "2024–2026. Ғылыми жетекшілер: т.ғ.к., доцент Томилова Н.И. және "
          "т.ғ.м., аға оқытушы Кожанов М.Г.",
    "en": "Candidate: Gayni Alikhan Sayatuly, programme 7M06103 \"Machine "
          "Learning and Data Analysis\", Abylkas Saginov Karaganda Technical "
          "University, 2024–2026. Supervisors: Tomilova N.I., PhD, Assoc. "
          "Prof., and Kozhanov M.G., M.Sc., Senior Lecturer.",
}


def about_functionality(lang: str = "ru") -> str: return _pick(_ABOUT_FUNC,  lang)
def about_dataset(lang: str = "ru") -> str:       return _pick(_ABOUT_DATA,  lang)
def about_model(lang: str = "ru") -> str:         return _pick(_ABOUT_MODEL, lang)
def about_developer(lang: str = "ru") -> str:     return _pick(_ABOUT_DEV,   lang)
