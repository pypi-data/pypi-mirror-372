"""VTS IFO parser."""

import enum
import fractions
import typing

import attrs
import more_itertools

import dvd
from . import util


class VTSCategory(enum.Enum):
    """Karaoke or not."""

    Unspecified = 0
    Karaoke = 1


class Aspect(enum.Enum):
    """Aspect ratio, includes the aspect ratio as a Fraction."""

    Standard = 0, fractions.Fraction(4, 3)
    Widescreen = 3, fractions.Fraction(16, 9)

    def __new__(cls, code: int, aspect: fractions.Fraction) -> typing.Self:
        """Allow for normal enum initialization and normal usage just passing the value."""
        obj = object.__new__(cls)
        obj._value_ = code
        return obj

    def __init__(self, code: int, aspect: fractions.Fraction | None = None):
        """Allow for normal enum initialization and normal usage just passing the value."""
        assert self.value == code
        assert aspect is not None
        self.aspect = aspect

    def __str__(self):
        """Str representation with additional info."""
        return f"({self.value}, {self.aspect})"

    def __repr__(self) -> str:
        """Repr with additional info."""
        return f"<{self.__class__.__name__}.{self.name}: {self.value!r}, {self.aspect!r}>"


class Standard(enum.Enum):
    """Video Standard."""

    NTSC = 0
    PAL = 1


class VideoCodingMode(enum.Enum):
    """Video coding mode."""

    MPEG_1 = 0
    MPEG_2 = 1


class Film(enum.Enum):
    """Type of film."""

    Camera = 0
    Film = 1  # PAL only


class Letterboxed(enum.Enum):
    """Whether the content is (should be?) letterboxed."""

    FullScreen = 0
    TopAndBottomCropped = 1


class Resolution(enum.Enum):
    """Video resolution, different for PAL and NTSC."""

    NTSC_0 = (Standard.NTSC, 0), (720, 480)
    PAL_0 = (Standard.PAL, 0), (720, 576)
    NTSC_1 = (Standard.NTSC, 1), (704, 480)
    PAL_1 = (Standard.PAL, 1), (704, 576)
    NTSC_2 = (Standard.NTSC, 2), (352, 480)
    PAL_2 = (Standard.PAL, 2), (352, 576)
    NTSC_3 = (Standard.NTSC, 3), (352, 240)
    PAL_3 = (Standard.PAL, 3), (352, 288)

    def __new__(cls, key: tuple[Standard, int], resolution: tuple[int, int]) -> typing.Self:
        """Allow for normal enum initialization and normal usage just passing the value."""
        obj = object.__new__(cls)
        obj._value_ = key
        return obj

    def __init__(self, key: tuple[Standard, int], resolution: tuple[int, int] | None = None):
        """Allow for normal enum initialization and normal usage just passing the value."""
        assert self.value == key
        assert resolution is not None
        self.resolution = resolution

    def __str__(self) -> str:
        """Str representation with additional info."""
        return f"({self.value}, {self.resolution})"

    def __repr__(self) -> str:
        """Repr with additional info."""
        return f"<{self.__class__.__name__}.{self.name}: {self.value!r}, {self.resolution!r}>"


@attrs.define
class VideoAttrs:
    """Video attributes."""

    auto_letterbox_disallowed: bool
    auto_panscan_disallowed: bool
    aspect: Aspect
    standard: Standard
    coding_mode: VideoCodingMode
    film: Film
    reserved: bool
    letterboxed: Letterboxed
    resolution: Resolution
    cc_field_2: bool
    cc_field_1: bool

    @classmethod
    def from_stream(cls, stream: util.BinaryStream) -> typing.Self:
        """Construct from binary stream."""
        raw = stream.get_bytes(2)
        standard = Standard((raw[0] >> 4) & 0b11)
        return cls(
            (raw[0] & 0b1) == 1,
            ((raw[0] >> 1) & 0b1) == 1,
            Aspect((raw[0] >> 2) & 0b11),
            standard,
            VideoCodingMode((raw[0] >> 6) & 0b11),
            Film(raw[1] & 0b1),
            ((raw[1] >> 1) & 0b1) == 1,
            Letterboxed((raw[1] >> 2) & 0b1),
            Resolution((standard, (raw[1] >> 3) & 0b111)),
            ((raw[1] >> 6) & 0b1) == 1,
            ((raw[1] >> 7) & 0b1) == 1,
        )


class ApplicationMode(enum.Enum):
    """Application mode."""

    Unspecified = 0
    Karaoke = 1
    Surround = 2


class LanguageType(enum.Enum):
    """Language type."""

    Unspecified = 0
    Specified = 1


class AudioCodingMode(enum.Enum):
    """Audio coding mode."""

    AC3 = 0
    Mpeg_1 = 2
    Mpeg_2ext = 3
    LPCM = 4
    DTS = 6


class SampleRate(enum.Enum):
    """Sample rate."""

    SR_48Ksps = 0
    SR_96Ksps = 1


class Quantization(enum.Enum):
    """Quantization."""

    Q_16bps = 0
    Q_20bps = 1
    Q_24bps = 2
    DynamicRangeControl = 3


class AudioCodeExtension(enum.Enum):
    """Audio code extension."""

    Unspecified = 0
    Normal = 1
    ForVisuallyImpaired = 2
    DirectorsComments = 3
    AlternateDirectorsComments = 4


class Singers(enum.Enum):
    """Singers."""

    Solo = 0
    Duet = 1


class ChannelAssignments(enum.Enum):
    """Audio channel assignments."""

    C = 2, "2/0 L,R"
    D = 3, "3/0 L,M,R"
    E = 4, "2/1 L,R,V1"
    F = 5, "3/1 L,M,R,V1"
    G = 6, "2/2 L,R,V1,V2"
    H = 7, "3/2 L,M,R,V1,V2"

    def __new__(cls, code: int, description: str) -> typing.Self:
        """Allow for normal enum initialization and normal usage just passing the value."""
        obj = object.__new__(cls)
        obj._value_ = code
        return obj

    def __init__(self, code: int, description: str | None = None):
        """Allow for normal enum initialization and normal usage just passing the value."""
        assert self.value == code
        assert description is not None
        self.description = description

    def __str__(self):
        """Str representation with additional info."""
        return f"({self.value}, {self.description})"

    def __repr__(self) -> str:
        """Repr with additional info."""
        return f"<{self.__class__.__name__}.{self.name}: {self.value!r}, {self.description!r}>"


