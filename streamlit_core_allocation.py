import streamlit as st
import pandas as pd
import math
from io import BytesIO
from core_allocation import (
    assign_teacher_kids,
    assign_lively_students_case1,
    assign_lively_students_case2,
    assign_special_case1,
    assign_special_case2
)

st.set_page_config(page_title="Κατανομή Πυρήνα Μαθητών", layout="wide")
st.title("📘 Κατανομή Πυρήνα Μαθητών (Βήματα 1–3)")

uploaded_file = st.file_uploader("📥 Μεταφόρτωση Excel με Μαθητές", type=[".xlsx"])
if uploaded_file:
    df = pd.read_excel(uploaded_file)
    num_classes = math.ceil(len(df) / 25)
    st.success(f"✅ Υπολογίστηκαν {num_classes} τμήματα.")

    df['ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ'] = df.get('ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ', '')

    # Βήμα 1: Παιδιά Εκπαιδευτικών
    df = assign_teacher_kids(df)
    st.info("Βήμα 1: Τοποθετήθηκαν τα παιδιά εκπαιδευτικών.")

    # Βήμα 2: Ζωηροί
    lively_count = len(df[df['ΖΩΗΡΟΣ'] == 'Ν'])
    if lively_count <= num_classes:
        df = assign_lively_students_case1(df)
    else:
        df = assign_lively_students_case2(df)
    st.info("Βήμα 2: Ολοκληρώθηκε η κατανομή ζωηρών μαθητών.")

    # Βήμα 3: Παιδιά με Ιδιαιτερότητες
    special_count = len(df[df['ΙΔΙΑΙΤΕΡΟΤΗΤΑ'] == 'Ν'])
    if special_count <= num_classes:
        df = assign_special_case1(df)
    else:
        df = assign_special_case2(df)
    st.info("Βήμα 3: Ολοκληρώθηκε η κατανομή παιδιών με ιδιαιτερότητες.")

    st.subheader("📊 Προεπισκόπηση Κατανομής Πυρήνα")
    st.dataframe(df[['ΟΝΟΜΑΤΕΠΩΝΥΜΟ', 'ΠΑΙΔΙ ΕΚΠΑΙΔΕΥΤΙΚΟΥ', 'ΖΩΗΡΟΣ', 'ΙΔΙΑΙΤΕΡΟΤΗΤΑ', 'ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ']])

    output = BytesIO()
    df.to_excel(output, index=False)
    st.download_button("📤 Εξαγωγή Πυρήνα σε Excel", data=output.getvalue(), file_name="Πυρήνας_Κατανομής.xlsx")
