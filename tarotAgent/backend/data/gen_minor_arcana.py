"""Generate Minor Arcana cards and append to tarot_cards.json."""
import json
import os

CARD_FILE = os.path.join(os.path.dirname(__file__), "tarot_cards.json")

SUITS = {
    "Wands": {"cn": "权杖", "element": "Fire",
              "theme": "行动力、创造力与激情",
              "love_theme": "激情与主动",
              "career_theme": "事业冲劲",
              "destiny_theme": "热烈的缘分",
              "family_theme": "家庭活力",
              "general_theme": "行动与创造"},
    "Cups": {"cn": "圣杯", "element": "Water",
             "theme": "情感、关系与内心世界",
             "love_theme": "情感的流动",
             "career_theme": "职业满足感",
             "destiny_theme": "心灵契合的缘分",
             "family_theme": "家庭情感",
             "general_theme": "情感与直觉"},
    "Swords": {"cn": "宝剑", "element": "Air",
               "theme": "思维、冲突与真相",
               "love_theme": "理性与沟通",
               "career_theme": "职场策略",
               "destiny_theme": "理性审视的缘分",
               "family_theme": "家庭沟通",
               "general_theme": "思考与抉择"},
    "Pentacles": {"cn": "星币", "element": "Earth",
                  "theme": "物质、现实与安全感",
                  "love_theme": "稳定与承诺",
                  "career_theme": "财富与成就",
                  "destiny_theme": "踏实长久的缘分",
                  "family_theme": "家庭安定",
                  "general_theme": "物质与现实"},
}

NUMBER_NAMES = {
    1: ("Ace", "首牌"),
    2: ("Two", "二"),
    3: ("Three", "三"),
    4: ("Four", "四"),
    5: ("Five", "五"),
    6: ("Six", "六"),
    7: ("Seven", "七"),
    8: ("Eight", "八"),
    9: ("Nine", "九"),
    10: ("Ten", "十"),
    11: ("Page", "侍从"),
    12: ("Knight", "骑士"),
    13: ("Queen", "王后"),
    14: ("King", "国王"),
}

