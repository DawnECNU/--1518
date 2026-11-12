# -*- coding: utf-8 -*-
"""题目四：A* 距离矩阵与 Alpha-Beta 结合的宝藏分配博弈。"""

from __future__ import annotations

import heapq
import json
import math
from dataclasses import dataclass, replace
from typing import Dict, Iterable, Mapping, MutableMapping, Optional, Tuple

Point = Tuple[int, int]

GRID = [
    ["A", 1, 1, "X", 2, 1, "T1"],
    [1, "X", 6, "X", 1, "X", 1],
    [1, 1, "T2", 1, 1, 1, 1],
    ["X", 1, "X", 8, "X", 1, "X"],
    [1, 1, 1, 1, "T3", 1, 1],
    [1, "X", 9, "X", 1, "X", 1],
    ["T4", 1, 1, "X", 1, 1, "B"],
]

POINTS: Dict[str, Point] = {
    "A": (0, 0),
    "B": (6, 5),
    "T1": (0, 6),
    "T2": (2, 2),
    "T3": (4, 4),
    "T4": (6, 0),
}

# 题面预期结果对应 T3 取值为 6。该取值同时满足 H=2 与 H=4 的给定输出。
TREASURE_VALUES: Dict[str, int] = {"T1": 9, "T2": 6, "T3": 6, "T4": 7}


def _is_valid_grid(grid) -> bool:
    if not grid or not grid[0]:
        return False
    width = len(grid[0])
    return all(len(row) == width for row in grid)


def cell_cost(value: object) -> Optional[int]:
    """返回进入格子的代价；X、缺省值和非法权值返回 None。"""

    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value if value >= 0 else None
    if isinstance(value, str):
        text = value.strip()
        if text.upper() in {"", "X", "#"}:
            return None
        try:
            number = int(text)
        except ValueError:
            # A、B、T1 等特殊格均按代价 1 处理。
            return 1
        return number if number >= 0 else None
    return None


def shortest_path_cost(
    start: Point,
    end: Point,
    grid,
    return_path: bool = False,
    return_stats: bool = False,
):
    """
    用 A* 计算四邻域最短移动代价。

    进入数值格时支付该格权值；A、B、T 所在格按 1 处理。曼哈顿距离
    在本题所有可进入格权值不小于 1，故是可采纳启发函数。
    """

    empty_stats = {"expanded": 0, "generated": 0, "frontier_peak": 0}
    if not _is_valid_grid(grid):
        result = math.inf
        if return_path:
            return (result, [], empty_stats) if return_stats else (result, [])
        return (result, empty_stats) if return_stats else result

    rows, cols = len(grid), len(grid[0])

    def in_bounds(point: Point) -> bool:
        return 0 <= point[0] < rows and 0 <= point[1] < cols

    if not in_bounds(start) or not in_bounds(end):
        result = math.inf
        if return_path:
            return (result, [], empty_stats) if return_stats else (result, [])
        return (result, empty_stats) if return_stats else result
    if cell_cost(grid[start[0]][start[1]]) is None:
        result = math.inf
        if return_path:
            return (result, [], empty_stats) if return_stats else (result, [])
        return (result, empty_stats) if return_stats else result
    if cell_cost(grid[end[0]][end[1]]) is None:
        result = math.inf
        if return_path:
            return (result, [], empty_stats) if return_stats else (result, [])
        return (result, empty_stats) if return_stats else result

    if start == end:
        stats = {"expanded": 0, "generated": 1, "frontier_peak": 1}
        if return_path:
            return (0, [start], stats) if return_stats else (0, [start])
        return (0, stats) if return_stats else 0

    def heuristic(point: Point) -> int:
        return abs(point[0] - end[0]) + abs(point[1] - end[1])

    infinity = math.inf
    best_cost = {start: 0}
    parent: Dict[Point, Optional[Point]] = {start: None}
    directions = ((-1, 0), (1, 0), (0, -1), (0, 1))
    counter = 0
    frontier = [(heuristic(start), 0, counter, start)]
    expanded = 0
    generated = 1
    frontier_peak = 1

    while frontier:
        _, current_cost, _, current = heapq.heappop(frontier)
        if current_cost != best_cost.get(current, infinity):
            continue

        expanded += 1
        if current == end:
            stats = {
                "expanded": expanded,
                "generated": generated,
                "frontier_peak": frontier_peak,
            }
            if return_path:
                path = []
                node: Optional[Point] = current
                while node is not None:
                    path.append(node)
                    node = parent[node]
                path.reverse()
                return (
                    (current_cost, path, stats)
                    if return_stats
                    else (current_cost, path)
                )
            return (current_cost, stats) if return_stats else current_cost

        for dr, dc in directions:
            neighbor = (current[0] + dr, current[1] + dc)
            if not in_bounds(neighbor):
                continue
            step_cost = cell_cost(grid[neighbor[0]][neighbor[1]])
            if step_cost is None:
                continue

            new_cost = current_cost + step_cost
            if new_cost >= best_cost.get(neighbor, infinity):
                continue

            best_cost[neighbor] = new_cost
            parent[neighbor] = current
            counter += 1
            heapq.heappush(
                frontier,
                (new_cost + heuristic(neighbor), new_cost, counter, neighbor),
            )
            generated += 1
            frontier_peak = max(frontier_peak, len(frontier))

    result = math.inf
    stats = {
        "expanded": expanded,
        "generated": generated,
        "frontier_peak": frontier_peak,
    }
    if return_path:
        return (result, [], stats) if return_stats else (result, [])
    return (result, stats) if return_stats else result


