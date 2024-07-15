import matplotlib.pyplot as plt
from matplotlib import patches
import matplotlib.animation as animation
import numpy as np
import random
import streamlit as st # 使いたい...
import math
import heapq
import datetime

SIMU_COUNT = 15 # シミュレーション回数
AGENT_NUM = 20 # エージェント数
MAP_SIZE_X = 20 # マップサイズ
MAP_SIZE_Y = 10 
object_cost = 100 # 障害物のコスト
color_list = ["skyblue","DarkOliveGreen","HotPink","Indigo","DarkSlateBlue","CornflowerBlue","AntiqueWhite"]
wall_list = [] # 障害物座標list
result = [] # 結果記録用

class Map():
    """ マップ作りまーす """
    def __init__(self, map_size=(MAP_SIZE_X, MAP_SIZE_Y)):
        self.map_size = map_size
        self.map = [[0] * self.map_size[0] for _ in range(self.map_size[1])]  # マップの初期化
    ## -- マップ生成 --
    def generate_map(self, wall_list, start_list, goal_list):
        # --- 境界設定 ---
        # print("map_size", self.map_size)
        # print("map[0]", self.map[0])
        for i in range(self.map_size[1]): ## 左右の壁ガコン
            # print(i)
            self.map[i][0] = object_cost
            self.map[i][self.map_size[0] - 1] = object_cost
        for j in range(self.map_size[0]): ## 上下の壁ガコン
            self.map[0][j] = object_cost
            self.map[self.map_size[1] - 1][j] = object_cost
        # --- 壁の配置 ---
        if wall_list:
            for wall in wall_list:
                # print(f"this wall: {wall}")
                self.map[wall[1]][wall[0]] = object_cost
        # --- 初期位置&改札 ---
        # self.start = start
        # self.goal = goal
        print(start_list)
        for s in start_list:
            print(s)
            self.map[s[1]][s[0]] = -1
        for g in goal_list:
            self.map[g[1]][g[0]] = 1
        return self.map
    

class Agent():
    """ エージェントクラス """
    def __init__(self, ID, init_x, init_y, goal_list, maze):
        self.id = ID
        self.position = [init_x, init_y]
        self.goal = goal_list[random.randint(0, 3)] # 改札ランダム設定
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


### ----- 貰ったゾーン ----- ###
class Node():
    """
    ノードクラス、貰ったやつ
    """
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
    open_list = []
    closed_list = set()
    start_node = Node(start)
    end_node = Node(end)
    heapq.heappush(open_list, start_node) # open_listにstart_nodeを追加
    while open_list:
        current_node = heapq.heappop(open_list) # 最小値を取り出し消去
        closed_list.add(current_node.position)
        if current_node.position == end_node.position:
            path = []
            while current_node:
                path.append(current_node.position)
                current_node = current_node.parent
            return path[::-1]
        (x, y) = current_node.position
        neighbors = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
        for next_position in neighbors:
            if (next_position[0] < 0 or next_position[0] >= len(maze) or
                next_position[1] < 0 or next_position[1] >= len(maze[0]) or
                maze[next_position[0]][next_position[1]] == object_cost or
                next_position in closed_list):
                continue
            neighbor = Node(next_position, current_node)
            neighbor.g = current_node.g + 1
            neighbor.h = heuristic(neighbor.position, end_node.position)
            neighbor.f = neighbor.g + neighbor.h
            if add_to_open(open_list, neighbor):
                heapq.heappush(open_list, neighbor)
    return None

def add_to_open(open_list, neighbor):
    for node in open_list:
        if neighbor.position == node.position and neighbor.g >= node.g:
            return False
    return True
### --------------------------- ###

def wall_building(): # 壁
    """
    wall_list: A*で重みをつける壁の位置座標リスト
    wall_img_list: patchesで塗りつぶす壁のリスト
    """
    wall_list = [(x, y) for x in range(0, 5) for y in range(0, 5)] + [(x, y) for x in range(14, 19) for y in range(0, 4)]
    wall_img_list = [(x, y) for x in range(0, 4) for y in range(0, 4)] + [(x, y) for x in range(13, 18) for y in range(0, 3)]

    # --- A*テスト用 ---
    wall_list.extend([(4,5),(5,5),(6,5)])
    wall_img_list.extend([(4,3),(4,4),(4,5)])

    return wall_list, wall_img_list

def simulation(SIMU_COUNT):
    """
    シミュレーションの実行
    """
    s = 0 # シミュレーションカウント用
    result.append(f"最終更新: {datetime.datetime.now()}")
    start_list = [[5, 3], [18, 7], [14, 2]] # エージェント初期位置リスト
    goal_list = [[1, 5], [1, 6], [1, 7], [1, 8]] # 改札座標リスト
    wall_c = color_list[random.randint(0,len(color_list)-1)]

    # --- プロット設定 ---
    fig, ax = plt.subplots(figsize=(MAP_SIZE_X, MAP_SIZE_Y), facecolor=color_list[random.randint(0,len(color_list)-1)])
    ax.set_xlim(0, MAP_SIZE_X-1)
    ax.set_ylim(0, MAP_SIZE_Y-1)
    
    # --- マップ生成 ---
    map = Map((MAP_SIZE_X, MAP_SIZE_Y))
    wall_list, wall_img_list = wall_building()

    print(wall_list)
    maze = map.generate_map(wall_list, start_list, goal_list)

    for m in maze:
        result.append(m)
    
    # --- エージェント初期配置 ---
    agents = []
    result.append(f"---------simulation:0------------")
    for i in range(AGENT_NUM):
        # --- 初期位置、目的の改札設定 ---
        rs = random.randint(0, 2)
        start_x, start_y = start_list[rs][0], start_list[rs][1]

        agent = Agent(i, start_x, start_y, goal_list, maze)
        agents.append(agent)
        ax.scatter(agent.position[0], agent.position[1])
        result.append(agent.info())
    
    wall_list, wall_img_list = wall_building()
    for i in range(len(wall_img_list)):
        w = patches.Rectangle( xy=wall_img_list[i] , fill=True,width=1, height=1,color=wall_c, alpha=random.uniform(0.3,0.4))
        ax.add_patch(w)

    for i in range(4): # 改札の表示
        r = patches.Rectangle( xy=goal_list[i],width=1, height=0.5,color='gray')
        ax.add_patch(r)

    def update(frame):
        nonlocal s # シミュレーションカウント
        s += 1
        global result
        result.append(f"---------simulation:{s}------------")
        ax.set_title(f"simulation: {s}")
        ax.clear() # 前のフレームのエージェントをクリア
        ax.set_xlim(0, MAP_SIZE_X-1)
        ax.set_ylim(0, MAP_SIZE_Y-1)
        for agent in agents:
            agent.move()
            ax.scatter(agent.position[0], agent.position[1])
            ax.set_title(f"simulation: {s}")
            result.append(agent.info())
        # 障害物の再配置
        for i in range(len(wall_img_list)):
            w = patches.Rectangle( xy=wall_img_list[i] , fill=True, width=1, height=1,color=wall_c, alpha=random.uniform(0.3,0.4))
            ax.add_patch(w)

        for i in range(4): # 改札
            r = patches.Rectangle( xy=goal_list[i],width=1, height=0.5,color='gray')
            ax.add_patch(r)
        # ------------

    ani = animation.FuncAnimation(fig, update, frames=SIMU_COUNT, interval=800, repeat=False)
    plt.show()

    with open("xxlog.txt", "w") as f:
        for line in result:
            print(line, file=f)
    

if __name__ == "__main__":
    simulation(SIMU_COUNT)
    
