"""Extract titles from a DVD title set into their own video files, copying streams with no transcoding.

Usage:
    %(name)s --fast [--script] [--out=<out>] <path>
    %(name)s [--out=<out>] [--tmp=<tmp>] [--debug] <path>

Options:
    -h --help    Display help.
    --fast       Enables fast mode, no extra processing, no creation of temporary files, just get the titles from the
                 title(s). Chapters markers will be inaccurate the further into the video they are. Audio, video, and
                 subtitle streams may be in random orders per program.
    --script     Output scripts instead of running the commands directly. Only available with --fast.
    --out=<out>  Output path, must be a directory. Defaults to the current directory.
    --tmp=<tmp?  Directory to store temporary files in. Defaults to the output path.
    --debug      Keep temp directory and files.
    <path>       If the path is a directory with a DVD backup, extract all titles from all title sets.
                 If the path is a single VTS_*_0.IFO file, extract titles from just that title set.
"""

import contextlib
import enum
import more_itertools
import json
import os
import pathlib
import re
import shlex
import shutil
import subprocess
import tempfile
import textwrap
import sys

import attrs
import docopt

import dvd
from dvd.ifo import vts


class CommandException(Exception):
    """Thrown when a command fails and causes a fatal error."""


class Mode(enum.StrEnum):
    """Script mode."""

    Fast = enum.auto()
    FastScript = enum.auto()
    Full = enum.auto()


VTS_IFO_RE = re.compile(r"VTS_(\d\d)_0\.IFO")
READ_SIZE = 100 * 1024 * dvd.SECTOR_SIZE


@attrs.define
class Chapter:
    """Chapter metadata."""

    name: str
    length_ms: float


@attrs.define
class ProgramExtracter:
    """."""

    ifo_path: pathlib.Path = attrs.field()
    output_path: pathlib.Path = attrs.field()
    tmp_path: pathlib.Path = attrs.field()

    _title_set_num: str = attrs.field(init=False)
    _vobs: list[pathlib.Path] = attrs.field(init=False)
    _ifo: vts.VTS_IFO = attrs.field(init=False)
    _aspect_width: int = attrs.field(init=False)
    _aspect_height: int = attrs.field(init=False)

    def process(self) -> None:
        """Process an IFO."""
        match = VTS_IFO_RE.match(self.ifo_path.name)
        assert match is not None
        print(f"Processing {self.ifo_path}")
        self._title_set_num = match.group(1)
        vob_path = self.ifo_path.parent
        vob_glob = f"VTS_{self._title_set_num}_*.VOB"
        self._vobs = sorted(vob_path.glob(vob_glob))
        if len(self._vobs) == 0:
            raise Exception(f"{vob_glob!r} files not found in {str(vob_path)!r}")
        with open(self.ifo_path, "rb") as infile:
            self._ifo = vts.VTS_IFO.from_bytes(infile)
        self._aspect_width = int(
            self._ifo.vts_vobs_video_attrs.resolution.resolution[1]
            * self._ifo.vts_vobs_video_attrs.aspect.aspect
        )
        self._aspect_height = self._ifo.vts_vobs_video_attrs.resolution.resolution[1]
        self._process()

    def _process(self):
        for title_num, title in enumerate(self._ifo.get_titles()):
            self.process_title(title_num, title)

    def process_title(self, title_num: int, title: vts.Title) -> None:
        """Process a title from the title set."""
        raise NotImplementedError()

    def write_chapter_metadata(self, file_path: pathlib.Path, chapters: list[Chapter]) -> None:
        """Write chapter metadata file for ffmpeg."""
        with open(file_path, "w") as outfile:
            outfile.write(";FFMETADATA1\n\n")
            current_time = 0.0
            for chapter in chapters:
                end_time = chapter.length_ms + current_time
                outfile.write(
                    textwrap.dedent(
                        f"""
                        [CHAPTER]
                        TIMEBASE=1/1000
                        START={round(current_time)}
                        END={round(end_time)}
                        title={chapter.name}
                        """
                    )
                )
                current_time = end_time


