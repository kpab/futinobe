import matplotlib.pyplot as plt
from matplotlib import patches
import numpy as np
import random

SIMU_COUNT = 50 # シミュレーション回数
AGENT_NUM = 20 # エージェント数
MAP_SIZE_X = 20 # マップサイズ
MAP_SIZE_Y = 10

class Agent():
    def __init__(self, ID, init_x, init_y, goal):
        self.id = ID
        self.position = [init_x, init_y]
        self.goal = goal

def simulation(SIMU_COUNT):
    """
    シミュレーションの実行
    """
    start_list = [[5, 3], [18, 7], [14, 2]] # エージェント初期位置リスト
    goal_list_x = [0.5, 0.5, 0.5, 0.5] # 改札座標x
    goal_list_y = [5, 6, 7, 8] # 改札座標y
    wall = patches.Rectangle( xy=(0,0) , width=5, height=4, color="grey", alpha=0.5) # 壁の配置
    wall2 = patches.Rectangle( xy=(14,0) , width=5, height=4, color="grey", alpha=0.5) # 壁の配置

    agents = []
    # --- プロット ---
    fig, ax = plt.subplots(figsize=(MAP_SIZE_X, MAP_SIZE_Y), facecolor="skyblue")
    ax.set_xlim(0, MAP_SIZE_X-1)
    ax.set_ylim(0, MAP_SIZE_Y-1)
    
    # --- エージェント初期配置 ---
    for i in range(AGENT_NUM):
        # --- 初期位置、目的の改札設定 ---
        rs = random.randint(0, 2)
        start_x, start_y = start_list[rs][0], start_list[rs][1]
        rg = random.randint(0, 3)
        goal = [goal_list_x[rg], goal_list_y[rg]]
        
        agent = Agent(i, start_x, start_y, goal)
        agents.append(agent)
        ax.scatter(agent.position[0], agent.position[1])

    ax.scatter(goal_list_x, goal_list_y) # 改札の配置
    ax.add_patch(wall)
    ax.add_patch(wall2)
    plt.show()

    for _ in range(SIMU_COUNT):
        for agent in agents:
            
            return


if __name__ == "__main__":
    simulation(SIMU_COUNT)
