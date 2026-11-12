# 当代人工智能实验二 搜索算法

本目录包含实验二四道题的 Python 实现，包括：

- 四邻域迷宫 A*
- 加权地形 A*
- Minimax 与 Alpha-Beta 剪枝
- A* 距离矩阵与竞争宝藏博弈

代码仅使用 Python 标准库，运行环境要求 Python 3.10 或更高版本。

## 文件说明

| 文件 | 功能 | 默认返回值 |
| --- | --- | --- |
| `题目一.py` | 迷宫最短路径 | 路径坐标列表或 `[]` |
| `题目二.py` | 加权地图最小移动代价 | 总代价或 `-1` |
| `题目三.py` | 博弈树最佳得分 | MAX 玩家的最佳得分 |
| `题目四.py` | 距离矩阵、Minimax、Alpha-Beta | 完整结果字典 |

## 运行环境

所有命令都应在当前目录执行：

```powershell
cd C:\Users\Lenovo\Desktop\当代人工智能第二次大实验\当代人工智能实验二
```

检查 Python 是否可用：

```powershell
python --version
```

代码无需安装第三方包。可用以下命令检查四个文件的语法：

```powershell
python -m py_compile .\题目一.py .\题目二.py .\题目三.py .\题目四.py
```

## 使用方式概览

每个文件都有两种使用方式：

1. 直接运行文件：适合按实验文档样例从标准输入提交数据。
2. 导入函数：适合在自己的 Python 代码或自动测试中调用。

`题目一.py` 和 `题目二.py` 从标准输入读取三个 Python 字面量，顺序固定为：

```text
起点
终点
地图
```

`题目三.py` 从标准输入读取题面 JSON。`题目四.py` 使用固定地图，不需要输入。

注意：不要直接把 Python 的元组和二维列表粘贴到 PowerShell 提示符中。PowerShell 会自行解释这些符号，应使用下文给出的 here-string 管道方式。

## 题目一：迷宫 A*

### 文件直接运行

在 PowerShell 中复制并执行：

```powershell
@'
(0, 0)
(3, 4)
[
['S', '.', '.', 'X', '.'],
['.', 'X', '.', '.', '.'],
['.', 'X', '.', 'X', '.'],
['.', '.', '.', 'X', 'E'],
['X', 'X', '.', '.', '.']
]
'@ | python .\题目一.py
```

预期输出：

```text
[(0, 0), (0, 1), (0, 2), (1, 2), (1, 3), (1, 4), (2, 4), (3, 4)]
```

最短路径长度为 7。若存在多条同样短的路径，程序返回其中任意一条。

### 函数调用

```python
from 题目一 import astar_maze

maze = [
    ["S", ".", ".", "X", "."],
    [".", "X", ".", ".", "."],
    [".", "X", ".", "X", "."],
    [".", ".", ".", "X", "E"],
    ["X", "X", ".", ".", "."],
]

path = astar_maze((0, 0), (3, 4), maze)
print(path)
```

### 搜索统计

```python
from 题目一 import astar_maze, zero_heuristic

path, stats = astar_maze(
    (0, 0),
    (3, 4),
    maze,
    heuristic_func=zero_heuristic,
    return_stats=True,
)
print(path)
print(stats)
```

统计字段：

- `expanded`：实际展开的节点数
- `generated`：成功加入优先队列的节点数
- `frontier_peak`：优先队列峰值
- `path_cost`：路径代价，无解时为 `-1`

## 题目二：加权地形 A*

每进入一个相邻格，支付目标格的权值；终点 `E` 的进入代价按 0 计算。

### 文件直接运行

```powershell
@'
(0, 0)
(4, 4)
[
['S', 1, 1, 8, 1],
[1, 8, 3, 1, 1],
[1, 8, 1, 8, 1],
[1, 1, 1, 8, 1],
[8, 8, 1, 1, 'E']
]
'@ | python .\题目二.py
```

预期输出：

```text
7
```

对应路径：

```text
(0,0) -> (1,0) -> (2,0) -> (3,0) -> (3,1) -> (3,2)
      -> (4,2) -> (4,3) -> (4,4)
```

