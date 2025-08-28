from __future__ import annotations
from typing import Dict, List
try:
    import yaml
except Exception:  # pragma: no cover
    yaml = None


def to_openapi(endpoints: List[Dict], title: str = "API", version: str = "1.0.0") -> Dict:
    paths: Dict[str, Dict] = {}
    for ep in endpoints:
        path = ep.get("path", "/")
        method = ep.get("method", "get").lower()
        paths.setdefault(path, {})[method] = {
            "summary": ep.get("summary") or f"{method.upper()} {path}",
            "description": ep.get("description") or "",
            "responses": {
                "200": {"description": "OK"}
            },
        }
    return {
        "openapi": "3.1.0",
        "info": {"title": title, "version": version},
        "paths": paths,
    }


def to_openapi_yaml(endpoints: List[Dict], title: str = "API", version: str = "1.0.0") -> str:
    spec = to_openapi(endpoints, title=title, version=version)
    if yaml is None:
        raise RuntimeError("pyyaml not installed. Run: pip install pyyaml")
    return yaml.safe_dump(spec, sort_keys=False, allow_unicode=True)