def a_star(
    start_name: str,
    goal_name: str,
    grid=None,
    points: Optional[Mapping[str, Point]] = None,
) -> int | float:
    """按点名计算 A* 最短移动代价，无法到达时返回 inf。"""

    active_grid = GRID if grid is None else grid
    active_points = POINTS if points is None else points
    if start_name not in active_points or goal_name not in active_points:
        raise KeyError("起点或终点名称不存在")
    return shortest_path_cost(
        active_points[start_name], active_points[goal_name], active_grid
    )


def build_distance_matrix(
    grid=None,
    points: Optional[Mapping[str, Point]] = None,
    names: Optional[Iterable[str]] = None,
) -> Dict[str, Dict[str, int | float]]:
    """计算指定节点两两之间的最短移动代价。"""

    active_points = POINTS if points is None else points
    node_names = tuple(names) if names is not None else ("A", "B", "T1", "T2", "T3", "T4")
    return {
        start: {
            goal: a_star(start, goal, grid=grid, points=active_points)
            for goal in node_names
        }
        for start in node_names
    }


nodes = ("A", "B", "T1", "T2", "T3", "T4")
DIST_MATRIX = build_distance_matrix(names=nodes)


@dataclass(frozen=True)
class GameState:
    """一局游戏在某一决策时刻的完整状态。"""

    pos_A: str
    pos_B: str
    score_A: int
    score_B: int
    remaining: Tuple[str, ...]
    turn: str

    @property
    def utility(self) -> int:
        return self.score_A - self.score_B

    def as_dict(self) -> dict:
        return {
            "pos_A": self.pos_A,
            "pos_B": self.pos_B,
            "score_A": self.score_A,
            "score_B": self.score_B,
            "remaining": list(self.remaining),
            "turn": self.turn,
        }


def initial_state() -> GameState:
    return GameState(
        pos_A="A",
        pos_B="B",
        score_A=0,
        score_B=0,
        remaining=("T1", "T2", "T3", "T4"),
        turn="A",
    )


def _coerce_state(state) -> GameState:
    if isinstance(state, GameState):
        return state
    if not isinstance(state, Mapping):
        raise TypeError("state 必须是 GameState 或字典")
    return GameState(
        pos_A=state["pos_A"],
        pos_B=state["pos_B"],
        score_A=state["score_A"],
        score_B=state["score_B"],
        remaining=tuple(state["remaining"]),
        turn=state["turn"],
    )


def apply_action(
    state,
    action: str,
    distance_matrix: Optional[Mapping[str, Mapping[str, float]]] = None,
    treasure_values: Optional[Mapping[str, int]] = None,
):
    """执行一次宝藏选择并返回新状态，不修改原状态。"""

    current = _coerce_state(state)
    distances = DIST_MATRIX if distance_matrix is None else distance_matrix
    values = TREASURE_VALUES if treasure_values is None else treasure_values
    if action not in current.remaining:
        raise ValueError(f"宝藏 {action!r} 不在剩余集合中")
    if current.turn not in {"A", "B"}:
        raise ValueError("turn 必须为 A 或 B")

    if current.turn == "A":
        travel_cost = distances[current.pos_A][action]
        if not math.isfinite(travel_cost):
            raise ValueError(f"{current.pos_A} 无法到达 {action}")
        next_state = replace(
            current,
            pos_A=action,
            score_A=current.score_A + values[action] - travel_cost,
            remaining=tuple(item for item in current.remaining if item != action),
            turn="B",
        )
    else:
        travel_cost = distances[current.pos_B][action]
        if not math.isfinite(travel_cost):
            raise ValueError(f"{current.pos_B} 无法到达 {action}")
        next_state = replace(
            current,
            pos_B=action,
            score_B=current.score_B + values[action] - travel_cost,
            remaining=tuple(item for item in current.remaining if item != action),
            turn="A",
        )
    return next_state


