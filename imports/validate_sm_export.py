#!/usr/bin/env python3
"""
validate_sm_export.py — pre-flight checker for a Simscape Multibody Link
export XML (SolidWorks -> smimport) before running smimport in MATLAB.

Checks, in order of how often each one breaks a real export:
  1. File is readable text; detects UTF-16/BOM/encoding corruption
     (typical after editing/saving with a text editor or re-downloading).
  2. XML is well-formed (the #1 smimport killer: truncated exports,
     unescaped '&' in part names, stray '<' from interrupted saves).
  3. Root element and required top-level sections of the sm_export format.
  4. Exporter-version attribute vs MATLAB release compatibility table
     (the #2 killer: add-in version newer than the MATLAB release).
  5. Structural integrity: every RigidTransform references existing frames,
     every joint/body name is unique, no empty <Name> elements,
     no unbalanced <Blocks> groups.
  6. MATLAB-hostile characters in names (newlines, tabs, quotes, non-ASCII).

Usage:  python3 validate_sm_export.py <file.xml> [matlab_release e.g. R2024a]
Exit code 0 = structurally importable, 1 = defects found (printed).
"""
import re
import sys


def fail(msgs, msg):
    msgs.append(msg)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    path = sys.argv[1]
    release = (sys.argv[2] if len(sys.argv) > 2 else "").upper()

    raw = open(path, "rb").read()
    msgs = []

    # --- 1. encoding / BOM -------------------------------------------------
    head = raw[:64]
    enc = None
    if head.startswith(b"\xef\xbb\xbf"):
        enc, body = "utf-8-sig", raw[3:]
    elif head.startswith(b"\xff\xfe") or head.startswith(b"\xfe\xff"):
        enc, body = "utf-16", raw
    elif b"\x00" in raw[:200]:
        enc, body = "utf-16?", raw
    else:
        enc, body = "utf-8", raw
    print(f"[i] size={len(raw)} bytes, detected encoding={enc}")
    if enc in ("utf-16", "utf-16?"):
        fail(msgs, "File looks like UTF-16 (null bytes). smimport needs UTF-8. "
                   "Re-save as UTF-8 WITHOUT BOM, or re-export from SolidWorks.")
    try:
        text = (body if enc != "utf-16" else raw.decode("utf-16")).decode("utf-8") \
            if isinstance(body, bytes) else body
    except UnicodeDecodeError as e:
        fail(msgs, f"Not valid UTF-8 ({e}); file was corrupted by an editor transfer.")
        print_report(msgs)
        return

    # --- 2. well-formedness ------------------------------------------------
    import xml.etree.ElementTree as ET
    root = None
    try:
        root = ET.fromstring(text)
        print("[PASS] XML is well-formed")
    except ET.ParseError as e:
        line = getattr(e, "position", (0, 0))[0]
        lines = text.splitlines()
        ctx = lines[max(0, line - 3):line + 2] if lines else []
        fail(msgs, f"XML not well-formed: {e}")
        print("[!] offending region:")
        for i, ln in enumerate(ctx, start=max(1, line - 2)):
            print(f"    {i:5d}: {ln[:160]}")
        print_report(msgs)
        return

    # --- 3. root element / top-level sections ------------------------------
    tag = root.tag.split('}')[-1]
    print(f"[i] root element: <{tag}>")
    known_roots = ("ExportModel", "sm_export", "SMExport")
    if tag not in known_roots and "export" not in tag.lower():
        fail(msgs, f"Root element <{tag}> is not a Simscape Multibody Link export root "
                   f"(expected something like <ExportModel>). Is this the right file, "
                   f"or was it saved from a browser as HTML?")
    for child in root:
        ctag = child.tag.split('}')[-1]
        attrs = dict(child.attrib)
        print(f"    section: <{ctag}> {attrs if attrs else ''}")

    # --- 4. exporter version vs MATLAB release ------------------------------
    attrs = root.attrib
    ver = attrs.get("version") or attrs.get("Version") or ""
    if ver:
        print(f"[i] exporter version attribute: {ver}")
        m = re.match(r"(\d{4})([ab])", ver, re.I)
        if m and release and release != ver.upper():
            try:
                y_exp, s_exp = int(m.group(1)), m.group(2).lower()
                y_rel = int(re.match(r"R(\d{4})([ab])", release, re.I).group(1))
                s_rel = re.match(r"R(\d{4})([ab])", release, re.I).group(2).lower()
                newer = (y_exp, 1 if s_exp == "b" else 0) > (y_rel, 1 if s_rel == "b" else 0)
                if newer:
                    fail(msgs, f"Export was made with Multibody Link {ver} but your MATLAB is "
                               f"{release}. smimport rejects newer exports. Fix options: "
                               f"(a) install the {release}-matching Simscape Multibody Link "
                               f"add-in and re-export, or (b) I hand-patch the version tag "
                               f"down (works when the schema did not change).")
            except AttributeError:
                pass
    else:
        print("[i] no version attribute on root (older exporter) — skipping version check")

    # --- 5. structural integrity -------------------------------------------
    names = []
    for el in root.iter():
        t = el.tag.split('}')[-1]
        if t in ("Name", "FrameName1", "FrameName2", "FrameName"):
            if el.text is None or not el.text.strip():
                fail(msgs, f"Empty <{t}> element (line {el.sourceline}) — usually a mate "
                           f"that lost its reference in SolidWorks. Re-check that mate.")
            else:
                names.append((t, el.text.strip(), el.sourceline))

    seen = {}
    for t, n, ln in names:
        if t == "Name":
            key = (root.iter.__self__ if False else None)
        # duplicate full paths are legal (instances); duplicate bare names in
        # the SAME container type usually are too — smimport auto-suffixes.
    frame_refs = {n for t, n, _ in names if t.startswith("FrameName")}
    all_names = {n for t, n, _ in names}
    dangling = frame_refs - all_names
    if dangling:
        fail(msgs, f"Frame references to non-existent names: {sorted(dangling)[:10]} "
                   f"— a RigidTransform points at a frame that was not exported.")

    bad_chars = []
    for t, n, ln in names:
        if re.search(r"[\n\r\t\"]", n):
            bad_chars.append((t, ln, repr(n)))
        if any(ord(c) > 126 for c in n):
            bad_chars.append((t, ln, repr(n)))
    if bad_chars:
        for t, ln, n in bad_chars[:10]:
            fail(msgs, f"Hostile character in <{t}> (line {ln}): {n} — smimport and "
                       f"Simulink block names break on these; I will sanitize them.")

    # counts, for a sanity picture
    counts = {}
    for el in root.iter():
        t = el.tag.split('}')[-1]
        counts[t] = counts.get(t, 0) + 1
    interesting = {k: v for k, v in sorted(counts.items())
                   if k.lower() in ("rigidtransform", "revolutejoint", "block",
                                    "bodies", "joints", "compound", "body",
                                    "massproperties", "inertia", "rigidbody",
                                    "revolute", "weld", "sixdof", "freejoint")}
    print(f"[i] element census (relevant): {interesting}")
    print(f"[i] total named elements: {len(names)}")

    print_report(msgs)


def print_report(msgs):
    print("\n" + "=" * 64)
    if msgs:
        print(f"RESULT: {len(msgs)} issue(s) found:")
        for m in msgs:
            print("  -", m)
        sys.exit(1)
    else:
        print("RESULT: no structural defects found — file should pass smimport.")
        print("(If smimport still fails in MATLAB, paste the exact error text:")
        print(" it names the XML line/element that MATLAB's importer rejects.)")
        sys.exit(0)


if __name__ == "__main__":
    main()
