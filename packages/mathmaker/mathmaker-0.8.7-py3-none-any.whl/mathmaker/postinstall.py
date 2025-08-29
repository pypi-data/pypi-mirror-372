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
import shutil
import platform
import subprocess
from pathlib import Path

from mathmaker.core.env import safe_home


def get_latex_output_dir():
    """Determine output directory based on platform and user privileges."""
    is_root = os.geteuid() == 0  # Unix/Linux way to check root

    system = platform.system().lower()
    if is_root:
        if system == "freebsd":
            return Path("/usr/local/share/mathmaker/latex")
        elif system == "linux":
            return Path("/usr/share/mathmaker/latex")

    # Non-root user or unsupported system
    return safe_home() / ".local" / "share" / "mathmaker" / "latex"


def generate_latex_format(ltx_source: Path):
    """Generate LaTeX format file from .ltx source."""

    # Check if lualatex is available
    if not shutil.which("lualatex"):
        print("lualatex not found in PATH - skipping format generation")
        return False

    # Determine output directory
    output_dir = get_latex_output_dir()
    print(f"LaTeX output directory: {output_dir}")

    # Create output directory if needed
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        print(f"Permission denied creating {output_dir}")
        return False
    except Exception as e:
        print(f"Failed to create output directory {output_dir}: {e}")
        return False

    # Generate format file
    # Note: -jobname not needed, will use the .ltx filename by default
    cmd = ["lualatex", "-ini", f"-output-directory={output_dir}",
           str(ltx_source)]

    print(f"Generating LaTeX format: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True,
                                timeout=300)

        if result.returncode == 0:
            # Check if .fmt file was created
            fmt_name = ltx_source.stem  # 'mm' from 'mm.ltx'
            fmt_file = output_dir / f"{fmt_name}.fmt"
            if fmt_file.is_file():
                print(f"Successfully generated {fmt_file}")
                return True
            else:
                print("lualatex succeeded but .fmt file not found")
                return False
        else:
            print(
                f"lualatex failed with return code {result.returncode}")
            if result.stderr:
                print(f"Error output: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print("lualatex command timed out")
        return False
    except Exception as e:
        print(f"Error executing lualatex: {e}")
        return False


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

    # ltx_source = Path(__file__).parent / 'data/mm.ltx'
    # # lualatex -ini -jobname=myformat myformat.ltx
    # if ltx_source.exists():
    #     generate_latex_format(ltx_source)
    # else:
    #     print(f"LaTeX source file not found: {ltx_source}")

    if platform.system().lower() != 'freebsd':
        print('[mm_postinstall] Install rc.d script: skipped: not running '
              'on FreeBSD.')
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
