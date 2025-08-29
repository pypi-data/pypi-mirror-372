from __future__ import annotations

from typing import Union

from hamcrest.core.base_matcher import BaseMatcher, Description, Matcher, T

L = list[T]


class HasLastElement(BaseMatcher[L]):
    def __init__(self, matcher: Matcher[T]) -> None:
        self.matcher = matcher

    def _matches(self, item: L) -> bool:
        if not item:
            return False
        item_last = item[-1]
        return self.matcher.matches(item_last)

    def describe_to(self, description: Description) -> None:
        description.append_text("a list with last element").append_description_of(self.matcher)


def has_last_element(matcher: Matcher) -> HasLastElement:
    return HasLastElement(matcher)


class EndsWithSequence(BaseMatcher[L]):
    """
    Checks if a list ends with another list
    """

    def __init__(self, sequence: L) -> None:
        self.sequence = sequence

    def _matches(self, item: L) -> bool:
        if not item:
            return False
        # Check if the last n elements of the item match the given sequence
        return item[-len(self.sequence) :] == self.sequence

    def describe_to(self, description: Description) -> None:
        description.append_text(f"a list ending with {self.sequence}")


def ends_with_signal_value_sequence(sequence: L) -> EndsWithSequence:
    return EndsWithSequence(sequence)


class ContainsContiguousSublist(BaseMatcher[L]):
    def __init__(self, *sublist: T) -> None:
        self.sublist = list(sublist)

    def _has_consecutive_duplicates(self, seq: list) -> bool:
        return any(a == b for a, b in zip(seq, seq[1:]))

    def _matches(self, item: L) -> bool:
        if not item:
            return False

        if not self._has_consecutive_duplicates(self.sublist):
            filtered = [item[0]] if item else []
            for v in item[1:]:
                if v != filtered[-1]:
                    filtered.append(v)
        else:
            filtered = item

        sublist_len = len(self.sublist)
        if sublist_len > len(filtered):
            return False

        for i in range(len(filtered) - sublist_len + 1):
            if filtered[i : i + sublist_len] == self.sublist:
                return True
        return False

    def describe_to(self, description: Description) -> None:
        description.append_text(f"a list containing the contiguous sublist {self.sublist}")


def contains_signal_value_sequence(*sublist: T) -> ContainsContiguousSublist:
    return ContainsContiguousSublist(*sublist)


class ContainsContiguousSubdict(BaseMatcher[Union[dict[str, L], dict[str, dict[str, L]]]]):
    def __init__(self, expected: dict[str, L] | dict[str, dict[str, L]]) -> None:
        self.expected = expected

        self.matchers: dict[str, BaseMatcher] = {
            key: ContainsContiguousSubdict(subdict_or_sublist)
            if isinstance(subdict_or_sublist, dict)
            else contains_signal_value_sequence(*subdict_or_sublist)
            for key, subdict_or_sublist in expected.items()
        }

    def _matches(self, actual: dict[str, L] | dict[str, dict[str, L]]) -> bool:
        for key, matcher in self.matchers.items():
            if key not in actual or not matcher.matches(actual[key]):
                return False
        return True

    def describe_to(self, description: Description) -> None:
        description.append_text("a dict where each value contains its corresponding contiguous sublist: ")
        description.append_text(str(self.expected))


def contains_signal_value_sequences(expected: dict[str, L] | dict[str, dict[str, L]]) -> ContainsContiguousSubdict:
    return ContainsContiguousSubdict(expected)
