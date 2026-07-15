# Extract of Document: LAPORAN PROJECT BASED LEARNING (PJBL) DS_Final.docx

LAPORAN PROJECT BASED LEARNING

<JUDUL>

Diajukan untuk memenuhi tugas mata kuliah Project-Based Learning: Statistik Lanjut, Data Mining dan Pemrograman Python

Disusun Oleh :

Nama Mahasiswa 1		NIM Mahasiswa 1

Nama Mahasiswa 2		NIM Mahasiswa 2

dst

PROGRAM STUDI SISTEM INFORMASI

FAKULTAS ILMU KOMPUTER

UNIVERSITAS DUTA BANGSA

SURAKARTA

2026

HALAMAN PENGESAHAN

<JUDUL>

Disusun Oleh :

Nama Mahasiswa1		NIM Mahasiswa1

Nama Mahasiswa2		NIM Mahasiswa2

dst


| Ketua Kelompok     <Nama Mahasiswa> | Dosen Pengampu 1     <Dosen Pengampu 1> |
| --- | --- |
|  |  |
| Dosen Pengampu 2     <Dosen Pengampu 2> | Dosen Pengampu 3     <Dosen Pengampu 3> |
|  |  |
| Surakarta,                    2026 Ketua Program Studi  S-1 Sistem Informasi      Hanifah Permatasari, S.Kom., M.Kom | Surakarta,                    2026 Ketua Program Studi  S-1 Sistem Informasi      Hanifah Permatasari, S.Kom., M.Kom |

KATA PENGANTAR

Puji syukur ke hadirat Tuhan Yang Maha Esa atas rahmat dan karunia-Nya, sehingga laporan Project Based Learning (PBL) ini dapat diselesaikan dengan baik. Laporan ini disusun sebagai bentuk implementasi pembelajaran pada mata kuliah Statistik Lanjut, Data Mining dan Pemrograman Python.

Kegiatan PBL ini bertujuan untuk menerapkan konsep statistik, teknik data mining, dan pemrograman Python dalam pengolahan serta analisis data guna menyelesaikan permasalahan yang diangkat dalam studi kasus. Dalam penyusunan laporan ini, penyusun memperoleh bantuan, bimbingan, dan dukungan dari berbagai pihak. Oleh karena itu, penyusun menyampaikan terima kasih kepada:

Bapak/Ibu [instansi/perusahaan], yang telah memberikan izin serta membantu dalam proses pengambilan data untuk studi kasus ini.

Assoc. Prof. Dr. Singgih Purnomo, MM selaku Rektor Universitas Duta Bangsa Surakarta.

Eko Purwanto, S.Kom., M.Kom., Ph.D selaku Dekan Fakultas Ilmu Komputer.

Hanifah Permatasari, S.Kom., M.Kom selaku Ketua Program Studi Sistem Informasi.

Bapak/Ibu [Nama Dosen], selaku Dosen Pengampu mata kuliah Tata Kelola Teknologi Informasi.

Bapak/Ibu [Nama Dosen], selaku Dosen Pengampu mata kuliah Integrasi Aplikasi Korporasi.

Bapak/Ibu [Nama Dosen], selaku Dosen Pengampu mata kuliah E-Business.

Semua pihak yang telah membantu, baik secara langsung maupun tidak langsung, yang tidak dapat disebutkan satu per satu.

Penyusun menyadari bahwa laporan ini masih memiliki berbagai kekurangan. Oleh karena itu, kritik dan saran yang membangun sangat diharapkan demi perbaikan di masa mendatang. Semoga laporan ini dapat memberikan manfaat bagi pembaca dan menjadi referensi dalam pengembangan sistem informasi berbasis bisnis digital.

Surakarta, [Tanggal][Bulan][Tahun]

Penulis

DAFTAR ISI

Halaman Pengesahan

Kata Pengantar

Daftar Isi

Daftar Gambar

Daftar Tabel

BAB I Pendahuluan

BAB II Tinjauan Pustaka

BAB III Metodologi Project Based Learning

BAB IV Modelling dan Evaluasi

BAB V Deployment

BAB VI Kesimpulan

Daftar Pustaka

Lampiran

BAB I
PENDAHULUAN

1.1 Latar Belakang

Pembangunan wilayah yang merata dan berkelanjutan memerlukan integrasi data spasial yang akurat dan komprehensif. Peta geografis yang dipadukan dengan indikator kesejahteraan sosial ekonomi memberikan pemahaman mendalam mengenai pola pembangunan daerah. Melalui visualisasi spasial, pengambil keputusan dapat mengidentifikasi konsentrasi kemiskinan dan disparitas infrastruktur dengan lebih cepat. Dengan demikian, pemanfaatan data berbasis spasial menjadi instrumen krusial dalam merancang program pembangunan regional yang efektif.

Pada realitasnya, ketimpangan pembangunan antarwilayah di Indonesia masih sangat tinggi, terutama antara Pulau Jawa dan luar Pulau Jawa. Banyak kabupaten dan kota di daerah terpencil masih tertinggal dalam aspek pendidikan, kesehatan, dan kapasitas ekonomi riil. Metode pengelompokan statistik tradisional sering kali gagal mendeteksi daerah atipikal atau outlier spasial yang memiliki karakteristik ekstrem. Selain itu, analisis klaster konvensional tanpa pertimbangan autokorelasi geografis cenderung menghasilkan interpretasi wilayah yang bias dan kurang aplikatif.

Sebagai solusi atas keterbatasan tersebut, dikembangkan sistem informasi analitik bernama SENUWU yang menerapkan model hibrida HDBSCAN dan K-Means. Algoritma HDBSCAN digunakan untuk mendeteksi struktur klaster alami berbasis kepadatan serta mengisolasi data anomali secara objektif. Pusat klaster dari HDBSCAN kemudian dijadikan inisialisasi centroid untuk algoritma K-Means guna mempartisi seluruh daerah secara stabil. Integrasi model hibrida ini disajikan melalui dashboard interaktif berbasis web Streamlit untuk memudahkan visualisasi peta choropleth regional.

Kebaruan utama dalam riset ini terletak pada penerapan Welfare Clustering Validity Index (WCVI) sebagai metrik evaluasi klaster multidimensi. Indeks WCVI secara unik menggabungkan kecenderungan Hopkins, persentase varians R-Squared, dan akurasi klasifikasi berbasis Random Forest. Penggabungan metrik ini memberikan validasi yang lebih komprehensif dibandingkan dengan indeks validasi tradisional seperti Silhouette Score. Penerapan WCVI memastikan bahwa hasil klasterisasi kesejahteraan regional memiliki landasan teoretis yang kuat dan reliabilitas statistik yang tinggi.

1.2 Rumusan Masalah

1. Bagaimana mengimplementasikan pipeline hibrida HDBSCAN dan K-Means untuk mengelompokkan kabupaten dan kota di Indonesia secara optimal berdasarkan data spasial kesejahteraan?

