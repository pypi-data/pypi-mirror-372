import fractions
import json
import os
import pathlib
import shlex
import subprocess
import textwrap

import ffmpeg
import pyparsedvd

source_path = pathlib.Path("/mnt/video/DVD/backup/Gravity Falls")
for disc_path in source_path.glob("*"):
    if not disc_path.is_dir():
        continue
    disc = disc_path.name
    # disc = "Gravity Falls S3 Bonus Disc"
    path = disc_path / "VIDEO_TS"  # f"/mnt/video/DVD/backup/Gravity Falls/{disc}/VIDEO_TS"

    ifos = path.glob("VTS_*.IFO")

    cmds = []
    out_path = pathlib.Path("/mnt/video/DVD/Gravity Falls") / disc
    if not os.path.exists(out_path):
        os.mkdir(out_path)
    # tmp_path = pathlib.Path("/run/user/1000")
    tmp_path = out_path / "tmp"
    if not os.path.exists(tmp_path):
        os.mkdir(tmp_path)

    for ifo_path in ifos:
        print(ifo_path)
        title_num = ifo_path.name.split("_")[1]
        with open(ifo_path, "rb") as ifo_file:
            vts_pgci = pyparsedvd.load_vts_pgci(ifo_file)

        cat = f"cat {shlex.quote(f'{path}/VTS_{title_num}_')}*.VOB"

        combined_vob_fn = tmp_path / f"COMBINED_VTS_{title_num}.VOB"
        cat_combined = f"{cat} > {shlex.quote(str(combined_vob_fn))}"
        print(cat_combined)
        proc = subprocess.run(
            cat_combined,
            shell=True,
            check=True,
            # stderr=subprocess.STDOUT,
        )

        for p, chain in enumerate(vts_pgci.program_chains):
            print(f"Title {title_num} program chain {p}")

            last = None
            current_time = 0
            # current_frames = 0
            chapter_metadata = []

            if fractions.Fraction(*vts_pgci.video_attrs.resolution.value) != fractions.Fraction(
                *vts_pgci.video_attrs.aspect.value
            ):
                print(
                    f"Resolution {vts_pgci.video_attrs.resolution.value} does not match aspect ratio {vts_pgci.video_attrs.aspect.value}, attemping to correct with display ratio."
                )
                aspect = f"-aspect {int(vts_pgci.video_attrs.resolution.value[1] * fractions.Fraction(*vts_pgci.video_attrs.aspect.value))}:{vts_pgci.video_attrs.resolution.value[1]}"
            else:
                aspect = ""

            # cell_files = []
            extra_time = 0
            for i, cell in enumerate(chain.cells):
                # print(cell.last_vobu_end_sector - cell.first_vobu_start_sector + 1)
                if last is not None:
                    assert (
                        cell.first_vobu_start_sector == last.last_vobu_end_sector + 1
                    ), f"{last} {cell}"

                dd = f"dd ibs=2048 iflag=fullblock skip={cell.first_vobu_start_sector} count={cell.last_vobu_end_sector - cell.first_vobu_start_sector + 1}"

                # ffprobe = f"{cat} | {dd} | ffprobe -v error -select_streams v:0 -count_frames -show_entries stream=nb_read_frames -output_format json -i -"
                # ffprobe = f"{cat} | {dd} | ffprobe -v error -select_streams v:0 -count_packets -show_entries stream=nb_read_packets -output_format json -i -"

                # cell_mkv_fn = (
                #     out_path / f"Title {title_num} Program Chain {p:02d} Cell {i}.mkv"
                # )
                # meta_fn = out_path / f"Title {title_num} Program Chain {p:02d} Cell {i}.txt"
                # with open(meta_fn, "w") as f:
                #     f.write(
                #         textwrap.dedent(
                #             f"""\
                #             ;FFMETADATA1

                #             [CHAPTER]
                #             TIMEBASE=1
                #             START=0
                #             END={round(cell.playback_time.as_millis() / 1000 + 1)}
                #             title=Chapter {i}
                #             """
                #         )
                #     )
                # ffmpeg = f"{cat} | {dd} | ffmpeg -y -fflags +genpts -i pipe: -i {shlex.quote(str(meta_fn))} -map_chapters 1 {aspect} -map '0:v?' -map '0:a?' -map '0:s?' -c:v copy -c:a copy -c:s copy {shlex.quote(str(cell_mkv_fn))}"

                cell_mkv_fn = tmp_path / f"Title {title_num} Program Chain {p:02d} Cell {i}.mkv"
                try:
                    ffmpeg = f"cat {shlex.quote(str(combined_vob_fn))} | {dd} | ffmpeg -v error -y -fflags +genpts -i pipe: {aspect} -map '0:v?' -map '0:a?' -map '0:s?' -c:v copy -c:a copy -c:s copy {shlex.quote(str(cell_mkv_fn))}"
                    print(ffmpeg)
                    proc = subprocess.run(
                        ffmpeg,
                        shell=True,
                        check=True,
                        # stderr=subprocess.STDOUT,
                    )
                    # cell_files.append(cell_mkv_fn)

                    ffprobe = f"ffprobe -v error -show_entries format=duration -output_format json -i '{cell_mkv_fn}'"
                    completed = subprocess.run(ffprobe, shell=True, check=True, capture_output=True)
                    data = json.loads(completed.stdout.decode())
                    # cell_frames = int(data["streams"][0]["nb_read_frames"])
                    # cell_frames = int(data["streams"][0]["nb_read_packets"])
                    cell_duration = float(data["format"]["duration"]) - 0.05
                except Exception as exc:
                    print(
                        f"Exception probing duration from Cell {i}, using playback time from ifo instead: {exc}"
                    )
                    cell_duration = cell.playback_time.as_millis() / 1000.0 + 0.1
                else:
                    print(
                        f"Cell {i}: Probed time {cell_duration}, Cell time {cell.playback_time.as_millis() / 1000.0}, Difference {cell_duration - cell.playback_time.as_millis() / 1000}"
                    )

                if cell_mkv_fn.exists():
                    os.unlink(cell_mkv_fn)

                # print(f"{cell_frames} frames in cell {i}")
                # end_frames = current_frames + cell_frames
                # chapter_metadata.append(textwrap.dedent(
                #     f"""\
                #     [CHAPTER]
                #     TIMEBASE={chain.duration.fps.denominator}/{chain.duration.fps.numerator}
                #     START={current_frames}
                #     END={end_frames}
                #     title=Chapter {i}
                #     """
                # ))
                # print(
                #     f"Frame time {float(cell_frames / chain.duration.fps)}, Cell time {cell.playback_time.as_millis() / 1000}"
                # )
                # current_frames = end_frames

                last = cell

                if cell_duration + extra_time < 2:
                    print(f"Cell too short, skipping chapter")
                    # extra_time += cell_duration
                    continue

                end_time = current_time + (extra_time + cell_duration) * 1000000
                chapter_metadata.append(
                    textwrap.dedent(
                        f"""\
                        [CHAPTER]
                        TIMEBASE=1/1000000
                        START={round(current_time)}
                        END={round(end_time)}
                        title=Chapter {i}
                        """
                    )
                )
                current_time = end_time
                extra_time = 0

                # end_time = current_time + cell.playback_time.as_millis() * 1000
                # chapter_metadata.append(textwrap.dedent(
                #     f"""\
                #     [CHAPTER]
                #     TIMEBASE=1/1000000
                #     START={round(current_time)}
                #     END={round(end_time)}
                #     title=Chapter {i}
                #     """
                # ))
                # current_time = end_time

            meta_fn = tmp_path / f"t{title_num}p{p:02d}.txt"
            with open(meta_fn, "w") as f:
                f.write(f";FFMETADATA1\n\n{'\n'.join(chapter_metadata)}")

            dd = f"dd ibs=2048 iflag=fullblock count={last.last_vobu_end_sector + 1}"
            program_chain_cut_vod_fn = tmp_path / f"Title {title_num} Program Chain {p:02d} Cut.vob"
            cut = f"cat {shlex.quote(str(combined_vob_fn))} | {dd} > {shlex.quote(str(program_chain_cut_vod_fn))}"
            print(cut)
            proc = subprocess.run(
                cut,
                shell=True,
                check=True,
                # stderr=subprocess.STDOUT,
            )

            if chain.cells[0].first_vobu_start_sector != 0:
                pre_mkv_path = tmp_path / f"Title {title_num} Program Chain {p:02d} Pre.mkv"
                dd = f"dd ibs=2048 iflag=fullblock count={chain.cells[0].first_vobu_start_sector - 1}"
                ffmpeg = f"cat {shlex.quote(str(program_chain_cut_vod_fn))} | {dd} | ffmpeg -v error -y -fflags +genpts -i pipe: {aspect} -map '0:v?' -map '0:a?' -map '0:s?' -c:v copy -c:a copy -c:s copy {shlex.quote(str(pre_mkv_path))}"
                print(ffmpeg)
                proc = subprocess.run(
                    ffmpeg,
                    shell=True,
                    check=True,
                    # stderr=subprocess.STDOUT,
                )

                ffprobe = f"ffprobe -v error -show_entries format=duration -output_format json -i '{pre_mkv_path}'"
                completed = subprocess.run(ffprobe, shell=True, check=True, capture_output=True)
                data = json.loads(completed.stdout.decode())
                pre_duration = float(data["format"]["duration"])
                os.unlink(pre_mkv_path)
            else:
                pre_duration = 0

            # dd = f"dd ibs=2048 iflag=fullblock skip={chain.cells[0].first_vobu_start_sector} count={last.last_vobu_end_sector - chain.cells[0].first_vobu_start_sector + 1}"

            # # length = f"{chain.duration.hours:02d}:{chain.duration.minutes:02d}:{chain.duration.seconds:02d}.{round(chain.duration.frames / pyparsedvd.FRAMERATE[chain.duration.fps] * 1000):03d}"
            # # print(f"{cat}{seek} | ffmpeg -fflags +genpts -i pipe: -aspect 720:480 -map 0:v -map 0:a -map 0:s -c:v copy -c:a copy -c:s copy -t {length} 'Title {title_num:02d} Program Chain {p:02d}.mkv'")
            # cmd = f"{cat} | {dd} | ffmpeg -fflags +genpts -i pipe: -i {meta_fn} -map_chapters 1 {aspect} -map '0:v?' -map '0:a?' -map '0:s?' -c:v copy -c:a copy -c:s copy 'Title {title_num} Program Chain {p:02d}.mkv' || exit 1"
            # cmd = f"ffmpeg -v error -y {' '.join(f'-i {shlex.quote(str(cell_file))}' for cell_file in cell_files)} {aspect} -map '0:v?' -map '0:a?' -map '0:s?' -c:v copy -c:a copy -c:s copy {shlex.quote(str(out_path / f'Title {title_num} Program Chain {p:02d}.mkv'))}"

            # cmd = f"{cat} | {dd} | ffmpeg -fflags +genpts -y -ss {pre_duration}s -i pipe: -i {shlex.quote(str(meta_fn))} -map_chapters 1 {aspect} -map '0:v?' -map '0:a?' -map '0:s?' -c:v copy -c:a copy -c:s copy {shlex.quote(str(out_path / f'Title {title_num} Program Chain {p:02d}.mkv'))}"
            cmd = f"ffmpeg -v error -fflags +genpts -y -ss {pre_duration}s -i {shlex.quote(str(program_chain_cut_vod_fn))} -i {shlex.quote(str(meta_fn))} -map_chapters 1 {aspect} -map '0:v?' -map '0:a?' -map '0:s?' -c:v copy -c:a copy -c:s copy {shlex.quote(str(out_path / f'Title {title_num} Program Chain {p:02d}.mkv'))}"
            # cmds.append(cmd)
            print(cmd)
            proc = subprocess.run(
                cmd,
                shell=True,
                check=True,
                # stderr=subprocess.STDOUT,
            )
            os.unlink(meta_fn)
            os.unlink(program_chain_cut_vod_fn)
        os.unlink(combined_vob_fn)

    # import pprint; pprint.pprint(vts_pgci)

    # with open(out_path / "cmds.sh", "w") as f:
    #     f.write(f"#!/bin/bash -ex\n{'\n'.join(cmds)}\n")