@attrs.define
class FastProgramExtracter(ProgramExtracter):
    """."""

    script: bool = attrs.field()

    _script_file = attrs.field(init=False)
    _ffmpeg_path: str = attrs.field(init=False)

    def _process(self) -> None:
        if self.script:
            with open(
                self.output_path / f"extract_title_{self._title_set_num}.sh", "w"
            ) as self._script_file:
                os.chmod(self._script_file.fileno(), 0o755)
                self._script_file.write("#!/bin/bash -ex\n")
                super()._process()
        else:
            ffmpeg_path = shutil.which("ffmpeg")
            assert ffmpeg_path is not None, "ffmpeg executable not found, check your PATH"
            self._ffmpeg_path = ffmpeg_path
            super()._process()

    def process_title(self, title_num: int, title: vts.Title) -> None:
        """Process a title from the title set."""
        chapters = []
        for chapter_num, chapter in enumerate(title.chapters):
            chapters.append(Chapter(f"Chapter {chapter_num}", chapter.playback_time_as_millis))
        chapter_meta_file_path = (
            self.tmp_path / f"ts{self._title_set_num}t{title_num}_chapter_metadata.txt"
        )
        self.write_chapter_metadata(chapter_meta_file_path, chapters)
        title_path = str(
            self.output_path / f"Title Set {self._title_set_num} Title {title_num:02d}.mkv"
        )
        if self.script:
            num_sectors = (
                title.last_cell.playback_info.last_vobu_end_sector
                - title.first_cell.playback_info.first_vobu_start_sector
                + 1
            )
            self._script_file.write(
                f"cat {shlex.quote(str(self.ifo_path.parent))}/VTS_{self._title_set_num}_*.VOB"
                f" | dd ibs={dvd.SECTOR_SIZE} iflag=fullblock"
                f" skip={title.first_cell.playback_info.first_vobu_start_sector + self._ifo.title_vob_start_sector}"
                f" count={num_sectors}"
                f" | ffmpeg -v error -fflags +genpts -y -i pipe: -i {shlex.quote(str(chapter_meta_file_path))}"
                f" -map_chapters 1 -aspect {self._aspect_width}:{self._aspect_height}"
                " -map '0:v?' -map '0:a?' -map '0:s?' -c:v copy -c:a copy -c:s copy"
                f" {shlex.quote(title_path)}"
                "\n"
                f"rm {shlex.quote(str(chapter_meta_file_path))}\n"
            )
            return
        print(f"Writing program output to {title_path}")
        ffmpeg_cmd = [
            self._ffmpeg_path,
            "-v",
            "error",
            "-fflags",
            "+genpts",
            "-y",
            "-i",
            "pipe:",
            "-i",
            str(chapter_meta_file_path),
            "-map_chapters",
            "1",
            "-aspect",
            f"{self._aspect_width}:{self._aspect_height}",
            "-map",
            "0:v?",
            "-map",
            "0:a?",
            "-map",
            "0:s?",
            "-c:v",
            "copy",
            "-c:a",
            "copy",
            "-c:s",
            "copy",
            title_path,
        ]
        with subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE) as ffmpeg:
            assert ffmpeg.stdin is not None
            current_position = 0
            start_position = (
                title.first_cell.playback_info.first_vobu_start_sector
                + self._ifo.title_vob_start_sector
            ) * dvd.SECTOR_SIZE
            end_position = (
                title.last_cell.playback_info.last_vobu_end_sector
                + self._ifo.title_vob_start_sector
                + 1
            ) * dvd.SECTOR_SIZE
            for vob_path in self._vobs:
                vob_file_info = os.stat(vob_path)
                if current_position + vob_file_info.st_size < start_position:
                    current_position += vob_file_info.st_size
                    print(f"Skipping {vob_path}")
                    continue
                print(f"Reading {vob_path}")
                with open(vob_path, "rb", buffering=dvd.SECTOR_SIZE) as vob_file:
                    if current_position < start_position:
                        vob_file.seek(start_position - current_position)
                        current_position = start_position
                    while True:
                        chunk = vob_file.read(dvd.SECTOR_SIZE)
                        if not chunk:
                            break
                        ffmpeg.stdin.write(chunk)
                        current_position += len(chunk)
                        if current_position >= end_position:
                            break
                if current_position >= end_position:
                    break
        if ffmpeg.returncode != 0:
            raise CommandException(f"FFMPeg failed with exit code {ffmpeg.returncode}")
        print("Done")
        os.unlink(chapter_meta_file_path)