@attrs.define
class KaraokeInformation:
    """Karaoke information."""

    singers: Singers
    mc_intro_present: bool
    karaoke_version: int
    channel_assignments: ChannelAssignments

    @classmethod
    def from_byte(cls, value: int) -> typing.Self:
        """Construct from binary stream."""
        assert ((value >> 7) & 0b1) == 0, "bit 7 should be zero for KaraokeInformation"
        return cls(
            Singers(value & 0b1),
            ((value >> 1) & 0b1) == 1,
            (value >> 2) & 0b11,
            ChannelAssignments((value >> 4) & 0b111),
        )


@attrs.define
class SurroundInformation:
    """Surround information."""

    _reserved_1: int
    dolby_surround: bool
    _reserved_2: int

    @classmethod
    def from_byte(cls, value: int) -> typing.Self:
        """Construct from byte."""
        return cls(
            value & 0b111,
            ((value >> 3) & 0b1) == 1,
            (value >> 4) & 0b1111,
        )


@attrs.define
class AudioAttrs:
    """Audio attributes."""

    application_mode: ApplicationMode
    language_type: LanguageType
    multichannel_extension_present: bool
    coding_mode: AudioCodingMode
    channels: int
    _reserved_1: bool
    sample_rate: SampleRate
    quantization: Quantization
    language_code: bytes
    language_code_extension: int
    code_extension: AudioCodeExtension
    _reserved_2: int
    application_information: KaraokeInformation | SurroundInformation | int

    @classmethod
    def from_stream(cls, stream: util.BinaryStream) -> typing.Self:
        """Construct from binary stream."""
        raw = stream.get_bytes(8)
        application_mode = ApplicationMode(raw[0] & 0b11)
        match application_mode:
            case ApplicationMode.Unspecified:
                application_information: KaraokeInformation | SurroundInformation | int = raw[7]
            case ApplicationMode.Karaoke:
                application_information = KaraokeInformation.from_byte(raw[7])
            case ApplicationMode.Surround:
                application_information = SurroundInformation.from_byte(raw[7])

        return cls(
            application_mode,
            LanguageType((raw[0] >> 2) & 0b11),
            ((raw[0] >> 4) & 0b1) == 1,
            AudioCodingMode((raw[0] >> 5) & 0b111),
            raw[1] & 0b111,
            ((raw[1] >> 3) & 0b1) == 1,
            SampleRate((raw[1] >> 4) & 0b11),
            Quantization((raw[1] >> 6) & 0b11),
            raw[2:4],
            raw[4],
            AudioCodeExtension(raw[5]),
            raw[6],
            application_information,
        )


@attrs.define
class MenuAudioAttrs:
    """Menu audio attributes."""

    _raw: AudioAttrs
    coding_mode: AudioCodingMode
    channels: int
    sample_rate: SampleRate
    quantization: Quantization

    @classmethod
    def from_audio_attrs(cls, audio_attrs: AudioAttrs) -> typing.Self:
        """Construct from AudioAttrs."""
        return cls(
            audio_attrs,
            audio_attrs.coding_mode,
            audio_attrs.channels,
            audio_attrs.sample_rate,
            audio_attrs.quantization,
        )


# @attrs.define
# class MenuAudioAttrs:
#     _reserved_1: int
#     coding_mode: AudioCodingMode
#     channels: int
#     _reserved_2: bool
#     sample_rate: SampleRate
#     quantization: Quantization
#     _reserved_3: bytes

#     @classmethod
#     def from_bytes(cls, raw: bytes) -> typing.Self:
#         return MenuAudioAttrs(
#             raw[0] & 0b11111,
#             AudioCodingMode((raw[0] << 5) & 0b111),
#             raw[1] & 0b111,
#             ((raw[1] >> 3) & 0b1) == 1,
#             SampleRate((raw[1] >> 4) & 0b11),
#             Quantization((raw[1] >> 6) & 0b11),
#             raw[2:],
#         )


class SubpictureCodingMode(enum.Enum):
    """Subpicture coding mode."""

    TwoBitRLE = 0


class SubpictureCodeExtension(enum.Enum):
    """Subpicture code extension."""

    Unspecified = 0
    Normal = 1
    Large = 2
    Children = 3
    NormalCaptions = 5
    LargeCaptions = 6
    ChildrensCaptions = 7
    Forced = 9
    DirectorComments = 13
    LargeDirectorComments = 14
    DirectorCommentsForChildren = 15


@attrs.define
class SubpictureAttrs:
    """Subpicture attributes."""

    language_type: LanguageType
    _reserved_1: int
    coding_mode: SubpictureCodingMode
    _reserved_2: int
    language_code: bytes
    language_extension: int
    code_extension: SubpictureCodeExtension

    @classmethod
    def from_stream(cls, stream: util.BinaryStream) -> typing.Self:
        """Construct from binary stream."""
        raw = stream.get_bytes(6)
        return cls(
            LanguageType(raw[0] & 0b11),
            (raw[0] >> 2) & 0b111,
            SubpictureCodingMode((raw[0] >> 5) & 0b111),
            raw[1],
            raw[2:4],
            raw[4],
            SubpictureCodeExtension(raw[5]),
        )


@attrs.define
class MenuSubpictureAttrs:
    """Menu subpicture attributes."""

    _raw: SubpictureAttrs
    coding_mode: SubpictureCodingMode

    @classmethod
    def from_subpicture_attrs(cls, raw: SubpictureAttrs) -> typing.Self:
        """Construct from SubpictureAttrs."""
        return cls(
            raw,
            raw.coding_mode,
        )


@attrs.define
class Version:
    """IFO Version."""

    minor: int
    major: int

    @classmethod
    def from_stream(cls, stream: util.BinaryStream) -> "Version":
        """Construct from binary stream."""
        raw = stream.get_bytes(2)
        assert raw[0] == 0
        return cls(raw[1] & 0b1111, (raw[1] >> 4) & 0b1111)


@attrs.define
class CellAddress:
    """Cell address."""

    vob_idx: int
    cell_idx: int
    _reserved: int
    start_sector_in_vob: int
    end_sector_in_vob: int

    @classmethod
    def from_stream(cls, stream: util.BinaryStream) -> typing.Self:
        """Construct from binary stream."""
        return cls(*stream.unpack("HBBII"))


