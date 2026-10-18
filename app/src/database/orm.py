from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey, Date, Float, Text, CheckConstraint
from enum import Enum
from sqlalchemy import Enum as SQLAlchemyEnum


class Base(DeclarativeBase):
    pass


class GameStatus(str, Enum):
    TO_PLAY = "A faire"
    COMPLETED = "Terminé"
    ABANDONED = "Platiné"


class PlatformsRAWG(Base):
    __tablename__ = "platforms_rawg"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    idRawg: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)

    games: Mapped[list["Game"]] = relationship(
        secondary="game_platforms", back_populates="platforms_rawg"
    )


class Game(Base):
    __tablename__ = "games"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    idRawg: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    playtimeRAWG: Mapped[int | None] = mapped_column(Integer, nullable=True)
    developers: Mapped[str | None] = mapped_column(String(255), nullable=True)
    publishers: Mapped[str | None] = mapped_column(String(255), nullable=True)
    tags: Mapped[str | None] = mapped_column(String(255), nullable=True)
    genres: Mapped[str | None] = mapped_column(String(255), nullable=True)
    release: Mapped[Date | None] = mapped_column(Date, nullable=True)
    imageUrl: Mapped[str | None] = mapped_column(String(255), nullable=True)

    platforms: Mapped[list["PlatformsRAWG"]] = relationship(
        secondary="game_platforms", back_populates="games"
    )

    commentaryId: Mapped[int] = mapped_column(
        ForeignKey("commentary.id"), unique=True, nullable=False
    )
    commentary: Mapped["Commentary"] = relationship(back_populates="game")


class GamePlatform(Base):
    __tablename__ = "game_platforms"

    game_id: Mapped[int] = mapped_column(
        ForeignKey("games.id"),
        primary_key=True,
    )

    platforms_rawg_id: Mapped[int] = mapped_column(
        ForeignKey("platforms_rawg.id"),
        primary_key=True,
    )


class Commentary(Base):
    __tablename__ = "commentary"
    __table_args__ = (
        CheckConstraint(
            "note BETWEEN -1 AND 5", name="check_commentary_note"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    note: Mapped[int] = mapped_column(Integer, nullable=False, default=-1)
    color: Mapped[str | None] = mapped_column(String(7), nullable=True)
    commentary: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[GameStatus] = mapped_column(
        SQLAlchemyEnum(
            GameStatus,
            native_enum=False,
            create_constraint=True,
            values_callable=lambda enum_status: [
                status.value for status in enum_status
            ],
        ),
        default=GameStatus.TO_PLAY,
        nullable=False,
    )

    gameId: Mapped[int] = mapped_column(
        ForeignKey("games.id"), unique=True, nullable=False
    )
    game: Mapped["Game"] = relationship(back_populates="commentary")
