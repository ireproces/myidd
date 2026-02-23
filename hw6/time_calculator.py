import datetime


def calculate_duration(start_time_str: str, end_time_str: str) -> float:
    # Format matching: "Sun Feb 22 01:05:55 PM CET 2026"
    # Note: %Z matches timezone names like CET, but standard library check is limited.
    # If the timezone is always the same, it is safer to strip it or ignore it for simple diffs.
    # %a = Weekday (Sun)
    # %b = Month name (Feb)
    # %d = Day of month (22)
    # %I = Hour 12-hr clock (01)
    # %M = Minute (05)
    # %S = Second (55)
    # %p = AM/PM (PM)
    # %Z = Timezone name (CET)
    # %Y = Year (2026)

    fmt = "%a %b %d %I:%M:%S %p %Z %Y"

    # If standard parsing fails due to %Z, you might need to handle timezones manually
    # or remove them if they are constant.

    try:
        start_dt = datetime.datetime.strptime(start_time_str, fmt)
        end_dt = datetime.datetime.strptime(end_time_str, fmt)
    except ValueError:
        # Fallback for systems where %Z is tricky (often simple removal works if tz matches)
        # Removing timezone for calculation if simple subtraction is needed
        fmt_no_tz = "%a %b %d %I:%M:%S %p %Y"
        start_time_str_clean = " ".join([p for p in start_time_str.split() if p not in ["CET", "CEST", "UTC"]])
        end_time_str_clean = " ".join([p for p in end_time_str.split() if p not in ["CET", "CEST", "UTC"]])

        # A more robust regex approach might be needed for variable timezones
        # But assuming fixed format from `date` command:
        parts_start = start_time_str.split()
        parts_end = end_time_str.split()
        # reconstruct without the timezone (index -2 usually)
        s_clean = f"{parts_start[0]} {parts_start[1]} {parts_start[2]} {parts_start[3]} {parts_start[4]} {parts_start[6]}"
        e_clean = f"{parts_end[0]} {parts_end[1]} {parts_end[2]} {parts_end[3]} {parts_end[4]} {parts_end[6]}"

        start_dt = datetime.datetime.strptime(s_clean, fmt_no_tz)
        end_dt = datetime.datetime.strptime(e_clean, fmt_no_tz)

    duration = (end_dt - start_dt).total_seconds()
    return duration


if __name__ == "__main__":
    # Example usage
    start = "Sun Feb 22 01:22:28 PM CET 2026"
    end = "Sun Feb 22 01:23:09 PM CET 2026"

    diff = calculate_duration(start, end)
    print(f"Duration: {diff} seconds")
