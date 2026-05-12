from crewai_tools import BaseTool

class SupplierAnalysisTool(BaseTool):
    name:str="supplier_analysis_tool"
    description:str="Tedarikçi firmaların (A, B, C) güncel durumlarını ve avantajlarını sunar."

    def _run(self) -> str:
        analysis = (
            "GÜNCEL TEDARİKÇİ DURUM ÇİZELGESİ:\n"
            "- A Firması: Ekspres sevkiyat (24 saat), Prim fiyatlandırma (+%20 maliyet).\n"
            "- B Firması: Endüstriyel standart, toplu alımlarda %10 indirim, 3 gün teslimat.\n"
            "- C Firması: En düşük birim maliyet, 7 gün teslimat, minimum 1 ton sipariş şartı.\n"
        )
        return analysis