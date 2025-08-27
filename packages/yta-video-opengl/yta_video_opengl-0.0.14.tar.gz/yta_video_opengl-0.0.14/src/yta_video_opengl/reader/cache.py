"""
The pyav container stores the information based
on the packets timestamps (called 'pts'). Some
of the packets are considered key_frames because
they include those key frames.

Also, this library uses those key frames to start
decodifying from there to the next one, obtaining
all the frames in between able to be read and
modified.

This cache system will look for the range of 
frames that belong to the key frame related to the
frame we are requesting in the moment, keeping in
memory all those frames to be handled fast. It
will remove the old frames if needed to use only
the 'size' we set when creating it.

A stream can have 'fps = 60' but use another
different time base that make the pts values go 0,
 256, 512... for example. The 'time_base' is the
only accurate way to obtain the pts.

Feel free to move this explanation to other
place, its about the duration.

The stream 'duration' parameter is measured
on ticks, the amount of ticks that the
stream lasts. Here below is an example:

- Duration raw: 529200
- Time base: 1/44100
- Duration (seconds): 12.0
"""
from yta_video_opengl.t import T
from av.container import InputContainer
from av.video.stream import VideoStream
from av.audio.stream import AudioStream
from av.video.frame import VideoFrame
from av.audio.frame import AudioFrame
from av.packet import Packet
from yta_validation.parameter import ParameterValidator
from yta_validation import PythonValidator
from quicktions import Fraction
from collections import OrderedDict
from typing import Union

import numpy as np
import math


