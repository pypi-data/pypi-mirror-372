import time

def format_date_time(millisecond, format):
    result = time.strftime(format, time.localtime(millisecond))
    return result