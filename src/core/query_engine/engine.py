# engine/engine.py
"""
YML Engine - Ana orchestrator.
"""
from typing import Any, Dict, List, Optional
from pathlib import Path
import json

from .variables import build_variable_context
from .variable_engine import render_template, execute_query


class YMLEngine:
    """
    YML Engine - Pattern rendering ve query execution için ana sınıf.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Args:
            config: config.yml parsed dict
        """
        self.config = config
        self.globals = config.get('query_engine', {}).get('globals', {})
        self.root_paths = {
            'movies_dst': config.get('rename', {}).get('movies_dst', ''),
            'series_dst': config.get('rename', {}).get('series_dst', ''),
        }
    
    def render_filename(
        self,
        file_path: str,
        api_response_data: Optional[Dict[str, Any]] = None,
        ffprobe_data: Optional[Dict[str, Any]] = None,
        media_type: str = "movie",
        parsed_info: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Dosya için yeni isim render et.
        
        Args:
            file_path: Kaynak dosya yolu
            api_response_data: Normalized API response (from any API client)
            ffprobe_data: FFprobe JSON
            media_type: "movie" | "tv"
            parsed_info: Sanitiser parse sonucu
        
        Returns:
            Rendered filename pattern
        """
        # Variable context oluştur
        context = build_variable_context(
            file_path=file_path,
            api_response_data=api_response_data,
            ffprobe_data=ffprobe_data,
            media_type=media_type,
            parsed_info=parsed_info,
            config_globals=self.globals,
            root_paths=self.root_paths,
        )
        
        # Pattern al
        if media_type == "movie":
            pattern = self.config.get('rename', {}).get('movie_pattern', '$name ($movieYear)')
        else:
            pattern = self.config.get('rename', {}).get('series_pattern', '$showName - S$seasonNumberE$episodeNumber')
        
        # Render
        return render_template(pattern, context)
    
    def execute_queries(
        self,
        nfo_files: List[str],
        dry_run: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Query engine'i çalıştır.
        
        Args:
            nfo_files: *-ffmpeg.nfo dosya yolları
            dry_run: True ise sadece print, save yapma
        
        Returns:
            Her query için sonuç dict listesi
        """
        # NFO'lardan context'leri oluştur
        file_contexts = []
        for nfo_path in nfo_files:
            ctx = self._load_context_from_nfo(nfo_path)
            if ctx:
                file_contexts.append(ctx)
        
        # Query'leri çalıştır
        queries = self.config.get('query_engine', {}).get('queries', [])
        results = []
        
        for query_config in queries:
            result = execute_query(query_config, file_contexts, dry_run)
            results.append(result)
        
        return results
    
    def _load_context_from_nfo(self, nfo_path: str) -> Optional[Dict[str, Any]]:
        """
        *-ffmpeg.nfo dosyasından context yükle.
        
        Args:
            nfo_path: NFO dosya yolu
        
        Returns:
            Variable context veya None
        """
        try:
            with open(nfo_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # NFO içinde ffprobe + best (API response) + parsed bilgiler olabilir
            ffprobe_data = data.get('ffprobe')
            api_response_data = data.get('best')  # Normalized API response
            parsed_info = data.get('parsed')
            media_type = data.get('media_type', 'movie')
            file_path = data.get('file_path', nfo_path.replace('-ffmpeg.nfo', ''))
            
            return build_variable_context(
                file_path=file_path,
                api_response_data=api_response_data,
                ffprobe_data=ffprobe_data,
                media_type=media_type,
                parsed_info=parsed_info,
                config_globals=self.globals,
                root_paths=self.root_paths,
            )
        
        except Exception as e:
            # TODO: Log error
            return None
    
    def save_context_to_nfo(
        self,
        file_path: str,
        api_response_data: Optional[Dict[str, Any]] = None,
        ffprobe_data: Optional[Dict[str, Any]] = None,
        media_type: str = "movie",
        parsed_info: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Context'i *-ffmpeg.nfo olarak kaydet.
        
        Args:
            file_path: Kaynak dosya yolu
            api_response_data: API response data
            ffprobe_data: FFprobe data
            media_type: "movie" | "tv"
            parsed_info: Parsed info
        
        Returns:
            NFO dosya yolu
        """
        # NFO path oluştur
        p = Path(file_path)
        nfo_path = p.parent / f"{p.stem}-ffmpeg.nfo"
        
        # Data oluştur
        nfo_data = {
            'file_path': str(file_path),
            'media_type': media_type,
            'best': api_response_data,  # Normalized API response
            'ffprobe': ffprobe_data,
            'parsed': parsed_info,
        }
        
        # Kaydet
        with open(nfo_path, 'w', encoding='utf-8') as f:
            json.dump(nfo_data, f, indent=2, ensure_ascii=False)
        
        return str(nfo_path)
