import matplotlib.pyplot as plt
import matplotlib.animation as animation
import japanize_matplotlib
import numpy as np
import pandas as pd
import random
import streamlit as st # 使いたい...
import math
import heapq
import datetime

SIMU_COUNT = 60 # シミュレーション回数
AGENT_NUM = 20 # エージェント数
MAP_SIZE_X = 40 # マップサイズ
MAP_SIZE_Y = 20
object_cost = 100 # 障害物のコスト
color_list = ["skyblue","DarkOliveGreen","HotPink","Indigo","DarkSlateBlue","CornflowerBlue","AntiqueWhite"]
start_list = []
goal_list = []
wall_list = [] # 障害物座標list
result = [] # 結果記録用

class Map():
    """ マップ作りまーす """
    def __init__(self, object_cost=object_cost):
        self.map = pd.read_excel('Map.xlsx', sheet_name=0)
        # self.map = self.map.T
        self.map = self.map.fillna(0) # NaNを0
        # --- Mapから各地点を取得しリストへ ---
        for y in range(MAP_SIZE_Y):
            for x in range(MAP_SIZE_X):
                if self.map.iat[y, x] == "s":
                    start_list.append([y, x])
                elif self.map.iat[y, x] == "g":
                    goal_list.append([y, x])
                elif self.map.iat[y, x] == "x":
                    wall_list.append([y, x])

        self.map = self.map.replace('x', object_cost) # 壁にコスト
        self.map = self.map.replace('s', -1) # マップにコスト
        self.map = self.map.replace('g', 1) # マップにコスト
    def generate_map(self):
        self.map = self.map.values.tolist() # dfをリスト変換
        return self.map

class Agent():
    """ エージェントクラス """
    def __init__(self, ID, init_x, init_y, goal_list, maze):
        self.id = ID
        self.position = [init_x, init_y]
        self.goal = goal_list[random.randint(0, len(goal_list)-1)] # 改札ランダム設定
        self.speed = 0.2
        self.path = self.calc_path(maze) # 経路list
    # --- 情報 ---
    def info(self):
        return  f"ID:{self.id}\n現在地:{self.position}\n改札:{self.goal}\n経路:{self.path}"
    
    # --- 経路探索 ---
    def calc_path(self, maze):
        return astar(maze, tuple(self.position), tuple(self.goal)) # タプルにしないと動かない

    # --- 移動 ---
    def move(self): # pathリスト順に位置を更新
        if self.path:
            next_position = self.path.pop(0)
            self.position = [next_position[0], next_position[1]]


class Node():
    def __init__(self, position, parent=None):
        self.position = position
        self.parent = parent
        self.g = 0 # スタートからの距離
        self.h = 0 # ヒューリスティック距離
        self.f = 0 # 総コスト
    # --- ノードの比較 ---
    def __lt__(self, other): # "less than"のlt
        return self.f < other.f
def heuristic(a, b):
    """
    a: 現在地, b: ゴール
    """ 
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def astar(maze, start, end): # A*
    open_list = [] # 探索中のノード？
    closed_list = set() # 見たノードたち
    start_node = Node(start) # スタートノード
    end_node = Node(end) # えんど
    heapq.heappush(open_list, start_node) # open_listにstart_nodeを追加
    # --- open_listをもれなく ---
    while open_list:
        current_node = heapq.heappop(open_list) # 最小値を取り出し消去
        closed_list.add(current_node.position) # 見たよん
        # --- 現在ノードがエンドノードならpathを作成 ---
        if current_node.position == end_node.position:
            path = []
            while current_node:
                path.append(current_node.position)
                current_node = current_node.parent
            return path[::-1]
        (x, y) = current_node.position
        neighbors = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
        for next_position in neighbors:
            if (next_position[0] < 0 or next_position[0] >= len(maze) or # 迷路の左右に飛び出る
                next_position[1] < 0 or next_position[1] >= len(maze[0]) or # 迷路の上に飛ぶ、下に埋められる
                maze[next_position[0]][next_position[1]] == object_cost or # 壁に当たる
                next_position in closed_list): # 既に見た
                continue # 次のループ
            # --- お隣ノード作成、親は現在ノード ---
            neighbor = Node(next_position, current_node)
            neighbor.g = current_node.g + 1
            neighbor.h = heuristic(neighbor.position, end_node.position)
            neighbor.f = neighbor.g + neighbor.h
            if add_to_open(open_list, neighbor):
                heapq.heappush(open_list, neighbor) # open_listにneighborを追加
    return None
