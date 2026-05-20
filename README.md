# PinPoint Backend

Kuryer yetkazib berish tizimi — FastAPI, PostgreSQL, Redis, Groq AI

## O'rnatish

```bash
pip install -r requirements.txt
```

## .env sozlash

```
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/pinpoint
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-super-secret-key
GROQ_API_KEY=your_groq_api_key
```

## Ishga tushirish

```bash
uvicorn main:app --reload
```

## API Docs

http://localhost:8000/docs

---

## Asosiy endpointlar

| Method | URL | Tavsif |
|--------|-----|--------|
| POST | /api/v1/auth/register | Ro'yxatdan o'tish |
| POST | /api/v1/auth/login | Kirish |
| GET | /api/v1/restaurants/ | Restoranlar ro'yxati |
| POST | /api/v1/orders/ | Buyurtma berish (AI tahlil avtomatik) |
| GET | /api/v1/delivery/route/{order_id} | Kuryer marshruti (OSRM) |
| GET | /api/v1/delivery/navigate/{order_id} | 2.5D bino navigatsiyasi |
| POST | /api/v1/delivery/location | Kuryer joylashuvini yangilash |
| GET | /api/v1/delivery/track/{order_id} | Buyurtmani kuzatish |
| WS | /api/v1/delivery/ws/{order_id} | Real-time WebSocket tracking |
| POST | /api/v1/buildings/apartment-access | Kvartira kodini saqlash |
| GET | /api/v1/buildings/apartment-access/{building_id} | Saqlangan kodlar |

## Rollar

- `customer` — mijoz
- `courier` — kuryer
- `restaurant` — restoran egasi
- `company` — kuryer kompaniyasi
