"""
When we are reading from a source, the reader
has its own time base and properties. When we
are writing, the writer has different time
base and properties. We need to adjust our
writer to be able to write, because the videos
we read can be different, and the video we are
writing is defined by us. The 'time_base' is
an important property or will make ffmpeg
become crazy and deny packets (that means no
video written).
"""
from yta_video_opengl.complete.track import Track
from yta_video_opengl.video import Video
from yta_video_opengl.t import get_ts, fps_to_time_base, T
from yta_video_opengl.complete.frame_combinator import AudioFrameCombinator
from yta_validation.parameter import ParameterValidator
from av.video.frame import VideoFrame
from av.audio.frame import AudioFrame
from quicktions import Fraction
from typing import Union

import numpy as np


class Timeline:
    """
    Class to represent all the tracks that
    exist on the project and to handle the
    combination of all their frames.
    """

    @property
    def end(
        self
    ) -> Fraction:
        """
        The end of the last video of the track
        that lasts longer. This is the last time
        moment that has to be rendered.
        """
        return max(
            track.end
            for track in self.tracks
        )

    def __init__(
        self,
        size: tuple[int, int] = (1_920, 1_080),
        fps: Union[int, float, Fraction] = 60.0,
        audio_fps: Union[int, Fraction] = 44_100.0, # 48_000.0 for aac
        # TODO: I don't like this name
        # TODO: Where does this come from (?)
        audio_samples_per_frame: int = 1024
    ):
        # TODO: By now we are using just two video
        # tracks to test the composition
        # TODO: We need to be careful with the
        # priority, by now its defined by its
        # position in the array
        self.tracks: list[Track] = [
            Track(
                size = size,
                fps = fps,
                audio_fps = audio_fps,
                # TODO: I need more info about the audio
                # I think
                audio_samples_per_frame = audio_samples_per_frame
            ),
            Track(
                size = size,
                fps = fps,
                audio_fps = audio_fps,
                # TODO: I need more info about the audio
                # I think
                audio_samples_per_frame = audio_samples_per_frame
            )
        ]
        """
        All the video tracks we are handling.
        """
        # TODO: Handle the other properties
        self.size = size
        self.fps = fps
        self.audio_fps = audio_fps

    # TODO: Create 'add_track' method, but by now
    # we hare handling only one
    def add_video(
        self,
        video: Video,
        t: Union[int, float, Fraction],
        # TODO: This is for testing, it has to
        # disappear
        do_use_second_track: bool = False
    ) -> 'Timeline':
        """
        Add the provided 'video' to the timeline,
        starting at the provided 't' time moment.

        TODO: The 'do_use_second_track' parameter
        is temporary.
        """
        # TODO: This is temporary logic by now 
        # just to be able to test mixing frames
        # from 2 different tracks at the same
        # time
        index = 1 * do_use_second_track

        self.tracks[index].add_video(video, t)

        return self
    
    # TODO: This method is not for the Track but
    # for the timeline, as one track can only
    # have consecutive elements
    def get_frame_at(
        self,
        t: Union[int, float, Fraction]
    ) -> 'VideoFrame':
        """
        Get all the frames that are played at the
        't' time provided, but combined in one.
        """
        frames = (
            track.get_frame_at(t)
            for track in self.tracks
        )
        # TODO: Here I receive black frames because
        # it was empty, but I don't have a way to
        # detect those black empty frames because
        # they are just VideoFrame instances... I
        # need a way to know so I can skip them if
        # other frame in other track, or to know if
        # I want them as transparent or something

        # TODO: This is just a test function
        from yta_video_opengl.complete.frame_combinator import VideoFrameCombinator

        # TODO: Combinate frames, we force them to
        # rgb24 to obtain them with the same shape,
        # but maybe we have to change this because
        # we also need to handle alphas
        output_frame = next(frames).to_ndarray(format = 'rgb24')
        for frame in frames:
            # Combine them
            # TODO: We need to ignore the frames that
            # are just empty black frames and use them
            # not in the combination process
            # TODO: What about the 'format' (?)
            output_frame = VideoFrameCombinator.blend_add(output_frame, frame.to_ndarray(format = 'rgb24'))

        # TODO: How to build this VideoFrame correctly
        # and what about the 'format' (?)
        # We don't handle pts here, just the image
        return VideoFrame.from_ndarray(output_frame, format = 'rgb24')
    
    def get_audio_frames_at(
        self,
        t: float
    ):
        audio_frames = []
        """
        Matrix in which the rows are the different
        tracks we have, and the column includes all
        the audio frames for this 't' time moment
        for the track of that row. We can have more
        than one frame per column per row (track)
        but we need a single frame to combine all
        the tracks.
        """
        # TODO: What if the different audio streams
        # have also different fps (?)
        for track in self.tracks:
            # TODO: Make this work properly
            audio_frames.append(list(track.get_audio_frames_at(t)))
            # TODO: We need to ignore the frames that
            # are just empty black frames and use them
            # not in the combination process

        # We need only 1 single audio frame per column
        collapsed = [
            concatenate_audio_frames(frames)
            for frames in audio_frames
        ]

        # Now, mix column by column (track by track)
        # TODO: I do this to have an iterator, but 
        # maybe we need more than one single audio
        # frame because of the size at the original
        # video or something...
        frames = [
            AudioFrameCombinator.sum_tracks_frames(collapsed, self.audio_fps)
        ]

        for audio_frame in frames:
            yield audio_frame
            
    def render(
        self,
        filename: str,
        start: Union[int, float, Fraction] = 0.0,
        end: Union[int, float, Fraction, None] = None
    ) -> 'Timeline':
        """
        Render the time range in between the given
        'start' and 'end' and store the result with
        the also provided 'fillename'.

        If no 'start' and 'end' provided, the whole
        project will be rendered.
        """
        ParameterValidator.validate_mandatory_string('filename', filename, do_accept_empty = False)
        ParameterValidator.validate_mandatory_positive_number('start', start, do_include_zero = True)
        ParameterValidator.validate_positive_number('end', end, do_include_zero = False)

        # TODO: Limitate 'end' a bit...
        end = (
            self.end
            if end is None else
            end
        )

        if start >= end:
            raise Exception('The provided "start" cannot be greater or equal to the "end" provided.')

        from yta_video_opengl.writer import VideoWriter

        writer = VideoWriter('test_files/output_render.mp4')
        # TODO: This has to be dynamic according to the
        # video we are writing
        writer.set_video_stream(
            codec_name = 'h264',
            fps = self.fps,
            size = self.size,
            pixel_format = 'yuv420p'
        )
        
        writer.set_audio_stream(
            codec_name = 'aac',
            fps = self.audio_fps
        )

        time_base = fps_to_time_base(self.fps)
        audio_time_base = fps_to_time_base(self.audio_fps)

        """
        We are trying to render this:
        -----------------------------
        [0 a 0.5) => Frames negros
        [0.5 a 1.25) => [0.25 a 1.0) de Video1
        [1.25 a 1.75) => Frames negros
        [1.75 a 2.25) => [0.25 a 0.75) de Video1
        [2.25 a 3.0) => Frames negros
        [3.0 a 3.75) => [2.25 a 3.0) de Video2
        """
        
        audio_pts = 0
        for t in get_ts(start, end, self.fps):
            frame = self.get_frame_at(t)

            print(f'Getting t:{str(float(t))}')
            #print(frame)

            # We need to adjust our output elements to be
            # consecutive and with the right values
            # TODO: We are using int() for fps but its float...
            frame.time_base = time_base
            #frame.pts = int(video_frame_index / frame.time_base)
            frame.pts = T(t, time_base).truncated_pts

            # TODO: We need to handle the audio
            writer.mux_video_frame(
                frame = frame
            )

            #print(f'    [VIDEO] Here in t:{str(t)} -> pts:{str(frame.pts)} - dts:{str(frame.dts)}')

            # TODO: Uncomment all this below for the audio
            num_of_audio_frames = 0
            for audio_frame in self.get_audio_frames_at(t):
                # TODO: The track gives us empty (black)
                # frames by default but maybe we need a
                # @dataclass in the middle to handle if
                # we want transparent frames or not and/or
                # to detect them here because, if not,
                # they are just simple VideoFrames and we
                # don't know they are 'empty' frames

                # We need to adjust our output elements to be
                # consecutive and with the right values
                # TODO: We are using int() for fps but its float...
                audio_frame.time_base = audio_time_base
                #audio_frame.pts = int(audio_frame_index / audio_frame.time_base)
                audio_frame.pts = audio_pts
                # We increment for the next iteration
                audio_pts += audio_frame.samples
                #audio_frame.pts = int(t + (audio_frame_index * audio_frame.time_base) / audio_frame.time_base)

                #print(f'[AUDIO] Here in t:{str(t)} -> pts:{str(audio_frame.pts)} - dts:{str(audio_frame.dts)}')

                #num_of_audio_frames += 1
                #print(audio_frame)
                writer.mux_audio_frame(audio_frame)
            #print(f'Num of audio frames: {str(num_of_audio_frames)}')

        writer.mux_video_frame(None)
        writer.mux_audio_frame(None)
        writer.output.close()


