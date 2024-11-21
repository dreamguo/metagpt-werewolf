import asyncio
import platform
import fire
import random
import ipdb

from examples.werewolf_game.info2 import SYSTEM_PROMPT
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
    n_games: int = 1, n_player: int = 5,
    investment: float = 3.0, n_round: int = 5, shuffle : bool = True, add_human: bool = False,
    use_reflection: bool = True, use_experience: bool = False, use_memory_selection: bool = False,
    new_experience_version: str = "",
):
    game = WerewolfGame()
    name_list = [SYSTEM_PROMPT[i]['name'] for i in range(n_player - 1)]
    game_setup, players = init_game_setup(
        role_uniq_objs=[Villager, Werewolf, Guard, Seer, Witch],
        num_werewolf=int((n_player - 3) // 2 + (n_player - 3) % 2),
        num_villager=int((n_player - 3) // 2),
        shuffle=shuffle, add_human=add_human, use_reflection=use_reflection, use_experience=use_experience,
        use_memory_selection=use_memory_selection, new_experience_version=new_experience_version,
    )

    # Add memories to players
    i = 0
    for player in players:
        if 'Moderator' in str(player):
            continue
        player.add_initial_memories(SYSTEM_PROMPT[i]['promt'])
        i += 1

    players = [Moderator()] + players
    game.hire(players)
    game.invest(investment)
    game.start_project(game_setup)
    await game.run(n_round=n_round)


async def start_multi_game(
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
        player.add_initial_memories(SYSTEM_PROMPT[i]['promt'])
        i += 1


    for i in range(n_games):
        logger.info(f"=== start Game Round {i + 1} ===\n")
        players = [Moderator()] + players
        game.hire(players)
        game.invest(investment)
        game.start_project(game_setup)
        await game.run(n_round=n_round)
        logger.info(f"=== Completed Game Round {i + 1} ===\n")


def main(n_games: int = 1, n_player: int = 5,
         investment: float = 20.0, n_round: int = 100, shuffle : bool = True, add_human: bool = False,
         use_reflection: bool = True, use_experience: bool = False, use_memory_selection: bool = False,
         new_experience_version: str = ""):

    # asyncio.run(start_game(n_games, n_player, investment, n_round, shuffle, add_human,
    #                        use_reflection, use_experience, use_memory_selection, new_experience_version))
    asyncio.run(
        start_multi_game(
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
