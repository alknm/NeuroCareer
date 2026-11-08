"""LLM-based natural language explainer for profession matches (Layer 5).

The explainer takes the structured `ProfessionMatch` from the matcher and
produces a 3-5 sentence Russian explanation that cites the specific
intelligences, MBTI traits, cognitive cluster and roles that drove the
score.

Two backends are supported:
  * `ollama`   - HTTP request to a local Ollama server (default model:
                  qwen2.5:7b-instruct). Free, offline, works on CPU/GPU
                  depending on Ollama config.
  * `template` - Jinja-style template fallback that produces a valid
                  Russian explanation deterministically. Always works,
                  used as graceful fallback if Ollama is unavailable
                  and as a baseline reference in the dissertation.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Iterable
from urllib.error import URLError
from urllib.request import Request, urlopen

from .data_loader import GARDNER_FEATURES
from .matcher import ProfessionMatch


OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "qwen2.5:7b-instruct"
HTTP_TIMEOUT = 120  # seconds


# ---------------------------------------------------------------------------
# Public dataclass
# ---------------------------------------------------------------------------

@dataclass
class Explanation:
    profession_id: str
    backend: str           # "ollama" or "template"
    text: str
    prompt_tokens_estimate: int = 0


# ---------------------------------------------------------------------------
# Prompt construction
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = """Ты — карьерный консультант, помогающий студентам выбрать \
профессию. Тебе передают структурированный профиль человека (типология \
личности MBTI, интеллекты по Гарднеру, когнитивный кластер по ЭЭГ, \
прогнозируемые ролевые склонности) и одну рекомендованную профессию с \
числовыми оценками соответствия.

