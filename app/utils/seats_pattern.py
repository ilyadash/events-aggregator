def parse_seats_pattern(pattern: str) -> set[str]:
    seats: set[str] = set()
    for part in pattern.split(","):
        part = part.strip()
        if not part:
            continue
        letter = part[0]
        nums = part[1:]
        if "-" not in nums:
            start = end = int(nums)
        else:
            start_str, end_str = nums.split("-", 1)
            start = int(start_str)
            end = int(end_str)
        for num in range(start, end + 1):
            seats.add(f"{letter}{num}")
    return seats
