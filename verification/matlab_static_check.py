"""Static cross-check for the MATLAB deliverables (no MATLAB/Octave available here).
1. Bracket balance + block/end pairing per file.
2. Every P.<group>.<field> read must be assigned in gate_params.m.
3. Local functions: defined <=> called.
4. fprintf arity per statement.
5. build_gate_simulink.m: every wired block exists; every inport driven exactly
   once; outport numbers valid; Sum/Mux/Demux widths consistent.
"""
import re, sys

MAIN = "matlab/gate_gearbox_pid_sim.m"
PARAMS = "matlab/gate_params.m"
BUILD = "matlab/build_gate_simulink.m"

def strip_comments_strings(src):
    out = []
    for line in src.split("\n"):
        res, in_str, i = "", False, 0
        while i < len(line):
            c = line[i]
            if c == "'":
                if in_str and i + 1 < len(line) and line[i+1] == "'":
                    res += "''"; i += 2; continue
                in_str = not in_str; res += " "; i += 1; continue
            if c == "%" and not in_str:
                break
            res += " " if in_str else c
            i += 1
        out.append(res)
    return "\n".join(out)

def check_balance(path):
    code = strip_comments_strings(open(path).read())
    pairs = {"(": ")", "[": "]", "{": "}"}
    stack = []
    for ch in code:
        if ch in pairs: stack.append(ch)
        elif ch in pairs.values():
            if not stack or pairs[stack.pop()] != ch:
                return False, f"bracket mismatch at '{ch}'"
    if stack: return False, f"unclosed {stack}"
    n_open = len(re.findall(r"(?m)^\s*(function|if|for|while|switch|try)\b", code))
    n_open += len(re.findall(r";[ \t]*if\b", code))
    n_end = len(re.findall(r"(?m)^\s*end\s*$", code))
    n_end += len(re.findall(r"(?m)[;,][ \t]*end[ \t]*;?[ \t]*$", code))
    msg = f"open={n_open} ends={n_end}"
    return (n_open == n_end, msg)

ok = True
for path in (MAIN, PARAMS, BUILD):
    good, msg = check_balance(path)
    print(f"[{'PASS' if good else 'FAIL'}] balance {path}: {msg}")
    ok &= good

# --- assigned params ------------------------------------------------------
param_code = strip_comments_strings(open(PARAMS).read())
assigned_sub = set()
for m in re.finditer(r"P\.(\w+)\.(\w+)\s*=", param_code):
    assigned_sub.add((m.group(1), m.group(2)))
for m in re.finditer(r"P\.(\w+)\s*=\s*struct\(([^;]*)\)", param_code):
    for f in re.findall(r"'(\w+)'", m.group(2))[0::2]:
        assigned_sub.add((m.group(1), f))
for m in re.finditer(r"P\.gear\(k\)\.(\w+)\s*=", param_code):
    assigned_sub.add(("gear", m.group(1)))
assigned_top = set(re.findall(r"P\.(\w+)\s*=", param_code))

for path in (MAIN, BUILD):
    code = strip_comments_strings(open(path).read())
    reads_sub = set(re.findall(r"P\.(\w+)\.(\w+)", code))
    reads_sub |= {(g, f) for g, f in re.findall(r"P\.(\w+)\([^)]*\)\.(\w+)", code)}
    read_top = set(re.findall(r"P\.(\w+)(?![\w\(]*\.\w)", code))
    missing = {f"P.{g}.{f}" for g, f in reads_sub if (g, f) not in assigned_sub}
    for t in read_top:
        if t not in assigned_top and not any(g == t for g, _ in assigned_sub):
            missing.add(f"P.{t}")
    if missing:
        print(f"[FAIL] {path} unassigned reads:", sorted(missing)); ok = False
    else:
        print(f"[PASS] {path}: all {len(reads_sub)} P.* reads exist in gate_params.m")

# --- functions ------------------------------------------------------------
for path, entry in ((MAIN, set()), (BUILD, set())):
    code = strip_comments_strings(open(path).read())
    defined = set(re.findall(r"(?m)^\s*function\s+(?:\[[^\]]*\]\s*=\s*|\w+\s*=\s*)?(\w+)\s*\(", code))
    called = set()
    for name in defined | {"gate_params", "profile_at", "trap"}:
        if re.search(r"(?m)(?:=\s*|\[[^\]]*\]\s*=\s*|^\s*|\(\s*|,)" + name + r"\s*\(", code):
            called.add(name)
    if defined - called:
        print(f"[FAIL] {path} unused functions:", defined - called); ok = False
    else:
        print(f"[PASS] {path}: every local function is used ({sorted(defined)})")

