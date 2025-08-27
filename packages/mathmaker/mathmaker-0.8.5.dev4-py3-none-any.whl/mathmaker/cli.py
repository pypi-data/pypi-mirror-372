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

# import time
# start_time = time.time()
import sys
import os
import json
import errno
import logging
import argparse
import traceback
import locale
from pathlib import Path
from json.decoder import JSONDecodeError

import mathmakerlib.config

from mathmaker import __info__, __software_name__
from mathmaker import settings
from mathmaker.lib import shared
from mathmaker.lib import old_style_sheet
from mathmaker.lib.document.frames import Sheet
from mathmaker.lib.tools import load_user_config
from mathmaker.lib.tools.ignition \
    import (install_gettext_translations,
            check_settings_consistency)
from mathmaker.lib.tools.frameworks import list_all_sheets, read_index
from mathmaker.lib.tools.xml import get_xml_sheets_paths
from mathmaker.core.env import safe_home


def _safe_fallback_write_traceback(fileobj):
    try:
        traceback.print_exc(file=fileobj)
        try:
            fileobj.flush()
        except Exception:
            pass
        return True
    except Exception:
        return False


def _fatal_report(exc_message: str = "Fatal error in entry_point",
                  settings_module=None,
                  fallback_path: str | Path | None = None) -> None:
    """
    Try to report an exception robustly:
    1) try settings_module.mainlogger.exception / root logger
    2) try sys.stderr if available
    3) try /dev/console or /dev/tty
    4) try fallback_path if provided and writable
    """
    # 1) prefer configured logger (settings.mainlogger) then root logger
    try:
        logger = None
        if settings_module is not None:
            try:
                logger = getattr(settings_module, "mainlogger", None)
            except Exception:
                logger = None
        if logger is None:
            logger = logging.getLogger()
        if logger:
            try:
                # Prefer exception() which logs stacktrace
                logger.exception(exc_message)
                return
            except Exception:
                # logger failed (handlers might raise).
                # swallow and try fallback
                try:
                    # last attempt: error with exc_info True
                    logger.error(exc_message
                                 + " (logger.exception failed)",
                                 exc_info=True)
                    return
                except Exception:
                    pass
    except Exception:
        pass

    # 2) try sys.stderr (only if it's a real fd)
    try:
        stderr = sys.stderr
        if hasattr(stderr, "fileno"):
            fd = stderr.fileno()
            # verify fd valid
            os.fstat(fd)
            if _safe_fallback_write_traceback(stderr):
                return
    except Exception:
        pass

    # 3) try console devices
    for dev in ("/dev/console", "/dev/tty", "/dev/tty0"):
        try:
            with open(dev, "w") as f:
                if _safe_fallback_write_traceback(f):
                    return
        except Exception:
            continue

    # 4) try a fallback file if provided or a sane default in home
    candidates = []
    if fallback_path:
        candidates.append(Path(fallback_path))
    # try /var/log (may need root), then user-local
    candidates.extend([Path("/var/log/mathmakerd/fallback-errors.log"),
                       safe_home() / ".local/log/mathmakerd/"
                       "fallback-errors.log",
                       Path.cwd() / "fallback-errors.log"])
    for p in candidates:
        try:
            p.parent.mkdir(parents=True, exist_ok=True)
            with open(p, "a") as f:
                if _safe_fallback_write_traceback(f):
                    return
        except Exception:
            continue

    # If everything fails, give up quietly
    # (we don't want to raise another exception)
    return


