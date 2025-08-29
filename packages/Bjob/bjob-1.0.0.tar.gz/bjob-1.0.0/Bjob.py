#!/usr/bin/env python3
"""
工作性价比计算器 MCP工具
简化版本，只保留核心计算功能
"""

import json
import logging
from typing import Dict, Any
from mcp.server.fastmcp import FastMCP

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建MCP服务器
mcp = FastMCP("Bjob")

# ================================
# 📊 PPP数据和计算逻辑
# ================================

# 中国PPP转换因子（固定值）
CHINA_PPP_FACTOR = 4.19

# 学历加成系数
EDUCATION_BONUS = {
    "高中及以下": 0.8,
    "大专": 0.9,
    "本科": 1.0,
    "硕士": 1.15,
    "博士": 1.3,
    "博士后": 1.4
}

# 工作经验加成系数
EXPERIENCE_BONUS = {
    "0-1年": 0.8,
    "1-3年": 0.9,
    "3-5年": 1.0,
    "5-8年": 1.1,
    "8-12年": 1.2,
    "12年以上": 1.3
}

# 城市等级系数
CITY_LEVEL_FACTOR = {
    "一线城市": 1.2,
    "新一线城市": 1.1,
    "二线城市": 1.0,
    "三线城市": 0.9,
    "四线及以下城市": 0.8
}

# 工作环境评分系数
WORK_ENV_FACTOR = {
    "优秀": 1.2,
    "良好": 1.1,
    "一般": 1.0,
    "较差": 0.9,
    "很差": 0.8
}

# ================================
# 🔧 核心计算函数
# ================================

def _calculate_work_worth_internal(
    annual_salary: float,
    work_days_per_week: int,
    wfh_days_per_week: int,
    annual_leave_days: int,
    legal_holidays: int,
    paid_sick_leave: int,
    daily_work_hours: float,
    commute_hours: float,
    rest_hours: float,
    education: str,
    experience: str,
    city_level: str,
    work_environment: str
) -> Dict[str, Any]:
    """
    计算工作性价比的核心函数
    
    Args:
        annual_salary: 年薪总包
        work_days_per_week: 每周工作天数
        wfh_days_per_week: 每周居家办公天数
        annual_leave_days: 年假天数
        legal_holidays: 法定假日天数
        paid_sick_leave: 带薪病假天数
        daily_work_hours: 每日总工时（包括午休等）
        commute_hours: 每日通勤时间
        rest_hours: 每日休息摸鱼时间
        education: 学历水平
        experience: 工作经验
        city_level: 城市等级
        work_environment: 工作环境
    
    Returns:
        包含详细分析结果的字典
    """
    
    # 使用固定的中国PPP转换因子
    ppp_factor = CHINA_PPP_FACTOR
    
    # 计算年工作天数
    total_work_days = work_days_per_week * 52 - annual_leave_days - legal_holidays - paid_sick_leave
    
    # 计算实际工作时间（扣除休息摸鱼时间）
    effective_work_hours = daily_work_hours - rest_hours
    
    # 计算总投入时间（工作时间 + 通勤时间）
    total_daily_time = daily_work_hours + commute_hours
    
    # 计算标准化日薪（PPP调整后）
    daily_salary_ppp = (annual_salary / ppp_factor) / total_work_days
    
    # 计算时薪（基于总投入时间）
    hourly_rate = daily_salary_ppp / total_daily_time
    
    # 计算有效时薪（基于实际工作时间）
    effective_hourly_rate = daily_salary_ppp / effective_work_hours
    
    # 工作生活平衡评分
    wlb_score = 100
    
    # 工时惩罚
    if daily_work_hours > 8:
        wlb_score -= (daily_work_hours - 8) * 5
    
    # 通勤惩罚
    if commute_hours > 1:
        wlb_score -= (commute_hours - 1) * 10
    
    # WFH加分
    wfh_ratio = wfh_days_per_week / work_days_per_week
    wlb_score += wfh_ratio * 20
    
    # 假期加分
    if annual_leave_days > 10:
        wlb_score += (annual_leave_days - 10) * 2
    
    # 确保评分在合理范围内
    wlb_score = max(0, min(100, wlb_score))
    
    # 个人因素调整
    education_factor = EDUCATION_BONUS.get(education, 1.0)
    experience_factor = EXPERIENCE_BONUS.get(experience, 1.0)
    city_factor = CITY_LEVEL_FACTOR.get(city_level, 1.0)
    env_factor = WORK_ENV_FACTOR.get(work_environment, 1.0)
    
    # 计算综合性价比分数
    base_score = hourly_rate * 10  # 基础分数
    adjusted_score = base_score * education_factor * experience_factor * city_factor * env_factor
    final_score = adjusted_score * (wlb_score / 100)
    
    # 生成评级
    if final_score >= 80:
        rating = "优秀"
        rating_desc = "这份工作的性价比非常高！"
    elif final_score >= 60:
        rating = "良好"
        rating_desc = "这份工作的性价比不错。"
    elif final_score >= 40:
        rating = "一般"
        rating_desc = "这份工作的性价比中等。"
    elif final_score >= 20:
        rating = "较差"
        rating_desc = "这份工作的性价比偏低。"
    else:
        rating = "很差"
        rating_desc = "建议考虑其他机会。"
    
    result_data = {
        "基本信息": {
            "年薪总包": f"{annual_salary:,.0f}",
            "PPP转换因子": ppp_factor,
            "年工作天数": total_work_days,
            "每日总投入时间": f"{total_daily_time:.1f}小时",
            "每日有效工作时间": f"{effective_work_hours:.1f}小时"
        },
        "薪资分析": {
            "标准化日薪(PPP调整)": f"{daily_salary_ppp:.2f}",
            "时薪(基于总投入时间)": f"{hourly_rate:.2f}",
            "有效时薪(基于工作时间)": f"{effective_hourly_rate:.2f}"
        },
        "工作生活平衡": {
            "平衡评分": f"{wlb_score:.1f}/100",
            "WFH比例": f"{wfh_ratio*100:.1f}%",
            "年假天数": annual_leave_days,
            "通勤时间": f"{commute_hours:.1f}小时/天"
        },
        "个人因素": {
            "学历加成": f"{education_factor:.2f}x",
            "经验加成": f"{experience_factor:.2f}x",
            "城市系数": f"{city_factor:.2f}x",
            "环境系数": f"{env_factor:.2f}x"
        },
        "综合评估": {
            "性价比分数": f"{final_score:.1f}",
            "评级": rating,
            "评价": rating_desc
        },
        "改进建议": generate_suggestions({
            "wlb_score": wlb_score,
            "commute_hours": commute_hours,
            "daily_work_hours": daily_work_hours,
            "wfh_ratio": wfh_ratio,
            "annual_leave_days": annual_leave_days
        })
    }
    
    return result_data

