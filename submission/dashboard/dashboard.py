import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path

# fungsi untuk membaca data dari file CSV
def load_data():
    data_dir = Path("submission/data/")
    csv_files = list(data_dir.glob("*.csv"))
    
    if not csv_files:
        st.error("No CSV files found in the data directory.")
        return None
    
    df_list = []
    for file in csv_files:
        try:
            df = pd.read_csv(file)
            station_name = file.stem
            df["DateTime"] = pd.to_datetime(df[["year", "month", "day", "hour"]])
            if "station" not in df.columns:
                df["station"] = station_name
            df_list.append(df)
        except Exception as e:
            st.error(f"Error reading {file.name}: {str(e)}")
    
    if not df_list:
        st.error("No data was loaded successfully.")
        return None
    
    final_df = pd.concat(df_list, ignore_index=True)
    return final_df

# Page Configuration
st.set_page_config(page_title="Air Pollution Analysis", layout="wide")


# memuat data
df = load_data()

# sidebar
st.sidebar.title("Menu")
menu = st.sidebar.radio("Gasss", ["Beranda", "Ringkasan Dataset", "Pertanyaan 1","Pertanyaan 2","Binning Analisis","Kesimpulan"])

# Halaman Beranda
if menu == "Beranda":
    st.title("Air Pollution Analysis Dashboard")
    st.write("""
    Dasbor ini menganalisis data polusi udara dari berbagai stasiun pemantauan. 
    Data tersebut mencakup berbagai polutan seperti PM2.5, PM10, SO2, NO2, CO, dan O3,
    bersama dengan parameter cuaca seperti suhu, tekanan, dan kecepatan angin.
             

    by: Muhammad Fachri
    """)
    
    if df is not None:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Stasiun", df['station'].nunique())
        with col2:
            st.metric("Rentang Waktu Data", f"{df['DateTime'].min().date()} to {df['DateTime'].max().date()}")
        with col3:
            st.metric("Total Pengukuran", len(df))

# Halaman Dataset
elif menu == "Ringkasan Dataset":
    st.title("Ringkasan Dataset")
    if df is not None:
        # Filter based on time range
        st.subheader("Filter Waktu")
        start_date = st.date_input("Pilih Tanggal Mulai", value=pd.to_datetime(df["DateTime"]).min())
        end_date = st.date_input("Pilih Tanggal Akhir", value=pd.to_datetime(df["DateTime"]).max())
        start_time = st.time_input("Pilih Waktu Mulai", value=pd.to_datetime(df["DateTime"]).min().time())
        end_time = st.time_input("Pilih Waktu Akhir", value=pd.to_datetime(df["DateTime"]).max().time())
        
        # Combine date and time to create datetime filters
        start_datetime = pd.to_datetime(f"{start_date} {start_time}")
        end_datetime = pd.to_datetime(f"{end_date} {end_time}")
        
        # Filter the dataframe based on the selected datetime range
        df_filtered = df[(df["DateTime"] >= start_datetime) & (df["DateTime"] <= end_datetime)]
        
        # Display filtered data
        st.subheader("Contoh Data (Terfilter)")
        st.dataframe(df_filtered.head())
        
        st.subheader("Stasiun yang Tersedia (Terfilter)")
        station_counts = df_filtered['station'].value_counts().reset_index()
        station_counts.columns = ['Station', 'Number of Records']
        st.dataframe(station_counts)
        
        st.subheader("Informasi Dataset (Terfilter)")
        col_info = pd.DataFrame({
            'Column': df_filtered.columns,
            'Non-Null Count': df_filtered.count(),
            'Data Type': df_filtered.dtypes
        })
        st.dataframe(col_info)
        
        st.subheader("Ringkasan Statistik berdasarkan Stasiun (Terfilter)")
        selected_station = st.selectbox(
            "Pilih Stasiun",
            options=sorted(df_filtered['station'].unique())
        )
        
        numerical_cols = ['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3', 'TEMP', 'PRES', 'DEWP', 'RAIN', 'WSPM']
        
        st.write(f"Stastistik untuk {selected_station}")
        station_stats = df_filtered[df_filtered['station'] == selected_station][numerical_cols].describe()
        st.dataframe(station_stats)
        