2. Bagaimana mendeteksi wilayah anomali atau atipikal secara objektif menggunakan pendekatan berbasis kepadatan data?

3. Bagaimana mengukur kualitas dan stabilitas hasil klasterisasi kesejahteraan regional menggunakan metrik evaluasi baru Welfare Clustering Validity Index (WCVI)?

4. Bagaimana menyajikan peta tematik choropleth hasil klasterisasi secara interaktif melalui dashboard Streamlit SENUWU?

1.3 Batasan Masalah

1. Data penelitian dibatasi pada 7 indikator kesejahteraan BPS tahun 2024 untuk 514 kabupaten dan kota di Indonesia.

2. Algoritma klasterisasi yang digunakan adalah penggabungan (hibrida) HDBSCAN dan K-Means.

3. Evaluasi kualitas model dibatasi pada pengukuran indeks validitas komposit WCVI dan stabilitas ARI (Adjusted Rand Index).

4. Pemetaan visual spasial disajikan secara digital melalui platform dashboard web Streamlit.

1.4 Tujuan Project

1. Membangun model klasterisasi hibrida HDBSCAN and K-Means untuk mengelompokkan kabupaten dan kota secara akurat berdasarkan kemiripan indikator kesejahteraan.

2. Mengidentifikasi wilayah outlier atau atipikal yang membutuhkan penanganan khusus dalam pembangunan sosial ekonomi.

3. Memvalidasi kekuatan teoretis dan stabilitas klaster menggunakan metrik evaluasi komposit WCVI.

4. Mengembangkan dashboard pemetaan interaktif SENUWU sebagai media diseminasi informasi spasial bagi pemangku kepentingan.

1.5 Manfaat Project

1. Bagi Akademisi: Memberikan referensi ilmiah mengenai penerapan model hibrida klasterisasi dan penggunaan metrik validitas WCVI pada data spasial.

2. Bagi Pemerintah: Menyediakan alat bantu pengambilan keputusan berbasis data spasial untuk alokasi program pengentasan kemiskinan yang lebih tepat sasaran.

3. Bagi Peneliti: Menyediakan kerangka kerja analisis disparitas regional yang menggabungkan statistika multivariat dan teknologi sistem informasi geografis.

4. Bagi Mahasiswa: Menerapkan konsep statistik lanjut, data mining, dan pemrograman Python pada penyelesaian masalah pembangunan nyata di Indonesia.

BAB II 

TINJAUAN PUSTAKA

Studi literatur dalam penelitian ini difokuskan pada pemetaan disparitas sosial ekonomi dan optimalisasi teknik pengelompokan wilayah. Kajian pustaka ini menganalisis kontribusi riset mutakhir yang menggunakan pendekatan data mining, khususnya algoritma berbasis partisi, guna memahami pola pembangunan daerah di Indonesia. Melalui penelaahan metodologis ini, posisi ilmiah proyek yang dikembangkan dapat diletakkan dalam peta perkembangan teknologi sains data terkini. Hal ini penting untuk mengidentifikasi keterbatasan model sebelumnya dan merumuskan kontribusi kebaruan yang ditawarkan oleh sistem SENUWU.

Dalam perkembangannya, penelitian mengenai segmentasi wilayah kemiskinan banyak mengandalkan algoritma partisi klasik. Sebagai contoh, Amalia, Nikmah, dan Siniwi (2025) (ref_1) menerapkan algoritma K-Means dan K-Means++ untuk mengelompokkan kemiskinan di Provinsi Jawa Timur, yang membuktikan bahwa inisialisasi pusat klaster yang lebih baik dapat meningkatkan konsistensi hasil. Di sisi lain, upaya membandingkan efisiensi algoritma partisi dilakukan oleh Habibi dan Nursyanti (2023) (ref_2) yang mengevaluasi algoritma K-Means dan C-Means untuk clustering angka kemiskinan. Meskipun kedua studi ini berhasil memberikan kategorisasi wilayah yang operasional, evaluasi model yang digunakan masih terbatas pada metrik internal konvensional yang belum mempertimbangkan autokorelasi spasial antardaerah yang bertetangga.

Untuk mengatasi keterbatasan batasan wilayah tunggal, penelitian kemudian diarahkan pada analisis multivariat berskala regional yang lebih luas. Sabina dkk. (2024) (ref_3) melakukan pengelompokan kabupaten dan kota di Provinsi Nusa Tenggara Barat berdasarkan indikator kemiskinan sosial ekonomi dengan K-Means, yang menyoroti pentingnya indikator komposit BPS dalam mencerminkan kondisi riil daerah. Kebutuhan akan optimasi pengelompokan spasial yang lebih dinamis dijawab oleh Sundawati (2025) (ref_4) melalui penerapan Center Displacement Fuzzy K-Means untuk pemetaan kemiskinan di Pulau Jawa. Penelitian tersebut memperkenalkan pergeseran pusat klaster guna mengakomodasi heterogenitas data regional, namun visualisasi hasil pemodelan masih bersifat statis dan belum terintegrasi ke dalam platform interaktif yang mudah diakses publik.

Upaya untuk menyajikan hasil analisis data secara lebih komunikatif mulai dirintis melalui integrasi indikator kesejahteraan dengan visualisasi spasial. Amelia dkk. (2023) (ref_5) memetakan tingkat kemiskinan di Provinsi Jawa Barat menggunakan K-Means dengan fokus pada visualisasi yang menggambarkan distribusi pengangguran dan daya beli masyarakat. Riset ini memperkuat urgensi visualisasi data sebagai media penyampaian informasi yang ramah publik. Kendati demikian, sistem yang dibangun belum menyediakan mekanisme pemutakhiran data secara mandiri (realtime) ataupun fungsi prediksi otomatis bagi wilayah baru yang ingin diintegrasikan ke dalam peta klasifikasi yang sudah ada.

Berdasarkan sintesis dari berbagai literatur terdahulu, proyek SENUWU hadir untuk mengisi celah metodologis dengan menetapkan standar baru dalam analisis ketimpangan regional di Indonesia. Proyek ini mengintegrasikan model hibrida HDBSCAN dan K-Means yang secara otomatis mengatasi masalah inisialisasi centroid sekaligus menyaring data pencilan (outlier) spasial secara objektif melalui Moran's I. Kebaruan utama terletak pada perumusan Welfare Clustering Validity Index (WCVI) sebagai kerangka validasi komposit yang menggabungkan aspek keterpolaan data, varians regional, dan keandalan klasifikasi acak. Seluruh keunggulan teoretis tersebut diwujudkan dalam dashboard interaktif berbasis Streamlit yang dilengkapi dengan sistem otentikasi administrator untuk pemutakhiran data dan prediksi klasifikasi dinamis secara langsung.

BAB III
METODOLOGI PROJECT BASED LEARNING

3.1 Metode Pelaksanaan Proyek

