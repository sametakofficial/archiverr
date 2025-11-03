# sanitiser.py
import re
from typing import Tuple, Optional

QUALITY_KEYWORDS = [
    "4K", "2160p", "1080p", "720p", "480p", "UHD",
    "BluRay", "BDRip", "BRRip", "WEB-DL", "WEBDL",
    "WEBRip", "HDTV", "DVDRip", "PROPER", "EXTENDED"
]

CODEC_KEYWORDS = [
    "x264", "x265", "H.264", "H.265", "HEVC",
    "10bit", "DTS-HD", "DTS", "Atmos", "TrueHD",
    "AC3", "DD+5.1", "AAC"
]

LANGUAGE_KEYWORDS = [
    "FR EN", "MULTI", "TRUEFRENCH", "FRENCH",
    "DUAL", "TR-EN", "TR Dublaj", "Dublaj"
]
ALL_DEFAULT_KEYWORDS = QUALITY_KEYWORDS + CODEC_KEYWORDS + LANGUAGE_KEYWORDS
_JOINED_DEFAULT = "|".join([re.escape(k) for k in ALL_DEFAULT_KEYWORDS if k])
DEFAULT_DELETE_REGEX = re.compile(rf"(?i)[\s\._]?({_JOINED_DEFAULT})\b|[\(\[].*?[\)\]]|\s+$")
SPACE_REGEX = re.compile(r"[._]")
EXTRACT_DATE_REGEX = re.compile(r"^(.+?)\s?\(?(19\d{2}|20\d{2})\)?.*$")

# --- KLASİK (eski) kalıplar: önce bunlar
EPISODE_KEYWORDS = ["episode","集","episodio","épisode","حلقة","эпизод","bölüm","Folge"]
joined_episode_keywords = "|".join([re.escape(k) for k in EPISODE_KEYWORDS])
CLASSIC_PATTERNS = [
    re.compile(rf"(?i)^(?P<name>.+?)[\.\s]S(?P<season>\d{{1,2}})E(?P<episode>\d{{1,3}})"),
    re.compile(rf"(?i)^(?P<name>.+?)[\.\s](?P<season>\d{{1,2}})x(?P<episode>\d{{1,3}})"),
    re.compile(rf"(?i)^(?P<name>.+?)[\.\s](?P<kw>{joined_episode_keywords})[\.\s]?(?P<episode>\d{{1,3}})")
]

# --- GENİŞ arama: her yerde S/E, ABS yakalama
SEASON_PATTERNS = [
    re.compile(r"(?i)\bS(?:eason)?\s*(?P<season>\d{1,2})\b"),
    re.compile(r"(?i)\bSezon\s*(?P<season>\d{1,2})\b"),
    re.compile(r"(?i)\b(?P<season>\d{1,2})\s*\.?\s*S\b"),
]
EPISODE_PATTERNS_LOOSE = [
    re.compile(r"(?i)\bE(?:pisode)?\s*(?P<episode>\d{1,3})\b"),
    re.compile(r"(?i)\bEp\.?\s*(?P<episode>\d{1,3})\b"),
    re.compile(r"(?i)\bB[öo]l[üu]m\s*(?P<episode>\d{1,3})\b"),
]
ABS_EP_PATTERNS = [
    re.compile(r"(?i)\b(?P<abs>\d{1,3})\s*\.?\s*B[öo]l[üu]m\b"),
    re.compile(r"(?i)\bB[öo]l[üu]m\s*(?P<abs>\d{1,3})\b"),
    re.compile(r"(?i)\bEp\.?\s*(?P<abs>\d{1,3})\b"),
]
COMBINED_SEASON_EPISODE = [
    re.compile(r"(?i)\bS(?P<season>\d{1,2})\s*E(?P<episode>\d{1,3})\b"),
    re.compile(r"(?i)\b(?P<season>\d{1,2})x(?P<episode>\d{1,3})\b"),
    re.compile(r"(?i)\bS\s*(?P<season>\d{1,2}).{0,6}E[p]?\s*(?P<episode>\d{1,3})"),
    re.compile(r"(?i)\[(?P<season>\d{1,2})\s*\.?\s*S(?:[^0-9]+|\.|\s)*E[p]?\s*(?P<episode>\d{1,3})\]"),
]

