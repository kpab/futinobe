"""
Marusan
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

SIMU_COUNT = 200  # シミュレーション回数
AGENT_NUM = 10  # 初期エージェント数
BORN_AGENT_NUM = 5  # 新規エージェント数
BORN_INTERVAL = 0.4  # エージェント生成間隔
# AGENT_NUM = 20 # 初期エージェント数
# BORN_AGENT_NUM = 10 # 新規エージェント数
# BORN_INTERVAL = 0.8 # エージェント生成間隔
# ↑テスト中
MAP_SIZE_X = 80  # マップサイズ
MAP_SIZE_Y = 40
SPEED = 3
object_cost = 100  # 障害物のコスト
color_list = xx_mycolor.color_list
start_list = []
goal_list = []
wall_list = []  # 障害物座標list
result = []  # 結果記録用
use_colors = xx_mycolor.CrandomList(3)


class Map():
    """ マップ作りまーす """

    def __init__(self, object_cost=object_cost):
        self.map = pd.read_excel('Map.xlsx', sheet_name=2)
        # self.map = self.map.T
        self.map = self.map.fillna(0)  # NaNを0
        # --- Mapから各地点を取得しリストへ ---
        for y in range(MAP_SIZE_Y):
            for x in range(MAP_SIZE_X):
                if self.map.iat[y, x] == "s":
                    start_list.append([y, x])
                elif self.map.iat[y, x] == "g":
                    goal_list.append([y, x])
                elif self.map.iat[y, x] == "x":
                    wall_list.append([y, x])

        self.map = self.map.replace('x', object_cost)  # 壁にコスト
        self.map = self.map.replace('s', -1)  # マップにコスト
        self.map = self.map.replace('g', 1)  # マップにコスト

    def generate_map(self):
        self.map = self.map.values.tolist()  # dfをリスト変換
        return self.map


class Agent():
    """ エージェントクラス """

    def __init__(self, ID, init_x, init_y, goal_list, maze):
        self.id = ID
        self.position = [init_x, init_y]
        self.r = random.randint(0, len(goal_list)-1)
        self.goal = goal_list[self.r]  # 改札ランダム設定
        # self.path = self.calc_path(maze) # 経路list
        self.path = astar(maze, tuple(self.position), tuple(self.goal))
        self.path.pop(0)
        self.speed = SPEED
        # --- color設定 ---
        # if self.r == 0:
        #     self.color = "red"
        # elif self.r == 1:
        #     self.color = "blue"
        # elif self.r == 2:
        #     self.color = "green"
        # else:
        #     self.color = "black"
        self.color = cm.Spectral(float(self.id)/50.0)  # カラーマップ指定
        # ------------------
    # --- 情報 ---

    def info(self):
        return f"ID:{self.id}\n現在地:{self.position}\n改札:{self.goal}\n経路:{self.path}"

    # --- 経路探索 ---
    def calc_path(self, maze):
        # タプルにしないと動かない
        return astar(maze, tuple(self.position), tuple(self.goal))

    # --- 移動 ---
    def move(self):  # pathリスト順に位置を更新
        if len(self.path) > self.speed-1:
            for _ in range(self.speed):
                next_position = self.path.pop(0)
                self.position = [next_position[0], next_position[1]]

        else:  # ゴール
            self.position = self.path[-1]
            # self.path = []


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
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


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
    # --- 経路が見つからない場合 ---
    avoid_posis = []
    avoid_pos_dic = {}
    (x, y) = start
    for k in range(SPEED):
        # if k<1:
        #     continue
        avoid_posis.append((-k+x, k+y))
        avoid_posis.append((k+x, k+y))
        avoid_posis.append((k+x, -k+y))
        avoid_posis.append((k+x, k+y))
    # print("before: ", avoid_posis)
    for avoid_pos in avoid_posis:
        if (avoid_pos[0] < 0 or avoid_pos[0] >= len(maze) or  # 迷路の左右に飛び出る
                # 迷路の上に飛ぶ、下に埋められる
                avoid_pos[1] < 0 or avoid_pos[1] >= len(maze[0]) or
                maze[avoid_pos[0]][avoid_pos[1]] == object_cost or  # 壁に当たる
                maze[avoid_pos[0]][avoid_pos[1]] != 0
            ):
            avoid_posis.remove(avoid_pos)
    # print("after: ", avoid_posis)
    # --- 重複を削除 ---
    avoid_posis = list(set(avoid_posis))
    if len(avoid_posis) < 1:
        print("動けぬ…")
        return [(x, y)]
    # --- 優先度並び替え ---
    for pos in avoid_posis:
        h = heuristic(pos, end)
        avoid_pos_dic[pos] = h
    # --- value(hの値)で並び替え ---
    avoid_pos_dic = sorted(avoid_pos_dic.items(), key=lambda x: x[1])
    # print(avoid_pos_dic)

    # メモ avoid_pos_dicの小さいvalueで絞り込んで、ランダムで選ばせたい

    # # --- リスト変換 ---
    # avoid_pos_list = list(avoid_pos_dic.values())
    # print(f"{start}からの避ける選択肢{avoid_posis}")
    return [avoid_pos_dic[0][0]]


def add_to_open(open_list, neighbor):
    for node in open_list:
        # お隣が探索中の中にある & gが大きい
        if neighbor.position == node.position and neighbor.g >= node.g:
            return False
    return True
# シミュ


def simulation(SIMU_COUNT):
    s = 0  # シミュレーションカウント用
    sum_id = AGENT_NUM  # id合計
    result.append(f"最終更新: {datetime.datetime.now()}")
    # --- プロット設定 ---
    # fig, ax = plt.subplots(figsize=(MAP_SIZE_X, MAP_SIZE_Y), facecolor=color_list[random.randint(0,len(color_list)-1)])
    fig, ax = plt.subplots(figsize=(MAP_SIZE_X, MAP_SIZE_Y),
                           facecolor=xx_mycolor.Crandom())
    sca.mapping_set(ax, MAP_SIZE_X, MAP_SIZE_Y)

    # --- マップ生成 ---
    map = Map()
    maze = map.generate_map()
    # --- コスト図をログへ ---
    for m in maze:
        result.append(m)
    # --- エージェント初期配置 ---
    agents = []
    result.append(f"---------simulation:0------------")
    for i in range(AGENT_NUM):
        # --- 初期位置、目的の改札設定 ---
        rs = random.randint(0, len(start_list)-1)
        start_x, start_y = start_list[rs][0], start_list[rs][1]
        # --- 被ったら出てこない ---
        semai = False
        for agent in agents:
            if agent.position == (start_x, start_y):
                semai = True
                break
        if semai:
            continue
        agent = Agent(i, start_x, start_y, goal_list, maze)
        agents.append(agent)
        ax.scatter(agent.position[1], agent.position[0], c=agent.color)
        ax.text(agent.position[1], agent.position[0], agent.id)
        result.append(agent.info())
    # --- 障害物の初期配置 ---
    sca.scatman(ax, wall_list, goal_list, start_list, use_colors)

    def update(frame):
        nonlocal s  # シミュレーションカウント
        nonlocal sum_id
        global result
        result.append(f"---------simu: {s}------------")
        print("simu: ", s)
        # ------------------------------
        ax.set_title(f"simu: {s}")
        ax.clear()  # 前のフレームのエージェントをクリア
        sca.mapping_set(ax, MAP_SIZE_X, MAP_SIZE_Y)

        # こっから衝突回避
        for agent in agents:
            if agent.position == agent.goal:
                print("到着したお")
                agents.remove(agent)
                continue
            next_map = copy.deepcopy(maze)
            for other in agents:
                if agent.id == other.id:  # 違う人
                    continue
                elif len(other.path) < 1:
                    continue
                # --- スピード分動いた後のエージェントの位置にコスト設定 ---
                if len(other.path) > other.speed:
                    next_map[other.path[other.speed-1][0]
                             ][other.path[other.speed-1][1]] = object_cost
                else:  # 障害物回避してる人のコスト
                    next_map[other.path[0][0]][other.path[0][1]] = object_cost
            agent.path = astar(next_map, tuple(
                agent.position), tuple(agent.goal))
            if len(agent.path) > agent.speed-1:
                if next_map[agent.path[agent.speed-1][0]][agent.path[agent.speed-1][0]] == object_cost:
                    print(agent.id, "は衝突してる")
            if len(agent.path) < 2:
                print("pathの長さ0だよ")

        # --- エージェント位置更新 ---
        # ag.futureImpactError(agents)
        for agent in agents:
            # --- 到着処理 ---
            if agent.position == tuple(agent.goal):
                print("到着したお")
                agents.remove(agent)
                continue
            # ---------------
            agent.move()
            ax.scatter(agent.position[1], agent.position[0], c=agent.color)
            ax.text(agent.position[1], agent.position[0], agent.id)
            ax.set_title(f"シミュレーション: {s}")
            result.append(agent.info())

        # --- 新規エージェント ---
        for i in range(BORN_AGENT_NUM):
            if random.random() < BORN_INTERVAL:
                # --- 初期位置、目的の改札設定 ---
                rs = random.randint(0, len(start_list)-1)
                start_x, start_y = start_list[rs][0], start_list[rs][1]
                semai = False
                for agent in agents:
                    if agent.position == (start_x, start_y):
                        semai = True
                        break
                if semai:
                    continue
                agent = Agent(sum_id, start_x, start_y, goal_list, maze)
                agents.append(agent)
                ax.scatter(agent.position[1], agent.position[0])
                ax.text(agent.position[1], agent.position[0], agent.id)
                result.append(agent.info())
                sum_id += 1
        # --- 障害物の再配置 ---
        sca.scatman(ax, wall_list, goal_list, start_list, use_colors)
        # ------------
        s += 1

    ani = animation.FuncAnimation(
        fig, update, frames=SIMU_COUNT, interval=500, repeat=False)
    plt.show()
    # ani.save("xx.gif", writer="imagemagick")
    # --- 結果出力 ---
    with open("xxlog.txt", "w") as f:
        for line in result:
            print(line, file=f)

    # ---------------
if __name__ == "__main__":
    simulation(SIMU_COUNT)
