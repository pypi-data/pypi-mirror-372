from datetime import datetime
from typing import Optional
from typing import List
import uuid
from ....usercenter.base_user import BaseUser
from .. import db
from ..orm import Mapped
from ..orm import mapped_column
from ..orm import relationship
from ..orm import ForeignKey
from ..orm import Table
from ..orm import Column
from .role import Role
from .user_profile import UserProfile

user_role_table = Table(
    "user_role",
    db.Model.metadata,
    Column("user_id", ForeignKey("user.id"), primary_key=True),
    Column("role_id", ForeignKey("role.id"), primary_key=True),
)


class User(db.Model, BaseUser):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    uuid: Mapped[str] = mapped_column(unique=True, default=lambda: str(uuid.uuid4()))
    username: Mapped[Optional[str]] = mapped_column(unique=True)
    password: Mapped[Optional[str]]
    display_name: Mapped[Optional[str]]
    avatar: Mapped[Optional[str]]
    status: Mapped[int] = mapped_column(default=0)
    expired_at: Mapped[Optional[datetime]]
    actived: Mapped[bool] = mapped_column(default=False)
    email: Mapped[Optional[str]] = mapped_column(unique=True)
    email_verified: Mapped[bool] = mapped_column(default=False)
    email_verified_at: Mapped[Optional[datetime]]
    phone_number: Mapped[Optional[str]] = mapped_column(unique=True)
    phone_verified: Mapped[bool] = mapped_column(default=False)
    phone_verified_at: Mapped[Optional[datetime]]
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.now, onupdate=datetime.now
    )

    roles: Mapped[List["Role"]] = relationship(secondary=user_role_table)

    profile: Mapped["UserProfile"] = relationship(
        "UserProfile", back_populates="user", uselist=False
    )

    def get_roles(self):
        return [r.name for r in self.roles]
    
    @property
    def is_active(self):
        return self.actived

    @property
    def is_authenticated(self):
        return True


# from sqlalchemy import event
# @event.listens_for(User, "before_insert")
# def receive_before_insert(mapper, connection, target):
#     "listen for the 'before_insert' event"
#     if target.uuid is None:
#         target.uuid = str(uuid.uuid4())
