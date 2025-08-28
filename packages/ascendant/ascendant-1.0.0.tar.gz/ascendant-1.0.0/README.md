# asc

**asc** is a small CLI that prints the current point of the ascendant within the tropical zodiac using either the user's public IP address or given geographic coordinates, useful for electional astrology. pairs nicely with [ephem](https://codeberg.org/sailorfe/ephem).

## usage

```
usage: asc [-h] [-g] [--save-config] [--show-config] [latitude] [longitude]

Calculate current tropical ascendant using coordinates from args or config file.

positional arguments:
  latitude       latitude (positive for north, negative for south)
  longitude      longitude (positive for east, negative for west)

options:
  -h, --help     show this help message and exit
  -g, --glyphs   show sign glyphs instead of abbreviated names
  --save-config  save provided coordinates to config file
  --show-config  show current config file location and contents
```

## license

per the [swiss ephemeris](https://www.astro.com/swisseph/swephinfo_e.htm), this software is licensed under the AGPL 3.0.
