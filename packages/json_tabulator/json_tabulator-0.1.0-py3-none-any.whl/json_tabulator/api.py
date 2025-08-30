from dataclasses import dataclass
from .expression import Expression
from .query import QueryPlan
from .parser import parse_expression


@dataclass
class Attribute:
    name: str
    expression: Expression


@dataclass
class Query:
    attributes: list[Attribute]
    plan: QueryPlan
    omit_missing_attributes: bool

    def execute(self, data):
        return self.plan.execute(data, omit_missing_attributes=self.omit_missing_attributes)


def query(
        attributes: dict[str, str],
        omit_missing_attributes: bool = False
) -> Query:
    if isinstance(attributes, dict):
        attributes = [
            Attribute(name, expression=parse_expression(expr))
            for name, expr in attributes.items()
        ]
    else:
        raise ValueError(f'Query not understood: {attributes}')
    plan = QueryPlan.from_dict({a.name: a.expression for a in attributes})
    return Query(attributes, plan, omit_missing_attributes=omit_missing_attributes)
