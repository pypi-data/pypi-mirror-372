import subprocess
from pathlib import Path
from typing import List, Optional
import re
import json
from typing import Tuple


class FFmpegError(Exception):
    """Custom exception for FFmpeg errors."""
    pass


def extract_audio_from_video(video_path: Path, output_dir: Path, stream_indices: Optional[List[int]] = None, sample_rate: Optional[int] = None) -> List[Path]:
    """
    Extracts audio streams from a video file using ffmpeg and optionally resamples the audio.

    Parameters:
    - video_path (Path): Path to the input video file.
    - output_dir (Path): Directory where the extracted audio files will be saved.
    - stream_indices (Optional[List[int]]): List of audio stream indices to extract. If None, all audio streams are extracted.
    - sample_rate (Optional[int]): Desired sample rate for the extracted audio. If None, the original sample rate is used.

    Returns:
    - List[Path]: List of paths to the extracted audio files.

    Raises:
    - FileNotFoundError: If the video file does not exist.
    - FFmpegError: If ffmpeg encounters an error during processing.
    """
    if not video_path.exists():
        raise FileNotFoundError(f"The video file {video_path} does not exist.")
    
    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)

    audio_files = []

    if stream_indices is None:
        # Get all audio stream indices
        stream_indices = get_audio_stream_indices(video_path)

    for index in stream_indices:
        output_file = output_dir / f'audio_stream_{index}.mp3'
        command = [
            'ffmpeg', '-i', str(video_path),
            '-map', f'0:a:{index-1}',
        ]
        
        if sample_rate:
            command.extend(['-ar', str(sample_rate)])
        
        command.append(str(output_file))
        
        # Run the ffmpeg command
        try:
            subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            raise FFmpegError(f"FFmpeg error: {e.stderr.decode()}")
        
        audio_files.append(output_file)
    
    return audio_files


def get_audio_stream_indices(video_path: Path) -> List[int]:
    """
    Retrieves the indices of audio streams in a video file using ffmpeg.

    Parameters:
    - video_path (Path): Path to the input video file.

    Returns:
    - List[int]: List of audio stream indices.

    Raises:
    - FileNotFoundError: If the video file does not exist.
    - FFmpegError: If ffmpeg encounters an error during processing.
    """
    if isinstance(video_path, str):
        video_path = Path(video_path)

    if not video_path.exists():
        raise FileNotFoundError(f"The video file {video_path} does not exist.")
    
    command = ['ffmpeg', '-i', str(video_path)]
    
    try:
        result = subprocess.run(command, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        raise FFmpegError(f"FFmpeg error: {e.stderr.decode()}")
    
    stderr_output = result.stderr.decode()
    audio_indices = []
    
    for line in stderr_output.splitlines():
        if 'Stream #' in line and 'Audio:' in line:
            # Extract the stream index using a regular expression
            match = re.search(r'Stream #0:(\d+)', line)
            if match:
                stream_index = int(match.group(1))
                audio_indices.append(stream_index)
    
    return audio_indices

def get_audio_stream_info(video_path: Path) -> List[Tuple[int, Optional[str]]]:
    """
    Retrieves the indices and language tags of audio streams in a video file using ffprobe.

    Parameters:
    - video_path (Path): Path to the input video file.

    Returns:
    - List[Tuple[int, Optional[str]]]: A list of tuples, where each tuple contains
      (stream_index, language_code). language_code will be None if not found.

    Raises:
    - FileNotFoundError: If the video file does not exist.
    - FFmpegError: If ffprobe encounters an error during processing or JSON parsing.
    """
    if isinstance(video_path, str):
        video_path = Path(video_path)
        
    if not video_path.exists():
        raise FileNotFoundError(f"The video file {video_path} does not exist.")
    
    command = [
        'ffprobe',
        '-v', 'error',                 # Suppress verbose output
        '-select_streams', 'a',        # Select only audio streams
        '-show_entries', 'stream=index:stream_tags=language', # Show index and language tag
        '-of', 'json',                 # Output in JSON format
        str(video_path)
    ]
    
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        data = json.loads(result.stdout)
        
        audio_stream_info = []
        for s in data.get('streams', []):
            index = s.get('index')
            language = s.get('tags', {}).get('language')
            if index is not None:
                audio_stream_info.append((index, language))
        return audio_stream_info
    except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
        raise FFmpegError(f"FFprobe error: {e.stderr if isinstance(e, subprocess.CalledProcessError) else e}")