# Each number's core meaning per suit theme direction
NUMBER_MEANINGS = {
    1: {
        "kw_en": ["new beginnings", "opportunity", "potential"],
        "kw_cn": ["新的开始", "机遇", "潜力"],
        "kw_rev_en": ["missed opportunity", "false start"],
        "kw_rev_cn": ["错失良机", "不顺利的开始"],
        "up": "一个全新的开始，充满了潜力和机遇。",
        "rev": "机会可能被错过，或者开端不够顺利。",
    },
    2: {
        "kw_en": ["balance", "decisions", "duality"],
        "kw_cn": ["平衡", "抉择", "二元性"],
        "kw_rev_en": ["imbalance", "indecision"],
        "kw_rev_cn": ["失衡", "犹豫不决"],
        "up": "面临选择和平衡的考验，需要在两个方向间做出决定。",
        "rev": "失衡或犹豫不决，难以做出选择。",
    },
    3: {
        "kw_en": ["growth", "expansion", "collaboration"],
        "kw_cn": ["成长", "扩展", "合作"],
        "kw_rev_en": ["delays", "lack of growth"],
        "kw_rev_cn": ["延迟", "成长受阻"],
        "up": "成长和扩张的时期，合作带来进展。",
        "rev": "成长受阻，合作可能出现问题。",
    },
    4: {
        "kw_en": ["stability", "structure", "security"],
        "kw_cn": ["稳定", "结构", "安全"],
        "kw_rev_en": ["instability", "lack of security"],
        "kw_rev_cn": ["不稳定", "缺乏安全感"],
        "up": "稳定和安全的局面，结构化的进展。",
        "rev": "稳定受到威胁，可能感到不安全。",
    },
    5: {
        "kw_en": ["conflict", "loss", "challenge"],
        "kw_cn": ["冲突", "失去", "挑战"],
        "kw_rev_en": ["recovery", "moving on"],
        "kw_rev_cn": ["恢复", "向前看"],
        "up": "面临冲突或挑战，可能经历一些损失。",
        "rev": "从困境中恢复，开始向前看。",
    },
    6: {
        "kw_en": ["harmony", "generosity", "gratitude"],
        "kw_cn": ["和谐", "慷慨", "感恩"],
        "kw_rev_en": ["selfishness", "ingratitude"],
        "kw_rev_cn": ["自私", "不知感恩"],
        "up": "和谐与慷慨，充满感恩的时刻。",
        "rev": "可能忽略了感恩，或过于计较得失。",
    },
    7: {
        "kw_en": ["reflection", "assessment", "patience"],
        "kw_cn": ["反思", "评估", "耐心"],
        "kw_rev_en": ["impulsiveness", "lack of reflection"],
        "kw_rev_cn": ["冲动", "缺乏反思"],
        "up": "需要耐心和反思，评估当前的状况。",
        "rev": "过于急躁，缺乏必要的反思。",
    },
    8: {
        "kw_en": ["mastery", "skill", "diligence"],
        "kw_cn": ["精进", "技艺", "勤奋"],
        "kw_rev_en": ["lack of focus", "perfectionism"],
        "kw_rev_cn": ["缺乏专注", "完美主义"],
        "up": "通过勤奋和专注达到精进，技艺日益成熟。",
        "rev": "可能过于追求完美或缺乏专注。",
    },
    9: {
        "kw_en": ["abundance", "luxury", "gratitude"],
        "kw_cn": ["丰盛", "奢华", "感恩"],
        "kw_rev_en": ["greed", "dissatisfaction"],
        "kw_rev_cn": ["贪婪", "不满足"],
        "up": "丰盛和满足，享受劳动的成果。",
        "rev": "可能过于贪心或不满足现状。",
    },
    10: {
        "kw_en": ["completion", "burden", "responsibility"],
        "kw_cn": ["完成", "重担", "责任"],
        "kw_rev_en": ["release", "delegation"],
        "kw_rev_cn": ["释放", "分摊"],
        "up": "一个周期的完成，但也带来了沉重的责任。",
        "rev": "开始释放重担，学会分摊责任。",
    },
    11: {  # Page
        "kw_en": ["curiosity", "exploration", "learning"],
        "kw_cn": ["好奇", "探索", "学习"],
        "kw_rev_en": ["lack of focus", "immaturity"],
        "kw_rev_cn": ["缺乏专注", "不成熟"],
        "up": "充满好奇心和探索精神，新的学习旅程。",
        "rev": "注意力不集中或行为不够成熟。",
    },
    12: {  # Knight
        "kw_en": ["action", "drive", "ambition"],
        "kw_cn": ["行动", "驱动力", "抱负"],
        "kw_rev_en": ["recklessness", "restlessness"],
        "kw_rev_cn": ["鲁莽", "不安分"],
        "up": "充满行动力和抱负，勇往直前。",
        "rev": "可能过于鲁莽或急躁。",
    },
    13: {  # Queen
        "kw_en": ["nurturing", "compassion", "practicality"],
        "kw_cn": ["滋养", "同情", "务实"],
        "kw_rev_en": ["insecurity", "neediness"],
        "kw_rev_cn": ["不安全感", "依赖"],
        "up": "温暖而务实的力量，滋养周围的人。",
        "rev": "可能过于依赖他人或缺乏安全感。",
    },
    14: {  # King
        "kw_en": ["authority", "structure", "discipline"],
        "kw_cn": ["权威", "结构", "纪律"],
        "kw_rev_en": ["tyranny", "rigidity"],
        "kw_rev_cn": ["专制", "固执"],
        "up": "成熟的权威和领导力，建立稳固的结构。",
        "rev": "可能过于专制或固执己见。",
    },
}

