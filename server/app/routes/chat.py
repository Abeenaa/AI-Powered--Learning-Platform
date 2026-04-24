  # /chat endpoints + WebSocket
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timezone
from ..database import get_db, SessionLocal
from ..models.chat import ChatMessage
from ..models.user import User
from ..schemas.chat import MessageSend, MessageResponse, ConversationResponse
from ..utils.dependencies import get_current_user
from ..utils.security import decode_access_token
from ..services.chat_service import manager

router = APIRouter(prefix="/chat", tags=["Chat"])

# ─── REST ENDPOINTS ──────

# Get list of all conversations for current user.
@router.get("/conversations", response_model=List[ConversationResponse])
def get_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Get all unique users this person has chatted with
    sent_to = db.query(ChatMessage.receiver_id).filter(
        ChatMessage.sender_id == current_user.id
    ).distinct().all()

    received_from = db.query(ChatMessage.sender_id).filter(
        ChatMessage.receiver_id == current_user.id
    ).distinct().all()

    # Combine and deduplicate user IDs
    user_ids = set()
    for (uid,) in sent_to:
        user_ids.add(uid)
    for (uid,) in received_from:
        user_ids.add(uid)

    conversations = []
    for uid in user_ids:
        other_user = db.query(User).filter(User.id == uid).first()
        if not other_user:
            continue

    # Get last message between these two users
        last_msg = db.query(ChatMessage).filter(
            ((ChatMessage.sender_id == current_user.id) & (ChatMessage.receiver_id == uid)) |
            ((ChatMessage.sender_id == uid) & (ChatMessage.receiver_id == current_user.id))
        ).order_by(ChatMessage.timestamp.desc()).first()

        if last_msg:
            conversations.append(ConversationResponse(
                user_id=uid,
                full_name=other_user.full_name,
                last_message=last_msg.message,
                last_message_time=last_msg.timestamp
            ))

    return conversations


# Get all messages between current user and another user.
@router.get("/{user_id}/messages", response_model=List[MessageResponse])
def get_messages(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
   
    messages = db.query(ChatMessage).filter(
        ((ChatMessage.sender_id == current_user.id) & (ChatMessage.receiver_id == user_id)) |
        ((ChatMessage.sender_id == user_id) & (ChatMessage.receiver_id == current_user.id))
    ).order_by(ChatMessage.timestamp.asc()).all()

    return messages

# Send a message via REST (non-real-time).
@router.post("/send", response_model=MessageResponse)
def send_message(
    data: MessageSend,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
   
    receiver = db.query(User).filter(User.id == data.receiver_id).first()
    if not receiver:
        raise HTTPException(status_code=404, detail="User not found")

    message = ChatMessage(
        sender_id=current_user.id,
        receiver_id=data.receiver_id,
        message=data.message,
        file_url=data.file_url,
        timestamp=datetime.now(timezone.utc)
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message

# ─── WEBSOCKET ENDPOINT ────


# Real-time chat via WebSocket.
@router.websocket("/ws/{receiver_id}")
async def websocket_chat(
    websocket: WebSocket,
    receiver_id: int,
    token: str = Query(...),  # Token passed as query param: ws://...?token=JWT
):
    
   
    
    # Verify token
    payload = decode_access_token(token)
    if not payload:
        await websocket.close(code=1008)  # Policy violation
        return

    user_id = int(payload.get("sub"))

    # Connect user
    await manager.connect(user_id, websocket)

    # Create DB session for this connection
    db = SessionLocal()

    try:
        while True:
            # Wait for message from this user
            data = await websocket.receive_json()
            message_text = data.get("message", "")
            file_url = data.get("file_url", None)

            if not message_text:
                continue

            # Save message to database
            message = ChatMessage(
                sender_id=user_id,
                receiver_id=receiver_id,
                message=message_text,
                file_url=file_url,
                timestamp=datetime.now(timezone.utc)
            )
            db.add(message)
            db.commit()
            db.refresh(message)

            # Prepare message payload
            msg_data = {
                "id": message.id,
                "sender_id": user_id,
                "receiver_id": receiver_id,
                "message": message_text,
                "file_url": file_url,
                "timestamp": message.timestamp.isoformat()
            }

            # Send to receiver if online (real-time delivery)
            await manager.send_personal_message(msg_data, receiver_id)

            # Also send back to sender (confirmation)
            await websocket.send_json(msg_data)

    except WebSocketDisconnect:
        manager.disconnect(user_id)
        db.close()
