import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

################### import #################
day_df = pd.read_csv("dashboard/day_df_final.csv")
day_df["dteday"] = pd.to_datetime(day_df["dteday"])
hour_df = pd.read_csv("dashboard/hour_df_final.csv")
hour_df["dteday"] = pd.to_datetime(hour_df["dteday"])
############################################

min_date = day_df["dteday"].min()
max_date = day_df["dteday"].max()



########################## main app ##################

st.header('Dashboard Bike Sharing :bike:')

st.subheader('this dashboard provide information about data bike sharing')

with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[pd.to_datetime("2012-5-1"), pd.to_datetime("2012-5-31")]
    )
    day_df_filtered = day_df[(day_df["dteday"] >= str(start_date)) & 
                    (day_df["dteday"] <= str(end_date))]
    hour_df_filtered = hour_df[(hour_df["dteday"] >= str(start_date)) & 
                    (hour_df["dteday"] <= str(end_date))]


#################### data filter #####################

def get_daily_rentals(df):
    """Menghitung total peminjaman harian."""
    return df.groupby("dteday", as_index=False).agg({"cnt": "sum", "holiday": "first"})

def get_daily_rentals_registered(df):
    """Menghitung jumlah peminjam terdaftar vs biasa berdasarkan hari."""
    return df.groupby("dteday", as_index=False).agg({
        "casual": "sum",
        "registered": "sum",
        "holiday": "first"
    })

def get_monthly_rentals(df):
    """Menghitung total peminjaman berdasarkan bulan."""
    return df.groupby(df["dteday"].dt.strftime("%B"))["cnt"].sum().reset_index()

def get_hourly_rentals(df):
    """Menghitung total peminjaman berdasarkan jam."""
    hourly_rentals = df.groupby("hr")["cnt"].sum().reset_index()
    hourly_rentals["hr"] = hourly_rentals["hr"].astype(str)  # Konversi ke string
    return hourly_rentals.sort_values(by="cnt", ascending=False)

def get_seasonly_rentals(df):
    # menganalisa jumlah pengguna berdasarkan musim
    sharing_season_df = df.groupby("season").cnt.sum().reset_index()
    sharing_season_df = sharing_season_df.sort_values(by="cnt", ascending=False)
    return sharing_season_df

def get_wheatersit_rentals(df):
    # menganalisa jumlah pengguna berdasarkan cuaca
    sharing_weathersit_df = df.groupby("weathersit").cnt.sum().reset_index()
    sharing_weathersit_df = sharing_weathersit_df.sort_values(by="cnt", ascending=False)
    return  sharing_weathersit_df

def get_season_workingday(df):
    season_workingday = df.groupby(["season", "workingday"]).agg({
        "casual": "sum",
        "registered": "sum",
        "cnt": "sum"
    }).reset_index()

    return season_workingday

def get_holiday_rentals(df):
    # menghitung perbedaan jumlah peminjam saat hari libur nasional (holiday)
    holiday_df = df.groupby('holiday').agg({
        "instant" : "count", # total hari
        "cnt" : ["sum", "max", "min", "mean"] # analisis total peminjam
    })
    return holiday_df

def get_time_category(df):
    # Menghitung total peminjam berdasarkan jam
    time_category = hour_df.copy()
    # Fungsi untuk mengelompokkan jam ke dalam kategori waktu
    def categorize_time(hour):
        if 5 <= hour <= 10:
            return "Pagi"
        elif 11 <= hour <= 15:
            return "Siang"
        elif 16 <= hour <= 18:
            return "Sore"
        else:
            return "Malam"

    # Tambahkan kolom kategori waktu
    time_category["time_category"] = time_category["hr"].apply(categorize_time)
    return time_category

# Filtered Variable
daily_rentals = get_daily_rentals(day_df_filtered)
daily_rentals_registered = get_daily_rentals_registered(day_df_filtered)
monthly_rentals = get_monthly_rentals(day_df)
sum_sharing_hour_df = get_hourly_rentals(hour_df_filtered)
sum_sharing_season_df = get_seasonly_rentals(day_df)
sum_sharing_weathersit_df_alldata = get_wheatersit_rentals(hour_df)
sum_sharing_weathersit_df = get_wheatersit_rentals(hour_df_filtered)
season_workingday_df = get_season_workingday(day_df)
sum_holiday_df = get_holiday_rentals(day_df_filtered)
time_category_df = get_time_category(day_df_filtered)

# ----------------------------------------------------------------------------------------------------


############# Grafik 1 Tren Berdasarkan Range ###############

st.subheader(f"Tren Peminjaman Sepeda ({start_date.strftime('%d %B %Y')} - {end_date.strftime('%d %B %Y')})")