# Per-suit, per-number topic-specific readings
TOPIC_READINGS = {
    "Wands": {
        1: {"love": "新的激情火花点燃了你的感情生活。", "career": "充满创意的新项目即将启动。", "destiny": "一段充满激情的正缘即将开始。", "family": "家庭中迎来新的活力。", "general": "新的灵感和激情正在涌现。"},
        2: {"love": "感情中需要做出选择，两种可能性都令人期待。", "career": "正在规划更大的事业蓝图。", "destiny": "追寻正缘需要你做出勇敢的决定。", "family": "家庭中面临重要的选择。", "general": "远见和规划将带来回报。"},
        3: {"love": "感情稳步发展，前景光明。", "career": "事业蒸蒸日上，之前的规划开始见效。", "destiny": "正缘正在按命运的节奏向你走来。", "family": "家庭事务进展顺利。", "general": "远见和努力正在获得回报。"},
        4: {"love": "感情中值得庆祝的时刻，关系和谐稳定。", "career": "团队合作的成果值得庆祝。", "destiny": "正缘即将修成正果。", "family": "家庭团聚的喜悦。", "general": "收获和庆祝的时期。"},
        5: {"love": "感情中存在分歧，但磨合是成长的一部分。", "career": "职场竞争激烈，但能激发你的潜能。", "destiny": "正缘前需要经历一些考验。", "family": "家庭成员间意见不一。", "general": "竞争和挑战让你更强大。"},
        6: {"love": "感情中获得胜利，你们的爱情受到祝福。", "career": "事业成就获得广泛认可。", "destiny": "正缘是对你成长的奖赏。", "family": "家庭取得共同的成就。", "general": "大获全胜，努力得到回报。"},
        7: {"love": "坚持自己的爱情信念，不要轻易妥协。", "career": "面对挑战时需要坚定立场。", "destiny": "坚持等待正缘，不要将就。", "family": "在家庭中坚守自己的原则。", "general": "充满挑战但坚持就是胜利。"},
        8: {"love": "感情发展迅速，充满惊喜。", "career": "事情飞速推进，抓住机遇。", "destiny": "正缘来得很快，超出预期。", "family": "家庭事务快速推进。", "general": "快速发展，充满动感。"},
        9: {"love": "经历了一些感情考验，但你依然坚守。", "career": "坚持即将迎来回报。", "destiny": "正缘就在不远处，再坚持一下。", "family": "家庭中的坚持将带来转机。", "general": "韧性十足，胜利在望。"},
        10: {"love": "感情中承担了太多，需要学会分担。", "career": "事业负担重，但终点在望。", "destiny": "放下不必要的感情包袱才能迎接正缘。", "family": "家庭责任重大，需要寻求帮助。", "general": "负担较重，坚持即可到达终点。"},
        11: {"love": "感情中充满新鲜感和探索欲。", "career": "迎来令人兴奋的新机会。", "destiny": "正缘以充满惊喜的方式出现。", "family": "家庭中传来令人兴奋的消息。", "general": "充满活力和探索精神。"},
        12: {"love": "充满激情的追求，对方魅力四射。", "career": "干劲十足，是冲刺的好时机。", "destiny": "正缘如火焰般热烈地靠近。", "family": "家庭中充满活力。", "general": "充满激情和行动力。"},
        13: {"love": "自信的魅力吸引着爱情的到来。", "career": "自信和领导力让你脱颖而出。", "destiny": "正缘会被你的自信所吸引。", "family": "你是家庭中温暖而自信的存在。", "general": "自信阳光，魅力无法阻挡。"},
        14: {"love": "遇到有担当和魅力的对象。", "career": "领导地位稳固，远见卓识。", "destiny": "正缘是一位有担当的人。", "family": "家庭中的核心人物。", "general": "领导力和远见掌控全局。"},
    },
    "Cups": {
        1: {"love": "一段新的感情正在萌芽，充满了爱的可能性。", "career": "对工作产生了新的热情和满足感。", "destiny": "命中注定的爱正从心底涌起。", "family": "家庭中涌现新的温情。", "general": "情感的新起点，内心充满爱。"},
        2: {"love": "两人心意相通，感情甜蜜和谐。", "career": "工作伙伴间的默契配合。", "destiny": "你与正缘心有灵犀。", "family": "家人之间感情融洽。", "general": "关系和谐，心意相通。"},
        3: {"love": "社交中可能遇到心仪的对象，朋友们会助力。", "career": "团队合作愉快，工作氛围轻松。", "destiny": "正缘可能通过朋友圈出现。", "family": "家庭聚会增进感情。", "general": "社交活跃，友谊愉快。"},
        4: {"love": "对现有感情感到倦怠，需要重新发现美好。", "career": "对工作缺乏热情，需要寻找新的动力。", "destiny": "不要忽视身边的缘分。", "family": "可能忽视了家人的付出。", "general": "需要重新审视和感恩已有的美好。"},
        5: {"love": "感情中的失落和遗憾，允许自己悲伤。", "career": "工作中的挫折让你感到沮丧。", "destiny": "正缘之前可能需要释怀过去的伤痛。", "family": "家庭中有些未化解的伤感。", "general": "允许自己感受悲伤，然后向前看。"},
        6: {"love": "回忆过去的美好感情，或与旧人重逢。", "career": "工作中回归初心，找回热情。", "destiny": "正缘可能与过去有某种连接。", "family": "家庭中充满温馨的回忆。", "general": "怀旧的情绪，珍贵的回忆。"},
        7: {"love": "感情中的选择让人迷惑，需要看清真实的感受。", "career": "面对多种选择，需要辨别真正适合自己的。", "destiny": "不要被感情的幻象迷惑，正缘需要真实。", "family": "家庭中需要拨开迷雾看清真相。", "general": "需要分辨幻象与真实。"},
        8: {"love": "离开一段不满意的感情，寻找更深的情感满足。", "career": "放弃不合适的工作方向，追求真正的使命。", "destiny": "放下不适合的，才能迎接真正的正缘。", "family": "可能需要远离家庭的负面影响。", "general": "放下执念，追寻更有意义的事物。"},
        9: {"love": "感情中许愿成真，内心的满足感溢于言表。", "career": "工作获得极大的满足感和成就感。", "destiny": "你对正缘的期待即将实现。", "family": "家庭生活如你所愿。", "general": "心愿达成，幸福满溢。"},
        10: {"love": "感情圆满幸福，家庭的温馨与爱的丰盈。", "career": "事业与情感双丰收。", "destiny": "正缘带来完整的人生幸福。", "family": "家庭美满，幸福圆满。", "general": "幸福圆满，万事如意。"},
        11: {"love": "内心敏感温柔，容易被爱情打动。", "career": "用直觉和创意来面对工作。", "destiny": "用真诚的心去感受正缘的到来。", "family": "对家人的需求敏感体贴。", "general": "直觉敏锐，情感丰富。"},
        12: {"love": "浪漫的追求者出现，爱情充满诗意。", "career": "以创意和热情投入工作。", "destiny": "正缘以浪漫的方式降临。", "family": "为家庭带来温馨和惊喜。", "general": "浪漫与热情交织。"},
        13: {"love": "温暖体贴的伴侣，充满爱意和包容。", "career": "工作中展现关怀和创造力。", "destiny": "正缘是一位温柔包容的人。", "family": "家庭中的温暖港湾。", "general": "以爱和温柔面对一切。"},
        14: {"love": "感情中成熟稳重，给予深厚的爱和关怀。", "career": "以情感智慧处理工作中的关系。", "destiny": "正缘是一位情感成熟的人。", "family": "家庭中的情感支柱。", "general": "情感的智慧与成熟。"},
    },
    "Swords": {
        1: {"love": "感情中的真相浮出水面，清晰的沟通带来突破。", "career": "新思路和清晰的判断力带来事业突破。", "destiny": "正缘需要你用理性的眼光去识别。", "family": "家庭中需要坦诚沟通。", "general": "清晰的思维和果断的决定。"},
        2: {"love": "感情中的僵局需要打破，逃避不能解决问题。", "career": "工作中面临艰难的抉择。", "destiny": "正缘前需要先做出一个困难的决定。", "family": "家庭中的冷战需要化解。", "general": "需要面对困难的选择。"},
        3: {"love": "感情中的痛苦和心碎，但这也是治愈的开始。", "career": "工作中遭遇打击，需要时间恢复。", "destiny": "过去的感情伤痛需要先治愈才能迎接正缘。", "family": "家庭中存在令人痛心的问题。", "general": "痛苦是暂时的，治愈终会到来。"},
        4: {"love": "感情中需要休息和疗愈的空间。", "career": "工作是时候休息充电了。", "destiny": "在安静中恢复，为正缘做好准备。", "family": "家庭中需要一段平静的时光。", "general": "休息和恢复是必要的。"},
        5: {"love": "感情冲突激烈，需要放下自尊寻求和解。", "career": "职场纷争不断，注意言行。", "destiny": "不要让冲突阻碍了正缘的到来。", "family": "家庭争吵需要冷静处理。", "general": "冲突虽痛苦但能带来清醒。"},
        6: {"love": "从感情的低谷中慢慢走出，向着更好的方向前进。", "career": "离开不利的工作环境，寻找新的出路。", "destiny": "放下过去的伤痛，正缘在前方等你。", "family": "家庭关系正在改善。", "general": "过渡期，正在向好的方向转变。"},
        7: {"love": "感情中可能存在欺骗或不诚实。", "career": "工作中需要警惕不正当的行为。", "destiny": "不要被花言巧语迷惑了真正的正缘。", "family": "家庭中可能有隐藏的问题。", "general": "需要看清事物的真相。"},
        8: {"love": "感情中感到被困住和束缚，需要打破限制。", "career": "工作中感到受限和无力。", "destiny": "内心的恐惧阻碍了正缘的到来。", "family": "家庭中的限制感需要打破。", "general": "感到被困，但解脱即将来临。"},
        9: {"love": "对感情的焦虑和担忧，很多恐惧其实是想象。", "career": "对工作的过度担忧影响表现。", "destiny": "不要让恐惧阻止你相信正缘。", "family": "对家庭问题的过度焦虑。", "general": "很多恐惧只是心理的幻影。"},
        10: {"love": "感情的痛苦终结，但黎明前的黑暗过后是新生。", "career": "一个工作阶段的痛苦终结。", "destiny": "旧的结束是为了给正缘腾出空间。", "family": "家庭关系的重大转变。", "general": "痛苦结束，新的开始即将到来。"},
        11: {"love": "对感情充满好奇但可能过于理性。", "career": "以新的视角看待工作问题。", "destiny": "用敏锐的洞察力识别正缘。", "family": "需要用智慧处理家庭关系。", "general": "好奇心驱动学习和成长。"},
        12: {"love": "感情中行动迅速但可能过于急躁。", "career": "工作中快速行动，但需注意方向。", "destiny": "不要因为急躁而错过正缘的信号。", "family": "家庭中行动力强但需注意方式。", "general": "行动力强但需控制节奏。"},
        13: {"love": "以理性和独立的态度面对感情。", "career": "工作中展现清晰的判断力。", "destiny": "正缘需要在理性与感性间找到平衡。", "family": "以智慧处理家庭事务。", "general": "独立而敏锐的洞察力。"},
        14: {"love": "感情中理性成熟，能做出明智的判断。", "career": "以权威和智慧引领事业方向。", "destiny": "正缘是一位聪明且有决断力的人。", "family": "家庭中的理性力量。", "general": "清晰的思维和坚定的决断。"},
    },
    "Pentacles": {
        1: {"love": "一段有物质基础和实际承诺的新关系。", "career": "新的财务机会或事业开端。", "destiny": "正缘有着稳固的现实基础。", "family": "家庭经济状况改善。", "general": "新的财务机遇和实际进展。"},
        2: {"love": "在感情的多个方面之间寻找平衡。", "career": "在工作中平衡多项任务或资源。", "destiny": "正缘需要你在现实与浪漫间找到平衡。", "family": "平衡家庭的经济与情感需求。", "general": "灵活应变，在变化中保持平衡。"},
        3: {"love": "共同建设感情的基础，合作共赢。", "career": "团队合作完成重要项目。", "destiny": "与正缘共同打造美好未来。", "family": "家人共同建设温馨的家。", "general": "合作与学习带来实际成果。"},
        4: {"love": "感情中可能过于保守或控制。", "career": "对财务和资源的谨慎管理。", "destiny": "不要因过度保守而错过了正缘。", "family": "家庭中对资源的控制可能引发矛盾。", "general": "需要在对稳定和开放间找到平衡。"},
        5: {"love": "感情中的匮乏感或物质上的困难。", "career": "事业上遇到经济困难或被孤立。", "destiny": "当前的困境不代表没有正缘。", "family": "家庭中可能面临经济压力。", "general": "困难是暂时的，寻求帮助是明智的。"},
        6: {"love": "感情中慷慨给予和接受爱。", "career": "工作中获得资助或慷慨的帮助。", "destiny": "正缘会在你最需要的时候出现。", "family": "家庭中互相帮助和支持。", "general": "慷慨带来回报，施与受的平衡。"},
        7: {"love": "对感情的长期投资需要耐心等待回报。", "career": "审视事业进展，调整长期策略。", "destiny": "正缘需要时间的沉淀和等待。", "family": "耐心经营家庭关系将获得回报。", "general": "耐心和长远的目光。"},
        8: {"love": "用心经营感情，精益求精。", "career": "专注工作技能的磨练和提升。", "destiny": "正缘欣赏你的认真和专注。", "family": "用心维护家庭的每一个细节。", "general": "专注和匠心精神带来成就。"},
        9: {"love": "感情生活富足美满，享受二人世界的美好。", "career": "事业成功带来丰厚的物质回报。", "destiny": "正缘带来丰富而安稳的生活。", "family": "家庭生活优渥美满。", "general": "丰盈富足，享受劳动成果。"},
        10: {"love": "感情升华为家庭的传承和长久的承诺。", "career": "事业传承和家族企业的稳固。", "destiny": "正缘是一段经得起时间考验的缘分。", "family": "几代同堂，家庭兴旺。", "general": "长久的积累带来稳固的根基。"},
        11: {"love": "以务实的态度学习和探索感情。", "career": "新的学习机会或工作技能的提升。", "destiny": "用脚踏实地的态度迎接正缘。", "family": "家庭中的新机会值得期待。", "general": "脚踏实地，认真学习。"},
        12: {"love": "为感情的未来努力奋斗。", "career": "事业上的勤奋和坚持终获回报。", "destiny": "正缘需要你用行动去争取。", "family": "为家庭的未来努力付出。", "general": "踏实努力，稳中求进。"},
        13: {"love": "温暖务实的伴侣，给予物质和情感的双重关爱。", "career": "事业中展现务实和养育的品质。", "destiny": "正缘是一位踏实温暖的人。", "family": "家庭中的温馨守护者。", "general": "务实温暖，滋养周围的人。"},
        14: {"love": "感情中稳重可靠，给予安全感。", "career": "事业成功，财务稳固，领导有力。", "destiny": "正缘是一位可靠而有成就的人。", "family": "家庭中的经济支柱。", "general": "稳固成功，物质充盈。"},
    },
}


