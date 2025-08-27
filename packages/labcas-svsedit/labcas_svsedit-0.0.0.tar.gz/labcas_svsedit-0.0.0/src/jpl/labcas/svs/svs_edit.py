#!/usr/bin/env python3
import argparse
import os
import re
import sys
import tifftools
from . import VERSION
from typing import Dict, Tuple, List, Any


# Common TIFF tag codes we'll touch by name
TAGCODES = {
    "ImageDescription": 270,
    "Software": 305,
    "Artist": 315,
    "XMP": 700,  # XMP metadata packet
}


def load_xmp(path: str) -> bytes:
    with open(path, "rb") as f:
        return f.read()


def ifd_find_tag(ifd: Dict[str, Any], code: int):
    """
    Return the tag dict for the given numeric tag code.

    tifftools may expose IFD['tags'] as either:
      - dict[int, dict]  (newer versions), or
      - list[dict]       (older versions)
    This handles both.
    """
    tags = ifd.get("tags") or {}
    # dict form
    if isinstance(tags, dict):
        tag = tags.get(code) or tags.get(int(code)) or tags.get(str(code))
        # Some variants store a list for duplicate tags; take the first
        if isinstance(tag, list):
            return tag[0] if tag else None
        return tag
    # list form
    if isinstance(tags, list):
        for t in tags:
            if isinstance(t, dict) and t.get("code") == int(code):
                return t
    return None

def ifd_set_tag(ifd: Dict[str, Any], code: int, value):
    """
    Set or add a tag with raw value. Supports both dict and list 'tags' layouts.
    For ASCII tags, pass a Python str; tifftools will serialize appropriately.
    """
    tags = ifd.get("tags")
    if not tags:
        # Default to dict layout when creating from scratch
        ifd["tags"] = {int(code): {"code": int(code), "data": value}}
        return

    if isinstance(tags, dict):
        existing = tags.get(code) or tags.get(int(code)) or tags.get(str(code))
        if isinstance(existing, list):
            existing = existing[0] if existing else None
        if existing is None:
            tags[int(code)] = {"code": int(code), "data": value}
        else:
            existing["data"] = value

    elif isinstance(tags, list):
        tag = ifd_find_tag(ifd, code)
        if tag is None:
            tags.append({"code": int(code), "data": value})
        else:
            tag["data"] = value

def update_imagedescription_regex(
    ifd: Dict[str, Any],
    edit_pairs: Dict[str, str],
    append_missing: bool = False,
) -> Tuple[str, str, bool]:
    """
    Edit only the specified KEY=VALUE pairs inside ImageDescription (tag 270) for a single IFD.
    - Preserves the rest of the string (order/spacing).
    - If append_missing=False (default), keys that do not already exist are NOT added.
      Set append_missing=True to append " | KEY = VALUE" when a key is absent.
    Returns: (old_str, new_str, changed_bool)
    """
    tag_code = 270  # ImageDescription
    tag = ifd_find_tag(ifd, tag_code)
    old_val = tag.get("data") if tag else None

    # Normalize to str
    if isinstance(old_val, (bytes, bytearray)):
        try:
            old_str = old_val.decode("utf-8", errors="replace")
        except Exception:
            old_str = str(old_val)
    elif old_val is None:
        old_str = ""
    else:
        old_str = str(old_val)

    new_str = old_str
    changed = False

    for key, value in (edit_pairs or {}).items():
        key_escaped = re.escape(key)
        # Match first occurrence either at start or following a pipe
        pattern = rf'(^|\|)\s*{key_escaped}\s*=\s*([^|]*)'

        def _repl(m):
            sep = m.group(1)  # '' or '|'
            # Keep the original separator; add a space after if missing
            sep_out = f'{sep} ' if sep == '|' else ''
            return f'{sep_out}{key} = {value}'

        new_once, n_subs = re.subn(pattern, _repl, new_str, count=1)

        if n_subs == 0:
            # Key not present
            if append_missing:
                if new_str.strip():
                    new_str = f'{new_str} | {key} = {value}'
                else:
                    new_str = f'{key} = {value}'
                changed = True
            # else: do nothing (do not append into macro/geometry-only descriptions)
        else:
            if new_once != new_str:
                changed = True
                new_str = new_once

    if changed:
        ifd_set_tag(ifd, tag_code, new_str)

    return old_str, new_str, changed


def human_tag_name(code: int) -> str:
    for name, c in TAGCODES.items():
        if c == code:
            return name
    return f"Tag{code}"

