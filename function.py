import math
from typing import Callable


def normalize_score(score: float, max_score: int, star_count: int) -> float:
    # Convert any score to the number of stars in the range [0, star_count].
    return (score / max_score) * star_count


def full_only_distributor(
        stars: float, allow_half: bool, half_threshold: float, star_count: int
) -> tuple[int, int, int]:
    full = math.ceil(stars)
    full = min(full, star_count)
    return full, 0, star_count - full


def half_star_distributor(
        stars: float, allow_half: bool, half_threshold: float, star_count: int
) -> tuple[int, int, int]:
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


def draw_rating(score: float, config: dict) -> str:
    max_score = config.get("max_score", 100)
    if not (0 <= score <= max_score):
        raise ValueError(f"Score must be between 0 and {max_score}, got {score}")

    normalizer: Callable[[float, int, int], float] = config["normalizer"]
    distributor: Callable[[float, bool, float, int], tuple[int, int, int]] = config[
        "distributor"
    ]
    filled = config.get("filled", "★")
    half = config.get("half", "⯪")
    empty = config.get("empty", "☆")
    allow_half = config.get("allow_half", True)
    half_threshold = config.get("half_threshold", 0.25)
    star_count = config.get("star_count", 5)

    stars = round(normalizer(score, max_score, star_count), 3)

    full, half_stars, empty_stars = distributor(stars, allow_half, half_threshold, star_count)
    return filled * full + half * half_stars + empty * empty_stars


config_full_only = {
    "normalizer": normalize_score,
    "distributor": full_only_distributor,
    "filled": "★",
    "empty": "☆",
    "allow_half": False,
    "star_count": 5,
    "max_score": 100,
}

config_half = {
    "normalizer": normalize_score,
    "distributor": half_star_distributor,
    "filled": "★",
    "half": "⯪",
    "empty": "☆",
    "allow_half": True,
    "half_threshold": 0.25,
    "star_count": 5,
    "max_score": 90,
}

config_seven_star = {
    "normalizer": normalize_score,
    "distributor": half_star_distributor,
    "filled": "✪",
    "half": "◐",
    "empty": "·",
    "allow_half": True,
    "half_threshold": 0.25,
    "star_count": 7,
    "max_score": 130,
}

if __name__ == "__main__":
    print("Full only:")
    print(draw_rating(50, config_full_only))  # ★★★☆☆
    print(draw_rating(76, config_full_only))  # ★★★★☆
    print(draw_rating(100, config_full_only))  # ★★★★★

    print("\nWith half stars:")
    print(draw_rating(87, config_half))  # ★★★★⯪
    print(draw_rating(90, config_half))  # ★★★★★
    print(draw_rating(75, config_half))  # ★★★★☆

    print("\n7-star scale:")
    print(draw_rating(117, config_seven_star))  # ✪✪✪✪✪✪◐
    print(draw_rating(81, config_seven_star))  # ✪✪✪✪◐··
