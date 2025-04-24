import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

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
    
    select_fields = st.multiselect("Select fields to filter by:", options=categorical_fields, default = categorical_fields) # multi-select
    select_col = st.selectbox("Select fields to count:", numeric_fields) # 选择绘制直方图的字段，single-select
    group_field = st.selectbox("Select field to group by:", categorical_fields) # 选择分组字段，single-select
    
    bin_count = st.slider("Choose number of bins", min_value=5, max_value=100, value=20) # 选择箱数，slider
    if select_col:
        cols = st.columns(2) # 创建两列布局
        filters = {}
        
        for i, field in enumerate(select_fields):
            with cols[i % 2]:
                options = df[field].drop_duplicates().sort_values(ascending=True) # 获取选项
                selected_options = st.multiselect(f"Select {field}", options=options, default=options) # multi-select
                filters[field] = selected_options # 将选项存入字典
        
        # 过滤数据
        filtered_df = df.copy() # 复制数据
        for field, selected_options in filters.items():
            filtered_df = filtered_df[filtered_df[field].isin(selected_options)]
            
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
        plt.tight_layout(
            pad=3.0,
            h_pad=4.0,
            w_pad=1.5,
        ) # 调整子图之间的间距，防止第二排的图表标题和第一排的xlabel重合
        
        # axs.flatten() 是把二维坐标轴对象拉平成一维列表，好用循环遍历每个子图
        axs = axs.flatten() # 展平多维数组为一维数组
        
        # kde：在直方图上额外叠加一条平滑的曲线（Kernel Density Estimation），也叫核密度估计曲线。常出现在用 Seaborn 或 Pandas 画直方图的时候
        for i, value in enumerate(group_values):
            ax = axs[i]
            data = filtered_df[(filtered_df[group_field]==value)][select_col]
            sns.histplot(data.dropna(), bins=bin_count, kde=True, ax=ax) 
            ax.set_title(f"{value}")
            
        st.pyplot(fig) # 显示图表    
    