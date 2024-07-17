import matplotlib.pyplot as plt
import xx_mycolor # マイカラー


# 壁, ゴール, スタートの描画
def scatman(ax, wall_list, goal_list, start_list, color_1, color_2):
    for w in wall_list:
        ax.scatter(w[1], w[0], marker="x", c=color_1)
    for g in goal_list:
        ax.scatter(g[1], g[0], marker="*")
    for l in start_list:
        ax.scatter(l[1], l[0], s=200, marker=",", c=color_2)
