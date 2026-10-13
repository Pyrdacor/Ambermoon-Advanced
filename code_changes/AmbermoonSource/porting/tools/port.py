"""Apply the automatically applicable hunks of plan.json to the AmbermoonSource copy.

usage: port.py <target src dir>
Writes port_log.txt (applied / skipped hunks with reasons) next to plan.json.
"""
import json, os, re, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import srcmodel, symbols
from plan import git_diff_linemap

W = srcmodel.W
IDENT = re.compile(r'(?<![\w$.\\])(\.?[A-Za-z_][\w]*(?:\.[A-Za-z_][\w]*)?)')
DEF = re.compile(r'^(\.?[A-Za-z_][\w]*)(:?)')


def manual_key(h):
    """Stable key of a hunk: first base line and first Advanced line."""
    return (h['base_lines'][0], h['adv_lines'][0])


# Hunks which need a decision. Keys: (first base line, first Advanced line) of the hunk.
MANUAL = {
    # Monster knowledge: Advanced plays the animation in a new subroutine and shows the info
    # window afterwards. The moved exit label is not needed (both exits are a plain rts).
    (37387, 40753): {'mode': 'insert', 'drop': ('LAB_0023d62c:',), 'why': 'moved exit label dropped'},
    # New combat spells. FUN_SpellShowMonsterLP was rewritten: the old routine is now only the
    # star animation (FUN_ShowMysticStarsAnimation), the new routine gets the source name.
    (37750, 41171): {'mode': 'insert', 'allow_defs': True,
                     'post': [('COMBAT/COMBAT_M.S', 'CShow_monster_LP:\n; Show the green stars', '; Show the green stars')],
                     'why': 'CShow_monster_LP is the new routine'},
    # Year change: 1.21 already increments Time_data_year (same variable as Advanced's
    # DAT_YearsPassedSince978). Advanced's own increment would count the year twice.
    (22355, 23489): {'mode': 'skip', 'why': 'already fixed in 1.21 (Time_data_year)'},
    # Datachange random values 1...max: the source already has the fix (addq.w #1,d2), Advanced's
    # own fix (addq.w #1,d0) would add 1 twice.
    (25238, 26823): {'mode': 'skip', 'why': 'random value fix already in source'},
    (25257, 26843): {'mode': 'skip', 'why': 'random value fix already in source'},
    (25275, 26862): {'mode': 'skip', 'why': 'random value fix already in source'},
    (25297, 26885): {'mode': 'skip', 'why': 'random value fix already in source'},
    # Remove_member: the source fixed the loops with dbra d1 and sets d1 = Chest_data_file before
    # saving. Advanced fixed it with d7 as counter, which doesn't fit the source loops.
    (26148, 27983): {'mode': 'skip', 'why': 'Remove_member fix already in source'},
    (26167, 28005): {'mode': 'skip', 'why': 'Remove_member fix already in source'},
    (26180, 28019): {'mode': 'skip', 'why': 'Remove_member fix already in source'},
    (26200, 28039): {'mode': 'skip', 'why': 'Remove_member fix already in source'},
    # Copy_data: same btst fix in source and Advanced (keeps the source comments).
    (272946, 276003): {'mode': 'skip', 'why': 'btst fix already in source'},
    (272950, 276007): {'mode': 'skip', 'why': 'btst fix already in source'},
    # Jump target check: 1.21 has it as Check_jump_target / Do_condition_events (#98).
    # Only FUN_ExecuteConditionEventsExcept is new (used by ACTIONS.S).
    (13232, 13973): {'mode': 'insert', 'from_line': 14036, 'why': 'jump check already in 1.21, only ExecuteConditionEventsExcept'},
    # New BSS variable at the end of hunk 2 (Longword_BSS). The insertion point is the start of
    # the next section, so the section is given explicitly.
    (229137, 233444): {'mode': 'insert', 'text': ['\tSECTION\tLongword_BSS,bss',
                                                  'MysticBackupData:',
                                                  '\tds.w\t99\t\t\t; 33 per possible char',
                                                  '\tSECTION\tChip_DATA,data_c'],
                       'why': 'BSS variable in Longword_BSS'},
    # New chip BSS variable at the end of hunk 10 (Chip_BSS2). The insertion point is the start
    # of the Blitter code section, so it is placed in front of that section explicitly.
    (403486, 389871): {'mode': 'skip',
                       'post': [('MAP/3D_BLIT.S', '\tSECTION\tBlitter,code\n',
                                 '\tSECTION\tChip_BSS2,bss_c\nDAT_Random_party_members:\n\tds.b\t6\n\n\tSECTION\tBlitter,code\n')],
                       'why': 'chip BSS variable in Chip_BSS2'},
    # Item data buffer for 600 items.
    (272762, 275819): {'mode': 'replace-line', 'why': 'item buffer 36000 bytes'},
    # New code in the unused space at the end of the Texts code hunk (dcb.b 8322,0).
    (273022, 276111): {'mode': 'replace-line', 'why': 'new code in the unused patch space'},
}


