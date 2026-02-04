from dataclasses import dataclass
import re

@dataclass(frozen=True)
class Rule:
    pattern: re.Pattern[str]
    answer: str

RULES = [
    Rule(re.compile(r"\b(привет|здравствуй|hello|hi)\b", re.I), "Привет! Чем могу помочь?"),
    Rule(re.compile(r"\b(цена|стоимость|price)\b", re.I), "Цены зависят от услуги. Напишите, что именно вас интересует."),
    Rule(re.compile(r"\b(доставка|shipping)\b", re.I), "По доставке: обычно 1–3 дня по городу и 3–7 дней по регионам."),
    Rule(re.compile(r"\b(возврат|refund|return)\b", re.I), "Возврат возможен в течение 14 дней при сохранении товарного вида."),
    Rule(re.compile(r"\b(контакт|телефон|email|support)\b", re.I), "Можно написать в поддержку: support@example.com (замените на реальные контакты)."),
]

DEFAULT_ANSWER = "Я не нашёл подходящего ответа. Уточните, пожалуйста, ваш вопрос."

def get_bot_reply(text: str) -> str:
    t = text.strip()
    for rule in RULES:
        if rule.pattern.search(t):
            return rule.answer
    return DEFAULT_ANSWER