@attrs.define
class FullProgramExtracter(ProgramExtracter):
    """."""

    debug: bool = attrs.field(default=False)

    _ffmpeg_path: str = attrs.field(init=False)
    _ffprobe_path: str = attrs.field(init=False)
    _tmp_dir: pathlib.Path = attrs.field(init=False)
    _full_vob_path: pathlib.Path = attrs.field(init=False)

    def _process(self) -> None:
        """."""
        ffmpeg_path = shutil.which("ffmpeg")
        ffprobe_path = shutil.which("ffprobe")
        assert ffmpeg_path is not None, "ffmpeg executable not found, check your PATH"
        assert ffprobe_path is not None, "ffprobe executable not found, check your PATH"
        self._ffmpeg_path = ffmpeg_path
        self._ffprobe_path = ffprobe_path
        with tempfile.TemporaryDirectory(dir=self.tmp_path, delete=not self.debug) as tmp_dir:
            if self.debug:
                print(f"Temp directory is {tmp_dir}, script will not automatically delete it.")
            self._tmp_dir = pathlib.Path(tmp_dir)
            self._full_vob_path = self._tmp_dir / f"VTS_{self._title_set_num}.VOB"
            print(f"Writing full size VOB {self._full_vob_path}")

            current_position = 0
            start_position = self._ifo.title_vob_start_sector * dvd.SECTOR_SIZE
            with open(self._full_vob_path, "wb") as full_vob:
                for vob_path in self._vobs:
                    vob_file_info = os.stat(vob_path)
                    if current_position + vob_file_info.st_size < start_position:
                        current_position += vob_file_info.st_size
                        print(f"Skipping {vob_path}")
                        continue
                    print(f"Reading {vob_path}")
                    with open(vob_path, "rb", buffering=dvd.SECTOR_SIZE) as vob_file:
                        if current_position < start_position:
                            vob_file.seek(start_position - current_position)
                            current_position = start_position
                        while True:
                            chunk = vob_file.read(READ_SIZE)
                            if not chunk:
                                break
                            full_vob.write(chunk)
                            current_position += len(chunk)
            super()._process()

    def process_title(self, title_num: int, title: vts.Title) -> None:
        """Process a title from the title set."""
        chapters = []
        program_cut_vob_path = self._tmp_dir / f"ts{self._title_set_num}t{title_num}_cut.vob"
        program_pre_mkv_path = self._tmp_dir / f"ts{self._title_set_num}t{title_num}_pre.mkv"
        with (
            open(self._full_vob_path, "rb", buffering=dvd.SECTOR_SIZE) as full_vob,
            open(program_cut_vob_path, "wb") as program_cut_vob,
        ):
            start = title.first_cell.playback_info.first_vobu_start_sector * dvd.SECTOR_SIZE
            pre_program_duration = 0.0
            pre_ffmpeg: subprocess.Popen | None = None
            if start != 0:
                pre_ffmpeg = subprocess.Popen(
                    [
                        self._ffmpeg_path,
                        "-v",
                        "error",
                        "-y",
                        "-fflags",
                        "+genpts",
                        "-i",
                        "pipe:",
                        "-map",
                        "0:v?",
                        "-c:v",
                        "copy",
                        "-c:a",
                        "copy",
                        "-c:s",
                        "copy",
                        program_pre_mkv_path,
                    ],
                    stdin=subprocess.PIPE,
                )
            with pre_ffmpeg if pre_ffmpeg is not None else contextlib.nullcontext():
                while full_vob.tell() < start:
                    chunk = full_vob.read(min(start - full_vob.tell(), READ_SIZE))
                    program_cut_vob.write(chunk)
                    if pre_ffmpeg is not None:
                        assert pre_ffmpeg.stdin is not None
                        pre_ffmpeg.stdin.write(chunk)
            if pre_ffmpeg is not None:
                if pre_ffmpeg.returncode != 0:
                    raise CommandException(
                        f"ffmpeg command failed to process pre-title video with returncode {pre_ffmpeg.returncode}"
                        f" for title {title_num}"
                    )
                print("Probing pre-program skip")
                ffprobe = subprocess.Popen(
                    [
                        self._ffprobe_path,
                        "-v",
                        "error",
                        "-show_entries",
                        "format=duration",
                        "-output_format",
                        "json",
                        "-i",
                        program_pre_mkv_path,
                    ],
                    stdout=subprocess.PIPE,
                )
                (probe_out, _) = ffprobe.communicate()
                pre_program_duration = float(json.loads(probe_out.decode())["format"]["duration"])
                print(f"Probed pre-program skip: {pre_program_duration}s")

            assert all(
                a.playback_info.last_vobu_end_sector == b.playback_info.first_vobu_start_sector - 1
                for (a, b) in more_itertools.pairwise(
                    cell
                    for chapter in title.chapters
                    for program in chapter.programs
                    for cell in program.cells
                )
            ), f"All cells in title {title_num} are not contiguous"

            for chapter_num, chapter in enumerate(title.chapters):
                print(f"Processing chapter {chapter_num}")
                start = chapter.first_cell.playback_info.first_vobu_start_sector * dvd.SECTOR_SIZE
                end = (chapter.last_cell.playback_info.last_vobu_end_sector + 1) * dvd.SECTOR_SIZE
                assert start < end
                chapter_path = (
                    self._tmp_dir / f"ts{self._title_set_num}t{title_num}c{chapter_num}.mkv"
                )
                ffmpeg = subprocess.Popen(
                    [
                        self._ffmpeg_path,
                        "-v",
                        "error",
                        "-y",
                        "-fflags",
                        "+genpts",
                        "-i",
                        "pipe:",
                        "-map",
                        "0:v?",
                        "-map",
                        "0:a?",
                        "-map",
                        "0:s?",
                        "-c:v",
                        "copy",
                        "-c:a",
                        "copy",
                        "-c:s",
                        "copy",
                        chapter_path,
                    ],
                    stdin=subprocess.PIPE,
                )
                assert ffmpeg.stdin is not None
                assert full_vob.tell() == start, f"{full_vob.tell()} != {start}"
                while full_vob.tell() < end:
                    size = min(READ_SIZE, end - full_vob.tell())
                    chunk = full_vob.read(size)
                    if not chunk:
                        print(f"Breaking at {full_vob.tell()} < {end}")
                        break
                    ffmpeg.stdin.write(chunk)
                    program_cut_vob.write(chunk)
                ffmpeg.stdin.close()
                ffmpeg.wait()
                if ffmpeg.returncode == 0:
                    print("ffmpeg done")
                    ffprobe = subprocess.Popen(
                        [
                            self._ffprobe_path,
                            "-v",
                            "error",
                            "-show_entries",
                            "format=duration",
                            "-output_format",
                            "json",
                            "-i",
                            chapter_path,
                        ],
                        stdout=subprocess.PIPE,
                    )
                    (probe_out, _) = ffprobe.communicate()
                    if ffprobe.returncode == 0:
                        cell_duration = float(json.loads(probe_out.decode())["format"]["duration"])
                        ifo_time = chapter.playback_time_as_millis / 1000
                        print(
                            f"Probed duration {cell_duration}s,"
                            f" IFO playback time {ifo_time}s,"
                            f" discrepancy {cell_duration - ifo_time}s"
                        )
                        # chapters.append(Chapter(f"Chapter {chapter_num}", cell_duration * 1000))
                        chapters.append(
                            Chapter(
                                f"Chapter {chapter_num}",
                                (chapter.playback_time_as_millis + cell_duration * 1000) / 2,
                            )
                        )
                    else:
                        print("Failed to probe chapter length, using IFO time")
                        chapters.append(
                            Chapter(f"Chapter {chapter_num}", chapter.playback_time_as_millis)
                        )
                else:
                    print("Chapter failed to convert, using IFO time")
                    chapters.append(
                        Chapter(f"Chapter {chapter_num}", chapter.playback_time_as_millis)
                    )
                if not self.debug:
                    os.unlink(chapter_path)
        chapter_meta_file_path = (
            self._tmp_dir / f"ts{self._title_set_num}t{title_num}_chapter_metadata.txt"
        )
        self.write_chapter_metadata(chapter_meta_file_path, chapters)
        program_path = str(
            self.output_path / f"Title Set {self._title_set_num} Title {title_num:02d}.mkv"
        )
        print(f"Writing program output to {program_path}")
        ffmpeg_cmd = [
            self._ffmpeg_path,
            # "-v",
            # "error",
            "-fflags",
            "+genpts",
            "-y",
            "-ss",
            f"{pre_program_duration}s",
            "-i",
            str(program_cut_vob_path),
            "-i",
            str(chapter_meta_file_path),
            "-map_chapters",
            "1",
            "-aspect",
            f"{self._aspect_width}:{self._aspect_height}",
            "-map",
            "0:v?",
            "-map",
            "0:a?",
            "-map",
            "0:s?",
            "-c:v",
            "copy",
            "-c:a",
            "copy",
            "-c:s",
            "copy",
            program_path,
        ]
        import shlex

        print(f"Running {' '.join(shlex.quote(x) for x in ffmpeg_cmd)}")
        ffmpeg = subprocess.Popen(ffmpeg_cmd)
        ffmpeg.wait()
        print("Done")
        # sys.exit(1)
        if not self.debug:
            os.unlink(program_cut_vob_path)
            os.unlink(chapter_meta_file_path)