Pelaksanaan proyek analitik kesejahteraan regional ini dirancang dengan mengadopsi metodologi sains data terstruktur yang dikombinasikan dengan prinsip pembelajaran berbasis proyek. Pendekatan ini memastikan bahwa setiap fase pengerjaan berjalan secara sistematis dan terukur guna menjembatani teori statistika lanjut dengan pemrograman praktis. Alur kerja proyek ini dibagi secara runtut ke dalam lima tahapan utama yang meliputi identifikasi masalah, pengumpulan data, pengolahan data, analisis pemodelan data mining, hingga implementasi dan deployment. Dengan mengikuti lima tahapan sistematis ini, tim riset dapat meminimalkan risiko kesalahan logika dan mengoptimalkan kualitas hasil akhir.

Tahap pertama dimulai dengan identifikasi masalah untuk menetapkan tujuan analitis ketimpangan sosial ekonomi antarwilayah. Tahap kedua adalah pengumpulan data multivariat dari publikasi resmi pemerintah untuk memperoleh data yang valid. Tahap ketiga melibatkan pengolahan data untuk membersihkan, menstandarisasikan skala, serta memfilter data pencilan. Tahap keempat adalah analisis pemodelan data mining menggunakan model hibrida HDBSCAN dan K-Means yang kemudian divalidasi kinerjanya. Tahap kelima ditutup dengan implementasi dan deployment model ke dalam platform digital interaktif.

Penerapan kelima tahapan tersebut bermuara pada pengembangan sistem informasi analitik bernama SENUWU yang dapat diakses dengan mudah oleh publik. Dashboard ini dirancang untuk menampilkan visualisasi spasial dinamis dalam bentuk peta choropleth serta menyediakan fitur prediksi otomatis bagi data wilayah baru. Melalui sistem visualisasi ini, informasi analitik yang kompleks dari model hibrida dapat disajikan secara sederhana dan interaktif. Hal ini diharapkan mampu membantu para pengambil kebijakan dalam merancang program pembangunan regional yang berbasis data.

3.2 Identifikasi Masalah

Permasalahan utama yang melatarbelakangi riset ini adalah fenomena disparitas kesejahteraan regional yang persisten di berbagai wilayah Indonesia. Ketimpangan pembangunan sosial ekonomi antarwilayah, khususnya antara kawasan Pulau Jawa dan luar Pulau Jawa, menjadi hambatan serius bagi keadilan sosial. Indikator dasar pembangunan seperti akses kesehatan, kualitas pendidikan, dan daya beli masyarakat menunjukkan variabilitas yang sangat lebar antardaerah. Tanpa adanya pemetaan yang komprehensif, upaya intervensi pemerintah sering kali tidak merata dan kurang menyentuh akar permasalahan di wilayah terpencil.

Penyusunan kebijakan pembangunan daerah selama ini kerap terhambat oleh keterbatasan metode analisis statistik konvensional. Pendekatan pengelompokan tradisional seperti K-Means murni sangat sensitif terhadap nilai ekstrem dan rentan terjebak pada bias inisialisasi pusat klaster awal. Metode tersebut juga cenderung memaksakan seluruh observasi masuk ke dalam klaster tertentu tanpa menyaring data pencilan yang bersifat atipikal. Akibatnya, daerah-daerah dengan karakteristik kemiskinan ekstrem atau keunikan ekonomi tertentu sering kali terabaikan dalam pengelompokan umum.

Selain masalah akurasi algoritma, analisis disparitas kesejahteraan regional sering kali mengabaikan aspek keterkaitan geografis antardaerah tetangga. Padahal, kondisi sosial ekonomi suatu kabupaten atau kota secara logis dipengaruhi oleh aktivitas pembangunan di wilayah sekitarnya. Pengabaian faktor autokorelasi spasial ini menyebabkan bias interpretasi pada hasil klasterisasi pembangunan daerah. Oleh karena itu, diperlukan sebuah sistem pemodelan baru yang mampu mengintegrasikan analisis spasial multivariat dengan deteksi anomali data untuk memetakan profil kesejahteraan daerah secara presisi.

3.3 Pengumpulan Data

Data yang digunakan dalam proyek analitik ini sepenuhnya bersumber dari publikasi resmi Badan Pusat Statistik (BPS) Republik Indonesia tahun 2024. Pilihan sumber data ini menjamin validitas, keterpercayaan, dan legalitas informasi yang dianalisis dalam dokumen HKI. Populasi data mencakup seluruh wilayah administratif tingkat kabupaten dan kota di Indonesia dengan total observasi sebanyak 514 daerah. Penggunaan seluruh cakupan daerah secara nasional bertujuan untuk menghindari bias representasi geografis dan memberikan gambaran disparitas regional yang menyeluruh.

Untuk memudahkan pemahaman mengenai dimensi pembangunan yang diukur, tujuh indikator kesejahteraan tersebut disajikan secara terperinci dalam tabel di bawah ini. Tabel ini memuat nama indikator asli, nama pemetaan variabel, deskripsi singkat, sifat pengaruh variabel terhadap kesejahteraan, serta nilai domain maksimal yang digunakan sebagai ceiling regional.

Tabel 2. Rincian Tujuh Indikator Kesejahteraan Wilayah


| No | Indikator Asli BPS | Nama Variabel | Deskripsi Singkat | Sifat Pengaruh | Domain Maksimal |
| --- | --- | --- | --- | --- | --- |
| 1 | Umur Harapan Hidup (Tahun) | UHH | Mengukur rata-rata perkiraan usia hidup sejak lahir | Positif (+) | 80 Tahun |
| 2 | Rata-rata Lama Sekolah Penduduk 15+ (Tahun) | Rata_rata_Lama_Sekolah | Mengukur tingkat pencapaian pendidikan formal | Positif (+) | 15 Tahun |
| 3 | PDRB ADHK menurut Pengeluaran (Rupiah) | PDRB_Konstan | Mengukur kapasitas ekonomi riil regional | Positif (+) | 1 Triliun Rupiah |
| 4 | Persentase Penduduk Miskin (Persen) | Persentase_Penduduk_Miskin | Mengukur tingkat kerawanan kemiskinan daerah | Negatif (-) | 50 Persen |
| 5 | Pengeluaran per Kapita Disesuaikan (Ribu Rupiah) | Pengeluaran_per_Kapita | Mengukur daya beli dan tingkat konsumsi masyarakat | Positif (+) | 25 Ribu Rupiah |
| 6 | Akses Sanitasi Layak (Persen) | Sanitasi_Layak | Mengukur kualitas infrastruktur kesehatan dasar | Positif (+) | 100 Persen |
| 7 | Tingkat Pengangguran Terbuka (Persen) | TPT | Mengukur beban ketenagakerjaan daerah | Negatif (-) | 15 Persen |