def main():
    ap = argparse.ArgumentParser(
        description="Lossless editor for metadata in Aperio/Leica SVS (pyramidal TIFF) files."
    )
    ap.add_argument("input", help="Input .svs or .tif")
    ap.add_argument("output", help="Output .svs or .tif (will be written)")
    ap.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    ap.add_argument(
        "--set",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="[LEGACY] Set key/value inside ImageDescription by *rebuilding* the kv list (order not preserved).",
    )
    ap.add_argument(
        "--edit-desc",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="Edit ImageDescription by *regex substitution*, preserving order and spacing. Repeatable.",
    )
    ap.add_argument(
        "--append-missing",
        action="store_true",
        help="Append KEY=VALUE if the key is absent in an ImageDescription (default: edit existing keys only).",
    )
    ap.add_argument(
        "--replace-description",
        metavar="TEXT",
        help="Replace the entire ImageDescription (tag 270) with TEXT (advanced).",
    )
    ap.add_argument(
        "--tifftag",
        action="append",
        default=[],
        metavar="CODE_OR_NAME=VALUE",
        help="Set a standard TIFF tag by numeric code or common name (e.g., 305=MyTool, Software=MyTool). Can repeat.",
    )
    ap.add_argument(
        "--xmp",
        metavar="PATH",
        help="Replace or set XMP (tag 700) with the contents of the provided file.",
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would change without writing the output file.",
    )
    args = ap.parse_args()

    if not os.path.exists(args.input):
        print(f"Input not found: {args.input}", file=sys.stderr)
        sys.exit(2)

    # Read
    info = tifftools.read_tiff(args.input)
    ifds = info.get("ifds", [])
    if not ifds:
        print("No IFDs found; not a valid TIFF/SVS?", file=sys.stderr)
        sys.exit(2)
    ifd0 = ifds[0]

    changes: List[str] = []

    # 1) ImageDescription edits (regex-preserving mode)
    # Collect KEY=VALUE pairs from --edit-desc
    edit_pairs: Dict[str, str] = {}
    if hasattr(args, "edit_desc") and args.edit_desc:
        for item in args.edit_desc:
            if "=" not in item:
                print(f"--edit-desc expects KEY=VALUE, got: {item}", file=sys.stderr)
                sys.exit(2)
            k, v = item.split("=", 1)
            edit_pairs[k.strip()] = v.strip()

    # Apply to every IFD
    for idx, ifd in enumerate(ifds):
        old, new, changed = update_imagedescription_regex(
            ifd,
            edit_pairs,
            append_missing=args.append_missing,  # <- controls whether we add new keys
        )
        if changed:
            changes.append(
                f"IFD{idx} ImageDescription(270):\n"
                f"  OLD: {repr(old)[:2000]}\n"
                f"  NEW: {repr(new)[:2000]}"
            )

    # 2) Legacy set/rebuild mode
    # (kept for backward compatibility; order may change)
    if args.set and args.replace_description is None and not edit_pairs:
        # Only use legacy mode if no --edit-desc was supplied
        # Import here to avoid top-level dependency on parsing helpers
        def parse_aperio_desc(desc: str):
            parts = [p.strip() for p in desc.split("|")]
            kv = {}
            preamble = []
            for p in parts:
                if "=" in p:
                    k, v = p.split("=", 1)
                    kv[k.strip()] = v.strip()
                elif p:
                    preamble.append(p)
            header = " | ".join(preamble) if preamble else ""
            return header, kv

        def build_aperio_desc(header: str, kv: Dict[str, str]) -> str:
            segments = []
            if header:
                segments.append(header.strip())
            for k in sorted(kv.keys()):
                segments.append(f"{k} = {kv[k]}")
            return " | ".join(segments)

        code = TAGCODES["ImageDescription"]
        tag = ifd_find_tag(ifd0, code)
        old_val = tag.get("data") if tag else None
        if isinstance(old_val, (bytes, bytearray)):
            old_val = old_val.decode("utf-8", errors="replace")

        set_pairs = {}
        for item in args.set:
            if "=" not in item:
                print(f"--set expects KEY=VALUE, got: {item}", file=sys.stderr)
                sys.exit(2)
            k, v = item.split("=", 1)
            set_pairs[k.strip()] = v.strip()

        header, kv = parse_aperio_desc(old_val or "")
        kv.update(set_pairs)
        new_val = build_aperio_desc(header, kv) if (header or kv) else old_val
        if new_val != old_val:
            ifd_set_tag(ifd0, code, new_val)
            changes.append("ImageDescription(270) rebuilt (order may change)")

    # 3) Replace whole description
    if args.replace_description is not None:
        code = TAGCODES["ImageDescription"]
        ifd_set_tag(ifd0, code, args.replace_description)
        changes.append("ImageDescription(270) replaced entirely")

    # 4) Arbitrary TIFF tags
    for item in args.tifftag:
        if "=" not in item:
            print(f"--tifftag expects CODE_OR_NAME=VALUE, got: {item}", file=sys.stderr)
            sys.exit(2)
        key, val = item.split("=", 1)
        key = key.strip()
        val = val.strip()
        if key.isdigit():
            code = int(key)
        else:
            if key not in TAGCODES:
                print(f"Unknown tag name '{key}'. Known names: {', '.join(sorted(TAGCODES.keys()))}", file=sys.stderr)
                sys.exit(2)
            code = TAGCODES[key]
        old_tag = ifd_find_tag(ifd0, code)
        old_val = old_tag.get("data") if old_tag else None
        ifd_set_tag(ifd0, code, val)
        changes.append(f"{human_tag_name(code)}({code}): {repr(old_val)} -> {repr(val)}")

    # 5) XMP
    if args.xmp:
        xmp_bytes = load_xmp(args.xmp)
        old_tag = ifd_find_tag(ifd0, TAGCODES["XMP"])
        old_val = old_tag.get("data") if old_tag else None
        ifd_set_tag(ifd0, TAGCODES["XMP"], xmp_bytes)
        changes.append(f"XMP(700): {'present' if old_val else 'absent'} -> {len(xmp_bytes)} bytes")

    if not changes:
        print("No changes requested; nothing to do.")
        return

    print("Planned changes:")
    for ch in changes:
        print(" -", ch.replace("\n", "\n   "))

    if args.dry_run:
        print("\nDry-run mode: not writing output.")
        return

    # Write without touching tile data
    try:
        tifftools.write_tiff(info, args.output, allowExisting=False)
    except Exception as e:
        print(f"Failed to write output: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"\nWrote: {args.output}")
    print("Tip: validate with 'openslide-show-properties' or 'vipsheader -a'.")

if __name__ == "__main__":
    main()
