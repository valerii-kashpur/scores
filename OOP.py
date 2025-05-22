import math
from abc import ABC, abstractmethod
from typing import Tuple


class Normalizer(ABC):
    @abstractmethod
    def normalize(self, score: float, max_score: int, star_count: int) -> float:
        pass


class StarDistributor(ABC):
    @abstractmethod
    def distribute(self, stars: float, allow_half: bool, half_threshold: float, star_count: int) -> Tuple[
        int, int, int]:
        pass


class RatingFormatter(ABC):
    @abstractmethod
    def format(self, full: int, half: int, empty: int) -> str:
        pass


class RatingConfig:
    def __init__(
            self,
            max_score: int,
            star_count: int,
            filled: str,
            half: str,
            empty: str,
            allow_half: bool,
            half_threshold: float,
            normalizer: Normalizer,
            distributor: StarDistributor,
            formatter: RatingFormatter
    ):
        self.max_score = max_score
        self.star_count = star_count
        self.filled = filled
        self.half = half
        self.empty = empty
        self.allow_half = allow_half
        self.half_threshold = half_threshold
        self.normalizer = normalizer
        self.distributor = distributor
        self.formatter = formatter


class LinearNormalizer(Normalizer):
    def normalize(self, score: float, max_score: int, star_count: int) -> float:
        return (score / max_score) * star_count


class FullOnlyDistributor(StarDistributor):
    def distribute(self, stars: float, allow_half: bool, half_threshold: float, star_count: int) -> Tuple[
        int, int, int]:
        full = math.ceil(stars)
        full = min(full, star_count)
        return full, 0, star_count - full


class HalfStarDistributor(StarDistributor):
    def distribute(self, stars: float, allow_half: bool, half_threshold: float, star_count: int) -> Tuple[
        int, int, int]:
        stars = min(stars, star_count)
        full = int(stars)
        remainder = stars - full

        half = 0
        if allow_half and remainder >= half_threshold:
            half = 1

        if full + half > star_count:
            full = star_count - 1
            half = 1

        empty = star_count - full - half
        return full, half, empty


class StrictFullDistributor(StarDistributor):
    def distribute(self, stars: float, allow_half: bool, half_threshold: float, star_count: int) -> Tuple[
        int, int, int]:
        stars = min(stars, star_count)
        full = int(stars)
        remainder = stars - full

        if stars == star_count:
            return star_count, 0, 0

        half = 0
        if allow_half and remainder >= half_threshold:
            half = 1

        if full + half > star_count:
            full = star_count - 1
            half = 1

        empty = star_count - full - half
        return full, half, empty


class StarRatingFormatter(RatingFormatter):
    def __init__(self, filled: str, half: str, empty: str):
        self.filled = filled
        self.half = half
        self.empty = empty

    def format(self, full: int, half: int, empty: int) -> str:
        return self.filled * full + self.half * half + self.empty * empty


# main Class
class RatingRenderer:
    def __init__(self, config: RatingConfig):
        self.config = config

    def draw_rating(self, score: float) -> str:
        if not (0 <= score <= self.config.max_score):
            raise ValueError(f"Score must be between 0 and {self.config.max_score}, got {score}")

        stars = round(self.config.normalizer.normalize(score, self.config.max_score, self.config.star_count), 3)
        full, half_s, empty_s = self.config.distributor.distribute(
            stars, self.config.allow_half, self.config.half_threshold, self.config.star_count
        )
        return self.config.formatter.format(full, half_s, empty_s)


config_full_only = RatingConfig(
    max_score=100,
    star_count=5,
    filled="★",
    half="⯪",
    empty="☆",
    allow_half=False,
    half_threshold=0.25,
    normalizer=LinearNormalizer(),
    distributor=FullOnlyDistributor(),
    formatter=StarRatingFormatter(filled="★", half="⯪", empty="☆")
)

config_half = RatingConfig(
    max_score=100,
    star_count=5,
    filled="★",
    half="⯪",
    empty="☆",
    allow_half=True,
    half_threshold=0.25,
    normalizer=LinearNormalizer(),
    distributor=StrictFullDistributor(),
    formatter=StarRatingFormatter(filled="★", half="⯪", empty="☆")
)

config_seven_star = RatingConfig(
    max_score=130,
    star_count=7,
    filled="✪",
    half="◐",
    empty="·",
    allow_half=True,
    half_threshold=0.25,
    normalizer=LinearNormalizer(),
    distributor=HalfStarDistributor(),
    formatter=StarRatingFormatter(filled="✪", half="◐", empty="·")
)

if __name__ == "__main__":
    renderer_full_only = RatingRenderer(config_full_only)
    renderer_half = RatingRenderer(config_half)
    renderer_seven_star = RatingRenderer(config_seven_star)

    print("Full only:")
    print(renderer_full_only.draw_rating(76))  # ★★★★☆

    print("\nWith half stars:")
    print(renderer_half.draw_rating(87))  # ★★★★⯪
    print(renderer_half.draw_rating(100))  # ★★★★★
    print(renderer_half.draw_rating(82))  # ★★★★☆

    print("\n7-star scale (max 130):")
    print(renderer_seven_star.draw_rating(117))  # ✪✪✪✪✪✪◐
    print(renderer_seven_star.draw_rating(81))  # ✪✪✪✪◐··
