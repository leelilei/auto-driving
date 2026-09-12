"""
B2: Chain-of-Thought Baseline

Encourages step-by-step reasoning before generating the plan.
"""

from typing import Dict, Any
from .base import BaselineMethod


class ChainOfThoughtBaseline(BaselineMethod):
    """Chain-of-Thought prompting baseline."""

    def __init__(self, llm_client):
        super().__init__(llm_client, "b2_cot")

    def build_prompt(self, query: Dict[str, Any]) -> str:
        """
        Build CoT prompting prompt.

        Args:
            query: Dict with org, dest, days, people_number

        Returns:
            Prompt string encouraging step-by-step reasoning
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

请按照以下步骤进行思考和规划：

步骤1：分析需求
- 确定出发地和目的地是否相同
- 评估旅行天数是否充足
- 考虑人数对交通和住宿的影响

步骤2：选择目的地的主要景点
- 列出该城市的知名景点
- 根据天数选择合适数量的景点
- 考虑景点之间的地理位置和游览顺序

步骤3：安排餐饮
- 选择当地特色餐厅
- 考虑早中晚餐的合理分布
- 确保餐厅位置便于行程安排

步骤4：规划住宿
- 选择交通便利的酒店
- 考虑酒店档次与人数匹配

步骤5：安排交通
- 如果出发地与目的地不同，安排城际交通
- 考虑市内交通的便利性

步骤6：生成最终计划
根据以上分析，生成JSON格式的详细行程计划。

计划格式：
[
  [
    {{
      "days": 1,
      "current_city": "城市名",
      "transportation": "交通方式",
      "breakfast": "早餐餐厅名称",
      "attraction": ["景点1", "景点2"],
      "lunch": "午餐餐厅名称",
      "dinner": "晚餐餐厅名称",
      "accommodation": "住宿酒店名称"
    }}
  ]
]

注意事项：
1. 先进行步骤1-5的分析（可以简要说明你的思考）
2. 最后给出完整的JSON格式计划
3. JSON必须有效且符合上述格式
4. 如果某项不需要安排，使用"-"表示

请开始你的分析和规划："""

        return prompt
