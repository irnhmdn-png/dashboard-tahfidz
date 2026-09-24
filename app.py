import streamlit as st
import pandas as pd
import plotly.express as px

# Mengatur tampilan halaman web
st.set_page_config(page_title="Dashboard Tahfidz", page_icon="📊", layout="wide")

st.title("📊 Laporan Otomatis Capaian Tahfidz")
st.write("Unggah file Excel bulanan Anda ke sini. Sistem akan otomatis membersihkan data, menghitung persentase, dan membuat grafik kategorinya.")

# Membuat tombol untuk upload file
uploaded_file = st.file_uploader("Pilih file Excel (misal: list_tahfidz_UBR.xlsx)", type=['xlsx', 'xls'])

if uploaded_file is not None:
    try:
        # Membaca data dari Excel
        df = pd.read_excel(uploaded_file)
        
        # Membersihkan data (Membuang baris yang tidak memiliki data Kelas)
        df_clean = df.dropna(subset=['Kelas']).copy()
        
        # Mencari kolom persentase (mengantisipasi jika nama kolom ada spasi atau 'enter' / newline)
        col_persentase = [col for col in df_clean.columns if 'persentase' in col.lower()][0]
        
        # Mengubah data ke dalam bentuk angka desimal
        df_clean['Persentase_Numeric'] = pd.to_numeric(df_clean[col_persentase], errors='coerce')
        
        # Menentukan Kategori
        bins = [-float('inf'), 0.75, 0.90, 1.00, float('inf')]
        labels = ['Kurang', 'Cukup', 'Tercapai', 'Sangat Tercapai']
        df_clean['Kategori'] = pd.cut(df_clean['Persentase_Numeric'], bins=bins, labels=labels, right=True)
        
        st.success("File berhasil diproses!")
        st.divider()

        # Membagi layar menjadi dua kolom
        col1, col2 = st.columns([1, 2])

        with col1:
            st.subheader("📋 Rekapitulasi per Kelas")
            # Menghitung jumlah siswa di setiap kategori per kelas
            summary = df_clean.groupby(['Kelas', 'Kategori'], observed=False).size().unstack(fill_value=0)
            summary = summary[['Kurang', 'Cukup', 'Tercapai', 'Sangat Tercapai']] # Mengurutkan kolom
            summary['Total Siswa'] = summary.sum(axis=1)
            
            # Menampilkan tabel
            st.dataframe(summary, use_container_width=True)

        with col2:
            st.subheader("📈 Grafik Distribusi Capaian")
            # Menyiapkan data untuk grafik
            summary_reset = df_clean.groupby(['Kelas', 'Kategori'], observed=False).size().reset_index(name='Jumlah Siswa')
            
            # Membuat grafik batang bertumpuk (stacked bar chart) yang interaktif
            fig = px.bar(summary_reset, x='Kelas', y='Jumlah Siswa', color='Kategori',
                         category_orders={'Kategori': ['Kurang', 'Cukup', 'Tercapai', 'Sangat Tercapai']},
                         color_discrete_map={
                             'Kurang': '#e74c3c',
                             'Cukup': '#f1c40f',
                             'Tercapai': '#2ecc71',
                             'Sangat Tercapai': '#3498db'
                         },
                         barmode='stack',
                         text_auto=True)
            
            # Menyesuaikan tampilan grafik
            fig.update_layout(xaxis_title="Kelas", yaxis_title="Jumlah Siswa", legend_title="Kategori", margin=dict(t=20))
            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Terjadi kesalahan saat membaca file. Pastikan formatnya sesuai. Detail error: {e}")
