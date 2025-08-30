from enum import Enum
import itertools as it

from .expression import Expression, Key, Star


class State(Enum):
    start_segment = 0
    within_segment = 1
    end_segment = 2
    double_quotes = 3
    single_quotes = 4


class InvalidExpression(ValueError):
    pass


def error(s, i):
    raise InvalidExpression(f'Parsing expression {s}, failed at position {i}')


def parse_expression(s: str) -> Expression:
    return Expression(_parse(s))


def _parse(s: str):
    state = State.start_segment
    i_token = 0
    for i, c in enumerate(it.chain(s, [None])):
        if c in ('.', None):
            if state in (State.within_segment, State.end_segment):
                if i_token is not None:
                    text = s[i_token:i]
                    if text == '*':
                        yield Star()
                    else:
                        yield Key(text)
                i_token = i + 1
                state = State.start_segment
            elif i == 0 and state == State.start_segment:
                pass
            else:
                error(s, i)
        elif c == '*':
            if state == State.start_segment:
                state = State.end_segment
            elif state in (State.double_quotes, State.single_quotes):
                pass
            else:
                error(s, i)
        elif c in ['"', "'"]:
            quote_state = State.double_quotes if c == '"' else State.single_quotes
            if state == State.start_segment:
                i_token = i + 1
                state = quote_state
            elif state == quote_state:
                yield Key(s[i_token:i])
                i_token = None
                state = State.end_segment
        else:
            if state in (State.start_segment, State.within_segment):
                state = State.within_segment
            elif state in (State.double_quotes, State.single_quotes):
                pass
            else:
                error(s, i)
