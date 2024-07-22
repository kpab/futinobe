from collections import Counter

def futurePrediction(agents):
    next_agent_positions = {}
    for agent in agents:
        if len(agent.path) > 0:
            next_agent_positions[agent.id] = tuple(agent.path[0])  # タプルに変換
    return next_agent_positions

def futureImpactError(agents):
    next_agent_positions = futurePrediction(agents)

    # 次の位置とそのIDをリストに変換
    next_positions = list(next_agent_positions.values())
    next_ids = list(next_agent_positions.keys())

    # 次の位置をタプルに変換し、重複をカウント
    impact_positions = [
        pos for pos, count in Counter(next_positions).items() if count > 1
    ]

    # 衝突地点とその地点でのエージェントIDを収集
    impacts = {}
    for pos in impact_positions:
        colliding_agents = [next_ids[i] for i, p in enumerate(next_positions) if p == pos]
        impacts[pos] = colliding_agents

    # 衝突情報を表示
    for pos, ids in impacts.items():
        print(f"ID: {ids} が地点 {pos} で衝突")
