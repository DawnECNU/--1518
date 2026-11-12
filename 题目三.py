# -*- coding: utf-8 -*-
"""题目三：极大极小博弈树与 Alpha-Beta 剪枝。"""

from __future__ import annotations

import ast
import json
import math
import sys
from typing import Any, Iterable, Optional


class TreeNode:
    """博弈树节点；叶节点使用 value，内部节点使用 children。"""

    def __init__(
        self,
        value: Any = None,
        children: Optional[Iterable["TreeNode"]] = None,
    ):
        self.value = value
        self.children = list(children) if children is not None else []

    def __repr__(self) -> str:
        if self.children:
            return f"TreeNode(children={self.children!r})"
        return f"TreeNode(value={self.value!r})"


def _coerce_node(node: Any) -> TreeNode:
    """把 TreeNode 或题面 JSON 形式的字典统一为 TreeNode。"""

    if isinstance(node, TreeNode):
        return node
    if not isinstance(node, dict):
        raise TypeError("node 必须是 TreeNode 或字典")

    children = node.get("children")
    if children is not None:
        if not isinstance(children, (list, tuple)):
            raise ValueError("children 必须是列表")
        return TreeNode(children=[_coerce_node(child) for child in children])
    if "value" not in node:
        raise ValueError("叶节点必须包含 value")
    return TreeNode(value=node["value"])


def tree_from_dict(data: Any) -> TreeNode:
    """从题面给出的 JSON 结构创建 TreeNode。"""

    return _coerce_node(data)


def _alpha_beta(
    node: TreeNode,
    alpha: float,
    beta: float,
    is_maximizing: bool,
    stats: dict,
) -> float:
    stats["visited_nodes"] += 1

    if not node.children:
        if node.value is None:
            raise ValueError("叶节点 value 不能为空")
        stats["leaf_evaluations"] += 1
        return float(node.value)

    stats["internal_evaluations"] += 1
    if is_maximizing:
        best_value = -math.inf
        for child in node.children:
            value = _alpha_beta(child, alpha, beta, False, stats)
            best_value = max(best_value, value)
            alpha = max(alpha, best_value)
            if beta <= alpha:
                stats["pruned_children"] += 1
                break
        return best_value

    best_value = math.inf
    for child in node.children:
        value = _alpha_beta(child, alpha, beta, True, stats)
        best_value = min(best_value, value)
        beta = min(beta, best_value)
        if beta <= alpha:
            stats["pruned_children"] += 1
            break
    return best_value


def alpha_beta_pruning(
    node: Any,
    alpha: float = -math.inf,
    beta: float = math.inf,
    is_maximizing: bool = True,
    return_stats: bool = False,
):
    """
    用 Alpha-Beta 剪枝计算根节点对 MAX 玩家的最优值。

    子节点严格按从左到右的顺序访问。返回值为单个数值；当
    ``return_stats=True`` 时返回 ``(value, stats)``。
    """

    root = _coerce_node(node)
    stats = {
        "leaf_evaluations": 0,
        "internal_evaluations": 0,
        "visited_nodes": 0,
        "pruned_children": 0,
    }
    value = _alpha_beta(root, float(alpha), float(beta), bool(is_maximizing), stats)
    if math.isfinite(value) and value.is_integer():
        value = int(value)
    return (value, stats) if return_stats else value


def _minimax(node: TreeNode, is_maximizing: bool, stats: dict) -> float:
    stats["visited_nodes"] += 1
    if not node.children:
        if node.value is None:
            raise ValueError("叶节点 value 不能为空")
        stats["leaf_evaluations"] += 1
        return float(node.value)

    stats["internal_evaluations"] += 1
    values = (_minimax(child, not is_maximizing, stats) for child in node.children)
    return max(values) if is_maximizing else min(values)


def minimax_value(node: Any, is_maximizing: bool = True, return_stats: bool = False):
    """不使用剪枝的 Minimax，供对照实验和结果校验使用。"""

    root = _coerce_node(node)
    stats = {
        "leaf_evaluations": 0,
        "internal_evaluations": 0,
        "visited_nodes": 0,
        "pruned_children": 0,
    }
    value = _minimax(root, bool(is_maximizing), stats)
    if math.isfinite(value) and value.is_integer():
        value = int(value)
    return (value, stats) if return_stats else value


# 兼容使用 Minimax 名称直接导入的调用方式。
minimax = minimax_value


if __name__ == "__main__":
    source = sys.stdin.read()
    try:
        try:
            data = json.loads(source)
        except json.JSONDecodeError:
            data = ast.literal_eval(source)
        tree_data = data.get("tree_structure", data) if isinstance(data, dict) else data
        print(alpha_beta_pruning(tree_data))
    except (SyntaxError, ValueError, TypeError) as error:
        print(f"输入格式错误：{error}", file=sys.stderr)
        raise SystemExit(2)
