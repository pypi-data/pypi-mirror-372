from yta_video_opengl.complete.video_on_track import VideoOnTrack
from yta_video_opengl.video import Video
from yta_video_opengl.t import T
from yta_video_opengl.utils import audio_frames_and_remainder_per_video_frame
from yta_video_opengl.t import fps_to_time_base
from yta_video_opengl.complete.frame_generator import VideoFrameGenerator, AudioFrameGenerator
from yta_validation.parameter import ParameterValidator
from quicktions import Fraction
from typing import Union


NON_LIMITED_EMPTY_PART_END = 999
"""
A value to indicate that the empty part
has no end because it is in the last
position and there is no video after it.
"""
class _Part:
    """
    Class to represent an element that is on the
    track, that can be an empty space or a video
    (with audio).
    """

    @property
    def is_empty_part(
        self
    ) -> bool:
        """
        Flag to indicate if the part is an empty part,
        which means that there is no video associated
        but an empty space.
        """
        return self.video is None

    def __init__(
        self,
        track: 'Track',
        start: Union[int, float, Fraction],
        end: Union[int, float, Fraction],
        video: Union[VideoOnTrack, None] = None
    ):
        ParameterValidator.validate_mandatory_positive_number('start', start, do_include_zero = True)
        ParameterValidator.validate_mandatory_positive_number('end', end, do_include_zero = False)
        ParameterValidator.validate_instance_of('video', video, VideoOnTrack)

        self._track: Track = track
        """
        The instance of the track this part belongs
        to.
        """
        # TODO: I would like to avoid this 2 instances
        # here, and I think I've done it with static
        # properties in other project, but as I don't
        # remember how and where by now, here it is...
        self._video_frame_generator: VideoFrameGenerator = VideoFrameGenerator()
        """
        Useful internal tool to generate background
        frames for the empty parts.
        """
        self._audio_frame_generator: AudioFrameGenerator = AudioFrameGenerator()
        """
        Useful internal tool to generate silent
        audio frames for the empty parts.
        """
        self.start: Fraction = Fraction(start)
        """
        The start 't' time moment of the part.
        """
        self.end: Fraction = Fraction(end)
        """
        The end 't' time moment of the part.
        """
        self.video: Union[VideoOnTrack, None] = video
        """
        The video associated, if existing, or
        None if it is an empty space that we need
        to fulfill with a black background and
        silent audio.
        """

    def get_frame_at(
        self,
        t: Union[int, float, Fraction]
    ) -> 'VideoFrame':
        """
        Get the frame that must be displayed at 
        the given 't' time moment.
        """
        if self.is_empty_part:
            # TODO: What about the 'format' (?)
            # TODO: Maybe I shouldn't set the 'time_base'
            # here and do it just in the Timeline 'render'
            #return get_black_background_video_frame(self._track.size)
            # TODO: This 'time_base' maybe has to be related
            # to a Timeline general 'time_base' and not the fps
            return self._video_frame_generator.background.full_black(
                size = self._track.size,
                time_base = fps_to_time_base(self._track.fps)
            )

        frame = self.video.get_frame_at(t)

        # TODO: This should not happen because of
        # the way we handle the videos here but the
        # video could send us a None frame here, so
        # do we raise exception (?)
        if frame is None:
            #frame = get_black_background_video_frame(self._track.size)
            # TODO: By now I'm raising exception to check if
            # this happens or not because I think it would
            # be malfunctioning
            raise Exception(f'Video is returning None video frame at t={str(t)}.')
        
        return frame
    
    def get_audio_frames_at(
        self,
        t: Union[int, float, Fraction]
    ):
        if not self.is_empty_part:
            frames = self.video.get_audio_frames_at(t)
        else:
            # TODO: Transform this below to a utils in
            # which I obtain the array directly
            # Check many full and partial silent frames we need
            number_of_frames, number_of_remaining_samples = audio_frames_and_remainder_per_video_frame(
                video_fps = self._track.fps,
                sample_rate = self._track.audio_fps,
                number_of_samples_per_audio_frame = self._track.audio_samples_per_frame
            )

            # TODO: I need to set the pts, but here (?)
            # The complete silent frames we need
            frames = (
                [
                    self._audio_frame_generator.silent(
                        sample_rate = self._track.audio_fps,
                        # TODO: Check where do we get this value from
                        layout = 'stereo',
                        number_of_samples = self._track.audio_samples_per_frame,
                        # TODO: Check where do we get this value from
                        format = 'fltp',
                        pts = None,
                        time_base = None
                    )
                ] * number_of_frames
                if number_of_frames > 0 else
                []
            )

            # The remaining partial silent frames we need
            if number_of_remaining_samples > 0:
                frames.append(
                    self._audio_frame_generator.silent(
                        sample_rate = self._track.audio_fps,
                        # TODO: Check where do we get this value from
                        layout = 'stereo',
                        number_of_samples = number_of_remaining_samples,
                        # TODO: Check where do we get this value from
                        format = 'fltp',
                        pts = None,
                        time_base = None
                    )
                )

        for frame in frames:
            yield frame