# Advanced names for variables which the source already has under another name (same address).
EQUIV = {
    'DAT_YearsPassedSince978': 'Time_data_year',
}


DATA_SIZE = re.compile(r'^\s+d([sxc])\.([bwl])\s+(.*)$', re.I)


def data_offset_line(text, off):
    """Index of the line in text which starts at byte offset off, if text is plain data."""
    pos = 0
    for k, line in enumerate(text):
        code = symbols.strip_comment(line)[0]
        if code[:1] not in ' \t':
            ld = DEF.match(code)
            code = '\t' + code[ld.end():].lstrip(':').strip() if ld else code
        if not code.strip():
            continue
        if pos == off:
            # put the label before preceding label/comment-only lines
            while k > 0 and not symbols.strip_comment(text[k - 1])[0].strip():
                k -= 1
            return k
        m = DATA_SIZE.match(code)
        if not m:
            return None
        size = {'b': 1, 'w': 2, 'l': 4}[m.group(2).lower()]
        arg = m.group(3).strip()
        if m.group(1).lower() == 'c':
            pos += size * len([x for x in arg.split(',') if x.strip()])
        elif re.fullmatch(r'\d+', arg):
            pos += size * int(arg)
        else:
            return None
        if pos > off:
            return None
    return None


def scope_lines(src, ln):
    """Line numbers of the global label scope around line ln."""
    def is_global(i):
        code = symbols.strip_comment(src[i - 1])[0]
        m = DEF.match(code)
        return m and code[:1] not in ' \t.' and code.strip() and not re.match(r'\s*:?\s*(equ|=|set|macro)\b', code[m.end():], re.I)
    a = ln
    while a > 1 and not is_global(a):
        a -= 1
    b = ln + 1
    while b <= len(src) and not is_global(b):
        b += 1
    return range(a, b)


# Advanced labels which are the same symbol as the source label of the same name (find_aliases
# can't see it because the surrounding lines changed).
EXTRA_ALIASES = {'Party_or_monster'}


def skip_reason(h):
    plus = ' '.join(h['plus']).lower()
    if 'combat_data_size equ' in plus:
        return 'equivalent in source (Combat_data_size is defined at the same address)'
    return None


def find_aliases(M, R, names):
    """Advanced labels named like a source label which sit at the same address as that label."""
    eq = {}
    pb = pa = 0
    for line in open(os.path.join(W, 'canon62.diff'), encoding='latin1'):
        h = re.match(r'^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@', line)
        if not h:
            continue
        b1, bn = int(h.group(1)), int(h.group(2) or 1) if h.group(2) != '0' else 0
        a1, an = int(h.group(3)), int(h.group(4) or 1) if h.group(4) != '0' else 0
        bs = b1 - 1 if bn else b1
        as_ = a1 - 1 if an else a1
        while pa < as_:
            eq[pa + 1] = pb + 1; pa += 1; pb += 1
        pa, pb = as_ + an, bs + bn
    alines = open(os.path.join(W, 'adv.lines'), encoding='latin1').read().split('\n')
    ib = [int(x) for x in open(os.path.join(W, 'base', '62823505.idx'))]
    base62 = open(os.path.join(W, 'base', '62823505.s'), encoding='latin1').read().split('\n')
    base382 = open(os.path.join(W, 'base', '382eaeda.s'), encoding='latin1').read().split('\n')
    m = git_diff_linemap(base62, base382)
    res = set()
    for y in names:
        try:
            k = alines.index(y + ':') + 1
        except ValueError:
            continue
        while k <= len(alines) and k not in eq:
            k += 1
        if k not in eq:
            continue
        l382 = m.get(ib[eq[k] - 1])
        addr = M.b_addr(l382) if l382 else None
        if addr and any(d[2] == y for d in R.src_defs.get(addr, [])):
            res.add(y)
    return res