# --- bool返すんだ ---
def add_to_open(open_list, neighbor):
    for node in open_list:
        # お隣が探索中の中にある & gが大きい
        if neighbor.position == node.position and neighbor.g >= node.g:
            return False
    return True
### --------------------------- ###
# シミュ
def simulation(SIMU_COUNT):
    s = 0 # シミュレーションカウント用
    result.append(f"最終更新: {datetime.datetime.now()}")
    # --- プロット設定 ---
    fig, ax = plt.subplots(figsize=(MAP_SIZE_X, MAP_SIZE_Y), facecolor=color_list[random.randint(0,len(color_list)-1)])
    ax.set_xlim(-0.5, MAP_SIZE_X-1)
    ax.set_ylim(-0.5, MAP_SIZE_Y-0.5)
    ax.set_xticks(np.arange(0.5, MAP_SIZE_X-0.5, 1))
    ax.set_yticks(np.arange(0.5, MAP_SIZE_Y-0.5, 1))
    ax.axes.xaxis.set_ticklabels([])
    ax.axes.yaxis.set_ticklabels([])
    ax.axes.invert_yaxis() # y軸の反転
    ax.grid(True)
    
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
        agent = Agent(i, start_x, start_y, goal_list, maze)
        agents.append(agent)
        ax.scatter(agent.position[1], agent.position[0])
        result.append(agent.info())

    # --- 障害物の初期配置 ---
    for w in wall_list:
        ax.scatter(w[1], w[0], marker="x", color=color_list[1])
    for g in goal_list:
        ax.scatter(g[1], g[0], marker="*")
    for l in start_list:
        ax.scatter(l[1], l[0], s=200, marker=",", color=color_list[0])

    def update(frame):
        nonlocal s # シミュレーションカウント
        s += 1
        global result
        result.append(f"---------simulation:{s}------------")
        # ------------------------------
        ax.set_title(f"simulation: {s}")
        ax.clear() # 前のフレームのエージェントをクリア
        ax.set_xlim(-0.5, MAP_SIZE_X-0.5)
        ax.set_ylim(-0.5, MAP_SIZE_Y-0.5)
        ax.set_xticks(np.arange(0.5, MAP_SIZE_X-0.5, 1))
        ax.set_yticks(np.arange(0.5, MAP_SIZE_Y-0.5, 1))
        ax.axes.xaxis.set_ticklabels([])
        ax.axes.yaxis.set_ticklabels([])
        ax.axes.invert_yaxis() # y軸の反転
        ax.grid(True)

        # 0712 こっから衝突回避
        
        burst = []
        for id, agent in enumerate(agents):
            for id_2 ,agent_2 in enumerate(agents):
                if len(agent.path)<2 or len(agent_2.path)<2:
                    continue
                if id!=id_2 and agent.path[1]==agent_2.path[1]: # 異なるidで次の場所が同じ
                    agent.path = agent.calc_path(maze)

        # --- エージェント位置更新 ---
        for agent in agents:
            # agent.path = agent.calc_path(maze) # 経路再計算
            agent.move()
            ax.scatter(agent.position[1], agent.position[0])
            ax.set_title(f"シミュレーション: {s}")
            result.append(agent.info())
        # --- 障害物の再配置 ---
        for w in wall_list:
            ax.scatter(w[1], w[0], marker="x", color=color_list[1])
        for g in goal_list:
            ax.scatter(g[1], g[0], marker="*")
        for l in start_list:
            ax.scatter(l[1], l[0], s=200, marker=",", color=color_list[0])   
        # ------------

    ani = animation.FuncAnimation(fig, update, frames=SIMU_COUNT, interval=100, repeat=False)
    plt.show()
    # ani.save("xx.gif", writer="imagemagick")
    # --- 結果出力 ---
    with open("xxlog.txt", "w") as f:
        for line in result:
            print(line, file=f)
    # ---------------

if __name__ == "__main__":
    simulation(SIMU_COUNT)
    