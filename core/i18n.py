"""Минимальная i18n-таблица для Streamlit-приложения.

Языки: ru (по умолчанию), kz (қазақша), en (English).

Все UI-строки лежат в одном словаре STRINGS, ключ — короткий ASCII-идентификатор.
Если для конкретного языка перевод отсутствует, возвращается русская версия.

Функция `t(key, lang)` — единственный публичный API: используется в app.py
повсеместно вместо литералов.
"""
from __future__ import annotations

LANG_CODES = ("ru", "kz", "en")
LANG_LABELS = {
    "ru": "Русский",
    "kz": "Қазақша",
    "en": "English",
}


# ---------------------------------------------------------------------------
# Главный словарь строк
# ---------------------------------------------------------------------------

STRINGS: dict[str, dict[str, str]] = {
    # --- sidebar / header ---
    "app_subtitle": {
        "ru": "Гибридная система профориентации",
        "kz": "Кәсіптік бағдарлаудың гибридтік жүйесі",
        "en": "Hybrid career-guidance system",
    },
    "language": {
        "ru": "Язык интерфейса",
        "kz": "Интерфейс тілі",
        "en": "Interface language",
    },
    "about_section": {
        "ru": "О программе",
        "kz": "Бағдарлама туралы",
        "en": "About",
    },
    "about_purpose": {
        "ru": "Назначение",
        "kz": "Мақсаты",
        "en": "Purpose",
    },
    "about_dataset": {
        "ru": "Датасет",
        "kz": "Деректер жиыны",
        "en": "Dataset",
    },
    "about_model": {
        "ru": "Модель",
        "kz": "Модель",
        "en": "Model",
    },
    "about_developer": {
        "ru": "Разработчик",
        "kz": "Әзірлеуші",
        "en": "Developer",
    },
    # --- profile source ---
    "source_section": {
        "ru": "1. Источник профиля",
        "kz": "1. Профиль көзі",
        "en": "1. Profile source",
    },
    "source_choose": {
        "ru": "Выберите режим:",
        "kz": "Режимді таңдаңыз:",
        "en": "Choose a mode:",
    },
    "source_pilot": {
        "ru": "Пилотный респондент (n=47)",
        "kz": "Пилоттық респондент (n=47)",
        "en": "Pilot respondent (n=47)",
    },
    "source_upload": {
        "ru": "Загрузить Neiry-выгрузку (.xlsx/.csv)",
        "kz": "Neiry-файлын жүктеу (.xlsx/.csv)",
        "en": "Upload Neiry export (.xlsx/.csv)",
    },
    "source_mini_test": {
        "ru": "Пройти короткий онлайн-тест",
        "kz": "Қысқа онлайн-тестті өту",
        "en": "Take the short online test",
    },
    "source_hint": {
        "ru": "Источник профиля пользователя. «Пилотный респондент» — выбор из 47 "
              "реальных профилей. «Загрузить Neiry-выгрузку» — собственный "
              "Excel/CSV с 65 признаками. «Пройти онлайн-тест» — короткий "
              "тест прямо в браузере (упрощённая версия без нейроданных).",
        "kz": "Пайдаланушы профилінің көзі. «Пилоттық респондент» — 47 нақты "
              "профильден таңдау. «Neiry-файлын жүктеу» — 65 белгісі бар "
              "өзіңіздің Excel/CSV. «Онлайн-тестті өту» — браузерде "
              "тікелей қысқа тест (нейродеректерсіз жеңілдетілген нұсқа).",
        "en": "Source of the user profile. \"Pilot respondent\" picks one of "
              "47 real profiles. \"Upload Neiry export\" reads your own "
              "Excel/CSV with all 65 features. \"Take the short online "
              "test\" runs a brief in-browser test (a simplified version "
              "without EEG data).",
    },
    "respondent": {
        "ru": "Респондент",
        "kz": "Респондент",
        "en": "Respondent",
    },
    "upload_label": {
        "ru": "Файл с профилем",
        "kz": "Профиль файлы",
        "en": "Profile file",
    },
    "upload_respondent": {
        "ru": "Респондент в файле",
        "kz": "Файлдағы респондент",
        "en": "Respondent in file",
    },
    "upload_error_read": {
        "ru": "Не удалось прочитать файл",
        "kz": "Файлды оқу мүмкін болмады",
        "en": "Failed to read the file",
    },
    "upload_error_columns": {
        "ru": "В файле отсутствуют обязательные колонки",
        "kz": "Файлда міндетті бағандар жоқ",
        "en": "Required columns are missing in the file",
    },
    "select_profile_hint": {
        "ru": "Выберите профиль в боковой панели",
        "kz": "Бүйірлік панельде профильді таңдаңыз",
        "en": "Pick a profile in the sidebar",
    },
    # --- weights ---
    "weights_section": {
        "ru": "2. Веса компонентов",
        "kz": "2. Компоненттер салмағы",
        "en": "2. Component weights",
    },
    "weights_hint": {
        "ru": "Веса четырёх компонентов итоговой оценки. Сумма нормализуется "
              "автоматически. Меняйте их для чувствительного анализа.",
        "kz": "Қорытынды бағаның төрт компонентінің салмағы. Қосынды "
              "автоматты түрде қалыпқа келтіріледі. Сезімталдық "
              "талдауы үшін өзгертіңіз.",
        "en": "Weights of the four components in the total score. The sum "
              "is normalised automatically. Tweak them for sensitivity "
              "analysis.",
    },
    "weights_sum_error": {
        "ru": "Сумма весов не может быть равна нулю",
        "kz": "Салмақтар қосындысы нөлге тең бола алмайды",
        "en": "Weight sum cannot be zero",
    },
    "weights_sum_caption": {
        "ru": "Сумма",
        "kz": "Қосынды",
        "en": "Sum",
    },
    "weights_normalised": {
        "ru": "нормализуется автоматически",
        "kz": "автоматты қалыпқа келтіріледі",
        "en": "auto-normalised",
    },
    "weight_gardner_help": {
        "ru": "Вес теста множественного интеллекта Г. Гарднера.",
        "kz": "Гарднердің көпсалалы интеллект тесінің салмағы.",
        "en": "Weight of the H. Gardner multiple-intelligence test.",
    },
    "weight_mbti_help": {
        "ru": "Вес типологии Майерс — Бриггс.",
        "kz": "Майерс — Бриггс типологиясының салмағы.",
        "en": "Weight of the Myers — Briggs typology.",
    },
    "weight_cluster_help": {
        "ru": "Вес совпадения когнитивного кластера пользователя с требованием профессии.",
        "kz": "Пайдаланушының когнитивті кластерінің кәсіп талабымен сәйкестігінің салмағы.",
        "en": "Weight of how well the user's cognitive cluster fits the profession.",
    },
    "weight_roles_help": {
        "ru": "Вес совпадения предсказанного ранжирования ролей с top-ролями профессии.",
        "kz": "Болжалған рөл рейтингінің кәсіптің top-рөлдерімен сәйкестігінің салмағы.",
        "en": "Weight of how well the predicted role ranking matches the profession's top roles.",
    },
    # --- LLM backend ---
    "llm_section": {
        "ru": "3. LLM-объяснитель",
        "kz": "3. LLM-түсіндірмеші",
        "en": "3. LLM explainer",
    },
    "backend_label": {
        "ru": "Backend:",
        "kz": "Backend:",
        "en": "Backend:",
    },
    "backend_hint": {
        "ru": "ollama — локальная LLM Qwen2.5-7B (медленнее, естественный текст); "
              "template — детерминированный шаблон (мгновенно); "
              "auto — пробует ollama, при недоступности откатывается к шаблону.",
        "kz": "ollama — жергілікті LLM Qwen2.5-7B (баяуырақ, табиғи мәтін); "
              "template — детерминирленген үлгі (бірден); "
              "auto — алдымен ollama-ны сынайды, қол жетімсіз болса, үлгіге өтеді.",
        "en": "ollama — local LLM Qwen2.5-7B (slower, more natural text); "
              "template — deterministic template (instant); "
              "auto — tries ollama and falls back to the template if unavailable.",
    },
    "ollama_active": {
        "ru": "Ollama активен",
        "kz": "Ollama белсенді",
        "en": "Ollama is active",
    },
    "ollama_unavailable": {
        "ru": "Ollama недоступен — используется шаблон",
        "kz": "Ollama қол жетімсіз — үлгі қолданылады",
        "en": "Ollama is unavailable — using the template",
    },
    "template_active": {
        "ru": "Активен шаблонный объяснитель",
        "kz": "Үлгілік түсіндірмеші белсенді",
        "en": "Template explainer is active",
    },
    # --- top_n ---
    "top_n_label": {
        "ru": "Сколько профессий показать",
        "kz": "Қанша кәсіпті көрсету керек",
        "en": "How many professions to show",
    },
    "top_n_hint": {
        "ru": "Сколько профессий показать в рекомендациях и включить в PDF-отчёт.",
        "kz": "Ұсыныстарда қанша кәсіпті көрсету және PDF-есепке қосу.",
        "en": "How many professions to display in recommendations and include in the PDF.",
    },
    # --- short instructions ---
    "instructions": {
        "ru": "Краткая инструкция",
        "kz": "Қысқаша нұсқаулық",
        "en": "Quick instructions",
    },
    "instructions_body": {
        "ru": "1. **Выберите профиль** в блоке 1 — пилотного респондента, "
              "загрузите свой файл или пройдите онлайн-тест.\n"
              "2. При необходимости **отрегулируйте веса** (блок 2).\n"
              "3. **Профиль** — три радар-/бар-карты по тестам.\n"
              "4. **Рекомендации** — топ-N профессий с покомпонентной разбивкой.\n"
              "5. **Детальный разбор** — выбор профессии и LLM-объяснение.\n"
              "6. **Отчёт** — экспорт PDF и CSV.",
        "kz": "1. 1-блокта **профильді таңдаңыз** — пилоттық респондент, "
              "файлыңыз немесе онлайн-тест.\n"
              "2. Қажет болса **салмақтарды реттеңіз** (2-блок).\n"
              "3. **Профиль** — тесттер бойынша үш радар/бар-диаграмма.\n"
              "4. **Ұсыныстар** — top-N кәсіп компоненттік бөлшекпен.\n"
              "5. **Толық талдау** — кәсіпті таңдау және LLM-түсіндірме.\n"
              "6. **Есеп** — PDF және CSV экспорттау.",
        "en": "1. **Pick a profile** in block 1 — pilot respondent, your "
              "own file, or the online test.\n"
              "2. **Tweak weights** in block 2 if needed.\n"
              "3. **Profile** tab — three radar/bar charts per test.\n"
              "4. **Recommendations** — top-N professions with component "
              "breakdown.\n"
              "5. **Detail** — pick a profession for LLM explanation.\n"
              "6. **Report** — export PDF and CSV.",
    },
    # --- tabs ---
    "tab_profile": {"ru": "Профиль", "kz": "Профиль", "en": "Profile"},
    "tab_recs":    {"ru": "Рекомендации", "kz": "Ұсыныстар", "en": "Recommendations"},
    "tab_detail":  {"ru": "Детальный разбор", "kz": "Толық талдау", "en": "Detail"},
    "tab_export":  {"ru": "Отчёт", "kz": "Есеп", "en": "Report"},
    # --- profile subtabs ---
    "subtab_gardner": {"ru": "Гарднер", "kz": "Гарднер", "en": "Gardner"},
    "subtab_mbti":    {"ru": "MBTI", "kz": "MBTI", "en": "MBTI"},
    "subtab_neiry":   {"ru": "Neiry / EEG", "kz": "Neiry / EEG", "en": "Neiry / EEG"},
    "subtab_roles":   {"ru": "Роли Neiry", "kz": "Neiry рөлдері", "en": "Neiry roles"},
    "subtab_about":   {
        "ru": "Об используемых тестах",
        "kz": "Қолданылатын тесттер туралы",
        "en": "About the tests",
    },
    "intelligence_col": {"ru": "Интеллект", "kz": "Интеллект", "en": "Intelligence"},
    "score_col":        {"ru": "Балл (0..100)", "kz": "Балл (0..100)", "en": "Score (0..100)"},
    "indices_baseline_actual": {
        "ru": "Когнитивные индексы — baseline vs actual",
        "kz": "Когнитивті индекстер — baseline vs actual",
        "en": "Cognitive indices — baseline vs actual",
    },
    "bands_title": {
        "ru": "Спектр (Theta / Alpha / Beta)",
        "kz": "Спектр (Theta / Alpha / Beta)",
        "en": "Spectrum (Theta / Alpha / Beta)",
    },
    "emotions_title": {
        "ru": "Эмоциональные маркеры",
        "kz": "Эмоциялық маркерлер",
        "en": "Emotion markers",
    },
    "full_neiry_table": {
        "ru": "Полная таблица ЭЭГ-признаков",
        "kz": "ЭЭГ-белгілерінің толық кестесі",
        "en": "Full EEG features table",
    },
    "predicted_roles_top10": {
        "ru": "Прогнозируемые роли Neiry — топ-10",
        "kz": "Болжалған Neiry рөлдері — top-10",
        "en": "Predicted Neiry roles — top 10",
    },
    "predicted_roles_caption": {
        "ru": "Ранг 1 — наиболее выраженная роль. Шкала «affinity = 21 − rank» "
              "переводит ранги в удобную для сравнения метрику высоты.",
        "kz": "Ранг 1 — ең айқын рөл. «affinity = 21 − rank» шкаласы рангтерді "
              "салыстыруға ыңғайлы биіктік метрикасына аударады.",
        "en": "Rank 1 = the most expressed role. The \"affinity = 21 − rank\" "
              "scale converts ranks into a comparable height metric.",
    },
    "mbti_type_label": {"ru": "Тип по MBTI", "kz": "MBTI типі", "en": "MBTI type"},
    "mbti_caption": {
        "ru": "Каждая полоса показывает отклонение от центральной точки 50:50 — "
              "слева доминирует один полюс дихотомии, справа — противоположный.",
        "kz": "Әр жолақ 50:50 ортасынан ауытқуды көрсетеді — солда бір полюс, "
              "оңда қарама-қарсысы басым.",
        "en": "Each bar shows the deviation from the 50:50 midpoint — one pole "
              "dominates on the left, the opposite pole on the right.",
    },
    # --- recommendations ---
    "scoring_expander": {
        "ru": "Как считается оценка рекомендации",
        "kz": "Ұсыныс бағасы қалай есептеледі",
        "en": "How the recommendation score is computed",
    },
    "scoring_formula_label": {"ru": "Формула.", "kz": "Формула.", "en": "Formula."},
    "top_n_section": {
        "ru": "Топ-{n} рекомендаций",
        "kz": "Top-{n} ұсыныс",
        "en": "Top {n} recommendations",
    },
    "rank_col":      {"ru": "rank", "kz": "rank", "en": "rank"},
    "prof_col":      {"ru": "профессия", "kz": "кәсіп", "en": "profession"},
    "category_col":  {"ru": "категория", "kz": "санат", "en": "category"},
    "composition_section": {
        "ru": "Состав итогового скора по компонентам",
        "kz": "Қорытынды баллдың компоненттер бойынша құрамы",
        "en": "Total score broken down by components",
    },
    # --- detail tab ---
    "pick_profession": {
        "ru": "Выберите профессию для детального разбора",
        "kz": "Толық талдау үшін кәсіпті таңдаңыз",
        "en": "Pick a profession for detail",
    },
    "breakdown_section":  {"ru": "Разбивка скора", "kz": "Балл бөлшектемесі", "en": "Score breakdown"},
    "category_field":     {"ru": "Категория", "kz": "Санат", "en": "Category"},
    "cluster_match_field":{"ru": "Cluster match", "kz": "Cluster match", "en": "Cluster match"},
    "matches_section":    {"ru": "Совпадения", "kz": "Сәйкестіктер", "en": "Matches"},
    "intel_subhead":      {"ru": "Интеллекты:", "kz": "Интеллекттер:", "en": "Intelligences:"},
    "mbti_subhead":       {"ru": "MBTI:", "kz": "MBTI:", "en": "MBTI:"},
    "roles_subhead":      {"ru": "Роли:", "kz": "Рөлдер:", "en": "Roles:"},
    "explain_section":    {"ru": "Объяснение", "kz": "Түсіндірме", "en": "Explanation"},
    "explain_spin_ollama": {
        "ru": "Генерация объяснения LLM...",
        "kz": "LLM-түсіндірмесін генерациялау...",
        "en": "Generating LLM explanation...",
    },
    "explain_spin_template": {
        "ru": "Сборка шаблонного объяснения...",
        "kz": "Үлгілік түсіндірмені жинау...",
        "en": "Assembling template explanation...",
    },
    "backend_label_caption": {"ru": "backend:", "kz": "backend:", "en": "backend:"},
    # --- export tab ---
    "pdf_section":   {"ru": "PDF-отчёт", "kz": "PDF-есеп", "en": "PDF report"},
    "pdf_descr":     {
        "ru": "Будет сгенерирован отчёт по топ-{n} рекомендациям.",
        "kz": "Top-{n} ұсыныс бойынша есеп жасалады.",
        "en": "A report for the top {n} recommendations will be generated.",
    },
    "pdf_caption": {
        "ru": "Объяснения для PDF собираются текущим выбранным backend ({b}). "
              "На больших top_n генерация LLM может занять минуту.",
        "kz": "PDF-түсіндірмелері ағымдағы backend ({b}) арқылы жиналады. "
              "Үлкен top_n үшін LLM-генерация бір минутқа созылуы мүмкін.",
        "en": "PDF explanations are built using the currently selected backend "
              "({b}). For large top_n, LLM generation may take a minute.",
    },
    "build_pdf_btn": {"ru": "Сформировать PDF", "kz": "PDF құру", "en": "Build PDF"},
    "build_pdf_spin":{
        "ru": "Генерация объяснений и сборка PDF...",
        "kz": "Түсіндірмелер мен PDF-ті жасау...",
        "en": "Generating explanations and assembling PDF...",
    },
    "done": {"ru": "Готово.", "kz": "Дайын.", "en": "Done."},
    "download_pdf": {"ru": "Скачать отчёт (.pdf)", "kz": "Есепті жүктеу (.pdf)", "en": "Download report (.pdf)"},
    "csv_section":  {"ru": "CSV-таблица рекомендаций", "kz": "Ұсыныстар CSV-кестесі", "en": "Recommendations CSV"},
    "download_csv": {"ru": "Скачать таблицу (.csv)", "kz": "Кестені жүктеу (.csv)", "en": "Download table (.csv)"},
    # --- footer ---
    "footer": {
        "ru": "NeuroCareer — практическая часть магистерской диссертации. "
              "Все рекомендации носят ориентировочный характер.",
        "kz": "NeuroCareer — магистрлік диссертацияның практикалық бөлігі. "
              "Барлық ұсыныстар бағдарлы сипатта.",
        "en": "NeuroCareer is the practical part of a master's thesis. "
              "All recommendations are advisory only.",
    },
    # --- mini-test page ---
    "mini_test_title": {
        "ru": "Короткий онлайн-тест",
        "kz": "Қысқа онлайн-тест",
        "en": "Short online test",
    },
    "mini_test_not_done": {
        "ru": "Тест ещё не пройден. Заполните форму в центральной части "
              "страницы и нажмите «Рассчитать рекомендации».",
        "kz": "Тест әлі өтілмеген. Беттің ортасындағы форманы толтырып, "
              "«Ұсыныстарды есептеу» түймесін басыңыз.",
        "en": "The test has not been taken yet. Fill the form in the main "
              "area and press \"Compute recommendations\".",
    },
    "mini_test_redo": {
        "ru": "Пройти тест заново",
        "kz": "Тесті қайта өту",
        "en": "Retake the test",
    },
    "mini_test_name_label": {
        "ru": "Как к вам обращаться?",
        "kz": "Сізге қалай үндесейік?",
        "en": "How should we address you?",
    },
    "mini_test_guest": {"ru": "Гость", "kz": "Қонақ", "en": "Guest"},
    "mini_test_part1": {
        "ru": "Часть 1. Гарднер ({n} утверждений)",
        "kz": "1-бөлім. Гарднер ({n} тұжырым)",
        "en": "Part 1. Gardner ({n} statements)",
    },
    "mini_test_part2": {
        "ru": "Часть 2. MBTI ({n} утверждений)",
        "kz": "2-бөлім. MBTI ({n} тұжырым)",
        "en": "Part 2. MBTI ({n} statements)",
    },
    "mini_test_caption": {
        "ru": "Оцените, насколько каждое утверждение про вас, по шкале от 1 "
              "(«совсем не про меня») до 5 («очень про меня»).",
        "kz": "Әр тұжырымның сізге қатыстылығын 1 («мен туралы емес») — "
              "5 («дәл мен туралы») шкаласымен бағалаңыз.",
        "en": "Rate how well each statement describes you on a 1 (\"not me "
              "at all\") to 5 (\"very much me\") scale.",
    },
    "mini_test_scale_caption_prefix": {
        "ru": "Шкала ответов: ",
        "kz": "Жауап шкаласы: ",
        "en": "Answer scale: ",
    },
    "mini_test_submit": {
        "ru": "Рассчитать рекомендации",
        "kz": "Ұсыныстарды есептеу",
        "en": "Compute recommendations",
    },
    "mini_test_warning_eeg": {
        "ru": "ЭЭГ-маркеры подставлены средними значениями пилотной выборки "
              "(нейрогарнитура не использовалась) — компонент Cluster в "
              "оценке менее информативен.",
        "kz": "ЭЭГ-маркерлері пилоттық таңдаманың орташа мәндерімен "
              "ауыстырылды (нейрогарнитура қолданылған жоқ) — Cluster "
              "компоненті аз ақпаратты.",
        "en": "EEG markers were substituted with pilot-sample averages "
              "(no EEG headset was used) — the Cluster component is less "
              "informative in this mode.",
    },
    "mini_test_warning_roles": {
        "ru": "Ранжирование 20 ролей рассчитано супервайзерным слоем только "
              "по психометрическим признакам.",
        "kz": "20 рөлдің рейтингі супервайзерлік қабатпен тек "
              "психометриялық белгілер бойынша есептелді.",
        "en": "The ranking of 20 roles was computed by the supervised layer "
              "from psychometric features only.",
    },
    # --- generic profile header ---
    "top1_score": {"ru": "Top-1 score", "kz": "Top-1 балл", "en": "Top-1 score"},
    "cluster_label": {"ru": "Cluster", "kz": "Cluster", "en": "Cluster"},
}


