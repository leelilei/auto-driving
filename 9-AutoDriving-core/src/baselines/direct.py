"""
B0: Direct Prompting Baseline

The simplest baseline: directly ask LLM to generate a travel plan.
"""

from typing import Dict, Any
from .base import BaselineMethod


class DirectBaseline(BaselineMethod):
    """Direct prompting baseline."""

    def __init__(self, llm_client):
        super().__init__(llm_client, "b0_direct")

    def build_prompt(self, query: Dict[str, Any]) -> str:
        """
        Build direct prompting prompt.

        Args:
            query: Dict with org, dest, days, people_number

        Returns:
            Prompt string
        """
        org = query.get('org', '')
        dest = query.get('dest', '')
        days = query.get('days', 1)
        people_number = query.get('people_number', 1)

        prompt = f"""你是一个专业的旅行规划助手。请为以下查询生成一个详细的旅行计划。

查询信息：
- 出发城市：{org}
- 目的地城市：{dest}
- 旅行天数：{days}天
- 旅行人数：{people_number}人

请生成一个JSON格式的旅行计划，格式如下：

[
  [
    {{
      "days": 1,
      "current_city": "城市名",
      "transportation": "交通方式（如果是第一天从出发城市到目的地，写具体方式；如果在同一城市，写"-"）",
      "breakfast": "早餐餐厅名称（如果不安排早餐，写"-"）",
      "attraction": ["景点1", "景点2"],
      "lunch": "午餐餐厅名称",
      "dinner": "晚餐餐厅名称",
      "accommodation": "住宿酒店名称"
    }}
  ]
]

注意事项：
1. 返回的必须是有效的JSON格式
2. 每天的行程要合理，景点不要过多
3. 餐厅和酒店要选择实际存在的知名场所
4. 如果出发城市和目的地城市不同，第一天需要安排交通
5. 如果某项不需要安排，使用"-"表示
6. 景点列表可以包含多个景点，但要确保一天内能够完成

请直接返回JSON格式的计划，不要添加其他解释文字。"""

        return prompt
