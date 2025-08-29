from yta_video_ffmpeg.flag import FfmpegFlag
from yta_video_ffmpeg.command import FfmpegCommand
from yta_image_utils.resize import get_cropping_points_to_keep_aspect_ratio
from yta_video_utils.dimensions import get_video_size
from yta_positioning.coordinate import NORMALIZATION_MAX_VALUE, NORMALIZATION_MIN_VALUE
from yta_validation import PythonValidator
from yta_validation.parameter import ParameterValidator
from yta_file.handler import FileHandler
from yta_constants.file import FileType
from yta_constants.video import FfmpegAudioCodec, FfmpegFilter, FfmpegPixelFormat, FfmpegVideoCodec, FfmpegVideoFormat
from yta_programming.output import Output
from yta_temp import Temp
from typing import Union
from subprocess import run


class FfmpegHandler:
    """
    Class to simplify and encapsulate ffmpeg functionality.
    """

    @staticmethod
    def validate_video_filename(
        filename: str
    ):
        """
        Validate if the provided 'filename' parameter is
        a string and a valid video file (based on its
        extension).
        """
        ParameterValidator.validate_mandatory_string('video_filename', filename, do_accept_empty = False)

        # TODO: If possible (and no dependency issue) check 
        # the content to validate it is parseable as video
        if not FileHandler.is_video_file(filename):
            raise Exception('The provided "filename" is not a valid video file name.')
        
    @staticmethod
    def validate_audio_filename(
        filename: str
    ) -> None:
        """
        Validate if the provided 'filename' parameter is
        a string and a valid audio file (based on its
        extension).
        """
        ParameterValidator.validate_mandatory_string('audio_filename', filename, do_accept_empty = False)

        # TODO: If possible (and no dependency issue) check 
        # the content to validate it is parseable as audio
        if not FileHandler.is_audio_file(filename):
            raise Exception('The provided "filename" is not a valid audio file name.')

    @staticmethod
    def write_concat_file(
        filenames: str
    ) -> str:
        """
        Writes the files to concat in a temporary text file with
        the required format and returns that file filename. This
        is required to use different files as input.

        This method returns the created file filename that 
        includes the list with the 'filenames' provided ready
        to be concatenated.
        """
        text = '\n'.join(
            f"file '{filename}'"
            for filename in filenames
        )

        # TODO: Maybe this below is interesting for the 'yta_general_utils.file.writer'
        # open('concat.txt', 'w').writelines([('file %s\n' % input_path) for input_path in input_paths])
        filename = Temp.get_wip_filename('concat_ffmpeg.txt')
        FileHandler.write_str(filename, text)

        return filename

    @staticmethod
    def run_command(
        command: Union[list[FfmpegFlag, any], FfmpegCommand]
    ) -> None:
        """
        Runs the provided ffmpeg 'command'.
        """
        command = (
            FfmpegCommand(command)
            if not PythonValidator.is_instance_of(command, FfmpegCommand) else
            command
        )

        command.run()

    # TODO: Check this one below
    @staticmethod
    def get_audio_from_video_deprecated(
        video_filename: str,
        codec: FfmpegAudioCodec = None,
        output_filename: Union[str, None] = None
    ) -> str:
        """
        Exports the audio of the provided video to a local file named
        'output_filename' if provided or as a temporary file.

        # TODO: This has not been tested yet.

        Pro tip: You can read the return with AudioParser.as_audioclip
        method.

        This method returns the filename of the file that has been
        generated as a the audio of the provided video.
        """
        FfmpegHandler.validate_video_filename(video_filename)
        
        output_filename = Output.get_filename(output_filename, FileType.AUDIO)

        if codec:
            codec = FfmpegAudioCodec.to_enum(codec)

        FfmpegCommand([
            FfmpegFlag.input(video_filename),
            FfmpegFlag.audio_codec(codec) if codec else None,
            output_filename
        ]).run()

        return output_filename
    
    @staticmethod
    def get_audio_from_video(
        video_filename: str,
        output_filename: Union[str, None] = None
    ) -> str:
        """
        Exports the audio of the provided video to a local file named
        'output_filename' if provided or as a temporary file.

        Pro tip: You can read the return with AudioParser.as_audioclip
        method.

        This method returns the filename of the file that has been
        generated as a the audio of the provided video.
        """
        FfmpegHandler.validate_video_filename(video_filename)
        
        output_filename = Output.get_filename(output_filename, FileType.AUDIO)

        # TODO: Verify valid output_filename extension

        FfmpegCommand([
            FfmpegFlag.input(video_filename),
            FfmpegFlag.map('0:1'),
            output_filename
        ]).run()

        return output_filename

    @staticmethod
    def get_best_thumbnail(
        video_filename: str,
        output_filename: Union[str, None] = None
    ) -> str:
        """
        Gets the best thumbnail of the provided 'video_filename'.

        Pro tip: You can read the return with ImageParser.to_pillow
        method.

        This method returns the filename of the file that has been
        generated as a the thumbnail of the provided video.
        """
        FfmpegHandler.validate_video_filename(video_filename)

        output_filename = Output.get_filename(output_filename, FileType.IMAGE)

        FfmpegCommand([
            FfmpegFlag.input(video_filename),
            FfmpegFlag.filter(FfmpegFilter.THUMBNAIL),
            output_filename
        ]).run()

        return output_filename
    
    @staticmethod
    def concatenate_videos(
        video_filenames: str,
        output_filename: str = None
    ) -> str:
        """
        Concatenates the provided 'video_filenames' in the order in
        which they are provided.

        Using Ffmpeg is very useful when trying to concatenate similar
        videos (the ones that we create always with the same 
        specifications) because the codecs are the same so the speed
        is completely awesome.

        Pro tip: You can read the return with VideoParser.to_moviepy
        method.

        This method returns the filename of the file that has been
        generated as a concatenation of the provided ones.
        """
        for video_filename in video_filenames:
            FfmpegHandler.validate_video_filename(video_filename)

        output_filename = Output.get_filename(output_filename, FileType.VIDEO)
        concat_filename = FfmpegHandler.write_concat_file(video_filenames)

        FfmpegCommand([
            FfmpegFlag.overwrite,
            FfmpegFlag.force_format(FfmpegVideoFormat.CONCAT),
            FfmpegFlag.safe_routes(0),
            FfmpegFlag.input(concat_filename),
            FfmpegFlag.codec('copy'),
            output_filename
        ]).run()

        return output_filename
    
    @staticmethod
    def concatenate_images(
        image_filenames: str,
        frame_rate = 60,
        pixel_format: FfmpegPixelFormat = FfmpegPixelFormat.YUV420p,
        output_filename: Union[str, None] = None
    ) -> str:
        """
        Concatenates the provided 'image_filenames' in the order in
        which they are provided.

        Using Ffmpeg is very useful when trying to concatenate similar
        images because the speed is completely awesome.

        Pro tip: You can read the return with VideoParser.to_moviepy().

        This method returns the filename of the file that has been
        generated as a concatenation of the provided ones.
        """
        for image_filename in image_filenames:
            FfmpegHandler.validate_video_filename(image_filename)

        output_filename = Output.get_filename(output_filename, FileType.VIDEO)
        concat_filename = FfmpegHandler.write_concat_file(image_filenames)

        # TODO: Should we check the pixel format or give freedom (?)
        # pixel_format = FfmpegPixelFormat.to_enum(pixel_format)

        FfmpegCommand([
            FfmpegFlag.force_format(FfmpegVideoFormat.CONCAT),
            FfmpegFlag.safe_routes(0),
            FfmpegFlag.overwrite,
            FfmpegFlag.frame_rate(frame_rate),
            FfmpegFlag.input(concat_filename),
            FfmpegFlag.video_codec(FfmpegVideoCodec.QTRLE),
            FfmpegFlag.pixel_format(pixel_format), # I used 'argb' in the past
            output_filename
        ]).run()

        return output_filename

    @staticmethod
    def resize_video(
        video_filename: str,
        size: tuple,
        output_filename: Union[str, None] = None
    ) -> str:
        """
        Resize the provided 'video_filename', by keeping
        the aspect ratio (cropping if necessary), to the
        given 'size' and stores it locally as
        'output_filename'.

        This method returns the generated file filename.

        See more: 
        https://www.gumlet.com/learn/ffmpeg-resize-video/
        """
        FfmpegHandler.validate_video_filename(video_filename)
        ParameterValidator.validate_mandatory_tuple('size', size, None)
        # TODO: I think we don't need this with the 'Output.get_filename'
        ParameterValidator.validate_mandatory_string('output_filename', output_filename, do_accept_empty = False)
        
        output_filename = Output.get_filename(output_filename, FileType.VIDEO)

        # Validate that 'size' is a valid size
        # TODO: This code is a bit strange, but was refactored from the
        # original one that was in 'yta_multimedia' to remove the
        # dependency. Maybe update it?
        if not PythonValidator.is_numeric_tuple_or_list_or_array_of_2_elements_between_values(size, NORMALIZATION_MIN_VALUE, NORMALIZATION_MAX_VALUE, NORMALIZATION_MIN_VALUE, NORMALIZATION_MAX_VALUE):
            # TODO: Raise error
            raise Exception(f'The provided size parameter is not a tuple or array, or does not have 2 elements that are numbers between {str(NORMALIZATION_MIN_VALUE)} and {str(NORMALIZATION_MAX_VALUE)}.')

        w, h = get_video_size(video_filename)

        if (w, h) == size:
            # No need to resize, we just copy it to output
            FileHandler.copy_file(video_filename, output_filename)
        else:
            # First, we need to know if we need to scale it
            original_ratio = w / h
            new_ratio = size[0] / size[1]

            new_size = (
                (w * (size[1] / h), size[1])
                # Original video is wider than the expected one
                if original_ratio > new_ratio else
                # Original video is higher than the expected one
                (size[0], h * (size[0] / w))
                if original_ratio < new_ratio else
                (size[0], size[1])
            )

            tmp_filename = Temp.get_wip_filename('tmp_ffmpeg_scaling.mp4')

            # Scale to new dimensions
            FfmpegCommand([
                FfmpegFlag.input(video_filename),
                FfmpegFlag.scale_with_size(new_size),
                tmp_filename
            ]).run()

            # Now, with the new video resized, we look for the
            # cropping points we need to apply and we crop it
            top_left, _ = get_cropping_points_to_keep_aspect_ratio(new_size, size)

            # Second, we need to know if we need to crop it
            FfmpegCommand([
                FfmpegFlag.input(tmp_filename),
                FfmpegFlag.crop(size, top_left),
                FfmpegFlag.overwrite,
                output_filename
            ]).run()

        return output_filename
    
    @staticmethod
    def trim(
        video_filename: str,
        start_seconds: int,
        duration_seconds: int,
        output_filename: Union[str, None] = None
    ) -> str:
        """
        Trims the provided 'video_filename' and generates a
        shorter resource that is stored as 'output_filename'.
        This new resource will start from 'start_seconds' and
        last the provided 'duration_seconds'.

        This method returns the generated file filename.

        Thank you:
        https://www.plainlyvideos.com/blog/ffmpeg-trim-videos
        https://trac.ffmpeg.org/wiki/Seeking
        """
        FfmpegHandler.validate_video_filename(video_filename)
        ParameterValidator.validate_mandatory_positive_number('start_seconds', start_seconds, do_include_zero = True)
        ParameterValidator.validate_mandatory_positive_number('duration_seconds', duration_seconds, do_include_zero = True)
        
        output_filename = Output.get_filename(output_filename, FileType.VIDEO)

        command = FfmpegCommand([
            FfmpegFlag.seeking(start_seconds),
            FfmpegFlag.input(video_filename),
            FfmpegFlag.to(duration_seconds),
            FfmpegFlag.codec(FfmpegVideoCodec.COPY),
            FfmpegFlag.overwrite,
            output_filename
        ])
        # TODO: Remove this command when confirmed
        print(command)
        command.run()

        #ffmpeg_command = f'-ss 00:02:05 -i {video} -to 00:03:10 -c copy video-cutted-ffmpeg.mp4'
        return output_filename

    # TODO: This method must replace the one in 
    # yta_multimedia\video\audio.py > set_audio_in_video_ffmpeg
    @staticmethod
    def set_audio(
        video_filename: str,
        audio_filename: str,
        output_filename: Union[str, None] = None
    ):
        """
        TODO: This method has not been properly tested yet.

        Set the audio given in the 'audio_filename' in the also
        provided video (in 'video_filename') and creates a new
        file containing the video with the audio.

        This method returns the generated file filename.
        """
        FfmpegHandler.validate_video_filename(video_filename)
        FfmpegHandler.validate_audio_filename(audio_filename)
        # TODO: I think we don't need this with the 'Output.get_filename'
        ParameterValidator.validate_mandatory_string('output_filename', output_filename)
        
        output_filename = Output.get_filename(output_filename, FileType.VIDEO)
        
        # cls.run_command([
        #     FfmpegFlag.input(video_filename),
        #     FfmpegFlag.input(audio_filename),
        #     output_filename
        # # TODO: Unfinished
        # ])

        # TODO: Is this actually working (?)
        run(f"ffmpeg -i {video_filename} -i {audio_filename} -c:v copy -c:a aac -strict experimental -y {output_filename}")

        return output_filename
        
        # Apparently this is the equivalent command according
        # to ChatGPT, but maybe it doesn't work
        # ffmpeg -i input_video -i input_audio -c:v copy -c:a aac -strict experimental -y output_filename

        # There is also a post that says this:
        # ffmpeg -i input.mp4 -i input.mp3 -c copy -map 0:v:0 -map 1:a:0 output.mp4
        # in (https://superuser.com/a/590210)


        # # TODO: What about longer audio than video (?)
        # # TODO: This is what was being used before FFmpegHandler
        # input_video = ffmpeg.input(video_filename)
        # input_audio = ffmpeg.input(audio_filename)

        # ffmpeg.concat(input_video, input_audio, v = 1, a = 1).output(output_filename).run(overwrite_output = True)

    
    # TODO: Keep going

    # https://www.reddit.com/r/ffmpeg/comments/ks8zfs/comment/gieu7x6/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button
    # https://stackoverflow.com/questions/38368105/ffmpeg-custom-sequence-input-images/51618079#51618079
    # https://stackoverflow.com/a/66014158