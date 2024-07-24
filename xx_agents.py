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

# --- エージェントのネクストマップ ---
def agentNextMap(agents, maze):
    agent_next_map = copy.deepcopy(maze)
    for agent in agents:
        if len(agent.path)<2:
            continue
        agent_next_map[agent.path[1][0]][agent.path[1][1]] = agent.id
    return agent_next_map

# --- エージェントの周囲に人がいるか ---
def agentNeighborChk(agent, maze):
    

    return None

