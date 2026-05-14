from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from config import Config

Base = declarative_base()

class ChatTurn(Base):
    __tablename__ = "chat_turns"
    id = Column(Integer, primary_key=True)
    session_id = Column(String(128), nullable=False)
    turn_index = Column(Integer, nullable=False)
    speaker = Column(String(16), nullable=False)  # 'user', 'bot'
    msg_txt = Column(Text)
    interruptions = Column(Boolean)
    choices_given = Column(Text)
    choice_from = Column(String(128))
    stt_confidence = Column(Float)
    feedback = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)
    tenant_id = Column(String(128))
    outlet_id = Column(String(128))
    user_id = Column(String(128))

engine = create_engine(Config.DB_URL, echo=False)
Base.metadata.create_all(engine)
SessionMaker = sessionmaker(bind=engine)

def insert_turn(turn):
    s = SessionMaker()
    s.add(turn)
    s.commit()
    s.close()

def next_turn_index(session_id):
    s = SessionMaker()
    idx = s.query(ChatTurn).filter_by(session_id=session_id).count()
    s.close()
    return idx