"""
Refactored public interface for the NomadicML `VideoClient`.

🔹 **upload(**) – handles *one* or *many* uploads (local path / remote URL).
🔹 **analyze(**) – triggers analysis for *one* or *many* `video_id`s.

Internally the original, lower‑level helpers (`upload_video`, `analyze_video`, …) stay untouched.
This means there is *no* behavioural drift – the new API is just syntactic sugar & conven­ience.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Optional, Sequence, Union, Callable, Iterable

# ─── TYPE ALIASES ────────────────────────────────────────────────────────────
Json       = Dict[str, Any]
MaybeList  = Union[str, Sequence[str]]


class VideoClient:  # (inherits the unchanged implementation seen in nomadicml.sdk)
    # ---------------------------------------------------------------------
    # 🛠  Helper utilities
    # ---------------------------------------------------------------------
    def _as_list(self, item_or_items: MaybeList) -> List[str]:
        """Return *item_or_items* as a **list** without modifying the order."""
        if item_or_items is None:
            return []
        if isinstance(item_or_items, (list, tuple, set)):
            return list(item_or_items)
        return [item_or_items]  # single value

    def _map_concurrent(self,
                        fn: Callable[[str], Json],
                        items: Iterable[str],
                        *,
                        max_workers: Optional[int] = None) -> List[Json]:
        """Run *fn* concurrently for each *item* preserving **input order**."""
        items = list(items)
        if not items:
            return []
        if len(items) == 1:
            return [fn(items[0])]

        max_workers = max_workers or min(8, len(items))
        results: Dict[str, Json] = {}
        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            future_map = {pool.submit(fn, it): it for it in items}
            for fut in as_completed(future_map):
                key = future_map[fut]
                results[key] = fut.result()
        # preserve original ordering
        return [results[k] for k in items]

    # ---------------------------------------------------------------------
    # 🌐  Public API
    # ---------------------------------------------------------------------
    def upload(
        self,
        *,
        file_paths: MaybeList,
        edge_case_category: Optional[str] = None,
        **kwargs,
    ) -> Union[Json, List[Json]]:
        """Universal *upload* front‑door.

        Args:
            file_paths: Local paths **or** remote URLs.
            edge_case_category: Forwarded to :py:meth:`upload_video_edge` when given.
            **kwargs:    Forwarded verbatim to the underlying helper (e.g. `model_id`).
        """
        if file_paths is None:
            raise ValueError("Must provide file_paths for upload.")

        items = self._as_list(file_paths)  # type: List[str]

        def _single(item: str) -> Json:
            if edge_case_category:
                return self.upload_video_edge(file_path=item, category=edge_case_category, **kwargs)
            return self.upload_video(file_path=item, **kwargs)

        out = self._map_concurrent(_single, items)
        return out[0] if len(out) == 1 else out

    def analyze(
        self,
        video_ids: MaybeList,
        *,
        model_id: str = "Nomadic-VL-XLarge",
        concurrent: bool = True,
        **kwargs,
    ) -> Union[Json, List[Json]]:
        """Trigger analysis for *one* or *many* ``video_id``\ s.

        Args:
            video_ids:   Video identifier(s).
            model_id:    Backend model choice (defaults to *Nomadic‑VL‑XLarge*).
            concurrent:  When *True* analyses are kicked‑off in parallel threads.
            **kwargs:    Forwarded to :py:meth:`analyze_video`.
        """
        items = self._as_list(video_ids)

        if not concurrent or len(items) == 1:
            if len(items) == 1:
                return self.analyze_video(items[0], model_id=model_id, **kwargs)
            # sequential fall‑back (rarely used; mainly for debugging)
            return [self.analyze_video(v, model_id=model_id, **kwargs) for v in items]

        def _single(vid: str) -> Json:
            return self.analyze_video(vid, model_id=model_id, **kwargs)

        out = self._map_concurrent(_single, items)
        return out[0] if len(out) == 1 else out

    def upload_and_analyze(
        self,
        *,
        file_paths: MaybeList,
        wait_for_completion: bool = True,
        timeout: int = 2_400,
        **kwargs,
    ) -> Union[Json, List[Json]]:
        """Backwards‑compat convenience wrapper.

        All heavy‑lifting is deferred to :py:meth:`upload` and :py:meth:`analyze`.
        """
        # ── 1) Upload ────────────────────────────────────────────────────
        uploads = self.upload(file_paths=file_paths, **kwargs)
        # Normalise to list of dicts for downstream logic ------------
        if isinstance(uploads, dict):
            uploads_list = [uploads]
        else:
            uploads_list = uploads

        # ── 2) Analyse ──────────────────────────────────────────────────
        ids = [u["video_id"] for u in uploads_list]
        analyses = self.analyze(ids, **kwargs)

        # ── 3) Optionally wait for completion ---------------------------
        if wait_for_completion:
            if isinstance(ids, list) and len(ids) > 1:
                self.wait_for_analyses(ids, timeout=timeout)
            else:
                self.wait_for_analysis(ids[0] if isinstance(ids, list) else ids, timeout=timeout)

        return analyses

###########################
###########################
##############################


"""
Refactored public interface for the NomadicML `VideoClient`.

