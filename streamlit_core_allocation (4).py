import pandas as pd
import random
import math
import streamlit as st
from io import BytesIO
from auth import check_password
from core_allocation import (
    assign_teacher_kids,
    assign_lively_students_case1,
    assign_lively_students_case2,
    assign_special_case1,
    assign_special_case2
)

if not check_password():
    st.stop()

st.set_page_config(page_title="Κατανομή Πυρήνα Μαθητών (Βήματα 1–3)", layout="wide")
st.title("📘 Κατανομή Πυρήνα Μαθητών (Βήματα 1–3)")

uploaded_file = st.file_uploader("📥 Μεταφόρτωση Excel με Μαθητές", type=[".xlsx"])
if uploaded_file:
    df = pd.read_excel(uploaded_file)
    num_classes = math.ceil(len(df) / 25)
    st.success(f"✅ Υπολογίστηκαν {num_classes} τμήματα.")

    if 'ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ' not in df.columns:
        df['ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ'] = ''

    # Βήμα 1: Παιδιά Εκπαιδευτικών
    teacher_df = df[df['ΠΑΙΔΙ ΕΚΠΑΙΔΕΥΤΙΚΟΥ'] == 'Ν']
    df = assign_teacher_kids(df, teacher_df)
    st.info("Βήμα 1: Τοποθετήθηκαν τα παιδιά εκπαιδευτικών.")

    # Βήμα 2: Ζωηροί Μαθητές (λαμβάνοντας υπόψη ήδη τοποθετημένους)
    lively_df = df[(df['ΖΩΗΡΟΣ'] == 'Ν') & (df['ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ'] == '')]
    lively_total = len(df[df['ΖΩΗΡΟΣ'] == 'Ν'])  # Για τον κανόνα <= / > τμήματα
    if lively_total <= num_classes:
        df = assign_lively_students_case1(df, lively_df)
    else:
        df = assign_lively_students_case2(df, lively_df)
    st.info("Βήμα 2: Ολοκληρώθηκε η κατανομή ζωηρών μαθητών.")

    # Βήμα 3: Παιδιά με Ιδιαιτερότητες
    special_df = df[(df['ΙΔΙΑΙΤΕΡΟΤΗΤΑ'] == 'Ν') & (df['ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ'] == '')]
    special_total = len(df[df['ΙΔΙΑΙΤΕΡΟΤΗΤΑ'] == 'Ν'])
    if special_total <= num_classes:
        df = assign_special_case1(df, special_df)
    else:
        df = assign_special_case2(df, special_df)
    st.info("Βήμα 3: Ολοκληρώθηκε η κατανομή παιδιών με ιδιαιτερότητες.")

    st.subheader("📋 Προεπισκόπηση Κατανομής Πυρήνα")
    st.dataframe(df[['ΟΝΟΜΑΤΕΠΩΝΥΜΟ', 'ΠΑΙΔΙ ΕΚΠΑΙΔΕΥΤΙΚΟΥ', 'ΖΩΗΡΟΣ', 'ΙΔΙΑΙΤΕΡΟΤΗΤΑ', 'ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ']])

    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Κατανομή Πυρήνα')
    st.download_button("📤 Λήψη Κατανομής Πυρήνα", data=output.getvalue(), file_name="katanomi_pyrina.xlsx")
