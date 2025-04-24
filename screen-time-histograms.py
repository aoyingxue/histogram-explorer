import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

# Has to be first command
st.set_page_config(
    page_title="Teen Screen Time Histograms",
    layout="centered",
)
st.title("Teen Screen Time")

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
uploaded_file = st.file_uploader("Upload a CSV file", type=["xlsx", "csv"]) 

if uploaded_file:
    # 读取数据模块
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file) # 根据文件后缀读取CSV或Excel文件
    st.success("✅ File uploaded successfully!") # 绿色成功提示框
    st.write("Data Preview:", df.head()) # 显示数据预览
    
    # 让用户选择画图所需的字段
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist() # 选择数值型字段
    if numeric_cols:
        # 滑块和筛选器，分两列放置
        col1, col2 = st.columns(2)
        with col1:
            age_options = df['Age_Group'].drop_duplicates().sort_values(ascending=True) # 获取年龄选项
            age_range = st.multiselect("Select Age Group", options=age_options, default = age_options) # 选择年龄范围，multi-select
            gender_options = df['Gender'].dropna().unique().tolist() # 获取性别选项
            selected_gender = st.multiselect("Select Gender", options = gender_options, default=gender_options) # 选择性别，multi-select
            
        with col2:
            select_cols = st.selectbox("Select ", numeric_cols) # 选择绘制直方图的字段，box
            bin_count = st.slider("选择直方图的箱数", min_value=5, max_value=100, value=20) # 选择箱数，slider
            
        # 获取设备类型选项
        device_types = df['Device_Type'].drop_duplicates().sort_values(ascending=True).tolist() 
        
        # 过滤数据
        filtered_df = df[
            (df['Age_Group'].isin(age_range)) &
            (df['Gender'].isin(selected_gender))
        ]
        
        # 绘制直方图
        fig, axs = plt.subplots(
            nrows=2,
            ncols=2,
            figsize=(12, 10),
        )
        plt.tight_layout(
            pad=3.0,
            h_pad=4.0,
            w_pad=1.5,
        ) # 调整子图之间的间距，防止第二排的图表标题和第一排的xlabel重合
        
        # axs.flatten() 是把二维坐标轴对象拉平成一维列表，好用循环遍历每个子图
        axs = axs.flatten() # 展平多维数组为一维数组
        
        # kde：在直方图上额外叠加一条平滑的曲线（Kernel Density Estimation），也叫核密度估计曲线。常出现在用 Seaborn 或 Pandas 画直方图的时候
        for i, device in enumerate(device_types):
            ax = axs[i]
            data = filtered_df[(filtered_df["Device_Type"]==device)]['Weekly_Screen_Time_Hours']
            sns.histplot(data.dropna(), bins=bin_count, kde=True, ax=ax) 
            ax.set_title(f"{device}")
            ax.set_xlabel("Weekly Screen Time (Hours)")
            ax.set_ylabel("Number of Teens")
            
        st.pyplot(fig) # 显示图表
        