**Change in this revision →** `VideoInput` accepts either a string or `pathlib.Path`. Strings may represent local file paths or URLs.

Public helpers:

* **upload(paths, /, …)** – accepts a single `Path` or an iterable of `Path` objects. Returns *dict* (single) or *list[dict]* (many).
* **analyze(video_ids, /, …)** – unchanged polymorphic behaviour for backend IDs (still `str | Sequence[str]`).
* **upload_and_analyze(…)** – chains the two calls; input must be path(s).

Only the new/changed code is shown below; the remainder of `VideoClient` is intact.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Sequence, Union, List, Dict, Any, Optional, overload

# ──────────────────────────────────────────────────────────────────────────────
# Type aliases
# ──────────────────────────────────────────────────────────────────────────────
VideoInput   = Union[str, Path]
VideoInputs  = Union[VideoInput, Sequence[VideoInput]]
VideoID      = str
VideoIDList  = Sequence[VideoID]

# NOTE: we assume `VideoClient` already exists in the surrounding module with
# the original (large) implementation. In production these methods should be
# merged directly into the class definition.


def _is_iterable(obj):
    """True for list / tuple / set but *not* for strings or Path."""
    return isinstance(obj, Sequence) and not isinstance(obj, (str, Path))


class VideoClient(VideoClient):  # type: ignore[misc]
    """Add polymorphic public helpers while preserving the original contract."""

    # ───────────────────────── upload ────────────────────────────────
    @overload
    def upload(self, videos: VideoInput, /, **kwargs) -> Dict[str, Any]: ...

    @overload  # noqa: D401 – overload signature for list input
    def upload(self, videos: Sequence[VideoInput], /, **kwargs) -> List[Dict[str, Any]]: ...

    def upload(self, videos: VideoInputs, /, **kwargs):  # type: ignore[override]
        """Upload *one* or *many* local video files (paths).

        Parameters
        ----------
        videos : pathlib.Path | Sequence[pathlib.Path]
            Single file or a list/tuple thereof.
        **kwargs
            Forwarded verbatim to the underlying :py:meth:`upload_video` /
            :py:meth:`upload_video_edge` helpers.
        """
        if _is_iterable(videos):
            paths = list(videos)
            if not paths:
                raise ValueError("No paths provided")
            return self._upload_many(paths, **kwargs)
        else:
            return self._upload_single(videos, **kwargs)

    #  ── helpers ──────────────────────────────────────────────────────
    def _upload_single(self, video: VideoInput, /, **kw) -> Dict[str, Any]:
        """Delegate to the low‑level helper using a local file path."""
        edge_case_category = kw.get("edge_case_category")

        kw.setdefault("file_path", str(video))

        if edge_case_category:
            return self.upload_video_edge(**kw)  # type: ignore[arg-type]
        return self.upload_video(**kw)            # type: ignore[arg-type]

    def _upload_many(self, videos: List[VideoInput], /, **kw) -> List[Dict[str, Any]]:
        with ThreadPoolExecutor(max_workers=len(videos)) as exe:
            futs = [exe.submit(self._upload_single, v, **kw) for v in videos]
            return [f.result() for f in futs]  # preserves input order

    # ───────────────────────── analyze ────────────────────────────────
    @overload
    def analyze(self, video_ids: VideoID, /, **kwargs) -> Dict[str, Any]: ...

    @overload
    def analyze(self, video_ids: VideoIDList, /, **kwargs) -> List[Dict[str, Any]]: ...

    def analyze(self, video_ids: Union[VideoID, VideoIDList], /, **kwargs):  # type: ignore[override]
        """Trigger analysis for one or many backend videos."""
        if _is_iterable(video_ids):
            vids = list(video_ids)
            if not vids:
                raise ValueError("No video_ids provided")
            return self._analyze_many(vids, **kwargs)
        else:
            return self._analyze_single(video_ids, **kwargs)

    #  ── helpers ──────────────────────────────────────────────────────
    def _analyze_single(self, vid: VideoID, /, **kw) -> Dict[str, Any]:
        edge_case_category = kw.get("edge_case_category")
        if edge_case_category:
            return self.analyze_video_edge(video_id=vid, **kw)  # type: ignore[arg-type]
        return self.analyze_video(video_id=vid, **kw)            # type: ignore[arg-type]

    def _analyze_many(self, vids: List[VideoID], /, **kw) -> List[Dict[str, Any]]:
        with ThreadPoolExecutor(max_workers=len(vids)) as exe:
            futs = [exe.submit(self._analyze_single, v, **kw) for v in vids]
            return [f.result() for f in futs]

    # ─────────────────────── upload + analyze ─────────────────────────
    def upload_and_analyze(self, videos: VideoInputs, /, **kw):  # type: ignore[override]
        """Convenience wrapper preserving legacy name.

        Input must be path(s). For a *single* `Path` we return a *dict*; for a
        list we return a *list[dict]*.
        """
        uploads_result = self.upload(videos, wait_for_completion=False, **kw)

        # Normalise to list for the analyse phase
        uploads = uploads_result if isinstance(uploads_result, list) else [uploads_result]
        video_ids = [u["video_id"] for u in uploads]

        analyses_result = self.analyze(video_ids, **kw)
        return analyses_result[0] if isinstance(videos, Path) else analyses_result
