# ---------- import graph analyzer (pure Python) ----------
import argparse,json,os,re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from .constants import *

is_allowed = REACT_ALLOWED
# --- add near your regex imports (or constants) ---
_RE_FN_DECL     = re.compile(r'\bfunction\s+([A-Za-z_$][\w$]*)\s*\(')
_RE_CLASS_DECL  = re.compile(r'\bclass\s+([A-Za-z_$][\w$]*)\b')
_RE_VAR_BLOCK   = re.compile(r'\b(?P<kind>const|let|var)\s+(?P<list>[^;]*)\s*;')

def _decl_kinds(code: str) -> Dict[str, str]:
    """
    Return {name: kind} where kind in {'function','class','const','let','var'}
    (best-effort; simple regex-based)
    """
    kinds: Dict[str, str] = {}

    for m in _RE_FN_DECL.finditer(code):
        kinds[m.group(1)] = 'function'
    for m in _RE_CLASS_DECL.finditer(code):
        kinds[m.group(1)] = 'class'

    # const/let/var a = 1, b = 2, c;
    for m in _RE_VAR_BLOCK.finditer(code):
        k = m.group('kind')
        lst = m.group('list')
        for piece in lst.split(','):
            name = piece.strip().split('=')[0].strip()
            if name and re.match(r'^[A-Za-z_$][\w$]*$', name):
                kinds.setdefault(name, k)

    return kinds