前 7 次进入的地形权值均为 1，最后进入 E 的代价为 0，因此总代价为 7。

### 函数调用

```python
from 题目二 import weighted_astar

grid = [
    ["S", 1, 1, 8, 1],
    [1, 8, 3, 1, 1],
    [1, 8, 1, 8, 1],
    [1, 1, 1, 8, 1],
    [8, 8, 1, 1, "E"],
]

cost = weighted_astar((0, 0), (4, 4), grid)
print(cost)
```

### 启发函数模式

```python
weighted_astar(start, end, grid, h_mode="corrected")
```

可选值：

- `zero`：h=0，等价于 Dijkstra 对照
- `manhattan`：使用曼哈顿距离
- `corrected`：使用考虑免费终点的修正下界
- `auto`：存在零权格时自动回退到 `zero`

设置 `return_stats=True` 可获得：

```python
cost, stats = weighted_astar(
    (0, 0), (4, 4), grid, h_mode="corrected", return_stats=True
)
print(cost)
print(stats)
```

## 题目三：Minimax 与 Alpha-Beta

### 文件直接运行

将下面的 JSON 粘贴到 PowerShell 中：

```powershell
@'
{
  "tree_structure": {
    "is_maximizing_player": true,
    "children": [
      {
        "is_maximizing_player": false,
        "children": [
          {
            "is_maximizing_player": true,
            "children": [{"value": 3}, {"value": 5}]
          },
          {
            "is_maximizing_player": true,
            "children": [{"value": 6}, {"value": 9}]
          }
        ]
      },
      {
        "is_maximizing_player": false,
        "children": [
          {
            "is_maximizing_player": true,
            "children": [{"value": 6}, {"value": 9}]
          },
          {
            "is_maximizing_player": true,
            "children": [{"value": 1}, {"value": 2}]
          }
        ]
      }
    ]
  }
}
'@ | python .\题目三.py
```

预期输出：

```text
5
```

### 使用 TreeNode

```python
from 题目三 import TreeNode, alpha_beta_pruning, minimax_value

leaf = [TreeNode(value=value) for value in (3, 5, 6, 9, 1, 2)]
max1 = TreeNode(children=[leaf[0], leaf[1]])
max2 = TreeNode(children=[leaf[2], leaf[3]])
max3 = TreeNode(children=[leaf[4], leaf[5]])
min1 = TreeNode(children=[max1, max2])
min2 = TreeNode(children=[max2, max3])
root = TreeNode(children=[min1, min2])

print(minimax_value(root))
print(alpha_beta_pruning(root))
```

两个函数的结果都应为 `5`。设置 `return_stats=True` 可比较叶节点访问数和剪枝次数。

## 题目四：竞争宝藏分配

### 文件直接运行

题目四使用固定地图和宝藏价值，不需要输入：

```powershell
python .\题目四.py
```

程序输出四部分：

1. `initial_state`：双方位置、累计收益、剩余宝藏和当前玩家
2. `treasure_values`：四个宝藏的价值
3. `distance_matrix`：6×6 关键点最短移动代价矩阵
4. `results`：Minimax 与 Alpha-Beta 分别取 H=2、H=4 时的最优首步和收益差

距离矩阵预期：

```text
        A   B  T1  T2  T3  T4
A       0  11  10   4   8   8
B      11   0   9   9   3   9
T1     10   9   0   6   6  12
T2      4   9   6   0   6   6
T3      8   3   6   6   0   6
T4      8   9  12   6   6   0
```

搜索结果预期：

```json
{
  "Minimax": {
    "H=2": {"best_target": "T2", "best_value": -1},
    "H=4": {"best_target": "T3", "best_value": 3}
  },
  "Alpha-Beta": {
    "H=2": {"best_target": "T2", "best_value": -1},
    "H=4": {"best_target": "T3", "best_value": 3}
  }
}
```

### 单独调用搜索函数

```powershell
python -c "from 题目四 import find_best_first_move; print(find_best_first_move(2, False)); print(find_best_first_move(2, True)); print(find_best_first_move(4, False)); print(find_best_first_move(4, True))"
```

预期输出：

