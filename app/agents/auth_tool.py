from crewai_tools import BaseTool
from app.database import SessionLocal
from app.models.user import User


class AuthorityCheckTool(BaseTool):
    name: str = "authority_check_tool"
    description: str = "Kullanıcı ismine göre DB'den rol kontrolü yapar ve terminale log basar."

    def _run(self, user_name: str) -> str:
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.name == user_name).first()

            if user:
                role = "USER"
                if hasattr(user, 'is_admin') and user.is_admin:
                    role = "ADMIN"
                elif hasattr(user, 'role') and user.role.upper() == "ADMIN":
                    role = "ADMIN"

                print(f"\n[DEBUG] Veritabanı Kontrolü: {user_name} -> Rol: {role}")
                return role

            print(f"\n[DEBUG] Veritabanı Kontrolü: {user_name} -> Kullanıcı bulunamadı, varsayılan: USER")
            return "USER"

        except Exception as e:
            print(f"\n[DEBUG] DB HATASI: {str(e)} ")
            return "USER"
        finally:
            db.close()