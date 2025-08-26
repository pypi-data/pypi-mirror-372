from collections import defaultdict

def build_nested_options(rows, level_names=None):
    """
    rows: list of tuples (any length >=1)
    level_names: optional list of level labels for the widget
    returns: (options_dict, levels_list)
    """
    depth = max(len(t) for t in rows)
    if level_names is None:
        defaults = ["Level " + str(i+1) for i in range(depth)]
        level_names = defaults[:depth]

    TREE_LEAVES = "__leaves__"

    def node():
        return defaultdict(node)

    root = node()

    for tup in rows:
        if len(tup) == 1:
            # just a leaf
            root.setdefault(TREE_LEAVES, set()).add(tup[0])
        else:
            *heads, leaf = tup
            cur = root
            for h in heads:
                cur = cur[h]
            cur.setdefault(TREE_LEAVES, set()).add(leaf)

    def finalize(d):
        # if it only has leaves, return sorted list
        if set(d.keys()) == {TREE_LEAVES}:
            return sorted(d[TREE_LEAVES])
        out = {}
        for k, v in d.items():
            if k == TREE_LEAVES:
                continue
            out[k] = finalize(v)
        return out

    options = {k: finalize(v) for k, v in root.items()}
    if TREE_LEAVES in root:
        # top-level leaves
        options.update({k: k for k in sorted(root[TREE_LEAVES])})

    return options, level_names