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

"""
Common logging configuration utilities for mathmaker CLI and daemon.

configure_logging function cleans up any pre-existing handlers to avoid
inheriting broken `SysLogHandler` instances when a process is started
from a daemon / parent process.
"""

import logging
import sys
import platform
from pathlib import Path
from logging.handlers import RotatingFileHandler, SysLogHandler

from ruamel.yaml import YAML
from microlib import XDict

from mathmaker.core.env import safe_home


def load_config(entry_point: str) -> XDict:
    """Load configuration file"""

    loader = YAML(typ='safe', pure=True)
    config = XDict(loader.load(Path(__file__).parent.parent.parent
                               / f'settings/default/{entry_point}.yaml'))

    # Paths to check for configuration file
    config_paths = [
        Path(f'/etc/mathmaker/{entry_point}.yaml'),
        safe_home() / f'.config/mathmaker/{entry_point}.yaml',
    ]

    # Update config with user redefined settings, if any
    for config_path in config_paths:
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config.recursive_update(loader.load(f))
            except Exception as e:
                print(f'Error reading {config_path}: {e}')

    return config


def _clean_handlers(logger: logging.Logger):
    """Remove and close all existing handlers from a logger."""
    for handler in list(logger.handlers):
        try:
            handler.close()
        except Exception:
            pass
        logger.removeHandler(handler)


def _safe_mkdir(path: Path):
    try:
        path.mkdir(parents=True, exist_ok=True)
        return path
    except PermissionError:
        raise
    except Exception:
        # Any unexpected error -> re-raise to let caller decide
        raise


def configure_logging(entry_point: str):
    """
    Configure logging.
    """
    config = load_config(entry_point) or {}
    logging_config = config.get('logging', {})
    app_name = {'mmd': 'mathmakerd', 'cli': 'mathmaker'}[entry_point]

    # Determine log directory with same semantics as previous code
    log_dir0 = Path(logging_config.get('log_dir', f'/var/log/{app_name}'))
    try:
        log_dir0.mkdir(parents=True, exist_ok=True)
        log_dir = log_dir0
    except PermissionError:
        # fallback to user-local
        log_dir1 = safe_home() / f'.local/log/{app_name}'
        log_dir1.mkdir(parents=True, exist_ok=True)
        log_dir = log_dir1

    log_file = log_dir / f'{app_name}.log'

    log_level_name = logging_config.get('log_level', 'INFO')
    log_level = getattr(logging, log_level_name.upper(), logging.INFO)

    if entry_point == 'mmd':
        use_syslog = bool(logging_config.get('use_syslog', False))
    else:
        use_syslog = False

    logger = logging.getLogger()
    logger.setLevel(log_level)

    # Remove any existing handlers to avoid inheriting broken sockets
    _clean_handlers(logger)

    # Common formatter
    fmt = '%(asctime)s - %(name)s - %(levelname)s '\
        '- [%(filename)s:%(lineno)d] - %(message)s'
    formatter = logging.Formatter(fmt)

    # Rotating file handler
    try:
        fh = RotatingFileHandler(
            log_file,
            maxBytes=int(logging_config.get('max_bytes', 5)) * 1024 * 1024,
            backupCount=int(logging_config.get('backup_count', 3))
        )
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    except Exception as e:
        print(f"[logging] Failed to initialize file handler: {e}"
              f"fallback to basic logging config for {app_name}",
              file=sys.stderr)
        # fallback to basic config if file handler cannot be created
        logging.basicConfig(level=log_level, format=fmt)

    # Console handler (only if stderr available)
    log_to_console = logging_config.get('log_to_console', True)
    if log_to_console:
        try:
            if sys.stderr and sys.stderr.fileno() >= 0:
                ch = logging.StreamHandler(sys.stderr)
                ch.setFormatter(formatter)
                logger.addHandler(ch)
        except Exception:  # stderr closed/invalid (daemon mode), ignore
            pass

    # Syslog handler
    if use_syslog:
        facility_name = logging_config.get('syslog_facility', 'daemon').upper()
        facility = getattr(SysLogHandler, f'LOG_{facility_name}',
                           SysLogHandler.LOG_DAEMON)
        system = platform.system().lower()
        if system == 'linux':
            candidates = ['/dev/log', '/run/systemd/journal/dev-log']
        elif system == 'freebsd':
            candidates = ['/var/run/log']
        else:
            candidates = []

        address = None
        for c in candidates:
            try:
                if Path(c).exists():
                    address = c
                    break
            except Exception:
                # Path check failed (very unlikely) -> skip candidate
                continue

        # fallback to UDP localhost only if one really wants network syslog
        # as last resort
        if address is None:
            address = ('localhost', 514)

        try:
            sh = SysLogHandler(address=address, facility=facility)
            sh_fmt = '%(name)s[%(process)d]: %(levelname)s - %(message)s'
            sh.setFormatter(logging.Formatter(sh_fmt))
            logger.addHandler(sh)
            logger.info('Syslog enabled')
        except Exception as e:
            # If syslog is not available or the socket is invalid, keep going
            logger.warning(f'Cannot connect to syslog: {e}')

    settings = config.get('settings', {})
    return logger, log_dir, settings
