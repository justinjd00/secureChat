from sqlalchemy import Column, String, DateTime, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID  # Verwenden von UUID-Typ
from sqlalchemy.orm import relationship, declarative_base  # Updated import
import uuid
from datetime import datetime

# Use the new import for declarative_base
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

group_membership = Table(
    'group_membership', Base.metadata,
    Column('user_id', UUID(as_uuid=True), ForeignKey('Users.id'), primary_key=True),
    Column('group_id', UUID(as_uuid=True), ForeignKey('groups.id'), primary_key=True)
)

class Group(Base):
    __tablename__ = "groups"  # Name of the table in the database

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationship with users through the associative table (many-to-many)
    members = relationship("User", secondary=group_membership, back_populates="groups")

    # Relationship with group messages (one-to-many)
    messages = relationship("GroupMessage", back_populates="group", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Group(name={self.name})>"

class GroupMessage(Base):
    __tablename__ = "group_messages"  # Name of the table in the database

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    group_id = Column(UUID(as_uuid=True), ForeignKey('groups.id'), nullable=False)
    sender_id = Column(UUID(as_uuid=True), ForeignKey('Users.id'), nullable=False)
    content = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationship with the sender (many-to-one)
    sender = relationship("User", foreign_keys=[sender_id])

    # Relationship with the group (many-to-one)
    group = relationship("Group", back_populates="messages")

    def __repr__(self):
        return f"<GroupMessage(sender={self.sender.username}, group={self.group.name}, content={self.content})>"

# Update the User model to reflect the relationship with groups
User.groups = relationship(
    "Group",
    secondary=group_membership,
    back_populates="members"
)

User.sent_group_messages = relationship(
    "GroupMessage",
    back_populates="sender",
    cascade="all, delete-orphan"
)
