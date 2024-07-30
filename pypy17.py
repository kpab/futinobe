"""
+ Boids
"""
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
BORN_AGENT_NUM = 10 # 新規エージェント数
BORN_INTERVAL = 0.8 # エージェント生成間隔
MAP_SIZE_X = 80 # マップサイズ
MAP_SIZE_Y = 40
SPEED = 2 # エージェント最大速度
RANGE_Separate = 1#分離ルールの範囲
RANGE_Alignment = 5#整列ルールの範囲
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
        # for m in self.map:
        #     print(m)
        return self.map

class Agent():
    """ エージェントクラス """
    def __init__(self, ID, init_x, init_y, goal_list, maze):
        self.id = ID
        self.position = [init_x, init_y]
        self.r = random.randint(0, len(goal_list)-1)
        self.goal = goal_list[self.r] # 改札ランダム設定
        self.speed = np.random.uniform(-SPEED,SPEED,2)

        ## --- color設定 ---
        if self.r == 0:
            self.color = "red"
        elif self.r == 1:
            self.color = "blue"
        elif self.r == 2:
            self.color = "green"
        else:
            self.color = "black"


class Boids():
    def __init__(self, agents):
        self.agents = []
        for agent in agents:
            for i in range(len(goal_list)):
                if agent.r == i:
                    self.agents += [{'p':agent.position, 'v':agent.speed, 'r':agent.goal}]
        self.dist = np.zeros([len(agents), len(agents)])
        self.goal_reach = np.zeros([len(agents), len(agents)])
    # 距離計算
    def distance(self, agents):
        for i in range(len(agents)):
            for j in range(len(agents)):
                d = np.array(self.agents[i]['p']) - np.array(self.agents[j]['p'])
                self.dist[i][j] = np.linalg.norm(d)
    # 距離計算ゴールまで
    def distance(self, agents):
        for i in range(len(agents)):
            d = np.array(self.agents[i]['p']) - np.array(self.agents[i]['r'])
            self.goal_reach = np.linalg.norm(d)
    # 分離ルール
    def ruleSeparate(self, n):
        a = np.array(np.where((self.dist[n] < RANGE_Separate) & (self.dist[n] > 0)), dtype=int)[0]
        v = np.zeros(2)
        cnt = 0
        for i in a:
            if i != n:
                d = np.array(self.agents[n]['p']) - np.array(self.agents[i]['p'])
                if self.dist[n][i] != 0:
                    v += d / self.dist[n][i]**2
                    cnt += 1
        if cnt == 0:
            return np.zeros(2)  # 無効な値を返さないようにする
        return v / cnt
    # 整列ルール
    def ruleAlignment(self, n):
        a = np.array(np.where((self.dist[n] < RANGE_Alignment) & (self.dist[n] > 0)), dtype=int)[0]
        v = np.zeros(2)
        cnt = 0
        for i in a:
            v -= self.agents[n]['v'] - self.agents[i]['v']
            cnt += 1
        if cnt == 0:
            return np.zeros(2)  # 無効な値を返さないようにする
        return v / cnt
    #結合ルール
    def ruleCohesion(self, n, agents):
        p = np.zeros(2)
        cnt = 0
        for i in range(len(agents)):
            if self.dist[n][i] != 0:  # 距離がゼロでない場合のみ計算
                p -= np.array(self.agents[n]['p']) - np.array(self.agents[i]['p'])
                cnt += 1
        if cnt == 0:
            return 0
        return p / cnt
    # 目的地ルール
    def ruleMokuteki(self, n, agents):
        p = np.zeros(2)
        cnt = 0
        for i in range(len(agents)):
            # エージェント n からエージェント i の距離を使う代わりに目的地までの距離を使う
            if np.linalg.norm(np.array(self.agents[n]['p']) - np.array(self.agents[n]['r'])) > 0:  # 距離がゼロでない場合のみ計算
                direction = np.array(self.agents[n]['r']) - np.array(self.agents[n]['p'])
                p += direction / np.linalg.norm(direction)  # 方向を正規化して加算
                cnt += 1
        if cnt == 0:
            return np.zeros(2)  # 無効な値を返さないようにする
        return p / cnt  # 全エージェントの目的地に対する加重平均方向
     #シミュレーション
    def simulation(self, agents):
        self.distance(agents)
        vel_tmp = []
        for i in range(len(agents)):
            vel = [self.ruleSeparate(i)*0.5 + self.ruleAlignment(i)*0.3 + self.ruleCohesion(i, agents)*0.2 + self.ruleMokuteki(i,agents)*0.3]
            if not np.isnan(vel).any():  # NaNが含まれる速度を除外
                vel_tmp.append(vel)
            else:
                vel_tmp.append(np.zeros(2))  # 無効な速度をゼロに設定
        for i in range(len(agents)):
            self.agents[i]['v'] += vel_tmp[i]
            v = np.linalg.norm(self.agents[i]['v'])
            if v>SPEED:
                self.agents[i]['v'] = self.agents[i]['v']/v*SPEED
            elif v<SPEED/2:
                self.agents[i]['v'] = self.agents[i]['v']/v*SPEED/2

        for i in range(len(agents)):
            # --- 境界条件 ---
            if(abs((self.agents[i]['p']+self.agents[i]['v'])[0]) > MAP_SIZE_X):
                self.agents[i]['v'][0] = -self.agents[i]['v'][0]
            if(abs((self.agents[i]['p']+self.agents[i]['v'])[1]) > MAP_SIZE_Y):
                self.agents[i]['v'][1] = -self.agents[i]['v'][1]
            # --- 壁 ---
            if [int(abs((self.agents[i]['p']+self.agents[i]['v'])[0])), int(abs((self.agents[i]['p']+self.agents[i]['v'])[1]))] in wall_list:
                self.agents[i]['v'][0] = -self.agents[i]['v'][0]
                self.agents[i]['v'][1] = -self.agents[i]['v'][1]
            self.agents[i]['p'] += self.agents[i]['v']
       

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
    # --- 障害物の初期配置 ---
    sca.scatman(ax, wall_list, goal_list, start_list, use_colors)
    B = Boids(agents)

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

          
        # --- エージェント位置更新 ---
        B.simulation(agents)
        for i, agent in enumerate(agents):
            agent.position = B.agents[i]['p']
            print(agent.position)
            # --- ゴール済みエージェントの削除 ---
            # if agent.position==agent.goal:
            if np.array_equal(agent.position, agent.goal):
                agents.remove(agent)
                continue
            ax.scatter(agent.position[1], agent.position[0], c=agent.color)
            ax.text(agent.position[1], agent.position[0], agent.id)
            ax.set_title(f"シミュレーション: {s}")
          
        # --- 新規エージェント ---
        # for i in range(BORN_AGENT_NUM):
        #     if random.random() < BORN_INTERVAL:
        #         # --- 初期位置、目的の改札設定 ---
        #         rs = random.randint(0, len(start_list)-1)
        #         start_x, start_y = start_list[rs][0], start_list[rs][1]
        #         agent = Agent(sum_id, start_x, start_y, goal_list, maze)
        #         agents.append(agent)
        #         ax.scatter(agent.position[1], agent.position[0])
        #         ax.text(agent.position[1], agent.position[0], agent.id)
        #         sum_id+=1
        # --- 障害物の再配置 ---
        sca.scatman(ax, wall_list, goal_list, start_list, use_colors)
        # ------------
        

    ani = animation.FuncAnimation(fig, update, frames=SIMU_COUNT, interval=500, repeat=False)
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
    