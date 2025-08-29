def parse_duration_to_nanoseconds(duration: str) -> int:
    """
    Parses a duration string (e.g., '30s', '1m', '500ms') into nanoseconds.

    Docker health-check timings are specified in nanoseconds. This utility
    converts human-readable strings into the required format.

    Args:
        duration: The duration string to parse.

    Returns:
        The equivalent duration in nanoseconds.
    """
    if not duration or not isinstance(duration, str):
        return 0

    duration = duration.lower().strip()

    value_str = "".join(filter(str.isdigit, duration))
    if not value_str:
        return 0

    value = int(value_str)

    if "ms" in duration:
        return value * 1_000_000
    if "s" in duration:
        return value * 1_000_000_000
    if "m" in duration:
        return value * 60 * 1_000_000_000
    if "h" in duration:
        return value * 3600 * 1_000_000_000

    # Assume seconds if no unit
    return value * 1_000_000_000
