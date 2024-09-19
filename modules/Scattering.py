import matplotlib.pyplot as plt
import numpy as np


# プロットベース
def mapping_set(ax, map_size_x, map_size_y):
    ax.set_xlim(-0.5, map_size_x-0.5)
    ax.set_ylim(-0.5, map_size_y-0.5)
    ax.set_xticks(np.arange(0.5, map_size_x-0.5, 1))
    ax.set_yticks(np.arange(0.5, map_size_y-0.5, 1))
    ax.axes.xaxis.set_ticklabels([])
    ax.axes.yaxis.set_ticklabels([])
    ax.axes.invert_yaxis()  # y軸の反転
    ax.grid(True)


# 壁, ゴール, スタートの描画
def scatman(ax, wall_list, goal_list, start_list, use_colors):
    for w in wall_list:
        ax.scatter(w[1], w[0], marker="x", c=use_colors[0])
    for g in goal_list:
        ax.scatter(g[1], g[0], s=150, marker="*", c=use_colors[1])
    for l in start_list:
        ax.scatter(l[1], l[0], s=150, marker=",", c=use_colors[2])


# 壁, ゴール, スタートの描画ver.2
def scatman_v2(ax, wall_list, goal_list, goal_list_2, start_list, start_list_2, mix_list):
    for w in wall_list:
        ax.scatter(w[1], w[0], marker="x", c="green")
    for g in goal_list:
        ax.scatter(g[1], g[0], s=100, marker="*", c="red")
    for g in goal_list_2:
        ax.scatter(g[1], g[0], s=100, marker="*", c="blue")
    for l in start_list:
        ax.scatter(l[1], l[0], s=100, marker=",", c="red")
    for l in start_list_2:
        ax.scatter(l[1], l[0], s=100, marker=",", c="blue")
    for m in mix_list:
        ax.scatter(m[1], m[0], s=60, marker="$❤️$", c="red")
