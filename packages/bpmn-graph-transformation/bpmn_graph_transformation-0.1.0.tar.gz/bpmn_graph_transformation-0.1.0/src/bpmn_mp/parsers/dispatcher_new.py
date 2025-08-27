# src/bpmn_mp/parsers/dispatcher_new.py
from __future__ import annotations

from importlib.metadata import entry_points, EntryPoint
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .base import ParserPlugin, SourceLike

_GROUP = "bpmn_mp.parsers"
_PLUGIN_CACHE: Optional[List[ParserPlugin]] = None


def _load_plugins() -> List[ParserPlugin]:
    """
    Discover & instantiate all parser plugins registered under entry point group.
    Cached for subsequent calls.
    """
    global _PLUGIN_CACHE
    if _PLUGIN_CACHE is not None:
        return _PLUGIN_CACHE

    # importlib.metadata.entry_points API (Py>=3.10)
    eps = entry_points()
    selected: List[EntryPoint] = []
    try:
        # New API returns an EntryPoints object supporting dict-style access
        selected = list(eps.select(group=_GROUP))  # type: ignore[attr-defined]
    except Exception:
        # Fallback: older behavior — eps might be a dict
        selected = list(eps.get(_GROUP, []))  # type: ignore[assignment]

    plugins: List[ParserPlugin] = []
    for ep in selected:
        try:
            plugin_cls = ep.load()
            plugin = plugin_cls()  # type: ignore[call-arg]
            if isinstance(plugin, ParserPlugin):
                plugins.append(plugin)
        except Exception:
            # Silently skip bad plugins; we don't want discovery to crash
            continue

    _PLUGIN_CACHE = plugins
    return plugins


def list_plugins() -> List[str]:
    """
    Return list of discovered plugin ids (for debugging/CLI).
    """
    return [p.plugin_id for p in _load_plugins()]


def _score_plugins(
    source: SourceLike, *,
    filename: Optional[str],
    candidates: List[ParserPlugin],
) -> List[Tuple[float, ParserPlugin]]:
    """
    Ask each candidate to detect() and return a sorted list of (score, plugin).
    Sort order: highest score first; tie-breaker by plugin.priority (higher wins).
    """
    scored: List[Tuple[float, ParserPlugin]] = []
    for p in candidates:
        try:
            score = float(p.detect(source, filename=filename))
        except Exception:
            score = 0.0
        scored.append((score, p))

    scored.sort(key=lambda x: (x[0], x[1].priority), reverse=True)
    return scored


def dispatch_parse(
    source: SourceLike,
    *,
    filename: Optional[str] = None,
    hint: Optional[str] = None
) -> Tuple[Dict[str, Any], str]:
    """
    Choose the best plugin for `source`, run parse(), and return (native_json, plugin_id).

    Parameters
    ----------
    source : Union[str, bytes, pathlib.Path]
        Path to file, raw bytes, or XML string.
    filename : Optional[str]
        Optional original filename (helps detection for streams).
    hint : Optional[str]
        Force-narrow candidates to a specific plugin_id ("bpmn", "xpdl", "xml", "native", "vdx").

    Returns
    -------
    (native_json, plugin_id) : (dict, str)

    Raises
    ------
    ValueError
        If no plugin is available or none can handle the source.
    """
    candidates = _load_plugins()
    if not candidates:
        raise ValueError("No parser plugins registered. Check your entry points configuration.")

    if hint:
        candidates = [p for p in candidates if p.plugin_id == hint]
        if not candidates:
            raise ValueError(f"No parser plugin registered for hint='{hint}'.")

    scored = _score_plugins(source, filename=filename, candidates=candidates)
    best_score, best = scored[0]

    if best_score <= 0.0:
        # Optionally include top-3 diagnostics to help users
        diag = ", ".join(f"{p.plugin_id}:{s:.2f}" for s, p in scored[:3])
        raise ValueError(f"No parser can handle the provided source (top scores: {diag}).")

    # Parse with the winning plugin
    data = best.parse(source, filename=filename)
    if not isinstance(data, dict):
        raise ValueError(f"Parser '{best.plugin_id}' returned non-dict payload.")

    return data, best.plugin_id