def localize_inner_globals(target, new_globals):
    """New global labels inserted in the middle of a source routine break the scope of the
    routine's local labels behind them. Per original routine: turn the new global labels which
    have local labels behind them into local labels, if all their references are inside the routine."""
    import glob
    done, manual = [], []
    LOCAL_TOK = re.compile(r'(?<![\w])\.[A-Za-z_]\w*')
    for p in glob.glob(os.path.join(target, '**', '*.S'), recursive=True):
        raw = open(p, 'rb').read()
        nl = '\r\n' if b'\r\n' in raw else '\n'
        lines = raw.decode('latin1').replace('\r\n', '\n').split('\n')
        gl = []
        for i, line in enumerate(lines):
            code, _ = symbols.strip_comment(line)
            m = symbols.GLOBAL_DEF.match(code)
            if m and not re.match(r'^\w+\s+(equ|=|rs\.|macro)', code, re.I):
                gl.append((i, m.group(1)))
        orig = [(i, n) for i, n in gl if n not in new_globals]
        changed = False
        for k, (rs, rname) in enumerate(orig):
            re_ = orig[k + 1][0] if k + 1 < len(orig) else len(lines)
            inner = [(i, n) for i, n in gl if rs < i < re_ and n in new_globals]
            if not inner:
                continue
            problem = []
            for i, n in inner:
                if any(LOCAL_TOK.search(symbols.strip_comment(lines[j])[0]) for j in range(i + 1, re_)):
                    problem.append(n)
            if not problem:
                continue
            # all references of the problematic labels inside the routine?
            outside = []
            for n in problem:
                pat = re.compile(r'(?<![\w.])' + re.escape(n) + r'(?![\w])')
                for q in glob.glob(os.path.join(target, '**', '*.S'), recursive=True):
                    ls = lines if q == p else open(q, encoding='latin1').read().replace('\r\n', '\n').split('\n')
                    for j, line in enumerate(ls):
                        if pat.search(symbols.strip_comment(line)[0]) and not (q == p and rs <= j < re_):
                            outside.append(n); break
                    if n in outside:
                        break
            if outside:
                manual.append((os.path.relpath(p, target), rname, ','.join(outside)))
                continue
            for n in problem:
                pat = re.compile(r'(?<![\w.])' + re.escape(n) + r'(?![\w])')
                for j in range(rs, re_):
                    code, comment = symbols.strip_comment(lines[j])
                    lines[j] = pat.sub('.' + n, code) + comment
                done.append((os.path.relpath(p, target), n))
            changed = True
        if changed:
            open(p, 'wb').write(nl.join(lines).encode('latin1'))
    return done, manual


TERMINATORS = re.compile(r'^\s+(rts|rte|bra(\.[bswl])?|jmp)\b', re.I)
LOCAL_TOK = re.compile(r'(?<![\w])\.[A-Za-z_]\w*')


def added_ranges(pristine, current):
    """Line ranges (1-based, inclusive) of lines added in current compared to pristine."""
    import tempfile
    r = subprocess.run(['git', 'diff', '--no-index', '-U0', pristine, current], capture_output=True, text=True, encoding='latin1')
    res = []
    for line in r.stdout.split('\n'):
        h = re.match(r'^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@', line)
        if h:
            s = int(h.group(1)); n = int(h.group(2) or 1) if h.group(2) != '0' else 0
            if n:
                res.append((s, s + n - 1))
    return res


