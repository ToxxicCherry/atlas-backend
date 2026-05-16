from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict, computed_field
from typing import List, Optional, Union

class ProductSizeSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: Optional[str] = Field(default=None)
    price_basic: Optional[int] = Field(default=None)
    price_product: Optional[int] = Field(default=None)

    @computed_field()
    @property
    def discount_amount(self) -> int:
        return self.price_basic - self.price_product

    @computed_field()
    @property
    def discount_percent(self) -> int:
        if not self.price_basic:
            return 0
        return int(self.discount_amount / self.price_basic * 100)


class ProductSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field()
    name: Optional[str] = Field(default=None)
    brand: Optional[str] = Field(default=None)
    brand_id: Optional[int] = Field(default=None)
    subject_id: Optional[int] = Field(description='ID категории', default=None)
    sizes: List[ProductSizeSchema] = Field(default_factory=ProductSizeSchema)
    total_quantity: Optional[int] = Field(default=None)
    rating: Optional[float] = Field(ge=0, le=5, default=None)
    feedbacks: Optional[int] = Field(default=None)
    supplier: Optional[str] = Field(default=None)
    supplier_id: Optional[int] = Field(default=None)
    supplier_rating: Optional[float] = Field(default=None)
    weight: Optional[float] = Field(default=None)
    wh: Optional[int] = Field(description='ID склада', default=None)


class ProductPositionSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product: ProductSchema = Field(default_factory=ProductSchema)
    position: int = Field()
    created_at: datetime = Field()
