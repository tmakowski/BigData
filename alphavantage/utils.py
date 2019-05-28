from datetime import datetime, timedelta
from pytz import timezone


def curr_time(output_format=None, us_tz=False):
    """ Returns current local/us time. Formatted if format is provided. """
    current_time = datetime.now().astimezone()
    if us_tz:
        current_time = current_time.astimezone(timezone("US/Eastern"))
    return current_time if output_format is None else current_time.strftime(output_format)


def next_update_time(current_time=None, offset=0, output_format=None, us_tz=False):
    """ Returns datetime object when next update should happen.
    Returned time is a local time unless uz_timezone=True. """
    assert isinstance(current_time, datetime) or current_time is None
    assert isinstance(offset, int) and 0 <= offset < 60

    # Get current time if it was not provided
    if current_time is None:
        current_time = curr_time()

    # Check if stock market is open
    us_timezone = timezone("US/Eastern")
    current_time_useastern = current_time.astimezone(us_timezone)

    # If it's past 16 or before 9:30 UE Eastern time then next update will be at 9:30 US Eastern time
    already_closed = 16 <= current_time_useastern.hour
    still_closed = (current_time_useastern - timedelta(hours=9, minutes=30)).day < current_time_useastern.day

    if already_closed or still_closed or current_time_useastern.weekday() in [5, 6]:  # Check if it's weekend
        if current_time_useastern.weekday() in [5, 6]:  # Saturday & sunday
            days_offset = 7 - current_time_useastern.weekday()

        elif already_closed and current_time_useastern.weekday() == 4:  # Already closed on friday
            days_offset = 3

        elif already_closed:  # Already closed in middle of the week
            days_offset = 1

        else:
            days_offset = 0

        # Sets update time to local time corresponding to the 9:30 US Eastern time either the same day if the stock
        # market is yet to open or next working day if it's already closed. Note: does not include days off
        update_time = current_time + timedelta(
            days=days_offset,
            hours=-current_time_useastern.hour + 9,
            minutes=-current_time.minute + 30,
            seconds=-current_time.second + offset,
            microseconds=-current_time.microsecond)
    else:

        # If stock market is open then next update will be at next full 5 minutes
        update_time = current_time + timedelta(
            minutes=5 - current_time.minute % 5,
            seconds=-current_time.second + offset,
            microseconds=-current_time.microsecond)

    # Convert option to US Eastern
    if us_tz:
        update_time = update_time.astimezone(us_timezone)

    # Return either formatted string or datetime object
    return update_time if output_format is None else update_time.strftime(output_format)


def time_until_update(offset=0):
    """ Returns number of seconds until next update. """
    assert isinstance(offset, int) and 0 <= offset < 60

    # Get current time
    current_time = datetime.now()

    # Return time in seconds until next update
    return next_update_time(current_time, offset=offset) - current_time
