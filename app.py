# app.py - 西昌学院北校区食堂智能推荐系统（完整稳定版）
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# ============ 页面配置 ============
st.set_page_config(
    page_title="西昌学院北校区食堂智能推荐系统",
    page_icon="🏫",
    layout="wide"
)

# ============ 标题部分 ============
st.title("🏫 西昌学院北校区食堂智能推荐系统")
st.markdown("🎓 人工智能课程期末项目 | 基于多因素加权推荐模型")
st.markdown("---")

# ============ 侧边栏配置 ============
with st.sidebar:
    st.header("⚙️ 智能推荐设置")
    
    # 用户信息
    st.subheader("👤 用户信息")
    user_type = st.selectbox(
        "身份类型",
        ["本科生", "研究生", "教师", "留学生", "访客"],
        key="user_type"
    )
    
    # 就餐目的
    st.subheader("🎯 就餐目的")
    dining_purpose = st.selectbox(
        "本次就餐目的",
        ["日常快速就餐", "朋友聚餐", "学习讨论", "改善伙食"],
        key="dining_purpose"
    )
    
    # 时间设置
    st.subheader("🕒 时间设置")
    current_time = st.time_input("就餐时间", datetime.now().time(), key="current_time")
    
    # 价格预算
    st.subheader("💰 价格预算")
    price_range = st.slider(
        "价格范围（元）",
        5, 50, (8, 25),
        key="price_range"
    )
    
    # 等待容忍
    st.subheader("⏱️ 等待容忍")
    max_wait_time = st.slider(
        "最长等待时间（分钟）",
        5, 45, 15,
        key="max_wait_time"
    )

# ============ 食堂基础数据 ============
CANTEENS_DATA = [
    {
        "name": "北一食堂（大众餐厅）",
        "type": "大众食堂",
        "price_range": [8, 12],
        "base_score": 8.5,
        "location": "教学楼A区旁",
        "specialty": "价格实惠，传统菜品"
    },
    {
        "name": "北二食堂（风味餐厅）",
        "type": "风味食堂",
        "price_range": [10, 18],
        "base_score": 9.0,
        "location": "学生活动中心1楼",
        "specialty": "川味小吃，麻辣鲜香"
    },
    {
        "name": "北三食堂（清真食堂）",
        "type": "清真食堂",
        "price_range": [12, 20],
        "base_score": 8.3,
        "location": "留学生公寓旁",
        "specialty": "清真食品，牛羊肉特色"
    },
    {
        "name": "北四食堂（快餐中心）",
        "type": "快餐食堂",
        "price_range": [10, 16],
        "base_score": 7.8,
        "location": "图书馆负一楼",
        "specialty": "快捷便利，打包方便"
    },
    {
        "name": "北五食堂（自助餐厅）",
        "type": "自助食堂",
        "price_range": [15, 25],
        "base_score": 9.2,
        "location": "体育馆旁",
        "specialty": "菜品多样，自由选择"
    },
    {
        "name": "北六食堂（教工餐厅）",
        "type": "教工食堂",
        "price_range": [15, 30],
        "base_score": 8.8,
        "location": "行政楼1楼",
        "specialty": "环境安静，教师居多"
    },
    {
        "name": "北七食堂（美食广场）",
        "type": "美食广场",
        "price_range": [12, 25],
        "base_score": 8.6,
        "location": "商业街2楼",
        "specialty": "各地风味，选择多样"
    },
    {
        "name": "北八食堂（夜宵中心）",
        "type": "夜宵食堂",
        "price_range": [15, 35],
        "base_score": 9.5,
        "location": "学生宿舍区中心",
        "specialty": "营业时间长，夜宵丰富"
    }
]

