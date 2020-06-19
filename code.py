"""
This example will figure out the current local time using the internet, and
then draw out a count-up clock since an event occurred!
Once the event is happening, a new graphic is shown
"""
import time
import board
import displayio
from adafruit_pyportal import PyPortal

# The time of the thing!
EVENT_YEAR = 2020
EVENT_MONTH = 3
EVENT_DAY = 10
EVENT_HOUR = 0
EVENT_MINUTE = 0
# we'll make a python-friendly structure
event_time = time.struct_time((EVENT_YEAR, EVENT_MONTH, EVENT_DAY,
                               EVENT_HOUR, EVENT_MINUTE, 0,  # we don't track seconds
                               -1, -1, False))  # we dont know day of week/year or DST

# determine the current working directory
# needed so we know where to find files
cwd = ("/"+__file__).rsplit('/', 1)[0]
# Initialize the pyportal object and let us know what data to fetch and where
# to display it
pyportal = PyPortal(status_neopixel=board.NEOPIXEL,
                    default_bg=0)

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
    everything_group = displayio.Group(x = 0, y = 0)

    f_header = open("/bmp/header.bmp", "rb")
    header_group = displayio.Group(x = 0, y = 10)
    odb = displayio.OnDiskBitmap(f_header)
    header = displayio.TileGrid(odb, pixel_shader=displayio.ColorConverter())
    header_group.append(header)
    everything_group.append(header_group)

    everything_group.append(make_large_goup(large_number))

    # small_group = displayio.Group(x = 0, y = 0)
    # f_small_tens = open("/bmp/digits-small-%d.bmp" % little_tens, "rb")
    # small_tens_group = displayio.Group(x = 259, y = 194)
    # odb = displayio.OnDiskBitmap(f_small_tens)
    # small_tens_digit = displayio.TileGrid(odb, pixel_shader=displayio.ColorConverter())
    # small_tens_group.append(small_tens_digit)
    # small_group.append(small_tens_group)
    #
    # f_small_ones = open("/bmp/digits-small-%d.bmp" % little_ones, "rb")
    # small_ones_group = displayio.Group(x = 259 + 30, y = 194)
    # odb = displayio.OnDiskBitmap(f_small_ones)
    # small_ones_digit = displayio.TileGrid(odb, pixel_shader=displayio.ColorConverter())
    # small_ones_group.append(small_ones_digit)
    # small_group.append(small_ones_group)
    # everything_group.append(small_group)
    everything_group.append(make_small_goup(small_number))

    board.DISPLAY.show(everything_group)
    board.DISPLAY.refresh(target_frames_per_second=60)
    # f_header.close()
    # f_tens.close()
    # f_ones.close()
    # f_small_tens.close()
    # f_small_ones.close()


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

    # We're going to do a little cheat here, since circuitpython can't
    # track huge amounts of time, we'll calculate the delta years here
    if now[0] > (EVENT_YEAR+1):  # we add one year to avoid half-years
        years_since = now[0] - (EVENT_YEAR+1)
        # and then set the event_time to not include the year delta
        event_time = time.struct_time((EVENT_YEAR+years_since, EVENT_MONTH, EVENT_DAY,
                                       EVENT_HOUR, EVENT_MINUTE, 0,  # we don't track seconds
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

    do_display(large_number=days_since, small_number=(days_since - 4))

    # update every minute
    time.sleep(60)
