"""
september01.pyを改造
- スピードの落とし方変更
"""
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.cm as cm  # カラーマップ
import japanize_matplotlib
import numpy as np
import pandas as pd
import random
import heapq
import datetime
import modules.Agent_Data as ag
import xx_mycolor  # マイカラー
import modules.Scattering as sca
import copy

SIMU_COUNT = 30  # シミュレーション回数
AGENT_NUM = 10  # 初期エージェント数
# BORN_AGENT_NUM = 5  # 新規エージェント数
# BORN_INTERVAL = 0.4  # エージェント生成間隔
BORN_AGENT_NUM = 30  # 新規エージェント数
BORN_INTERVAL = 0.8  # エージェント生成間隔
MAP_SIZE_X = 80  # マップサイズ
MAP_SIZE_Y = 40
SPEED = 4  # エージェント最大速度
object_cost = 100  # 障害物のコスト
color_list = xx_mycolor.color_list
start_list = []
start_list_2 = []
goal_list = []
goal_list_2 = []
wall_list = []  # 障害物座標list
result = []  # 結果記録用
result_agents = []
use_colors = xx_mycolor.CrandomList(3)


class Map():
    """ マップ作りまーす """

    def __init__(self, object_cost=object_cost):
        # self.map = pd.read_excel('Map.xlsx', sheet_name=2)
        self.map = pd.read_excel('Map.xlsx', sheet_name=4)
        # self.map = self.map.T
        self.map = self.map.fillna(0)  # NaNを0
        # --- Mapから各地点を取得しリストへ ---
        for y in range(MAP_SIZE_Y):
            for x in range(MAP_SIZE_X):
                if self.map.iat[y, x] == "s":
                    start_list.append([y, x])
                elif self.map.iat[y, x] == "s2":
                    start_list_2.append([y, x])
                elif self.map.iat[y, x] == "g":
                    goal_list.append([y, x])
                elif self.map.iat[y, x] == "g2":
                    goal_list_2.append([y, x])
                elif self.map.iat[y, x] == "x":
                    wall_list.append([y, x])
        self.map = self.map.replace('x', object_cost)  # 壁にコスト
        self.map = self.map.replace('s', -1)  # マップにコスト
        self.map = self.map.replace('s2', -1)
        self.map = self.map.replace('g', 1)  # マップにコスト
        self.map = self.map.replace('g2', 1)

    def generate_map(self):
        self.map = self.map.values.tolist()  # dfをリスト変換
        return self.map


class Agent():
    """ エージェントクラス """

    def __init__(self, ID, init_x, init_y, goal_list, maze, agent_type):
        self.id = ID
        self.position = [init_x, init_y]
        self.r = random.randint(0, len(goal_list)-1)
        self.goal = goal_list[self.r]  # 改札ランダム設定
        self.agent_type = agent_type  # 0:降りる, 1:乗る
        self.speed = SPEED
        self.path = astar(maze, tuple(self.position), tuple(self.goal))
        self.impact_count = 0  # 衝突数
        # --- color設定 ---
        if self.agent_type == 0:
            self.color = "red"
        else:
            self.color = "blue"

        # ------------------
    # --- 情報 ---
    def info(self):
        return f"ID:{self.id}\n現在地:{self.position}\n改札:{self.goal}\n経路:{self.path}\n衝突数:{self.impact_count}"

    # --- 経路探索 ---
    def calc_path(self, maze):
        # タプルにしないと動かない
        return astar(maze, tuple(self.position), tuple(self.goal))

    # --- 移動 ---
    def move(self, next_people_map):  # pathリスト順に位置を更新
        if len(self.path) <= self.speed:
            self.position = self.goal
            return

        if next_people_map[self.path[self.speed][0]][self.path[self.speed][1]] > 1:  # 同じマスに一人以上いる場合
            # 速度更新
            self.speed = SPEED - \
                next_people_map[self.path[self.speed]
                                [0]][self.path[self.speed][1]]-1
            if self.speed < 1:
                self.speed = 1
        for _ in range(self.speed):
            next_position = self.path.pop(0)
            self.position = next_position


class Node():
    def __init__(self, position, parent=None):
        self.position = position
        self.parent = parent
        self.g = 0  # スタートからの距離
        self.h = 0  # ヒューリスティック距離
        self.f = 0  # 総コスト
    # --- ノードの比較 ---

    def __lt__(self, other):  # "less than"のlt
        return self.f < other.f


def heuristic(a, b):
    """
    a: 現在地, b: ゴール
    """
    # return abs(a[0] - b[0]) + abs(a[1] - b[1])
    return (a[0] - b[0])**2 + (a[1] - b[1])**2


def astar(maze, start, end):  # A*
    open_list = []  # 探索中のノード
    closed_list = set()  # 見たノードたち
    start_node = Node(start)  # スタートノード
    end_node = Node(end)  # えんど
    heapq.heappush(open_list, start_node)  # open_listにstart_nodeを追加
    # --- open_listをもれなく ---
    while open_list:
        current_node = heapq.heappop(open_list)  # 最小値を取り出し消去
        closed_list.add(current_node.position)  # 見たよ
        # --- 現在ノードがエンドノードならpathを作成 ---
        if current_node.position == end_node.position:
            path = []
            while current_node:
                path.append(current_node.position)
                current_node = current_node.parent
            return path[::-1]
        (x, y) = current_node.position
        neighbors = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1),
                     (x+1, y+1), (x+1, y-1), (x-1, y+1), (x-1, y-1)]
        for index, next_position in enumerate(neighbors):
            if (next_position[0] < 0 or next_position[0] >= len(maze) or  # 迷路の左右に飛び出る
                # 迷路の上に飛ぶ、下に埋められる
                next_position[1] < 0 or next_position[1] >= len(maze[0]) or
                maze[next_position[0]][next_position[1]] == object_cost or  # 壁に当たる
                    next_position in closed_list):  # 既に見た
                continue  # 次のループ
            # --- お隣ノード作成、親は現在ノード ---
            neighbor = Node(next_position, current_node)
            if index < 4:
                neighbor.g = current_node.g + 1
            else:
                neighbor.g = current_node.g + 1.414
                neighbor.h = heuristic(neighbor.position, end_node.position)
                neighbor.f = neighbor.g + neighbor.h
            if add_to_open(open_list, neighbor):
                heapq.heappush(open_list, neighbor)  # open_listにneighborを追加
    return [start]  # 変更した


