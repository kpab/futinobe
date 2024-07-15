import matplotlib.pyplot as plt
from matplotlib import patches
import matplotlib.animation as animation
import numpy as np
import random
import streamlit as st # 使いたい...
import math

SIMU_COUNT = 50 # シミュレーション回数
AGENT_NUM = 10 # エージェント数
MAP_SIZE_X = 20 # マップサイズ
MAP_SIZE_Y = 10 
object_cost = 100 # 障害物のコスト
wall_list = []

class Map():
    """ マップ作りまーす """
    def __init__(self, map_size=(MAP_SIZE_X, MAP_SIZE_Y)):
        self.map_size = map_size
        self.map = [[0] * self.map_size[0] for i in range(self.map_size[1])] # マップの初期化
    ## -- マップ生成 --
    def generate_map(self, wall_list, start, goal):
        # --- 境界設定 ---
        for i in range(self.map_size[1]): ## 上下の壁ガコン
            self.map[0][i] = object_cost
            self.map[self.map_size[0] - 1][i] = object_cost
        for j in range(self.map_size[0]): ## 左右の壁ガコン
            self.map[j][0] = object_cost
            self.map[j][self.map_size[1] - 1] = object_cost
        # --- 壁の配置 ---
        if wall_list:
            for wall in wall_list:
                self.map[wall[0],wall[1]] = object_cost
        # --- 初期位置&改札 ---
        self.start = start
        self.goal = goal
        self.map[start.x][start.y] = -1
        self.map[goal.x][goal.y] = 1
        self.goal.now_cost(self.goal) # ゴールの初期コスト
        self.start.now_cost(self.goal) # 初期位置の初期コスト/Hの計算に必要?
        return self.map, self.start, self.goal
    

class Agent():
    """ エージェントクラス """
    def __init__(self, ID, init_x, init_y, goal_list):
        self.id = ID
        self.position = [init_x, init_y]
        self.goal = goal_list[random.randint(0, 3)] # 改札ランダム設定
        self.speed = 0.2
    # --- 情報 ---
    def info(self):
        print(f"ID:{self.id}\n現在地:{self.position}\n改札:{self.goal}")
    # --- 現在コストの計算 ---
    def now_cost(self, goal):
        return
    # --- 移動 ---
    def move(self): ### 適当に移動作る/今後修正
        dist_x = self.goal[0] - self.position[0]
        dist_y = self.goal[1] - self.position[1]
        dist = math.sqrt(dist_x**2 + dist_y**2) # 距離計算
        if dist>0:
            move_x = dist_x / dist * self.speed
            move_y = dist_y / dist * self.speed
            self.position[0] += move_x
            self.position[1] += move_y



def simulation(SIMU_COUNT):
    """
    シミュレーションの実行
    """
    start_list = [[5.0, 3.0], [18.0, 7.0], [14.0, 2.0]] # エージェント初期位置リスト
    goal_list = [[0.5, 5.0], [0.5, 6.0], [0.5, 7.0], [0.5, 8.0]] # 改札座標リスト

    # --- プロット設定 ---
    color_list = ["skyblue","DarkOliveGreen","HotPink","Indigo","DarkSlateBlue","CornflowerBlue","AntiqueWhite"]
    fig, ax = plt.subplots(figsize=(MAP_SIZE_X, MAP_SIZE_Y), facecolor=color_list[random.randint(0,len(color_list)-1)])
    ax.set_xlim(0, MAP_SIZE_X-1)
    ax.set_ylim(0, MAP_SIZE_Y-1)
    
    agents = []
    ims = [] # アニメーション用
    # --- エージェント初期配置 ---
    for i in range(AGENT_NUM):
        # --- 初期位置、目的の改札設定 ---
        rs = random.randint(0, 2)
        start_x, start_y = start_list[rs][0], start_list[rs][1]

        agent = Agent(i, start_x, start_y, goal_list)
        agents.append(agent)
        # im = ax.scatter(agent.position[0], agent.position[1])
        # ims.append(im)
        ax.scatter(agent.position[0], agent.position[1])
    # --- 障害物配置 ---
    wall = patches.Rectangle( xy=(0,0) , width=5, height=4, color="grey", alpha=0.5) # 壁の配置
    wall2 = patches.Rectangle( xy=(14,0) , width=5, height=4, color="grey", alpha=0.5) # 壁の配置
    ax.add_patch(wall)
    ax.add_patch(wall2)
    for i in range(4): # 改札の表示
        r = patches.Rectangle( xy=goal_list[i],width=1, height=0.5,color='b')
        ax.add_patch(r)

    agent_pos = [] # 確認用^_^
    for s in range(SIMU_COUNT):
        print("------------------------")
        for agent in agents:
            agent.move()
            ax.scatter(agent.position[0], agent.position[1])
            # im = ax.scatter(agent.position[0], agent.position[1])
            # ims.append(im)
            print(f"id:{agent.id}\npos:{agent.position}")
        ax.set_title(f"simu:{s}")
        plt.pause(0.5)
    plt.show()
    # ani = animation.ArtistAnimation(fig, ims, interval=1, repeat_delay=1000)
    # plt.show()
        


if __name__ == "__main__":
    simulation(SIMU_COUNT)
    