```text
('T2', -1)
('T2', -1)
('T3', 3)
('T3', 3)
```

参数含义：

- 第一个参数为搜索深度 `H`
- 第二个参数为 `False` 时使用完整 Minimax
- 第二个参数为 `True` 时使用 Alpha-Beta
- 设置第三个参数 `return_stats=True` 可查看访问节点数、叶访问数和剪枝数

代码中的 `GameState` 保存：

- `pos_A`、`pos_B`：双方当前位置
- `score_A`、`score_B`：双方累计收益
- `remaining`：尚未取得的宝藏
- `turn`：当前玩家

### 输入数据说明

PDF 表格中 T3 的旁注为 7，但同页给出的两组预期输出只有在 T3 取 6 时才能同时成立。当前 `TREASURE_VALUES` 采用：

```python
{"T1": 9, "T2": 6, "T3": 6, "T4": 7}
```

这一配置用于匹配 PDF 给出的 H=2、H=4 标准答案。

## 算法性能与评分点复现

评分细则中的“算法性能”共 10 分，分为搜索效率评估和剪枝效率评估。代码负责实际搜索、剪枝以及返回统计指标；实验报告负责展示对比数据并解释差异。两部分共同支撑该评分项。

### 代码中已实现的性能机制

| 题目 | 代码中的实现 | `return_stats=True` 提供的数据 |
| --- | --- | --- |
| 题目一 | 曼哈顿距离 A*、零启发对照 | `expanded`、`generated`、`frontier_peak` |
| 题目二 | 修正可采纳启发、零启发对照 | `expanded`、`generated`、`frontier_peak` |
| 题目三 | Minimax 与 Alpha-Beta | `visited_nodes`、`leaf_evaluations`、`pruned_children` |
| 题目四 | 距离矩阵缓存、Minimax、Alpha-Beta | `visited_nodes`、`leaf_evaluations`、`pruned_actions`、`cutoffs` |

### 搜索效率评估

题目一使用报告中的 20×20 固定地图复现。随机种子为 `20261111`，每格障碍概率为 `0.23`：

```python
import random
from 题目一 import astar_maze, manhattan_distance, zero_heuristic

random.seed(20261111)
maze = [["." for _ in range(20)] for _ in range(20)]
for row in range(20):
    for col in range(20):
        if random.random() < 0.23:
            maze[row][col] = "X"
maze[0][0] = "S"
maze[19][19] = "E"

path_zero, stats_zero = astar_maze(
    (0, 0), (19, 19), maze, zero_heuristic, return_stats=True
)
path_manhattan, stats_manhattan = astar_maze(
    (0, 0), (19, 19), maze, manhattan_distance, return_stats=True
)

print("h=0:", stats_zero)
print("Manhattan:", stats_manhattan)
```

报告中的参考结果：

```text
h=0:       expanded=308, generated=308, frontier_peak=20
Manhattan: expanded=229, generated=244, frontier_peak=25
```

两者路径长度均为 `38`。曼哈顿启发使展开节点数减少约 `25.6%`，说明方向性下界减少了无效扩展。

### 题目二搜索效率

```python
from 题目二 import weighted_astar

grid = [
    ["S", 1, 1, 8, 1],
    [1, 8, 3, 1, 1],
    [1, 8, 1, 8, 1],
    [1, 1, 1, 8, 1],
    [8, 8, 1, 1, "E"],
]

for mode in ("zero", "manhattan", "corrected"):
    cost, stats = weighted_astar(
        (0, 0), (4, 4), grid, h_mode=mode, return_stats=True
    )
    print(mode, cost, stats)
```

报告中的参考结果：

| 启发模式 | 总代价 | 展开节点 | 生成节点 |
| --- | ---: | ---: | ---: |
| `zero` | 7 | 15 | 24 |
| `manhattan` | 7 | 11 | 19 |
| `corrected` | 7 | 11 | 19 |

样本地图的最小正权值为 1，因此曼哈顿和修正启发数值相同。报告同时说明了终点免费时原始曼哈顿启发可能高估的原因。

### 题目三剪枝效率

