# -*- coding: utf-8 -*-
"""题目二：在带地形权值的地图上用 A* 求最小进入代价。"""

from __future__ import annotations

import ast
import heapq
import math
import sys
from typing import Optional, Sequence, Tuple

Point = Tuple[int, int]


def manhattan_distance(a: Point, b: Point) -> int:
    """返回两个坐标之间的曼哈顿距离。"""

    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def _is_valid_grid(grid: Sequence[Sequence[object]]) -> bool:
    if not grid or not grid[0]:
        return False
    width = len(grid[0])
    return all(len(row) == width for row in grid)


def _is_obstacle(value: object) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip().upper() in {"", "X", "#"}
    return False


def _terrain_cost(value: object, is_end: bool) -> Optional[float]:
    """返回进入格子的代价；不可通行或非法权值返回 None。"""

    if is_end:
        return 0.0
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        cost = float(value)
    elif isinstance(value, str):
        text = value.strip()
        if text.upper() in {"S", "E"}:
            return 1.0 if text.upper() == "S" else 0.0
        try:
            cost = float(text)
        except ValueError:
            return None
    else:
        return None

    if not math.isfinite(cost) or cost < 0:
        return None
    return cost


def weighted_astar(
    start: Point,
    end: Point,
    grid: Sequence[Sequence[object]],
    h_mode: str = "corrected",
    return_stats: bool = False,
):
    """
    计算从 start 到 end 的最小移动代价。

    移动代价等于进入目标相邻格的权值；终点 E 的进入代价为 0。结果无解时
    返回 -1。``h_mode`` 支持：

    * ``zero``：h=0，退化为 Dijkstra；
    * ``manhattan``：h=曼哈顿距离；
    * ``corrected``：h=max(0, d-1)*最小正权值，考虑终点不收费；
    * ``auto``：存在零权格时使用 zero，否则使用 corrected。

    当 ``return_stats=True`` 时，返回 ``(cost, stats)``。
    """

    empty_stats = {"expanded": 0, "generated": 0, "frontier_peak": 0}
    if not _is_valid_grid(grid):
        return (-1, empty_stats) if return_stats else -1

    rows, cols = len(grid), len(grid[0])

    def in_bounds(point: Point) -> bool:
        return 0 <= point[0] < rows and 0 <= point[1] < cols

    if not in_bounds(start) or not in_bounds(end):
        return (-1, empty_stats) if return_stats else -1
    if _is_obstacle(grid[start[0]][start[1]]):
        return (-1, empty_stats) if return_stats else -1
    if _terrain_cost(grid[end[0]][end[1]], True) is None:
        return (-1, empty_stats) if return_stats else -1

    if start == end:
        stats = {"expanded": 0, "generated": 1, "frontier_peak": 1}
        return (0, stats) if return_stats else 0

    valid_modes = {"zero", "manhattan", "corrected", "auto"}
    if h_mode not in valid_modes:
        raise ValueError(f"未知 h_mode: {h_mode!r}")

    min_positive_cost: Optional[float] = None
    has_zero_cost = False
    for r, row in enumerate(grid):
        for c, value in enumerate(row):
            if (r, c) == end or _is_obstacle(value):
                continue
            cost = _terrain_cost(value, False)
            if cost is None:
                continue
            if cost == 0:
                has_zero_cost = True
            elif min_positive_cost is None or cost < min_positive_cost:
                min_positive_cost = cost

    if h_mode == "auto":
        h_mode = "zero" if has_zero_cost or min_positive_cost is None else "corrected"

    def heuristic(point: Point) -> float:
        if h_mode == "zero":
            return 0.0

        distance = manhattan_distance(point, end)
        if h_mode == "manhattan":
            return float(distance)
        if has_zero_cost or min_positive_cost is None:
            return 0.0
        return float(max(0, distance - 1)) * min_positive_cost

    infinity = float("inf")
    best_cost = {start: 0.0}
    direction = ((-1, 0), (1, 0), (0, -1), (0, 1))
    counter = 0
    frontier = [(heuristic(start), 0.0, counter, start)]
    expanded = 0
    generated = 1
    frontier_peak = 1

    while frontier:
        _, current_cost, _, current = heapq.heappop(frontier)
        if current_cost != best_cost.get(current, infinity):
            continue

        expanded += 1
        if current == end:
            result_cost: object = current_cost
            if result_cost.is_integer():
                result_cost = int(result_cost)
            stats = {
                "expanded": expanded,
                "generated": generated,
                "frontier_peak": frontier_peak,
            }
            return (result_cost, stats) if return_stats else result_cost

        for dr, dc in direction:
            neighbor = (current[0] + dr, current[1] + dc)
            if not in_bounds(neighbor):
                continue
            if _is_obstacle(grid[neighbor[0]][neighbor[1]]):
                continue

            step_cost = _terrain_cost(
                grid[neighbor[0]][neighbor[1]], neighbor == end
            )
            if step_cost is None:
                continue

            new_cost = current_cost + step_cost
            if new_cost >= best_cost.get(neighbor, infinity):
                continue

            best_cost[neighbor] = new_cost
            counter += 1
            priority = new_cost + heuristic(neighbor)
            heapq.heappush(frontier, (priority, new_cost, counter, neighbor))
            generated += 1
            frontier_peak = max(frontier_peak, len(frontier))

    stats = {
        "expanded": expanded,
        "generated": generated,
        "frontier_peak": frontier_peak,
    }
    return (-1, stats) if return_stats else -1


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

    start, end, grid = values
    if not (
        isinstance(start, tuple)
        and isinstance(end, tuple)
        and len(start) == 2
        and len(end) == 2
        and isinstance(grid, list)
    ):
        raise ValueError("起点和终点应为二元组，地图应为二维列表")
    return start, end, grid


if __name__ == "__main__":
    try:
        sample_start, sample_end, sample_grid = _read_single_case()
        print(weighted_astar(sample_start, sample_end, sample_grid))
    except (SyntaxError, ValueError) as error:
        print(f"输入格式错误：{error}", file=sys.stderr)
        raise SystemExit(2)
