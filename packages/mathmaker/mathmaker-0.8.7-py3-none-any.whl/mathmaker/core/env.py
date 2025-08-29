# -*- coding: utf-8 -*-

# Mathmaker creates automatically maths exercises sheets
# with their answers
# Copyright 2006-2017 Nicolas Hainaux <nh.techn@gmail.com>

# This file is part of Mathmaker.

# Mathmaker is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# any later version.

# Mathmaker is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Mathmaker; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import os
import sys
import glob
import logging
import platform
from pathlib import Path

MATHMAKER_PATH = None
TEXLIVE_PATH = None
__myname__ = 'mathmaker'


def safe_home():
    """
    Return a usable ‘home’ path even if Path.home() or $HOME is invalid.
    Logs the decision steps.
    """
    logger = logging.getLogger(__name__)

    env_home = os.environ.get("HOME")
    path_home = Path.home()
    logger.debug(f"$HOME={env_home!r} ; Path.home()={str(path_home)!r}")

    # Usual case
    if path_home != Path("/") and path_home.exists():
        logger.debug(f"Using Path.home() : {path_home}")
        return path_home

    # Case of root with invalid home (or / as home)
    if os.geteuid() == 0:
        root_path = Path("/root")
        if root_path.exists():
            logger.warning(
                f"Invalid Path.home() ({path_home}) for root, "
                f"making use of {root_path}"
            )
            return root_path

    # Final fallback
    fallback = Path("/var/lib/mathmaker")
    if not fallback.exists():
        try:
            fallback.mkdir(parents=True, exist_ok=True)
            logger.warning(
                f"Create fallback directory {fallback} "
                f"because Path.home() is invalid ({path_home})"
            )
        except Exception as e:
            logger.error(f"Unable to create the fallback directory "
                         f"{fallback}: {e}")
    else:
        logger.warning(
            f"Making use of fallback directory {fallback} "
            f"because Path.home() is invalid ({path_home})"
        )

    return fallback


def load_search_paths():
    """
    Load search paths, starting with default ones in settings/default,
    possibly overwritten by the contents of /etc/mathmaker/mathmaker_paths.txt,
    then by the contents of ~/.config/mathmaker/mathmaker_paths.txt and
    finally by the dev settings.
    """
    logger = logging.getLogger('server')
    py_version = f"{sys.version_info.major}{sys.version_info.minor}"

    config_files = [
        Path(__file__).parent.parent / "settings/default/mathmaker_paths.txt",
        Path("/etc/mathmaker/mathmaker_paths.txt"),
        Path(safe_home()) / ".config/mathmaker/mathmaker_paths.txt",
        Path(__file__).parent.parent / "settings/dev/mathmaker_paths.txt",
    ]

    paths = []

    for config_file in config_files:
        if config_file.exists():
            logger.debug(f"Loading paths from {config_file}")
            try:
                with open(config_file, 'r') as f:
                    current_paths = []
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            path = line.replace('%%PY%%', py_version)
                            if path.startswith('~/'):
                                path = str(Path(safe_home()) / path[2:])
                            current_paths.append(path)

                    paths = current_paths
                    logger.debug(f"Loaded {len(paths)} paths "
                                 f"from {config_file}")

            except Exception as e:
                logger.warning(f"Error reading {config_file}: {e}")

    if not paths:
        logger.error("No valid path configuration found!")

    return paths


def find_mathmaker_script():
    """Find mathmaker script using the paths list."""
    logger = logging.getLogger('server')
    search_paths = load_search_paths()

    logger.debug(f"Searching mathmaker in {len(search_paths)} locations")

    for path in search_paths:
        path_obj = Path(path)
        logger.debug(f"Checking: {path}")

        if path_obj.exists() and path_obj.is_file():
            if os.access(path, os.X_OK):
                logger.info(f"Found mathmaker at: {path}")
                return str(path_obj)
            else:
                logger.warning(f"Found existing but not executable "
                               f"file: {path}")

    logger.error("mathmaker not found. Searched paths:")
    for i, path in enumerate(search_paths, 1):
        logger.error(f"  {i}. {path}")

    raise FileNotFoundError(f"mathmaker script not found in "
                            f"{len(search_paths)} locations")


def initialize_mathmaker_path():
    """Initialize and check mathmaker path at start"""
    global MATHMAKER_PATH
    logger = logging.getLogger('server')

    try:
        MATHMAKER_PATH = find_mathmaker_script()
        logger.info(f"Mathmaker initialized: {MATHMAKER_PATH}")
        return True
    except FileNotFoundError as e:
        logger.error(f"Failed to initialize mathmaker: {e}")
        logger.error("Daemon will not start without mathmaker available")
        return False


def get_mathmaker_path():
    """Get mathmaker path (after it has been initialized)"""
    if MATHMAKER_PATH is None:
        raise RuntimeError("Mathmaker not initialized. Call "
                           "initialize_mathmaker_path() first.")
    return MATHMAKER_PATH


def initialize_texlive_path():
    """
    Return TeXLive install directory.
    Remove any /skeleton prefix.
    """
    global TEXLIVE_PATH
    logger = logging.getLogger('server')
    candidates = glob.glob("/usr/local/texlive/*/bin")
    if not candidates:
        logger.error('Cannot find any /usr/local/texlive/*/bin directory.')
        return False
    path = os.path.dirname(sorted(candidates)[-1])
    if path.startswith('/skeleton'):
        path = path[len('/skeleton'):]
    TEXLIVE_PATH = path
    logger.info(f'TeXLive found at {TEXLIVE_PATH}')
    return True


def get_texlive_path():
    """Get TeXLive path (after it has been initialized)"""
    if TEXLIVE_PATH is None:
        raise RuntimeError("TeXLive path not initialized. Call "
                           "initialize_texlive_path() first.")
    return TEXLIVE_PATH


def find_tex_format(fmt_name="mm"):
    """
    Return full path to LaTeX .fmt file if found, otherwise None.
    """
    logger = logging.getLogger('env')
    fmt_file = f"{fmt_name}.fmt"

    # 1. user paths (XDG spec)
    user_paths = [
        safe_home() / ".local" / "share" / "mathmaker" / "latex",
    ]

    # 2. system paths
    system_paths = []
    system = platform.system().lower()
    if system == "freebsd":
        system_paths = [
            Path("/usr/local/share") / "mathmaker" / "latex",
            Path("/usr/share") / "mathmaker" / "latex",  # fallback
        ]
    elif system == "linux":
        system_paths = [
            Path("/usr/share") / "mathmaker" / "latex",
            Path("/usr/local/share") / "mathmaker" / "latex",
        ]
    else:
        logger.warning("Not implemented yet: look for ltx file on systems "
                       "other than FreeBSD and Linux.")

    search_paths = user_paths + system_paths

    for path in search_paths:
        candidate = path / fmt_file
        if candidate.is_file():
            return str(candidate)

    return None


USER_LOCAL_SHARE = os.path.join(str(safe_home()), '.local', 'share',
                                __myname__)
