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

@register_image_displayer("mpv")
class MPVImageDisplayer(ImageDisplayer):
    """Implementation of ImageDisplayer using mpv, a general media viewer.
    Opens media in a separate X window.

    mpv 0.25+ needs to be installed for this to work.
    """

    def _send_command(self, path, sock):

        message = '{"command": ["raw","loadfile",%s]}\n' % json.dumps(path)
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.connect(str(sock))
        logger.info('-> ' + message)
        s.send(message.encode())
        message = s.recv(1024).decode()
        logger.info('<- ' + message)

    def _launch_mpv(self, path, sock):

        proc = subprocess.Popen([
            * os.environ.get("MPV", "mpv").split(),
            "--no-terminal",
            "--force-window",
            "--input-ipc-server=" + str(sock),
            "--image-display-duration=inf",
            "--loop-file=inf",
            "--no-osc",
            "--no-input-default-bindings",
            "--keep-open",
            "--idle",
            "--",
            path,
        ])

        @atexit.register
        def cleanup():
            proc.terminate()
            sock.unlink()

    def draw(self, path, start_x, start_y, width, height):

        path = os.path.abspath(path)
        cache = Path(os.environ.get("XDG_CACHE_HOME", "~/.cache")).expanduser()
        cache = cache / "ranger"
        cache.mkdir(exist_ok=True)
        sock = cache / "mpv.sock"

        try:
            self._send_command(path, sock)
        except (ConnectionRefusedError, FileNotFoundError):
            logger.info('LAUNCHING ' + path)
            self._launch_mpv(path, sock)
        except Exception as e:
            logger.exception(traceback.format_exc())
            sys.exit(1)
        logger.info('SUCCESS')

