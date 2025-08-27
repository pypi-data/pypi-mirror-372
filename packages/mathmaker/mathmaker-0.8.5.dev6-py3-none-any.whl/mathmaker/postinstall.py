# -*- coding: utf-8 -*-

# Copyright 2006-2017 Nicolas Hainaux <nh.techn@gmail.com>

# This file is part of Mathmaker.

# Mathmaker is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.

# Mathmaker is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Mathmaker; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import os
import sys
import platform
import subprocess
from pathlib import Path


def entry_point():
    print('[mm_postinstall] Starting post-install script...')
    font_source = Path(__file__).parent / 'data/lcmmi8mod.otf'

    if not font_source.exists():
        print(f'[mm_postinstall] ERROR: font file not found at {font_source}')
        sys.exit(1)

    system = platform.system().lower()
    is_root = os.geteuid() == 0
    user_fonts = Path.home() / '.local/share/fonts'

    if system == 'freebsd':
        base_dir = Path('/usr/local/share/fonts') if is_root else user_fonts
    elif system == 'linux':
        base_dir = Path('/usr/share/fonts') if is_root else user_fonts
    else:
        print(f'[mm_postinstall] WARNING: Unsupported platform: {system}, '
              'skipping font installation.')
        return

    target_dir = base_dir / 'mathmaker'
    target_dir.mkdir(parents=True, exist_ok=True)

    target_file = target_dir / font_source.name

    print(f'[mm_postinstall] Installing font to {target_file}')
    try:
        data = font_source.read_bytes()
        target_file.write_bytes(data)
    except Exception as e:
        print(f'[mm_postinstall] ERROR: Could not install font: {e}')
        sys.exit(1)

    try:
        print(f'[mm_postinstall] Updating font cache for {target_dir}')
        subprocess.run(
            ['fc-cache', '-f', str(target_dir)],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except FileNotFoundError:
        print('[mm_postinstall] WARNING: fc-cache not found, font cache not '
              'updated.')
    except subprocess.CalledProcessError as e:
        print(f'[mm_postinstall] WARNING: fc-cache failed: '
              f'{e.stderr.decode().strip()}')
    else:
        print('[mm_postinstall] Font installation completed successfully.')

    if platform.system().lower() != 'freebsd':
        print('[mm_postinstall] Skipped: Not running on FreeBSD.')
        return

    if os.geteuid() != 0:
        print('[mm_postinstall] Error: Must be run as root to install '
              'rc.d script.')
        return

    pyver_nodot = f'{sys.version_info.major}{sys.version_info.minor}'

    template_path = Path(__file__).parent / 'settings/default/mathmakerd.in'
    if not template_path.exists():
        print(f'[mm_postinstall] Error: Template not found at {template_path}')
        return

    try:
        content = template_path.read_text()
        content = content.replace("%%PYVER_NODOT%%", pyver_nodot)
    except Exception as e:
        print(f'[mm_postinstall] Error while reading or preparing '
              f'template: {e}')
        return

    rc_target = Path('/usr/local/etc/rc.d/mathmakerd')

    try:
        rc_target.write_text(content)
        rc_target.chmod(0o755)
        print(f'[mm_postinstall] rc.d script successfully installed '
              f'at {rc_target}')
    except Exception as e:
        print(f'[mm_postinstall] Error writing to {rc_target}: {e}')