def _game_search(
    state: GameState,
    depth: int,
    alpha: float,
    beta: float,
    use_alpha_beta: bool,
    distance_matrix: Mapping[str, Mapping[str, float]],
    treasure_values: Mapping[str, int],
    stats: MutableMapping[str, int],
) -> float:
    stats["visited_nodes"] += 1
    if depth <= 0 or not state.remaining:
        stats["leaf_evaluations"] += 1
        return float(state.utility)

    reachable_actions = [
        action
        for action in state.remaining
        if math.isfinite(
            distance_matrix[
                state.pos_A if state.turn == "A" else state.pos_B
            ][action]
        )
    ]
    if not reachable_actions:
        stats["leaf_evaluations"] += 1
        return float(state.utility)

    if state.turn == "A":
        best_value = -math.inf
        for index, action in enumerate(reachable_actions):
            child = apply_action(state, action, distance_matrix, treasure_values)
            value = _game_search(
                child,
                depth - 1,
                alpha,
                beta,
                use_alpha_beta,
                distance_matrix,
                treasure_values,
                stats,
            )
            max_previous = best_value
            best_value = max(best_value, value)
            alpha = max(alpha, best_value)
            if best_value != max_previous:
                stats["chosen_updates"] += 1
            if use_alpha_beta and beta <= alpha:
                stats["pruned_actions"] += len(reachable_actions) - index - 1
                stats["cutoffs"] += 1
                break
        return best_value

    best_value = math.inf
    for index, action in enumerate(reachable_actions):
        child = apply_action(state, action, distance_matrix, treasure_values)
        value = _game_search(
            child,
            depth - 1,
            alpha,
            beta,
            use_alpha_beta,
            distance_matrix,
            treasure_values,
            stats,
        )
        min_previous = best_value
        best_value = min(best_value, value)
        beta = min(beta, best_value)
        if best_value != min_previous:
            stats["chosen_updates"] += 1
        if use_alpha_beta and beta <= alpha:
            stats["pruned_actions"] += len(reachable_actions) - index - 1
            stats["cutoffs"] += 1
            break
    return best_value


def game_search(
    state,
    depth: int,
    alpha: float = -math.inf,
    beta: float = math.inf,
    use_alpha_beta: bool = True,
    return_stats: bool = False,
    distance_matrix: Optional[Mapping[str, Mapping[str, float]]] = None,
    treasure_values: Optional[Mapping[str, int]] = None,
):
    """计算当前状态的博弈值；A 为 MAX，B 为 MIN。"""

    if depth < 0:
        raise ValueError("depth 不能为负数")
    current = _coerce_state(state)
    distances = DIST_MATRIX if distance_matrix is None else distance_matrix
    values = TREASURE_VALUES if treasure_values is None else treasure_values
    stats = {
        "visited_nodes": 0,
        "leaf_evaluations": 0,
        "chosen_updates": 0,
        "pruned_actions": 0,
        "cutoffs": 0,
    }
    value = _game_search(
        current,
        depth,
        float(alpha),
        float(beta),
        bool(use_alpha_beta),
        distances,
        values,
        stats,
    )
    return (value, stats) if return_stats else value


def find_best_first_move(
    depth: int,
    use_alpha_beta: bool = True,
    return_stats: bool = False,
    distance_matrix: Optional[Mapping[str, Mapping[str, float]]] = None,
    treasure_values: Optional[Mapping[str, int]] = None,
):
    """
    求 A 的最优首步及其在最坏理性应对下可保证的收益差。

    并列时保留初始状态 remaining 中靠前的动作；输入状态没有被修改。
    """

    if depth < 1:
        raise ValueError("depth 必须至少为 1")

    distances = DIST_MATRIX if distance_matrix is None else distance_matrix
    values = TREASURE_VALUES if treasure_values is None else treasure_values
    state = initial_state()
    best_action: Optional[str] = None
    best_value = -math.inf
    first_move_values: Dict[str, float] = {}
    totals = {
        "visited_nodes": 0,
        "leaf_evaluations": 0,
        "chosen_updates": 0,
        "pruned_actions": 0,
        "cutoffs": 0,
    }

    for action in state.remaining:
        child = apply_action(state, action, distances, values)
        value, stats = game_search(
            child,
            depth - 1,
            -math.inf,
            math.inf,
            use_alpha_beta,
            True,
            distances,
            values,
        )
        first_move_values[action] = value
        for key in totals:
            totals[key] += stats[key]
        if value > best_value:
            best_value = value
            best_action = action

    if best_action is None:
        raise ValueError("初始状态没有可执行动作")
    first_move_values = {
        action: int(value) if float(value).is_integer() else value
        for action, value in first_move_values.items()
    }
    if float(best_value).is_integer():
        best_value = int(best_value)
    result = (best_action, best_value)
    if return_stats:
        return result, {
            "search_stats": totals,
            "first_move_values": first_move_values,
        }
    return result


if __name__ == "__main__":
    root_state = initial_state()
    payload = {
        "initial_state": root_state.as_dict(),
        "treasure_values": dict(TREASURE_VALUES),
        "distance_matrix": {
            start: {goal: int(DIST_MATRIX[start][goal]) for goal in nodes}
            for start in nodes
        },
        "results": {
            "Minimax": {},
            "Alpha-Beta": {},
        },
    }
    for algorithm, use_alpha_beta in (("Minimax", False), ("Alpha-Beta", True)):
        for height in (2, 4):
            target, value = find_best_first_move(
                height, use_alpha_beta=use_alpha_beta
            )
            payload["results"][algorithm][f"H={height}"] = {
                "best_target": target,
                "best_value": value,
            }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
