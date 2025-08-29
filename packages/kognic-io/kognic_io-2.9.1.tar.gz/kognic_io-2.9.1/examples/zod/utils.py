LIDARS = ["VLS128", "VLP16_Left", "VLP16_Right"]


def seconds_to_ns(seconds: float) -> int:
    return int(seconds * 1e9)


def ns_to_ms(ns: int) -> int:
    return int(ns / 1e6)
