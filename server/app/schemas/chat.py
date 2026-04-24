from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class MessageSend(BaseModel):
    receiver_id: int  # receiver_id: to whom you are sending
    message: str
    file_url: Optional[str] = None     # file_url: optional file attachment link
   
 

class MessageResponse(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    message: str
    file_url: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True



class ConversationResponse(BaseModel):  # Shows the last message in each conversation
  
    user_id: int
    full_name: str
    last_message: str
    last_message_time: datetime
   
