# app.py
import streamlit as st
import pandas as pd
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from io import BytesIO

st.set_page_config(page_title="مولد تقارير تقييم العروض", layout="wide")
st.markdown("<h1 style='text-align: center;'>مولد تقارير تقييم العروض</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center;'>مثل تقرير 09/2025 - بنزرت</h3>", unsafe_allow_html=True)

# === En-tête ===
header = """
<div style='text-align: center; margin-bottom: 20px;'>
    <h2>الجمهورية التونسية</h2>
    <p>وزارة الفلاحة والموارد المائية والصيد البحري</p>
    <p>المندوبية الجهوية للتنمية الفلاحية ببنزرت</p>
    <hr/>
    <h2>تقرير تقييم العروض</h2>
</div>
"""
st.markdown(header, unsafe_allow_html=True)

# === بيانات عامة ===
with st.expander("بيانات التقرير", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        tender_number = st.text_input("رقم الإعلان", "09/2025")
        tender_date = st.date_input("تاريخ الإعلان", datetime(2025, 9, 1))
    with col2:
        region = st.text_input("الولاية", "بنزرت")
        authority = st.text_input("الجهة", "المندوبية الجهوية")

# === الأقساط ===
lots = []
for i in range(1, 4):
    st.markdown(f"#### القسط {i}")
    col1, col2, col3 = st.columns(3)
    with col1:
        lot_name = st.text_input(f"اسم القسط {i}", f"القسط {i}", key=f"name{i}")
    with col2:
        estimate = st.number_input(f"تقديرات الإدارة", value=45000.0, key=f"est{i}")
    with col3:
        company = st.text_input(f"الشركة", "CAP BON EMIHEM" if i <= 2 else "EGBAT", key=f"comp{i}")
    bid = st.number_input(f"العرض المالي", value=52645.6 if i == 1 else 35033.6 if i == 2 else 174811.0, key=f"bid{i}")
    lots.append({"lot": lot_name, "company": company, "bid": bid, "estimate": estimate})

# === توليد PDF ===
def create_pdf():
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=20*mm)
    elements = []
    styles = getSampleStyleSheet()
    styles['Title'].alignment = TA_CENTER
    styles['Normal'].alignment = TA_RIGHT
    styles['Normal'].fontName = 'Arabic'

    elements.append(Paragraph("تقرير تقييم العروض", styles['Title']))
    elements.append(Paragraph(f"رقم {tender_number} - تاريخ {tender_date.strftime('%Y/%m/%d')}", styles['Title']))
    elements.append(Spacer(1, 12))

    data = [["القسط", "الشركة", "العرض (د.ت)", "التقديرات", "الفرق %"]]
    for l in lots:
        diff = (l['bid'] - l['estimate']) / l['estimate'] * 100
        data.append([l['lot'], l['company'], f"{l['bid']:,.3f}", f"{l['estimate']:,.3f}", f"{diff:.1f}%"])

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#4472C4')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('FONTNAME', (0,0), (-1,-1), 'Arabic'),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 20))
    elements.append(Paragraph(f"تحرير في: {datetime.now().strftime('%Y/%m/%d %H:%M')}", styles['Normal']))

    doc.build(elements)
    return buffer.getvalue()

if st.button("توليد التقرير PDF"):
    pdf = create_pdf()
    st.download_button("تحميل التقرير", pdf, f"تقرير_{tender_number}.pdf", "application/pdf")
    st.success("تم إنشاء التقرير بنجاح!")
