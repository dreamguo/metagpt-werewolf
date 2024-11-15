from examples.werewolf_game.actions import InstructSpeak, Speak, Save, Poison
from examples.werewolf_game.roles.base_player import BasePlayer

class Witch(BasePlayer):
    def __init__(
        self,
        name: str = "",
        profile: str = "Witch",
        special_action_names: list[str] = ["Save", "Poison"],
        **kwargs,
    ):
        super().__init__(name, profile, special_action_names, **kwargs)

    async def _think(self):
        """女巫涉及两个特殊技能，因此在此需要改写_think进行路由"""
        news = self._rc.news[0]
        assert news.cause_by == InstructSpeak # 消息为来自Moderator的指令时，才去做动作
        if not news.restricted_to:
            # 消息接收范围为全体角色的，做公开发言（发表投票观点也算发言）
            self._rc.todo = Speak()
        elif self.profile in news.restricted_to.split(","):
            # FIXME: hard code to split, restricted为"Moderator"或"Moderator,角色profile"
            # Moderator加密发给自己的，意味着要执行角色的特殊动作
            # 这里用关键词进行动作的选择，需要Moderator侧的指令进行配合
            if "save" in news.content.lower():
                self._rc.todo = Save()
            elif "poison" in news.content.lower():
                self._rc.todo = Poison()
            else:
                raise ValueError("Moderator's instructions must include save or poison keyword")