@attrs.define
class CellAddressTable:
    """Cell address table."""

    num_vobs: int
    _reserved: int
    end_address: int

    entries: list[CellAddress]

    @classmethod
    def from_stream(cls, stream: util.BinaryStream) -> typing.Self:
        """Construct from binary stream."""
        start_address = stream.tell()
        (num_vobs, _reserved, end_address) = stream.unpack("HHI")
        entries = [CellAddress.from_stream(stream) for _ in range(8, end_address, 12)]
        assert (
            stream.tell() - start_address == end_address + 1
        ), f"{stream.tell()} - {start_address} ({stream.tell() - start_address}) != {end_address + 1}"
        return cls(num_vobs, _reserved, end_address, entries)


@attrs.define
class VobuAddressMap:
    """VOBU address map."""

    end_address: int
    vobu_starting_sectors_within_vob: list[int]

    @classmethod
    def from_stream(cls, stream: util.BinaryStream) -> typing.Self:
        """Construct from binary stream."""
        start_address = stream.tell()
        (end_address,) = stream.unpack("I")
        vobu_starting_sectors_within_vob = [stream.unpack("I")[0] for _ in range(4, end_address, 4)]
        assert (
            stream.tell() - start_address == end_address + 1
        ), f"{stream.tell()} - {start_address} ({stream.tell() - start_address}) != {end_address + 1}"
        return cls(end_address, vobu_starting_sectors_within_vob)


@attrs.define
class PartOfTitle:  # VTS_PTT
    """Part of title."""

    program_chain: int  # PGCN
    program: int  # PGN

    @classmethod
    def from_stream(cls, stream: util.BinaryStream) -> typing.Self:
        """Construct from binary stream."""
        return cls(*stream.unpack("HH"))


@attrs.define
class TitlesAndChaptersTable:  # VTS_PTT_SRPT
    """Titles and chapters table, or part-of-titles table."""

    num_titles: int
    _reserved: bytes
    end_address: int

    titles: list[list[PartOfTitle]]  # indexed by TT_PTTN

    @classmethod
    def from_stream(cls, stream: util.BinaryStream) -> typing.Self:
        """Construct from binary stream."""
        start_address = stream.tell()
        (num_titles, _reserved, end_address) = stream.unpack("HHI")
        titles = []
        offsets = stream.unpack("I" * num_titles)
        for title_idx in range(num_titles):
            stream.seek(start_address + offsets[title_idx])
            title_end_address = (
                offsets[title_idx + 1] if title_idx < num_titles - 1 else end_address
            ) + start_address
            title_parts = []
            idx = 1
            while stream.tell() < title_end_address:
                ptt = PartOfTitle.from_stream(stream)
                assert ptt.program == idx, f"{ptt.program} {idx}"
                idx += 1
                title_parts.append(ptt)
            titles.append(title_parts)
        assert (
            stream.tell() - start_address == end_address + 1
        ), f"{stream.tell()} - {start_address} ({stream.tell() - start_address}) != {end_address + 1}"
        return cls(num_titles, _reserved, end_address, titles)


class Framerate(enum.Enum):
    """Framerate."""

    # Illegal = 0, fractions.Fraction(0)
    TwentyFive = 1, fractions.Fraction(25)
    Thirty = 3, fractions.Fraction(30000, 1001)

    def __new__(cls, code: int, fps: fractions.Fraction) -> typing.Self:
        """Allow for normal enum initialization and normal usage just passing the value."""
        obj = object.__new__(cls)
        obj._value_ = code
        return obj

    def __init__(self, code: int, fps: fractions.Fraction | None = None):
        """Allow for normal enum initialization and normal usage just passing the value."""
        assert self.value == code
        assert fps is not None
        self.fps = fps

    def __str__(self):
        """Str representation with additional info."""
        return f"({self.value}, {self.fps})"

    def __repr__(self) -> str:
        """Repr with additional info."""
        return f"<{self.__class__.__name__}.{self.name}: {self.value!r}, {self.fps!r}>"


@attrs.define
class PlaybackTime:
    """Playback time."""

    framerate: Framerate
    hours: int
    minutes: int
    seconds: int
    frames: int

    @classmethod
    def from_stream(cls, stream: util.BinaryStream) -> typing.Self:
        """Construct from binary stream."""
        raw = stream.get_bytes(4)
        hours, minutes, seconds = [cls._bcd_to_int(i) for i in raw[:3]]
        frames_fps = raw[3]
        frames = cls._bcd_to_int(frames_fps & 0b111111)
        framerate = Framerate((frames_fps >> 6) & 0b11)
        return cls(framerate, hours, minutes, seconds, frames)

    @staticmethod
    def _bcd_to_int(bcd: int) -> int:
        """Convert binary coded decimal to int."""
        tens = 0b1111 & (bcd >> 4)
        assert tens < 10
        ones = bcd & 0b1111
        assert ones < 10
        return tens * 10 + ones

    def as_millis(self) -> float:
        """Return time as milliseconds."""
        return (
            (self.hours * 60 + self.minutes) * 60
            + self.seconds
            + float(self.frames / self.framerate.fps)
        ) * 1000

    # def __add__(self, b) -> typing.Self:
    #     assert self.framerate == b.framerate, "Framerates must be equal to add"
    #     ret = PlaybackTime(self.framerate, self.hours + b.hours, self.minutes + b.minutes, self.seconds + b.seconds, self.frames + b.frames)
    #     extra_secs = int(ret.frames / ret.framerate.fps)
    #     ret.seconds += extra_secs
    #     ret.frames -= int(extra_secs * ret.framerate.fps)


class ProhibitedUserOps(enum.IntFlag):
    """Prohibited user operations."""

    TimePlayOrSearch = enum.auto()  # 0b1
    PTTPlayOrSearch = enum.auto()  # 0b10
    TitlePlay = enum.auto()
    Stop = enum.auto()
    GoUp = enum.auto()
    TimeOrPTTSearch = enum.auto()
    TopPGOrPrevPGSearch = enum.auto()
    NextPGSearch = enum.auto()
    ForwardScan = enum.auto()
    BackwardScan = enum.auto()
    MenuCallTitle = enum.auto()
    MenuCallRoot = enum.auto()
    MenuCallSubpicture = enum.auto()
    MenuCallAudio = enum.auto()
    MenuCallAngle = enum.auto()
    MenuCallPTT = enum.auto()
    Resume = enum.auto()
    ButtonSelectOrActivate = enum.auto()
    StillOff = enum.auto()
    PauseOn = enum.auto()
    AudioStreamChange = enum.auto()
    SubpictureStreamChange = enum.auto()
    AngleChange = enum.auto()
    KaraokeAudioMixChange = enum.auto()
    VideoPresentationModeChange = enum.auto()


