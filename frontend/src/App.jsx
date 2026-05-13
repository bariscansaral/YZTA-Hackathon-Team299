import { useState } from "react";
import "./App.css";

const pages = {
  overview: "Genel Bakış",
  stock: "Stok Yönetimi",
  orders: "Siparişler",
  cargo: "Kargo Takibi",
  customers: "Müşteri Soruları",
  insights: "Satış İçgörüleri",
  settings: "Ayarlar",
};

const menu = [
  ["overview", "🏠", "Genel Bakış"],
  ["stock", "📦", "Stok Yönetimi"],
  ["orders", "🛒", "Siparişler"],
  ["cargo", "🚚", "Kargo Takibi"],
  ["customers", "💬", "Müşteri Soruları"],
  ["insights", "📈", "Satış İçgörüleri"],
  ["settings", "⚙️", "Ayarlar"],
];

const data = {
  overview: [
    ["Bugünkü Sipariş", "38", "+12% düne göre"],
    ["Kritik Stok", "7", "3 ürün acil yenilenmeli"],
    ["Bekleyen Kargo", "14", "3 gecikme riski"],
    ["Cevaplanan Talep", "126", "AI ile otomatik"],
  ],
  stock: [
    ["Toplam Ürün", "184", "7 kritik stok"],
    ["Yenileme Önerisi", "12", "AI tedarik önerisi"],
    ["Stok Değeri", "₺86.420", "+8% bu ay"],
    ["Riskli Ürün", "3", "Hızlı tükenen ürün"],
  ],
  orders: [
    ["Yeni Sipariş", "38", "Bugün"],
    ["Hazırlanıyor", "14", "Depoda"],
    ["Tamamlandı", "92", "Bu hafta"],
    ["İptal", "2", "Düşük risk"],
  ],
  cargo: [
    ["Yolda", "14", "Aktif gönderi"],
    ["Gecikme Riski", "3", "Müşteri bilgilendirilmeli"],
    ["Teslim Edildi", "41", "Bu hafta"],
    ["İade", "1", "Kontrol gerekli"],
  ],
  customers: [
    ["Yeni Soru", "27", "Bugün"],
    ["AI Yanıtladı", "126", "Otomatik"],
    ["İnsan Gerekli", "5", "Öncelikli"],
    ["Memnuniyet", "%91", "+6 puan"],
  ],
  insights: [
    ["Haftalık Ciro", "₺128.540", "+18%"],
    ["En Çok Satan", "Kahve Paketi", "42 adet"],
    ["Tahmini Talep", "+24%", "Gelecek hafta"],
    ["Kampanya Fırsatı", "3", "Segment hazır"],
  ],
  settings: [
    ["Mağaza", "Demo KOBİ", "Aktif"],
    ["AI Modu", "Demo", "Backend bağlanacak"],
    ["Dil", "Türkçe", "Varsayılan"],
    ["Tema", "KOBİ Turuncu", "Aktif"],
  ],
};

