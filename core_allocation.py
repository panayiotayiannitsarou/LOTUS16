import pandas as pd
import random
import math


def assign_teacher_kids(df):
    # ... (όπως ήδη υπάρχει)
    return df


def prepare_lively_distribution(df):
    # ... (όπως ήδη υπάρχει)
    return lively_kids, lively_counts


def assign_lively_students_case1(df):
    # ... (όπως ήδη υπάρχει)
    return df


def assign_lively_students_case2(df):
    # ... (όπως ήδη υπάρχει)
    return df


def prepare_special_needs_distribution(df):
    special_kids = df[df['ΙΔΙΑΙΤΕΡΟΤΗΤΑ'] == 'Ν']
    assigned_special = special_kids[special_kids['ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ'] != '']
    special_counts = assigned_special.groupby('ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ').size().to_dict()
    return special_kids, special_counts


def assign_special_case1(df):
    special_kids, special_counts = prepare_special_needs_distribution(df)
    total_students = len(df)
    num_classes = math.ceil(total_students / 25)
    class_labels = [chr(913 + i) for i in range(num_classes)]
    assigned_count = {label: special_counts.get(label, 0) for label in class_labels}
    lively_counts = df[df['ΖΩΗΡΟΣ'] == 'Ν'].groupby('ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ').size().to_dict()
    to_assign = special_kids[special_kids['ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ'] == '']

    for idx, row in to_assign.iterrows():
        candidate_classes = sorted(class_labels, key=lambda x: (assigned_count[x], lively_counts.get(x, 0)))

        for class_label in candidate_classes:
            conflict_ok = True
            if 'ΣΥΓΚΡΟΥΣΗ' in df.columns and isinstance(row['ΣΥΓΚΡΟΥΣΗ'], str):
                conflicts = [x.strip() for x in row['ΣΥΓΚΡΟΥΣΗ'].split(',') if x.strip() != '']
                classmates = df[(df['ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ'] == class_label) &
                                (df['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'].isin(conflicts)) &
                                ((df['ΠΑΙΔΙ ΕΚΠΑΙΔΕΥΤΙΚΟΥ'] == 'Ν') | (df['ΖΩΗΡΟΣ'] == 'Ν'))]
                if not classmates.empty:
                    continue

            friends = []
            if 'ΦΙΛΙΑ' in df.columns and isinstance(row['ΦΙΛΙΑ'], str):
                friends = [x.strip() for x in row['ΦΙΛΙΑ'].split(',') if x.strip() != '']
            mutual_friend_ok = False
            for friend in friends:
                f_row = df[df['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'] == friend]
                if not f_row.empty and f_row.iloc[0]['ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ'] == class_label:
                    if row['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'] in str(f_row.iloc[0].get('ΦΙΛΙΑ', '')):
                        if f_row.iloc[0]['ΠΑΙΔΙ ΕΚΠΑΙΔΕΥΤΙΚΟΥ'] == 'Ν' or f_row.iloc[0]['ΖΩΗΡΟΣ'] == 'Ν':
                            mutual_friend_ok = True
                            break

            same_gender_ok = True
            same_gender = df[(df['ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ'] == class_label) & (df['ΦΥΛΟ'] == row['ΦΥΛΟ'])]
            opposite_gender = df[(df['ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ'] == class_label) & (df['ΦΥΛΟ'] != row['ΦΥΛΟ'])]
            if len(same_gender) > len(opposite_gender):
                same_gender_ok = False

            if same_gender_ok:
                df.at[idx, 'ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ'] = class_label
                assigned_count[class_label] += 1
                break

    return df


def assign_special_case2(df):
    special_kids, special_counts = prepare_special_needs_distribution(df)
    total_students = len(df)
    num_classes = math.ceil(total_students / 25)
    class_labels = [chr(913 + i) for i in range(num_classes)]
    assigned_count = {label: special_counts.get(label, 0) for label in class_labels}
    lively_counts = df[df['ΖΩΗΡΟΣ'] == 'Ν'].groupby('ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ').size().to_dict()
    to_assign = special_kids[special_kids['ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ'] == '']

    for idx, row in to_assign.iterrows():
        candidate_classes = sorted(class_labels, key=lambda x: (assigned_count[x], lively_counts.get(x, 0)))

        for class_label in candidate_classes:
            if 'ΣΥΓΚΡΟΥΣΗ' in df.columns and isinstance(row['ΣΥΓΚΡΟΥΣΗ'], str):
                conflicts = [x.strip() for x in row['ΣΥΓΚΡΟΥΣΗ'].split(',') if x.strip() != '']
                classmates = df[(df['ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ'] == class_label) &
                                (df['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'].isin(conflicts))]
                if not classmates.empty:
                    continue

            friends = []
            if 'ΦΙΛΙΑ' in df.columns and isinstance(row['ΦΙΛΙΑ'], str):
                friends = [x.strip() for x in row['ΦΙΛΙΑ'].split(',') if x.strip() != '']
            mutual_friend_ok = False
            for friend in friends:
                f_row = df[df['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'] == friend]
                if not f_row.empty and f_row.iloc[0]['ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ'] == class_label:
                    if row['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'] in str(f_row.iloc[0].get('ΦΙΛΙΑ', '')):
                        if f_row.iloc[0]['ΠΑΙΔΙ ΕΚΠΑΙΔΕΥΤΙΚΟΥ'] == 'Ν' or f_row.iloc[0]['ΖΩΗΡΟΣ'] == 'Ν':
                            mutual_friend_ok = True
                            break

            all_have_lively = all(label in lively_counts and lively_counts[label] > 0 for label in class_labels)
            same_gender_ok = True
            same_gender = df[(df['ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ'] == class_label) & (df['ΦΥΛΟ'] == row['ΦΥΛΟ'])]
            opposite_gender = df[(df['ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ'] == class_label) & (df['ΦΥΛΟ'] != row['ΦΥΛΟ'])]
            if len(same_gender) > len(opposite_gender):
                same_gender_ok = False

            if same_gender_ok and (not mutual_friend_ok or all_have_lively):
                df.at[idx, 'ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ'] = class_label
                assigned_count[class_label] += 1
                break

    return df
