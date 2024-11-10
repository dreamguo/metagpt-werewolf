import re
import ipdb
import json

def parse_log_file(filename):
    # 读取文件
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. 提取玩家设置信息
    setup_pattern = r"0 \| Game setup:\s*Player1: ([^,]+),\s*Player2: ([^,]+),\s*Player3: ([^,]+),\s*Player4: ([^,]+),\s*Player5: ([^,]+),\s*Player6: ([^,]+),\s*Player7: ([^,]+),"
    setup_match = re.search(setup_pattern, content)
    
    players = []
    if setup_match:
        roles = setup_match.groups()
        for i, role in enumerate(roles, 1):
            players.append({
                "id": i,
                "name": f"Player{i}",
                "role": role.strip()
            })
    
    # 添加Moderator
    players.append({
        "id": 0,
        "name": "Moderator",
        "role": "Moderator"
    })
    
    # 2. 提取对话信息
    dialogue = []
    
    # 修改后的正则表达式，匹配两种模式：
    # 1. "ROLE" 到 "\n} 的JSON消息
    # 2. 常规的Player/Moderator消息
    messages = re.finditer(
        r'(?:'
        r'(?:Player(\d)\(([^)]+)\)|Moderator\(Moderator\)):\s*\d+\s*\|\s*([^`]*?(?=(?:Player\d\([^)]+\)|Moderator\(Moderator\)|"ROLE"|\Z)))' # 常规消息
        r'|'
        r'(?:"ROLE"(.*?)"\n})'  # JSON块
        r')', 
        content,
        re.DOTALL
    )

    for match in messages:
        matched_text = match.group(0).strip()
        
        # 判断是否是JSON消息(以"ROLE"开头)
        if matched_text.startswith('"ROLE"'):
            # 重建完整的JSON格式
            json_text = "{" + matched_text
            try:
                data = json.loads(json_text)
                speaker = data.get("PLAYER_NAME", "Unknown")
                
                # 提取THOUGHTS
                if "THOUGHTS" in data:
                    dialogue.append({
                        "speaker": speaker,
                        "content": data.get("THOUGHTS", ""),
                        "type": "Thought",
                        "role": data.get("ROLE", ""),
                        "player_name": data.get("PLAYER_NAME", ""),
                        "living_players": data.get("LIVING_PLAYERS", [])
                    })
                
                # 提取RESPONSE
                if "RESPONSE" in data:
                    dialogue.append({
                        "speaker": speaker,
                        "content": data.get("RESPONSE", ""),
                        "type": "Response",
                        "role": data.get("ROLE", ""),
                        "player_name": data.get("PLAYER_NAME", ""),
                        "living_players": data.get("LIVING_PLAYERS", [])
                    })
            except json.JSONDecodeError:
                continue
        else:
            # 常规消息处理
            if match.group(1):  # Player消息
                player_num = match.group(1)
                role = match.group(2)
                message = match.group(3).strip() if match.group(3) else ""
                speaker = f"Player{player_num}"
            else:  # Moderator消息
                speaker = "Moderator"
                message = matched_text.split("|", 1)[1].strip() if "|" in matched_text else matched_text
            
            # 确定消息类型
            msg_type = "Say"  # 默认类型
            if "vote to eliminate" in message:
                msg_type = "Action"
            elif any(keyword in message for keyword in ["Hunt", "Protect", "Verify", "Poison", "SAVE", "PASS"]):
                msg_type = "Action"
            elif speaker == "Moderator":
                if "choose" in message.lower() or "who" in message.lower():
                    msg_type = "Question"
                elif "understood" in message.lower():
                    msg_type = "Confirmation"
                elif "killed" in message.lower() or "eliminated" in message.lower():
                    msg_type = "Announcement"
                else:
                    msg_type = "Instruction"
            
            dialogue.append({
                "speaker": speaker,
                "content": message,
                "type": msg_type
            })
    
    # 3. 创建最终的gameData结构
    game_data = {
        "players": players,
        "dialogue": dialogue
    }
    
    # 4. 保存对话到txt文件，保持原始字典格式
    with open("dialogue.txt", "w", encoding="utf-8") as f:
        f.write(str(dialogue))
    
    return game_data

# 使用示例
if __name__ == "__main__":
    game_data = parse_log_file("output.log")
    
    # 将结果写入新文件
    with open("game_data.json", "w", encoding="utf-8") as f:
        json.dump(game_data, f, ensure_ascii=False, indent=2)
    
    # 打印结果
    print("Players:")
    for player in game_data["players"]:
        print(f"{player['name']}: {player['role']}")
    
    print("\nDialogue count:", len(game_data["dialogue"]))
    print("\nMessage types distribution:")
    type_count = {}
    for entry in game_data["dialogue"]:
        type_count[entry["type"]] = type_count.get(entry["type"], 0) + 1
    for msg_type, count in type_count.items():
        print(f"{msg_type}: {count}")

    ipdb.set_trace()
    print("\nSample dialogue entries:")
    for entry in game_data["dialogue"][:3]:
        print(f"{entry['speaker']} ({entry['type']}): {entry['content'][:100]}...")