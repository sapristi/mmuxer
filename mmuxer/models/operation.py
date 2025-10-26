from datetime import date, timedelta
from typing import ForwardRef

from imap_tools.query import AND as imap_AND
from imap_tools.query import NOT as imap_NOT
from imap_tools.query import OR as imap_OR
from imap_tools.query import H as imap_HEADER
from pydantic import ConfigDict

from mmuxer.models.action import Action

from .common import BaseModel
from .enums import Flag


class SearchCriteriaBase(BaseModel):
    model_config = ConfigDict(frozen=True)


class HasFlag(SearchCriteriaBase):
    flag: Flag

    def to_search_condition(self):
        return {self.flag.value.lower(): True}


class HasCustomFlag(SearchCriteriaBase):
    custom_flag: str

    def to_search_condition(self):
        return {"keyword": self.custom_flag}


class OlderThan(SearchCriteriaBase):
    older_than_days: int

    def to_search_condition(self):
        return {"date_lt": date.today() - timedelta(days=self.older_than_days)}


class YoungerThan(SearchCriteriaBase):
    younger_than_days: int

    def to_search_condition(self):
        return {"date_gte": date.today() - timedelta(days=self.younger_than_days)}


class Header(SearchCriteriaBase):
    name: str
    value: str

    def to_search_condition(self):
        return {"header": imap_HEADER(self.name, self.value)}


SearchCriteria = HasFlag | HasCustomFlag | OlderThan | YoungerThan | Header

All = ForwardRef("All")  # type: ignore
Any = ForwardRef("Any")  # type: ignore
Not = ForwardRef("Not")  # type: ignore


class All(BaseModel):
    ALL: list[SearchCriteria | All | Any | Not]

    def to_search_condition(self):
        args = []
        kwargs = {}
        for value in self.ALL:
            if isinstance(value, BoolOperator):
                args.append(value.to_search_condition())
            else:
                kwargs.update(value.to_search_condition())
        return imap_AND(*args, **kwargs)


class Any(BaseModel):
    ANY: list[SearchCriteria | All | Any | Not]

    def to_search_condition(self):
        args = []
        kwargs = {}
        for value in self.ANY:
            if isinstance(value, BoolOperator):
                args.append(value.to_search_condition())
            else:
                kwargs.update(value.to_search_condition())
        return imap_OR(*args, **kwargs)


class Not(BaseModel):
    NOT: SearchCriteria | All | Any | Not

    def to_search_condition(self):
        args = []
        kwargs = {}
        value = self.NOT
        if isinstance(value, BoolOperator):
            args.append(value.to_search_condition())
        else:
            kwargs.update(value.to_search_condition())
        return imap_NOT(*args, **kwargs)


BoolOperator = All | Any | Not
All.model_rebuild()
Any.model_rebuild()
Not.model_rebuild()


SearchQuery = SearchCriteria | All | Any | Not


class Operation(BaseModel):
    name: str
    folders: list[str]
    query: SearchQuery | None = None
    actions: list[Action]
    batch_size: int = 100