Ketujuh indikator yang dipilih memiliki skala pengukuran yang sangat bervariasi, mulai dari persentase hingga nilai rupiah nominal yang mencapai triliunan. Sifat pengaruh variabel juga terbagi menjadi dua kategori, yaitu indikator positif yang bernilai baik jika tinggi, serta indikator negatif yang menggambarkan beban sosial jika nilainya meningkat. Perbedaan skala dan arah pengaruh yang kontras ini menuntut adanya proses penanganan data yang ketat. Proses tersebut bertujuan agar fitur-fitur dominan secara nominal tidak menutupi kontribusi variabel lainnya saat dilakukan pemodelan klaster.

3.4 Pengolahan dan Persiapan Data

Fase awal persiapan data dimulai dengan proses pembersihan nilai kosong menggunakan metode imputasi berbasis nilai median masing-masing kolom. Setelah data lengkap, tim riset menerapkan transformasi skala menggunakan Power Transformer dengan metode Yeo-Johnson guna mengatasi skewness distribusi data. Transformasi ini sangat penting untuk menyamakan rentang nilai antarindikator serta menormalkan distribusi fitur agar memenuhi asumsi statistik model klasterisasi. Data terstandar ini kemudian menjadi input yang bebas dari bias perbedaan satuan metrik untuk tahap analisis selanjutnya.

Guna meningkatkan kualitas klaster inti, proses eliminasi pencilan (outliers) dilakukan menggunakan algoritma Isolation Forest dengan parameter kontaminasi sebesar 5 persen. Langkah pengkondisian data ini berhasil mengidentifikasi 26 kabupaten dan kota yang memiliki karakteristik atipikal ekstrem dibandingkan dengan wilayah lainnya. Kelompok daerah pencilan ini dipisahkan sebagai klaster eksklusif agar tidak mengganggu kestabilan pembentukan centroid klaster utama. Sebanyak 488 observasi yang tergolong inliers kemudian digunakan sebagai dataset inti dalam proses pelatihan model hibrida.

Sebelum pemodelan dijalankan, kelayakan clusterability spasial diuji secara ketat menggunakan indeks autokorelasi spasial Moran's I pre-clustering. Dengan membangun matriks bobot spasial k-nearest neighbors (k = 5), pengujian ini mengukur apakah nilai indikator kesejahteraan terdistribusi secara acak atau membentuk pola geografis tertentu. Hasil pengujian menunjukkan bahwa ketujuh variabel memiliki nilai indeks Moran's I positif yang sangat signifikan dengan nilai signifikansi p = 0.0010. Temuan statistik ini memvalidasi secara ilmiah bahwa data kesejahteraan di Indonesia memiliki struktur keterpolaan spasial regional yang kuat untuk diklasterkan.

Bagian penting yang melengkapi tahap persiapan ini adalah pengujian korelasi multikolinearitas untuk memastikan tidak ada redundansi informasi antarfitur. Tim riset juga menetapkan pembobotan fitur secara eksplisit berdasarkan tingkat kepentingannya terhadap dimensi kesejahteraan rakyat. Indikator Umur Harapan Hidup diberikan bobot tertinggi sebesar 25 persen, disusul kapasitas ekonomi PDRB konstan sebesar 20 persen, serta lama sekolah dan pengangguran masing-masing 15 persen. Pembobotan proporsional ini digunakan untuk menghitung Composite Welfare Score pasca-klasterisasi guna memberikan penilaian kesejahteraan wilayah yang lebih adil dan teoretis.

3.5 Jadwal Pelaksanaan Proyek

Sub bab ini berisi rencana atau jadwal kegiatan proyek mulai dari tahap perencanaan hingga penyusunan laporan akhir. Jadwal dapat disajikan dalam bentuk tabel atau diagram untuk memudahkan pemantauan pelaksanaan setiap tahapan proyek.

Contoh :

Table 1. Jadwal Kegiatan Project Based Learning


| No | Kegiatan | Minggu 1 | Minggu 2 | Minggu 3 | Minggu 4 | Minggu 5 | Minggu 6 | Minggu 7 | Minggu 8 | Minggu 9 | Minggu 10 | Minggu 11 | Minggu 12 | Minggu 13 | Minggu 14 | Minggu 15 | Minggu 16 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Identifikasi masalah dan studi literatur | ✓ | ✓ |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 2 | Pengumpulan data |  | ✓ | ✓ | ✓ |  |  |  |  |  |  |  |  |  |  |  |  |
| 3 | Data understanding dan eksplorasi data |  |  | ✓ | ✓ |  |  |  |  |  |  |  |  |  |  |  |  |
| 4 | Data cleaning dan data preparation |  |  |  | ✓ | ✓ | ✓ |  |  |  |  |  |  |  |  |  |  |
| 5 | Pemilihan metode statistik/data mining |  |  |  |  | ✓ | ✓ |  |  |  |  |  |  |  |  |  |  |
| 6 | Implementasi model menggunakan Python |  |  |  |  |  | ✓ | ✓ | ✓ | ✓ |  |  |  |  |  |  |  |
| 7 | Pengujian dan evaluasi model |  |  |  |  |  |  |  | ✓ | ✓ | ✓ |  |  |  |  |  |  |
| 8 | Analisis hasil dan interpretasi |  |  |  |  |  |  |  |  | ✓ | ✓ | ✓ |  |  |  |  |  |
| 9 | Penyusunan laporan proyek |  |  |  |  |  |  |  |  |  | ✓ | ✓ | ✓ | ✓ |  |  |  |
| 10 | Revisi laporan |  |  |  |  |  |  |  |  |  |  |  | ✓ | ✓ | ✓ |  |  |
| 11 | Penyusunan presentasi |  |  |  |  |  |  |  |  |  |  |  |  | ✓ | ✓ |  |  |
| 12 | Presentasi dan finalisasi laporan |  |  |  |  |  |  |  |  |  |  |  |  |  |  | ✓ | ✓ |

BAB IV
MODELLING DAN EVALUASI

4.1 Pemilihan Metode/Algoritma

Pemilihan algoritma dalam riset kesejahteraan ini didasarkan pada karakteristik data regional Indonesia yang heterogen dan memiliki pencilan spasial. Algoritma K-Means konvensional sering kali tidak mampu memproses kerapatan data yang bervariasi dan sangat rentan terhadap inisialisasi centroid awal yang acak. Sebagai solusi, model hibrida menggabungkan kekuatan algoritma berbasis kepadatan HDBSCAN dengan algoritma partisi K-Means. Pendekatan ini memungkinkan sistem untuk mengidentifikasi bentuk klaster alami terlebih dahulu sebelum melakukan partisi penuh pada wilayah administratif.

Algoritma HDBSCAN dipilih sebagai langkah awal karena kemampuannya dalam mendeteksi klaster tanpa perlu menentukan jumlah kelompok di awal. Algoritma ini bekerja dengan mengidentifikasi area data yang memiliki kepadatan tinggi dan memisahkannya dari wilayah yang memiliki kerapatan rendah. Daerah yang berada pada area berkepadatan rendah tersebut diklasifikasikan sebagai data pencilan (noise) secara objektif. Hasil klaster inti dari HDBSCAN ini yang kemudian menjadi dasar untuk menentukan jumlah kelompok optimal secara otomatis.

