#!/usr/bin/env python3
"""Resolve CoreAIKit metadata without downloading or running model weights."""
import argparse
import difflib
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys
from urllib.parse import quote
from urllib.request import Request, urlopen

MAX_BYTES = 1024 * 1024


def resolve(catalog, *, release, platform, model_id=None, kind=None):
    if not isinstance(catalog, dict) or not isinstance(catalog.get("models"), list):
        raise ValueError("Expected a CoreAIKit catalog with a models array")
    models = catalog["models"]
    if any(not isinstance(m, dict) or not isinstance(m.get("id"), str) for m in models):
        raise ValueError("Every catalog entry must have a string id")
    ids = [m["id"] for m in models]
    if len(set(ids)) != len(ids):
        raise ValueError("Catalog contains duplicate model IDs")
    if model_id is not None and model_id not in ids:
        suggestions = difflib.get_close_matches(model_id, ids, n=3)
        suffix = " Similar IDs: " + ", ".join(suggestions) if suggestions else ""
        raise ValueError(f"Unknown CoreAIKit ID: {model_id}.{suffix}")
    if kind is not None and kind not in {m.get("kind") for m in models}:
        kinds = ", ".join(sorted({str(m.get("kind")) for m in models}))
        raise ValueError(f"Unknown kind: {kind}. Available: {kinds}")
    matched = [m for m in models if (model_id is None or m["id"] == model_id)
               and (kind is None or m.get("kind") == kind)]
    if model_id is not None and not matched:
        raise ValueError(f"Model {model_id} does not have kind {kind}")
    result = []
    for model in matched:
        variants = model.get("variants")
        if not isinstance(variants, dict):
            raise ValueError(f"Model {model['id']} has invalid variants")
        if platform not in variants:
            if model_id is not None:
                raise ValueError(f"Model {model_id} has no {platform} variant")
            continue
        variant = variants[platform]
        repo, revision = model.get("repo", ""), model.get("revision", "")
        if not isinstance(repo, str) or not re.fullmatch(r"[\w.-]+/[\w.-]+", repo):
            raise ValueError(f"Model {model['id']} has an invalid Hugging Face repository")
        if not isinstance(revision, str) or not re.fullmatch(r"[0-9a-f]{40}", revision):
            raise ValueError(f"Model {model['id']} lacks an immutable Hugging Face pin")
        variant_path = variant.get("path") if isinstance(variant, dict) else None
        if not isinstance(variant_path, str) or PurePosixPath(variant_path).is_absolute() or ".." in PurePosixPath(variant_path).parts:
            raise ValueError(f"Model {model['id']} has an invalid variant path")
        result.append({
            "id": model["id"], "name": model.get("name"), "kind": model.get("kind"),
            "platform": platform, "repo": repo, "revision": revision,
            "variant": variant,
            "model_card_url": f"https://huggingface.co/{repo}/blob/{revision}/README.md",
            "artifact_url": f"https://huggingface.co/{repo}/tree/{revision}/{quote(variant_path, safe='/')}",
        })
    source = f"https://github.com/john-rocky/coreai-kit/blob/{release}"
    return {
        "package_ref": release, "platform": platform,
        "selection_scope": "live catalog" if release == "main" else "selected release catalog",
        "catalog_schema_version": catalog.get("version"),
        "documentation": {"setup": source + "/README.md#quickstart",
                          "validation": source + "/docs/GETTING_STARTED.md",
                          "cookbook": source + "/docs/COOKBOOK.md"},
        "evidence_scope": "Catalog metadata only. A variant is not a device/OS execution check; sizeMB is download size, not RAM.",
        "count": len(result), "models": result,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release", default="0.4.1", help="Release tag, or main for live data (default: 0.4.1)")
    parser.add_argument("--platform", choices=("macos", "ios"), required=True)
    parser.add_argument("--id", dest="model_id", help="Exact CoreAIKit catalog ID")
    parser.add_argument("--kind", help="Catalog kind, such as chat, vlm, asr, or tts")
    parser.add_argument("--catalog", type=Path, help="Read a local catalog snapshot instead of the network")
    args = parser.parse_args()
    if args.release != "main" and not re.fullmatch(r"v?\d+\.\d+\.\d+(?:[-+][A-Za-z0-9.-]+)?", args.release):
        parser.error("--release must be a release tag such as 0.4.1, or main")
    url = f"https://raw.githubusercontent.com/john-rocky/coreai-kit/{args.release}/catalog.json"
    try:
        if args.catalog:
            with args.catalog.open("rb") as handle:
                raw = handle.read(MAX_BYTES + 1)
        else:
            request = Request(url, headers={"User-Agent": "coreai-kit-skills-catalog/1.0"})
            with urlopen(request, timeout=20) as response:
                raw = response.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            raise ValueError("Catalog exceeds the 1 MiB metadata limit")
        output = resolve(json.loads(raw), release=args.release, platform=args.platform,
                         model_id=args.model_id, kind=args.kind)
        output["source"] = str(args.catalog) if args.catalog else url
        output["catalog_sha256"] = hashlib.sha256(raw).hexdigest()
        print(json.dumps(output, indent=2, ensure_ascii=False))
    except (OSError, ValueError, TypeError) as error:
        print(json.dumps({"error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