```python
from 题目三 import TreeNode, alpha_beta_pruning, minimax_value

leaf = [TreeNode(value=value) for value in (3, 5, 6, 9, 1, 2)]
max1 = TreeNode(children=[leaf[0], leaf[1]])
max2 = TreeNode(children=[leaf[2], leaf[3]])
max3 = TreeNode(children=[leaf[4], leaf[5]])
root = TreeNode(children=[
    TreeNode(children=[max1, max2]),
    TreeNode(children=[max2, max3]),
])

value_minimax, stats_minimax = minimax_value(root, return_stats=True)
value_ab, stats_ab = alpha_beta_pruning(root, return_stats=True)
print(value_minimax, stats_minimax)
print(value_ab, stats_ab)
```

报告中的参考结果：

| 算法 | 根值 | 访问节点 | 叶访问 | 剪枝次数 |
| --- | ---: | ---: | ---: | ---: |
| Minimax | 5 | 15 | 8 | 0 |
| Alpha-Beta | 5 | 14 | 7 | 2 |

两种算法根值相同，说明剪枝没有改变最优结果，同时减少了不必要的叶节点访问。

### 题目四剪枝效率

```python
from 题目四 import find_best_first_move

for height in (2, 4):
    for use_alpha_beta in (False, True):
        result, stats = find_best_first_move(
            height,
            use_alpha_beta=use_alpha_beta,
            return_stats=True,
        )
        algorithm = "Alpha-Beta" if use_alpha_beta else "Minimax"
        print(algorithm, f"H={height}", result, stats["search_stats"])
```

报告中的参考结果：

| 深度 | 算法 | 首步与收益差 | 访问节点 | 叶访问 | 剪枝动作 |
| --- | --- | --- | ---: | ---: | ---: |
| H=2 | Minimax | T2, -1 | 16 | 12 | 0 |
| H=2 | Alpha-Beta | T2, -1 | 16 | 12 | 0 |
| H=4 | Minimax | T3, 3 | 64 | 24 | 0 |
| H=4 | Alpha-Beta | T3, 3 | 54 | 19 | 5 |

H=4 时，Alpha-Beta 将访问节点从 `64` 降到 `54`，把叶访问从 `24` 降到 `19`。两种算法仍给出相同首步和收益差。报告还比较了原顺序、逆序和按即时收益优先排序时的剪枝开销。

### 报告中的对应图表

- 图 1 汇总四道题的节点数或叶访问数。
- 题目一、题目二的表格给出不同启发函数下的搜索规模。
- 题目三、题目四的表格给出 Minimax 与 Alpha-Beta 的访问量、叶访问和剪枝次数。
- 正文分析解释了启发函数、终点免费规则、候选顺序和搜索深度为什么会影响性能。

计时结果受设备和运行环境影响，不作为唯一依据；当前评估主要使用固定输入下的节点数和叶节点访问数，结果更容易复现。

## 在 Python 交互环境中运行

进入本目录后执行：

```powershell
python
```

随后可直接导入函数：

```python
from 题目一 import astar_maze
from 题目二 import weighted_astar
from 题目三 import alpha_beta_pruning
from 题目四 import find_best_first_move
```

输入结束后可执行：

```python
exit()
```

## 常见问题

### 为什么直接粘贴 `[` 会报错

因为那是 PowerShell 语法解析，不是 Python 输入。应使用前面的 here-string 管道命令：

```powershell
@'
Python 字面量内容
'@ | python .\题目一.py
```

### 程序为什么一直等待输入

`题目一.py`、`题目二.py` 和 `题目三.py` 会等待标准输入结束。逐行粘贴完成后，在 PowerShell 中按：

```text
Ctrl+Z
Enter
```

也可以在命令末尾通过管道一次性传入全部数据。

### `python` 命令不存在

先尝试：

```powershell
py --version
```

若 `python` 可用但 `py` 不可用，继续使用 `python`；若两者都不可用，需要先安装 Python 3.10 或更高版本。

### 无解时返回什么

- 题目一返回空列表 `[]`
- 题目二返回 `-1`

### 输入坐标的顺序

所有坐标均为 `(row, col)`，不是 `(x, y)`；只允许上下左右移动。