Setelah klaster inti teridentifikasi oleh HDBSCAN, algoritma K-Means digunakan untuk mengelompokkan seluruh daerah, termasuk daerah pencilan, ke dalam kategori akhir. Penggabungan ini mengatasi kelemahan utama K-Means yang sensitif terhadap penentuan jumlah klaster awal. Centroid atau pusat klaster yang dihasilkan oleh density peaks HDBSCAN digunakan sebagai inisialisasi posisi awal centroid K-Means. Dengan demikian, K-Means dapat melakukan pembagian wilayah secara lengkap dan konsisten tanpa terjebak pada optimum lokal.

Integrasi kedua algoritma sains data ini menghasilkan klasifikasi wilayah yang sangat kokoh dan representatif untuk analisis sosial ekonomi. Model hibrida ini mampu mengelompokkan 514 kabupaten dan kota secara adil berdasarkan kemiripan multidimensi indikator kesejahteraan. Informasi klasifikasi yang stabil ini sangat penting bagi pemerintah untuk menghindari bias dalam alokasi dana bantuan daerah. Pendekatan ini memastikan bahwa setiap wilayah ditempatkan pada kelompok yang sesuai dengan kondisi riil di lapangan.

4.2 Perancangan Model

Fase perancangan model diawali dengan menentukan parameter konfigurasi yang optimal pada algoritma HDBSCAN and K-Means. Konfigurasi parameter ini disesuaikan dengan distribusi data inliers hasil penyaringan Isolation Forest yang dijelaskan pada bab sebelumnya. Variabel terstandar Yeo-Johnson dimasukkan ke dalam ruang koordinat multidimensi sebagai fitur input utama. Desain eksperimen ini disusun untuk menguji stabilitas klaster di bawah berbagai variasi inisialisasi nilai acak.

Penentuan jumlah klaster optimal dilakukan secara otomatis menggunakan mekanisme pencarian parameter (grid search) pada HDBSCAN. Tim riset melakukan iterasi pada parameter min cluster size dari rentang 5 hingga 15 dan min samples dari 3 hingga 8. Skenario yang dipilih adalah kombinasi parameter yang menghasilkan jumlah klaster valid antara 2 hingga 5 kelompok dengan tingkat noise seminimal mungkin. Hasil pencarian otomatis ini menetapkan nilai min cluster size sebesar 5 dan min samples sebesar 3 sebagai konfigurasi terbaik.

Konfigurasi parameter optimal tersebut menghasilkan jumlah klaster alami sebanyak 4 kelompok utama di luar kelompok pencilan. Tim riset kemudian mengekstraksi nilai rata-rata (centroid) dari masing-masing klaster inti yang terbentuk pada ruang Yeo-Johnson. Nilai centroid dari density peaks ini digunakan sebagai titik awal penempatan pusat klaster untuk proses iterasi algoritma K-Means. Skenario inisialisasi centroid ini menjamin hasil partisi K-Means akan selalu konvergen pada kelompok yang stabil.

Untuk menguji keandalan batas klaster yang terbentuk, dirancang skenario pelatihan klasifikasi menggunakan algoritma Random Forest. Dataset wilayah beserta label klaster K-Means dibagi untuk proses pelatihan model klasifikasi guna mengukur tingkat keterpisahan klaster. Pengujian ini menggunakan metode Out-of-Bag (OOB) untuk mengevaluasi keakuratan klasifikasi tanpa memerlukan dataset uji eksternal yang terpisah. Rancangan pengujian klasifikasi ini menjadi basis utama dalam perhitungan komponen evaluasi model komposit.

4.3 Hasil Pemodelan

Model hibrida yang dikembangkan berhasil membagi 488 wilayah inliers ke dalam 4 klaster utama, ditambah 26 wilayah pencilan yang dikelompokkan sebagai klaster eksklusif. Klaster 2 merupakan kelompok terbesar yang mencakup 159 daerah, disusul Klaster 1 sebanyak 134 daerah, Klaster 0 sebanyak 108 daerah, dan Klaster 3 sebanyak 87 daerah. Distribusi ini menunjukkan pola pengelompokan yang seimbang di mana tidak ada satu klaster utama yang mendominasi seluruh populasi daerah secara ekstrem. Pembagian klaster ini menggambarkan profil tingkat kesejahteraan regional Indonesia secara komprehensif.

Untuk memberikan interpretasi yang ramah publik, karakteristik setiap kelompok wilayah diidentifikasi berdasarkan nilai rata-rata indikator aslinya. Nilai profil statistik ini disajikan secara lengkap pada tabel di bawah ini untuk menunjukkan disparitas indikator antar kelompok wilayah.

Tabel 3. Profil Nilai Rata-rata Indikator Kesejahteraan per Klaster


| Nama Klaster | Persentase Kemiskinan (%) | Rata-rata Lama Sekolah (Tahun) | Pengeluaran per Kapita (Ribu Rp) | Umur Harapan Hidup (Tahun) | Akses Sanitasi Layak (%) | Tingkat Pengangguran (%) | PDRB Konstan (Miliar Rp) | Jumlah Daerah |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Maju & Urbanized | 6.2800 | 10.5200 | 14.8500 | 73.2100 | 85.1200 | 5.1200 | 120.4500 | 87 |
| Berkembang Seimbang | 8.0800 | 8.9000 | 11.2300 | 71.4500 | 78.9000 | 4.3000 | 45.1200 | 159 |
| Berkembang Industrial | 10.9800 | 7.9500 | 9.8000 | 69.8000 | 72.1000 | 5.8000 | 85.3000 | 108 |
| Berkembang Rentan | 16.5300 | 7.1200 | 8.1200 | 67.5000 | 65.4000 | 3.9000 | 15.2000 | 134 |
| Subsisten Tertinggal (Outlier) | 19.2600 | 6.2500 | 6.8000 | 64.2000 | 52.1000 | 6.5000 | 8.4000 | 26 |

Visualisasi spasial hasil klasterisasi disajikan secara komprehensif melalui peta choropleth tingkat nasional yang interaktif. Peta ini menggambarkan pembagian 4 klaster kesejahteraan di seluruh kabupaten dan kota dengan kode warna yang merepresentasikan karakteristik tipologi masing-masing daerah. Melalui pemetaan geografis ini, pola ketimpangan spasial terlihat sangat jelas di mana wilayah dengan kesejahteraan tinggi mengelompok di Jawa, sementara wilayah dengan kesejahteraan rendah mendominasi bagian Timur. Detail representasi visual peta choropleth hasil klasterisasi ini disajikan pada gambar di bawah ini.

Gambar 1. Peta Choropleth Hasil Klasterisasi Kesejahteraan Wilayah Indonesia

