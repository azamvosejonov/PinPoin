# PinPoint Backend API

FastAPI asosida yaratilgan PinPoint Delivery backend API.

## Xususiyatlar

- FastAPI - zamonaviy, tez Python web framework
- PostgreSQL - bepul ochiq kodli database
- Docker - containerization
- Docker Compose - multi-container orchestration
- SQLAlchemy - ORM
- Pydantic - data validation

## Qurilish

### Talablar:

- Docker
- Docker Compose

### Ishga tushirish:

```bash
cd backend

# Docker Compose orqali barcha servislarni ishga tushirish
docker-compose up -d

# Loglarni ko'rish
docker-compose logs -f api

# To'xtatish
docker-compose down
```

### Servislar:

1. **PostgreSQL** - port 5432
2. **FastAPI** - port 8000
3. **pgAdmin** - port 5050 (database management uchun)

## API Endpoints

Base URL: `http://localhost:8000/api/v1`

### Deliveries
- `GET /deliveries` - Faol buyurtmalarni olish
- `GET /deliveries/{id}` - Buyurtmani ID bo'yicha olish
- `GET /deliveries/courier/{courier_id}/today` - Bugungi buyurtmalar
- `POST /deliveries` - Yangi buyurtma yaratish
- `PUT /deliveries/{id}` - Buyurtmani yangilash
- `PATCH /deliveries/{id}/status` - Holatni o'zgartirish
- `DELETE /deliveries/{id}` - Buyurtmani o'chirish

### Buildings
- `GET /buildings/{id}` - Binoni ID bo'yicha olish
- `GET /buildings/address` - Binoni manzil bo'yicha olish
- `GET /buildings/nearby` - Yaqin atrofdagi binolar
- `POST /buildings` - Yangi bino yaratish
- `PUT /buildings/{id}` - Binoni yangilash
- `GET /buildings/{building_id}/entrances` - Kirish joylari
- `POST /buildings/{building_id}/entrances` - Yangi kirish joyi
- `PATCH /buildings/entrances/{entrance_id}/confirm` - Kirish joyini tasdiqlash

### Domofon Codes
- `GET /domofon-codes/building/{building_id}` - Bino kodlari
- `GET /domofon-codes/building/{building_id}/verified` - Eng ko'p tasdiqlangan kod
- `GET /domofon-codes/{id}` - Kodni ID bo'yicha olish
- `GET /domofon-codes/find` - Kodni qidirish
- `POST /domofon-codes` - Yangi kod yaratish
- `PUT /domofon-codes/{id}` - Kodni yangilash
- `PATCH /domofon-codes/{id}/verify` - Kodni tasdiqlash
- `PATCH /domofon-codes/{id}/decrement` - Tasdiqlash sonini kamaytirish

### Locations
- `GET /locations/latest` - Oxirgi lokatsiya
- `GET /locations/since` - Vaqt bo'yicha lokatsiyalar
- `POST /locations` - Lokatsiyani saqlash
- `GET /locations/points/delivery/{delivery_id}` - Trayektoriya
- `GET /locations/points/recent` - So'nggi trayektoriya
- `POST /locations/points` - Lokatsiya nuqtasini saqlash
- `DELETE /locations/points/old` - Eski nuqtalarni o'chirish

## pgAdmin

pgAdmin orqali database'ni boshqarish:

- URL: http://localhost:5050
- Email: admin@pinpoint.com
- Password: admin123

## Mahalliy ishga tushirish (Docker siz)

```bash
# Virtual environment yaratish
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Dependencies o'rnatish
pip install -r requirements.txt

# PostgreSQL o'rnatish va ishga tushirish
# (lokalda PostgreSQL o'rnatilgan bo'lishi kerak)

# .env faylni yaratish
cp .env.example .env
# .env faylida DATABASE_URL ni o'zgartiring

# Server ishga tushirish
uvicorn main:app --reload
```

## Konfiguratsiya

`.env` faylida sozlamalarni o'zgartiring:

```env
DATABASE_URL=postgresql://pinpoint:pinpoint123@postgres:5432/pinpoint
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
API_V1_PREFIX=/api/v1
```

## Android ilovasi bilan bog'lash

Android ilovasida `ApiConfig.kt` faylni o'zgartiring:

```kotlin
object ApiConfig {
    const val BASE_URL = "http://YOUR_SERVER_IP:8000/api/"
}
```

Agar Docker Compose ishlatilsa:
```kotlin
const val BASE_URL = "http://10.0.2.2:8000/api/"  # Android emulator
# yoki
const val BASE_URL = "http://YOUR_LOCAL_IP:8000/api/"  # Real device
```

## Xavfsizlik

Production uchun:
1. `SECRET_KEY` ni o'zgartiring
2. HTTPS ishlating
3. API authentication qo'shing (JWT)
4. Rate limiting qo'shing
5. Input validation kuchaytiring
