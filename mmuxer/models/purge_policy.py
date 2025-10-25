from .common import BaseModel
from .enums import Flag


class PurgePolicy(BaseModel):
    name: str | None = None
    folder: str
    older_than_days: int
    flag: Flag | None = None
    custom_flag: str | None = None
    exclude_flagged: bool = True

    def display_name(self):
        return self.name or self.folder
