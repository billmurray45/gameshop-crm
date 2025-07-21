from sqlalchemy import Integer, String, DateTime, func, ForeignKey, Table, Column, Text, UniqueConstraint
from sqlalchemy.orm import mapped_column, Mapped, relationship
from app.core.database import Base
from datetime import datetime
from typing import List, Optional

game_platform = Table(
    'game_platform', Base.metadata,
    Column('game_id', ForeignKey('games.id', ondelete='CASCADE'), primary_key=True),
    Column('platform_id', ForeignKey('platforms.id', ondelete='CASCADE'), primary_key=True)
)


class Game(Base):
    __tablename__ = "games"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    platforms: Mapped[List["Platform"]] = relationship(
        "Platform",
        secondary=game_platform,
        back_populates="games",
        lazy="selectin"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    __table_args__ = (
        UniqueConstraint('name', 'year', name='uq_game_name_year'),
    )

    def __repr__(self) -> str:
        return f"<Game(id={self.id}, name='{self.name}', year={self.year})>"


class Platform(Base):
    __tablename__ = "platforms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    games: Mapped[List["Game"]] = relationship(
        "Game",
        secondary=game_platform,
        back_populates="platforms",
        lazy="selectin"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    def __repr__(self) -> str:
        return f"<Platform(id={self.id}, name='{self.name}')>"
