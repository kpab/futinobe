"""
september10.pyを改造
- 結果記録用
"""
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.cm as cm  # カラーマップ
from matplotlib import colormaps
from cmap import Colormap
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
from operator import attrgetter
import seaborn as sns

SIMU_COUNT = 260  # シミュレーション回数
SKIP_SIMU_COUNT = 60
AGENT_NUM = 10  # 初期エージェント数
BORN_AGENT_NUM = 30  # 新規エージェント数
HUTINOBE_BORN_RATE = 0.2
BORN_INTERVAL = 1.0  # エージェント生成間隔
MAP_SIZE_X = 80  # マップサイズ
MAP_SIZE_Y = 40
SPEED = 4  # エージェント最大速度
object_cost = 100  # 障害物のコスト
color_list = xx_mycolor.color_list
start_list = []
start_list_2 = []
goal_list = []
goal_list_2 = []
mix_list = []  # スタート地点かつゴール地点s2g1
mix_list_2 = []  # s1g2
wall_list = []  # 障害物座標list
result = []  # 結果記録用
agents = []
result_agents = []
total_slow = 0
use_colors = xx_mycolor.CrandomList(3)
agent_text_on = True


class Map():
    """ マップ作りまーす """

    def __init__(self, object_cost=object_cost):
        self.map = pd.read_excel('Map.xlsx', sheet_name=11)
        # self.map = self.map.T
        self.map = self.map.fillna(0)  # NaNを0
        # --- Mapから各地点を取得しリストへ ---
        for y in range(MAP_SIZE_Y):
            for x in range(MAP_SIZE_X):
                if self.map.iat[y, x] == "s":
                    start_list.append([y, x])
                elif self.map.iat[y, x] == "s1":
                    start_list.append([y, x])
                elif self.map.iat[y, x] == "s2":
                    start_list_2.append([y, x])
                elif self.map.iat[y, x] == "g":
                    goal_list.append([y, x])
                elif self.map.iat[y, x] == "g1":
                    goal_list.append([y, x])
                elif self.map.iat[y, x] == "g2":
                    goal_list_2.append([y, x])
                elif self.map.iat[y, x] == "s2g1":
                    goal_list.append([y, x])
                    start_list_2.append([y, x])
                    mix_list.append([y, x])
                elif self.map.iat[y, x] == "s1g2":
                    goal_list_2.append([y, x])
                    start_list.append([y, x])
                    mix_list_2.append([y, x])
                elif self.map.iat[y, x] == "x":
                    wall_list.append([y, x])

        self.map = self.map.replace('x', object_cost)  # 壁にコスト
        self.map = self.map.replace('s', 1)  # マップにコスト
        self.map = self.map.replace('s1', 1)
        self.map = self.map.replace('s2', 1)
        self.map = self.map.replace('g', 1)  # マップにコスト
        self.map = self.map.replace('g1', 1)
        self.map = self.map.replace('g2', 1)
        self.map = self.map.replace('s2g1', 1)
        self.map = self.map.replace('s1g2', 1)

    def generate_map(self):
        self.map = self.map.values.tolist()  # dfをリスト変換
        return self.map


class Agent:
    def __init__(self, ID, init_x, init_y, goal_list, maze, agent_type):
        self.id = ID
        self.position = [init_x, init_y]
        self.r = random.randint(0, len(goal_list)-1)
        self.goal = goal_list[self.r]  # 改札ランダム設定
        self.agent_type = agent_type  # 0:降りる, 1:乗る
        self.speed = SPEED
        graph = convert_to_adj_list(maze)  # グラフ形式に変換
        self.path = dijkstra(graph, tuple(self.position), tuple(self.goal))
        self.impact_count = 0  # 衝突数
        self.slow_count = 0  # 減速数

        self.color_num = init_y/80

        colormap = plt.get_cmap("ocean")
        N = self.position[1]
        # --- color設定 ---
        if self.agent_type == 0:
            self.color = "red"
        else:
            self.color = colormap(self.color_num)
        # ------------------
    # --- 情報 ---

    def info(self):
        return f"ID:{self.id}\n現在地:{self.position}\n改札:{self.goal}\n経路:{self.path}\n衝突数:{self.impact_count}\n減速数:{self.slow_count}"

    # --- 経路探索 ---
    def calc_path(self, maze):
        # タプルにしないと動かない
        # return astar(maze, tuple(self.position), tuple(self.goal))
        return dijkstra(maze, tuple(self.position), tuple(self.goal))

    # --- 移動 ---
    def move(self, next_people_map):  # pathリスト順に位置を更新
        global total_slow
        if len(self.path) <= self.speed:
            self.position = self.goal
            return

        if next_people_map[self.path[self.speed][0]][self.path[self.speed][1]] > 1:  # 同じマスに一人以上いる場合
            # 減速数更新
            self.slow_count += next_people_map[self.path[self.speed]
                                               [0]][self.path[self.speed][1]]-1
            # total_slow += next_people_map[self.path[self.speed]
            #                               [0]][self.path[self.speed][1]]-1

            # 速度更新
            self.speed = SPEED - \
                next_people_map[self.path[self.speed]
                                [0]][self.path[self.speed][1]]-1
            if self.speed < 1:
                self.speed = 1
        if self.speed > 0:
            for _ in range(self.speed):
                next_position = self.path.pop(0)
                self.position = next_position


