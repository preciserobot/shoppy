from pydantic import BaseModel, Field, model_validator, ConfigDict
from typing import Optional, Dict
from datetime import datetime, timezone
from app.redis import DB
from app.config import ITEM_PREFIX

class Item(BaseModel):
    model_config = ConfigDict(extra='ignore')

    # main item data (the curated part)
    ean: str
    name: str
    detail: Optional[str] = Field(default=None, description="Item detail")
    quantity: Optional[int] = Field(default=1, description="Item quantity")
    unit: Optional[str] = Field(default='pcs', description="Item unit")

    # automatic timestamps
    created_at: Optional[str]
    updated_at: Optional[str]

    # source data (empty means manually added)
    src_data: Optional[Dict] = Field(default=None, description="Item data from API")
    src_url: Optional[str] = Field(default=None, description="Data source URL")

    @property
    def description(self):
        desc = []
        if self.detail:
            desc.append(self.detail)
        if self.quantity:
            desc.append(f"{self.quantity}{self.unit}")
        return ', '.join(desc)

    def update(self, item):
        assert isinstance(item, Item)
        assert self.ean == item.ean
        # merge items
        for k, v in item.model_dump().items():
            setattr(self, k, v)
        return self

    @classmethod
    def from_api(cls, ean):
        '''
        Fetches item data from an API and map to model
        '''
        return None
        raise NotImplementedError

    @classmethod
    def from_redis(cls, ean):
        db = DB()        
        data = db.get(f"{ITEM_PREFIX}{ean}")
        if not data:
            return None
        return cls(**data)

    @model_validator(mode='before')
    def pre(cls, values):
        # convert quantity to numeric
        values['quantity'] = int(values['quantity']) if values.get('quantity') else None
        # add timestamps
        now = datetime.now(timezone.utc).isoformat()
        values['updated_at'] = now
        if not values.get('created_at'):
            values['created_at'] = now
        return values

    def write(self, force=False):
        db = DB()
        data = self.model_dump()
        return db.set(f"{ITEM_PREFIX}{self.ean}", data)

    def delete(self):
        db = DB()
        return db.delete(f"{ITEM_PREFIX}{self.ean}")


