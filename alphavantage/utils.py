from datetime import datetime, timedelta


def next_update_time(current_time=None, offset=0, format_output=False):
    """ Returns datetime object when next update should happen. """
    assert isinstance(current_time, datetime) or current_time is None
    assert isinstance(offset, int) and 0 <= offset < 60

    # Get current time if it was not provided
    if current_time is None:
        current_time = datetime.now()

    # Create update time object
    update_time = current_time + timedelta(
        minutes=5 - current_time.minute % 5,
        seconds=-current_time.second + offset,
        microseconds=-current_time.microsecond)

    # Return either formatted string or datetime object
    return update_time.strftime("%H:%M:%S") if format_output else update_time


def time_until_update(current_time=None, offset=0):
    """ Returns number of seconds until next update. """
    assert isinstance(current_time, datetime) or current_time is None
    assert isinstance(offset, int) and 0 <= offset < 60

    # Get current time if it was not provided
    if current_time is None:
        current_time = datetime.now()

    # Return time in seconds until next update
    return next_update_time(current_time, offset) - current_time