Твоя задача — кратко (3–5 предложений) объяснить пользователю, почему \
именно эта профессия ему подходит, опираясь на конкретные данные профиля. \
Пиши на русском, прямо, без шаблонных фраз вроде «вы — уникальная \
личность». Не выдумывай характеристики, которых нет во входных данных. \
Не добавляй заголовков и списков, только связный текст."""


def _format_user_block(user_meta: dict) -> str:
    intel_top = user_meta.get("top_intelligences", [])
    intel_str = ", ".join(f"{name} ({score:.0f})" for name, score in intel_top)
    return (
        f"Профиль пользователя:\n"
        f"  • MBTI: {user_meta.get('mbti', '—')}\n"
        f"  • Когнитивный кластер: {user_meta.get('cluster', '—')}\n"
        f"  • Ведущие интеллекты: {intel_str}"
    )


def _format_match_block(m: ProfessionMatch) -> str:
    intel_lines = "\n".join(
        f"    – {name}: пользователь {u:.0f}, идеал для профессии {i:.0f}"
        for name, u, i in m.matched_intelligences
    ) or "    – (не задано)"
    mbti_lines = "\n".join(
        f"    – {dim}: пользователь {u:+.0f}, предпочтение {p:+.0f}"
        for dim, u, p in m.matched_mbti
    ) or "    – (не задано)"
    role_lines = "\n".join(
        f"    – {role}: предсказанный ранг {rk}/20"
        for role, rk in m.matched_roles
    ) or "    – (не задано)"
    return (
        f"Рекомендованная профессия: {m.name_ru} ({m.category})\n"
        f"  Итоговая оценка соответствия: {m.total_score:.1f}/100\n"
        f"  Разбивка:\n"
        f"    • интеллекты Гарднера: {m.breakdown.gardner:.1f}\n"
        f"    • типологические черты MBTI: {m.breakdown.mbti:.1f}\n"
        f"    • совпадение когнитивного кластера: {m.breakdown.cluster:.1f}\n"
        f"    • ролевой профиль: {m.breakdown.roles:.1f}\n"
        f"  Совпадения по интеллектам:\n{intel_lines}\n"
        f"  Совпадения по MBTI:\n{mbti_lines}\n"
        f"  Совпадения по ролям:\n{role_lines}"
    )


def build_prompt(user_meta: dict, m: ProfessionMatch) -> str:
    return (
        f"{_SYSTEM_PROMPT}\n\n"
        f"{_format_user_block(user_meta)}\n\n"
        f"{_format_match_block(m)}\n\n"
        f"Объяснение (3–5 предложений):"
    )


# ---------------------------------------------------------------------------
# Backends
# ---------------------------------------------------------------------------

def _ollama_generate(prompt: str, model: str = DEFAULT_MODEL,
                     temperature: float = 0.5,
                     max_tokens: int = 350) -> str:
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": max_tokens,
            "top_p": 0.9,
        },
    }
    req = Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(req, timeout=HTTP_TIMEOUT) as resp:
        body = json.loads(resp.read().decode("utf-8"))
    return body.get("response", "").strip()


def _template_explanation(user_meta: dict, m: ProfessionMatch) -> str:
    """Deterministic Russian fallback - never fails, useful as baseline."""
    parts: list[str] = []

    # Lead sentence with profession name and numerical fit
    cluster_phrase = {
        "exact":    "ваш когнитивный профиль соответствует требованиям профессии",
        "any":      "профессия не требует специфического когнитивного состояния",
        "mismatch": "требуемое когнитивное состояние отличается от вашего",
    }.get(m.cluster_match_kind, "")
    parts.append(
        f"Профессия «{m.name_ru}» получила итоговую оценку соответствия "
        f"{m.total_score:.0f} из 100. {cluster_phrase.capitalize()}."
    )

    # Strongest matched intelligence
    if m.matched_intelligences:
        strongest = min(m.matched_intelligences, key=lambda t: abs(t[1] - t[2]))
        name, u, i = strongest
        if abs(u - i) < 15:
            parts.append(
                f"Ваш {name.lower()} ({u:.0f} из 100) близок к идеальному "
                f"уровню для этой профессии ({i:.0f})."
            )

    # MBTI alignment summary - name the actual side of each dichotomy
    if m.matched_mbti:
        aligned = [(d, u, p) for d, u, p in m.matched_mbti
                   if (u >= 0) == (p >= 0) and abs(p) > 10]
        if aligned:
            # (positive_side, negative_side)
            dim_sides = {
                "extraversion": ("экстраверсия", "интроверсия"),
                "intuition":    ("интуиция", "сенсорика"),
                "thinking":     ("логика в принятии решений", "опора на ценности и эмоции"),
                "judging":      ("склонность к планированию", "гибкость и спонтанность"),
                "assertive":    ("уверенность в себе", "повышенная самокритичность"),
            }
            phrases: list[str] = []
            for d, _, p in aligned[:2]:
                pos, neg = dim_sides.get(d, (d, d))
                phrases.append(pos if p >= 0 else neg)
            parts.append(
                f"По типу MBTI совпадают значимые черты: {', '.join(phrases)}."
            )

    # Role alignment summary
    if m.matched_roles:
        good_roles = [r for r, rk in m.matched_roles if rk <= 7]
        if good_roles:
            roles_str = ", ".join(good_roles[:3])
            parts.append(
                f"Прогнозируемый ролевой профиль выделяет у вас сильные "
                f"стороны для этой профессии: {roles_str}."
            )

    parts.append(
        "Это рекомендация-ориентир; окончательный выбор стоит делать с "
        "учётом личных предпочтений и опыта."
    )
    return " ".join(parts)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

class LLMExplainer:
    def __init__(self, backend: str = "auto", model: str = DEFAULT_MODEL,
                 temperature: float = 0.5):
        if backend not in {"auto", "ollama", "template"}:
            raise ValueError(f"unknown backend: {backend}")
        self.backend = backend
        self.model = model
        self.temperature = temperature
        self._ollama_available = self._probe_ollama() if backend != "template" else False

    def _probe_ollama(self) -> bool:
        try:
            req = Request("http://localhost:11434/api/tags", method="GET")
            with urlopen(req, timeout=3) as resp:
                resp.read()
            return True
        except (URLError, TimeoutError, OSError):
            return False

    def _resolved_backend(self) -> str:
        if self.backend == "template":
            return "template"
        if self.backend == "ollama":
            return "ollama"
        # auto
        return "ollama" if self._ollama_available else "template"

    def explain(self, user_meta: dict, m: ProfessionMatch) -> Explanation:
        backend = self._resolved_backend()
        if backend == "ollama":
            prompt = build_prompt(user_meta, m)
            try:
                text = _ollama_generate(prompt, self.model, self.temperature)
                return Explanation(
                    profession_id=m.profession_id, backend="ollama",
                    text=text, prompt_tokens_estimate=len(prompt) // 4,
                )
            except Exception:
                # graceful fallback
                pass
        text = _template_explanation(user_meta, m)
        return Explanation(profession_id=m.profession_id, backend="template",
                           text=text, prompt_tokens_estimate=0)

    def explain_top(self, user_meta: dict, matches: Iterable[ProfessionMatch],
                    n: int = 5) -> list[Explanation]:
        out: list[Explanation] = []
        for m in list(matches)[:n]:
            out.append(self.explain(user_meta, m))
        return out


def make_user_meta(row, cluster_label: str) -> dict:
    """Build the small dict of user metadata that the prompt needs."""
    intel = sorted(
        ((name, float(row[name])) for name in GARDNER_FEATURES),
        key=lambda t: t[1], reverse=True,
    )[:3]
    from .data_loader import MBTI_TYPE_COL
    return {
        "mbti": str(row[MBTI_TYPE_COL]),
        "cluster": cluster_label,
        "top_intelligences": intel,
    }


__all__ = [
    "Explanation", "LLMExplainer", "build_prompt", "make_user_meta",
    "DEFAULT_MODEL", "OLLAMA_URL",
]