# --- ダイクストラ ---
def dijkstra(graph, start, end):
    distances = {node: float('infinity') for node in graph}
    distances[start] = 0
    queue = [(0, start)]
    prev_nodes = {start: None}  # 各ノードの親ノードを記録する辞書

    while queue:
        current_distance, current_node = heapq.heappop(queue)

        if current_node == end:
            # 経路を再構築
            path = []
            while current_node is not None:
                path.append(current_node)
                current_node = prev_nodes.get(current_node)
            return path[::-1]  # 経路を逆順にして返す

        if distances[current_node] < current_distance:
            continue

        for neighbor, weight in graph.get(current_node, {}).items():
            distance = current_distance + weight

            if distance < distances[neighbor]:
                distances[neighbor] = distance
                prev_nodes[neighbor] = current_node
                heapq.heappush(queue, (distance, neighbor))

    return None


def convert_to_adj_list(maze):
    adj_list = {}
    rows = len(maze)
    cols = len(maze[0])

    for r in range(rows):
        for c in range(cols):
            node = (r, c)
            if maze[r][c] == object_cost:
                continue  # 障害物ノードをスキップ
            neighbors = {}
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1), (1, 1), (-1, -1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols:
                    neighbor = (nr, nc)
                    if maze[nr][nc] != object_cost:
                        neighbors[neighbor] = 1  # 隣接ノードとの重みを設定
            adj_list[node] = neighbors
    return adj_list


# 結果出力
def result_print(result_agents):
    global total_slow
    total_impact = 0
    average_impact = 0
    for agent in result_agents:
        total_impact += agent.impact_count
        total_slow += agent.slow_count
    average_impact = total_impact/len(result_agents)
    print(f"--この結果は最初の{SKIP_SIMU_COUNT}回をスキップしています。--")
    print(f"対象フレーム数は{SKIP_SIMU_COUNT+1}~{SIMU_COUNT}です")
    print(
        f"総脱出数：{len(result_agents)}\n総減速数: {total_slow}\nトータルインパクト: {total_impact}\nアベレージインパクト: {round(average_impact,1)}\nアベレージスロウ: {round(total_slow/len(result_agents),1)}\n脱出数[人/f]: {len(result_agents)/(SIMU_COUNT-SKIP_SIMU_COUNT)}")


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

    total_map = ag.resetTotalAgentMap(maze)
    red_map = ag.resetTotalAgentMap(maze)
    blue_map = ag.resetTotalAgentMap(maze)

    start_lists = [start_list, start_list_2]
    goal_lists = [goal_list, goal_list_2]

    # --- コスト図をログへ ---
    for m in maze:
        result.append(m)
    # --- エージェント初期配置 ---
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
        else:
            sum_id -= 1

        ax.scatter(agent.position[1], agent.position[0], c=agent.color)
        if agent_text_on:

            ax.text(agent.position[1], agent.position[0], agent.id)
        result.append(agent.info())
    # --- 障害物の初期配置 ---
    sca.scatman_v2(ax, wall_list, goal_list,
                   goal_list_2, start_list, start_list_2, mix_list, mix_list_2)

    def update(frame):
        nonlocal s  # シミュレーションカウント
        nonlocal sum_id
        s += 1
        global result
        global agents
        result.append(f"---------simu: {s}------------")
        print("simu: ", s)
        # ------------------------------
        ax.set_title(f"simu: {s}")
        ax.clear()  # 前のフレームのエージェントをクリア
        sca.mapping_set(ax, MAP_SIZE_X, MAP_SIZE_Y)
        ag.agentImpactUpdate(agents, maze)
        # ag.updateAgentTotalMap(agents, total_agent_map)
        ag.updateAgentTotalMapRB(agents, total_map, red_map, blue_map)

        agents = sorted(agents, key=lambda x: x.id)

        # --- エージェント位置更新 ---
        for agent in agents:
            # --- ゴール済みエージェントの削除 ---
            if agent.position == agent.goal:
                if s > SKIP_SIMU_COUNT:
                    result_agents.append(agent)
                agents.remove(agent)
                continue

            next_people_map = ag.agentNextCountMap(agents, maze)
            agent.move(next_people_map)

            ax.scatter(agent.position[1], agent.position[0], c=agent.color)
            if agent_text_on:
                ax.text(agent.position[1], agent.position[0], agent.id)
            ax.set_title(f"シミュレーション: {s}")
            result.append(agent.info())

        # --- 新規エージェント ---
        for i in range(BORN_AGENT_NUM):
            if random.random() < BORN_INTERVAL:
                # --- 初期位置、目的の改札設定 ---
                # agent_type = random.randint(0, 1)
                agent_type = 0 if random.random() < HUTINOBE_BORN_RATE else 1
                now_start_list = start_lists[agent_type]
                rs = random.randint(0, len(now_start_list)-1)
                start_x, start_y = now_start_list[rs][0], now_start_list[rs][1]
                agent = Agent(sum_id+i, start_x, start_y,
                              goal_lists[agent_type], maze, agent_type)
                now_map = ag.agentNowMap(agents, maze)
                if now_map[agent.position[0]][agent.position[1]] < 2:
                    agents.append(agent)
                else:
                    sum_id -= 1
                ax.scatter(agent.position[1], agent.position[0])
                if agent_text_on:
                    ax.text(agent.position[1], agent.position[0], agent.id)
                result.append(agent.info())
                sum_id += 1
        # --- 障害物の再配置 ---
        sca.scatman_v2(ax, wall_list, goal_list,
                       goal_list_2, start_list, start_list_2, mix_list, mix_list_2)
        # ------------

    ani = animation.FuncAnimation(
        fig, update, frames=SIMU_COUNT, interval=100, repeat=False)
    # plt.show()
    # --- gif保存用↓ ---
    # ani.save("xx.gif", writer="imagemagick")
    # --- 結果出力 ---
    with open("xxlog.txt", "w") as f:
        for line in result:
            print(line, file=f)

    heatMapping(total_map, red_map, blue_map)


# ヒートマップ
def heatMapping(total_map, red_map, blue_map):
    fig, ax = plt.subplots(figsize=(MAP_SIZE_X, MAP_SIZE_Y),
                           facecolor=xx_mycolor.Crandom())

    ax.set_title("全体ヒートマップ")
    sns.heatmap(total_map, cmap='cool', square=True)
    sca.scatman_heatver(ax, wall_list)
    plt.show()
    fig, ax1 = plt.subplots(figsize=(MAP_SIZE_X, MAP_SIZE_Y),
                            facecolor=xx_mycolor.Crandom())
    ax1.set_title("淵野辺民ヒートマップ")
    sns.heatmap(red_map, cmap='Reds', square=True)
    sca.scatman_heatver(ax1, wall_list)

    plt.show()
    fig, ax2 = plt.subplots(figsize=(MAP_SIZE_X, MAP_SIZE_Y),
                            facecolor=xx_mycolor.Crandom())
    ax2.set_title("その他ヒートマップ")
    sns.heatmap(blue_map, cmap='Blues', square=True)
    sca.scatman_heatver(ax2, wall_list)
    plt.show()
    fig, ax4 = plt.subplots(figsize=(MAP_SIZE_X, MAP_SIZE_Y),
                            facecolor=xx_mycolor.Crandom())

    ax4.set_title("全体ヒートマップ")
    sns.heatmap(total_map, cmap='cool', square=True)
    sca.scatman_heatver(ax4, wall_list)
    plt.show()


    # ---------------
if __name__ == "__main__":
    bool_agText = input("テキストを表示しない場合は何か入力: ")
    if bool_agText:
        agent_text_on = False
    simulation(SIMU_COUNT)
    result_print(result_agents)
