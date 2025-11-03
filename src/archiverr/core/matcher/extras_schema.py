# core/matcher/extras_schema.py
"""
Extra Metadata Schema - Defines standard structure for optional metadata.

This module defines the normalized schema for extra metadata that can be
fetched from APIs like TMDb. These are optional and require additional API calls.
"""
from typing import TypedDict, List, Dict, Any, Optional


# ============================================================================
# CREDITS
# ============================================================================

class CastMember(TypedDict, total=False):
    """Single cast member"""
    id: int
    name: str
    character: str
    order: int
    profile_path: Optional[str]


class CrewMember(TypedDict, total=False):
    """Single crew member"""
    id: int
    name: str
    job: str
    department: str
    profile_path: Optional[str]


class Credits(TypedDict, total=False):
    """Credits structure (cast & crew)"""
    cast: List[CastMember]
    crew: List[CrewMember]


class AggregateCastMember(TypedDict, total=False):
    """Aggregate cast member (TV series across all seasons)"""
    id: int
    name: str
    roles: List[Dict[str, Any]]  # [{'character': str, 'episode_count': int}]
    total_episode_count: int
    profile_path: Optional[str]


class AggregateCrewMember(TypedDict, total=False):
    """Aggregate crew member (TV series across all seasons)"""
    id: int
    name: str
    jobs: List[Dict[str, Any]]  # [{'job': str, 'episode_count': int}]
    total_episode_count: int
    profile_path: Optional[str]


class AggregateCredits(TypedDict, total=False):
    """Aggregate credits (TV series)"""
    cast: List[AggregateCastMember]
    crew: List[AggregateCrewMember]


# ============================================================================
# IMAGES
# ============================================================================

class Image(TypedDict, total=False):
    """Single image"""
    path: str
    width: int
    height: int
    aspect_ratio: float
    vote_average: float
    iso_639_1: Optional[str]  # Language code


class Images(TypedDict, total=False):
    """Images collection"""
    posters: List[Image]
    backdrops: List[Image]
    stills: List[Image]  # For episodes
    logos: List[Image]   # For companies/networks


# ============================================================================
# VIDEOS
# ============================================================================

class Video(TypedDict, total=False):
    """Single video (trailer, teaser, clip)"""
    key: str           # YouTube key
    site: str          # Usually 'YouTube'
    name: str
    type: str          # 'Trailer', 'Teaser', 'Clip', etc.
    size: int          # 360, 720, 1080, etc.
    iso_639_1: Optional[str]
    iso_3166_1: Optional[str]


class Videos(TypedDict, total=False):
    """Videos collection"""
    trailers: List[Video]
    teasers: List[Video]
    clips: List[Video]
    other: List[Video]


# ============================================================================
# WATCH PROVIDERS
# ============================================================================

class WatchProvider(TypedDict, total=False):
    """Single watch provider"""
    id: int
    name: str
    logo_path: str


class WatchProviders(TypedDict, total=False):
    """Watch providers by region"""
    link: Optional[str]
    flatrate: List[WatchProvider]  # Streaming (Netflix, etc.)
    rent: List[WatchProvider]
    buy: List[WatchProvider]


# ============================================================================
# EXTERNAL IDS
# ============================================================================

class ExternalIds(TypedDict, total=False):
    """External IDs across different platforms"""
    imdb: Optional[str]
    tvdb: Optional[str]
    tvrage: Optional[str]
    facebook: Optional[str]
    instagram: Optional[str]
    twitter: Optional[str]
    wikidata: Optional[str]


# ============================================================================
# CONTENT RATINGS
# ============================================================================

class ContentRatings(TypedDict, total=False):
    """Content ratings by country (age ratings)"""
    # Dynamic: {country_code: rating}
    # Example: {'US': 'TV-14', 'GB': '12A'}
    ratings: Dict[str, str]


# ============================================================================
# EXTRAS CONTAINER
# ============================================================================

class Extras(TypedDict, total=False):
    """
    Container for all extra metadata.
    
    All fields are optional and fetched on-demand.
    """
    # Core extras
    credits: Optional[Credits]
    aggregate_credits: Optional[AggregateCredits]  # TV series only
    images: Optional[Images]
    videos: Optional[Videos]
    keywords: Optional[List[str]]
    external_ids: Optional[ExternalIds]
    watch_providers: Optional[WatchProviders]
    content_ratings: Optional[ContentRatings]  # TV only
    
    # Additional metadata
    recommendations: Optional[List[Dict[str, Any]]]
    similar: Optional[List[Dict[str, Any]]]
    reviews: Optional[List[Dict[str, Any]]]
    translations: Optional[List[str]]


# ============================================================================
# EXTRAS CATEGORIES
# ============================================================================

# Define which extras require separate API calls
EXTRAS_CATEGORIES = {
    'movie': {
        'credits': 'movie/{id}/credits',
        'images': 'movie/{id}/images',
        'videos': 'movie/{id}/videos',
        'keywords': 'movie/{id}/keywords',
        'external_ids': 'movie/{id}/external_ids',
        'watch_providers': 'movie/{id}/watch/providers',
        'recommendations': 'movie/{id}/recommendations',
        'similar': 'movie/{id}/similar',
        'reviews': 'movie/{id}/reviews',
        'translations': 'movie/{id}/translations',
    },
    'tv': {
        'credits': 'tv/{id}/credits',
        'aggregate_credits': 'tv/{id}/aggregate_credits',
        'images': 'tv/{id}/images',
        'videos': 'tv/{id}/videos',
        'keywords': 'tv/{id}/keywords',
        'external_ids': 'tv/{id}/external_ids',
        'watch_providers': 'tv/{id}/watch/providers',
        'content_ratings': 'tv/{id}/content_ratings',
        'recommendations': 'tv/{id}/recommendations',
        'similar': 'tv/{id}/similar',
        'reviews': 'tv/{id}/reviews',
        'translations': 'tv/{id}/translations',
    },
    'season': {
        'credits': 'tv/{tv_id}/season/{season}/credits',
        'images': 'tv/{tv_id}/season/{season}/images',
        'videos': 'tv/{tv_id}/season/{season}/videos',
    },
    'episode': {
        'credits': 'tv/{tv_id}/season/{season}/episode/{episode}/credits',
        'images': 'tv/{tv_id}/season/{season}/episode/{episode}/images',
        'videos': 'tv/{tv_id}/season/{season}/episode/{episode}/videos',
    },
}


# Default extras to fetch (can be overridden in config)
DEFAULT_EXTRAS = {
    'movie': [],  # No extras by default
    'tv': [],     # No extras by default
    'season': [],
    'episode': [],
}
