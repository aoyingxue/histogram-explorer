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
    # layout="wide", # 让页面宽度最大化
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

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False 

# 绘图模块
def plot_histogram(data, ax, bin_count):
    sns.histplot(data.dropna(), bins=bin_count, kde=True, ax=ax) 
    counts, bins = np.histogram(data.dropna(), bins=bin_count) # 计算直方图的频数和区间
    for count, bin_left, bin_right in zip(counts, bins[:-1], bins[1:]):
        ax.text(
            (bin_left + bin_right) / 2, # 计算区间中点
            count,
            str(count),
            ha='center',
            va='bottom',
            fontsize=10,
        ) # 在直方图上添加频数标签
    ax.set_xticks(bins[::max(1, len(bins)//10)]) # 每10步算1个step，max用来确保步长至少为 1
    ax.set_xticklabels([f"{b:.0f}" for b in bins[::max(1, len(bins)//10)]]) # 约合到整数的label
    return ax

# 上传文件模块
# 是否让用户自行选择默认数据还是自己上传数据
option = st.radio(
    "Choose data source:",
    ['Use sample data *(Teens Screen Time Mock Data by Back 2 Viz Basic)*', 'Upload your own data file'],
    index=0, # 默认选项
)

uploaded_file = None
# File uploader only shown if user selects "Upload"
if option == 'Upload your own data file':
    uploaded_file = st.file_uploader("Upload a data file (CSV or xlsx)", type=["xlsx", "csv"]) 
    
@st.cache_data
def get_data(source_option, uploaded_file):
    if source_option == 'Use sample data *(Teens Screen Time Mock Data by Back 2 Viz Basic)*':
        # 使用默认数据
        df = pd.read_csv("https://github.com/aoyingxue/histogram-explorer/blob/main/data/teen_screen_time_mock_dataset.csv") # 读取数据
    else:
        if uploaded_file is not None:
            # 读取用户上传的数据
            df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
    return df

df = pd.DataFrame()
if option == 'Use sample data *(Teens Screen Time Mock Data by Back 2 Viz Basic)*':
    df = get_data(option, uploaded_file)
    st.success("Sample data loaded successfully!")
elif uploaded_file is not None:
    df = get_data(option, uploaded_file)
    st.success("File uploaded successfully!")
    st.write("Data Preview:", df.head()) # 显示数据预览

if df.shape[0]>0: 
    # 让用户选择画图所需的字段
    st.markdown("### Multi-Field Filter Panel")
    numeric_fields = df.select_dtypes(include=[np.number]).columns.tolist() # 选择数值型字段
    categorical_fields = df.select_dtypes(include=['object']).columns.tolist() # 选择字符串型字段

    select_col = st.selectbox("Select fields to count:", options=numeric_fields) # 选择绘制直方图的数值型字段，single-select
    select_fields = st.multiselect("Select fields to filter by:", options=categorical_fields) # multi-select

    group_field = st.selectbox(
        "Select field to group by (optional):", 
        options=[i for i in categorical_fields if i not in select_fields]+["None"]
    ) # 选择分组字段，single-select
    if group_field == "None": # 如果选择了None，则设置为None
        group_field = None # 设置为None

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
            
        else:
            if group_field == None:
                # 没有选择分组字段，即全选
                st.markdown("#### Overall Distribution")
                fig, ax = plt.subplots(figsize=(14, 8)) # 创建图表对象
                data = filtered_df[select_col]
                plot_histogram(data, ax, bin_count)  # 使用提取出来的函数来绘图
                st.pyplot(fig) # 显示图表 
                
            else:
                # 如果选择了分组字段
                st.markdown("#### Distribution Group By " + group_field)
                group_values = filtered_df[group_field].drop_duplicates().sort_values(ascending=True).tolist() # 获取分组字段的选项

                # 判断有多少行多少列（每行两个）
                cols = 2
                rows = (len(group_values)+1)//2 # 计算行数，确保够用
                            
                fig, axs = plt.subplots(
                    nrows=rows,
                    ncols=cols,
                    figsize=(14, 6*rows), # 根据行数调整图表高度
                )
                
                # axs.flatten() 是把二维坐标轴对象拉平成一维列表，好用循环遍历每个子图
                axs = axs.flatten() # 展平多维数组为一维数组
                
                for i, value in enumerate(group_values):
                    ax = axs[i]
                    data = filtered_df[(filtered_df[group_field]==value)][select_col]
                    ax = plot_histogram(data, ax, bin_count)  # 使用提取出来的函数来绘图
                    ax.set_title(f"{value}", fontsize=16)
                
                # 隐藏多余的子图
                for j in range(i+1, len(axs)):
                    axs[j].axis('off') 
                    
                plt.tight_layout(
                    pad=3.0,
                    h_pad=4.0,
                    w_pad=1.5,
                ) # 调整子图之间的间距，防止第二排的图表标题和第一排的xlabel重合
                st.pyplot(fig) # 显示图表