# TODO: This is not actually a Video
# cache, is a FrameCache because we
# create one for video but another
# one for audio. Rename it please.
class VideoFrameCache:
    """
    Class to manage the frames cache of a video
    within a video reader instance.
    """

    @property
    def fps(
        self
    ) -> Union[int, Fraction, None]:
        """
        The frames per second.
        """
        return (
            self.stream.average_rate
            if self.stream.type == 'video' else
            self.stream.rate
        )
    
    @property
    def time_base(
        self
    ) -> Union[Fraction, None]:
        """
        The time base of the stream.
        """
        return self.stream.time_base

    def __init__(
        self,
        container: InputContainer,
        stream: Union[VideoStream, AudioStream],
        size: Union[int, None] = None
    ):
        ParameterValidator.validate_mandatory_instance_of('container', container, InputContainer)
        ParameterValidator.validate_mandatory_instance_of('stream', stream, [VideoStream, AudioStream])
        ParameterValidator.validate_positive_int('size', size)

        self.container: InputContainer = container
        """
        The pyav container.
        """
        self.stream: Union[VideoStream, AudioStream] = stream
        """
        The pyav stream.
        """
        self.cache: OrderedDict = OrderedDict()
        """
        The cache ordered dictionary.
        """
        self.size: Union[int, None] = size
        """
        The size (in number of frames) of the cache.
        """
        self.key_frames_pts: list[int] = []
        """
        The list that contains the timestamps of the
        key frame packets, ordered from begining to
        end.
        """

        # TODO: This is new, remove this comment if
        # it is ok
        # TODO: This way of obtaining the duration
        # in ticks must be a utils
        self.frame_duration: int = (
            self.stream.duration / self.stream.frames
            if PythonValidator.is_instance_of(stream, VideoStream) else
            # TODO: Is this below ok (?)
            self.stream.frames
        )
        """
        The duration (in ticks) of the frame, that
        is the step between the different pts.
        """
        self._last_packet_accessed: Union[Packet, None] = None
        """
        The last packet that has been accessed
        """
        self._last_frame_read: Union[VideoFrame, AudioFrame, None] = None
        """
        The last frame we have read when decoding.
        Useful to avoid seeking all the time when we
        don't need it.
        """

        self._prepare()

    def _prepare(
        self
    ):
        # Index key frames
        for packet in self.container.demux(self.stream):
            if packet.is_keyframe:
                self.key_frames_pts.append(packet.pts)

        # The cache size will be auto-calculated to
        # use the amount of frames of the biggest
        # interval of frames that belongs to a key
        # frame, or a value by default
        # TODO: Careful if this is too big
        fps = (
            float(self.stream.average_rate)
            if PythonValidator.is_instance_of(self.stream, VideoStream) else
            float(self.stream.rate)
        )
        # Intervals, but in number of frames
        intervals = np.diff(
            # Intervals of time between keyframes
            np.array(self.key_frames_pts) * self.time_base
        ) * fps

        self.size = (
            math.ceil(np.max(intervals))
            if intervals.size > 0 else
            (
                self.size or
                # TODO: Make this 'default_size' a setting or something
                60
            )
        )
        
        self.container.seek(0)

    def _get_nearest_keyframe_pts(
        self,
        pts: int
    ):
        """
        Get the fps of the keyframe that is the
        nearest to the provided 'pts'. Useful to
        seek and start decoding frames from that
        keyframe.
        """
        return max([
            key_frame_pts
            for key_frame_pts in self.key_frames_pts
            if key_frame_pts <= pts
        ])

    def _store_frame_in_cache(
        self,
        frame: Union[VideoFrame, AudioFrame]
    ) -> Union[VideoFrame, AudioFrame]:
        """
        Store the provided 'frame' in cache if it
        is not on it, removing the first item of
        the cache if full.
        """
        if frame.pts not in self.cache:
            self.cache[frame.pts] = frame

            # Clean cache if full
            if len(self.cache) > self.size:
                self.cache.popitem(last = False)

        return frame
    
    def _seek(
        self,
        pts: int
    ):
        """
        Seek to the given 'pts' only if it is not
        the next 'pts' to the last read, and it 
        will also apply a pad to avoid problems
        when reading audio frames.

        TODO: Apply the padding only to audio 
        frame reading (?)
        """
        # I found that it is recommended to
        # read ~100ms before the pts we want to
        # actually read so we obtain the frames
        # clean (this is important in audio)
        # TODO: This is maybe too much for a
        # video and not needed
        pts_pad = int(0.1 / self.time_base)
        self.container.seek(
            offset = max(0, pts - pts_pad),
            stream = self.stream
        )

    def get_video_frame(
        self,
        t: Union[int, float, Fraction]
    ) -> VideoFrame:
        """
        Get the video frame that is in the 't'
        time moment provided.
        """
        for frame in self.get_video_frames(t):
            return frame

    def get_video_frames(
        self,
        start: Union[int, float, Fraction] = 0,
        end: Union[int, float, Fraction, None] = None
    ):
        """
        Get all the frames in the range between
        the provided 'start' and 'end' time in
        seconds.

        This method is an iterator that yields
        the frame, its t and its index.
        """
        start = T(start, self.time_base).truncated
        end = (
            T(end, self.time_base).truncated
            if end is not None else
            # The next frame
            start + (1 / self.fps)
        )

        key_frame_pts = self._get_nearest_keyframe_pts(start / self.time_base)

        if (
            self._last_packet_accessed is None or
            self._last_packet_accessed.pts != key_frame_pts
        ):
            self._seek(key_frame_pts)

        for packet in self.container.demux(self.stream):
            if packet.pts is None:
                continue

            self._last_packet_accessed = packet

            for frame in packet.decode():
                if frame.pts is None:
                    continue

                # We store all the frames in cache
                self._store_frame_in_cache(frame)
                
                current_frame_time = frame.pts * self.time_base
                
                # We want the range [start, end)
                if start <= current_frame_time < end:
                    yield frame

                if current_frame_time >= end:
                    break

    def get_audio_frame_from_t(
        self,
        t: Union[int, float, Fraction]
    ):
        """
        Get the single audio frame that must be
        played at the 't' time moment provided.
        This method is useful to get the single
        audio frame that we need to combine 
        when using it in a composition.

        TODO: Are we actually using this method (?)
        """
        t: T = T(t, self.time_base)
        # We need the just one audio frame
        for frame in self.get_audio_frames(t.truncated, t.next(1).truncated):
            return frame

    def get_audio_frames_from_t(
        self,
        t: Union[int, float, Fraction]
    ):
        """
        Get all the audio frames that must be
        played at the 't' time moment provided.
        """
        for frame in self.get_audio_frames(t):
            yield frame

    def get_audio_frames(
        self,
        start: Union[int, float, Fraction] = 0,
        end: Union[int, float, Fraction, None] = None
    ):
        """
        Get all the audio frames in the range
        between the provided 'start' and 'end'
        time (in seconds).

        This method is an iterator that yields
        the frame, its t and its index.
        """
        # TODO: Is this ok? We are trying to obtain
        # the audio frames for a video frame, so
        # should we use the 'self.time_base' to
        # truncate (?)
        start = T(start, self.time_base).truncated
        end = (
            T(end, self.time_base).truncated
            if end is not None else
            start + (1 / self.fps)
        )

        key_frame_pts = self._get_nearest_keyframe_pts(start / self.time_base)

        if (
            self._last_packet_accessed is None or
            self._last_packet_accessed.pts != key_frame_pts
        ):
            self._seek(key_frame_pts)

        for packet in self.container.demux(self.stream):
            if packet.pts is None:
                continue

            self._last_packet_accessed = packet

            for frame in packet.decode():
                if frame.pts is None:
                    continue

                # We store all the frames in cache
                self._store_frame_in_cache(frame)

                current_frame_time = frame.pts * self.time_base
                # End is not included, its the start of the
                # next frame actually
                frame_end = current_frame_time + (frame.samples / self.stream.sample_rate)

                # For the next comments imagine we are looking
                # for the [1.0, 2.0) audio time range
                # Previous frame and nothing is inside
                if frame_end <= start:
                    # From 0.25 to 1.0
                    continue
                
                # We finished, nothing is inside and its after
                if current_frame_time >= end:
                    # From 2.0 to 2.75
                    return

                # If we need audio from 1 to 2, audio is:
                #   - from 0 to 0.75    (Not included, omit)
                #   - from 0.5 to 1.5   (Included, take 1.0 to 1.5)
                #   - from 0.5 to 2.5   (Included, take 1.0 to 2.0)
                #   - from 1.25 to 1.5  (Included, take 1.25 to 1.5)
                #   - from 1.25 to 2.5  (Included, take 1.25 to 2.0)
                #   - from 2.5 to 3.5   (Not included, omit)
                
                # Here below, at least a part is inside
                if (
                    current_frame_time < start and
                    frame_end > start
                ):
                    # A part at the end is included
                    end_time = (
                        # From 0.5 to 1.5 0> take 1.0 to 1.5
                        frame_end
                        if frame_end <= end else
                        # From 0.5 to 2.5 => take 1.0 to 2.0
                        end
                    )
                    #print('A part at the end is included.')
                    frame = trim_audio_frame(
                        frame = frame,
                        start = start,
                        end = end_time,
                        time_base = self.time_base
                    )
                elif (
                    current_frame_time >= start and
                    current_frame_time < end
                ):
                    end_time = (
                        # From 1.25 to 1.5 => take 1.25 to 1.5
                        frame_end
                        if frame_end <= end else
                        # From 1.25 to 2.5 => take 1.25 to 2.0
                        end
                    )
                    # A part at the begining is included
                    #print('A part at the begining is included.')
                    frame = trim_audio_frame(
                        frame = frame,
                        start = current_frame_time,
                        end = end_time,
                        time_base = self.time_base
                    )

                # If the whole frame is in, past as it is
                yield frame
    
    def clear(
        self
    ) -> 'VideoFrameCache':
        """
        Clear the cache by removing all the items.
        """
        self.cache.clear()

        return self

