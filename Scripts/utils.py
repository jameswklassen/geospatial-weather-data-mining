from datetime import datetime
from consts import DEG, YEAR


def get_units(var):
    if var == 'mean_sea_level_pressure':
        return 'kPa'
    else:
        return DEG + ' C'


def get_english_variable_name(var):
    if var == 'two_metre_temperature':
        return 'Two Metre Temperature'
    if var == 'mean_sea_level_pressure':
        return 'Mean Sea Level Pressure'
    if var == 'sea_surface_temperature':
        return 'Sea Surface Temperature'


def day_str(day):
    """
    Convert an integer day to a date string with format <Month Date, Year>
    e.g. 1 -> "Jan 1 2019"
    """
    padded = f"{int(day)+1:03d}"

    dt = datetime.strptime(padded, "%j")
    return dt.strftime(f"%B %d, {YEAR}")
