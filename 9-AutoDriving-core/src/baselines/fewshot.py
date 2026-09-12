"""
B1: Few-shot Prompting Baseline

Provides 2-3 examples before asking for plan generation.
"""

from typing import Dict, Any
from .base import BaselineMethod


class FewshotBaseline(BaselineMethod):
    """Few-shot prompting baseline with examples."""

    def __init__(self, llm_client):
        super().__init__(llm_client, "b1_fewshot")

    def build_prompt(self, query: Dict[str, Any]) -> str:
        """
        Build few-shot prompting prompt with examples.

        Args:
            query: Dict with org, dest, days, people_number

        Returns:
            Prompt string with examples
        """
        org = query.get('org', '')
        dest = query.get('dest', '')
        days = query.get('days', 1)
        people_number = query.get('people_number', 1)

        # Example 1: 1-day Beijing trip
        example1 = """
查询：
- 出发城市：北京
- 目的地城市：北京
- 旅行天数：1天
- 旅行人数：2人

计划：
[
  [
    {
      "days": 1,
      "current_city": "北京",
      "transportation": "-",
      "breakfast": "-",
      "attraction": ["故宫", "天坛"],
      "lunch": "全聚德烤鸭店",
      "dinner": "东来顺饭庄",
      "accommodation": "北京饭店"
    }
  ]
]"""

        # Example 2: 2-day Shanghai trip
        example2 = """
查询：
- 出发城市：杭州
- 目的地城市：上海
- 旅行天数：2天
- 旅行人数：3人

计划：
[
  [
    {
      "days": 1,
      "current_city": "杭州到上海",
      "transportation": "高铁",
      "breakfast": "-",
      "attraction": ["外滩", "东方明珠"],
      "lunch": "南翔馒头店",
      "dinner": "老正兴菜馆",
      "accommodation": "和平饭店"
    }
  ],
  [
    {
      "days": 2,
      "current_city": "上海",
      "transportation": "-",
      "breakfast": "上海小南国",
      "attraction": ["豫园", "田子坊"],
      "lunch": "鼎泰丰",
      "dinner": "新旺茶餐厅",
      "accommodation": "-"
    }
  ]
]"""

        prompt = f"""你是一个专业的旅行规划助手。我将提供一些示例，然后你需要为新的查询生成类似格式的旅行计划。

示例1：
{example1}

示例2：
{example2}

现在，请为以下新查询生成旅行计划：

查询：
- 出发城市：{org}
- 目的地城市：{dest}
- 旅行天数：{days}天
- 旅行人数：{people_number}人

计划：
请生成JSON格式的计划，格式与上面的示例相同。

注意事项：
1. 返回的必须是有效的JSON格式
2. 每天的行程要合理，景点不要过多
3. 餐厅和酒店要选择实际存在的知名场所
4. 如果出发城市和目的地城市不同，第一天需要安排交通
5. 如果某项不需要安排，使用"-"表示

请直接返回JSON格式的计划，不要添加其他解释文字。"""

        return prompt
