from collections import Counter
import copy


# --- 全エージェントの次の場所リストを返す ---
def futurePrediction(agents):
    next_agent_positions = {}
    for agent in agents:
        if len(agent.path) > 0:
            next_agent_positions[agent.id] = tuple(agent.path[0])  # タプルに変換
    return next_agent_positions


# --- 次のフレームで衝突が発生する場合、その位置とidを出力 ---
# speedが無い場合(エージェントが次のパスに進む場合)、有効
def futureImpactError(agents):
    next_agent_positions = futurePrediction(agents)

    # 次の位置とそのIDをリストに変換
    next_positions = list(next_agent_positions.values())
    next_ids = list(next_agent_positions.keys())

    # 次の位置をタプルに変換し、重複をカウント
    impact_positions = [
        pos for pos, count in Counter(next_positions).items() if count > 1
    ]
    # 衝突地点がkey, idがvalue
    impacts = {}
    for pos in impact_positions:
        impact_agents = [next_ids[i]
                         for i, p in enumerate(next_positions) if p == pos]
        impacts[pos] = impact_agents

    # 衝突情報を表示
    for pos, ids in impacts.items():
        print(f"ID: {ids} が地点 {pos} で衝突")


# --- エージェントの現在地マップ ---
def agentNowMap(agents, maze):
    agent_map = copy.deepcopy(maze)
    for agent in agents:
        agent_map[agent.position[0]][agent.position[1]] = agent.id
    return agent_map


def agentNowPosiList(agents):
    now_agent_positions = {}
    for agent in agents:
        now_agent_positions[agent.id] = tuple(agent.position)  # タプルに変換
    return now_agent_positions


# --- エージェントいるところにコスト ---
def agentNextMap(agents, agent_id, object_cost, s, maze):
    """
    agents: エージェントクラスリスト
    s: スピード
    """
    agent_next_map = copy.deepcopy(maze)
    for agent in agents:
        if len(agent.path) < s+1:
            continue
        # --- 同じエージェントを除く ---
        if agent.id == agent_id:
            continue
        agent_next_map[agent.path[s][0]][agent.path[s][1]] = object_cost
    return agent_next_map


# neighbors取得
def getNeighbors(position, other_agents, maze, object_cost):
    (x, y) = position
    neighbors = [(x-1, y), (x+1, y), (x, y-1), (x, y+1),
                 (x+1, y+1), (x+1, y-1), (x-1, y+1), (x-1, y-1)]
    for index, next_position in enumerate(neighbors):
        if ((maze[next_position[0]][next_position[1]] == object_cost) or  # 回避先に壁 効いてない？
            next_position[0] < 0 or next_position[0] >= len(maze) or
            next_position[1] < 0 or next_position[1] >= len(maze[0])
            ):
            # neighbors.remove(next_position) # その回避地点を除外
            neighbors.pop(index)
            continue
        for other in other_agents:  # 人がいる場合も除外
            # if other.position[0] == next_position[0] and other.position[1]==next_position[1]:
            if other.position == next_position:
                # neighbors.remove(next_position)
                neighbors.pop(index)
                break
    # print(f"回避候補: {neighbors}")
    return neighbors


# エージェントの現在地の被りをチェック
def nowAgentImpactChk(agents, maze):
    agent_positions = agentNowPosiList(agents)
    # 次の位置とそのIDをリストに変換
    next_positions = list(agent_positions.values())
    next_ids = list(agent_positions.keys())

    # 次の位置をタプルに変換し、重複をカウント
    impact_positions = [
        pos for pos, count in Counter(next_positions).items() if count > 1
    ]
    # 衝突地点がkey, idがvalue
    impacts = {}
    for pos in impact_positions:
        impact_agents = [next_ids[i]
                         for i, p in enumerate(next_positions) if p == pos]
        impacts[pos] = impact_agents
    # 衝突情報を表示
    for pos, ids in impacts.items():
        print(f"ID: {ids} が地点 {pos} で衝突")


# 壁破壊チェック
def wallBreakerChk(agents, wall_list, maze, object_cost):
    for agent in agents:
        if list(agent.position) in wall_list:
            print(f"{agent.id}が壁に突っ込んだ")
        if maze[agent.position[0]][agent.position[1]] == object_cost:
            print(f"{agent.id}のいる場所コストあり")


# エージェント数カウントマップ
def agentCountMap(agents, maze):
    people_map = copy.deepcopy(maze)
    for y in range(len(people_map)):
        for x in range(len(people_map[0])):
            if people_map[y][x] != 0:
                people_map[y][x] = 0
    for agent in agents:
        people_map[agent.position[0]][agent.position[1]] += 1
    return people_map


# 現在スピードで移動した際の、エージェントカウントマップ
def agentNextCountMap(agents, maze):
    next_people_map = copy.deepcopy(maze)
    for y in range(len(next_people_map)):
        for x in range(len(next_people_map[0])):
            if next_people_map[y][x] != 0:
                next_people_map[y][x] = 0
    for agent in agents:
        if len(agent.path) < agent.speed:  # ゴールを除外
            pass
        else:
            next_people_map[agent.path[agent.speed-1][0]
                            ][agent.path[agent.speed-1][1]] += 1
    return next_people_map


# エージェントの衝突数更新（現在の被り）
def agentImpactUpdate(agents, maze):
    # 現在のセル毎の人数把握
    now_map = agentCountMap(agents, maze)
    for agent in agents:
        agent.impact_count += now_map[agent.position[0]][agent.position[1]]-1


# エージェント総数マップのリセット(0で初期化)
def resetTotalAgentMap(maze):
    totalAgentMap = copy.deepcopy(maze)
    for y in range(len(totalAgentMap)):
        for x in range(len(totalAgentMap[0])):
            if totalAgentMap[y][x] != 0:
                totalAgentMap[y][x] = 0
    return totalAgentMap


# エージェント総数マップの更新
def updateAgentTotalMap(agents, total_agent_map):
    for agent in agents:
        total_agent_map[agent.position[0]][agent.position[1]] += 1


# エージェント総数マップの更新(乗客の種別で分ける)
def updateAgentTotalMapRB(agents, total_map, red_map, blue_map):
    for agent in agents:
        total_map[agent.position[0]][agent.position[1]] += 1
        if agent.agent_type == 0:
            red_map[agent.position[0]][agent.position[1]] += 1
        elif agent.agent_type == 1:
            blue_map[agent.position[0]][agent.position[1]] += 1