@attrs.define
class AudioStreamControl:
    """Audio stream control."""

    stream_or_substream_number: int
    _reserved_1: int
    stream_available: bool
    _reserved_2: int

    @classmethod
    def from_stream(cls, stream: util.BinaryStream) -> typing.Self:
        """Construct from binary stream."""
        raw = stream.get_bytes(2)
        return cls(
            raw[0] & 0b111,
            (raw[0] >> 3) & 0b1111,
            ((raw[0] >> 7) & 0b1) == 1,
            raw[1],
        )


@attrs.define
class SubpictureStreamControl:
    """Subpicture stream control."""

    stream_number_for_4_3: int
    _reserved_1: int
    stream_available: bool
    stream_number_for_wide: int
    reserved_2: int
    stream_number_for_letterbox: int
    reserved_3: int
    stream_number_for_pan_scan: int
    reserved_4: int

    @classmethod
    def from_stream(cls, stream: util.BinaryStream) -> typing.Self:
        """Construct from binary stream."""
        raw = stream.get_bytes(4)
        return cls(
            raw[0] & 0b11111,
            (raw[0] >> 5) & 0b11,
            ((raw[0] >> 7) & 0b1) == 1,
            raw[1] & 0b11111,
            (raw[1] >> 5) & 0b111,
            raw[2] & 0b11111,
            (raw[2] >> 5) & 0b111,
            raw[3] & 0b11111,
            (raw[3] >> 5) & 0b111,
        )


class PGPlaybackType(enum.Enum):
    """PG playback type."""

    Sequential = -1
    Random = 0
    Shuffle = 1


@attrs.define
class PGPlaybackMode:
    """PG playback mode."""

    playback_type: PGPlaybackType
    zero_index_program_count: int

    @classmethod
    def from_stream(cls, stream: util.BinaryStream) -> typing.Self:
        """Construct from binary stream."""
        raw = stream.get_bytes(1)[0]
        return cls(PGPlaybackType(-1 if raw == 0 else ((raw >> 7) & 0b1)), raw & 0b1111111)


@attrs.define
class TitlePGCCategory:
    """PGC category."""

    title_number: int
    is_entry_pgc: bool
    _reserved: int
    parental_management_mask: bytes

    @classmethod
    def from_stream(cls, stream: util.BinaryStream) -> typing.Self:
        """Construct from binary stream."""
        raw = stream.get_bytes(4)
        return cls(
            raw[0] & 0b1111111,
            ((raw[0] >> 7) & 0b1) == 1,
            raw[1],
            raw[2:],
        )


@attrs.define
class Color:
    """Color."""

    zero: int
    y: int
    cr: int
    cb: int

    @classmethod
    def from_stream(cls, stream: util.BinaryStream) -> typing.Self:
        """Construct from binary stream."""
        return cls(*stream.unpack("BBBB"))


@attrs.define
class Commands:
    """Commands."""

    num_pre_commands: int
    num_post_commands: int
    num_cell_commands: int
    end_address: int

    # TODO: Actual parsing of each command
    pre_commands: list[bytes]
    post_commands: list[bytes]
    cell_commands: list[bytes]

    @classmethod
    def from_stream(cls, stream: util.BinaryStream) -> typing.Self:
        """Construct from binary stream."""
        start_address = stream.tell()
        (num_pre_commands, num_post_commands, num_cell_commands, end_address) = stream.unpack(
            "HHHH"
        )
        assert num_pre_commands + num_post_commands + num_cell_commands <= 128
        pre_commands = [stream.get_bytes(8) for _ in range(num_pre_commands)]
        post_commands = [stream.get_bytes(8) for _ in range(num_post_commands)]
        call_commands = [stream.get_bytes(8) for _ in range(num_cell_commands)]
        assert (
            stream.tell() - start_address == end_address + 1
        ), f"{stream.tell()} - {start_address} ({stream.tell() - start_address}) != {end_address + 1}"
        return cls(
            num_pre_commands,
            num_post_commands,
            num_cell_commands,
            end_address,
            pre_commands,
            post_commands,
            call_commands,
        )


class BlockType(enum.Enum):
    """Block type."""

    Normal = 0
    AngleBlock = 1


class CellType(enum.Enum):
    """Cell type."""

    Normal = 0b00
    FirstOfAngleBlock = 0b01
    MiddleOfAngleBlock = 0b10
    LastOfAngleBlock = 0b11


class KaraokeApplicationCellType(enum.Enum):
    """Karaoke application cell type."""

    NoneDesignated = 0
    TitlePicture = 1
    Introduction = 2
    SongPartOtherThanAClimax = 3  # bridge
    SongPartOfTheFirstClimax = 4
    SongPartOfTheSecondClimax = 5
    SongPartForALowVocal = 6
    SongPartForAHighVocal = 7
    SongPartForMixedVoices = 8
    InterludePart = 9  # instrumental
    InterludeFadeIn = 10
    InterludeFadeOut = 11
    FirstEnding = 12
    SecondEnding = 13


@attrs.define
class CellPlaybackInfo:
    """Cell playback information."""

    seamless_angle_linked_in_DS1: bool
    scr_discontinuity: bool
    interleaved: bool
    seamless_multiplex: bool
    block_type: BlockType
    cell_type: CellType

    application_cell_type: KaraokeApplicationCellType
    restricted: bool
    VOBU_still_mode: bool
    _reserved: bool

    still_time: int
    command_num: int

    playback_time: PlaybackTime

    first_vobu_start_sector: int
    first_ilvu_end_sector: int
    last_vobu_start_sector: int
    last_vobu_end_sector: int

    @classmethod
    def from_stream(cls, stream: util.BinaryStream) -> typing.Self:
        """Construct from binary stream."""
        (b1, b2, still_time, command_num) = stream.unpack("BBBB")
        playback_time = PlaybackTime.from_stream(stream)
        (
            first_vobu_start_sector,
            first_ilvu_end_sector,
            last_vobu_start_sector,
            last_vobu_end_sector,
        ) = stream.unpack("IIII")
        return cls(
            (b1 & 0b1) == 1,
            ((b1 >> 1) & 0b1) == 1,
            ((b1 >> 2) & 0b1) == 1,
            ((b1 >> 3) & 0b1) == 1,
            BlockType((b1 >> 4) & 0b11),
            CellType(b1 >> 6 & 0b11),
            KaraokeApplicationCellType(b2 & 0b11111),
            ((b2 >> 5) & 0b1) == 1,
            ((b2 >> 6) & 0b1) == 1,
            ((b2 >> 7) & 0b1) == 1,
            still_time,
            command_num,
            playback_time,
            first_vobu_start_sector,
            first_ilvu_end_sector,
            last_vobu_start_sector,
            last_vobu_end_sector,
        )


