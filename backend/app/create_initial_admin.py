import asyncio
import os

from app.database import SessionLocal
from app import services, schemas


async def main() -> None:
    email = os.getenv("ADMIN_EMAIL")
    password = os.getenv("ADMIN_PASSWORD")

    if not email or not password:
        # No credentials provided, skip bootstrap
        print("[bootstrap] ADMIN_EMAIL or ADMIN_PASSWORD not set; skipping admin creation")
        return

    async with SessionLocal() as db:
        existing = await services.get_user_by_email(db, email.lower())
        if existing:
            print(f"[bootstrap] Admin user already exists: {existing.email}")
            return

        payload = schemas.UserCreate(
            email=email,
            password=password,
            full_name="Admin",
            phone=None,
            role=schemas.UserRole.admin,
        )

        user = await services.create_user(db, payload, auto_activate=True)
        print(f"[bootstrap] Admin user created: id={user.id}, email={user.email}")


if __name__ == "__main__":
    asyncio.run(main())
