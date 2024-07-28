import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.cm as cm # カラーマップ
import japanize_matplotlib
import numpy as np
import pandas as pd
import random
import heapq
import datetime
import xx_agents as ag
import xx_mycolor # マイカラー
import xx_scattering as sca

SIMU_COUNT = 200 # シミュレーション回数
AGENT_NUM = 10 # 初期エージェント数
BORN_AGENT_NUM = 5 # 新規エージェント数
BORN_INTERVAL = 0.4 # エージェント生成間隔
MAP_SIZE_X = 80 # マップサイズ
MAP_SIZE_Y = 40
SPEED = 3 # エージェント最大速度
object_cost = 100 # 障害物のコスト
color_list = xx_mycolor.color_list
start_list = []
goal_list = []
wall_list = [] # 障害物座標list
result = [] # 結果記録用
use_colors = xx_mycolor.CrandomList(3)

class Map():
    """ マップ作りまーす """
    def __init__(self, object_cost=object_cost):
        self.map = pd.read_excel('Map.xlsx', sheet_name=2)
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
        self.r = random.randint(0, len(goal_list)-1)
        self.goal = goal_list[self.r] # 改札ランダム設定
        self.speed = SPEED
        self.path = astar(maze, tuple(self.position), tuple(self.goal)) 
        ## --- color設定 ---
        if self.r == 0:
            self.color = "red"
        elif self.r == 1:
            self.color = "blue"
        elif self.r == 2:
            self.color = "green"
        else:
            self.color = "black"
        # self.color = cm.Spectral(float(self.id)/50.0) # カラーマップ指定

        # if self.id%10==0:
        #     self.color = "red"
        # elif self.id%13==0:
        #     self.color = "blue"
        # else:
        #     self.color = "black"
        ## ------------------
    # --- 情報 ---
    def info(self):
        return  f"ID:{self.id}\n現在地:{self.position}\n改札:{self.goal}\n経路:{self.path}"
    
    # --- 経路探索 ---
    def calc_path(self, maze):
        return astar(maze, tuple(self.position), tuple(self.goal)) # タプルにしないと動かない

    # --- 移動 ---
    def move(self): # pathリスト順に位置を更新
        # if self.path:
        #     next_position = self.path.pop(0)
        #     self.position = [next_position[0], next_position[1]]
        if len(self.path)>self.speed-1:
            for _ in range(self.speed):
                next_position = self.path.pop(0)
                self.position = [next_position[0], next_position[1]]
        else: # ゴール
            self.position = self.path[-1]


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
    open_list = [] # 探索中のノード
    closed_list = set() # 見たノードたち
    start_node = Node(start) # スタートノード
    end_node = Node(end) # えんど
    heapq.heappush(open_list, start_node) # open_listにstart_nodeを追加
    # --- open_listをもれなく ---
    while open_list:
        current_node = heapq.heappop(open_list) # 最小値を取り出し消去
        closed_list.add(current_node.position) # 見たよ
        # --- 現在ノードがエンドノードならpathを作成 ---
        if current_node.position == end_node.position:
            path = []
            while current_node:
                path.append(current_node.position)
                current_node = current_node.parent
            return path[::-1]
        (x, y) = current_node.position
        neighbors = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1), (x+1, y+1), (x+1, y-1), (x-1, y+1), (x-1, y-1)]
        for index, next_position in enumerate(neighbors):
            if (next_position[0] < 0 or next_position[0] >= len(maze) or # 迷路の左右に飛び出る
                next_position[1] < 0 or next_position[1] >= len(maze[0]) or # 迷路の上に飛ぶ、下に埋められる
                maze[next_position[0]][next_position[1]] == object_cost or # 壁に当たる
                next_position in closed_list): # 既に見た
                continue # 次のループ
            # --- お隣ノード作成、親は現在ノード ---
            neighbor = Node(next_position, current_node)
            if index<4:
                neighbor.g = current_node.g + 1
            else:
                neighbor.g = current_node.g + 1.414
                neighbor.h = heuristic(neighbor.position, end_node.position)
                neighbor.f = neighbor.g + neighbor.h
            if add_to_open(open_list, neighbor):
                heapq.heappush(open_list, neighbor) # open_listにneighborを追加
    return [start] # 変更した

