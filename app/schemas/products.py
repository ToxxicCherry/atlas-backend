from pydantic import BaseModel, Field, ConfigDict, computed_field
from typing import List

class ProductSizeSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str = Field()
    price_basic: int = Field()
    price_product: int = Field()

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
    name: str = Field()
    brand: str = Field()
    brand_id: int = Field()
    subject_id: int = Field(description='ID категории')
    sizes: List[ProductSizeSchema] = Field(default_factory=list)
    total_quantity: int = Field()
    rating: float = Field(ge=0, le=5)
    feedbacks: int = Field()
    supplier: str = Field()
    supplier_id: int = Field()
    supplier_rating: float = Field()
    weight: float = Field()
    wh: int = Field(description='ID склада')