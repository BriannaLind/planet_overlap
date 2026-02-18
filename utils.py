from datetime import datetime, timedelta


def estimate_scene_count(start_date: str,
                         end_date: str,
                         max_cloud: float,
                         scenes_per_day: float = 1.5) -> int:
    """
    Estimate number of scenes before execution.
    """

    days = (datetime.fromisoformat(end_date)
            - datetime.fromisoformat(start_date)).days

    estimated = int(days * scenes_per_day * (1 - max_cloud))
    return max(estimated, 0)


def generate_monthly_ranges(start_date: str, end_date: str):
    """
    Split date range into monthly windows.
    """

    ranges = []

    current = datetime.fromisoformat(start_date)
    end = datetime.fromisoformat(end_date)

    while current < end:
        next_month = (current.replace(day=28) + timedelta(days=4)).replace(day=1)
        window_end = min(next_month, end)

        ranges.append(
            (current.date().isoformat(),
             window_end.date().isoformat())
        )

        current = window_end

    return ranges
