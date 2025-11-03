# nfo.py
from typing import Any, Dict, Optional
from pathlib import Path
import xml.etree.ElementTree as ET

def _text(elem, tag, text):
    e = ET.SubElement(elem, tag)
    if text is not None:
        e.text = str(text)

def make_movie_nfo(tmdb: Dict[str, Any]) -> str:
    # Basit, ama zenginleştirilebilir
    root = ET.Element("movie")
    _text(root, "title", tmdb.get("title") or tmdb.get("original_title"))
    _text(root, "originaltitle", tmdb.get("original_title"))
    _text(root, "year", (tmdb.get("release_date") or "")[:4])
    _text(root, "plot", tmdb.get("overview"))
    _text(root, "id", tmdb.get("id"))
    for g in tmdb.get("genres") or []:
        _text(root, "genre", g.get("name"))
    for c in tmdb.get("production_companies") or []:
        _text(root, "studio", c.get("name"))
    # oyuncular
    for c in (tmdb.get("credits", {}) or {}).get("cast", [])[:50]:
        p = ET.SubElement(root, "actor")
        _text(p, "name", c.get("name"))
        _text(p, "role", c.get("character"))
    return ET.tostring(root, encoding="utf-8", xml_declaration=True).decode("utf-8")

def make_episode_nfo(show: Dict[str, Any], ep: Dict[str, Any]) -> str:
    root = ET.Element("episodedetails")
    _text(root, "title", ep.get("name"))
    _text(root, "season", ep.get("season_number"))
    _text(root, "episode", ep.get("episode_number"))
    _text(root, "showtitle", show.get("name") or show.get("original_name"))
    _text(root, "aired", ep.get("air_date"))
    _text(root, "plot", ep.get("overview"))
    _text(root, "id", ep.get("id"))
    for c in (show.get("credits", {}) or {}).get("cast", [])[:50]:
        p = ET.SubElement(root, "actor")
        _text(p, "name", c.get("name"))
        _text(p, "role", "")
    return ET.tostring(root, encoding="utf-8", xml_declaration=True).decode("utf-8")

def maybe_write(path_without_ext: str, content: str):
    out = Path(path_without_ext + ".nfo")
    out.write_text(content, encoding="utf-8")