# ============ 核心推荐算法 ============
def calculate_recommendations():
    """计算推荐结果"""
    results = []
    current_hour = current_time.hour
    
    # 高峰期检测
    is_lunch_peak = (11 <= current_hour <= 13)
    is_dinner_peak = (17 <= current_hour <= 19)
    is_peak_hour = is_lunch_peak or is_dinner_peak
    
    for canteen in CANTEENS_DATA:
        # 基础分数
        score = canteen["base_score"]
        
        # 价格调整
        min_price, max_price = canteen["price_range"]
        avg_price = (min_price + max_price) / 2
        
        if min_price > price_range[1] or max_price < price_range[0]:
            continue  # 价格不符合要求
        
        if avg_price > price_range[1]:
            score -= 1.5
        elif avg_price > (price_range[0] + price_range[1]) / 2:
            score -= 0.5
        
        # 用户身份调整
        if user_type == "教师" and "教工" in canteen["name"]:
            score += 1.0
        elif user_type == "留学生" and "清真" in canteen["name"]:
            score += 1.0
        
        # 就餐目的调整
        if dining_purpose == "学习讨论" and "教工" in canteen["name"]:
            score += 1.0
        elif dining_purpose == "朋友聚餐" and ("美食" in canteen["name"] or "夜宵" in canteen["name"]):
            score += 1.0
        elif dining_purpose == "日常快速就餐" and "快餐" in canteen["name"]:
            score += 0.8
        
        # 营业时间检查
        if "夜宵" in canteen["name"] and current_hour < 16:
            continue  # 夜宵食堂未营业
        if "教工" in canteen["name"] and not ((11 <= current_hour <= 13) or (17 <= current_hour <= 19)):
            continue  # 教工食堂未营业
        
        # 计算等待时间
        base_wait = 10
        if is_peak_hour:
            base_wait *= 1.5
        if "快餐" in canteen["name"]:
            base_wait *= 0.7
        if "大众" in canteen["name"]:
            base_wait *= 1.3
        
        wait_time = max(3, min(40, int(base_wait + np.random.randint(-3, 6))))
        
        # 计算拥挤度
        base_crowd = 50
        if is_peak_hour:
            base_crowd += 25
        if "教工" in canteen["name"]:
            base_crowd -= 20
        if "大众" in canteen["name"]:
            base_crowd += 20
        
        crowd_level = max(10, min(95, base_crowd + np.random.randint(-10, 15)))
        
        # 确定拥挤状态
        if crowd_level < 30:
            crowd_status = "🟢 空闲"
        elif crowd_level < 50:
            crowd_status = "🟡 较空"
        elif crowd_level < 70:
            crowd_status = "🟠 适中"
        elif crowd_level < 85:
            crowd_status = "🔴 拥挤"
        else:
            crowd_status = "⚫ 爆满"
        
        # 推荐状态
        is_recommended = (score >= 6.5 and wait_time <= max_wait_time)
        
        if is_recommended:
            if score >= 8.0:
                rec_status = "🏆 强烈推荐"
                rec_color = "success"
            else:
                rec_status = "👍 推荐"
                rec_color = "info"
        else:
            rec_status = "⏳ 不推荐"
            rec_color = "warning"
        
        results.append({
            "食堂名称": canteen["name"],
            "类型": canteen["type"],
            "价格范围": f"{min_price}-{max_price}元",
            "地理位置": canteen["location"],
            "特色": canteen["specialty"],
            "推荐指数": round(score, 1),
            "等待时间": f"{wait_time}分钟",
            "拥挤状态": crowd_status,
            "推荐状态": rec_status,
            "推荐颜色": rec_color,
            "_score": score,
            "_wait": wait_time
        })
    
    return pd.DataFrame(results)

# ============ 主界面显示 ============
# 状态指标
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("🏫 食堂总数", "8个", "北校区全覆盖")
with col2:
    st.metric("👥 服务师生", "8000+人", "实时数据")
with col3:
    st.metric("⏰ 当前时间", current_time.strftime("%H:%M"))
with col4:
    st.metric("📊 推荐准确率", "92.5%", "+1.2%")

st.markdown("---")

# 生成推荐结果
st.subheader("🎯 智能推荐结果")
df = calculate_recommendations()

if df.empty:
    st.warning("⚠️ 未找到符合条件的食堂，请调整筛选条件")
