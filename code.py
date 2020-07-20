"""
This example will figure out the current local time using the internet, and
then draw out a count-up clock since an event occurred!
Once the event is happening, a new graphic is shown
"""
import time
import board
import displayio
from adafruit_pyportal import PyPortal

# The start of quarantine, as per our notes.
QUARANTINE_YEAR = 2020
QUARANTINE_MONTH = 3
QUARANTINE_DAY = 10
# The start of protests, as per https://en.wikipedia.org/wiki/George_Floyd_protests_in_Portland,_Oregon
PROTEST_YEAR = 2020
PROTEST_MONTH = 5
PROTEST_DAY = 28
# Midnight
MIDNIGHT_HOUR = 0
MIDNIGHT_MINUTE = 0

# determine the current working directory
# needed so we know where to find files
cwd = ("/"+__file__).rsplit('/', 1)[0]
# Initialize the pyportal object and let us know what data to fetch and where
# to display it
pyportal = PyPortal(status_neopixel=board.NEOPIXEL, default_bg=0)

refresh_time = None
display = board.DISPLAY


def split_digits(value):
    digit_list = []
    if value >= 100:
        digit_list.append(int(value / 100))
        value %= 100
    digit_list.append(int(value / 10))
    value %= 10
    digit_list.append(value)
    return digit_list


def make_large_goup(large_number):
    digit_list = split_digits(large_number)
    # Position for 320x240 screen
    if len(digit_list) > 2:
        x_offset = 25
    else:
        x_offset = 70
    group = displayio.Group(x = 0, y = 0)

    for digit in digit_list:
        f = open("/bmp/digits-large-%d.bmp" % digit, "rb")
        digit_group = displayio.Group(x=x_offset, y=50)
        odb = displayio.OnDiskBitmap(f)
        digit_tile = displayio.TileGrid(odb, pixel_shader=displayio.ColorConverter())
        digit_group.append(digit_tile)
        group.append(digit_group)
        x_offset += 90
    return group


def make_small_goup(small_number):
    digit_list = split_digits(small_number)
    # Position for 320x240 screen
    if len(digit_list) > 2:
        x_offset = 229
    else:
        x_offset = 259
    group = displayio.Group(x = 0, y = 0)

    for digit in digit_list:
        f = open("/bmp/digits-small-%d.bmp" % digit, "rb")
        digit_group = displayio.Group(x=x_offset, y=194)
        odb = displayio.OnDiskBitmap(f)
        digit_tile = displayio.TileGrid(odb, pixel_shader=displayio.ColorConverter())
        digit_group.append(digit_tile)
        group.append(digit_group)
        x_offset += 30
    return group


def do_display(large_number, small_number):
    everything_group = displayio.Group(x=0, y=0)

    f_header = open("/bmp/header.bmp", "rb")
    header_group = displayio.Group(x = 0, y = 10)
    odb = displayio.OnDiskBitmap(f_header)
    header = displayio.TileGrid(odb, pixel_shader=displayio.ColorConverter())
    header_group.append(header)
    everything_group.append(header_group)

    f_small_header = open("/bmp/days_protest.bmp", "rb")
    small_header_group = displayio.Group(x=0, y=209)
    odb2 = displayio.OnDiskBitmap(f_small_header)
    small_header = displayio.TileGrid(odb2, pixel_shader=displayio.ColorConverter())
    small_header_group.append(small_header)
    everything_group.append(small_header_group)

    everything_group.append(make_large_goup(large_number))
    everything_group.append(make_small_goup(small_number))

    board.DISPLAY.show(everything_group)
    board.DISPLAY.refresh(target_frames_per_second=60)


def calculate_days_since(current_time, year, month, day):
    event_time = time.struct_time((year, month, day,
                                   MIDNIGHT_HOUR, MIDNIGHT_MINUTE, 0,  # we don't track seconds
                                   -1, -1, False))  # we dont know day of week/year or DST
    # We're going to do a little cheat here, since circuitpython can't
    # track huge amounts of time, we'll calculate the delta years here
    if current_time[0] > (year + 1):  # we add one year to avoid half-years
        years_since = current_time[0] - (year + 1)
        # and then set the event_time to not include the year delta
        event_time = time.struct_time((year + years_since, month, day,
                                       MIDNIGHT_HOUR, MIDNIGHT_MINUTE, 0,  # we don't track seconds
                                       -1, -1, False))  # we dont know day of week/year or DST
    else:
        years_since = 0
    print(event_time)
    since = time.mktime(now) - time.mktime(event_time)
    print("Time since not including years (in sec):", since)
    sec_since = since % 60
    since //= 60
    mins_since = since % 60
    since //= 60
    hours_since = since % 24
    since //= 24
    days_since = since % 365
    since //= 365
    years_since += since
    return days_since


do_display(large_number=0, small_number=0)

while True:
    # only query the online time once per hour (and on first run)
    if (not refresh_time) or (time.monotonic() - refresh_time) > 3600:
        try:
            print("Getting time from internet!")
            pyportal.get_local_time()
            refresh_time = time.monotonic()
        except RuntimeError as e:
            print("Some error occured, retrying! -", e)
            continue

    now = time.localtime()
    #print("Current time:", now)

    quarantine_days = calculate_days_since(now, QUARANTINE_YEAR, QUARANTINE_MONTH, QUARANTINE_DAY)
    protest_days = calculate_days_since(now, PROTEST_YEAR, PROTEST_MONTH, PROTEST_DAY)

    do_display(large_number=quarantine_days, small_number=protest_days)

    # update every minute
    time.sleep(60)