def generate_suggestions(metrics: Dict[str, float]) -> list:
    """生成改进建议"""
    suggestions = []
    
    if metrics["commute_hours"] > 2:
        suggestions.append("🚗 考虑搬家到离公司更近的地方，或寻找支持远程办公的职位")
    
    if metrics["daily_work_hours"] > 10:
        suggestions.append("⏰ 工作时间过长，建议与上级沟通工作量分配")
    
    if metrics["wfh_ratio"] < 0.2:
        suggestions.append("🏠 争取更多居家办公机会，提升工作灵活性")
    
    if metrics["annual_leave_days"] < 10:
        suggestions.append("🏖️ 年假天数偏少，可以在下次谈薪时争取更多假期")
    
    if metrics["wlb_score"] < 50:
        suggestions.append("⚖️ 工作生活平衡需要改善，考虑寻找更平衡的工作机会")
    
    if not suggestions:
        suggestions.append("🎉 当前工作状态不错，继续保持！")
    
    return suggestions

# ================================
# 🎨 HTML报告模板已删除
# ================================

# ================================
# 🔧 MCP工具函数
# ================================

@mcp.tool()
def calculate_job_worth(
    annual_salary: float,
    work_days_per_week: int = 5,
    wfh_days_per_week: int = 0,
    annual_leave_days: int = 5,
    legal_holidays: int = 11,
    paid_sick_leave: int = 0,
    daily_work_hours: float = 8.0,
    commute_hours: float = 1.0,
    rest_hours: float = 1.0,
    education: str = "本科",
    experience: str = "3-5年",
    city_level: str = "二线城市",
    work_environment: str = "一般",
    return_format: str = "text"
) -> Any:
    """
    计算工作性价比，综合评估薪资、工时、通勤等多维度因素
    
    Args:
        annual_salary: 年薪总包（元）
        work_days_per_week: 每周工作天数
        wfh_days_per_week: 每周居家办公天数
        annual_leave_days: 年假天数
        legal_holidays: 法定假日天数
        paid_sick_leave: 带薪病假天数
        daily_work_hours: 每日总工时（小时，包括午休等）
        commute_hours: 每日通勤时间（小时）
        rest_hours: 每日休息摸鱼时间（小时）
        education: 学历水平（高中及以下/大专/本科/硕士/博士/博士后）
        experience: 工作经验（0-1年/1-3年/3-5年/5-8年/8-12年/12年以上）
        city_level: 城市等级（一线城市/新一线城市/二线城市/三线城市/四线及以下城市）
        work_environment: 工作环境（优秀/良好/一般/较差/很差）
        return_format: 返回格式（text=文本报告，json=JSON数据，both=同时返回）
    
    Returns:
        详细的工作性价比分析报告（文本或JSON格式）
    """
    
    try:
        # 调用内部计算函数
        result = _calculate_work_worth_internal(
            annual_salary=annual_salary,
            work_days_per_week=work_days_per_week,
            wfh_days_per_week=wfh_days_per_week,
            annual_leave_days=annual_leave_days,
            legal_holidays=legal_holidays,
            paid_sick_leave=paid_sick_leave,
            daily_work_hours=daily_work_hours,
            commute_hours=commute_hours,
            rest_hours=rest_hours,
            education=education,
            experience=experience,
            city_level=city_level,
            work_environment=work_environment
        )
        
        # 根据返回格式决定输出
        if return_format == "json":
            return json.dumps(result, ensure_ascii=False, indent=2)  # 返回JSON字符串
        elif return_format == "both":
            # 生成文本报告
            text_report = f"""
🎯 工作性价比分析报告
{'='*50}

📊 基本信息：
• 年薪总包：{result['基本信息']['年薪总包']} 元
• PPP转换因子：{result['基本信息']['PPP转换因子']}
• 年工作天数：{result['基本信息']['年工作天数']} 天
• 每日总投入：{result['基本信息']['每日总投入时间']}
• 有效工作时间：{result['基本信息']['每日有效工作时间']}

💰 薪资分析：
• 标准化日薪：{result['薪资分析']['标准化日薪(PPP调整)']} USD
• 时薪（总投入）：{result['薪资分析']['时薪(基于总投入时间)']} USD/小时
• 有效时薪：{result['薪资分析']['有效时薪(基于工作时间)']} USD/小时

⚖️ 工作生活平衡：
• 平衡评分：{result['工作生活平衡']['平衡评分']}
• WFH比例：{result['工作生活平衡']['WFH比例']}
• 年假天数：{result['工作生活平衡']['年假天数']} 天
• 通勤时间：{result['工作生活平衡']['通勤时间']}

👤 个人因素：
• 学历加成：{result['个人因素']['学历加成']}
• 经验加成：{result['个人因素']['经验加成']}
• 城市系数：{result['个人因素']['城市系数']}
• 环境系数：{result['个人因素']['环境系数']}

🏆 综合评估：
• 性价比分数：{result['综合评估']['性价比分数']}/100
• 评级：{result['综合评估']['评级']}
• 评价：{result['综合评估']['评价']}

💡 改进建议：
"""
            for suggestion in result['改进建议']:
                text_report += f"• {suggestion}\n"
            
            return {
                "text_report": text_report,
                "json_data": result
            }
        else:  # default to text
            # 格式化文本报告
            report = f"""
🎯 工作性价比分析报告
{'='*50}

📊 基本信息：
• 年薪总包：{result['基本信息']['年薪总包']} 元
• PPP转换因子：{result['基本信息']['PPP转换因子']}
• 年工作天数：{result['基本信息']['年工作天数']} 天
• 每日总投入：{result['基本信息']['每日总投入时间']}
• 有效工作时间：{result['基本信息']['每日有效工作时间']}

💰 薪资分析：
• 标准化日薪：{result['薪资分析']['标准化日薪(PPP调整)']} USD
• 时薪（总投入）：{result['薪资分析']['时薪(基于总投入时间)']} USD/小时
• 有效时薪：{result['薪资分析']['有效时薪(基于工作时间)']} USD/小时

⚖️ 工作生活平衡：
• 平衡评分：{result['工作生活平衡']['平衡评分']}
• WFH比例：{result['工作生活平衡']['WFH比例']}
• 年假天数：{result['工作生活平衡']['年假天数']} 天
• 通勤时间：{result['工作生活平衡']['通勤时间']}

👤 个人因素：
• 学历加成：{result['个人因素']['学历加成']}
• 经验加成：{result['个人因素']['经验加成']}
• 城市系数：{result['个人因素']['城市系数']}
• 环境系数：{result['个人因素']['环境系数']}

🏆 综合评估：
• 性价比分数：{result['综合评估']['性价比分数']}/100
• 评级：{result['综合评估']['评级']}
• 评价：{result['综合评估']['评价']}

💡 改进建议：
"""
            
            for suggestion in result['改进建议']:
                report += f"• {suggestion}\n"
            
            return report
        
    except Exception as e:
        logger.error(f"计算工作性价比时出错: {e}")
        return f"❌ 计算失败：{str(e)}"

# PPP转换因子工具已删除

# 工作对比工具已删除




# 参数模板工具已删除



# ================================
# 🚀 主函数
# ================================

def main():
    """启动MCP服务器"""
    logger.info("启动工作性价比计算器...")
    logger.info("🎯 功能：计算工作真实价值，考虑薪资、工时、通勤等多维度因素")
    mcp.run()

if __name__ == "__main__":
    main()