@attrs.define
class CellPositionInfo:
    """Cell position information."""

    vob_id: int
    _reserved: int
    cell_id: int

    @classmethod
    def from_stream(cls, stream: util.BinaryStream) -> typing.Self:
        """Construct from binary stream."""
        return cls(*stream.unpack("HBB"))


@attrs.define
class ProgramChain:
    """Program Chain."""

    _unknown: bytes
    num_programs: int
    num_cells: int
    playback_time: PlaybackTime
    prohibited_user_ops: list[ProhibitedUserOps]  # I don't know why this is 4 bytes
    audio_stream_controls: list[AudioStreamControl]  # 8
    subpicture_stream_controls: list[SubpictureStreamControl]  # 32
    next_pgcn: int
    prev_pgcn: int
    go_up_pgcn: int
    pg_playback_mode: PGPlaybackMode
    pgc_still_time: int
    color_lookup_table: list[Color]  # 16
    commands_offset: int
    program_map_offset: int
    cell_playback_info_table_offset: int
    cell_position_info_table_offset: int
    commands: Commands | None
    program_map: list[int]
    cell_playback_info_table: list[CellPlaybackInfo]
    cell_position_info_table: list[CellPositionInfo]

    @classmethod
    def from_stream(cls, stream: util.BinaryStream) -> typing.Self:
        """Construct from binary stream."""
        start_address = stream.tell()
        _unknown = stream.get_bytes(2)
        (num_programs, num_cells) = stream.unpack("BB")
        assert num_programs <= num_cells
        playback_time = PlaybackTime.from_stream(stream)
        prohibited_user_ops = [ProhibitedUserOps(stream.get_bytes(1)[0]) for _ in range(4)]
        audio_stream_controls = [AudioStreamControl.from_stream(stream) for _ in range(8)]
        subpicture_stream_controls = [
            SubpictureStreamControl.from_stream(stream) for _ in range(32)
        ]
        (next_pgcn, prev_pgcn, go_up_pgcn) = stream.unpack("HHH")
        pg_playback_mode = PGPlaybackMode.from_stream(stream)
        (pgc_still_time,) = stream.unpack("B")
        color_lookup_table = [Color.from_stream(stream) for _ in range(16)]
        (
            commands_offset,
            program_map_offset,
            cell_playback_info_table_offset,
            cell_position_info_table_offset,
        ) = stream.unpack("HHHH")

        if commands_offset == 0:
            commands = None
        else:
            stream.seek(start_address + commands_offset)
            commands = Commands.from_stream(stream)

        if num_programs == 0:
            assert (
                pgc_still_time == 0
                and playback_time.as_millis() == 0
                and pg_playback_mode.playback_type == PGPlaybackType.Sequential
                and program_map_offset == 0
                and cell_playback_info_table_offset == 0
                and cell_position_info_table_offset == 0
            )
        if program_map_offset == 0:
            program_map = []
        else:
            stream.seek(start_address + program_map_offset)
            program_map = list(stream.unpack("B" * num_programs))

        if cell_playback_info_table_offset == 0:
            cell_playback_info_table = []
        else:
            stream.seek(start_address + cell_playback_info_table_offset)
            cell_playback_info_table = [
                CellPlaybackInfo.from_stream(stream) for _ in range(num_cells)
            ]

        if cell_position_info_table_offset == 0:
            cell_position_info_table = []
        else:
            stream.seek(start_address + cell_position_info_table_offset)
            cell_position_info_table = [
                CellPositionInfo.from_stream(stream) for _ in range(num_cells)
            ]

        return cls(
            _unknown,
            num_programs,
            num_cells,
            playback_time,
            prohibited_user_ops,
            audio_stream_controls,
            subpicture_stream_controls,
            next_pgcn,
            prev_pgcn,
            go_up_pgcn,
            pg_playback_mode,
            pgc_still_time,
            color_lookup_table,
            commands_offset,
            program_map_offset,
            cell_playback_info_table_offset,
            cell_position_info_table_offset,
            commands,
            program_map,
            cell_playback_info_table,
            cell_position_info_table,
        )


@attrs.define
class TitleProgramChain:  # VTS_PGC
    """Program chain."""

    category: TitlePGCCategory
    offset: int
    program_chain: ProgramChain

    @classmethod
    def from_stream(cls, start_address: int, stream: util.BinaryStream) -> typing.Self:
        """Construct from binary stream."""
        category = TitlePGCCategory.from_stream(stream)
        (offset,) = stream.unpack("I")
        stream.seek(start_address + offset)
        return cls(category, offset, ProgramChain.from_stream(stream))


@attrs.define
class TitleProgramChainTable:  # VTS_PGCI
    """Program chain table."""

    num_program_chains: int
    _reserved: int
    end_address: int  # relative to beginning of he table
    program_chains: list[TitleProgramChain]

    @classmethod
    def from_stream(cls, stream: util.BinaryStream) -> typing.Self:
        """Construct from binary stream."""
        start_address = stream.tell()
        (num_program_chains, _reserved, end_address) = stream.unpack("HHI")

        program_chains = []
        for chain_num in range(num_program_chains):
            stream.seek(start_address + 8 + chain_num * 8)
            program_chains.append(TitleProgramChain.from_stream(start_address, stream))
        assert (
            stream.tell() - start_address == end_address + 1
        ), f"{stream.tell()} - {start_address} ({stream.tell() - start_address}) != {end_address + 1}"

        return cls(num_program_chains, _reserved, end_address, program_chains)


class MenuType(enum.Enum):
    """Menu type."""

    Root = 3
    SubPicture = 4
    Audio = 5
    Angle = 6
    PTT = 7


@attrs.define
class MenuPGCCategory:
    """Menu PGC category."""

    menu_type: MenuType | None
    _reserved: int
    is_entry_pgc: bool
    _unknown: int
    parental_management_mask: bytes

    @classmethod
    def from_stream(cls, stream: util.BinaryStream) -> typing.Self:
        """Construct from binary stream."""
        raw = stream.get_bytes(4)
        is_entry_pgc = ((raw[0] >> 7) & 0b1) == 1
        return cls(
            MenuType(raw[0] & 0b1111) if is_entry_pgc else None,
            (raw[0] >> 4) & 0b111,
            is_entry_pgc,
            raw[1],
            raw[2:],
        )