# Plot hasilnya menggunakan Streamlit
fig, ax = plt.subplots(figsize=(14, 6))

# Line chart
sns.lineplot(x="dteday", y="cnt", data=daily_rentals, marker="o", linewidth=2.0, color="c", ax=ax)

# Tambahkan titik merah untuk hari libur nasional
non_working_days = daily_rentals[daily_rentals["holiday"] == "Yes"]
ax.scatter(non_working_days["dteday"], non_working_days["cnt"], color="red", s=80, label="Hari Libur Nasional")

# Tambahkan keterangan
ax.set_xlabel("Tanggal")
ax.set_ylabel("Total Peminjaman")
ax.set_title(f"Tren Peminjaman Sepeda dari {start_date.strftime('%d %B %Y')} sampai {end_date.strftime('%d %B %Y')}")
ax.tick_params(axis="x", rotation=45)
ax.grid(True)
ax.legend()

# Tampilkan plot di Streamlit
st.pyplot(fig)


############# Grafik 2 Tren Berdasarkan Range Member atau Bukan ###############

fig, ax = plt.subplots(figsize=(14, 6))

# Membuat line chart
sns.lineplot(x="dteday", y="casual", data=daily_rentals_registered, marker="o", linewidth=2.0, color="r", label="Casual Users", ax=ax)
sns.lineplot(x="dteday", y="registered", data=daily_rentals_registered, marker="o", linewidth=2.0, color="b", label="Registered Users", ax=ax)

# Menambahkan titik merah untuk hari libur nasional
non_working_days = daily_rentals_registered[daily_rentals_registered["holiday"] == "Yes"]
ax.scatter(non_working_days["dteday"], non_working_days["casual"], color="red", s=80, label="Hari Libur Nasional (Casual)")
ax.scatter(non_working_days["dteday"], non_working_days["registered"], color="darkred", s=80, label="Hari Libur Nasional (Registered)")

# Menambah keterangan label x sebagai tanggal dan y adalah total peminjaman
ax.set_xlabel("Tanggal")
ax.set_ylabel("Total Peminjaman")
ax.set_title(f"Tren Peminjaman Sepeda dari {start_date.strftime('%d %B %Y')} sampai {end_date.strftime('%d %B %Y')}")
ax.tick_params(axis="x", rotation=45)
ax.grid(True)
ax.legend()

# Menampilkan plot di Streamlit
st.pyplot(fig)



############# Grafik 3 Tren Berdasarkan Bulan ###############
# Urutan Bulan
month_order = ['January', 'February', 'March', 'April', 'May', 'June', 
               'July', 'August', 'September', 'October', 'November', 'December']

# Mengurutkan bulan dengan benar
monthly_rentals["dteday"] = pd.Categorical(monthly_rentals["dteday"], categories=month_order, ordered=True)
monthly_rentals = monthly_rentals.sort_values("dteday")

# Streamlit layout
st.subheader("Total Peminjaman Sepeda Berdasarkan Bulan (2011-2012)")

fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(x="dteday", y="cnt", data=monthly_rentals, hue="cnt", palette="rocket", ax=ax)

ax.set_xlabel("Bulan")
ax.set_ylabel("Total Peminjaman")
ax.set_title("Total Peminjaman Sepeda Berdasarkan Bulan (2011-2012) (total)")
ax.tick_params(axis='x', rotation=45)

st.pyplot(fig)


############# Grafik 4 Perform Share Berdasarkan Jam ###############

st.subheader("Analisis Peminjaman Sepeda Berdasarkan Jam")

# Membuat plot
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(24, 6))

colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot(
    x="cnt", y="hr", data=sum_sharing_hour_df.head(5), 
    hue="hr", palette=colors, legend=False, ax=ax[0]
)
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("Best Performing Hour", loc="center", fontsize=15)
ax[0].tick_params(axis='y', labelsize=12)

sns.barplot(
    x="cnt", y="hr", 
    data=sum_sharing_hour_df.sort_values(by="cnt", ascending=True).head(5),
    hue="hr", palette=colors, legend=False, ax=ax[1]
)
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Worst Performing Hour", loc="center", fontsize=15)
ax[1].tick_params(axis='y', labelsize=12)

plt.suptitle(f"Best and Worst Performing Hour ({start_date.strftime('%d %B %Y')} - {end_date.strftime('%d %B %Y')})", fontsize=20)

# Tampilkan plot di Streamlit
st.pyplot(fig)


st.subheader("Analisis Peminjaman Sepeda Berdasarkan Season (2011-2012)")
############# Grafik 5 Jumlah Share Berdasarkan Season ###############
fig, ax = plt.subplots(figsize=(10, 6))
ax = sns.barplot(x='season', y='cnt', data=sum_sharing_season_df, hue='season', palette='coolwarm')

