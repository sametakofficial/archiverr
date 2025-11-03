# integrations/ffprobe/client.py
from __future__ import annotations
import json
import subprocess
from typing import Any, Dict, List
from pathlib import Path
from archiverr.core.matcher.api_normalizer import normalize

FFPROBE_ENTITY = "media"  # Custom entity for FFProbe

class FFProbeClient:
    """FFProbe integration - analyzes local media files"""
    
    def __init__(self, timeout: int = 15):
        self.timeout = timeout
    
    def probe_file(self, file_path: str, use_cache: bool = True) -> Dict[str, Any]:
        """
        Analyze media file with ffprobe and return normalized format.
        
        Returns normalized structure with:
        - entity: "media"
        - ids: {"file_path": str}
        - container: {...}
        - video: {...}
        - audio: [...]
        - subtitles: [...]
        - extras: raw ffprobe output
        """
        cpath = self._cache_path_for_media(file_path)
        
        # Try cache first
        if use_cache and cpath.is_file():
            try:
                cached = json.loads(cpath.read_text(encoding="utf-8", errors="ignore"))
                return self._normalize_ffprobe(cached, file_path)
            except Exception:
                pass
        
        # Run ffprobe
        try:
            raw = self._run_ffprobe(file_path)
        except Exception:
            raw = {}
        
        # Cache result
        try:
            cpath.write_text(json.dumps(raw, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:
            pass
        
        return self._normalize_ffprobe(raw, file_path)
    
    def _run_ffprobe(self, path: str) -> Dict[str, Any]:
        """Execute ffprobe command"""
        cmd = ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", path]
        out = subprocess.check_output(cmd, timeout=self.timeout)
        return json.loads(out.decode("utf-8", "ignore")) or {}
    
    def _cache_path_for_media(self, path: str) -> Path:
        """Generate cache file path"""
        p = Path(path)
        return p.with_name(p.stem + "-ffmpeg.nfo")
    
    def _normalize_ffprobe(self, raw: Dict[str, Any], file_path: str) -> Dict[str, Any]:
        """Normalize ffprobe output to standard format"""
        streams: List[Dict[str, Any]] = raw.get("streams") or []
        format_info = raw.get("format") or {}
        
        # Video stream
        video_stream = next((s for s in streams if (s.get("codec_type") or "").lower() == "video"), None)
        
        # Audio streams
        audio_streams = [s for s in streams if (s.get("codec_type") or "").lower() == "audio"]
        
        # Subtitle streams
        subtitle_streams = [s for s in streams if (s.get("codec_type") or "").lower() == "subtitle"]
        
        # Normalize video
        video = None
        if video_stream:
            width = video_stream.get("width")
            height = video_stream.get("height")
            resolution = self._calculate_resolution(height)
            
            video = {
                "codec": video_stream.get("codec_name"),
                "codec_long": video_stream.get("codec_long_name"),
                "profile": video_stream.get("profile"),
                "width": width,
                "height": height,
                "resolution": resolution,
                "aspect_ratio": video_stream.get("display_aspect_ratio"),
                "pix_fmt": video_stream.get("pix_fmt"),
                "bit_rate": int(video_stream.get("bit_rate", 0)) if video_stream.get("bit_rate") else None,
                "fps": self._parse_fps(video_stream.get("r_frame_rate")),
                "color_space": video_stream.get("color_space"),
                "color_transfer": video_stream.get("color_transfer"),
                "color_primaries": video_stream.get("color_primaries"),
                "hdr": self._detect_hdr(video_stream)
            }
        
        # Normalize audio
        audio = []
        for i, a in enumerate(audio_streams):
            tags = a.get("tags") or {}
            lang = tags.get("language") or tags.get("LANGUAGE") or tags.get("lang")
            
            audio.append({
                "index": i + 1,
                "codec": a.get("codec_name"),
                "codec_long": a.get("codec_long_name"),
                "profile": a.get("profile"),
                "language": lang,
                "channels": a.get("channels"),
                "channel_layout": a.get("channel_layout"),
                "sample_rate": int(a.get("sample_rate", 0)) if a.get("sample_rate") else None,
                "bit_rate": int(a.get("bit_rate", 0)) if a.get("bit_rate") else None,
                "title": tags.get("title") or tags.get("TITLE")
            })
        
        # Normalize subtitles
        subtitles = []
        for i, s in enumerate(subtitle_streams):
            tags = s.get("tags") or {}
            lang = tags.get("language") or tags.get("LANGUAGE") or tags.get("lang")
            
            subtitles.append({
                "index": i + 1,
                "codec": s.get("codec_name"),
                "language": lang,
                "title": tags.get("title") or tags.get("TITLE"),
                "forced": tags.get("forced") == "1" or tags.get("FORCED") == "1"
            })
        
        # Container/format info
        container = {
            "format": format_info.get("format_name"),
            "format_long": format_info.get("format_long_name"),
            "duration": float(format_info.get("duration", 0)) if format_info.get("duration") else None,
            "size": int(format_info.get("size", 0)) if format_info.get("size") else None,
            "bit_rate": int(format_info.get("bit_rate", 0)) if format_info.get("bit_rate") else None,
        }
        
        # Build normalized response (no entity enforcement, just clean structure)
        return {
            "ids": {"file_path": file_path},
            "container": container,
            "video": video,
            "audio": audio if audio else None,
            "subtitles": subtitles if subtitles else None,
            "extras": raw  # Keep raw ffprobe output
        }
    
    def _calculate_resolution(self, height) -> str:
        """Calculate resolution label from height"""
        if not height:
            return None
        try:
            h = int(height)
            if h >= 2160:
                return "2160p"
            elif h >= 1440:
                return "1440p"
            elif h >= 1080:
                return "1080p"
            elif h >= 720:
                return "720p"
            elif h > 0:
                return f"{h}p"
        except Exception:
            pass
        return None
    
    def _parse_fps(self, fps_str) -> float:
        """Parse frame rate from string like '24000/1001'"""
        if not fps_str:
            return None
        try:
            if '/' in str(fps_str):
                num, den = fps_str.split('/')
                return round(float(num) / float(den), 3)
            return float(fps_str)
        except Exception:
            return None
    
    def _detect_hdr(self, video_stream: Dict[str, Any]) -> bool:
        """Detect HDR from video stream metadata"""
        color_transfer = (video_stream.get("color_transfer") or "").lower()
        color_space = (video_stream.get("color_space") or "").lower()
        
        hdr_indicators = ["smpte2084", "arib-std-b67", "bt2020", "rec2020"]
        
        return any(indicator in color_transfer or indicator in color_space for indicator in hdr_indicators)