@attrs.define
class MenuProgramChain:
    """Menu program chain."""

    # from VTSM_LU entry
    pgc_category: MenuPGCCategory
    offset: int

    program_chain: ProgramChain  # VTSM_PGC

    @classmethod
    def from_stream(cls, start_address: int, stream: util.BinaryStream) -> typing.Self:
        """Construct from binary stream."""
        pgc_category = MenuPGCCategory.from_stream(stream)
        (offset,) = stream.unpack("I")
        stream.seek(start_address + offset)
        return cls(pgc_category, offset, ProgramChain.from_stream(stream))


class MenuExistenceFlags(enum.Flag):
    """Menu existence flags."""

    Root = 0x80
    SubPicture = 0x40
    Audio = 0x20
    Angle = 0x10
    PTT = 0x08


@attrs.define
class MenuLanguageUnit:
    """Menu language unit."""

    # from VTSM_PGCI_UT entry
    language_code: int  # ISO639
    language_code_extension: int
    menu_existence_flags: MenuExistenceFlags
    offset: int

    # from VTSM_LU
    num_program_chains: int
    _reserved: int
    end_address: int

    program_chains: list[MenuProgramChain]

    @classmethod
    def from_stream(cls, start_address: int, stream: util.BinaryStream) -> typing.Self:
        """Construct from binary stream."""
        # table entry in VTSM_PGCI_UT
        (language_code, language_code_extension, menu_existence_flags, offset) = stream.unpack(
            "HBBI"
        )
        lu_start_address = start_address + offset
        stream.seek(lu_start_address)

        # VTSM_LU
        (num_program_chains, _reserved, end_address) = stream.unpack("HHI")

        program_chains = []
        for pgc_idx in range(num_program_chains):
            stream.seek(lu_start_address + 8 + pgc_idx * 8)
            program_chains.append(MenuProgramChain.from_stream(lu_start_address, stream))
        assert (
            stream.tell() - lu_start_address == end_address + 1
        ), f"{stream.tell()} - {lu_start_address} ({stream.tell() - lu_start_address}) != {end_address + 1}"
        return cls(
            language_code,
            language_code_extension,
            MenuExistenceFlags(menu_existence_flags),
            offset,
            num_program_chains,
            _reserved,
            end_address,
            program_chains,
        )


@attrs.define
class MenuProgramChainTable:  # VTSM_PGCI_UT
    """Menu program chain table."""

    num_language_units: int
    _reserved: bytes
    end_address: int

    language_units: list[MenuLanguageUnit]

    @classmethod
    def from_stream(cls, stream: util.BinaryStream) -> typing.Self:
        """Construct from binary stream."""
        start_address = stream.tell()
        (num_language_units, _reserved, end_address) = stream.unpack("HHI")
        language_units = []
        for lu_idx in range(num_language_units):
            stream.seek(start_address + 8 + lu_idx * 8)
            language_units.append(MenuLanguageUnit.from_stream(start_address, stream))
        assert (
            stream.tell() - start_address == end_address + 1
        ), f"{stream.tell()} - {start_address} ({stream.tell() - start_address}) != {end_address + 1}"
        return cls(num_language_units, _reserved, end_address, language_units)


@attrs.define
class TimeMapEntry:
    """
    Time map entry.

    Sector offset within VOBS of VOBU which begins on or before the time for this entry and ends after the time
    for this entry.
    """

    sector_offset: int
    next_entry_for_different_cell: bool

    @classmethod
    def from_stream(cls, stream: util.BinaryStream) -> typing.Self:
        """Construct from binary stream."""
        (raw,) = stream.unpack("I")
        return cls(raw & 0b1111111111111111111111111111111, ((raw >> 31) & 0b1) == 1)


@attrs.define
class TimeMap:
    """Time map."""

    offset: int
    time_unit: int
    _unknown: int
    num_entries: int
    entries: list[TimeMapEntry]

    @classmethod
    def from_stream(cls, start_address: int, stream: util.BinaryStream) -> typing.Self:
        """Construct from binary stream."""
        (offset,) = stream.unpack("I")
        stream.seek(start_address + offset)
        (time_unit, _unknown, num_entries) = stream.unpack("BBH")
        assert num_entries <= 2048, f"{num_entries}"
        entries = [TimeMapEntry.from_stream(stream) for _ in range(num_entries)]
        return cls(offset, time_unit, _unknown, num_entries, entries)


@attrs.define
class TimeMapTable:  # VTS_TMAPTI
    """Time map table."""

    num_program_chains: int
    _unknown: int
    end_address: int
    time_maps: list[TimeMap]

    @classmethod
    def from_stream(cls, stream: util.BinaryStream) -> typing.Self:
        """Construct from binary stream."""
        start_address = stream.tell()
        (num_program_chains, _unknown, end_address) = stream.unpack("HHI")
        time_maps = []
        for tm_idx in range(num_program_chains):
            stream.seek(start_address + 8 + tm_idx * 4)
            time_maps.append(TimeMap.from_stream(start_address, stream))
        assert (
            stream.tell() - start_address == end_address + 1
        ), f"{stream.tell()} - {start_address} ({stream.tell() - start_address}) != {end_address + 1}"
        return cls(num_program_chains, _unknown, end_address, time_maps)


