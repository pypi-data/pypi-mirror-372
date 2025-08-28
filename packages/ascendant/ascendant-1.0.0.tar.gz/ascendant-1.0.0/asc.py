import argparse
import configparser
import swisseph as swe
from datetime import datetime, timezone
from pathlib import Path

SIGNS = [
    ("Ari", "♈︎"),
    ("Tau", "♉︎"),
    ("Gem", "♊︎"),
    ("Can", "♋︎"),
    ("Leo", "♌︎"),
    ("Vir", "♍︎"),
    ("Lib", "♎︎"),
    ("Sco", "♏︎"),
    ("Sag", "♐︎"),
    ("Cap", "♑︎"),
    ("Aqu", "♒︎"),
    ("Pis", "♓︎")
]


CONFIG_DIR = Path.home() / '.config' / 'asc'
CONFIG_FILE = CONFIG_DIR / 'config.ini'


def load_config():
    """Load coordinates from config file."""
    if not CONFIG_FILE.exists():
        return None, None

    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)

    try:
        lat = config.getfloat('location', 'latitude')
        lng = config.getfloat('location', 'longitude')
        return lat, lng
    except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
        return None, None


def save_config(latitude, longitude):
    """Save coordinates to config file."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    config = configparser.ConfigParser()
    config['location'] = {
        'latitude': str(latitude),
        'longitude': str(longitude)
    }

    with open(CONFIG_FILE, 'w') as f:
        config.write(f)

    print(f"Saved coordinates to {CONFIG_FILE}")


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Calculate current tropical ascendant using coordinates from args or config file."
    )
    parser.add_argument(
        'latitude',
        nargs='?',
        type=float,
        help="latitude (positive for north, negative for south)"
    )
    parser.add_argument(
        'longitude',
        nargs='?',
        type=float,
        help="longitude (positive for east, negative for west)"
    )
    parser.add_argument(
        '-g', '--glyphs',
        action='store_true',
        help='show sign glyphs instead of abbreviated names'
    )
    parser.add_argument(
        '--save-config',
        action='store_true',
        help='save provided coordinates to config file'
    )
    parser.add_argument(
        '--show-config',
        action='store_true',
        help='show current config file location and contents'
    )
    return parser.parse_args()


def ascendant_sign(latitude, longitude, show_glyphs=False):
    now = datetime.now(timezone.utc)
    jd = swe.julday(
        now.year,
        now.month,
        now.day,
        now.hour + now.minute / 60 + now.second / 3600
    )

    houses = swe.houses(jd, latitude, longitude, b'W')
    asc_deg = houses[1][0]
    dms = swe.split_deg(asc_deg, 8)
    sign_abbr, sign_glyph = SIGNS[dms[4]]

    if show_glyphs:
        sign = sign_glyph
    else:
        sign = sign_abbr

    deg, mins = dms[0], dms[1]

    print(f"AC {deg:2d} {sign} {mins:2d}")


def main():
    args = parse_arguments()

    # Handle config display
    if args.show_config:
        if CONFIG_FILE.exists():
            lat, lng = load_config()
            if lat is not None and lng is not None:
                print(f"Config file: {CONFIG_FILE}")
                print(f"Saved coordinates: {lat}, {lng}")
            else:
                print("Config file exists but coordinates could not be read")
        else:
            print(f"No config file found at {CONFIG_FILE}")
        return 0

    # Get coordinates from args or config
    if args.latitude is not None and args.longitude is not None:
        lat, lng = args.latitude, args.longitude

        if args.save_config:
            save_config(lat, lng)
    else:
        lat, lng = load_config()
        if lat is None and lng is None:
            print("No coordinates provided and none saved in config.")
            print("Usage:")
            print("  asc 40.7128 -74.0060              # one-time use")
            print("  asc 40.7128 -74.0060 --save-config # save for future")
            print("  asc                                # use saved coordinates")
            return 1

    ascendant_sign(lat, lng, args.glyphs)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
