"""FFProbe Plugin - Extract media file metadata"""
import subprocess
import json
from typing import Dict, Any
from datetime import datetime
from pathlib import Path
from archiverr.utils.debug import get_debugger


class FFProbePlugin:
    """Output plugin that extracts media metadata using ffprobe"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = "ffprobe"
        self.category = "output"
        self.debugger = get_debugger()
    
    def execute(self, match_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract media metadata using ffprobe.
        
        Args:
            match_data: Must contain 'input' with path and virtual flag
            
        Returns:
            {status, video, audio, container} or not_supported for virtual paths
        """
        from datetime import datetime
        start_time = datetime.now()
        
        # Get input metadata from match globals
        input_metadata = match_data.get('input', {})
        input_path = input_metadata.get('path')
        is_virtual = input_metadata.get('virtual', False)
        
        # Skip virtual paths - ffprobe cannot analyze non-existent files
        if is_virtual:
            self.debugger.debug("ffprobe", "Skipping virtual path", path=input_path)
            return self._not_supported_result()
        
        if not input_path or not Path(input_path).exists():
            return self._error_result()
        
        try:
            # Run ffprobe
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                input_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            
            if result.returncode != 0:
                return self._error_result()
            
            data = json.loads(result.stdout)
            
            self.debugger.debug("ffprobe", "Analysis complete", streams=len(data.get('streams', [])))
            
            # Parse streams
            video_stream = None
            audio_streams = []
            
            for stream in data.get('streams', []):
                if stream.get('codec_type') == 'video' and not video_stream:
                    video_stream = stream
                elif stream.get('codec_type') == 'audio':
                    audio_streams.append(stream)
            
            # Extract video info
            video = {}
            if video_stream:
                video = {
                    'codec': video_stream.get('codec_name', ''),
                    'codec_long': video_stream.get('codec_long_name', ''),
                    'profile': video_stream.get('profile', ''),
                    'level': video_stream.get('level', ''),
                    'width': video_stream.get('width', 0),
                    'height': video_stream.get('height', 0),
                    'resolution': f"{video_stream.get('height', 0)}p",
                    'aspect_ratio': video_stream.get('display_aspect_ratio', ''),
                    'bit_depth': video_stream.get('bits_per_raw_sample', 8),
                    'pix_fmt': video_stream.get('pix_fmt', ''),
                    'fps': eval(video_stream.get('r_frame_rate', '0/1').replace('/', './')),
                    'duration': float(video_stream.get('duration', 0)),
                    'bitrate': int(video_stream.get('bit_rate', 0))
                }
            
            # Extract audio info
            audio = []
            for stream in audio_streams:
                audio.append({
                    'codec': stream.get('codec_name', ''),
                    'codec_long': stream.get('codec_long_name', ''),
                    'channels': stream.get('channels', 0),
                    'channel_layout': stream.get('channel_layout', ''),
                    'sample_rate': stream.get('sample_rate', ''),
                    'bitrate': int(stream.get('bit_rate', 0)),
                    'language': stream.get('tags', {}).get('language', '')
                })
            
            # Extract container info
            format_info = data.get('format', {})
            container = {
                'format': format_info.get('format_name', ''),
                'duration': float(format_info.get('duration', 0)),
                'size': int(format_info.get('size', 0)),
                'bitrate': int(format_info.get('bit_rate', 0))
            }
            
            # Log extracted info
            if video:
                self.debugger.info("ffprobe", "Video stream found", 
                                 codec=video.get('codec'), 
                                 resolution=f"{video.get('width')}x{video.get('height')}")
            self.debugger.debug("ffprobe", "Audio streams", count=len(audio))
            self.debugger.debug("ffprobe", "Container format", format=container.get('format'))
            
            end_time = datetime.now()
            return {
                'status': {
                    'success': True,
                    'started_at': start_time.isoformat(),
                    'finished_at': end_time.isoformat(),
                    'duration_ms': int((end_time - start_time).total_seconds() * 1000)
                },
                'video': video,
                'audio': audio,
                'container': container
            }
            
        except Exception as e:
            end_time = datetime.now()
            return {
                'status': {
                    'success': False,
                    'started_at': start_time.isoformat(),
                    'finished_at': end_time.isoformat(),
                    'duration_ms': int((end_time - start_time).total_seconds() * 1000)
                },
                'video': {},
                'audio': [],
                'container': {}
            }
    
    def _error_result(self) -> Dict[str, Any]:
        """Return error result"""
        end_time = datetime.now()
        return {
            'status': {
                'success': False,
                'started_at': datetime.now().isoformat(),
                'finished_at': end_time.isoformat(),
                'duration_ms': int((end_time - datetime.now()).total_seconds() * 1000)
            },
            'video': {},
            'audio': [],
            'container': {}
        }
    
    def _not_supported_result(self) -> Dict[str, Any]:
        """Return not supported result for virtual paths"""
        now = datetime.now()
        return {
            'status': {
                'success': False,
                'not_supported': True,
                'started_at': now.isoformat(),
                'finished_at': now.isoformat(),
                'duration_ms': 0
            },
            'video': {},
            'audio': [],
            'container': {}
        }
