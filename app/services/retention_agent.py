from sqlalchemy.orm import Session
from datetime import datetime
from app.models.user import User

class RetentionAgent:
    def __init__(self, db: Session):
        self.db = db

    def analyze_and_engage(self):
        users = self.db.query(User).all()
        results = []

        for user in users:
            # Eğer kullanıcının son sipariş tarihi yoksa pas geçebiliriz veya yeni diyebiliriz
            if not user.last_order_date:
                days_inactive = 0
                status = "YENİ"
                msg = f"Merhaba {user.name}, ilk siparişine özel %10 indirim seni bekliyor!"
                rec = "Hoş geldin kampanyası."
            else:
                days_inactive = (datetime.now() - user.last_order_date).days
                
                if days_inactive > 60:
                    status = "KAYIP (CHURNED)"
                    msg = f"Selam {user.name}, seni çok özledik! Geri dönmen şerefine sepetinde %10 indirim tanımladık."
                    rec = "Şok indirim stratejisi."
                elif days_inactive > 30:
                    status = "RİSKLİ (AT RISK)"
                    msg = f"Merhaba {user.name}, bir süredir yoksun. Favori ürünlerin stokta, göz atmak ister misin?"
                    rec = "Hatırlatma stratejisi."
                else:
                    status = "AKTİF"
                    msg = f"Harikasın {user.name}! Bizi tercih ettiğin için teşekkürler."
                    rec = "Bağlılık teşekkürü."

            results.append({
                "user_id": user.id,
                "days_since_last_order": days_inactive,
                "status": status,
                "recommendation": rec,
                "generated_message": msg
            })
        
        return results