Analisis data di atas menghasilkan penamaan tipologi kesejahteraan regional yang menggambarkan kondisi sosial ekonomi masing-masing kelompok. Klaster Maju dan Urbanized dicirikan oleh angka harapan hidup dan lama sekolah tertinggi, serta daya beli masyarakat yang sangat kuat. Klaster Berkembang Seimbang menunjukkan pertumbuhan sarana sosial yang merata dengan kelas menengah yang stabil. Klaster Berkembang Industrial memiliki kapasitas ekonomi PDRB tinggi namun kualitas pembangunan manusianya masih tertinggal. Klaster Berkembang Rentan dan Subsisten Tertinggal merupakan daerah dengan angka kemiskinan tinggi yang mendesak untuk diberikan prioritas pembangunan dasar.

Hasil pemodelan ini juga memperkuat hipotesis ketimpangan pembangunan antara Pulau Jawa dan luar Pulau Jawa secara spasial. Sebagian besar daerah yang masuk dalam kategori Maju dan Urbanized terkonsentrasi di Pulau Jawa dan kota-besar nasional. Sebaliknya, wilayah yang tergolong Berkembang Rentan dan Subsisten Tertinggal didominasi oleh kabupaten di wilayah Indonesia Timur dan daerah perbatasan. Hasil uji statistik asosiasi menunjukkan adanya hubungan spasial yang sangat kuat (Cramer's V sebesar 0.6486) antara lokasi geografis wilayah dengan kelas klaster kesejahteraan yang terbentuk.

4.4 Evaluasi Model

Evaluasi keandalan model klasterisasi hibrida diuji menggunakan metrik komposit Welfare Clustering Validity Index (WCVI) yang dirumuskan pada Bab III. Komponen pertama dari WCVI adalah Hopkins Statistic (H) yang menguji kelayakan pembentukan klaster alami pada dataset. Nilai Hopkins yang diperoleh adalah sebesar 0.7183, yang berada jauh di atas ambang batas teoritis minimal sebesar 0.5000. Angka ini secara statistik membuktikan bahwa dataset indikator kesejahteraan BPS memiliki kecenderungan alami untuk membentuk kelompok yang terpisah, bukan terdistribusi secara acak.

Komponen kedua dalam evaluasi model adalah nilai R-Squared (EESS%) yang mengukur seberapa besar varians data kesejahteraan dapat dijelaskan oleh kelompok klaster yang terbentuk. Nilai R-Squared yang dihasilkan model hibrida ini mencapai 49.11 persen, yang menunjukkan tingkat keterpolaan data yang baik untuk dimensi multivariat regional. Nilai ini mengonfirmasi bahwa pembagian empat klaster utama mampu menangkap hampir sepertiga dari total variasi kesejahteraan sosial ekonomi di Indonesia. Proporsi varians ini memberikan landasan bahwa pembagian kelompok wilayah memiliki signifikansi statistik yang tinggi.

Untuk merangkum hasil evaluasi kualitas dan keandalan model secara keseluruhan, komponen-komponen metrik pengujian disajikan pada tabel di bawah ini.

Tabel 4. Ringkasan Metrik Evaluasi Model Komposit


| No | Metrik Evaluasi | Nilai Uji | Deskripsi Teoretis | Interpretasi Kelayakan |
| --- | --- | --- | --- | --- |
| 1 | Hopkins Statistic (H) | 0.7183 | Mengukur tendensi klasterisasi alami pada data | Sangat Layak (Nilai > 0.50) |
| 2 | R-Squared (EESS%) | 49.11% | Proporsi varians multivariat yang dijelaskan | Baik (Menggambarkan ~50% variasi) |
| 3 | RF OOB Accuracy | 89.75% | Akurasi keterpisahan batas klaster via klasifikasi | Sangat Tinggi (Batas klaster tegas) |
| 4 | WCVI Score | 0.6812 | Nilai indeks validitas komposit kesejahteraan | Kualitas Klasterisasi Tinggi |
| 5 | ARI Mean (10 Seeds) | 0.8966 | Uji stabilitas klaster terhadap inisialisasi acak | Sangat Stabil (Nilai > 0.80) |

Komponen ketiga dari WCVI diukur melalui akurasi klasifikasi Out-of-Bag (OOB) menggunakan algoritma Random Forest untuk menilai keterpisahan antar klaster. Model klasifikasi yang dilatih berdasarkan label klaster K-Means menghasilkan akurasi OOB yang sangat tinggi yaitu mencapai 89.75 persen. Akurasi yang tinggi ini membuktikan bahwa batas-batas antarklaster yang ditentukan oleh model hibrida memiliki keterpisahan dimensi yang sangat tegas. Hasil evaluasi komposit WCVI secara keseluruhan menghasilkan nilai akhir sebesar 0.6812, yang mengindikasikan kualitas klasterisasi yang sangat baik.

Kestabilan hasil klasterisasi diuji lebih lanjut menggunakan Adjusted Rand Index (ARI) melalui simulasi iterasi 10 seed KMeans yang berbeda. Uji stabilitas ini bertujuan untuk memastikan bahwa model hibrida tidak sensitif terhadap perubahan inisialisasi awal acak. Nilai ARI rata-rata yang dicapai adalah sebesar 0.8966 dengan deviasi standar yang sangat kecil yaitu 0.0405. Hasil uji stabilitas yang mendekati nilai 1.0000 ini menegaskan bahwa model hibrida HDBSCAN-KMeans memiliki keandalan yang sangat tinggi dan konsisten untuk digunakan secara berulang.

BAB V
DEPLOYMENT

5.1 Implementasi Model

Implementasi model ke dalam lingkungan operasional dilakukan dengan mengintegrasikan seluruh alur kerja pemodelan ke dalam framework aplikasi web Streamlit. Proses integrasi ini mencakup penyimpanan centroid klaster terstandar Yeo-Johnson dan parameter model latih Random Forest ke dalam folder results. Melalui penyimpanan terstruktur ini, sistem tidak perlu melakukan pelatihan ulang model setiap kali aplikasi dijalankan oleh pengguna. Hal ini secara signifikan meminimalkan waktu pemrosesan dan konsumsi memori server saat menangani permintaan pengguna secara realtime.

Pada sisi backend, data baru yang dimasukkan oleh pengguna akan diproses secara on-the-fly menggunakan parameter normalisasi dari pre-trained model. Nilai indikator mentah dari form input akan ditransformasikan ke dalam skala Yeo-Johnson yang sama persis dengan dataset awal. Selanjutnya, sistem menghitung jarak Euclidean antara data baru yang telah ditransformasikan tersebut dengan centroid dari keempat klaster utama. Wilayah baru kemudian diklasifikasikan ke dalam kategori klaster yang memiliki jarak Euclidean terkecil untuk menjamin konsistensi metodologi riset.

Setelah label klaster diperoleh, sistem akan menghitung Composite Welfare Score secara dinamis menggunakan bobot kepentingan fitur yang telah dirumuskan pada Bab III. Sistem juga menghitung nilai z-score regional dengan membandingkan nilai input daerah baru terhadap rata-rata dan standar deviasi klaster yang terpilih. Perhitungan z-score ini berfungsi untuk mendeteksi indikator yang paling dominan di wilayah tersebut. Hasil perhitungan ini kemudian disuntikkan ke dalam database utama untuk memperbarui repositori visualisasi secara langsung.

Untuk menjamin pengalaman pengguna yang lancar dan no-lag, antarmuka dashboard mengimplementasikan rendering peta interaktif menggunakan pustaka Plotly WebGL. Penggunaan WebGL sangat penting mengingat ukuran file poligon koordinat geografis kabupaten dan kota di Indonesia mencapai kapasitas puluhan megabyte. Peta choropleth yang dihasilkan dapat digeser dan diperbesar secara responsif tanpa menurunkan kinerja memori browser. Optimalisasi rendering ini menjadikan sistem SENUWU sangat andal dan nyaman digunakan oleh publik secara interaktif.

5.2 Tampilan Sistem atau Aplikasi atau Model yang di-build

Tampilan antarmuka dashboard SENUWU dirancang dengan mengusung tema Academia Mode untuk memberikan impresi visual yang premium dan profesional. Skema warna didominasi oleh perpaduan warna tanah yang lembut dengan aksen warna kuningan kuno untuk menciptakan kesan akademis yang kuat. Pilihan tipografi serif digunakan pada bagian judul bab guna mempertegas nuansa ilmiah laporan. Tata letak elemen visual disusun secara bersih dan terstruktur untuk memudahkan navigasi pengguna di setiap menu dashboard.

Halaman pertama yang menyambut pengguna adalah menu Beranda yang menyajikan peta interaktif choropleth klasifikasi kesejahteraan nasional. Peta ini dilengkapi dengan fitur hover insight yang menampilkan detail indikator sosial ekonomi daerah saat kursor diarahkan ke area tertentu. Bagian bawah halaman beranda menyajikan kartu ringkasan kategori klaster yang menjelaskan karakteristik umum dari masing-masing kelompok wilayah. Tampilan menu Beranda ini secara lengkap disajikan pada gambar tangkapan layar di bawah ini.

Gambar 2. Screenshot Tampilan Antarmuka Halaman Beranda Dashboard SENUWU

Menu kedua adalah fitur Cari yang didesain khusus untuk memberikan informasi naratif komprehensif mengenai kondisi daerah tertentu. Pengguna dapat memilih provinsi dan kabupaten melalui dropdown menu secara intuitif tanpa memicu waktu jeda pemrosesan yang lama. Setelah tombol cari diklik, sistem akan menampilkan visualisasi metrik kesejahteraan beserta narasi analisis yang mendalam tentang potensi pembangunan wilayah tersebut. Tampilan visual menu Cari ini disajikan pada gambar tangkapan layar di bawah ini.

Gambar 3. Screenshot Tampilan Antarmuka Halaman Cari Dashboard SENUWU

Menu ketiga adalah halaman Update Data Baru yang didesain sebagai modul administrasi untuk memutakhirkan database sistem. Halaman ini diproteksi oleh sistem keamanan sandi satu pintu guna mencegah perubahan data dari pihak yang tidak memiliki otoritas. Setelah sandi admin dimasukkan, form input tujuh indikator kesejahteraan akan muncul secara dinamis dan siap menerima masukan data baru. Tampilan halaman administrasi pembaruan data ini disajikan secara lengkap pada gambar di bawah ini.

Gambar 4. Screenshot Tampilan Antarmuka Halaman Update Data Baru Dashboard SENUWU

Menu terakhir adalah halaman Info yang berfungsi sebagai media edukasi mengenai dasar teori dan validitas model yang digunakan. Halaman ini menyajikan penjelasan ringkas mengenai algoritma hybrid HDBSCAN dan K-Means serta keunggulan penggunaan metrik validitas WCVI. Bagian utama halaman info menampilkan grafik metrik evaluasi model secara komparatif untuk meyakinkan pembaca mengenai kekuatan ilmiah sistem. Tampilan halaman informasi metodologi dan metrik evaluasi disajikan pada gambar di bawah ini.

Gambar 5. Screenshot Tampilan Antarmuka Halaman Info Dashboard SENUWU

5.3 Pengujian Implementasi

Skenario pengujian keandalan aplikasi web SENUWU dirancang secara komprehensif menggunakan dua pendekatan utama, yaitu pengujian kotak hitam (Black Box Testing) dan pengujian kotak putih (White Box Testing). Pengujian ini penting untuk memverifikasi fungsionalitas antarmuka serta keakuratan aliran logika internal program komputer yang didaftarkan dalam HKI ini. Seluruh pengujian dijalankan langsung pada server lokal yang aktif pada port 8501 menggunakan data simulasi riil. Pendekatan pengujian berlapis ini memastikan aplikasi bebas dari kesalahan komputasi dasar dan aman digunakan secara berkelanjutan.

Pengujian kotak hitam difokuskan pada pengujian seluruh fungsi antarmuka pengguna tanpa melihat struktur kode di dalam sistem. Hasil pengujian menunjukkan bahwa menu navigasi sidebar berhasil memindahkan halaman secara dinamis dan responsif. Modul otentikasi sandi admin123 bekerja dengan benar di mana input kata sandi yang salah langsung memicu munculnya notifikasi kegagalan otentikasi. Selain itu, form input pada menu penambahan data dapat menerima data dengan baik dan tombol simpan data secara sukses melakukan pembaruan pada database disk.

Pengujian kotak putih diarahkan untuk memvalidasi akurasi perhitungan matematis dan percabangan keputusan di dalam modul program. Fokus utama pengujian ini adalah memverifikasi fungsionalitas komputasi Welfare Score dan keandalan transformasi data Yeo-Johnson. Logika internal fungsi compute welfare score terbukti mampu menghasilkan nilai normalisasi yang tepat sebesar 1.0000 untuk skenario paling sejahtera dan 0.0000 untuk skenario tidak sejahtera. Struktur pencarian centroid terdekat menggunakan jarak Euclidean dalam ruang dimensi tujuh juga bekerja secara konsisten tanpa menimbulkan kesalahan bias.

Rangkuman skenario dan status hasil pengujian kotak hitam dan kotak putih secara rinci disajikan dalam tabel pengujian di bawah ini untuk menunjukkan kelayakan operasional sistem.

Tabel 5. Hasil Pengujian Fungsionalitas Black Box dan White Box


| No | Jenis Pengujian | Modul / Fungsi yang Diuji | Skenario Uji | Hasil Aktual | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Black Box | Otentikasi Sandi Admin | Input kata sandi admin123 dan sandi salah | Sandi salah ditolak, sandi admin123 membuka form | Sukses (Pass) |
| 2 | Black Box | Form Input Wilayah Baru | Submit form dengan data kabupaten fiktif | Data tersimpan di disk dan klaster terprediksi instan | Sukses (Pass) |
| 3 | Black Box | Navigasi Menu Sidebar | Klik menu Beranda, Cari, Update, dan Info | Halaman berpindah secara responsif dan tanpa lag | Sukses (Pass) |
| 4 | White Box | Fungsi compute_welfare_score | Uji nilai input ideal (1.00) dan terburuk (0.00) | Perhitungan bobot dan normalisasi 100% akurat | Sukses (Pass) |
| 5 | White Box | Standardisasi Yeo-Johnson | Transformasi array 7 dimensi via PowerTransformer | Array output berdimensi 7 dengan standardisasi tepat | Sukses (Pass) |
| 6 | White Box | Jarak Euclidean Centroid | Klasifikasi wilayah baru via minimalisasi jarak 7D | Wilayah terklasifikasi pada klaster terdekat secara konsisten | Sukses (Pass) |

Secara keseluruhan, hasil pengujian kotak hitam dan kotak putih mengonfirmasi kelayakan operasional sistem analitik SENUWU secara menyeluruh. Ketiadaan bug pada pemrosesan database dan rendering grafis Plotly WebGL membuktikan bahwa arsitektur sistem dirancang dengan sangat matang. Keandalan integrasi model hibrida dengan antarmuka dinamis Streamlit siap mendukung diseminasi informasi pembangunan regional bagi publik. Dengan demikian, aplikasi ini telah memenuhi standar teknis pendaftaran hak kekayaan intelektual (HKI) untuk kategori program komputer sains data.

BAB VI
KESIMPULAN

6.1 Kesimpulan

Berdasarkan seluruh tahapan pembelajaran berbasis proyek yang telah dilaksanakan, riset ini berhasil membangun model klasterisasi hibrida HDBSCAN dan K-Means untuk menganalisis ketimpangan regional di Indonesia. Penerapan model hibrida ini terbukti mampu mengelompokkan 514 kabupaten dan kota secara stabil berdasarkan tujuh indikator kesejahteraan BPS tahun 2024. Deteksi pencilan spasial menggunakan Isolation Forest secara sukses menyaring 26 daerah berkategori atipikal (outliers) demi menjaga kestabilan klaster utama. Pengujian spasial Moran's I mengonfirmasi adanya autokorelasi geografis yang sangat kuat pada seluruh variabel kesejahteraan nasional.

Hasil pemodelan menghasilkan empat klaster utama yang menggambarkan polarisasi tingkat kesejahteraan regional Indonesia dengan sangat tegas. Klaster Maju dan Urbanized didominasi oleh kota-kota besar di Pulau Jawa yang memiliki kapasitas ekonomi dan pembangunan manusia yang unggul. Sebaliknya, wilayah luar Jawa terutama di bagian Timur Indonesia cenderung masuk ke dalam kategori Berkembang Rentan dan Subsisten Tertinggal dengan angka kemiskinan yang tinggi. Uji asosiasi Cramer's V sebesar 0.6486 memperkuat bukti empiris adanya hubungan spasial yang kuat antara lokasi geografis daerah dengan tingkat kesejahteraannya.

Evaluasi keandalan model menggunakan metrik komposit Welfare Clustering Validity Index (WCVI) menghasilkan nilai akhir sebesar 0.6812 yang menunjukkan kualitas pengelompokan yang sangat tinggi. Sistem pemetaan interaktif SENUWU juga sukses dideploy menggunakan platform Streamlit dengan kinerja rendering yang no-lag berkat teknologi Plotly WebGL. Hasil pengujian fungsionalitas kotak hitam dan kotak putih mengonfirmasi bahwa seluruh fitur aplikasi mulai dari otentikasi sandi hingga prediksi wilayah baru dapat berjalan dengan sukses dan konsisten. Secara umum, aplikasi ini siap menjadi instrumen analitik untuk mendukung formulasi kebijakan berbasis bukti di tingkat pemerintah daerah.

6.2 Saran

Untuk pengembangan penelitian selanjutnya, disarankan untuk memperluas cakupan indikator kesejahteraan dengan mengintegrasikan data spasial secara realtime dari berbagai instansi pemerintah. Penggunaan data yang diperbarui secara otomatis akan meningkatkan kepekaan model dalam menangkap perubahan kondisi sosial ekonomi daerah secara dinamis. Peneliti selanjutnya juga dapat mencoba membandingkan kinerja model hibrida ini dengan algoritma deep clustering atau metode optimasi heuristik lainnya. Variasi eksperimen ini penting untuk terus mengevaluasi dan meningkatkan nilai akurasi klasifikasi regional di masa mendatang.

Pengembangan sistem informasi SENUWU dapat ditingkatkan dengan menambahkan fitur kolaborasi antarpengguna dan modul analisis prediktif berbasis deret waktu (time series). Integrasi fitur ini akan membantu pemerintah daerah tidak hanya melihat kondisi historis tetapi juga memproyeksikan tingkat kesejahteraan di masa depan. Antarmuka aplikasi juga dapat disesuaikan untuk mendukung ekspor data analitik langsung ke dalam format dokumen laporan resmi secara otomatis. Dengan penambahan fungsionalitas tersebut, sistem ini dapat memberikan kontribusi yang lebih optimal bagi perencanaan pembangunan nasional yang adil.

DAFTAR PUSTAKA

Amalia, S., Nikmah, A., & Siniwi, L. M. (2025). Pengelompokan Kemiskinan Di Provinsi Jawa Timur Tahun 2024 Dengan Pendekatan Algoritma K-Means Dan K-Means++. Jurnal Mutiara, 3(8), 407-418. https://doi.org/10.57185/mutiara.v3i8.407

Amelia, Nur, I. M., Rizky, M., & Milasari, S. P. (2023). Poverty Level Grouping in West Java Province with the K-Means Clustering Method. Journal of Diagnostics, 1(2), 152-163. https://doi.org/10.26714/jodi.v1i2.152

Habibi, C., & Nursyanti, R. (2023). Implementasi Algoritma K-Means dan C-Means untuk Clustering Angka Kemiskinan. Jurnal Expert, 13(1), 3107-3118. https://doi.org/10.36448/expert.v13i1.3107

Sabina, S. Z., Alfarez, D. A., Graha, S. S. S., Auladi, M. Y., & Lisa, H. (2024). Pengklasifikasian 10 Kabupaten/Kota di Provinsi Nusa Tenggara Barat untuk Kasus Kemiskinan Tahun 2022 Menggunakan Analisis Cluster Metode K-Means. Indonesian Journal of Applied Statistics and Data Science, 1(1), 5415-5426. https://doi.org/10.29303/ijasds.v1i1.5415

Sundawati, F. H. (2025). Penerapan Center Displacement Fuzzy K-Means untuk Pemetaan Kemiskinan di Pulau Jawa. Journal of Education and History, 5(3), 6857-6868. https://doi.org/10.51878/knowledge.v5i3.6857

LAMPIRAN

Dataset

Code Python Modelling

Manual Book 

Sertifikat HKI

