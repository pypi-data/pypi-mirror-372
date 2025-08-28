"""
If we have a video placed in a timeline,
starting at the t=2s and the video lasts
2 seconds, the `t` time range in which the
video is playing is `[2s, 4s]`, so here 
you have some examples with global `t` 
values:
- `t=1`, the video is not playing because
it starts at `t=2`
- `t=3`, the video is playing, it started
at `t=2` and it has been playing during 1s
- `t=5`, the video is not playing because
it started at `t=2`, lasting 2s, so it
finished at `t=4`
"""
from yta_video_opengl.video import Video
from yta_validation.parameter import ParameterValidator
from av.video.frame import VideoFrame
from av.audio.frame import AudioFrame
from quicktions import Fraction
from typing import Union


class VideoOnTrack:
    """
    A video in the timeline.
    """

    @property
    def end(
        self
    ) -> Fraction:
        """
        The end time moment 't' of the video once
        once its been placed on the track, which
        is affected by the video duration and its
        start time moment on the track.

        This end is different from the video end.
        """
        return self.start + self.video.duration

    def __init__(
        self,
        video: Video,
        start: Union[int, float, Fraction] = 0.0
    ):
        ParameterValidator.validate_mandatory_instance_of('video', video, Video)
        ParameterValidator.validate_mandatory_positive_number('start', start, do_include_zero = True)

        self.video: Video = video
        """
        The video source, with all its properties,
        that is placed in the timeline.
        """
        self.start: Fraction = Fraction(start)
        """
        The time moment in which the video should
        start playing, within the timeline.

        This is the time respect to the timeline
        and its different from the video `start`
        time, which is related to the file.
        """

    def _get_video_t(
        self,
        t: Union[int, float, Fraction]
    ) -> float:
        """
        The video 't' time moment for the given
        global 't' time moment. This 't' is the one
        to use inside the video content to display
        its frame.
        """
        # TODO: Use 'T' here to be precise or the
        # argument itself must be precise (?)
        return t - self.start

    def is_playing(
        self,
        t: Union[int, float, Fraction]
    ) -> bool:
        """
        Check if this video is playing at the general
        't' time moment, which is a global time moment
        for the whole project.
        """
        # TODO: Use 'T' here to be precise or the
        # argument itself must be precise (?)
        return self.start <= t < self.end

    def get_frame_at(
        self,
        t: Union[int, float, Fraction]
    ) -> Union[VideoFrame, None]:
        """
        Get the frame for the 't' time moment provided,
        that could be None if the video is not playing
        in that moment.
        """
        # TODO: Use 'T' here to be precise or the
        # argument itself must be precise (?)
        return (
            self.video.get_frame_from_t(self._get_video_t(t))
            if self.is_playing(t) else
            None
        )
    
    def get_audio_frame_at(
        self,
        t: Union[int, float, Fraction]
    ) -> Union[AudioFrame, None]:
        """
        Get the audio frame for the 't' time moment
        provided, that could be None if the video
        is not playing in that moment.
        """
        # TODO: Use 'T' here to be precise or the
        # argument itself must be precise (?)
        return (
            self.video.get_audio_frame_from_t(self._get_video_t(t))
            if self.is_playing(t) else
            None
        )
    
    def get_audio_frames_at(
        self,
        t: Union[int, float, Fraction]
    ) -> Union[any, None]:
        """
        Get the audio frames that must be played at
        the 't' time moment provided, that could be
        None if the video is not playing at that
        moment.

        This method will return None if no audio
        frames found in that 't' time moment, or an
        iterator if yes.
        """
        # TODO: Use 'T' here to be precise or the
        # argument itself must be precise (?)
        frames = (
            self.video.get_audio_frames_from_t(self._get_video_t(t))
            if self.is_playing(t) else
            []
        )

        for frame in frames:
            yield frame

        # # TODO: This was a simple return before
        # return (
        #     self.video.reader.get_audio_frames_from_t(self._get_video_t(t))
        #     if self.is_playing(t) else
        #     None
        # )