YEAR_PATTERN = re.compile(r"\b(19|20)\d{2}\b")

def _strip_leading_brackets(s: str) -> str:
    return re.sub(r"^\s*(\[[^\]]*\]\s*)+", '', s)

def sanitize_string(s: str, custom_delete_keywords=None) -> str:
    s = SPACE_REGEX.sub(' ', s)
    s = DEFAULT_DELETE_REGEX.sub(' ', s)
    if custom_delete_keywords:
        for kw in custom_delete_keywords:
            if kw:
                s = re.sub(rf"(?i)\b{re.escape(kw)}\b", ' ', s)
    s = re.sub(r"\s+", ' ', s).strip()
    return s

def _guess_show_name(cleaned: str) -> str:
    s = _strip_leading_brackets(cleaned)
    if ' - ' in s:
        left = s.split(' - ', 1)[0].strip()
        if left: return left
    m = re.search(r"(?i)\b(S(?:eason)?\s*\d+|Sezon\s*\d+|\d+\s*\.?\s*S|E(?:p|pisode)?\s*\d+|B[öo]l[üu]m\s*\d+)\b", s)
    if m:
        left = s[:m.start()].strip()
        if left: return left
    return s.strip()

def _classic_try(s: str):
    for patt in CLASSIC_PATTERNS:
        m = patt.search(s)
        if m:
            gd = m.groupdict()
            name = gd.get("name", "").strip() or s[:m.start()].strip()
            season = int(gd.get("season") or 1)
            episode = int(gd.get("episode") or 1)
            return name, season, episode
    return None

def _wide_try(s: str):
    for patt in COMBINED_SEASON_EPISODE:
        m = patt.search(s); 
        if m:
            return int(m['season']), int(m['episode'])
    # ayrık
    season = episode = None
    for p in SEASON_PATTERNS:
        m = p.search(s)
        if m:
            try: season = int(m['season']); break
            except: pass
    for p in EPISODE_PATTERNS_LOOSE:
        m = p.search(s)
        if m:
            try: episode = int(m['episode']); break
            except: pass
    return season, episode

def _abs_try(s: str) -> Optional[int]:
    for p in ABS_EP_PATTERNS:
        m = p.search(s)
        if m:
            try: return int(m.group('abs'))
            except: pass
    return None

def parse_movie_name(name_without_ext: str, custom_delete_keywords=None) -> Tuple[str, Optional[int]]:
    cleaned = sanitize_string(name_without_ext, custom_delete_keywords)
    m = EXTRACT_DATE_REGEX.match(cleaned)
    if m: return m.group(1).strip().title(), int(m.group(2))
    return cleaned.title(), None

def parse_episode_name(name_without_ext: str, custom_delete_keywords=None, exclude_unparsed: bool=False):
    # 0) çok minimal normalizasyon (nokta/altçizgi->boşluk), bracketları KORU
    pre = SPACE_REGEX.sub(' ', name_without_ext)

    # 1) önce klasik (en güvenilir)
    c = _classic_try(pre)
    if c:
        name, season, episode = c
        show = sanitize_string(name, custom_delete_keywords).title()
        return show, season, episode, False

    # 2) geniş arama
    season, episode = _wide_try(pre)
    # sezon işareti var mı?
    has_season_marker = season is not None or bool(re.search(r"(?i)\bS(?:eason)?\s*\d+\b|\bSezon\s*\d+\b|\b\d+\s*\.?\s*S\b|\b\d+x\d+\b", pre))
    # ABS?
    abs_ep = _abs_try(pre)

    if (not has_season_marker) and (abs_ep is not None):
        season, episode = 0, abs_ep

    # isim tahmini
    show_name = sanitize_string(_guess_show_name(pre), custom_delete_keywords).title()

    if season is None:  season = 1
    if episode is None: episode = 1

    if exclude_unparsed and (not show_name or len(show_name) < 2):
        return '', 0, 0, True
    return show_name, int(season), int(episode), False