# ---------------------------------------------------------------------------
# Cluster descriptions (ранее в ui_helpers.CLUSTER_DESCRIPTION)
# ---------------------------------------------------------------------------

CLUSTER_DESCRIPTIONS: dict[str, dict[str, str]] = {
    "balanced": {
        "ru": "сбалансированный профиль: умеренные показатели концентрации, "
              "релаксации и утомляемости.",
        "kz": "тепе-теңдік профилі: концентрация, релаксация және "
              "шаршағыштықтың орташа көрсеткіштері.",
        "en": "balanced profile: moderate concentration, relaxation and "
              "fatigue indices.",
    },
    "mobilized": {
        "ru": "мобилизованный профиль: высокая концентрация, низкий уровень "
              "релаксации, низкая утомляемость — готовность к интенсивной "
              "умственной работе.",
        "kz": "жұмылдырылған профиль: жоғары концентрация, төмен релаксация, "
              "төмен шаршағыштық — қарқынды ой жұмысына дайындық.",
        "en": "mobilised profile: high concentration, low relaxation and low "
              "fatigue — ready for intense mental work.",
    },
    "depleted": {
        "ru": "истощённый профиль: пониженная концентрация, повышенная "
              "релаксация, выраженная утомляемость — подходят более щадящие "
              "режимы деятельности.",
        "kz": "сарқылған профиль: төмен концентрация, жоғары релаксация, "
              "айқын шаршағыштық — жұмсақ режимдер ұсынылады.",
        "en": "depleted profile: reduced concentration, elevated relaxation "
              "and pronounced fatigue — gentler work regimes are preferable.",
    },
}


def t(key: str, lang: str = "ru", **fmt) -> str:
    """Lookup a translated string. Returns Russian fallback if missing.

    Supports `str.format(**fmt)` placeholders. Unknown key returns the key
    itself wrapped in `[]` for debugging.
    """
    entry = STRINGS.get(key)
    if entry is None:
        return f"[{key}]"
    raw = entry.get(lang) or entry.get("ru", f"[{key}]")
    return raw.format(**fmt) if fmt else raw


def cluster_description(cluster_label: str, lang: str = "ru") -> str:
    """Return localized cluster description."""
    entry = CLUSTER_DESCRIPTIONS.get(cluster_label)
    if entry is None:
        return ""
    return entry.get(lang) or entry.get("ru", "")