def relocate_inner_subroutines(target, pristine_dir, scope_manual):
    """Move Advanced subroutines which were inserted into the middle of an original routine
    in front of that routine, if the control flow allows it."""
    moved, still = [], []
    by_file = {}
    for f, r, labs in scope_manual:
        by_file.setdefault(f, []).append((r, labs.split(',')))
    for f, items in by_file.items():
        p = os.path.join(target, f)
        raw = open(p, 'rb').read()
        nl = '\r\n' if b'\r\n' in raw else '\n'
        lines = raw.decode('latin1').replace('\r\n', '\n').split('\n')
        added = added_ranges(os.path.join(pristine_dir, f), p)
        for rname, labs in items:
            for lab in labs:
                # current line of the label
                li = next((i for i, l in enumerate(lines) if re.match(re.escape(lab) + r':', l)), None)
                rs = next((i for i, l in enumerate(lines) if re.match(re.escape(rname) + r':', l)), None)
                if li is None or rs is None:
                    still.append((f, rname, lab, 'not found')); continue
                rng = next(((s - 1, e - 1) for s, e in added if s - 1 <= li <= e - 1), None)
                if rng is None:
                    still.append((f, rname, lab, 'not inside added lines')); continue
                # block: from the label (plus directly preceding added comment lines) to the end of the added range
                bs = li
                while bs - 1 >= rng[0] and (not lines[bs - 1].strip() or lines[bs - 1].lstrip().startswith(';')):
                    bs -= 1
                be = rng[1]
                code_lines = [l for l in lines[bs:be + 1] if symbols.strip_comment(l)[0].strip()]
                prev = next((lines[i] for i in range(bs - 1, rs, -1) if symbols.strip_comment(lines[i])[0].strip()), '')
                ok_before = bool(TERMINATORS.match(symbols.strip_comment(prev)[0]))
                ok_after = bool(code_lines) and bool(TERMINATORS.match(symbols.strip_comment(code_lines[-1])[0]))
                block_defs = {m.group(0) for l in lines[bs:be + 1] for m in [re.match(r'^\.[A-Za-z_]\w*', symbols.strip_comment(l)[0])] if m}
                block_refs = {t for l in lines[bs:be + 1] for t in LOCAL_TOK.findall(symbols.strip_comment(l)[0])}
                # references to routine locals from inside the block, or to block locals from outside
                outside_refs = set()
                re_end = next((i for i in range(be + 1, len(lines)) if symbols.GLOBAL_DEF.match(symbols.strip_comment(lines[i])[0])), len(lines))
                for i in list(range(rs, bs)) + list(range(be + 1, re_end)):
                    outside_refs |= set(LOCAL_TOK.findall(symbols.strip_comment(lines[i])[0]))
                if not ok_before or not ok_after or (block_refs - block_defs) or (outside_refs & block_defs):
                    still.append((f, rname, lab, 'flow' if not (ok_before and ok_after) else 'locals'))
                    continue
                block = lines[bs:be + 1]
                del lines[bs:be + 1]
                # insert in front of the routine and its header comment
                ins = rs
                while ins > 0 and lines[ins - 1].lstrip().startswith(';'):
                    ins -= 1
                lines[ins:ins] = block + ['']
                added = [(s, e) for s, e in added]  # positions changed: recompute
                open(p, 'wb').write(nl.join(lines).encode('latin1'))
                added = added_ranges(os.path.join(pristine_dir, f), p)
                moved.append((f, rname, lab))
        open(p, 'wb').write(nl.join(lines).encode('latin1'))
    return moved, still


