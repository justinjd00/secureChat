from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID  # Verwenden von UUID-Typ
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = "Users"  # Tabellenname in der Datenbank

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    ip_address = Column(String, nullable=False)
    user_agent = Column(String, nullable=True)
    os = Column(String, nullable=True)
    registration_date = Column(DateTime, nullable=False)
    last_login = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<User(username={self.username}, email={self.email})>"

class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    sender_id = Column(UUID(as_uuid=True), ForeignKey("Users.id"), nullable=False)
    receiver_id = Column(UUID(as_uuid=True), ForeignKey("Users.id"), nullable=False)
    content = Column(String, nullable=False)
    timestamp = Column(DateTime)

    sender = relationship("User", foreign_keys=[sender_id])
    receiver = relationship("User", foreign_keys=[receiver_id])

    def __repr__(self):
        return f"<Message(sender={self.sender.username}, receiver={self.receiver.username}, content={self.content})>"

# New Contact table to store user connections
class Contact(Base):
    __tablename__ = "contacts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("Users.id"), nullable=False)
    contact_id = Column(UUID(as_uuid=True), ForeignKey("Users.id"), nullable=False)
    created_at = Column(DateTime, nullable=False)

    user = relationship("User", foreign_keys=[user_id])
    contact = relationship("User", foreign_keys=[contact_id])

    def __repr__(self):
        return f"<Contact(user_id={self.user_id}, contact_id={self.contact_id})>"