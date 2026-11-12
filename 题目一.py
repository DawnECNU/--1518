# -*- coding: utf-8 -*-
"""题目一：使用 A* 算法求解四邻域迷宫的最短路径。"""

from __future__ import annotations

import ast
import heapq
import sys
from typing import Callable, List, Optional, Sequence, Tuple

Point = Tuple[int, int]


def manhattan_distance(a: Point, b: Point) -> int:
    """返回两个坐标之间的曼哈顿距离。"""

    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def zero_heuristic(a: Point, b: Point) -> int:
    """零启发函数；此时 A* 退化为 Dijkstra 算法。"""

    return 0


def _is_valid_grid(maze: Sequence[Sequence[str]]) -> bool:
    """检查地图是否为非空矩形。"""

    if not maze or not maze[0]:
        return False
    width = len(maze[0])
    return all(len(row) == width for row in maze)


def astar_maze(
    start: Point,
    end: Point,
    maze: Sequence[Sequence[str]],
    heuristic_func: Optional[Callable[[Point, Point], float]] = None,
    return_stats: bool = False,
):
    """
    求从 start 到 end 的一条最短路径。

    每次移动的代价为 1，只能上下左右移动。地图中的 ``X`` 表示障碍，
    其他字符均视为可通行。无解或输入不合法时返回空列表。

    当 ``return_stats=True`` 时，返回 ``(path, stats)``；否则只返回路径。
    stats 包含已展开节点数、已生成节点数、队列峰值和路径代价。
    """

    heuristic = manhattan_distance if heuristic_func is None else heuristic_func
    empty_stats = {
        "expanded": 0,
        "generated": 0,
        "frontier_peak": 0,
        "path_cost": -1,
    }

    if not _is_valid_grid(maze):
        return ([], empty_stats) if return_stats else []

    rows, cols = len(maze), len(maze[0])

    def in_bounds(point: Point) -> bool:
        return 0 <= point[0] < rows and 0 <= point[1] < cols

    def is_blocked(point: Point) -> bool:
        return str(maze[point[0]][point[1]]).strip().upper() in {"X", "#"}

    if not in_bounds(start) or not in_bounds(end):
        return ([], empty_stats) if return_stats else []
    if is_blocked(start) or is_blocked(end):
        return ([], empty_stats) if return_stats else []

    if start == end:
        stats = {
            "expanded": 0,
            "generated": 1,
            "frontier_peak": 1,
            "path_cost": 0,
        }
        return ([start], stats) if return_stats else [start]

    directions = ((-1, 0), (1, 0), (0, -1), (0, 1))
    g_score = {start: 0}
    parent = {start: None}
    counter = 0
    frontier = [(float(heuristic(start, end)), counter, start, 0)]
    expanded = 0
    generated = 1
    frontier_peak = 1

    while frontier:
        _, _, current, queued_g = heapq.heappop(frontier)

        # 优先队列允许保留旧记录；只处理当前最优的那一条。
        if queued_g != g_score.get(current):
            continue
        current_g = g_score[current]
        expanded += 1

        if current == end:
            path: List[Point] = []
            node: Optional[Point] = current
            while node is not None:
                path.append(node)
                node = parent[node]
            path.reverse()
            stats = {
                "expanded": expanded,
                "generated": generated,
                "frontier_peak": frontier_peak,
                "path_cost": current_g,
            }
            return (path, stats) if return_stats else path

        for dr, dc in directions:
            neighbor = (current[0] + dr, current[1] + dc)
            if not in_bounds(neighbor) or is_blocked(neighbor):
                continue

            tentative_g = current_g + 1
            if tentative_g >= g_score.get(neighbor, float("inf")):
                continue

            g_score[neighbor] = tentative_g
            parent[neighbor] = current
            counter += 1
            priority = tentative_g + float(heuristic(neighbor, end))
            heapq.heappush(frontier, (priority, counter, neighbor, tentative_g))
            generated += 1
            frontier_peak = max(frontier_peak, len(frontier))

    stats = {
        "expanded": expanded,
        "generated": generated,
        "frontier_peak": frontier_peak,
        "path_cost": -1,
    }
    return ([], stats) if return_stats else []


def _read_single_case() -> Tuple[Point, Point, list]:
    """读取题面格式的三个 Python 字面量：起点、终点和地图。"""

    source = sys.stdin.read()
    module = ast.parse(source, mode="exec")
    if len(module.body) != 3:
        raise ValueError("需要依次输入起点、终点和地图三个字面量")

    values = []
    for statement in module.body:
        if not isinstance(statement, ast.Expr):
            raise ValueError("输入只能包含表达式，不能包含赋值或函数调用")
        values.append(ast.literal_eval(statement.value))

    start, end, maze = values
    if not (
        isinstance(start, tuple)
        and isinstance(end, tuple)
        and len(start) == 2
        and len(end) == 2
        and isinstance(maze, list)
    ):
        raise ValueError("起点和终点应为二元组，地图应为二维列表")
    return start, end, maze


if __name__ == "__main__":
    try:
        sample_start, sample_end, sample_maze = _read_single_case()
        print(astar_maze(sample_start, sample_end, sample_maze))
    except (SyntaxError, ValueError) as error:
        print(f"输入格式错误：{error}", file=sys.stderr)
        raise SystemExit(2)