@attrs.define
class MultichannelExtension:
    """Multichannel extension, for karaoke."""

    ach0_guide_melody_exists: bool
    _reserved_1: int
    ach1_guide_melody_exists: bool
    _reserved_2: int
    ach2_guide_melody_2_exists: bool
    ach2_guide_melody_1_exists: bool
    ach2_guide_vocal_2_exists: bool
    ach2_guide_vocal_1_exists: bool
    _reserved_3: int
    ach3_guide_melody_2_exists: bool
    ach3_guide_melody_1_exists: bool
    ach3_guide_vocal_2_exists: bool
    ach3_guide_vocal_1_exists: bool
    _reserved_4: int
    ach4_guide_melody_2_exists: bool
    ach4_guide_melody_1_exists: bool
    ach4_guide_vocal_2_exists: bool
    ach4_guide_vocal_1_exists: bool
    _reserved_5: int
    _unknown: bytes

    @classmethod
    def from_stream(cls, stream: util.BinaryStream) -> typing.Self:
        """Construct from binary stream."""
        raw = stream.get_bytes(24)
        return cls(
            (raw[0] & 0b1) == 1,
            (raw[0] >> 1) & 0b1111111,
            (raw[1] & 0b1) == 1,
            (raw[1] >> 1) & 0b1111111,
            (raw[2] & 0b1) == 1,
            ((raw[2] >> 1) & 0b1) == 1,
            ((raw[2] >> 2) & 0b1) == 1,
            ((raw[2] >> 3) & 0b1) == 1,
            (raw[2] >> 4) & 0b1111,
            (raw[3] & 0b1) == 1,
            ((raw[3] >> 1) & 0b1) == 1,
            ((raw[3] >> 2) & 0b1) == 1,
            ((raw[3] >> 3) & 0b1) == 1,
            (raw[3] >> 4) & 0b1111,
            (raw[4] & 0b1) == 1,
            ((raw[4] >> 1) & 0b1) == 1,
            ((raw[4] >> 2) & 0b1) == 1,
            ((raw[4] >> 3) & 0b1) == 1,
            (raw[4] >> 4) & 0b1111,
            raw[5:],
        )


@attrs.define
class Cell:
    """Information about a single VOB cell."""

    position_info: CellPositionInfo
    playback_info: CellPlaybackInfo


@attrs.define
class Program:
    """Information about a single Chapter."""

    cells: list[Cell]

    @property
    def playback_time_as_millis(self) -> float:
        """Playback time for chapter as millis."""
        return sum(cell.playback_info.playback_time.as_millis() for cell in self.cells)

    @property
    def first_cell(self) -> Cell:
        """First Cell in the Program."""
        return self.cells[0]

    @property
    def last_cell(self) -> Cell:
        """Last Cell in the Program."""
        return self.cells[-1]


@attrs.define
class Chapter:
    """Information about a single Chapter."""

    programs: list[Program]

    @property
    def playback_time_as_millis(self) -> float:
        """Playback time for chapter as millis."""
        return sum(prog.playback_time_as_millis for prog in self.programs)

    @property
    def first_cell(self) -> Cell:
        """First Cell in the Program."""
        return self.programs[0].first_cell

    @property
    def last_cell(self) -> Cell:
        """Last Cell in the Program."""
        return self.programs[-1].last_cell


@attrs.define
class Title:
    """information about a single Title."""

    chapters: list[Chapter]

    @property
    def first_cell(self) -> Cell:
        """First Cell in the Program."""
        return self.chapters[0].first_cell

    @property
    def last_cell(self) -> Cell:
        """Last Cell in the Program."""
        return self.chapters[-1].last_cell


