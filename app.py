# app.py
import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from io import BytesIO
from datetime import datetime

st.set_page_config(page_title="تقرير تقييم العروض", layout="wide")
st.markdown("<h1 style='text-align: center;'>مولد تقارير تقييم العروض</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center;'>مثل تقرير 09/2025 - بنزرت</h3>", unsafe_allow_html=True)

# === بيانات التقرير ===
with st.expander("بيانات عامة", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        tender_number = st.text_input("رقم الإعلان", "09/2025")
        tender_date = st.date_input("تاريخ الإعلان", datetime(2025, 9, 1))
    with col2:
        region = st.text_input("الولاية", "بنزرت")
        authority = st.text_input("الجهة", "المندوبية الجهوية للتنمية الفلاحية")

# === الأقساط ===
lots = []
for i in range(1, 4):
    st.markdown(f"#### القسط {i}")
    col1, col2, col3 = st.columns(3)
    with col1:
        lot_name = st.text_input(f"اسم القسط {i}", f"القسط {i}", key=f"name{i}")
    with col2:
        estimate = st.number_input(f"تقديرات الإدارة (د.ت)", value=45101.0 if i == 1 else 32695.25 if i == 2 else 100733.5, key=f"est{i}")
    with col3:
        company = st.text_input(f"الشركة", "CAP BON EMIHEM" if i <= 2 else "EGBAT", key=f"comp{i}")
    bid = st.number_input(f"العرض المالي (د.ت)", value=52645.6 if i == 1 else 35033.6 if i == 2 else 174811.0, key=f"bid{i}")
    lots.append({"lot": lot_name, "company": company, "bid": bid, "estimate": estimate})

# === توليد PDF ===
def create_pdf():
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=20*mm, bottomMargin=15*mm, leftMargin=15*mm, rightMargin=15*mm)
    elements = []
    styles = getSampleStyleSheet()
    styles['Title'].alignment = TA_CENTER
    styles['Title'].fontSize = 14
    styles['Normal'].alignment = TA_RIGHT
    styles['Normal'].fontName = 'DejaVuSans'  # خط عربي

    # عنوان
    elements.append(Paragraph("تقرير تقييم العروض", styles['Title']))
    elements.append(Paragraph(f"طلب عروض رقم {tender_number} - {tender_date.strftime('%Y/%m/%d')}", styles['Title']))
    elements.append(Spacer(1, 12))

    # جدول الأقساط
    data = [["القسط", "الشركة", "العرض (د.ت)", "التقديرات (د.ت)", "الفرق %"]]
    for l in lots:
        diff = (l['bid'] - l['estimate']) / l['estimate'] * 100 if l['estimate'] > 0 else 0
        data.append([l['lot'], l['company'], f"{l['bid']:,.3f}", f"{l['estimate']:,.3f}", f"{diff:+.1f}%"])

    table = Table(data, colWidths=[80, 120, 90, 90, 70])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#4472C4')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('FONTNAME', (0,0), (-1,-1), 'DejaVuSans'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 20))
    elements.append(Paragraph(f"تاريخ الإنشاء: {datetime.now().strftime('%Y/%m/%d %H:%M')}", styles['Normal']))

    doc.build(elements)
    return CDbuffer.getvalue()

if st.button("توليد التقرير PDF"):
    pdf = create_pdf()
    st.download_button(
        label="تحميل التقرير (PDF)",
        data=pdf,
        file_name=f"تقرير_تقييم_العروض_{tender_number.replace('/', '-')}.pdf",
        mime="application/pdf"
    )
    st.success("تم إنشاء التقرير بنجاح!")