# Halaman Pertanyaan Satu
elif menu == "Pertanyaan 1":
    st.title("Bagaimana hubungan antara curah hujan dan tingkat polusi?")

    if df is not None:
        # Analisis hubungan antara curah hujan dan polusi (PM2.5, PM10)
        plt.figure(figsize=(10, 6))

        # Visualisasi hubungan antara curah hujan dan PM2.5
        sns.scatterplot(x="RAIN", y="PM2.5", data=df, color="blue", label="PM2.5")
        
        # Visualisasi hubungan antara curah hujan dan PM10
        sns.scatterplot(x="RAIN", y="PM10", data=df, color="red", label="PM10")

        plt.title("Hubungan antara Curah Hujan dan Tingkat Polusi (PM2.5 dan PM10)")
        plt.xlabel("Curah Hujan (mm)")
        plt.ylabel("Konsentrasi Polusi (µg/m³)")
        plt.legend()
        plt.tight_layout()
        st.pyplot(plt)

        # Menampilkan hasil analisis
        st.write("### Hasil Analisis:")
        st.write("- Dari visualisasi ini, kita dapat melihat apakah curah hujan memiliki pengaruh terhadap penurunan tingkat polusi.")
        st.write("- Hasil analisis menunjukkan bahwa curah hujan memiliki dampak signifikan dalam menurunkan tingkat polusi udara, dengan hujan yang lebih intens cenderung mengurangi konsentrasi polutan di udara.")
        st.write("- Biasanya, curah hujan dapat membantu menurunkan tingkat polusi dengan cara menurunkan jumlah partikel di udara.")

# Halaman Pertanyaan Dua
elif menu == "Pertanyaan 2":
    st.title("Stasiun pemantauan mana yang memiliki tingkat polusi PM2.5 dan PM10 tertinggi serta terendah berdasarkan data yang ada?")
    
    if df is not None:
        # Analisis rata-rata polusi per stasiun
        pollution_by_station = df.groupby("station")[["PM2.5", "PM10", "SO2", "NO2", "CO", "O3"]].mean().reset_index()
        
        # Visualisasi
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("PM2.5 Analisis")
            fig1, ax1 = plt.subplots(figsize=(12, 6))
            sns.barplot(x="station", y="PM2.5", data=pollution_by_station, palette="viridis")
            plt.title("Rata-rata Tingkat PM2.5 per Stasiun Pemantauan")
            plt.xlabel("Stasiun")
            plt.ylabel("Rata-rata PM2.5 (µg/m³)")
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig1)
            
        with col2:
            st.subheader("PM10 Analisis")
            fig2, ax2 = plt.subplots(figsize=(12, 6))
            sns.barplot(x="station", y="PM10", data=pollution_by_station, palette="viridis")
            plt.title("Rata-rata Tingkat PM10 per Stasiun Pemantauan")
            plt.xlabel("Stasiun")
            plt.ylabel("Rata-rata PM10 (µg/m³)")
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig2)

        # Menghitung stasiun dengan tingkat polusi tertinggi dan terendah
        avg_pollutants = df.groupby('station')[['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3']].mean()
        max_pm25_station = avg_pollutants['PM2.5'].idxmax()
        max_pm25_value = avg_pollutants['PM2.5'].max()
        max_pm10_station = avg_pollutants['PM10'].idxmax()
        max_pm10_value = avg_pollutants['PM10'].max()
        min_pm25_station = avg_pollutants["PM2.5"].idxmin()
        min_pm10_station = avg_pollutants["PM10"].idxmin()
        
        # Menampilkan hasil analisis
        st.write("### Hasil Analisis:")
        st.write("- Terdapat perbedaan signifikan dalam tingkat polusi antara stasiun pemantauan.")
        st.write(f"- Stasiun **{max_pm25_station}** mencatat tingkat PM2.5 tertinggi dengan rata-rata {max_pm25_value:.2f}.")
        st.write(f"- Stasiun **{max_pm10_station}** mencatat tingkat PM10 tertinggi dengan rata-rata {max_pm10_value:.2f}.")
        st.write(f"- Stasiun **{min_pm25_station}** memiliki tingkat PM2.5 yang lebih rendah dibandingkan stasiun lainnya.")
        st.write(f"- Stasiun **{min_pm10_station}** memiliki tingkat PM10 yang lebih rendah dibandingkan stasiun lainnya.")
        
