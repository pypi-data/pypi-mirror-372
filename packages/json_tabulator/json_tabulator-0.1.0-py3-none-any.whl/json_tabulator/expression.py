from dataclasses import dataclass
import itertools as it


@dataclass(frozen=True)
class Segment:
    pass


@dataclass(frozen=True)
class Key(Segment):
    value: str


@dataclass(frozen=True)
class Star(Segment):
    pass


@dataclass(frozen=True)
class Index(Segment):
    value: int



def is_wildcard(segment: Segment):
    return isinstance(segment, Star)


class Expression(tuple):
    def __repr__(self):
        return f'Expression({str(self)})'

    def __str__(self):
        def render_element(seg):
            if isinstance(seg, Star):
                return '*'
            elif isinstance(seg, Key):
                return seg.value
            elif isinstance(seg, Index):
                return str(seg.value)
            else:
                raise ValueError(f'Not a path segment: {seg}')

        return '.'.join(map(render_element, self))

    def _iter_generic(self):
        return (seg if isinstance(seg, Key) else Star() for seg in self)

    def get_attribute(self):
        return Expression(self._iter_generic())

    def get_table(self):
        idx = -1
        for i, p in enumerate(self._iter_generic()):
            if not isinstance(p, Key):
                idx = i
        return Expression(it.islice(self._iter_generic(), idx + 1))

    def is_valid(self):
        has_valid_elements = all(
            isinstance(value, Key) and isinstance(value.value, str)
            or isinstance(value, Index) and value.value >= 0
            or isinstance(value, Star)
            for value in self
        )
        return has_valid_elements and (self.is_generic() or self.is_concrete())

    def coincides_with(self, other):
        length = min(len(self), len(other))
        return self[:length] == other[:length]

    def get_row(self):
        idx = -1
        for i, seg in enumerate(self):
            if isinstance(seg, Index):
                idx = i
            elif isinstance(seg, Star):
                raise ValueError(f'Cannot get row because path is not concrete: {self}.')
        return Expression(self[:idx + 1])

    def is_generic(self):
        return not any(isinstance(seg, Index) for seg in self)

    def is_concrete(self):
        return not any(isinstance(seg, Star) for seg in self)

    def __add__(self, other):
        return Expression(super().__add__(other))