ax.set_title("Ranking Jumlah Peminjam Berdasarkan Musim (2011-2012)")
ax.set_xlabel("Season")
ax.set_ylabel("Total Peminjaman")

# Tambahkan label jumlah di atas tiap bar
for p in ax.patches:
    ax.annotate(f'{p.get_height()}', (p.get_x() + 0.4, p.get_height() + 150), ha='center')

st.pyplot(fig)


st.subheader("Analisis Peminjaman Sepeda Berdasarkan Cuaca")
############# Grafik 6 Jumlah Share Berdasarkan Cuaca 2011-2012 ###############

fig, ax = plt.subplots(figsize=(10, 6))
ax = sns.barplot(x='weathersit', y='cnt', data=sum_sharing_weathersit_df_alldata, hue='weathersit', palette='coolwarm')

ax.set_title(f"Ranking Jumlah Peminjam Berdasarkan Cuaca (2011-2012)")
ax.set_xlabel("Cuaca")
ax.set_ylabel("Total Peminjaman")

# Tambahkan label jumlah di atas tiap bar
for p in ax.patches:
    ax.annotate(f'{p.get_height()}', (p.get_x() + 0.4, p.get_height() + 150), ha='center')

st.pyplot(fig)


############# Grafik 7 Jumlah Share Berdasarkan Cuaca range waktu ###############

fig, ax = plt.subplots(figsize=(10, 6))
ax = sns.barplot(x='weathersit', y='cnt', data=sum_sharing_weathersit_df, hue='weathersit', palette='coolwarm')

ax.set_title(f"Ranking Jumlah Peminjam Berdasarkan Cuaca ({start_date.strftime('%d %B %Y')} - {end_date.strftime('%d %B %Y')})")
ax.set_xlabel("Cuaca")
ax.set_ylabel("Total Peminjaman")

# Tambahkan label jumlah di atas tiap bar
for p in ax.patches:
    ax.annotate(f'{p.get_height()}', (p.get_x() + 0.4, p.get_height() + 150), ha='center')

st.pyplot(fig)


st.subheader("Analisis Peminjaman Sepeda Berdasarkan Musim dan Hari Kerja")
############# Grafik 8 Jumlah Share Berdasarkan Musim dan Hari Kerja ###############

# Membuat bar chart
fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(
    x="season", y="cnt", hue="workingday",
    data=season_workingday_df, palette=["#FF9999", "#66B3FF"], ax=ax
)

# Menambahkan label dan judul
ax.set_xlabel("Musim")
ax.set_ylabel("Total Peminjaman")
ax.set_title("Total Peminjaman Sepeda Berdasarkan Musim dan Hari Kerja (2011-2012)")
ax.legend(title="Hari")
ax.grid(axis="y", linestyle="--", alpha=0.7)  # Menambahkan grid agar lebih rapi

# Menampilkan plot di Streamlit
st.pyplot(fig)


st.subheader(f"Total Peminjaman Hari Libur Nasional ({start_date.strftime('%d %B %Y')} - {end_date.strftime('%d %B %Y')})")
############# Grafik 9 Jumlah Share Berdasarkan hari libur nasional atau bukan ###############
fig, ax = plt.subplots(figsize=(8, 6))
sns.boxplot(x="holiday", y="cnt", data=day_df_filtered, hue="holiday", palette=["gray", "red"], ax=ax)
ax.set_xlabel("Hari Libur Nasional")
ax.set_ylabel("Total Peminjaman")
ax.set_title("Perbandingan Peminjaman Sepeda Saat Hari Libur Nasional vs Bukan")
ax.grid(True)
st.pyplot(fig)


############# Grafik 9 Jumlah Share Berdasarkan hari libur nasional atau bukan ###############
st.subheader(f"Total Peminjaman di Kategori Waktu ({start_date.strftime('%d %B %Y')} - {end_date.strftime('%d %B %Y')})")
# Tentukan urutan kategori waktu
time_order = ["Pagi", "Siang", "Sore", "Malam"]

# Ubah kolom 'time_category' menjadi kategori terurut
time_category_df["time_category"] = pd.Categorical(
    time_category_df["time_category"], categories=time_order, ordered=True
)

# Buat plot
fig, ax = plt.subplots(figsize=(8, 6))
sns.boxplot(x="time_category", y="cnt", data=time_category_df, hue="time_category", palette=["c", "b", "orange", "gray"], ax=ax)
ax.set_xlabel("Kategori Waktu")
ax.set_ylabel("Total Peminjaman")
ax.set_title("Perbandingan Peminjaman Sepeda Di Waktu Tertentu")
ax.grid(True)

# Tampilkan plot di Streamlit
st.pyplot(fig)


st.caption('copyright (c) pramudya 2025')