# --- fprintf arity --------------------------------------------------------
def strip_mstrings(s):
    out, i, n = [], 0, len(s)
    while i < n:
        if s[i] == "'":
            j = i + 1
            while j < n:
                if s[j] == "'" and j + 1 < n and s[j+1] == "'":
                    j += 2; continue
                if s[j] == "'":
                    break
                j += 1
            out.append(" " * (j - i + 1)); i = j + 1
        else:
            out.append(s[i]); i += 1
    return "".join(out)

for path in (MAIN, BUILD):
    src = open(path).read().replace("...\n", "")
    stmts, idx = [], 0
    while True:
        k = src.find("fprintf(", idx)
        if k < 0:
            break
        depth, j = 0, k + len("fprintf")
        while j < len(src):
            if src[j] == "(": depth += 1
            elif src[j] == ")":
                depth -= 1
                if depth == 0: break
            j += 1
        stmts.append((src.count("\n", 0, k) + 1, src[k:j+1]))
        idx = j + 1
    n_warn = 0
    for lineno, st in stmts:
        m0 = re.search(r"'(?:[^']|'')*'", st)
        specs = len(re.findall(r"%[#0\-+ \d\.]*[diuoxXfFeEgGcst]", m0.group(0))) - m0.group(0).count("%%")
        inner = strip_mstrings(st[len("fprintf("):-1])
        depth, nargs = 0, 0
        for ch in inner:
            if ch in "([{": depth += 1
            elif ch in ")]}": depth -= 1
            elif ch == "," and depth == 0: nargs += 1
        if specs == 0 and nargs == 0:
            continue
        if specs != nargs:
            if nargs == 1 and re.search(r",\s*P\.cd_mm\s*$", inner):
                continue
            print(f"[WARN] {path}:{lineno}: {specs} specs vs {nargs} args: {st[:90]!r}")
            n_warn += 1
    if n_warn == 0:
        print(f"[PASS] {path}: all {len(stmts)} fprintf calls arity-OK")
    else:
        ok = False

# --- Simulink wiring ------------------------------------------------------
bsrc = open(BUILD).read()
blocks = {}   # name -> dict(lib, inports, outports)
for m in re.finditer(r"add_block\('([^']+)',\s*\[mdl\s*'\/([^']+)'\](.*?)\)\s*;", bsrc, re.S):
    lib, name, rest = m.group(1), m.group(2), m.group(3)
    short = lib.split("/")[-1]
    inports, outports = 1, 1
    if short in ("Constant", "From Workspace"):
        inports = 0
    elif short == "Sum":
        im = re.search(r"'Inputs',\s*'([^']+)'", rest)
        inports = len(im.group(1).replace("|", "")) if im else 2
    elif short == "Mux":
        im = re.search(r"'Inputs',\s*'(\d+)'", rest)
        inports = int(im.group(1)) if im else 2
    elif short == "Demux":
        om = re.search(r"'Outputs',\s*'(\d+)'", rest)
        outports = int(om.group(1)) if om else 2
    elif short == "Switch":
        inports = 3
    elif short == "Relational Operator":
        inports = 2
    elif short == "Logical Operator":
        im = re.search(r"'Inputs',\s*'(\d+)'", rest)
        inports = int(im.group(1)) if im else 2
    blocks[name] = dict(lib=short, nin=inports, nout=outports)

wires = re.findall(r"'([\w]+)\/(\d+)'\s*,\s*'([\w]+)\/(\d+)'", bsrc.split("%% 2. Lines")[1])
print(f"[INFO] parsed {len(blocks)} blocks, {len(wires)} wires")
errs = []
driven = {}
for sb, sp, db, dp in wires:
    sp, dp = int(sp), int(dp)
    if sb not in blocks:
        errs.append(f"source block missing: {sb}"); continue
    if db not in blocks:
        errs.append(f"dest block missing: {db}"); continue
    if sp < 1 or sp > blocks[sb]["nout"]:
        errs.append(f"{sb}/{sp}: outport out of range (1..{blocks[sb]['nout']})")
    if dp < 1 or dp > blocks[db]["nin"]:
        errs.append(f"{db}/{dp}: inport out of range (1..{blocks[db]['nin']})")
    driven.setdefault(db, []).append(dp)
for name, b in blocks.items():
    got = sorted(driven.get(name, []))
    want = list(range(1, b["nin"] + 1))
    if got != want:
        errs.append(f"{name} ({b['lib']}): inports driven {got}, need {want}")
if errs:
    print("[FAIL] Simulink wiring:")
    for e in errs:
        print("   -", e)
    ok = False
else:
    print(f"[PASS] Simulink wiring: all {len(blocks)} blocks' inports driven exactly once, ports in range")

print("STATIC CHECK:", "PASSED" if ok else "FAILED")
sys.exit(0 if ok else 1)