def main():
    with open(CARD_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    card_id = 22
    for suit_name, suit_info in SUITS.items():
        for num in range(1, 15):
            num_en, num_cn = NUMBER_NAMES[num]
            nm = NUMBER_MEANINGS[num]
            topics = TOPIC_READINGS[suit_name][num]

            card = {
                "card_id": card_id,
                "name_en": f"{num_en} of {suit_name}",
                "name_cn": f"{suit_info['cn']}{num_cn}",
                "arcana": "Minor",
                "suit": suit_name,
                "number": num,
                "element": suit_info["element"],
                "keywords": {
                    "upright": nm["kw_en"],
                    "upright_cn": nm["kw_cn"],
                    "reversed": nm["kw_rev_en"],
                    "reversed_cn": nm["kw_rev_cn"],
                },
                "meanings": {
                    "upright_cn": nm["up"],
                    "reversed_cn": nm["rev"],
                },
                "topic_meanings": {
                    "love": {"upright_cn": topics["love"], "reversed_cn": f"逆位时需要反思{suit_info['love_theme']}中的不足。"},
                    "career": {"upright_cn": topics["career"], "reversed_cn": f"逆位时{suit_info['career_theme']}可能遇到阻碍。"},
                    "destiny": {"upright_cn": topics["destiny"], "reversed_cn": f"逆位时{suit_info['destiny_theme']}可能暂时受阻。"},
                    "family": {"upright_cn": topics["family"], "reversed_cn": f"逆位时{suit_info['family_theme']}需要更多关注。"},
                    "general": {"upright_cn": topics["general"], "reversed_cn": f"逆位时{suit_info['general_theme']}方面需要注意。"},
                },
            }
            data["cards"].append(card)
            card_id += 1

    with open(CARD_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Done! Total cards: {len(data['cards'])}")


if __name__ == "__main__":
    main()
