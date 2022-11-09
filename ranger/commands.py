from __future__ import (absolute_import, division, print_function)
import os
import subprocess
import json
import atexit
import socket
import logging
import traceback

from pathlib import Path
from ranger.api.commands import Command
from ranger.ext.img_display import ImageDisplayer, register_image_displayer

logger = logging.getLogger(__name__)

class set_as_wallpaper(Command):
    """:set_as_wallpaper <filename>

    Sets image as a wallpaper using 'feh'.
    """
    def execute(self):
        if self.arg(1):
            target_filename = self.rest(1)
        else:
            target_filename = self.fm.thisfile.path

        self.fm.notify("Setting " + target_filename + " as wallpaper!")

        if not os.path.exists(target_filename):
            self.fm.notify("The given file does not exist!", bad=True)
            return

        self.fm.run("feh --bg-fill " + target_filename)

class dye(Command):
    """:dye <palette>

    Make image's copy that matches given color palette
    """
    def execute(self):
        target_filename = self.fm.thisfile.path
        target_palette = self.rest(1) if self.arg(1) else "catpuccin"

        self.fm.notify("Dying " + target_filename + " to match " + target_palette + " palette!")

        if not os.path.exists(target_filename):
            self.fm.notify("The given file does not exist!", bad=True)
            return

        p = Path(target_filename)
        new_filename = "{}/{}_{}".format(p.parent, p.stem, target_palette)

        self.fm.run("dye " + target_filename + " -p " + target_palette + " -o " + new_filename + " -b")

class convert(Command):
    """:convert <ext>

    Convert image using imagick's convert.
    """
    def execute(self):
        target_filename = self.fm.thisfile.path
        target_ext = self.rest(1) if self.arg(1) else "png"

        self.fm.notify("Converting " + target_filename + " to " + target_ext + "!")

        if not os.path.exists(target_filename):
            self.fm.notify("The given file does not exist!", bad=True)
            return

        p = Path(target_filename)
        new_filename = "{}/{}.{}".format(p.parent, p.stem, target_ext)

        self.fm.run("convert " + target_filename + " " + new_filename)

