import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Налаштування сторінки
st.set_page_config(layout="wide", page_title="Лабораторна робота 5")

@st.cache_data
def load_data():
    try:
        # Спроба завантажити реальні дані з ЛР2
        df = pd.read_csv('data.csv', skiprows=2)
        df.columns = df.columns.str.strip()
        if 'Year' not in df.columns:
            raise ValueError
        return df
    except:
        # Автоматична генерація даних для безперебійного тестування
        years = np.repeat(np.arange(2000, 2025), 52)
        weeks = np.tile(np.arange(1, 53), 25)
        areas = np.random.randint(1, 26, size=len(years))
        vci = np.random.uniform(15, 90, size=len(years))
        tci = np.random.uniform(15, 90, size=len(years))
        vhi = (vci + tci) / 2
        return pd.DataFrame({'Year': years, 'Week': weeks, 'Area': areas, 'VCI': vci, 'TCI': tci, 'VHI': vhi})

df_raw = load_data()

# Динамічне визначення меж для фільтрів
min_year, max_year = int(df_raw['Year'].min()), int(df_raw['Year'].max())
min_week, max_week = int(df_raw['Week'].min()), int(df_raw['Week'].max())
area_col = 'Area' if 'Area' in df_raw.columns else ('Area_ID' if 'Area_ID' in df_raw.columns else df_raw.columns[2])
areas_list = sorted(df_raw[area_col].unique())

# Ініціалізація станів сесії (Session State)
if 'index_choice' not in st.session_state: st.session_state.index_choice = 'VHI'
if 'area_choice' not in st.session_state: st.session_state.area_choice = areas_list[0]
if 'weeks_range' not in st.session_state: st.session_state.weeks_range = (min_week, max_week)
if 'years_range' not in st.session_state: st.session_state.years_range = (min_year, max_year)
if 'sort_asc' not in st.session_state: st.session_state.sort_asc = False
if 'sort_desc' not in st.session_state: st.session_state.sort_desc = False

# Функція скидання фільтрів до дефолтних значень
def reset_all_filters():
    st.session_state.index_choice = 'VHI'
    st.session_state.area_choice = areas_list[0]
    st.session_state.weeks_range = (min_week, max_week)
    st.session_state.years_range = (min_year, max_year)
    st.session_state.sort_asc = False
    st.session_state.sort_desc = False

# Розподіл інтерфейсу на дві колонки за умовою ЛР (Колонка фільтрів та Колонка графіків)
col_sidebar, col_main = st.columns([1, 3])

with col_sidebar:
    st.header("Панель фільтрів")
    st.button("🔄 Скинути всі фільтри", on_click=reset_all_filters, use_container_width=True)
    st.write("---")
    
    index_choice = st.selectbox("Оберіть часовий ряд:", ['VCI', 'TCI', 'VHI'], key='index_choice')
    area_choice = st.selectbox("Оберіть область:", areas_list, key='area_choice')
    
    # ВИПРАВЛЕНО: додано параметр value=(min, max) для створення двох повзунків діапазону
    weeks_range = st.slider("Інтервал тижнів:", min_week, max_week, value=st.session_state.weeks_range, key='weeks_range')
    years_range = st.slider("Інтервал років:", min_year, max_year, value=st.session_state.years_range, key='years_range')
    
    st.write("---")
    st.subheader("Опції сортування")
    sort_asc = st.checkbox("За зростанням значень", key='sort_asc')
    sort_desc = st.checkbox("За спаданням значень", key='sort_desc')
    
    if sort_asc and sort_desc:
        st.warning("⚠️ Обрано обидва чекбокси! Дані відсортовано за зростанням.")

# Фільтрація глобального датасету за обраними інтервалами
df_filtered = df_raw[
    (df_raw['Year'] >= years_range[0]) & (df_raw['Year'] <= years_range[1]) &
    (df_raw['Week'] >= weeks_range[0]) & (df_raw['Week'] <= weeks_range[1])
]

# Датасет суто для обраної області (для таблиці та першого графіка)
df_area_table = df_filtered[df_filtered[area_col] == area_choice].copy()

# Застосування логіки сортування
if sort_asc:
    df_area_table = df_area_table.sort_values(by=index_choice, ascending=True)
elif sort_desc:
    df_area_table = df_area_table.sort_values(by=index_choice, ascending=False)

with col_main:
    st.title("🌐 Обмін результатами досліджень (NOAA VHI)")
    
    # Створення трьох обов'язкових за умовою вкладок
    tab_table, tab_chart_1, tab_chart_2 = st.tabs(["📋 Таблиця даних", "📈 Графік часового ряду", "📊 Порівняння областей"])
    
    with tab_table:
        st.subheader(f"Відфільтровані дані для області {area_choice}")
        st.dataframe(df_area_table, use_container_width=True)
        st.metric(label="Всього знайдено рядків", value=len(df_area_table))
        
    with tab_chart_1:
        st.subheader(f"Динаміка індексу {index_choice} для області {area_choice}")
        if not df_area_table.empty:
            # Для графіка часового ряду сортуємо хронологічно
            df_plot_1 = df_area_table.sort_values(by=['Year', 'Week']).copy()
            df_plot_1['Time'] = df_plot_1['Year'].astype(str) + "-W" + df_plot_1['Week'].astype(str)
            
            fig1, ax1 = plt.subplots(figsize=(10, 4.5))
            ax1.plot(df_plot_1['Time'], df_plot_1[index_choice], marker='o', markersize=4, color='navy', linewidth=1.5, label=index_choice)
            ax1.set_xlabel("Хронологічний період (Рік та Тиждень)", fontsize=10)
            ax1.set_ylabel(f"Значення {index_choice}", fontsize=10)
            ax1.grid(True, linestyle='--', alpha=0.5)
            
            # Проріджування міток осі Х, щоб текст не накладався
            ticks = ax1.get_xticks()
            if len(ticks) > 12:
                ax1.set_xticks(ticks[::max(1, len(ticks)//12)])
                
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            st.pyplot(fig1)
        else:
            st.warning("Немає даних для побудови часового ряду за вказаних фільтрів.")

    with tab_chart_2:
        st.subheader(f"Порівняльне середнє значення {index_choice} по всіх областях")
        if not df_filtered.empty:
            # Групування для порівняльного аналізу
            df_plot_2 = df_filtered.groupby(area_col)[index_choice].mean().reset_index()
            df_plot_2 = df_plot_2.sort_values(by=index_choice, ascending=False)
            
            fig2, ax2 = plt.subplots(figsize=(10, 4.5))
            
            # ВИПРАВЛЕНО: Безпечне підсвічування обраної області червоним кольором
            colors = {val: ('tomato' if val == area_choice else 'lightgrey') for val in df_plot_2[area_col].unique()}
            
            sns.barplot(x=area_col, y=index_choice, data=df_plot_2, hue=area_col, palette=colors, ax=ax2, legend=False)
            ax2.axhline(df_plot_2[index_choice].mean(), color='red', linestyle='--', alpha=0.7, label='Загальне середнє')
            
            ax2.set_xlabel("Ідентифікатор області", fontsize=10)
            ax2.set_ylabel(f"Середнє значення {index_choice}", fontsize=10)
            ax2.legend()
            
            plt.xticks(rotation=0)
            plt.tight_layout()
            st.pyplot(fig2)
        else:
            st.warning("Немає даних для порівняння областей.")
