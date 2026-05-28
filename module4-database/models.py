from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import uuid

Base = declarative_base()

class Channel(Base):
    __tablename__ = 'channels'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    notifications = relationship("Notification", back_populates="channel")
    templates = relationship("Template", back_populates="channel")

class Template(Base):
    __tablename__ = 'templates'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    subject = Column(String(200))
    body = Column(Text, nullable=False)
    channel_id = Column(Integer, ForeignKey('channels.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    channel = relationship("Channel", back_populates="templates")
    notifications = relationship("Notification", back_populates="template")

class Notification(Base):
    __tablename__ = 'notifications'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    channel_id = Column(Integer, ForeignKey('channels.id'))
    template_id = Column(Integer, ForeignKey('templates.id'))
    recipient = Column(String(200), nullable=False)
    status = Column(String(50), default='pending')
    sent_at = Column(DateTime)
    error = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    channel = relationship("Channel", back_populates="notifications")
    template = relationship("Template", back_populates="notifications")

# Подключение к PostgreSQL в Docker
DATABASE_URL = "postgresql://postgres:mysecretpassword@localhost:5432/notification_hub"

def get_engine():
    engine = create_engine(DATABASE_URL, echo=True)
    return engine

def create_tables():
    engine = get_engine()
    Base.metadata.create_all(engine)
    print("✅ Таблицы созданы!")

def get_session():
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()

if __name__ == "__main__":
    create_tables()
