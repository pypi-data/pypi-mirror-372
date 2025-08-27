# --- helpers ---------------------------------------------------------------
def make_string(x):
    if isinstance(x, (list, tuple, set)):
        return ",".join(str(i) for i in x)
    return "" if x is None else str(x)

def _norm_csv(val, *, lower=True, split_chars=(",","|")):
    """Normalize a CSV/pipe string or iterable to a sorted tuple for stable compare."""
    if not val or val is False:
        return tuple()
    if isinstance(val, (list, tuple, set)):
        items = [str(v) for v in val]
    else:
        s = str(val)
        for ch in split_chars[1:]:
            s = s.replace(ch, split_chars[0])
        items = [p.strip() for p in s.split(split_chars[0]) if p.strip()]
    if lower:
        items = [i.lower() for i in items]
    return tuple(sorted(items))

def _filters_subset(state: dict) -> dict:
    """Just the filter fields (the ones you care about for auto-unlink)."""
    return {
        "allowed_exts":    _norm_csv(state.get("allowed_exts", "")),
        "unallowed_exts":  _norm_csv(state.get("unallowed_exts", "")),
        "exclude_types":   _norm_csv(state.get("exclude_types", ""), lower=False),
        "exclude_dirs":    _norm_csv(state.get("exclude_dirs", ""),  lower=False),
        "exclude_patterns":_norm_csv(state.get("exclude_patterns",""),lower=False),
    }
