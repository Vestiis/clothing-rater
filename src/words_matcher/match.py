from dataclasses import dataclass
from functools import cached_property
from typing import List


@dataclass
class Match:
    found_word: str
    matching_sub_sentence: str
    score: float
    sentence: str

    @cached_property
    def start(self):
        return self.sentence.find(self.matching_sub_sentence)

    @cached_property
    def end(self):
        return self.start + len(self.matching_sub_sentence) - 1


class MatchFilter:
    best = "best"
    longest = "longest"


@dataclass
class OverlappingMatches:
    left_bound: int
    right_bound: int
    matches: List[Match]

    def match_overlaps(self, match: Match):
        if (
            self.left_bound <= match.start <= self.right_bound
            or self.left_bound <= match.end <= self.right_bound
        ):
            return True
        return False

    def add(self, match: Match):
        if not self.match_overlaps(match):
            raise Exception
        self.matches.append(match)
        self.left_bound = min(self.left_bound, match.start)
        self.right_bound = max(self.right_bound, match.end)
