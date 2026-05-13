# KOBİ Zeka: AI Destekli Operasyon Yönetim Paneli

**KOBİ Zeka**, küçük ve orta ölçekli işletmelerin dijital dönüşüm süreçlerini hızlandırmak, envanter yönetimini optimize etmek ve satış stratejilerini yapay zeka ile güçlendirmek için geliştirilmiş bir **karar destek sistemidir**.

Bu proje, YZTA Hackathon 2026 kapsamında **Team 299** tarafından geliştirilmiştir.

---

## 🚀 Proje Genel Bakış
İşletme sahiplerinin karmaşık veri tabloları arasında kaybolması yerine; sistem, mevcut stok, satış ve müşteri verilerini analiz ederek işletmeye özel aksiyon planları sunar. Sistem, ham veriyi "anlamlı bilgiye" dönüştüren bir köprü görevi görür.

## 🛠️ Teknik Mimari
Proje, modern yazılım mimarisi prensiplerine uygun olarak üç ana katmanda kurgulanmıştır:

1.  **Makine Öğrenmesi Katmanı:** Geçmiş verilerden öğrenen ve gelecek talebi tahmin eden **LightGBM** tabanlı model.
2.  **Ajan Katmanı (CrewAI):** Belirli iş rollerine bürünmüş (Pazarlama, Satış Tahmini, Güvenlik) otonom ajanların iş birliği.
3.  **Yönetim Paneli (React & FastAPI):** Kullanıcının sistemle doğal dilde etkileşime girdiği ve analiz sonuçlarını görsel olarak takip ettiği arayüz.

---

## 📊 Makine Öğrenmesi ve Tahmin Modeli
Sistemin kalbinde yer alan satış tahminleme modülü şu süreçlerden geçmiştir:
- **Model Seçimi:** Yüksek performanslı ve hızlı eğitim süreci sunan `LightGBM` algoritması tercih edilmiştir.
- **Eğitim Verisi:** Kaggle üzerinden erişilebilen, "Retail Sales Forecasting Dataset" üzerinde değişiklikler yapılıp kullanılmıştır. Zaman serisi analizi, tatil günleri, dönemsel etkiler ve stok değişimleri dikkate alınarak veri mühendisliği yapılmıştır.
- **Ajan Entegrasyonu:** Eğitilen model, bir **Custom Tool** olarak `Oracle Agent`'a bağlanmış; böylece ajanın tahminde bulunurken gerçek ML verilerini kullanması sağlanmıştır.

---

## 🤖 Yapay Zeka Ajanları (Multi-Agent System)
**CrewAI** framework'ü kullanılarak tasarlanan ajanlar, işletme süreçlerini şu şekilde yönetir:

- **Stratejik Satış Tahmincisi (Oracle):** `sales_forecast_tool` aracılığıyla ML modelinden tahminleri alır ve işletme için stratejik yorumlar üretir.
- **Pazarlama Stratejisti (Marketing):** Kritik stok veya stok fazlası durumlarını analiz ederek müşteri segmentlerine özel kampanya kurguları oluşturur.
- **Güvenlik Analisti (Fraud):** İşlem hacmindeki anormal değişimleri ve potansiyel riskli siparişleri denetler.

---

## 💻 Kullanılan Teknolojiler
- **Backend:** Python, FastAPI, SQLAlchemy
- **Frontend:** React.js, CSS3 (Modern Dashboard Tasarımı)
- **AI/LLM:** Google Gemini 3.1 Flash Lite, CrewAI, LangChain
- **Data/ML:** Pandas, Scikit-learn, LightGBM, Joblib
- **Veritabanı:** SQLite

---

## ⚙️ Kurulum ve Kullanım
Projenin yerel ortamda çalıştırılması için gerekli adımlar:

1.  **Bağımlılıkları Yükleyin:** `pip install -r requirements.txt`
2.  **Environment Ayarları:** `.env` dosyasına `GOOGLE_API_KEY` bilgilerinizi ekleyin.
3.  **Backend Başlatma:** `uvicorn app.main:app --reload`
4.  **Frontend Başlatma:** `npm run dev` (Frontend klasörü içerisinde)

---

## 🎯 Projenin Katma Değeri
- **Maliyet Tasarrufu:** Doğru talep tahmini ile gereksiz stok tutma maliyetlerini düşürür.
- **Hızlı Aksiyon:** Veri analizi için harcanan saatleri saniyelere indirir.
- **Akıllı Pazarlama:** Genel kampanyalar yerine veri odaklı, kişiselleştirilmiş pazarlama stratejileri sunar.

**Team 299**