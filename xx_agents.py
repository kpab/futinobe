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
### speedが無い場合(エージェントが次のパスに進む場合)、有効
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
        impact_agents = [next_ids[i] for i, p in enumerate(next_positions) if p == pos]
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
# --- エージェントのネクストマップ ---
# def agentNextMap(agents, maze):
#     agent_next_map = copy.deepcopy(maze)
#     for agent in agents:
#         if len(agent.path)<2:
#             continue
#         agent_next_map[agent.path[1][0]][agent.path[1][1]] = agent.id
#     return agent_next_map

# --- エージェントいるところにコスト ---
def agentNextMap(agents, agent_id, object_cost, s, maze):
    """
    agents: エージェントクラスリスト
    s: スピード
    """
    agent_next_map = copy.deepcopy(maze)
    for agent in agents:
        if len(agent.path)<s+1:
            continue
        # --- 同じエージェントを除く ---
        if agent.id==agent_id:
            continue
        agent_next_map[agent.path[s][0]][agent.path[s][1]] = object_cost
    return agent_next_map

# neighbors取得
def getNeighbors(position, other_agents, maze, object_cost):
    (x, y) = position
    neighbors = [(x-1, y), (x+1, y), (x, y-1), (x, y+1), (x+1, y+1), (x+1, y-1), (x-1, y+1), (x-1, y-1)]
    for index, next_position in enumerate(neighbors):
        if((maze[next_position[0]][next_position[1]]==object_cost) or # 回避先に壁
            next_position[0] < 0 or next_position[0] >= len(maze) or
            next_position[1] < 0 or next_position[1] >= len(maze[0])
            ):
            # neighbors.remove(next_position) # その回避地点を除外
            neighbors.pop(index)
            continue
        for other in other_agents: # 人がいる場合も除外
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
        impact_agents = [next_ids[i] for i, p in enumerate(next_positions) if p == pos]
        impacts[pos] = impact_agents
    # 衝突情報を表示
    for pos, ids in impacts.items():
        print(f"ID: {ids} が地点 {pos} で衝突")
# 壁突っ込みチェック
def wallBreakerChk(agents, wall_list, maze, object_cost):
    for agent in agents:
        if list(agent.position) in wall_list:
            print(f"{agent.id}が壁に突っ込んだ")
        if maze[agent.position[0]][agent.position[1]]==object_cost:
            print(f"{agent.id}のいる場所コストあり")