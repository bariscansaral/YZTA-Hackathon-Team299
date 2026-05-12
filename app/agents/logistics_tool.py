from crewai_tools import BaseTool
from app.database import SessionLocal
from app.models.order import Order
from app.models.user import User


class OrderTrackingTool(BaseTool):
    name: str = "order_tracking_tool"
    description: str = "Kullanıcı email adresini alarak siparişlerin durumunu ve içeriğini getirir."

    def _run(self, user_email: str) -> str:
        db = SessionLocal()
        try:

            user = db.query(User).filter(User.email == user_email).first()

            if not user:
                return f"{user_email} adresine sahip bir kullanıcı bulunamadı."

            orders = db.query(Order).filter(Order.user_id == user.id).all()

            if not orders:
                return f"{user_email} adına kayıtlı bir sipariş bulunmamaktadır."

            order_reports = []
            for order in orders:
                items = ", ".join([item.product.name for item in order.items]) if hasattr(order,'items') else "Ürün detayı yok"
                order_reports.append(f"Sipariş ID: {order.id} | Durum: {order.status} | İçerik: {items}")

            return "\n".join(order_reports)

        except Exception as e:
            return f"Sipariş sorgulanırken hata oluştu: {str(e)}"
        finally:
            db.close()