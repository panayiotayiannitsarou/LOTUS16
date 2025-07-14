import streamlit as st
import pandas as pd
import random
import io
from auth import check_password

st.set_page_config(page_title="Κατανομή Μαθητών", layout="wide")

# 🔐 Κλείδωμα με Κωδικό
if check_password():
    st.title("📚 Ψηφιακή Κατανομή Μαθητών Α’ Δημοτικού")

    # 🟢 Ενεργοποίηση/Απενεργοποίηση
    app_enabled = st.checkbox("✅ Ενεργοποίηση κύριας εφαρμογής", value=True)

    if app_enabled:
        # 📅 Εισαγωγή Excel
        uploaded_file = st.file_uploader("📅 Επιλέξτε αρχείο Excel με μαθητές", type=["xlsx"])

        if uploaded_file:
            df = pd.read_excel(uploaded_file)
            st.success("✅ Το αρχείο φορτώθηκε.")
            st.dataframe(df.head())

            if st.button("⚖️ Εκτέλεση Κατανομής Πληθυσμού"):
                # Κατανομή σε τμήματα με μέγιστο 25 ανά τμήμα
                num_students = len(df)
                num_classes = -(-num_students // 25)  # Ceiling division
                class_labels = [chr(913 + i) for i in range(num_classes)]  # 'Α', 'Β', ...
                
                class_assignment = [class_labels[i % num_classes] for i in range(num_students)]
                random.shuffle(class_assignment)
                df['ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ'] = class_assignment

                st.success(f"✅ Οι μαθητές κατανέμηθηκαν σε {num_classes} τμήματα.")
                st.dataframe(df)

                # 📊 Στατιστικά Κατανομής
                if st.checkbox("📊 Προβολή Στατιστικών Κατανομής"):
                    df_stat = df.copy()
                    df_stat['ΑΓΟΡΙ'] = (df_stat['ΦΥΛΟ'] == 'Α').astype(int)
                    df_stat['ΚΟΡΙΤΣΙ'] = (df_stat['ΦΥΛΟ'] == 'Κ').astype(int)
                    df_stat['ΕΚΠΑΙΔΕΥΤΙΚΟΙ'] = (df_stat['ΠΑΙΔΙ ΕΚΠΑΙΔΕΥΤΙΚΟΥ'] == 'Ν').astype(int)
                    df_stat['ΖΩΗΡΟΙ'] = (df_stat['ΖΩΗΡΟΣ'] == 'Ν').astype(int)
                    df_stat['ΙΔΙΑΙΤΕΡΟΤΗΤΑ'] = (df_stat['ΙΔΙΑΙΤΕΡΟΤΗΤΑ'] == 'Ν').astype(int)
                    df_stat['ΓΝΩΣΗ ΕΛΛ.'] = (df_stat['ΚΑΛΗ ΓΝΩΣΗ ΕΛΛΗΝΙΚΩΝ'] == 'Ν').astype(int)
                    df_stat['ΜΑΘΗΣΙΑΚΗ ΙΚ.'] = (df_stat['ΙΚΑΝΟΠΟΙΗΤΙΚΗ ΜΑΘΗΣΙΑΚΗ ΙΚΑΝΟΤΗΤΑ'] == 'Ν').astype(int)

                    stats_table = df_stat.groupby('ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ')[
                        ['ΑΓΟΡΙ', 'ΚΟΡΙΤΣΙ', 'ΕΚΠΑΙΔΕΥΤΙΚΟΙ', 'ΖΩΗΡΟΙ', 'ΙΔΙΑΙΤΕΡΟΤΗΤΑ', 'ΓΝΩΣΗ ΕΛΛ.', 'ΜΑΘΗΣΙΑΚΗ ΙΚ.']
                    ].sum()
                    stats_table['ΣΥΝΟΛΟ'] = df_stat.groupby('ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ').size()
                    stats_table.reset_index(inplace=True)

                    st.dataframe(stats_table)

                # 📝 Εντοπισμός Πυρήνα Μαθητών
                st.subheader("🔍 Εντοπισμός Πυρήνα Κατανομής")
                πυρήνας = df[(df['ΠΑΙΔΙ ΕΚΠΑΙΔΕΥΤΙΚΟΥ'] == 'Ν') | (df['ΖΩΗΡΟΣ'] == 'Ν') | (df['ΙΔΙΑΙΤΕΡΟΤΗΤΑ'] == 'Ν')]
                st.write(f"Βρέθηκαν {len(πυρήνας)} μαθητές στον πυρήνα.")
                st.dataframe(πυρήνας)

                export_buffer = io.BytesIO()
                with pd.ExcelWriter(export_buffer, engine='xlsxwriter') as writer:
                    πυρήνας.to_excel(writer, index=False, sheet_name='Πυρήνας')
                export_buffer.seek(0)

                st.download_button(
                    label="📄 Εξαγωγή Πυρήνα σε Excel",
                    data=export_buffer,
                    file_name="pyhnas_mathiton.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

                # 📄 Εξαγωγή Excel Κατανομής + Στατιστικά
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False, sheet_name='Κατανομή')
                    stats_table.to_excel(writer, index=False, sheet_name='Στατιστικά')
                output.seek(0)

                st.download_button(
                    label="📄 Λήψη Κατανομής Excel",
                    data=output,
                    file_name="katanomi.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
    else:
        st.info("🚫 Η εφαρμογή είναι απενεργοποιημένη.")

    # 📅 Πνευματικά Δικαιώματα
    st.markdown("---")
    st.markdown("© 2025 Παναγιώτα Γιαννίτσαρου – All rights reserved. Δεν επιτρέπεται η αναπαραγωγή ή αναδιανομή χωρίς άδεια.")
else:
    st.stop()
