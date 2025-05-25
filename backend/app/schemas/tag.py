from pydantic import BaseModel


class TagBase(BaseModel):
    name: str


class TagCreate(TagBase):
    pass


class TagInDBBase(TagBase):
    id: int

    class Config:
        from_attributes = True


class Tag(TagInDBBase):
    pass


class TagRead(Tag):
    pass