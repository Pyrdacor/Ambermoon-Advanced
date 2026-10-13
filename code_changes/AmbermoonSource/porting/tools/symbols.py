"""Name resolution between the Advanced disassembly, the base disassembly and AmbermoonSource."""
import bisect, os, re
import srcmodel

W = srcmodel.W
GLOBAL_DEF = re.compile(r'^([A-Za-z_][\w]*):')
ANY_DEF = re.compile(r'^([A-Za-z_.][\w.]*)(?::|(?=\s)|$)')


def strip_comment(s):
    q = None
    for i, ch in enumerate(s):
        if q:
            if ch == q:
                q = None
        elif ch in '"\'':
            q = ch
        elif ch == ';':
            return s[:i], s[i:]
    return s, ''


class Resolver:
    def __init__(self, M):
        self.M = M
        self.need_labels = {}   # disassembly label -> address, labels to add to the source
        # adv -> base62 label mapping (qualified local names)
        self.adv2base = dict(l.split('\t') for l in open(os.path.join(W, 'map_adv_to_62823505.tsv')).read().split('\n') if l)
        self.base_labels = set(open(os.path.join(W, 'base', '62823505.labels')).read().split('\n'))
        self.adv_labels = set(open(os.path.join(W, 'adv.labels')).read().split('\n'))
        # SYMBOLS.txt: disassembly label -> (name, file)
        self.symbols = {}
        for l in open(os.path.join(W, 'src121', 'AmbermoonSource', 'SYMBOLS.txt'), encoding='latin1'):
            if l.startswith('#'):
                continue
            p = l.rstrip('\n').split('\t')
            if len(p) >= 2:
                self.symbols[p[0]] = (p[1], p[2] if len(p) > 2 else '')
        # base382 label definition lines (qualified like norm.py)
        self.b382_def = {}
        scope = ''
        for no, line in enumerate(open(os.path.join(W, 'base', '382eaeda.s'), encoding='latin1').read().split('\n'), 1):
            m = ANY_DEF.match(line)
            if m and line[:1] not in ' \t;*':
                name = m.group(1)
                if name.startswith('.'):
                    name = scope + name
                else:
                    scope = name
                self.b382_def[name] = no
        # source label definitions: per file list of (line, name, scope); address via next emitting line
        self.src_defs = {}       # (sec, off) -> list of (file, line, name, scope)
        self.src_globals = set()
        self.src_scope_locals = {}  # (file, scope) -> set of local names
        for f in M.s_by_file:
            lines = M.src_lines(f)
            emit = M.s_by_file[f]
            scope = ''
            for no, line in enumerate(lines, 1):
                code, _ = strip_comment(line)
                m = ANY_DEF.match(code)
                if not m or code[:1] in ' \t':
                    continue
                name = m.group(1)
                rest = code[m.end():].strip()
                if rest.lower().startswith(('equ', '=', 'rs.', 'macro', 'set ')) or rest.lower() in ('macro',):
                    continue
                if name.startswith('.'):
                    self.src_scope_locals.setdefault((f, scope), set()).add(name)
                else:
                    scope = name
                    self.src_globals.add(name)
                i = bisect.bisect_left(emit, no)
                if i < len(emit):
                    addr = M.s_emit[(f, emit[i])]
                    self.src_defs.setdefault(addr, []).append((f, no, name, scope))

    def src_scope_at(self, f, line):
        """Global label scope in source file f before line."""
        lines = self.M.src_lines(f)
        for no in range(min(line, len(lines)) - 1, 0, -1):
            code, _ = strip_comment(lines[no - 1])
            m = GLOBAL_DEF.match(code)
            if m:
                return m.group(1)
        return ''

    def _b62_to_382(self):
        """Labels of the 62823505 disassembly -> labels of the 382eaeda disassembly (renamed ones)."""
        if hasattr(self, '_m62'):
            return self._m62
        from plan import git_diff_linemap
        b62 = open(os.path.join(W, 'base', '62823505.s'), encoding='latin1').read().split('\n')
        b382 = open(os.path.join(W, 'base', '382eaeda.s'), encoding='latin1').read().split('\n')
        lm = git_diff_linemap(b62, b382)
        def defs(lines):
            res = {}
            for no, line in enumerate(lines, 1):
                m = GLOBAL_DEF.match(line)
                if m:
                    res[no] = m.group(1)
            return res
        d62, d382 = defs(b62), defs(b382)
        self._m62 = {}
        for no, name in d62.items():
            if name in self.b382_def:
                continue
            n382 = lm.get(no)
            if n382 in d382:
                self._m62[name] = d382[n382]
        return self._m62

    def base_to_src(self, x, target_file, target_scope):
        """Name to use in the source for base label x, or None with a reason."""
        if x not in self.b382_def and '.' not in x[1:]:
            x = self._b62_to_382().get(x, x)
        sym = self.symbols.get(x.split('.')[0] if '.' in x[1:] and not x.startswith('.') else x)
        if sym and sym[1] and not sym[0].startswith('Lbl_') and '.' not in x[1:]:
            return sym[0], None
        # resolve by address
        ln = self.b382_def.get(x)
        if ln is None:
            return None, 'unknown base label %s' % x
        addr = self.M.b_addr(ln)
        defs = self.src_defs.get(addr, [])
        globs = [d for d in defs if not d[2].startswith('.')]
        if globs:
            return globs[0][2], None
        for f, no, name, scope in defs:
            if f == target_file and scope == target_scope:
                return name, None
        # no usable label at this address: a new label with the disassembly name is added there
        if not self.M.s_at(*addr):
            # data inside a larger definition: express it as previous source label + offset
            if re.match(r'^(DAT|BYTE|WORD|DWORD|PTR|s)_', x):
                cand = [(a, d) for a, ds in self.src_defs.items() if a[0] == addr[0] and a[1] <= addr[1] and addr[1] - a[1] < 256
                        for d in ds if not d[2].startswith('.')]
                if cand:
                    a, d = max(cand, key=lambda c: c[0][1])
                    return '%s+%d' % (d[2], addr[1] - a[1]), None
            return None, 'no source line starts at the address of %s' % x
        self.need_labels[x] = addr
        return x, None