def add_to_open(open_list, neighbor):
    for node in open_list:
        # お隣が探索中の中にある & gが大きい
        if neighbor.position == node.position and neighbor.g >= node.g:
            return False
    return True
# シミュ
def simulation(SIMU_COUNT):
    s = 0 # シミュレーションカウント用
    sum_id = AGENT_NUM # id合計
    result.append(f"最終更新: {datetime.datetime.now()}")
    # --- プロット設定 ---
    # fig, ax = plt.subplots(figsize=(MAP_SIZE_X, MAP_SIZE_Y), facecolor=color_list[random.randint(0,len(color_list)-1)])
    fig, ax = plt.subplots(figsize=(MAP_SIZE_X, MAP_SIZE_Y), facecolor=xx_mycolor.Crandom())
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
        agent = Agent(i, start_x, start_y, goal_list, maze)
        agents.append(agent)
        ax.scatter(agent.position[1], agent.position[0], c=agent.color)
        ax.text(agent.position[1], agent.position[0], agent.id)
        result.append(agent.info())
    # --- 障害物の初期配置 ---
    sca.scatman(ax, wall_list, goal_list, start_list, use_colors)

    def update(frame):
        nonlocal s # シミュレーションカウント
        nonlocal sum_id
        s += 1
        global result
        result.append(f"---------simu: {s}------------")
        print("simu: ",s)
        # ------------------------------
        ax.set_title(f"simu: {s}")
        ax.clear() # 前のフレームのエージェントをクリア
        sca.mapping_set(ax, MAP_SIZE_X, MAP_SIZE_Y)

        # こっから衝突回避
        ag.futureImpactError(agents)
        for agent in agents:
            avoid = False
            if not agent.path: # パスない場合次のエージェントへ
                continue
            (x, y) = agent.position
            back_posi  = (x - (agent.path[0][0]-agent.position[0]), y - (agent.path[0][1]-agent.position[1]))
            neighbors = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1), (x+1, y+1), (x+1, y-1), (x-1, y+1), (x-1, y-1)]
            if back_posi in neighbors:
                neighbors.remove(back_posi) # 後方の選択肢を除外
            for agent_2 in agents:
                if not agent_2.path:
                    continue
                if agent.id!=agent_2.id and agent.path[0]==agent_2.path[0]: # 異なるidで次の場所が同じ
                    # print(f"シミュレーション{s}の{agent.id}と{agent_2.id}が{(x, y)}で衝突の危機")
                    neighbors = [pos for pos in neighbors if pos != agent.path[0]] # 予定パスを除く
                    avoid = True
            if not avoid:
                continue
            # --- 移動範囲の制限 ---
            can_neighbors = [
                pos for pos in neighbors # neighborsの中から
                if maze[pos[0]][pos[1]] != object_cost and # 壁でもない
                not any(pos == a.position for a in agents) and# 他のエージェントがいない場所をピック
                not any(pos == a.path[0] for a in agents if len(a.path)>0)
            ]        
            if can_neighbors:
                new_position = can_neighbors[random.randint(0,len(can_neighbors)-1)] # neighborsからランダムに移動
                agent.path = astar(maze, new_position, tuple(agent.goal))
                # agent.path = agent.calc_path(maze)
            else: # 動ける場所がない場合、停止
                agent.path.insert(0, agent.position)
          
        # --- エージェント位置更新 ---
        
        for agent in agents:
            # --- ゴール済みエージェントの削除 ---
            if agent.position==agent.goal:
                agents.remove(agent)
                continue
            
            if len(agent.path) < 1:
                agents.remove(agent)
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
                agent = Agent(sum_id, start_x, start_y, goal_list, maze)
                agents.append(agent)
                ax.scatter(agent.position[1], agent.position[0])
                ax.text(agent.position[1], agent.position[0], agent.id)
                result.append(agent.info())
                sum_id+=1
        # --- 障害物の再配置 ---
        sca.scatman(ax, wall_list, goal_list, start_list, use_colors)
        # ------------

    ani = animation.FuncAnimation(fig, update, frames=SIMU_COUNT, interval=500, repeat=False)
    plt.show()
    # ani.save("xx.gif", writer="imagemagick")
    # --- 結果出力 ---
    with open("xxlog.txt", "w") as f:
        for line in result:
            print(line, file=f)
    # ---------------
if __name__ == "__main__":
    simulation(SIMU_COUNT)
    