# TODO: I don't know where to put this
# method because if a bit special
# TODO: Refactor and move please
def concatenate_audio_frames(
    frames: list[AudioFrame]
) -> AudioFrame:
    """
    Combina varios AudioFrames consecutivos en uno solo.
    - Convierte a float32
    - Concatena muestras a lo largo del tiempo
    - Devuelve un AudioFrame nuevo
    """
    if not frames:
        # TODO: This should not happen
        return None
    
    if len(frames) == 1:
        return frames[0]

    # Verificamos consistencia básica
    sample_rate = frames[0].sample_rate
    layout = frames[0].layout.name
    channels = frames[0].layout.channels

    arrays = []
    for f in frames:
        if f.sample_rate != sample_rate or f.layout.name != layout:
            raise ValueError("Los frames deben tener mismo sample_rate y layout")

        # arr = f.to_ndarray()  # (channels, samples)
        # if arr.dtype == np.int16:
        #     arr = arr.astype(np.float32) / 32768.0
        # elif arr.dtype != np.float32:
        #     arr = arr.astype(np.float32)

        arrays.append(f.to_ndarray())

    # Concatenamos por eje de samples
    combined = np.concatenate(arrays, axis = 1)

    # Creamos un frame nuevo
    out = AudioFrame.from_ndarray(combined, format = frames[0].format, layout = layout)
    out.sample_rate = sample_rate

    return out