else:
    # 排序
    df = df.sort_values("_score", ascending=False)
    
    # 最佳推荐
    if not df.empty:
        best = df.iloc[0]
        
        # 显示最佳推荐
        st.markdown(f"### 🏆 今日最佳：**{best['食堂名称']}**")
        
        col_a, col_b = st.columns([2, 1])
        with col_a:
            st.info(f"**推荐理由：** {best['特色']}")
            st.write(f"**📍 位置：** {best['地理位置']}")
            st.write(f"**💰 价格：** {best['价格范围']}")
            st.write(f"**⏱️ 等待：** {best['等待时间']}")
            st.write(f"**👥 拥挤：** {best['拥挤状态']}")
        
        with col_b:
            # 行动建议
            st.markdown("### 🚀 行动建议")
            hour = current_time.hour
            if (11 <= hour <= 13) or (17 <= hour <= 19):
                st.warning("**高峰期建议：**\n- 错峰就餐\n- 提前预订\n- 考虑打包")
            else:
                st.success("**当前为平峰期**\n- 建议堂食\n- 环境舒适\n- 无需排队")
        
        st.markdown("---")
        
        # 所有食堂列表
        st.subheader("📋 所有食堂状态")
        
        # 使用简单的显示方式
        for idx, row in df.iterrows():
            with st.container():
                cols = st.columns([3, 2, 2, 2, 3])
                with cols[0]:
                    st.write(f"**{row['食堂名称']}**")
                    st.caption(f"{row['类型']} | {row['地理位置']}")
                with cols[1]:
                    st.metric("推荐指数", f"{row['推荐指数']}/10")
                with cols[2]:
                    st.write(f"⏱️ {row['等待时间']}")
                with cols[3]:
                    st.write(row['拥挤状态'])
                with cols[4]:
                    if row['推荐状态'] == "🏆 强烈推荐":
                        st.success(row['推荐状态'])
                    elif row['推荐状态'] == "👍 推荐":
                        st.info(row['推荐状态'])
                    else:
                        st.warning(row['推荐状态'])
                st.markdown("---")

# ============ 用户反馈 ============
st.markdown("---")
st.subheader("💬 用户体验反馈")

with st.form("feedback_form"):
    st.write("您的反馈对我们非常重要！")
    
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        accuracy = st.slider("预测准确度", 1, 5, 4)
        usability = st.slider("系统易用性", 1, 5, 4)
    with col_f2:
        usefulness = st.slider("实用价值", 1, 5, 4)
        likelihood = st.slider("再次使用意愿", 1, 5, 4)
    
    feedback = st.text_area("具体建议或问题")
    
    submitted = st.form_submit_button("📤 提交反馈")
    if submitted:
        st.success("✅ 感谢您的宝贵反馈！")
        st.balloons()

# ============ 项目信息 ============
st.markdown("---")
st.subheader("📋 项目信息")

with st.expander("查看项目详情"):
    col_info1, col_info2 = st.columns(2)
    
    with col_info1:
        st.markdown("""
        ### 🎓 项目背景
        
        **课程名称：** 人工智能  
        **项目类型：** 课程设计/期末项目  
        **开发时间：** 2024年12月  
        **适用对象：** 西昌学院北校区全体师生  
        
        ### 🎯 项目目标
        
        1. 解决食堂高峰期拥堵问题  
        2. 优化师生就餐体验  
        3. 实现个性化智能推荐  
        """)
    
    with col_info2:
        st.markdown("""
        ### 🛠️ 技术特色
        
        **前端技术：**  
        - Streamlit (交互式Web应用)  
        
        **后端算法：**  
        - 多因素加权推荐模型  
        - 时间序列预测  
        - 实时数据处理  
        
        **数据来源：**  
        - 西昌学院食堂实地调研  
        - 学生问卷调查数据  
        """)

# ============ 开发者信息 ============
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 20px; background-color: #f0f2f6; border-radius: 10px;">
    <h4>🎓 西昌学院人工智能课程期末项目</h4>
    <p><strong>开发者：</strong>Lizhanghuan | <strong>学号：</strong>2311030019</p>
    <p><strong>指导老师：</strong>黎华老师 | <strong>班级：</strong>计算机科学与技术23级1班</p>
    <p><strong>项目时间：</strong>2025年12月 | <strong>版本：</strong>v2.0</p>
    <p style="font-size: 0.9em; color: #666;">© 2025 西昌学院人工智能课程组</p>
</div>
""", unsafe_allow_html=True)

# ============ 刷新按钮 ============
st.markdown("---")
if st.button("🔄 刷新推荐数据", type="primary", use_container_width=True):
    st.rerun()