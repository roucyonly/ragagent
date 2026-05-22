SYSTEM_PROMPT = """你是一位资深塔罗牌占卜师，拥有丰富的占卜经验和深厚的心灵洞察力。

用户正在进行一次塔罗占卜的追问环节。请根据原始占卜的问题、牌阵以及之前的对话历史，
回答用户的追问。要求：
- 语言优美有灵性，结合牌阵给出深层解读
- 回答限制在300字以内
- 只针对当前占卜的话题和牌阵内容进行回答，不开启新的占卜
- 在回答中自然融入牌阵信息
- 如果用户的问题与原始占卜话题无关，或是开启了全新话题，请明确告知"这个问题超出了当前占卜的范围，请继续围绕之前的议题追问"，不要生成牌阵解读
- 如果用户只是在闲聊而非提问，可以温和地引导用户："让我们回到你的占卜上..."
"""

USER_PROMPT_TEMPLATE = """原始占卜信息：
- 占卜话题：{topic_name}
- 用户问题：{question}
- 抽到的三张牌（过去、现在、未来）：
{cards_text}

各牌的参考含义：
{cards_meanings}

用户信息：{user_info}

对话历史：
{history}

用户的追问：{follow_up_question}

请回答用户的追问。"""


def build_follow_up_prompt(
    topic_name: str,
    question: str | None,
    cards_text: str,
    cards_meanings: str,
    user_info: str = "",
    history: list[dict] | None = None,
    follow_up_question: str = "",
) -> tuple[str, str]:
    history_text = ""
    if history:
        for msg in history:
            role_label = "用户" if msg["role"] == "user" else "占卜师"
            history_text += f"{role_label}：{msg['content']}\n\n"

    user_prompt = USER_PROMPT_TEMPLATE.format(
        topic_name=topic_name,
        question=question or "无特定问题",
        cards_text=cards_text,
        cards_meanings=cards_meanings,
        user_info=user_info or "未提供",
        history=history_text or "（无历史对话）",
        follow_up_question=follow_up_question,
    )
    return SYSTEM_PROMPT, user_prompt