def add_to_open(open_list, neighbor):
    for node in open_list:
        # お隣が探索中の中にある & gが大きい
        if neighbor.position == node.position and neighbor.g >= node.g:
            return False
    return True


# 結果出力
def result_print(result_agents):
    total_impact = 0
    average_impact = 0
    for agent in result_agents:
        total_impact += agent.impact_count
    average_impact = total_impact/len(result_agents)
    print(
        f"総脱出数：{len(result_agents)}\nトータルインパクト: {total_impact}\nアベレージインパクト: {average_impact}")


# シミュ
def simulation(SIMU_COUNT):
    s = 0  # シミュレーションカウント用
    sum_id = AGENT_NUM  # id合計
    result.append(f"最終更新: {datetime.datetime.now()}")
    # --- プロット設定 ---
    fig, ax = plt.subplots(figsize=(MAP_SIZE_X, MAP_SIZE_Y),
                           facecolor=xx_mycolor.Crandom())
    sca.mapping_set(ax, MAP_SIZE_X, MAP_SIZE_Y)

    # --- マップ生成 ---
    map = Map()
    maze = map.generate_map()

    start_lists = [start_list, start_list_2]
    goal_lists = [goal_list, goal_list_2]

    # --- コスト図をログへ ---
    for m in maze:
        result.append(m)
    # --- エージェント初期配置 ---
    agents = []
    result.append(f"---------simulation:0------------")
    for i in range(AGENT_NUM):
        # --- 初期位置、目的の改札設定 ---
        agent_type = random.randint(0, 1)
        now_start_list = start_lists[agent_type]
        rs = random.randint(0, len(now_start_list)-1)
        start_x, start_y = now_start_list[rs][0], now_start_list[rs][1]
        agent = Agent(i, start_x, start_y,
                      goal_lists[agent_type], maze, agent_type)
        now_map = ag.agentNowMap(agents, maze)
        if now_map[agent.position[0]][agent.position[1]] < 2:
            agents.append(agent)

        ax.scatter(agent.position[1], agent.position[0], c=agent.color)
        ax.text(agent.position[1], agent.position[0], agent.id)
        result.append(agent.info())
    # --- 障害物の初期配置 ---
    sca.scatman_v2(ax, wall_list, goal_list,
                   goal_list_2, start_list, start_list_2)

    def update(frame):
        nonlocal s  # シミュレーションカウント
        nonlocal sum_id
        s += 1
        global result
        result.append(f"---------simu: {s}------------")
        print("simu: ", s)
        # ------------------------------
        ax.set_title(f"simu: {s}")
        ax.clear()  # 前のフレームのエージェントをクリア
        sca.mapping_set(ax, MAP_SIZE_X, MAP_SIZE_Y)

        # --- エージェント位置更新 ---
        for agent in agents:
            # --- ゴール済みエージェントの削除 ---
            if agent.position == agent.goal:
                result_agents.append(agent)
                agents.remove(agent)
                continue

            next_people_map = ag.agentNextCountMap(agents, maze)
            agent.move(next_people_map)
            ag.agentImpactUpdate(agents, maze)
            ax.scatter(agent.position[1], agent.position[0], c=agent.color)
            ax.text(agent.position[1], agent.position[0], agent.id)
            ax.set_title(f"シミュレーション: {s}")
            result.append(agent.info())

        # --- 新規エージェント ---
        for i in range(BORN_AGENT_NUM):
            if random.random() < BORN_INTERVAL:
                # --- 初期位置、目的の改札設定 ---
                agent_type = random.randint(0, 1)
                now_start_list = start_lists[agent_type]
                rs = random.randint(0, len(now_start_list)-1)
                start_x, start_y = now_start_list[rs][0], now_start_list[rs][1]
                agent = Agent(i, start_x, start_y,
                              goal_lists[agent_type], maze, agent_type)
                now_map = ag.agentNowMap(agents, maze)
                if now_map[agent.position[0]][agent.position[1]] < 2:
                    agents.append(agent)
                ax.scatter(agent.position[1], agent.position[0])
                ax.text(agent.position[1], agent.position[0], agent.id)
                result.append(agent.info())
                sum_id += 1
        # --- 障害物の再配置 ---
        sca.scatman_v2(ax, wall_list, goal_list,
                       goal_list_2, start_list, start_list_2)
        # ------------

    ani = animation.FuncAnimation(
        fig, update, frames=SIMU_COUNT, interval=100, repeat=False)
    plt.show()
    # --- gif保存用↓ ---
    # ani.save("xx.gif", writer="imagemagick")
    # --- 結果出力 ---
    with open("xxlog.txt", "w") as f:
        for line in result:
            print(line, file=f)


    # ---------------
if __name__ == "__main__":
    simulation(SIMU_COUNT)
    result_print(result_agents)
