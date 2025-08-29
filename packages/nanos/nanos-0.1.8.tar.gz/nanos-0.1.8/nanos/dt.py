import datetime


def days_after_now(
    days_num: int = 1, tz: datetime.tzinfo | None = datetime.timezone.utc
) -> datetime.datetime:
    """Returns a datetime object representing the date that is ``days_num`` days after now.

    Args:
        days_num (int): The number of days after now. Defaults to 1.
        tz (datetime.tzinfo, optional): The timezone to use. Defaults to
            :attr:`datetime.timezone.utc`.

    Returns:
        The datetime that is ``days_num`` days after now.
    """
    return datetime.datetime.now(tz=tz) + datetime.timedelta(days=days_num)


def tomorrow(tz: datetime.tzinfo | None = datetime.timezone.utc) -> datetime.datetime:
    """Returns a datetime object representing the date that is 1 day after now.

    Args:
        tz (datetime.tzinfo, optional): The timezone to use. Defaults to
            :attr:`datetime.timezone.utc`.

    Returns:
        The datetime that is 1 day after now.
    """
    return days_after_now(tz=tz)


def days_before_now(
    days_num: int = 1, tz: datetime.tzinfo | None = datetime.timezone.utc
) -> datetime.datetime:
    """Returns a datetime object representing the date that is ``days_num`` days before now.

    Args:
        days_num (int): The number of days before now. Defaults to 1.
        tz (datetime.tzinfo, optional): The timezone to use. Defaults to
            :attr:`datetime.timezone.utc`.

    Returns:
        The datetime that is ``days_num`` days before now.
    """
    return days_after_now(-days_num, tz=tz)


def yesterday(tz: datetime.tzinfo | None = datetime.timezone.utc) -> datetime.datetime:
    """Returns a datetime object representing the date that is 1 day before now.

    Args:
        tz (datetime.tzinfo, optional): The timezone to use. Defaults to
            :attr:`datetime.timezone.utc`.

    Returns:
        The datetime that is 1 day before now.
    """
    return days_before_now(tz=tz)


def yesterday_start(tz: datetime.tzinfo | None = datetime.timezone.utc) -> datetime.datetime:
    """Returns a datetime object representing the start of yesterday.

    Args:
        tz (datetime.tzinfo, optional): The timezone to use. Defaults to
            :attr:`datetime.timezone.utc`.

    Returns:
        The datetime that is the start of yesterday.
    """
    return datetime.datetime.combine(yesterday(tz=tz), datetime.datetime.min.time()).replace(
        tzinfo=tz
    )


def yesterday_end(tz: datetime.tzinfo | None = datetime.timezone.utc) -> datetime.datetime:
    """
    Returns a datetime object representing the end of yesterday.

    Args:
        tz (datetime.tzinfo, optional): The timezone to use. Defaults to
            :attr:`datetime.timezone.utc`.

    Returns:
        The datetime that is the end of yesterday.
    """
    return datetime.datetime.combine(yesterday(tz=tz), datetime.datetime.max.time()).replace(
        tzinfo=tz
    )


def today_eod(tz: datetime.tzinfo = datetime.timezone.utc) -> datetime.datetime:
    """
    Returns a datetime object representing the end of the current day.

    Args:
        tz (datetime.tzinfo, optional): The timezone to use. Defaults to
            :attr:`datetime.timezone.utc`.

    Returns:
        The datetime that is the end of the current day.
    """
    today = datetime.datetime.now().date()
    return datetime.datetime.combine(today, datetime.datetime.max.time()).replace(tzinfo=tz)
