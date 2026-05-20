from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User, UserRole
from app.models.support import SupportTicket, TicketMessage, TicketStatus, TicketCategory
from app.services.notification_service import notify_support_reply
from app.services.support_ws import manager
from jose import jwt, JWTError
from app.core.config import settings
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/support", tags=["Support"])

class TicketCreate(BaseModel):
    category: TicketCategory
    subject: str
    message: str
    order_id: Optional[int] = None

class MessageCreate(BaseModel):
    message: str

class TicketStatusUpdate(BaseModel):
    status: TicketStatus

# ── Ticket yaratish ───────────────────────────────────

@router.post("/tickets", status_code=201)
async def create_ticket(data: TicketCreate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    ticket = SupportTicket(
        user_id=user.id,
        order_id=data.order_id,
        category=data.category,
        subject=data.subject,
    )
    db.add(ticket)
    await db.flush()

    msg = TicketMessage(ticket_id=ticket.id, sender_id=user.id, message=data.message)
    db.add(msg)
    await db.commit()
    await db.refresh(ticket)
    return {"id": ticket.id, "subject": ticket.subject, "status": ticket.status}

# ── Ticketlar ro'yxati ────────────────────────────────

@router.get("/tickets")
async def my_tickets(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    if user.role == UserRole.admin:
        result = await db.execute(select(SupportTicket).order_by(SupportTicket.created_at.desc()))
    else:
        result = await db.execute(
            select(SupportTicket).where(SupportTicket.user_id == user.id).order_by(SupportTicket.created_at.desc())
        )
    tickets = result.scalars().all()
    return [{"id": t.id, "subject": t.subject, "category": t.category, "status": t.status, "created_at": t.created_at} for t in tickets]

# ── Xabarlar tarixi ───────────────────────────────────

@router.get("/tickets/{ticket_id}/messages")
async def get_messages(ticket_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    ticket_result = await db.execute(select(SupportTicket).where(SupportTicket.id == ticket_id))
    ticket = ticket_result.scalar_one_or_none()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket topilmadi")
    if ticket.user_id != user.id and user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Ruxsat yo'q")

    result = await db.execute(
        select(TicketMessage).where(TicketMessage.ticket_id == ticket_id).order_by(TicketMessage.created_at)
    )
    messages = result.scalars().all()
    return [{"id": m.id, "sender_id": m.sender_id, "message": m.message, "created_at": m.created_at} for m in messages]

# ── HTTP orqali xabar yuborish ────────────────────────

@router.post("/tickets/{ticket_id}/messages", status_code=201)
async def send_message(ticket_id: int, data: MessageCreate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    ticket_result = await db.execute(select(SupportTicket).where(SupportTicket.id == ticket_id))
    ticket = ticket_result.scalar_one_or_none()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket topilmadi")
    if ticket.user_id != user.id and user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Ruxsat yo'q")
    if ticket.status == TicketStatus.closed:
        raise HTTPException(status_code=400, detail="Yopilgan ticketga xabar yuborib bo'lmaydi")

    msg = TicketMessage(ticket_id=ticket_id, sender_id=user.id, message=data.message)
    db.add(msg)

    if user.role == UserRole.admin and ticket.status == TicketStatus.open:
        ticket.status = TicketStatus.in_progress

    await db.commit()
    await db.refresh(msg)

    payload = {
        "ticket_id": ticket_id,
        "sender_id": user.id,
        "sender_name": user.full_name,
        "role": user.role,
        "message": data.message,
        "created_at": str(msg.created_at),
    }

    # WebSocket orqali real-time yuborish
    await manager.broadcast_to_ticket(ticket_id, payload)

    # Admin javob berganda mijozga push notification
    if user.role == UserRole.admin:
        await notify_support_reply(ticket.user_id, ticket_id)

    return {"ok": True}

# ── Ticket statusini yangilash (admin) ────────────────

@router.patch("/tickets/{ticket_id}/status")
async def update_ticket_status(ticket_id: int, data: TicketStatusUpdate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    if user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Faqat adminlar uchun")
    ticket_result = await db.execute(select(SupportTicket).where(SupportTicket.id == ticket_id))
    ticket = ticket_result.scalar_one_or_none()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket topilmadi")
    ticket.status = data.status
    await db.commit()

    # Mijozga status o'zgargani haqida WebSocket xabari
    await manager.broadcast_to_ticket(ticket_id, {"type": "status_update", "status": data.status})
    return {"id": ticket_id, "status": data.status}

# ── WebSocket real-time chat ──────────────────────────

@router.websocket("/ws/{ticket_id}")
async def support_websocket(websocket: WebSocket, ticket_id: int, token: str, db: AsyncSession = Depends(get_db)):
    """
    Real-time support chat.
    Ulanish: ws://host/api/v1/support/ws/{ticket_id}?token=<jwt>
    """
    # Token tekshirish
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = int(payload.get("sub"))
    except (JWTError, TypeError):
        await websocket.close(code=4001)
        return

    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalar_one_or_none()
    if not user:
        await websocket.close(code=4001)
        return

    # Ticket mavjudligini va ruxsatni tekshirish
    ticket_result = await db.execute(select(SupportTicket).where(SupportTicket.id == ticket_id))
    ticket = ticket_result.scalar_one_or_none()
    if not ticket or (ticket.user_id != user.id and user.role != UserRole.admin):
        await websocket.close(code=4003)
        return

    await manager.connect(ticket_id, user.id, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            message_text = data.get("message", "").strip()
            if not message_text:
                continue
            if ticket.status == TicketStatus.closed:
                await websocket.send_json({"error": "Ticket yopilgan"})
                continue

            # DB ga saqlash
            msg = TicketMessage(ticket_id=ticket_id, sender_id=user.id, message=message_text)
            db.add(msg)
            if user.role == UserRole.admin and ticket.status == TicketStatus.open:
                ticket.status = TicketStatus.in_progress
            await db.commit()
            await db.refresh(msg)

            broadcast_payload = {
                "ticket_id": ticket_id,
                "sender_id": user.id,
                "sender_name": user.full_name,
                "role": user.role,
                "message": message_text,
                "created_at": str(msg.created_at),
            }

            # Barcha ulangan foydalanuvchilarga yuborish
            await manager.broadcast_to_ticket(ticket_id, broadcast_payload)

            # Admin yozsa mijozga push
            if user.role == UserRole.admin:
                await notify_support_reply(ticket.user_id, ticket_id)

    except WebSocketDisconnect:
        manager.disconnect(ticket_id, user.id)
