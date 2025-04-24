import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

## Edited on 2025/4/24 by Yuki

# Has to be first command
st.set_page_config(
    page_title="Histogram Explorer",
    layout="centered",
)
st.title("Histogram Explorer")

## Keep menu without default colorful bar at the top
st.markdown(
    """
        <style>
            [data-testid="stDecoration"] {
                background: #FFFFFF;
            }
        </style>
    """,
    unsafe_allow_html=True,
)

# 上传文件模块
uploaded_file = st.file_uploader("Upload a data file (CSV or xlsx)", type=["xlsx", "csv"]) 

if uploaded_file:
    # 读取数据模块
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file) # 根据文件后缀读取CSV或Excel文件
    st.success("✅ File uploaded successfully!") # 绿色成功提示框
    st.write("Data Preview:", df.head()) # 显示数据预览
    
    # 让用户选择画图所需的字段
    st.markdown("### Multi-Field Filter Panel")
    numeric_fields = df.select_dtypes(include=[np.number]).columns.tolist() # 选择数值型字段
    categorical_fields = df.select_dtypes(include=['object']).columns.tolist() # 选择字符串型字段
    
    select_col = st.selectbox("Select fields to count:", options=numeric_fields) # 选择绘制直方图的数值型字段，single-select
    
    select_fields = st.multiselect("Select fields to filter by:", options=categorical_fields) # multi-select
    group_field = st.selectbox(
        "Select field to group by (optional):", 
        options=[i for i in categorical_fields if i not in select_fields]
    ) # 选择分组字段，single-select
    group_field = group_field or None # 如果没有选择分组字段，则设置为None
    
    bin_count = st.slider("Choose the number of bins", min_value=5, max_value=100, value=20) # 选择箱数，slider
    
    
    if select_fields and select_col:
        cols = st.columns(2) # 创建两列布局
        filters = {}
        
        for i, field in enumerate(select_fields):
            with cols[i % 2]:
                col_options = df[field].drop_duplicates().sort_values(ascending=True) # 获取选项
                selected_options = st.multiselect(f"Filter {field}", options=col_options, default=col_options[0]) # multi-select
                filters[field] = selected_options # 将选项存入字典
                if set(selected_options) != set(col_options):
                    all_selected = False # 如果没有选择所有选项，则设置为False
        
        # 应用筛选
        filtered_df = df.copy() # 复制数据
        for field, values in filters.items():
            filtered_df = filtered_df[filtered_df[field].isin(values)]
            
        if filtered_df.empty:
            st.warning("No data available for the selected filters.")
            
        elif group_field==None:
            # 没有选择分组字段，即全选
            st.markdown("#### Overall Screen Time Distribution")
            fig, ax = plt.subplots(figsize=(14, 8)) # 创建图表对象
            sns.histplot(filtered_df[select_col], bins=bin_count, kde=True, ax=ax) 
            st.pyplot(fig) # 显示图表 
            
        elif group_field:
            st.markdown("#### Screen Time Distribution Group By " + group_field)
            group_values = filtered_df[group_field].drop_duplicates().sort_values(ascending=True).tolist() # 获取分组字段的选项
            
            # 判断有多少行多少列（每行两个）
            rows = (len(group_values)+1)//2
            cols = 2 if len(group_values) % 2 == 0 else 1
            
            # 绘制直方图
            fig, axs = plt.subplots(
                nrows=rows,
                ncols=cols,
                figsize=(14, 4*rows), # 根据行数调整图表高度
            )
            
            # axs.flatten() 是把二维坐标轴对象拉平成一维列表，好用循环遍历每个子图
            axs = axs.flatten() # 展平多维数组为一维数组
            
            # kde：在直方图上额外叠加一条平滑的曲线（Kernel Density Estimation），也叫核密度估计曲线。常出现在用 Seaborn 或 Pandas 画直方图的时候
            for i, value in enumerate(group_values):
                ax = axs[i]
                data = filtered_df[(filtered_df[group_field]==value)][select_col]
                sns.histplot(data.dropna(), bins=bin_count, kde=True, ax=ax) 
                ax.set_title(f"{value}")
                
            st.pyplot(fig) # 显示图表 
            plt.tight_layout(
                pad=3.0,
                h_pad=4.0,
                w_pad=1.5,
            ) # 调整子图之间的间距，防止第二排的图表标题和第一排的xlabel重合
           
