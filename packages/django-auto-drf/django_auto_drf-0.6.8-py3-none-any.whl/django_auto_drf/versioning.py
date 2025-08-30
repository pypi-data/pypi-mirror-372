from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Optional

from django.core.exceptions import ImproperlyConfigured

from django_auto_drf.core import EndpointConfig
from django_auto_drf.settings import AUTO_DRF_VERSIONS


@dataclass
class _Segment:
    cfg: EndpointConfig


class VersionHeaderMixin:
    """Expose fixed API version in responses. If a view defines FIXED_API_VERSION, use that directly.
    Otherwise, fall back to DRF's versioning (request.version) if present.
    """

    # Allow views to set a class attribute FIXED_API_VERSION = "1" or an int; used for simplicity.
    FIXED_API_VERSION = None

    def finalize_response(self, request, response, *args, **kwargs):
        resp = super().finalize_response(request, response, *args, **kwargs)
        v = getattr(self, 'FIXED_API_VERSION', None)
        if v is None:
            v = getattr(request, 'version', None)
        if v is not None:
            resp.headers['X-API-Version'] = str(v)
        return resp

    def determine_version(self, request, *args, **kwargs):
        """Return a tuple (version, scheme) as expected by DRF 3.15+ when overriding on views.
        - If FIXED_API_VERSION is set on the view, return (str(version), None).
        - Otherwise, delegate to DRF and normalize into a tuple.
        """
        fixed = getattr(self, 'FIXED_API_VERSION', None)
        if fixed is not None:
            return str(fixed), None
        # Normalize kwargs keys in case DRF/spectacular still calls with view.kwargs
        if isinstance(kwargs, dict):
            try:
                kwargs = {str(k): v for k, v in kwargs.items()}
            except Exception:
                kwargs = {}
        else:
            kwargs = {}
        result = super().determine_version(request, *args, **kwargs)
        # DRF's determine_version may return just a version (pre-3.15) or (version, scheme). Normalize to tuple.
        if isinstance(result, tuple) and len(result) == 2:
            return result
        return result, None


from rest_framework.versioning import URLPathVersioning


class AutoDRFURLVersioning(URLPathVersioning):
    """
    DRF-aware versioning that reads version from URL path prefix like /api/v1/...
    Behavior:
    - If AUTO_DRF_VERSIONS is None: versioning OFF -> returns None (DRF leaves request.version=None)
    - If ON: extracts the first segment matching v<digits>, returns the number as string
      and (optionally) validates that it's in AUTO_DRF_VERSIONS.
    No need to configure REST_FRAMEWORK settings.
    """

    version_param = None  # not using query params

    _regex = re.compile(r"/v(\d+)(/|$)")

    def determine_version(self, request, *args, **kwargs):
        # Normalize kwargs keys defensively (some callers may pass non-string keys)
        if isinstance(kwargs, dict):
            try:
                kwargs = {str(k): v for k, v in kwargs.items()}
            except Exception:
                kwargs = {}
        # OFF: do nothing
        if AUTO_DRF_VERSIONS is None:
            return None, None
        path = request.path or ""
        m = self._regex.search(path)
        if not m:
            # Not a versioned URL; keep None
            return None, None
        version_str = m.group(1)
        # Validate against configured versions if provided
        try:
            v_int = int(version_str)
        except ValueError:
            return None, None
        if AUTO_DRF_VERSIONS and v_int not in AUTO_DRF_VERSIONS:
            # Router should already constrain, but be safe: treat as invalid => None
            return None, None
        # DRF expects version string and scheme
        return version_str, self


class VersionedEndpoint:
    """
    Maintains ordered EndpointConfig segments and resolves configs per version.
    """

    def __init__(self, endpoint: str):
        self.endpoint = endpoint
        self.segments: List[EndpointConfig] = []

    def _versioning_on(self) -> bool:
        return AUTO_DRF_VERSIONS is not None

    def add(self, config: EndpointConfig):
        """
        Add a config segment with validations. When versioning is OFF, it must have no version metadata.
        When ON, enforce version in list, last_version>=version and uniqueness of starting version for this endpoint.
        """
        if not isinstance(config, EndpointConfig):
            raise TypeError("config must be an EndpointConfig")
        if self._versioning_on():
            if config.version is None:
                raise ImproperlyConfigured(
                    f"Versioning is ON; 'version' is required for endpoint '{self.endpoint}'"
                )
            if config.version not in AUTO_DRF_VERSIONS:
                raise ImproperlyConfigured(
                    f"version={config.version} for endpoint '{self.endpoint}' is not in AUTO_DRF_VERSIONS={AUTO_DRF_VERSIONS}"
                )
            if config.last_version is not None:
                if config.last_version not in AUTO_DRF_VERSIONS:
                    raise ImproperlyConfigured(
                        f"last_version={config.last_version} for endpoint '{self.endpoint}' is not in AUTO_DRF_VERSIONS={AUTO_DRF_VERSIONS}"
                    )
                if config.last_version < config.version:
                    raise ImproperlyConfigured(
                        f"last_version ({config.last_version}) must be >= version ({config.version}) for endpoint '{self.endpoint}'"
                    )
            # If a segment with the same starting version exists, skip adding to avoid duplicate error from Django runserver double-loading.
            for idx, s in enumerate(self.segments):
                if s.version == config.version:
                    # Do not overwrite; simply return keeping the first registration
                    return
            # Insert keeping segments sorted by version
            self.segments.append(config)
            self.segments.sort(key=lambda s: s.version or -1)
            # Optional coalescing: merge adjacent identical configs
            self._coalesce()
        else:
            # OFF: accept configs regardless of version metadata; force default version=1 for internal consistency
            config.version = 1
            config.last_version = None
            # Keep only one segment for OFF for internal uniformity
            self.segments = [config]

    def _coalesce(self):
        # Coalesce only when ON
        if not self._versioning_on():
            return
        if not self.segments:
            return
        merged: List[EndpointConfig] = []
        for seg in sorted(self.segments, key=lambda s: s.version or -1):
            if not merged:
                merged.append(seg)
                continue
            last = merged[-1]
            # Two segments are "identical" if all behavior-affecting fields equal
            if self._identical(last, seg) and (last.last_version or self._max_version()) + 1 == (seg.version or 0):
                # Extend the last segment's last_version
                last.last_version = seg.last_version or last.last_version or self._max_version()
            else:
                merged.append(seg)
        self.segments = merged

    def _max_version(self) -> int:
        return AUTO_DRF_VERSIONS[-1] if AUTO_DRF_VERSIONS else 0

    @staticmethod
    def _identical(a: EndpointConfig, b: EndpointConfig) -> bool:
        return (
                a.model_label == b.model_label
                and a.viewset_class == b.viewset_class
                and a.serializer_class == b.serializer_class
                and a.filterset_class == b.filterset_class
                and a.permissions == b.permissions
                and a.paginate_by == b.paginate_by
                and [n for n, _ in a.extra_actions] == [n for n, _ in b.extra_actions]
        )

    def get_for_version(self, k: int) -> Optional[EndpointConfig]:
        if not self._versioning_on():
            # Single config if exists
            return self.segments[0] if self.segments else None
        last_match: Optional[EndpointConfig] = None
        for s in sorted(self.segments, key=lambda s: s.version or -1):
            if (s.version or 0) > k:
                break
            if s.last_version is None or k <= s.last_version:
                last_match = s
        return last_match

    def has_for_version(self, k: int) -> bool:
        return self.get_for_version(k) is not None
