"""Repair local label scopes after Advanced code with global labels was inserted into the middle
of original routines.

vasm scopes local labels (.x) by the last global label. A new global label inside an original
routine splits the routine. For every original routine:
 * find local labels which are referenced in one part but defined in another part,
 * if a new global label between them is only referenced inside the routine, make it local,
 * otherwise make the crossing local label global (Routine_Label).
"""
import glob, os, re
import symbols

LOCAL = re.compile(r'(?<![\w])(\.[A-Za-z_]\w*)')
LOCAL_DEF = re.compile(r'^(\.[A-Za-z_]\w*)')
NOT_LABEL = re.compile(r'^\w+\s+(equ|=|rs\.|macro|set)\b', re.I)


def _globals(lines):
    gl = []
    for i, line in enumerate(lines):
        code, _ = symbols.strip_comment(line)
        m = symbols.GLOBAL_DEF.match(code)
        if m and not NOT_LABEL.match(code):
            gl.append((i, m.group(1)))
    return gl


def _refs_outside(name, texts, p, rs, re_):
    pat = re.compile(r'(?<![\w.])' + re.escape(name) + r'(?![\w])')
    for q, ls in texts.items():
        for j, line in enumerate(ls):
            if pat.search(symbols.strip_comment(line)[0]) and not (q == p and rs <= j < re_):
                return True
    return False


def _rename_in(lines, rs, re_, old, new):
    pat = re.compile(r'(?<![\w.])' + re.escape(old) + r'(?![\w])')
    for j in range(rs, re_):
        code, comment = symbols.strip_comment(lines[j])
        if pat.search(code):
            lines[j] = pat.sub(new, code) + comment


def fix_scopes(target, new_globals, orig_globals=None):
    """orig_globals: global labels of the unchanged source (routine boundaries). All other global
    labels are treated as inserted."""
    files = glob.glob(os.path.join(target, '**', '*.S'), recursive=True)
    texts, nls = {}, {}
    for p in files:
        raw = open(p, 'rb').read()
        nls[p] = '\r\n' if b'\r\n' in raw else '\n'
        texts[p] = raw.decode('latin1').replace('\r\n', '\n').split('\n')
    log = []
    pinned = set()       # labels made global by this repair: never localize them again
    all_globals = set()
    for ls in texts.values():
        all_globals |= {n for _, n in _globals(ls)}
    for p in files:
        lines = texts[p]
        changed_file = False
        rounds = 0
        while True:
            rounds += 1
            if rounds > 500:
                log.append(('scope-repair-aborted', os.path.relpath(p, target), '', ''))
                break
            gl = _globals(lines)
            if orig_globals is not None:
                orig = [(i, n) for i, n in gl if n in orig_globals]
                new_globals = set(n for _, n in gl if n not in orig_globals) | set(new_globals)
            else:
                orig = [(i, n) for i, n in gl if n not in new_globals]
            progress = False
            for k, (rs, rname) in enumerate(orig):
                re_ = orig[k + 1][0] if k + 1 < len(orig) else len(lines)
                bounds = [i for i, n in gl if rs < i < re_]
                if not bounds:
                    continue
                cuts = [rs] + bounds + [re_]
                seg_of = lambda j: max(s for s in range(len(cuts) - 1) if cuts[s] <= j)
                defs, refs = {}, []
                for j in range(rs, re_):
                    code, _ = symbols.strip_comment(lines[j])
                    if not code.strip():
                        continue
                    md = LOCAL_DEF.match(code)
                    if md:
                        defs.setdefault(md.group(1), set()).add(seg_of(j))
                    for m in LOCAL.finditer(code):
                        if md and m.start() == 0:
                            continue
                        refs.append((m.group(1), seg_of(j)))
                crossing = []
                for name, s in refs:
                    ds = defs.get(name)
                    if not ds or s in ds:
                        continue
                    d = min(ds, key=lambda x: abs(x - s))
                    crossing.append((name, s, d))
                if not crossing:
                    continue
                # boundaries which break at least one crossing reference
                breaking = set()
                for name, s, d in crossing:
                    for b in range(min(s, d) + 1, max(s, d) + 1):
                        breaking.add(b)   # cut index b = boundary cuts[b]
                localizable = []
                for b in sorted(breaking):
                    i = cuts[b]
                    name = next(n for ii, n in gl if ii == i)
                    if name in new_globals and name not in pinned and not _refs_outside(name, texts, p, rs, re_):
                        localizable.append(name)
                if localizable:
                    name = localizable[0]
                    _rename_in(lines, rs, re_, name, '.' + name)
                    log.append(('localized', os.path.relpath(p, target), rname, name))
                else:
                    name = crossing[0][0]
                    new = '%s_%s' % (rname, name[1:])
                    n = 2
                    while new in all_globals:
                        new = '%s_%s%d' % (rname, name[1:], n); n += 1
                    all_globals.add(new)
                    pinned.add(new)
                    # rename the definition in segment d and the references which resolve to it:
                    # references in segment d and in segments without an own definition of the name
                    d = crossing[0][2]
                    ds = defs[name]
                    pat = re.compile(r'(?<![\w.])' + re.escape(name) + r'(?![\w])')
                    for j in range(rs, re_):
                        s = seg_of(j)
                        if s != d and (s in ds or min(ds, key=lambda x: abs(x - s)) != d):
                            continue
                        code, comment = symbols.strip_comment(lines[j])
                        if pat.search(code):
                            lines[j] = pat.sub(new, code) + comment
                    log.append(('globalized', os.path.relpath(p, target), rname, '%s -> %s' % (name, new)))
                progress = True
                changed_file = True
                break
            if not progress:
                break
        if changed_file:
            open(p, 'wb').write(nls[p].join(lines).encode('latin1'))
    return log
