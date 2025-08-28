from countrytagger import tag_place
from ftmq.util import get_name_symbols
from followthemoney import model
from functools import cached_property
from pydantic import BaseModel, computed_field


PERSON = model["Person"]
ORG = model["Organization"]


class QueryString(BaseModel):
    q: str

    @computed_field
    @cached_property
    def symbols(self) -> set[str]:
        symbols: set[str] = set()
        symbols.update(get_name_symbols(PERSON, [self.q]))
        symbols.update(get_name_symbols(ORG, [self.q]))
        return symbols

    @computed_field
    @cached_property
    def countries(self) -> set[str]:
        countries: set[str] = set()
        results = tag_place(self.q)
        if results is not None and len(results):
            countries = {r[2] for r in results}
        return countries