@attrs.define
class VTS_IFO:
    """VTS IFO file."""

    ifo_type: str
    last_title_set_sector: int
    last_ifo_sector: int
    version: Version
    vts_category: VTSCategory
    vts_mat_end_address: int
    menu_vob_start_sector: int
    title_vob_start_sector: int
    titles_and_chapters_table_sector_ptr: int  # -> VTS_PTT_SRPT
    title_program_chain_table_sector_ptr: int  # -> VTS_PGCI
    menu_program_chain_table_sector_ptr: int  # -> VTSM_PGCI_UT
    time_map_sector_ptr: int  # -> VTS_TMAPTI
    menu_cell_address_table_sector_ptr: int  # -> VTSM_C_ADT
    menu_vobu_address_map_sector_ptr: int  # -> VTSM_VOBU_ADMAP
    title_set_cell_address_table_sector_ptr: int  # -> VTS_C_ADT
    title_set_vobu_address_map_sector_ptr: int  # -> VTS_VOBU_ADMAP
    vtsm_vobs_video_attrs: VideoAttrs
    vtsm_vobs_num_audio_streams: int
    vtsm_vobs_audio_attrs: MenuAudioAttrs
    vtsm_vobs_num_subpicture_streams: int
    vtsm_vobs_subpicture_attributes: MenuSubpictureAttrs
    vts_vobs_video_attrs: VideoAttrs
    vts_vobs_num_audio_streams: int
    vts_vobs_audio_attrs: tuple[AudioAttrs, ...]
    vts_vobs_num_subpicture_streams: int
    vts_vobs_subpicture_attributes: tuple[SubpictureAttrs, ...]
    multichannel_extension: list[MultichannelExtension]  # 8

    titles_and_chapters_table: TitlesAndChaptersTable
    title_program_chain_table: TitleProgramChainTable
    menu_program_chain_table: MenuProgramChainTable
    time_map_table: TimeMapTable
    menu_cell_address_table: CellAddressTable
    menu_vobu_address_map: VobuAddressMap
    title_set_cell_address_table: CellAddressTable
    title_set_vobu_address_map: VobuAddressMap

    @classmethod
    def from_bytes(cls, inbytes: typing.BinaryIO) -> typing.Self:
        """Construct from binary input."""
        stream = util.BinaryStream(inbytes)

        ifo_type = stream.get_bytes(12).decode("utf-8")
        assert ifo_type == "DVDVIDEO-VTS", f"{ifo_type} != DVDVIDEO-VTS"
        (last_title_set_sector,) = stream.unpack("I")
        stream.skip_bytes(12)  # unspecified
        (last_ifo_sector,) = stream.unpack("I")
        version = Version.from_stream(stream)
        (vts_category_int,) = stream.unpack("I")
        vts_category = VTSCategory(vts_category_int)

        # Unused in VTS
        stream.unpack("HHB")
        stream.skip_bytes(19)  # unspecified padding
        stream.unpack("H")
        stream.skip_bytes(32)  # unused
        stream.unpack("Q")
        stream.skip_bytes(24)  # unspecified padding

        # TODO: What should this be checked against?
        (vts_mat_end_address,) = stream.unpack("I")

        # Unused in VTS
        stream.unpack("I")
        stream.skip_bytes(56)  # unspecified padding

        (
            menu_vob_start_sector,
            title_vob_start_sector,
            titles_and_chapters_table_sector_ptr,
            title_program_chain_table_sector_ptr,
            menu_program_chain_table_sector_ptr,
            time_map_sector_ptr,
            menu_cell_address_table_sector_ptr,
            menu_vobu_address_map_sector_ptr,
            title_set_cell_address_table_sector_ptr,
            title_set_vobu_address_map_sector_ptr,
        ) = stream.unpack("IIIIIIIIII")

        stream.skip_bytes(24)  # unspecified padding

        vtsm_vobs_video_attrs = VideoAttrs.from_stream(stream)

        (vtsm_vobs_num_audio_streams,) = stream.unpack("H")
        assert vtsm_vobs_num_audio_streams in (0, 1)

        vtsm_vobs_audio_attrs = MenuAudioAttrs.from_audio_attrs(AudioAttrs.from_stream(stream))

        # Unused
        stream.skip_bytes(56)  # reserved
        stream.skip_bytes(16)  # unknown

        (vtsm_vobs_num_subpicture_streams,) = stream.unpack("H")
        assert vtsm_vobs_num_subpicture_streams in (0, 1)

        vtsm_vobs_subpicture_attributes = MenuSubpictureAttrs.from_subpicture_attrs(
            SubpictureAttrs.from_stream(stream)
        )

        # Unused
        stream.skip_bytes(164)  # reserved

        vts_vobs_video_attrs = VideoAttrs.from_stream(stream)
        (vts_vobs_num_audio_streams,) = stream.unpack("H")
        assert vts_vobs_num_audio_streams <= 8
        vts_vobs_audio_attrs = tuple(
            AudioAttrs.from_stream(stream) for _ in range(vts_vobs_num_audio_streams)
        )
        # skip the rest of the unused entries
        stream.skip_bytes(8 * (8 - vts_vobs_num_audio_streams))

        # Unused
        stream.skip_bytes(16)

        (vts_vobs_num_subpicture_streams,) = stream.unpack("H")
        assert vts_vobs_num_subpicture_streams <= 32
        vts_vobs_subpicture_attributes = tuple(
            SubpictureAttrs.from_stream(stream) for _ in range(vts_vobs_num_subpicture_streams)
        )
        # skip the rest of the unused entries
        stream.skip_bytes(6 * (32 - vts_vobs_num_subpicture_streams))

        # Unused
        stream.skip_bytes(2)

        # Multichannel extension
        multichannel_extension = [MultichannelExtension.from_stream(stream) for _ in range(8)]

        # Unused
        stream.skip_bytes(40)

        end_of_header = stream.tell()
        assert end_of_header == 0x03D8 + 40

        stream.seek(titles_and_chapters_table_sector_ptr * dvd.SECTOR_SIZE)
        titles_and_chapters_table = TitlesAndChaptersTable.from_stream(stream)

        stream.seek(title_program_chain_table_sector_ptr * dvd.SECTOR_SIZE)
        title_program_chain_table = TitleProgramChainTable.from_stream(stream)

        stream.seek(menu_program_chain_table_sector_ptr * dvd.SECTOR_SIZE)
        menu_program_chain_table = MenuProgramChainTable.from_stream(stream)

        stream.seek(time_map_sector_ptr * dvd.SECTOR_SIZE)
        time_map_table = TimeMapTable.from_stream(stream)

        stream.seek(menu_cell_address_table_sector_ptr * dvd.SECTOR_SIZE)
        menu_cell_address_table = CellAddressTable.from_stream(stream)

        stream.seek(menu_vobu_address_map_sector_ptr * dvd.SECTOR_SIZE)
        menu_vobu_address_map = VobuAddressMap.from_stream(stream)

        stream.seek(title_set_cell_address_table_sector_ptr * dvd.SECTOR_SIZE)
        title_set_cell_address_table = CellAddressTable.from_stream(stream)

        stream.seek(title_set_vobu_address_map_sector_ptr * dvd.SECTOR_SIZE)
        title_set_vobu_address_map = VobuAddressMap.from_stream(stream)

        return cls(
            ifo_type,
            last_title_set_sector,
            last_ifo_sector,
            version,
            vts_category,
            vts_mat_end_address,
            menu_vob_start_sector,
            title_vob_start_sector,
            titles_and_chapters_table_sector_ptr,
            title_program_chain_table_sector_ptr,
            menu_program_chain_table_sector_ptr,
            time_map_sector_ptr,
            menu_cell_address_table_sector_ptr,
            menu_vobu_address_map_sector_ptr,
            title_set_cell_address_table_sector_ptr,
            title_set_vobu_address_map_sector_ptr,
            vtsm_vobs_video_attrs,
            vtsm_vobs_num_audio_streams,
            vtsm_vobs_audio_attrs,
            vtsm_vobs_num_subpicture_streams,
            vtsm_vobs_subpicture_attributes,
            vts_vobs_video_attrs,
            vts_vobs_num_audio_streams,
            vts_vobs_audio_attrs,
            vts_vobs_num_subpicture_streams,
            vts_vobs_subpicture_attributes,
            multichannel_extension,
            titles_and_chapters_table,
            title_program_chain_table,
            menu_program_chain_table,
            time_map_table,
            menu_cell_address_table,
            menu_vobu_address_map,
            title_set_cell_address_table,
            title_set_vobu_address_map,
        )

    def get_titles(self) -> list[Title]:
        """Get Titles with chapters, programs, and cells."""
        titles = []
        for title in self.titles_and_chapters_table.titles:
            program_chain_idxes = {ch.program_chain for ch in title}
            assert (
                len(program_chain_idxes) == 1
            ), f"Program PartOfTitles refer to more than one program chain {program_chain_idxes}"
            program_chain = self.title_program_chain_table.program_chains[
                list(program_chain_idxes)[0] - 1
            ]
            chapters = []
            for chapter, next_chapter in more_itertools.pairwise(title + [None]):
                assert chapter is not None
                start_program_idx = chapter.program - 1
                end_program_idx = (
                    next_chapter.program - 1
                    if next_chapter is not None
                    else program_chain.program_chain.num_programs
                )
                programs = []
                for program_idx in range(start_program_idx, end_program_idx):
                    start_cell = program_chain.program_chain.program_map[program_idx] - 1
                    end_cell = (
                        program_chain.program_chain.program_map[end_program_idx] - 1
                        if end_program_idx < program_chain.program_chain.num_programs
                        else program_chain.program_chain.num_cells
                    )
                    cells = []
                    for cell_idx in range(start_cell, end_cell):
                        cells.append(
                            Cell(
                                program_chain.program_chain.cell_position_info_table[cell_idx],
                                program_chain.program_chain.cell_playback_info_table[cell_idx],
                            )
                        )
                    programs.append(Program(cells))
                chapters.append(Chapter(programs))
            titles.append(Title(chapters))
        return titles