def process_ifo(
    ifo_path: pathlib.Path,
    output_path: pathlib.Path,
    tmp_path: pathlib.Path,
    mode: Mode,
    debug: bool = False,
) -> None:
    """Extract titles from title set."""
    if mode == Mode.Full:
        FullProgramExtracter(ifo_path, output_path, tmp_path, debug).process()
    else:
        FastProgramExtracter(ifo_path, output_path, tmp_path, mode is Mode.FastScript).process()


def main() -> None:
    """Run script."""
    args = docopt.docopt(str(__doc__) % {"name": os.path.basename(__file__)})
    input_path = pathlib.Path(os.path.realpath(args["<path>"]))
    output_path = pathlib.Path(os.path.realpath(args["--out"] or os.getcwd()))
    tmp_path = pathlib.Path(os.path.realpath(args["--tmp"] or output_path))
    fast = bool(args["--fast"])
    script = bool(args["--script"])
    debug = bool(args["--debug"])
    if script and not fast:
        print("Script output requires fast mode.", file=sys.stdout)
        sys.exit(1)
    mode = Mode.FastScript if fast and script else Mode.Fast if fast else Mode.Full
    if not output_path.is_dir():
        print("Output path must be a directory.")
        sys.exit(1)
    if not input_path.exists():
        print("Input path does not exist.", file=sys.stderr)
        sys.exit(1)
    if input_path.is_dir():
        if len(list(input_path.glob("VTS_*_0.IFO"))) == 0:
            if (input_path / "VIDEO_TS").is_dir():
                input_path = input_path / "VIDEO_TS"
            if not input_path.glob("VTS_*_0.IFO"):
                print("No VTS IFO files found.", file=sys.stderr)
                sys.exit(1)
        for ifo_path in input_path.glob("VTS_*_0.IFO"):
            process_ifo(ifo_path, output_path, tmp_path, mode)
        return
    if VTS_IFO_RE.match(input_path.name) is None:
        print(
            f"Input path {str(input_path)!r} is not in the format VTS_<NN>_0.IFO.", file=sys.stderr
        )
        sys.exit(1)
    process_ifo(input_path, output_path, tmp_path, mode, debug)


if __name__ == "__main__":
    main()