function App() {
  const [activePage, setActivePage] = useState("overview");
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      text: "Merhaba 👋 Ben KOBİ AI Asistanınız. Sipariş, stok, kargo ve müşteri taleplerini tek ekrandan yönetmenize yardımcı olurum.",
    },
  ]);
  const [input, setInput] = useState("");

  const sendMessage = (customText) => {
    const text = customText || input;
    if (!text.trim()) return;

    setMessages([
      ...messages,
      { role: "user", text },
      {
        role: "assistant",
        text: `"${text}" için demo yanıt oluşturdum. Backend bağlandığında gerçek verilerle analiz yapacağım.`,
      },
    ]);
    setInput("");
  };

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="logoCard">
          <div className="academyLogo">
            <span className="roof"></span>
            <span className="bar red"></span>
            <span className="bar yellow"></span>
            <span className="bar green"></span>
            <span className="base"></span>
          </div>
          <div>
            <h2>KOBİ Zeka</h2>
            <p>YZTA AI Operasyon Paneli</p>
          </div>
        </div>

        <nav className="menu">
          {menu.map(([id, icon, label]) => (
            <button
              key={id}
              className={activePage === id ? "active" : ""}
              onClick={() => setActivePage(id)}
            >
              {icon} {label}
            </button>
          ))}
        </nav>

        <div className="sideNote">
          <strong>Bugünün odağı</strong>
          <p>7 ürün kritik stokta. 3 kargo gecikme riski taşıyor.</p>
        </div>
      </aside>

      <main className="main">
        <header className="header">
          <div>
            <span className="eyebrow">KOBİ’ler için yapay zeka destekli kontrol merkezi</span>
            <h1>{pages[activePage]}</h1>
            <p>
              Siparişleri, stokları, kargo durumlarını ve müşteri taleplerini
              tek ekranda takip et. AI önerileriyle hızlı aksiyon al.
            </p>
          </div>

          <button className="primaryBtn" onClick={() => sendMessage("Günlük özeti çıkar")}>
            Günlük Özeti Al
          </button>
        </header>

        <section className="cards">
          {data[activePage].map(([title, value, note]) => (
            <div className="card" key={title}>
              <span>{title}</span>
              <strong>{value}</strong>
              <small>{note}</small>
            </div>
          ))}
        </section>

        <section className="grid">
          <div className="panel large">
            <div className="panelHead">
              <h3>{activePage === "stock" ? "Stok Risk Trendi" : "Satış ve Talep Trendi"}</h3>
              <span>Son 7 gün</span>
            </div>

            <div className="lineChart">
              <svg viewBox="0 0 600 220" preserveAspectRatio="none">
                <path
                  d="M0,170 C70,120 120,150 180,95 C240,40 300,150 360,105 C430,55 480,80 600,35"
                  fill="none"
                  stroke="#f97316"
                  strokeWidth="5"
                  strokeLinecap="round"
                />
                <path
                  d="M0,170 C70,120 120,150 180,95 C240,40 300,150 360,105 C430,55 480,80 600,35 L600,220 L0,220 Z"
                  fill="url(#orangeFade)"
                />
                <defs>
                  <linearGradient id="orangeFade" x1="0" y1="0" x2="0" y2="1">
                    <stop stopColor="#fb923c" stopOpacity="0.28" />
                    <stop offset="1" stopColor="#fb923c" stopOpacity="0" />
                  </linearGradient>
                </defs>
              </svg>
            </div>
          </div>

          <div className="panel">
            <h3>AI Aksiyon Önerileri</h3>
            <div className="suggestion">
              <b>📦 Stok yenile</b>
              <p>Kahve paketi stoğu 2 gün içinde bitebilir.</p>
            </div>
            <div className="suggestion">
              <b>🚚 Kargo uyarısı</b>
              <p>3 sipariş için müşteriye bilgilendirme mesajı hazırlanmalı.</p>
            </div>
            <div className="suggestion">
              <b>💬 Müşteri yanıtı</b>
              <p>“Ürün stokta mı?” soruları otomatik cevaplanabilir.</p>
            </div>
          </div>
        </section>

        <section className="panel tablePanel">
          <div className="panelHead">
            <h3>{pages[activePage]} Özeti</h3>
            <button onClick={() => sendMessage(`${pages[activePage]} için detaylı rapor hazırla`)}>
              Tümünü Gör
            </button>
          </div>

          <div className="table">
            <div className="head">Kayıt</div>
            <div className="head">Kategori</div>
            <div className="head">Durum</div>
            <div className="head">AI Önerisi</div>

            <div>#10254 - Ahmet Yılmaz</div>
            <div>Sipariş</div>
            <div><span className="ok">Hazırlanıyor</span></div>
            <div>Kargo etiketi oluştur</div>

            <div>Kahve Paketi 250gr</div>
            <div>Stok</div>
            <div><span className="warn">Kritik</span></div>
            <div>50 adet sipariş öner</div>

            <div>#10248 - Zeynep Kaya</div>
            <div>Kargo</div>
            <div><span className="danger">Gecikme riski</span></div>
            <div>Müşteriye mesaj hazırla</div>
          </div>
        </section>
      </main>

      <aside className="assistant">
        <div className="assistantHead">
          <div className="bot">✦</div>
          <div>
            <h3>KOBİ AI Asistan</h3>
            <span>Çevrimiçi</span>
          </div>
        </div>

        <div className="chat">
          {messages.map((m, i) => (
            <div key={i} className={`message ${m.role}`}>
              {m.text}
            </div>
          ))}
        </div>

        <div className="quick">
          <button onClick={() => sendMessage("Bugünkü siparişleri özetle")}>
            Bugünkü siparişleri özetle
          </button>
          <button onClick={() => sendMessage("Stokta azalan ürünleri göster")}>
            Stokta azalan ürünleri göster
          </button>
          <button onClick={() => sendMessage("Geciken kargolar var mı?")}>
            Geciken kargolar var mı?
          </button>
        </div>

        <div className="inputBox">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Asistana sor..."
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
          />
          <button onClick={() => sendMessage()}>➜</button>
        </div>
      </aside>
    </div>
  );
}

export default App;