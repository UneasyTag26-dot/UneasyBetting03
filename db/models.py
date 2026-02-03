from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class Pick(Base):
    __tablename__ = "picks"
    id = Column(Integer, primary_key=True, index=True)
    player = Column(String, index=True)
    market = Column(String)
    line = Column(Float)
    side = Column(String)  # "over" or "under"
    model_prob = Column(Float)
    market_prob = Column(Float)
    edge = Column(Float)
    game_id = Column(String)
    player_id = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    suggested = Column(Boolean, default=True)
    result = Column(String, nullable=True)  # "win", "loss", "push", or None

    entries = relationship("EntryLeg", back_populates="pick")


class Entry(Base):
    __tablename__ = "entries"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    legs = relationship("EntryLeg", back_populates="entry")


class EntryLeg(Base):
    __tablename__ = "entry_legs"
    id = Column(Integer, primary_key=True, index=True)
    entry_id = Column(Integer, ForeignKey("entries.id"))
    pick_id = Column(Integer, ForeignKey("picks.id"))
    entry = relationship("Entry", back_populates="legs")
    pick = relationship("Pick", back_populates="entries")
