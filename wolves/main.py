from game import WerewolfGame

if __name__ == '__main__':
    # 可以在这里调整真人和AI玩家的数量
    total_players = int(input("请输入总玩家人数："))
    human_num = int(input("请输入真人玩家人数："))
    ai_num = int(input("请输入AI玩家人数："))
    
    game = WerewolfGame(total_players, human_num=human_num, ai_num=ai_num)
    game.play()