def read_file(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""
    
def strip_comments(src: str) -> str:
    src = RE_BLOCK_COMMENT.sub('', src)
    src = RE_LINE_COMMENT.sub('', src)
    return src

    
def is_local_spec(spec: str) -> bool:
    return spec.startswith("./") or spec.startswith("../") or spec.startswith("/")
 
def find_entry(src_root: Path, entries: List[str]) -> Path:
    for base in entries:
        for ext in EXTS:
            p = src_root / f"{base}{ext}"
            if p.is_file():
                return p
    for ext in EXTS:
        p = src_root / f"index{ext}"
        if p.is_file():
            return p
    raise FileNotFoundError(f"No entry found. Tried {entries} with extensions {EXTS} under {src_root}")

# 3) resolve_with_ext that uses the same allowed predicate
def resolve_with_ext(base: Path, is_allowed=None) -> Optional[Path]:
    candidates: list[Path] = []
    if base.is_file():
        candidates.append(base)
    for ext in EXTS:
        candidates.append(base.with_suffix(ext))
    if base.is_dir():
        for ext in EXTS:
            candidates.append(base / f"index{ext}")
    for p in candidates:
        if p.is_file() and (is_allowed(p) if is_allowed else True):
            return p
    return None



def parse_import_clause(clause: str) -> List[str]:
    names: List[str] = []
    if "* as" in clause or clause.strip().startswith("*"):
        names.append("*")
        return names
    m_def = RE_DEFAULT_IMPORT.match(clause)
    if m_def:
        names.append("<default>")
    m_named = RE_NAMED_BINDINGS.search(clause)
    if m_named:
        raw = m_named.group("named")
        for piece in raw.split(","):
            piece = piece.strip()
            if not piece:
                continue
            name = piece.split(" as ")[0].strip()
            if name:
                names.append(name)
    return names or ["<side-effect>"]

def analyze_file(p: Path) -> Dict:
    code = strip_comments(read_file(p))
    decl_k = _decl_kinds(code)
    exports: Set[str] = set()
    imports: List[Dict] = []
    reexports: List[Dict] = []
    export_kinds: Dict[str, str] = {}

    for m in RE_EXPORT_FN_DECL.finditer(code):
        exports.add(m.group(1))
    for m in RE_EXPORT_CONST_FN.finditer(code):
        exports.add(m.group(1))
    for m in RE_EXPORT_DEFAULT_NAMED.finditer(code):
        exports.add(m.group(1))
    if RE_EXPORT_DEFAULT_ANON.search(code):
        exports.add("<default>")

    for m in RE_EXPORT_NAMED_LOCAL.finditer(code):
        for piece in m.group(1).split(","):
            nm = piece.strip().split(" as ")[-1].strip()
            if nm:
                exports.add(nm)

    for m in RE_REEXPORT.finditer(code):
        spec = m.group("spec")
        if is_local_spec(spec):
            reexports.append({"spec": spec, "named": [s.strip().split(" as ")[0] for s in m.group("names").split(",") if s.strip()] or ["<reexport>"]})

    for m in RE_IMPORT.finditer(code):
        spec = m.group("spec")
        clause = m.group("clause")
        if is_local_spec(spec):
            imports.append({"spec": spec, "named": parse_import_clause(clause)})

    for m in RE_SIDE_EFFECT_IMPORT.finditer(code):
        spec = m.group("spec")
        if is_local_spec(spec):
            imports.append({"spec": spec, "named": ["<side-effect>"]})

    # For things you explicitly matched as functions/const funcs, etc.,
    # we already added names to `exports`. Pull kinds from decl_k if known.
    for name in list(exports):
        kind = decl_k.get(name, None)
        if kind:
            export_kinds[name] = kind

    # Named local re-exports (export { foo, bar as baz })
    # You already collect names via RE_EXPORT_NAMED_LOCAL; make sure those
    # names get a kind if we can find a local decl:
    for m in RE_EXPORT_NAMED_LOCAL.finditer(code):
        for piece in m.group(1).split(','):
            nm = piece.strip().split(" as ")[-1].strip()
            if nm:
                exports.add(nm)
                if nm in decl_k:
                    export_kinds[nm] = decl_k[nm]

    # Return with both the original 'exports' AND new 'export_kinds'
    return {
        "file": str(p),
        "exports": sorted(exports),
        "imports": imports,
        "reexports": reexports,
        "export_kinds": export_kinds  # <-- NEW
    }
    return {"file": str(p), "exports": sorted(exports), "imports": imports, "reexports": reexports}
def build_graph_reachable(entry: Path, src_root: Path) -> Dict:
    visited: Set[Path] = set()
    nodes: Dict[str, Dict] = {}
    edges: List[Dict] = {}

    def dfs(fp: Path):
        if fp in visited:
            return
        visited.add(fp)
        info = analyze_file(fp)
        nodes[str(fp)] = {"exports": info["exports"]}

        # resolve and traverse imports & reexports
        for block in (info["reexports"], info["imports"]):
            for item in block:
                base = (fp.parent / item["spec"]).resolve()
                resolved = resolve_with_ext(base)
                if resolved:
                    edges.setdefault(str(fp), []).append({
                        "to": str(resolved),
                        "named": item["named"],
                    })
                    dfs(resolved)

    dfs(entry.resolve())

    # flatten edges
    flat_edges = []
    for frm, lst in edges.items():
        for e in lst:
            flat_edges.append({"from": frm, "to": e["to"], "named": e["named"]})

    return {"entry": str(entry.resolve()), "nodes": nodes, "edges": flat_edges}


def build_graph_all(src_root: Path,cfg=None) -> Dict:
    cfg = cfg or REACT_DEFAULT_CFG
    roots=make_list(src_root)
    files = collect_filepaths(roots,cfg)
    
    analyses: Dict[str, Dict] = {}
    for f in files:
        try:
            info = analyze_file(Path(f))   # <-- ensure Path
            analyses[str(Path(f))] = info
        except Exception as e:
            # helpful debug
            print(f"[analyze_file] failed on {f}: {e}")

        nodes: Dict[str, Dict] = {
            f: {
                "exports": analyses[f]["exports"],
                "kinds":   analyses[f].get("export_kinds", {})  # <-- NEW
            }
            for f in analyses.keys()
            }
        edges: List[Dict] = []

    for f, info in analyses.items():
        fp = Path(f)
        for block in (info["reexports"], info["imports"]):
            for item in block:
                base = (fp.parent / item["spec"]).resolve()
                resolved = resolve_with_ext(base, is_allowed=is_allowed)
                if resolved:
                    edges.append({"from": f, "to": str(resolved), "named": item["named"]})
                else:
                    edges.append({"from": f, "to": item["spec"], "named": item["named"], "unresolved": True})

    return {"entry": None, "nodes": nodes, "edges": edges}


def to_dot(graph: Dict, src_root: Path) -> str:
    def rel(p: str) -> str:
        try:
            return str(Path(p).resolve().relative_to(src_root.resolve()))
        except Exception:
            return p  # for unresolved specs

    def q(s: str) -> str:
        return json.dumps(s)

    lines = ["digraph G {", "  rankdir=LR;", "  node [shape=box, fontsize=10];"]
    for p, data in graph["nodes"].items():
        rp = rel(p)
        ex = data.get("exports") or []
        extra = f"\\nexports: {', '.join(ex)}" if ex else ""
        lines.append(f"  {q(rp)} [label={q(rp + extra)}];")
    for e in graph["edges"]:
        frm = rel(e["from"])
        to = rel(e["to"])
        label = ", ".join((e.get("named") or [])[:4])
        if (e.get("named") and len(e["named"]) > 4):
            label += ", …"
        style = " [style=dashed]" if e.get("unresolved") else ""
        lines.append(f"  {q(frm)} -> {q(to)} [label={q(label)}]{style};")
    lines.append("}")
    return "\n".join(lines)



def invert_to_function_map(graph:dict)->dict:
    """Return { funcName: { 'exported_in': set(files), 'imported_in': set(files) } }"""
    funcs: dict[str, dict[str, set[str]]] = {}
    # exporters
    for f, data in graph['nodes'].items():
        for fn in data.get('exports', []):
            if fn not in funcs: funcs[fn] = {'exported_in': set(), 'imported_in': set()}
            funcs[fn]['exported_in'].add(f)
    # importers (edges carry imported names)
    for e in graph['edges']:
        names = e.get('named') or []
        for n in names:
            # skip "*" and side-effects which don’t name a function
            if n in ('*','<side-effect>'): continue
            # for default, we can record under '<default>' (or resolve later)
            key = n
            if key not in funcs: funcs[key] = {'exported_in': set(), 'imported_in': set()}
            funcs[key]['imported_in'].add(e['from'])
    # convert sets to sorted lists
    return {k: {'exported_in': sorted(v['exported_in']), 'imported_in': sorted(v['imported_in'])}
            for k,v in funcs.items()}
def start_analyzer(
    root=None,
    scope="all",
    out=None,
    entries=None,
    dot=None
    ):
    
        
    root = root or os.getcwd()
    src_root = Path(root).resolve()
    entries = entries or []
    if isinstance(entries,str):
        entries = entries.split(",")
    if scope == "reachable":
        entries = [s.strip() for s in entries if s.strip()]
        entry = find_entry(src_root, entries)
        graph = build_graph_reachable(entry, src_root)
    else:
        graph = build_graph_all(src_root)
    out = out or os.path.join(root,'import-graph.json')
    Path(out).write_text(json.dumps(graph, indent=2), encoding="utf-8")
    print(f"✅ Wrote {out} (scope: {scope})")

    if dot:
        dot_data = to_dot(graph, src_root)
        Path(dot).write_text(dot_data, encoding="utf-8")
        print(f"✅ Wrote {dot} (Graphviz)")

def react_cmd_start():
    ap = argparse.ArgumentParser(description="Map local imports & exported functions.")
    ap.add_argument("--root", default="src", help="Project source root (default: src)")
    ap.add_argument("--entries", default="index,main", help="Comma list of entry basenames (used when --scope=reachable)")
    ap.add_argument("--scope", choices=["reachable", "all"], default="all", help="reachable|all (default: reachable)")
    ap.add_argument("--out", default="import-graph.json", help="Output JSON file")
    ap.add_argument("--dot", default="graph.dot", help="Optional Graphviz .dot output path")
    args = ap.parse_args()
    root = args.root
    scope = args.scope
    out = args.out
    entries = args.entries
    dot = args.dot
    start_analyzer(
        root=root,
        scope=scope,
        out=out,
        entries=entries,
        dot=dot
    )
