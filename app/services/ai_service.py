from groq import AsyncGroq
from app.core.config import settings
import json

client = AsyncGroq(api_key=settings.GROQ_API_KEY)

async def analyze_order(items: list[dict]) -> dict:
    """Buyurtma tarkibini AI tahlil qiladi: issiqligi, ehtiyotkorlik, yetkazish tavsiyasi"""
    items_text = "\n".join([f"- {i['name']} (kaloriya: {i.get('calories','?')}, issiq: {i.get('temperature_sensitive', False)})" for i in items])

    prompt = f"""Quyidagi buyurtma tarkibini tahlil qil:
{items_text}

JSON formatda qaytar:
{{
  "urgency": "high/medium/low",
  "temperature_warning": true/false,
  "max_delivery_minutes": <raqam>,
  "courier_advice": "<kuryerga maslahat>",
  "packaging_tip": "<qadoqlash tavsiyasi>"
}}
Faqat JSON qaytar, boshqa matn yo'q."""

    response = await client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    text = response.choices[0].message.content.strip()
    try:
        return json.loads(text)
    except Exception:
        return {"urgency": "medium", "courier_advice": text}

async def get_navigation_instructions(floor: int, apartment: str, has_elevator: bool, floor_map: dict | None) -> list[str]:
    """2.5D bino navigatsiyasi uchun yo'riqnoma"""
    prompt = f"""Kuryer bino ichida yetkazib bermoqda.
- Qavat: {floor}
- Kvartira: {apartment}
- Lift bor: {has_elevator}
- Bino xaritasi: {json.dumps(floor_map) if floor_map else 'mavjud emas'}

Kuryerga qisqa, aniq yo'riqnoma ber (JSON array):
["1-qadam", "2-qadam", ...]
Faqat JSON array qaytar."""

    response = await client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    text = response.choices[0].message.content.strip()
    try:
        return json.loads(text)
    except Exception:
        return [text]