def trim_audio_frame(
    frame: AudioFrame,
    start: Union[int, float, Fraction],
    end: Union[int, float, Fraction],
    time_base: Fraction
) -> AudioFrame:
    """
    Trim an audio frame to obtain the part between
    [start, end), that is provided in seconds.
    """
    # (channels, n_samples)
    samples = frame.to_ndarray()  
    n_samples = samples.shape[1]

    # In seconds
    frame_start = frame.pts * float(time_base)
    frame_end = frame_start + (n_samples / frame.sample_rate)

    # Overlapping 
    cut_start = max(frame_start, float(start))
    cut_end = min(frame_end, float(end))

    if cut_start >= cut_end:
        # No overlapping
        return None  

    # To sample indexes
    start_index = int(round((cut_start - frame_start) * frame.sample_rate))
    end_index = int(round((cut_end - frame_start) * frame.sample_rate))

    new_frame = AudioFrame.from_ndarray(
        # end_index is not included: so [start, end)
        array = samples[:, start_index:end_index],
        format = frame.format,
        layout = frame.layout
    )

    # Set attributes
    new_frame.sample_rate = frame.sample_rate
    new_frame.time_base = time_base
    new_frame.pts = int(round(cut_start / float(time_base)))

    return new_frame



"""
There is a way of editing videos being
able to arbitrary access to frames, that
is transforming the source videos to
intra-frame videos. This is a ffmpeg
command that can do it:

- `ffmpeg -i input.mp4 -c:v libx264 -x264opts keyint=1 -preset fast -crf 18 -c:a copy output_intra.mp4`

Once you have the 'output_intra.mp4',
each packet can decodify its frame 
depending not on the previous one, being
able to seek and jump easy.
"""