import yaml


filename = "src/assets/data/experiments/behavior_trees.yml"
out_filename = "behavior_tree.mermaid"

with open(filename) as file:
    data = yaml.safe_load(file.read())

bt = data["melee_attacker"]["root"]


def draw_tree(tree: dict, start_index: int, subtree_root: str | None) -> list[str]:
    maybe_comment = f"<br/>{tree.get('comment')}" if tree.get("comment") else ""
    maybe_params = (
        f"<br/>{'<br/>'.join((f"{param[0]}: {param[1]}" for param in tree.get('params', {}).items()))}"
        if tree.get("params")
        else ""
    )
    current_node = f"{start_index}[{tree['type']}<br/>{maybe_comment}{maybe_params}]"
    res: list[str] = (
        [f"{subtree_root} --> {current_node}"]
        if subtree_root is not None
        else [current_node]
    )
    j = start_index + 1
    if "children" in tree:
        for child_tree in tree["children"]:
            drawn_subtree = draw_tree(child_tree, j, current_node)
            res += drawn_subtree
            j += len(drawn_subtree)
    return res


with open(out_filename, "w") as outfile:
    header = """---
title: Behavior Tree 
---
graph TB"""
    drawn_tree = draw_tree(bt, 0, None)
    drawn_tree_indented = [f"    {s}" for s in drawn_tree]

    contents = "\n".join((header, *drawn_tree_indented))
    outfile.write(contents)