# TODO: I don't like using t as float,
# we need to implement fractions.Fraction
# TODO: This is called Track but it is
# handling videos only. Should I have
# VideoTrack and AudioTrack (?)
class Track:
    """
    Class to represent a track in which we place
    videos, images and audio to build a video
    project.
    """

    @property
    def parts(
        self
    ) -> list[_Part]:
        """
        The list of parts that build this track,
        but with the empty parts detected to 
        be fulfilled with black frames and silent
        audios.

        A part can be a video or an empty space.
        """
        if (
            not hasattr(self, '_parts') or
            self._parts is None
        ):
            self._recalculate_parts()

        return self._parts

    @property
    def end(
        self
    ) -> Fraction:
        """
        The end of the last video of this track,
        which is also the end of the track. This
        is the last time moment that has to be
        rendered.
        """
        return Fraction(
            0.0
            if len(self.videos) == 0 else
            max(
                video.end
                for video in self.videos
            )
        )
    
    @property
    def videos(
        self
    ) -> list[VideoOnTrack]:
        """
        The list of videos we have in the track
        but ordered using the 'start' attribute
        from first to last.
        """
        return sorted(self._videos, key = lambda video: video.start)

    def __init__(
        self,
        # TODO: I need the general settings of the
        # project to be able to make audio also, not
        # only the empty frames
        size: tuple[int, int],
        fps: float,
        audio_fps: float,
        # TODO: Where does it come from (?)
        audio_samples_per_frame: int
    ):
        self._videos: list[VideoOnTrack] = []
        """
        The list of 'VideoOnTrack' instances that
        must play on this track.
        """
        self.size: tuple[int, int] = size
        """
        The size of the videos of this track.
        """
        self.fps: float = float(fps)
        """
        The fps of the track, needed to calculate
        the base t time moments to be precise and
        to obtain or generate the frames.
        """
        self.audio_fps: float = float(audio_fps)
        """
        The fps of the audio track, needed to 
        generate silent audios for the empty parts.
        """
        self.audio_samples_per_frame: int = audio_samples_per_frame
        """
        The number of samples per audio frame.
        """

    def _is_free(
        self,
        start: Union[int, float, Fraction],
        end: Union[int, float, Fraction]
    ) -> bool:
        """
        Check if the time range in between the 
        'start' and 'end' time given is free or
        there is some video playing at any moment.
        """
        return not any(
            (
                video.video.start < end and
                video.video.end > start
            )
            for video in self.videos
        )
    
    def _get_part_at_t(
        self,
        t: Union[int, float, Fraction]
    ) -> _Part:
        """
        Get the part at the given 't' time
        moment, that will always exist because
        we have an special non ended last 
        empty part that would be returned if
        accessing to an empty 't'.
        """
        for part in self.parts:
            if part.start <= t < part.end:
                return part
            
        # TODO: This will only happen if they are
        # asking for a value greater than the
        # NON_LIMITED_EMPTY_PART_END...
        raise Exception('NON_LIMITED_EMPTY_PART_END exceeded.')
        return None

    def get_frame_at(
        self,
        t: Union[int, float, Fraction]
    ) -> 'VideoFrame':
        """
        Get the frame that must be displayed at
        the 't' time moment provided, which is
        a frame from the video audio that is
        being played at that time moment.

        Remember, this 't' time moment provided
        is about the track, and we make the
        conversion to the actual video 't' to
        get the frame.
        """
        # TODO: What if the frame, that comes from
        # a video, doesn't have the expected size (?)
        return self._get_part_at_t(t).get_frame_at(t)
    
    # TODO: This is not working well...
    def get_audio_frames_at(
        self,
        t: Union[int, float, Fraction]
    ):
        """
        Get the sequence of audio frames that
        must be displayed at the 't' time 
        moment provided, which the collection
        of audio frames corresponding to the
        video frame that is being played at
        that time moment.

        Remember, this 't' time moment provided
        is about the track, and we make the
        conversion to the actual video 't' to
        get the frame.

        This is useful when we want to write a
        video frame with its audio, so we obtain
        all the audio frames associated to it
        (remember that a video frame is associated
        with more than 1 audio frame).
        """
        for frame in self._get_part_at_t(t).get_audio_frames_at(t):
            yield frame
    
    def add_video(
        self,
        video: Video,
        t: Union[int, float, Fraction, None] = None
    ) -> 'Track':
        """
        Add the 'video' provided to the track. If
        a 't' time moment is provided, the video
        will be added to that time moment if 
        possible. If there is no other video 
        placed in the time gap between the given
        't' and the provided 'video' duration, it
        will be added succesfully. In the other
        case, an exception will be raised.

        If 't' is None, the first available 't'
        time moment will be used, that will be 0.0
        if no video, or the end of the last video.
        """
        ParameterValidator.validate_mandatory_instance_of('video', video, Video)
        ParameterValidator.validate_positive_number('t', t, do_include_zero = True)

        if t is not None:
            # TODO: We can have many different strategies
            # that we could define in the '__init__' maybe
            t: T = T.from_fps(t, self.fps)
            if not self._is_free(t.truncated, t.next(1).truncated):
                raise Exception('The video cannot be added at the "t" time moment, something blocks it.')
            t = t.truncated
        else:
            t = self.end
        
        self._videos.append(VideoOnTrack(
            video,
            t
        ))

        self._recalculate_parts()

        # TODO: Maybe return the VideoOnTrack instead (?)
        return self
    
    def _recalculate_parts(
        self
    ) -> 'Track':
        """
        Check the track and get all the parts. A
        part can be empty (non video nor audio on
        that time period, which means black 
        background and silence audio), or a video
        with (or without) audio.
        """
        parts = []
        cursor = 0.0

        for video in self.videos:
            # Empty space between cursor and start of
            # the next clip
            if video.start > cursor:
                parts.append(_Part(
                    track = self,
                    start = cursor,
                    end = video.start,
                    video = None
                ))

            # The video itself
            parts.append(_Part(
                track = self,
                start = video.start,
                end = video.end,
                video = video
            ))
            
            cursor = video.end

        # Add the non limited last empty part
        parts.append(_Part(
            track = self,
            start = cursor,
            end = NON_LIMITED_EMPTY_PART_END,
            video = None
        ))

        self._parts = parts

        return self