def entry_point():
    try:
        settings.init()
        mathmakerlib.config.polygons.DEFAULT_WINDING = 'clockwise'
        XML_SHEETS = get_xml_sheets_paths()
        YAML_SHEETS = read_index()
        log = settings.mainlogger
        # check_dependencies(xmllint=settings.xmllint,
        #                    lualatex=settings.lualatex,
        #                    luaotfload_tool=settings.luaotfload_tool)
        parser = argparse.ArgumentParser(
            description='Creates maths exercices sheets and their solutions.')
        parser.add_argument('-l', '--language', action='store', dest='lang',
                            default=settings.language,
                            help='force the language of the output to '
                                 'LANGUAGE. This will override any value you '
                                 'may have set in '
                                 '~/.config/mathmaker/user_config.yaml')
        parser.add_argument('--cotinga-template', action='store', dest='cot',
                            default='',
                            help='extra tex files will be produced as '
                                 'templates for use with Cotinga. The '
                                 'provided value will be used as name for the '
                                 'template(s). In conjunction with --shift, '
                                 'two templates will be produced.')
        parser.add_argument('--belts', action='store', dest='belts',
                            default=None,
                            help='belts names defined in the file whose path '
                                 'is provided will override the default ones.')
        parser.add_argument('--titles', action='store', dest='titles',
                            default=None,
                            help='sheet and answers titles defined in the '
                                 'file whose path is provided will override '
                                 'the default ones.')
        parser.add_argument('--pdf', action='store_true', dest='pdf_output',
                            help='the output will be in pdf format instead '
                                 'of LaTeX')
        parser.add_argument('-d', '--output-directory', action='store',
                            dest='outputdir',
                            default=settings.outputdir,
                            help='where to put the possible output files, '
                                 'like pictures. '
                                 'This will override any value you may have '
                                 'set ~/.config/mathmaker/user_config.yaml. '
                                 'Left undefined, the default will be current '
                                 'directory.')
        parser.add_argument('--shift', action='store_true',
                            dest='shift',
                            help='When this option is enabled, the mental '
                                 'calculation tabular will be created twice, '
                                 'with questions shifted by a random offset '
                                 'the second time. ')
        parser.add_argument('--interactive', action='store_true',
                            dest='enable_js_form',
                            help='When this option is enabled, the mental '
                                 'calculation tabular questions\' sheet will '
                                 'be added fields and buttons to enter '
                                 'answers and validate them. ')
        parser.add_argument('-f', '--font', action='store',
                            dest='font',
                            default=settings.font,
                            help='The font to use. If it\'s not installed on '
                                 'your system, lualatex will not be able '
                                 'to compile the document. '
                                 'This will override any value you may have '
                                 'set in ~/.config/mathmaker/user_config.yaml')
        parser.add_argument('--encoding', action='store',
                            dest='encoding',
                            default=settings.encoding,
                            help='The encoding to use. Take care it\'s '
                                 'available on your system, otherwise '
                                 'lualatex will not be able to compile '
                                 'the document. This will override any value '
                                 'you may have set in '
                                 '~/.config/mathmaker/user_config.yaml')
        parser.add_argument('main_directive', metavar='[DIRECTIVE|FILE]',
                            help='this can either match a sheetname included '
                                 'in mathmaker, or a mathmaker xml file, or '
                                 'it may be the special directives "list", '
                                 'that will print the complete list and exit; '
                                 '"config" that will show current mathmaker '
                                 'configuration values; or "belts" that will '
                                 'show currently loaded belts scale.')
        parser.add_argument('--version', '-v',
                            action='version',
                            version=__info__)
        args = parser.parse_args()
        install_gettext_translations(language=args.lang)
        # From now on, settings.language has its definitive value
        settings.outputdir = args.outputdir
        settings.font = args.font
        settings.encoding = args.encoding
        settings.locale = settings.language + '.' + settings.encoding \
            if not sys.platform.startswith('win') \
            else settings.language
        locale.setlocale(locale.LC_ALL, settings.locale)
        check_settings_consistency()
        shared.init()
        mathmakerlib.config.language = settings.language
        if args.belts:
            if Path(args.belts).is_file():
                try:
                    redefined_belts = json.loads(Path(args.belts).read_text())
                except JSONDecodeError:
                    raise RuntimeError(f'Provided file for belts names '
                                       f'({args.belts}) cannot be read as '
                                       'json (raised a JSONDecodeError)')
                settings.mc_belts.recursive_update(redefined_belts)
            else:
                raise FileNotFoundError(errno.ENOENT,
                                        os.strerror(errno.ENOENT),
                                        args.belts)
        if args.titles:
            if Path(args.titles).is_file():
                try:
                    redefined_titles = json.loads(
                        Path(args.titles).read_text())
                except JSONDecodeError:
                    raise RuntimeError(f'Provided file for titles '
                                       f'({args.titles}) cannot be read as '
                                       'json (raised a JSONDecodeError)')
                settings.mc_titles.recursive_update(redefined_titles)
            else:
                raise FileNotFoundError(errno.ENOENT,
                                        os.strerror(errno.ENOENT),
                                        args.belts)

        if args.main_directive == 'list':
            sys.stdout.write(list_all_sheets())
            shared.db.close()
            shared.natural_nb_tuples_db.close()
            shared.solids_db.close()
            shared.shapes_db.close()
            shared.anglessets_db.close()
            sys.exit(0)
        elif args.main_directive in ('config', 'belts'):
            if args.main_directive == 'config':
                print(json.dumps(load_user_config('user_config',
                                                  settings.settingsdir),
                                 indent=2))
            else:
                print(json.dumps(settings.mc_belts,
                                 indent=2))
            shared.db.close()
            shared.natural_nb_tuples_db.close()
            shared.solids_db.close()
            shared.shapes_db.close()
            shared.anglessets_db.close()
            sys.exit(0)
        elif args.main_directive in old_style_sheet.AVAILABLE:
            sh = old_style_sheet.AVAILABLE[args.main_directive][0]()
        else:
            build_from_yaml = False
            if args.main_directive in XML_SHEETS:
                fn = XML_SHEETS[args.main_directive]
            elif os.path.isfile(args.main_directive):
                fn = args.main_directive
            elif args.main_directive in YAML_SHEETS:
                fn = YAML_SHEETS[args.main_directive]
                build_from_yaml = True
            else:
                log.error(args.main_directive
                          + " is not a correct directive for "
                          f"{__software_name__}, you can run `mathmaker "
                          f"list` to get the complete list of directives.")
                # print("--- {sec} seconds ---"\
                #      .format(sec=round(time.time() - start_time, 3)))
                shared.db.close()
                shared.natural_nb_tuples_db.close()
                shared.solids_db.close()
                shared.shapes_db.close()
                shared.anglessets_db.close()
                sys.exit(1)
            if build_from_yaml:
                sh = Sheet(*fn, filename=None, shift=args.shift,
                           enable_js_form=args.enable_js_form, cot=args.cot)
            else:
                sh = Sheet('', '', '', filename=fn)

        shared.machine.write_out(str(sh), pdf_output=args.pdf_output)

    except Exception:
        _fatal_report("Fatal error in mathmaker", settings_module=settings,
                      fallback_path="/var/log/mathmakerd/fallback-errors.log")
        shared.natural_nb_tuples_db.close()
        shared.solids_db.close()
        shared.shapes_db.close()
        shared.anglessets_db.close()
        shared.db.close()
        sys.exit(1)

    shared.db.commit()
    shared.db.close()
    shared.natural_nb_tuples_db.commit()
    shared.natural_nb_tuples_db.close()
    shared.solids_db.commit()
    shared.solids_db.close()
    shared.shapes_db.commit()
    shared.shapes_db.close()
    shared.anglessets_db.commit()
    shared.anglessets_db.close()
    log.info("Done.")
    sys.exit(0)


if __name__ == '__main__':
    entry_point()
    # print("--- {sec} seconds ---".format(sec=time.time() - start_time))
