"""Provides functions for the main GRASS GIS executable

(C) 2020 by Vaclav Petras and the GRASS Development Team

This program is free software under the GNU General Public
License (>=v2). Read the file COPYING that comes with GRASS
for details.

.. sectionauthor:: Vaclav Petras <wenzeslaus gmail com>
.. sectionauthor:: Linda Kladivova <l.kladivova seznam cz>

This is not a stable part of the API. Use at your own risk.
"""

import os
import tempfile
import getpass
import sys
from shutil import copytree, ignore_patterns
from grass.grassdb.create import create_mapset, get_default_mapset_name
from grass.grassdb.checks import mapset_exists, can_start_in_mapset

from grass.grassdb.checks import is_location_valid


def get_possible_database_path():
    """Looks for directory 'grassdata' (case-insensitive) in standard
    locations to detect existing GRASS Database.

    Returns the path as a string or None if nothing was found.
    """
    home = os.path.expanduser("~")

    # try some common directories for grassdata
    candidates = [
        home,
        os.path.join(home, "Documents"),
    ]

    # find possible database path
    for candidate in candidates:
        if os.path.exists(candidate):
            for subdir in next(os.walk(candidate))[1]:
                if "grassdata" in subdir.lower():
                    return os.path.join(candidate, subdir)
    return None


def create_database_directory():
    """Creates the standard GRASS GIS directory.
    Creates database directory named grassdata in the standard location
    according to the platform.

    Returns the new path as a string or None if nothing was found or created.
    """
    home = os.path.expanduser("~")

    # Determine the standard path according to the platform
    if sys.platform == "win32":
        path = os.path.join(home, "Documents", "grassdata")
    else:
        path = os.path.join(home, "grassdata")

    # Create "grassdata" directory
    try:
        os.mkdir(path)
        return path
    except OSError:
        pass

    # Create a temporary "grassdata" directory if GRASS is running
    # in some special environment and the standard directories
    # cannot be created which might be the case in some "try out GRASS"
    # use cases.
    path = os.path.join(tempfile.gettempdir(), "grassdata_{}".format(getpass.getuser()))

    # The created tmp is not cleaned by GRASS, so we are relying on
    # the system to do it at some point. The positive outcome is that
    # another GRASS instance will find the data created by the first
    # one which is desired in the "try out GRASS" use case we are
    # aiming towards."
    if os.path.exists(path):
        return path
    try:
        os.mkdir(path)
        return path
    except OSError:
        pass

    return None


def _get_startup_location_in_distribution():
    """Check for startup location directory in distribution.

    Returns startup location if found or None if nothing was found.
    """
    gisbase = os.getenv("GISBASE")
    startup_location = os.path.join(gisbase, "demolocation")

    # Find out if startup location exists
    if os.path.exists(startup_location):
        return startup_location
    return None


def _copy_startup_location(startup_location, location_in_grassdb):
    """Copy the simple startup_location with some data to GRASS database.

    Returns True if successfully copied or False
    when an error was encountered.
    """
    # Copy source startup location into GRASS database
    try:
        copytree(
            startup_location,
            location_in_grassdb,
            ignore=ignore_patterns("*.tmpl", "Makefile*"),
        )
        return True
    except (IOError, OSError):
        pass
    return False


def create_startup_location_in_grassdb(grassdatabase, startup_location_name):
    """Create a new startup location in the given GRASS database.

    Returns True if a new startup location successfully created
    in the given GRASS database.
    Returns False if there is no location to copy in the installation
    or copying failed.
    """
    # Find out if startup location exists
    startup_location = _get_startup_location_in_distribution()
    if not startup_location:
        return False

    # Copy the simple startup_location with some data to GRASS database
    location_in_grassdb = os.path.join(grassdatabase, startup_location_name)
    if _copy_startup_location(startup_location, location_in_grassdb):
        return True
    return False


def ensure_default_gisdbase(default_gisdbase=None):
    """Ensure that default gisdbase exists
    Creates database directory either based on default gisdbase obtained from
    gisrc file or on the default path determined according to OS.

    Returns the db"""

    if default_gisdbase:
        if not os.path.exists(default_gisdbase):
            try:
                os.mkdir(default_gisdbase)
                return default_gisdbase
            except OSError:
                pass
        return default_gisdbase
    else:
        default_gisdbase = get_possible_database_path()
        # If nothing found, try to create GRASS directory
        if not default_gisdbase:
            default_gisdbase = create_database_directory()
        return default_gisdbase


def ensure_default_location(default_gisdbase):
    """Ensure that default location exists
    Creates location if needed.

    Returns the db and location name.
    """

    default_location = "world_latlong_wgs84"
    if not is_location_valid(default_gisdbase, default_location):
        # If not valid, copy startup loc
        create_startup_location_in_grassdb(default_gisdbase, default_location)
    return default_location


def ensure_usable_mapset(grassdb, location):
    """Ensure that usable mapset exists

    Finds the usable mapset.
    It can create the new one named after user if needed.
    """
    mapset_name = "PERMANENT"
    mapset_path = os.path.join(grassdb, location, mapset_name)
    index = 1
    while not can_start_in_mapset(mapset_path, ignore_lock=False):
        if mapset_name == "PERMANENT":
            mapset_name = get_default_mapset_name()
        else:
            mapset_name = get_default_mapset_name() + "_" + str(index)
            index = index + 1
        if not mapset_exists(grassdb, location, mapset_name):
            create_mapset(grassdb, location, mapset_name)
        mapset_path = os.path.join(grassdb, location, mapset_name)
    return mapset_name
