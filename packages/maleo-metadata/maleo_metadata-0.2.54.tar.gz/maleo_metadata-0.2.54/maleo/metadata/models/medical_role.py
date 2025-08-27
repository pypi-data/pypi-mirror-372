from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import Integer, String
from maleo.soma.models.table import DataTable
from maleo.metadata.db import MaleoMetadataBase


class MedicalRolesMixin:
    parent_id = Column(
        "parent_id",
        Integer,
        ForeignKey("medical_roles.id", ondelete="SET NULL", onupdate="CASCADE"),
    )
    order = Column(name="order", type_=Integer)
    code = Column(name="code", type_=String(20), unique=True, nullable=False)
    key = Column(name="key", type_=String(255), unique=True, nullable=False)
    name = Column(name="name", type_=String(255), unique=True, nullable=False)


class MedicalRolesTable(MedicalRolesMixin, DataTable, MaleoMetadataBase):
    __tablename__ = "medical_roles"
    parent = relationship(
        "MedicalRolesTable",
        remote_side="MedicalRolesTable.id",
        # back_populates="specializations"
    )
    # specializations = relationship(
    #     "MedicalRolesTable",
    #     back_populates="parent",
    #     cascade="all",
    #     lazy="select",
    #     foreign_keys="[MedicalRolesTable.parent_id]",
    #     order_by="MedicalRolesTable.order"
    # )
