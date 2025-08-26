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
"""
from yta_video_opengl.utils import t_to_pts, pts_to_t, pts_to_index, index_to_pts
from yta_video_opengl.t import T
from av.container import InputContainer
from av.video.stream import VideoStream
from av.audio.stream import AudioStream
from av.video.frame import VideoFrame
from av.audio.frame import AudioFrame
from yta_validation.parameter import ParameterValidator
from yta_validation import PythonValidator
from quicktions import Fraction
from collections import OrderedDict
from typing import Union

import numpy as np
import av
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
    ) -> float:
        """
        The frames per second as a float.
        """
        return (
            float(self.stream.average_rate)
            if self.stream.type == 'video' else
            float(self.stream.rate)
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

    def get_frame_from_pts(
        self,
        pts: int
    ) -> Union[VideoFrame, AudioFrame, None]:
        """
        Get the frame that has the provided 'pts'.

        This method will start decoding frames from the
        most near key frame (the one with the nearer
        pts) until the one requested is found. All those
        frames will be stored in cache.

        This method must be called when the frame 
        requested is not stored in the caché.
        """
        if pts in self.cache:
            return self.cache[pts]
        
        # Look for the most near key frame
        key_frame_pts = self._get_nearest_keyframe_pts(pts)

        # Go to the key frame that includes it
        # but I read that it is recommended to
        # read ~100ms before the pts we want to
        # actually read so we obtain the frames
        # clean (this is important in audio)
        # TODO: This code is repeated, refactor
        pts_pad = int(0.1 / self.time_base)
        self.container.seek(
            offset = max(0, key_frame_pts - pts_pad),
            stream = self.stream
        )

        decoded = None
        for frame in self.container.decode(self.stream):
            # TODO: Could 'frame' be None (?)
            if frame.pts is None:
                continue

            # Store in cache if needed
            self._store_frame_in_cache(frame)

            """
            The 'frame.pts * frame.time_base' will give
            us the index of the frame, and actually the
            'pts' que are looking for seems to be the
            index and not a pts.

            TODO: Review all this in all the logic 
            please.
            """
            if frame.pts >= pts:
                decoded = self.cache[frame.pts]
                break

        # TODO: Is this working? We need previous 
        # frames to be able to decode...
        return decoded

    # TODO: I'm not using this method...
    def get_frame(
        self,
        index: int
    ) -> Union[VideoFrame, AudioFrame]:
        """
        Get the frame with the given 'index' from
        the cache.
        """
        # TODO: Maybe we can accept 'pts' also
        pts = index_to_pts(index, self.time_base, self.fps)

        return (
            self.cache[pts]
            if pts in self.cache else
            self.get_frame_from_pts(pts)
        )
    
    def get_frame_from_t(
        self,
        t: Union[int, float, Fraction]
    ) -> Union[VideoFrame, AudioFrame]:
        """
        Get the frame with the given 't' time moment
        from the cache.
        """
        return self.get_frame_from_pts(T(t, self.time_base).truncated_pts)

    def get_frames(
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
        # We use the cache as iterator if all the frames
        # requested are stored there
        # TODO: I think this is not ok... I will never
        # have all the pts form here stored, as they come
        # from 't' that is different...

        """
        Feel free to move this explanation to other
        place, its about the duration.

        The stream 'duration' parameter is measured
        on ticks, the amount of ticks that the
        stream lasts. Here below is an example:

        - Duration raw: 529200
        - Time base: 1/44100
        - Duration (seconds): 12.0
        """

        # The 'duration' is on pts ticks
        duration = float(self.stream.duration * self.time_base)
        # TODO: I think it would be better to
        # receive and work with pts instead of
        # 't' time moments...
        # pts_list = [
        #     t_to_pts(t, self.time_base)
        #     for t in T.get_frame_indexes(duration, self.fps, start, end)
        # ]

        # if all(
        #     pts in self.cache
        #     for pts in pts_list
        # ):
        #     for pts in pts_list:
        #         yield self.cache[pts]

        # If not all, we ignore the cache because we
        # need to decode and they are all consecutive
        start = T(start, self.time_base).truncated_pts
        end = (
            T(end, self.time_base).truncated_pts
            if end is not None else
            None
        )
        key_frame_pts = self._get_nearest_keyframe_pts(start)

        # Go to the key frame that includes it
        # but I read that it is recommended to
        # read ~100ms before the pts we want to
        # actually read so we obtain the frames
        # clean (this is important in audio)
        # TODO: This code is repeated, refactor
        pts_pad = int(0.1 / self.time_base)
        self.container.seek(
            offset = max(0, key_frame_pts - pts_pad),
            stream = self.stream
        )

        for packet in self.container.demux(self.stream):
            for frame in packet.decode():
                if frame.pts is None:
                    continue

                # We store all the frames in cache
                self._store_frame_in_cache(frame)

                frame_end_pts = frame.pts + int(frame.samples * (1 / self.stream.sample_rate) / self.time_base)
                #frame_end_pts = frame.pts + int(frame.samples)
                #frame_end_pts = frame.pts + int(frame.samples / (self.stream.sample_rate * self.time_base))

                # For the next comments imagine we are looking
                # for the [1.0, 2.0) audio time range
                # Previous frame and nothing is inside
                if frame_end_pts <= start:
                    # From 0.25 to 1.0
                    continue

                # We finished, nothing is inside and its after
                if (
                    end is not None and
                    frame.pts >= end
                ):
                    # From 2.0 to 2.75
                    return

                # We need: from 1 to 2
                # Audio is:
                #   - from 0 to 0.75    (Not included, omit)
                #   - from 0.5 to 1.5   (Included, take 1.0 to 1.5)
                #   - from 0.5 to 2.5   (Included, take 1.0 to 2.0)
                #   - from 1.25 to 1.5  (Included, take 1.25 to 1.5)
                #   - from 1.25 to 2.5  (Included, take 1.25 to 2.0)
                #   - from 2.5 to 3.5   (Not included, omit)
                
                # Here below, at least a part is inside
                if (
                    frame.pts < start and
                    frame_end_pts > start
                ):
                    # A part at the end is included
                    end_time = (
                        # From 0.5 to 1.5 0> take 1.0 to 1.5
                        frame_end_pts
                        if frame_end_pts <= end else
                        # From 0.5 to 2.5 => take 1.0 to 2.0
                        end
                    )
                    #print('A part at the end is included.')
                    # TODO: I'm using too much 'pts_to_t'
                    frame = trim_audio_frame_pts(
                        frame = frame,
                        start_pts = start,
                        end_pts = end_time,
                        time_base = self.time_base
                    )
                elif (
                    frame.pts >= start and
                    frame.pts < end
                ):
                    end_time = (
                        # From 1.25 to 1.5 => take 1.25 to 1.5
                        frame_end_pts
                        if frame_end_pts <= end else
                        # From 1.25 to 2.5 => take 1.25 to 2.0
                        end
                    )
                    # A part at the begining is included
                    #print('A part at the begining is included.')
                    # TODO: I'm using too much 'pts_to_t'
                    frame = trim_audio_frame_pts(
                        frame = frame,
                        start_pts = frame.pts,
                        end_pts = end_time,
                        time_base = self.time_base
                    )

                # If the whole frame is in, past as it is
                
                # TODO: Maybe send a @dataclass instead (?)
                # TODO: Do I really need these 't' and 'index' (?)
                yield (
                    frame,
                    pts_to_t(frame.pts, self.time_base),
                    pts_to_index(frame.pts, self.time_base, self.fps)
                )
    
    def clear(
        self
    ) -> 'VideoFrameCache':
        """
        Clear the cache by removing all the items.
        """
        self.cache.clear()

        return self
    

# TODO: Move this to a utils when refactored
def trim_audio_frame_pts(
    frame: av.AudioFrame,
    start_pts: int,
    end_pts: int,
    time_base
) -> av.AudioFrame:
    """
    Recorta un AudioFrame para quedarse solo con la parte entre [start_pts, end_pts] en ticks (PTS).
    """
    samples = frame.to_ndarray()  # (channels, n_samples)
    n_channels, n_samples = samples.shape
    sr = frame.sample_rate

    #frame_end_pts = frame.pts + int((n_samples / sr) / time_base)
    # TODO: This could be wrong
    frame_end_pts = frame.pts + int(frame.samples)

    # solapamiento en PTS
    cut_start_pts = max(frame.pts, start_pts)
    cut_end_pts = min(frame_end_pts, end_pts)

    if cut_start_pts >= cut_end_pts:
        raise Exception('Oops...')
        return None  # no hay solapamiento

    # convertir a índices de samples (en ticks → segundos → samples)
    cut_start_time = (cut_start_pts - frame.pts) * time_base
    cut_end_time = (cut_end_pts - frame.pts) * time_base

    start_idx = int(cut_start_time * sr)
    end_idx = int(cut_end_time * sr)

    # print(
    #     f"cutting [{frame.pts}, {frame_end_pts}] "
    #     f"to [{cut_start_pts}, {cut_end_pts}] "
    #     f"({start_idx}:{end_idx} / {frame.samples})"
    #     #f"({start_idx}:{end_idx} / {n_samples})"
    # )

    cut_samples = samples[:, start_idx:end_idx]

    # crear nuevo AudioFrame
    new_frame = av.AudioFrame.from_ndarray(cut_samples, format=frame.format, layout=frame.layout)
    new_frame.sample_rate = sr

    # ajustar PTS → corresponde al inicio real del recorte
    new_frame.pts = cut_start_pts
    new_frame.time_base = time_base

    return new_frame



def trim_audio_frame_t(
    frame: av.AudioFrame,
    start_time: float,
    end_time: float,
    time_base
) -> av.AudioFrame:
    """
    Recorta un AudioFrame para quedarse solo con la parte entre [start_time, end_time] en segundos.
    """
    samples = frame.to_ndarray()  # (channels, n_samples)
    n_channels, n_samples = samples.shape
    sr = frame.sample_rate

    frame_start = float(frame.pts * time_base)
    frame_end = frame_start + (n_samples / sr)

    # calcular solapamiento en segundos
    cut_start = max(frame_start, start_time)
    cut_end = min(frame_end, end_time)

    if cut_start >= cut_end:
        return None  # no hay solapamiento

    # convertir a índices de samples
    start_idx = int((cut_start - frame_start) * sr)
    end_idx = int((cut_end - frame_start) * sr)

    # print(f'cutting [{str(frame_start)}, {str(frame_end)}] to [{str(float(start_time))}, {str(float(end_time))}] from {str(start_idx)} to {str(end_idx)} of {str(int((frame_end - frame_start) * sr))}')
    cut_samples = samples[:, start_idx:end_idx]

    # crear nuevo AudioFrame
    new_frame = av.AudioFrame.from_ndarray(cut_samples, format = frame.format, layout = frame.layout)
    new_frame.sample_rate = sr

    # ajustar PTS → corresponde al inicio real del recorte
    new_pts = int(cut_start / time_base)
    new_frame.pts = new_pts
    new_frame.time_base = time_base

    return new_frame
