import asyncio
import platform
import fire
import random
import ipdb

from examples.werewolf_game.info1 import SYSTEM_PROMPT as SYSTEM_PROMPT1
from examples.werewolf_game.info2 import SYSTEM_PROMPT as SYSTEM_PROMPT2
from examples.werewolf_game.info3 import SYSTEM_PROMPT as SYSTEM_PROMPT3
from examples.werewolf_game.info4 import SYSTEM_PROMPT as SYSTEM_PROMPT4
from examples.werewolf_game.info5 import SYSTEM_PROMPT as SYSTEM_PROMPT5
from examples.werewolf_game.info6 import SYSTEM_PROMPT as SYSTEM_PROMPT6
from examples.werewolf_game.info_final import SYSTEM_PROMPT as SYSTEM_PROMPT_FINAL
from time import sleep
from examples.werewolf_game.interjection import INTERJECTION
from metagpt.logs import logger
from examples.werewolf_game.werewolf_game import WerewolfGame
from examples.werewolf_game.roles import Moderator, Villager, Werewolf, Guard, Seer, Witch
from examples.werewolf_game.roles.human_player import prepare_human_player

def init_game_setup(
        role_uniq_objs: list[object],
        num_villager: int = 2,
        num_werewolf: int = 2,
        shuffle=True, add_human=False,
        use_reflection=True, use_experience=False, use_memory_selection=False,
        new_experience_version="",
    ):
    roles = []
    for role_obj in role_uniq_objs:
        if "Villager" in str(role_obj):
            roles.extend([role_obj] * num_villager)
        elif "Werewolf" in str(role_obj):
            roles.extend([role_obj] * num_werewolf)
        else:
            roles.append(role_obj)

    if shuffle:
        # random.seed(2023)
        random.shuffle(roles)
    if add_human:
        assigned_role_idx = random.randint(0, len(roles) - 1)
        assigned_role = roles[assigned_role_idx]
        roles[assigned_role_idx] = prepare_human_player(assigned_role)

    players = [
        role(
            name = f"Player{i+1}",
            use_reflection=use_reflection, use_experience=use_experience, use_memory_selection=use_memory_selection,
            new_experience_version=new_experience_version
        ) for i, role in enumerate(roles)
    ]

    if add_human:
        logger.info(f"You are assigned {players[assigned_role_idx].name}({players[assigned_role_idx].profile})")

    game_setup = ["Game setup:"] + [f"{player.name}: {player.profile}," for player in players]
    game_setup = "\n".join(game_setup)

    return game_setup, players

async def start_game(
    n_games: int = 1,
    n_player: int = 5,
    investment: float = 3.0,
    n_round: int = 5,
    shuffle: bool = True,
    add_human: bool = False,
    use_reflection: bool = True,
    use_experience: bool = False,
    use_memory_selection: bool = False,
    new_experience_version: str = "",
):
    game = WerewolfGame()
    name_list = [SYSTEM_PROMPT[i]['name'] for i in range(n_player)]
    logger.info(
        f"n_games: {n_games}, n_round: {n_round}, n_player: {n_player}")
    game_setup, players = init_game_setup(
        role_uniq_objs=[Villager, Werewolf, Guard, Seer, Witch],
        num_werewolf=int((n_player - 3) // 2 + (n_player - 3) % 2),
        num_villager=int((n_player - 3) // 2),
        shuffle=shuffle,
        add_human=add_human,
        use_reflection=use_reflection,
        use_experience=use_experience,
        use_memory_selection=use_memory_selection,
        new_experience_version=new_experience_version,
    )
    logger.info(f"{game_setup}")

    # Add memories to players
    i = 0
    for player in players:
        if 'Moderator' in str(player):
            continue
        player.add_initial_memories(SYSTEM_PROMPT[i]['prompt'])
        i += 1


    for i in range(n_games):
        logger.info(f"=== start Game Round {i + 1} ===\n")
        players = [Moderator()] + players
        game.hire(players)
        game.invest(investment)
        game.start_project(game_setup)
        await game.run(n_round=n_round)
        
        sleep(5) # wait for the last message to be printed

        logger.info(f"=== Completed Game Round {i + 1} ===\n")


def main(n_games: int = 1, n_player: int = 5, group: int = 1,
         investment: float = 20.0, n_round: int = 500, shuffle : bool = True, add_human: bool = False,
         use_reflection: bool = True, use_experience: bool = False, use_memory_selection: bool = False,
         new_experience_version: str = ""):

    system_prompt_dict = {1: SYSTEM_PROMPT1, 2: SYSTEM_PROMPT2, 3: SYSTEM_PROMPT3, 4: SYSTEM_PROMPT4,
                          5: SYSTEM_PROMPT5, 6: SYSTEM_PROMPT6, 7: SYSTEM_PROMPT_FINAL}
    global SYSTEM_PROMPT
    SYSTEM_PROMPT = system_prompt_dict[group]

    # print(len(SYSTEM_PROMPT))
    # for i in range(len(SYSTEM_PROMPT)):
    #     print(f"'{SYSTEM_PROMPT[i]['name']}'", end=',')
    # ipdb.set_trace()

    asyncio.run(
        start_game(
            n_games,
            n_player,
            investment,
            n_round,
            shuffle,
            add_human,
            use_reflection,
            use_experience,
            use_memory_selection,
            new_experience_version,
        ))


if __name__ == '__main__':
    fire.Fire(main)

# names = {1: ['Kupo','GaryChia380460','Sczwt','nft2great','nftflair','ggbak',
#               'iDominoes','Mirou_Bouguerba','mferPalace','joltikahedron','kenthecaffiend'],
# }