# Halaman Binning
elif menu == "Binning Analisis":
    st.title("Binning untuk Tingkat Polusi Udara")

    if df is not None:
        # Tentukan ambang batas untuk binning (contoh untuk PM2.5 dan PM10)
        bins_pm25 = [0, 35, 75, 150, 250, 1000]  # Rentang PM2.5 dalam µg/m³
        labels_pm25 = ["Rendah", "Sedang", "Tinggi", "Sangat Tinggi", "Ekstrem"]

        bins_pm10 = [0, 50, 100, 200, 350, 1000]  # Rentang PM10 dalam µg/m³
        labels_pm10 = ["Rendah", "Sedang", "Tinggi", "Sangat Tinggi", "Ekstrem"]

        # Menambahkan kolom binning untuk PM2.5 dan PM10
        df['PM2.5 Binned'] = pd.cut(df['PM2.5'], bins=bins_pm25, labels=labels_pm25)
        df['PM10 Binned'] = pd.cut(df['PM10'], bins=bins_pm10, labels=labels_pm10)

        # Menampilkan distribusi kategori binning untuk PM2.5 dan PM10
        st.subheader("Distribusi Kategori Binning PM2.5 dan PM10")
        
        # Menampilkan bar plot untuk binning PM2.5
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.countplot(x='PM2.5 Binned', data=df, palette="Blues")
        plt.title("Distribusi Kategori PM2.5")
        plt.xlabel("Kategori PM2.5")
        plt.ylabel("Jumlah Observasi")
        plt.tight_layout()
        st.pyplot(fig)

        # Menampilkan bar plot untuk binning PM10
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.countplot(x='PM10 Binned', data=df, palette="Oranges")
        plt.title("Distribusi Kategori PM10")
        plt.xlabel("Kategori PM10")
        plt.ylabel("Jumlah Observasi")
        plt.tight_layout()
        st.pyplot(fig)

        # Menampilkan analisis hasil binning
        st.write("### Hasil Analisis Binning:")
        st.write("- Dari analisis binning, kita dapat melihat bagaimana tingkat PM2.5 dan PM10 terdistribusi dalam kategori yang berbeda.")
        st.write("- Kategori 'Rendah' menunjukkan tingkat polusi udara yang relatif lebih bersih, sementara kategori 'Sangat Tinggi' dan 'Ekstrem' menunjukkan tingkat polusi yang sangat berbahaya.")
        st.write("- Bin 'Tinggi' sering kali terkait dengan area dengan polusi yang cukup besar, yang dapat memengaruhi kesehatan masyarakat.")

# Halaman Kesimpulan
elif menu == "Kesimpulan":
    st.title("Kesimpulan Analisis Polusi Udara")

    if df is not None:
        
        st.write("1. **Hubungan Curah Hujan dan Polusi**:")
        st.write("   - Curah hujan memiliki dampak signifikan dalam menurunkan tingkat polusi udara, terutama untuk PM2.5 dan PM10.")
        st.write("2. **Perbedaan Tingkat Polusi Antar Stasiun**:")
        st.write("   - Terdapat perbedaan signifikan dalam tingkat polusi antara stasiun pemantauan.")
        st.write("3. **Bulan dengan Polusi Tertinggi**:")
        st.write("   - **PM2.5** dan **PM10** mencapai konsentrasi tertinggi pada bulan **Maret**.")
        st.write("   - **SO2** mencapai konsentrasi tertinggi pada bulan **Januari**.")
        st.write("   - **NO2** mencapai konsentrasi tertinggi pada bulan **Desember**.")
        st.write("   - **O3** mencapai konsentrasi tertinggi pada bulan **Mei**.")
        st.write("4. **Kondisi Lingkungan**:")
        st.write("   - Kondisi lingkungan seperti curah hujan, suhu, dan faktor lainnya berpengaruh dalam peningkatan polusi udara.")