def main():
    target = sys.argv[1]
    M = srcmodel.load()
    R = symbols.Resolver(M)
    H = json.load(open(os.path.join(W, 'plan.json')))
    adv = open(os.path.join(W, 'adv.s'), encoding='latin1').read().split('\n')
    ia = [int(x) for x in open(os.path.join(W, 'adv.idx'))]
    blines62 = open(os.path.join(W, 'base', '62823505.lines'), encoding='latin1').read().split('\n')
    m62_382 = git_diff_linemap(open(os.path.join(W, 'base', '62823505.s'), encoding='latin1').read().split('\n'),
                               open(os.path.join(W, 'base', '382eaeda.s'), encoding='latin1').read().split('\n'))
    # adv scope per raw line
    scope_of = []
    scope = ''
    for line in adv:
        code, _ = symbols.strip_comment(line)
        m = symbols.GLOBAL_DEF.match(code)
        if m:
            scope = m.group(1)
        scope_of.append(scope)
    # head line maps per file (1.21 source -> current copy)
    head = {}
    def to_head(f, ln):
        if f not in head:
            old = M.src_lines(f)
            new = open(os.path.join(target, f), encoding='latin1').read().split('\n')
            head[f] = git_diff_linemap(old, new)
        return head[f].get(ln)
    # renames for new Advanced globals that collide with source names
    new_globals = {x for x in R.adv_labels if '.' not in x and x not in R.adv2base and x not in R.base_labels}
    # new Advanced labels with the name of a source label at the same address are the same symbol
    aliases = find_aliases(M, R, new_globals & R.src_globals) | EXTRA_ALIASES
    grename = {x: x + '_Adv' for x in new_globals if x in R.src_globals and x not in aliases}
    edits = {}   # file -> list of (start_line, end_line_exclusive, new_lines, hunk_id)
    log = []
    local_renames = {}
    scope_used = {}

    def translate(raw_lines, raw_first, tf, tscope, region=False):
        region_defs = set()
        if region:
            for k, line in enumerate(raw_lines):
                code, _ = symbols.strip_comment(line)
                m = DEF.match(code)
                if m and code[:1] not in ' \t' and code.strip():
                    lab = m.group(1)
                    region_defs.add(scope_of[raw_first + k - 1] + lab if lab.startswith('.') else lab)
        out = []
        problems = []
        for k, line in enumerate(raw_lines):
            no = raw_first + k
            code, comment = symbols.strip_comment(line)
            ascope = scope_of[no - 1]
            def rep(m):
                tok = m.group(1)
                if tok in EQUIV:
                    return EQUIV[tok]
                q = ascope + tok if tok.startswith('.') else tok
                if q not in R.adv_labels:
                    return tok
                if q in R.adv2base:
                    b = R.adv2base[q]
                elif q in R.base_labels:
                    b = q
                else:
                    if tok.startswith('.'):
                        key = (tf, tscope, ascope, tok)
                        if key not in local_renames:
                            used = scope_used.setdefault((tf, tscope), set(R.src_scope_locals.get((tf, tscope), set())))
                            name = tok
                            n = 1
                            while name in used:
                                n += 1
                                name = '%s_Adv%d' % (tok, n) if n > 2 else tok + '_Adv'
                            used.add(name)
                            local_renames[key] = name
                        return local_renames[key]
                    return grename.get(tok, tok)
                name, why = R.base_to_src(b, tf, tscope)
                if region and q in region_defs and (name is None or '+' in name):
                    # defined by the rewritten region itself and without an own source label
                    return grename.get(tok, tok)
                if name is None:
                    problems.append(why)
                    return tok
                return name
            # label definition at line start
            m = DEF.match(code)
            if m and code[:1] not in ' \t' and code.strip() and m.group(1) in aliases:
                # the source already defines this label at the same address
                rest = code[m.end():].lstrip(':')
                if not rest.strip():
                    if comment.strip():
                        out.append('\t' + comment)
                    continue
                code = '\t' + rest.strip()
                m = None
            if m and code[:1] not in ' \t' and code.strip():
                lab = m.group(1)
                q = ascope + lab if lab.startswith('.') else lab
                if (q in R.adv2base or (q in R.base_labels)) and not region:
                    problems.append('defines existing label %s' % lab)
                newlab = IDENT.sub(rep, lab)
                rest = code[m.end():]
                # always write the colon (vasm accepts labels without one, the scope repair needs it)
                code = newlab + ':' + IDENT.sub(rep, rest) if rest.strip() else newlab + ':' + rest
            else:
                parts = re.match(r'^(\s*)(\S+)(\s*)(.*)$', code)
                if parts:
                    code = parts.group(1) + parts.group(2) + parts.group(3) + IDENT.sub(rep, parts.group(4))
            out.append(code + comment)
        return out, problems

    # ---------- region rewrites for partially covered source lines ----------
    import region
    RG = region.Regions(M, m62_382)
    groups = []   # [file, lo121, hi121, [hids]]
    for hid, h in enumerate(H):
        if h.get('kind') not in ('replace-partial', 'insert-inside') or skip_reason(h):
            continue
        sec, a, e = h['addr_range']
        if h['kind'] == 'insert-inside':
            lines, _ = M.s_covering(sec, a, a + 1)
        else:
            lines, _ = M.s_covering(sec, a, e)
        files = {f for f, _ in lines}
        if len(files) != 1:
            continue
        f = lines[0][0]
        lo, hi = min(ln for _, ln in lines), max(ln for _, ln in lines)
        for g in groups:
            if g[0] == f and not (hi < g[1] or lo > g[2]):
                g[1], g[2] = min(g[1], lo), max(g[2], hi); g[3].append(hid); break
        else:
            groups.append([f, lo, hi, [hid]])
    region_done = set()
    for f, lo, hi, hids in groups:
        # the emitting source lines lo..hi; include non-emitting lines between them
        S = M.s_emit[(f, lo)]
        E = RG.next_src_addr(f, hi)
        bS = RG.addr_first_code.get(S)
        bE = RG.addr_first.get(E) if E else None
        aS = RG.adv_stmt_for_base(bS) if bS else None
        aE = RG.adv_stmt_for_base(bE) if bE else None
        if not (aS and aE):
            for hid in hids:
                log.append((hid, 'skip', 'region: no statement mapping', H[hid]['base_lines'], H[hid].get('target')))
            continue
        a_first, a_last = ia[aS - 1], ia[aE - 1] - 1
        raw = adv[a_first - 1:a_last]
        # extend to the line before the next emitting line (rept blocks, label-only lines)
        nxt = [ln for (ff, ln) in M.s_at(*E) if ff == f] if E else []
        if nxt and min(nxt) > hi:
            src121 = M.src_lines(f)
            hi2 = min(nxt) - 1
            # but keep label-only and comment lines directly before the next emitting line
            while hi2 > hi:
                code, _ = symbols.strip_comment(src121[hi2 - 1])
                if not code.strip() or (DEF.match(code) and code[:1] not in ' \t' and not code[DEF.match(code).end():].strip(' \t:')):
                    hi2 -= 1
                else:
                    break
            hi = hi2
        hlo, hhi = to_head(f, lo), to_head(f, hi)
        if hlo is None or hhi is None or hhi - hlo != hi - lo:
            for hid in hids:
                log.append((hid, 'skip', 'region: head mapping', H[hid]['base_lines'], H[hid].get('target')))
            continue
        src = open(os.path.join(target, f), encoding='latin1').read().replace('\r\n', '\n').split('\n')
        keep = []
        code, _ = symbols.strip_comment(src[hlo - 1])
        m = DEF.match(code)
        if m and code[:1] not in ' \t' and code.strip():
            keep.append(m.group(1) + ':')
        tscope = R.src_scope_at(f, hlo)
        text, problems = translate(raw, a_first, f, tscope, region=True)
        if problems:
            for hid in hids:
                log.append((hid, 'skip', 'region symbols: ' + '; '.join(sorted(set(problems))), H[hid]['base_lines'], H[hid].get('target')))
            continue
        edits.setdefault(f, []).append((hlo, hhi + 1, keep + text, min(hids)))
        region_done.update(hids)
        log.append((min(hids), 'region', f, '%d-%d' % (hlo, hhi), ','.join(map(str, hids))))

    # ---------- hunks which need a decision (see MANUAL) ----------
    post_fixes = [
        # the inserted monster tables end on an odd address; the original relies on auto-alignment of dc.w
        ('KERNEL/DATA.S', '\tdc.b $00\nWorld_data:\n', '\tdc.b $00\n\teven\nWorld_data:\n'),
    ]
    for hid, h in enumerate(H):
        rule = MANUAL.get(manual_key(h))
        if not rule:
            continue
        if rule['mode'] == 'skip':
            post_fixes += rule.get('post', [])
            region_done.add(hid)
            log.append((hid, 'manual-skip', h['target'][0], h['target'][1], rule.get('why', '')))
            continue
        a_first = ia[h['a1'] - 2] + 1 if h['a1'] >= 2 else 1
        a_last = ia[h['a1'] + h['an'] - 2]
        if rule.get('from_line'):
            a_first = rule['from_line']
        if rule.get('to_line'):
            a_last = rule['to_line']
        raw = [l for l in adv[a_first - 1:a_last]]
        raw_nos = list(range(a_first, a_last + 1))
        drop = rule.get('drop', ())
        keep_idx = [k for k, l in enumerate(raw) if l.strip() not in drop]
        f, ln = h['target'][0], h['target'][1]
        tscope = R.src_scope_at(f, ln)
        text, problems = [], []
        for k in keep_idx:
            t, pr = translate([raw[k]], raw_nos[k], f, tscope, region=rule.get('allow_defs', False))
            text += t; problems += pr
        if rule.get('text'):
            text, problems = list(rule['text']), []
        if problems:
            log.append((hid, 'skip', 'manual symbols: ' + '; '.join(sorted(set(problems))), h['base_lines'], h.get('target'))); continue
        if rule['mode'] == 'replace-line':
            edits.setdefault(f, []).append((ln, ln + 1, text, hid))
        else:
            edits.setdefault(f, []).append((ln, ln, text, hid))
        post_fixes += rule.get('post', [])
        region_done.add(hid)
        log.append((hid, 'manual', f, ln, rule.get('why', '')))

    for hid, h in enumerate(H):
        if hid in region_done:
            continue
        kind = h.get('kind')
        why = skip_reason(h)
        if why:
            log.append((hid, 'skip', why, h['base_lines'], h.get('target')))
            continue
        if kind == 'labels-only':
            # new Advanced labels in unchanged code (renamed base labels need nothing)
            if not h['an']:
                log.append((hid, 'skip', 'labels-only (removed labels)', h['base_lines'], h.get('target'))); continue
            a_first = ia[h['a1'] - 1]
            a_last = ia[h['a1'] + h['an'] - 2]
            names = []
            for no in range(a_first, a_last + 1):
                code, _ = symbols.strip_comment(adv[no - 1])
                m = DEF.match(code)
                if not m or code[:1] in ' \t':
                    continue
                lab = m.group(1)
                q = scope_of[no - 1] + lab if lab.startswith('.') else lab
                if q in R.adv2base or q in R.base_labels or lab in aliases:
                    continue
                names.append((no, lab))
            if not names:
                log.append((hid, 'skip', 'labels-only (renamed labels)', h['base_lines'], h.get('target'))); continue
            l382 = m62_382.get(h['base_lines'][0])
            addr = M.b_addr(l382) if l382 else None
            at = M.s_at(*addr) if addr else []
            if not at:
                log.append((hid, 'skip', 'labels-only: no source line at the address', h['base_lines'], h.get('target'))); continue
            f, ln121 = at[0]
            ln = to_head(f, ln121)
            tscope = R.src_scope_at(f, ln)
            text, problems = translate([adv[no - 1] for no, _ in names], 0, f, tscope) if False else ([], [])
            for no, lab in names:
                t, pr = translate([adv[no - 1]], no, f, tscope)
                text += [x for x in t if x.strip()]
                problems += pr
            if problems:
                log.append((hid, 'skip', 'symbols: ' + '; '.join(sorted(set(problems))), h['base_lines'], h.get('target'))); continue
            edits.setdefault(f, []).append((ln, ln, text, hid))
            continue
        if kind not in ('replace-exact', 'insert'):
            log.append((hid, 'skip', kind, h['base_lines'], h.get('target')))
            continue
        # Advanced raw text (include comment lines right after the previous statement)
        if h['an']:
            a_first = ia[h['a1'] - 2] + 1 if h['a1'] >= 2 else 1
            a_last = ia[h['a1'] + h['an'] - 2]
            raw = adv[a_first - 1:a_last]
        else:
            a_first, raw = 0, []
        if kind == 'replace-exact':
            rng = h['src_range']
            f = rng[0][0]
            s121 = [ln for _, ln in rng]
            hs = [to_head(f, ln) for ln in s121]
            if None in hs or hs != list(range(hs[0], hs[0] + len(hs))):
                log.append((hid, 'skip', 'head-mapping', h['base_lines'], h.get('target'))); continue
            start, end = hs[0], hs[-1] + 1
            # keep label definitions of removed lines
            keep = []
            later = []   # (label, offset) of labels behind the start of the range
            src = open(os.path.join(target, f), encoding='latin1').read().split('\n')
            a0 = M.s_emit.get((f, s121[0]))
            for ln in range(start, end):
                code, _ = symbols.strip_comment(src[ln - 1])
                m = DEF.match(code)
                if m and code[:1] not in ' \t' and code.strip():
                    a = M.s_emit.get((f, s121[ln - start]))
                    if ln == start or not a or not a0 or a[1] == a0[1]:
                        keep.append(m.group(1) + ':')
                    else:
                        later.append((m.group(1), a[1] - a0[1]))
            # also labels on comment-free label-only lines are not in the range (they emit nothing)
            tscope = R.src_scope_at(f, start)
            text, problems = translate(raw, a_first, f, tscope)
            if problems:
                log.append((hid, 'skip', 'symbols: ' + '; '.join(sorted(set(problems))), h['base_lines'], h.get('target'))); continue
            for lab, off in reversed(later):
                pos = data_offset_line(text, off)
                if pos is not None:
                    text.insert(pos, lab + ':')
                    log.append((hid, 'label-moved', lab, off))
                elif lab.startswith('.') and not any(re.search(r'(?<![\w.])' + re.escape(lab) + r'\b', symbols.strip_comment(src[i - 1])[0])
                                                     for i in scope_lines(src, start) if not start <= i < end):
                    log.append((hid, 'label-dropped', lab, 'unreferenced local'))
                else:
                    keep.append(lab + ':')
                    log.append((hid, 'label-misplaced', lab, off))
            edits.setdefault(f, []).append((start, end, keep + text, hid))
        else:
            # insertion before the source line(s) at the address
            at = h['src_at']
            f = at[0][0]
            ln121 = min(ln for ff, ln in at if ff == f)
            ln = to_head(f, ln121)
            if ln is None:
                log.append((hid, 'skip', 'head-mapping', h['base_lines'], h.get('target'))); continue
            next_is_label = blines62[h['b1']].endswith(':') if h['b1'] < len(blines62) else False
            src = open(os.path.join(target, f), encoding='latin1').read().split('\n')
            # walk back over label-only lines directly before the emitting line
            lab_start = ln
            while lab_start > 1:
                code, _ = symbols.strip_comment(src[lab_start - 2])
                if code.strip() and DEF.match(code) and code[:1] not in ' \t' and not code[DEF.match(code).end():].strip():
                    lab_start -= 1
                elif not code.strip() and src[lab_start - 2].strip().startswith(';'):
                    break
                else:
                    break
            tscope = R.src_scope_at(f, ln)
            text, problems = translate(raw, a_first, f, tscope)
            if problems:
                log.append((hid, 'skip', 'symbols: ' + '; '.join(sorted(set(problems))), h['base_lines'], h.get('target'))); continue
            code, comment = symbols.strip_comment(src[ln - 1])
            m = DEF.match(code)
            line_has_label = bool(m and code[:1] not in ' \t' and code.strip())
            if next_is_label:
                edits.setdefault(f, []).append((lab_start, lab_start, text, hid))
            elif line_has_label:
                # split "label: instr" so that the new code is placed behind the label
                lab = m.group(1) + ':'
                rest = code[m.end():].lstrip(':')
                edits.setdefault(f, []).append((ln, ln + 1, [lab] + text + ['\t' + rest.strip() + comment], hid))
            else:
                edits.setdefault(f, []).append((ln, ln, text, hid))
    # labels which the Advanced code needs at addresses without a source label
    for k, (x, addr) in enumerate(sorted(R.need_labels.items())):
        f, ln121 = M.s_at(*addr)[0]
        ln = to_head(f, ln121)
        edits.setdefault(f, []).append((ln, ln, [x + ':'], 10 ** 6 + k))
        new_globals.add(x)
    applied = 0
    for f, ed in edits.items():
        p = os.path.join(target, f)
        raw = open(p, 'rb').read()
        nl = '\r\n' if b'\r\n' in raw else '\n'
        src = raw.decode('latin1').replace('\r\n', '\n').split('\n')
        # bottom-up; for equal positions keep the original order of the hunks
        for start, end, new, hid in sorted(ed, key=lambda e: (e[0], e[3]), reverse=True):
            src[start - 1:end - 1] = new
            applied += 1
            log.append((hid, 'applied', f, start, end))
        open(p, 'wb').write(nl.join(src).encode('latin1'))
    for f, old, new in post_fixes:
        p = os.path.join(target, f)
        raw = open(p, 'rb').read()
        nl = '\r\n' if b'\r\n' in raw else '\n'
        s = raw.decode('latin1').replace('\r\n', '\n')
        if s.count(old) != 1:
            log.append((0, 'post-fix failed', f, old.split('\n')[0], s.count(old)))
            continue
        open(p, 'wb').write(s.replace(old, new).replace('\n', nl).encode('latin1'))
    import scopes
    scope_log = scopes.fix_scopes(target, new_globals | set(grename.values()), R.src_globals)
    with open(os.path.join(W, 'port_log.txt'), 'w') as fo:
        for e in scope_log:
            fo.write('\t'.join(e) + '\n')
        for e in sorted(log, key=lambda e: e[0]):
            fo.write('\t'.join(map(str, e)) + '\n')
    print('applied', applied, 'skipped', sum(1 for e in log if e[1] == 'skip'))
    print('global renames', grename)


if __name__ == '__main__':
    main()
