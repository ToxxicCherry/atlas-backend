from .base import Base
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy import ForeignKey, BigInteger,  text, DateTime, func
from uuid import uuid4, UUID
from datetime import datetime
from typing import Optional


class ProductSizeModel(Base):
    __tablename__ = 'product_sizes'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4, server_default=text("gen_random_uuid()"))
    product_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("products.id"))
    name: Mapped[str]
    price_basic: Mapped[int]
    price_product: Mapped[int]

    products: Mapped['ProductModel'] = relationship('ProductModel', back_populates='sizes')

class ProductModel(Base):
    __tablename__ = 'products'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[Optional[str]]
    brand: Mapped[Optional[str]]
    brand_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    subject_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    total_quantity: Mapped[Optional[int]]
    rating: Mapped[Optional[float]]
    feedbacks: Mapped[Optional[int]]
    supplier: Mapped[Optional[str]]
    supplier_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    supplier_rating: Mapped[Optional[float]]
    weight: Mapped[Optional[float]]
    wh: Mapped[Optional[int]] = mapped_column(BigInteger)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    sizes: Mapped[list['ProductSizeModel']] = relationship('ProductSizeModel', back_populates='products', cascade='all, delete-orphan')
    positions: Mapped[list["PositionModel"]] = relationship("PositionModel", back_populates="product")

class TaskProductModel(Base):
    __tablename__ = 'task_products'

    task_id: Mapped[UUID] = mapped_column(ForeignKey("tasks.id", ondelete='CASCADE'), primary_key=True)
    product_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('products.id', ondelete='CASCADE'), primary_key=True)


class PositionModel(Base):
    __tablename__ = 'positions'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4, server_default=text("gen_random_uuid()"))
    task_id: Mapped[UUID] = mapped_column(ForeignKey("tasks.id", ondelete='CASCADE'), nullable=False)
    product_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    position: Mapped[int] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    task: Mapped['TaskModel'] = relationship('TaskModel', back_populates='positions')
    product: Mapped['ProductModel'] = relationship('ProductModel', back_populates='positions')