"""
Configuration spécifique au système éducatif camerounais.
"""

# CLASSE/NIVEAUX CAMEROUNAIS
CAMEROON_PRIMARY_LEVELS = {
    # Maternelle (3 ans)
    "PRE_NURSERY": {"code": "PREN", "name": "Pre-nursery", "cycle": "maternelle", "age": 4},
    "NURSERY_1": {"code": "NUR1", "name": "Nursery 1", "cycle": "maternelle", "age": 5},
    "NURSERY_2": {"code": "NUR2", "name": "Nursery 2", "cycle": "maternelle", "age": 6},
    
    # Primaire (6 ans) - Français
    "SIL": {"code": "SIL", "name": "SIL", "cycle": "primaire", "age": 6, "lang": "fr"},
    "CP": {"code": "CP", "name": "Cours Préparatoire", "cycle": "primaire", "age": 7, "lang": "fr"},
    "CE1": {"code": "CE1", "name": "Cours Élémentaire 1", "cycle": "primaire", "age": 8, "lang": "fr"},
    "CE2": {"code": "CE2", "name": "Cours Élémentaire 2", "cycle": "primaire", "age": 9, "lang": "fr"},
    "CM1": {"code": "CM1", "name": "Cours Moyen 1", "cycle": "primaire", "age": 10, "lang": "fr"},
    "CM2": {"code": "CM2", "name": "Cours Moyen 2", "cycle": "primaire", "age": 11, "lang": "fr"},
    
    # Primaire (6 ans) - Anglais
    "CLASS_1": {"code": "CLS1", "name": "Class 1", "cycle": "primaire", "age": 6, "lang": "en"},
    "CLASS_2": {"code": "CLS2", "name": "Class 2", "cycle": "primaire", "age": 7, "lang": "en"},
    "CLASS_3": {"code": "CLS3", "name": "Class 3", "cycle": "primaire", "age": 8, "lang": "en"},
    "CLASS_4": {"code": "CLS4", "name": "Class 4", "cycle": "primaire", "age": 9, "lang": "en"},
    "CLASS_5": {"code": "CLS5", "name": "Class 5", "cycle": "primaire", "age": 10, "lang": "en"},
    "CLASS_6": {"code": "CLS6", "name": "Class 6", "cycle": "primaire", "age": 11, "lang": "en"},
}

# TYPES DE FRAIS (Cameroun)
CAMEROON_FEE_TYPES = {
    "INSCRIPTION": {"code": "INSC", "name": "Frais d'inscription"},
    "SCOLARITE": {"code": "SCOL", "name": "Frais de scolarité"},
    "CANTINE": {"code": "CANT", "name": "Frais de cantine"},
    "UNIFORME": {"code": "UNIF", "name": "Uniforme scolaire"},
    "MATERIEL": {"code": "MAT", "name": "Matériel pédagogique"},
    "ACTIVITES": {"code": "ACT", "name": "Activités extra-scolaires"},
    "TRANSPORT": {"code": "TRANSP", "name": "Transport scolaire"},
    "ASSURANCE": {"code": "ASSU", "name": "Assurance scolaire"},
}

# MATIÈRES ENSEIGNÉES (Primaire Cameroun)
CAMEROON_SUBJECTS = {
    # Matières principales
    "FRANCAIS": {"code": "FR", "name": "Français", "coefficient": 2},
    "MATHEMATIQUES": {"code": "MATH", "name": "Mathématiques", "coefficient": 2},
    "SCIENCES": {"code": "SCI", "name": "Sciences", "coefficient": 1},
    "HISTOIRE_GEO": {"code": "HG", "name": "Histoire-Géographie", "coefficient": 1},
    "CIVISME": {"code": "CIV", "name": "Civisme et Éducation Morale", "coefficient": 1},
    "EPS": {"code": "EPS", "name": "Éducation Physique et Sportive", "coefficient": 1},
    "ANGLAIS": {"code": "EN", "name": "Anglais", "coefficient": 1},
    "INFORMATIQUE": {"code": "INFO", "name": "Informatique", "coefficient": 1},
    "ARTS": {"code": "ARTS", "name": "Arts Plastiques", "coefficient": 1},
    "MUSIQUE": {"code": "MUS", "name": "Musique", "coefficient": 1},
}

# CALENDRIER SCOLAIRE CAMEROUN
CAMEROON_ACADEMIC_YEAR_PATTERN = {
    "SEQUENCE_1": {"start_month": 9, "end_month": 11, "name": "Séquence 1"},
    "SEQUENCE_2": {"start_month": 12, "end_month": 12, "name": "Séquence 2"},
    "SEQUENCE_3": {"start_month": 1, "end_month": 3, "name": "Séquence 3"},
    "SEQUENCE_4": {"start_month": 4, "end_month": 6, "name": "Séquence 4"},
}

# RÔLES SUPPLÉMENTAIRES CAMEROUN
CAMEROON_ROLES = {
    "SUPER_ADMIN": "Super Administrateur",
    "COMPTABLE": "Comptable",
    "DIRECTEUR": "Directeur d'école",
    "ENSEIGNANT": "Enseignant",
    "PARENT": "Parent/Tuteur",
}

# STATUS COMPTES PARENTS
ACCOUNT_STATUS = {
    "ACTIVE": "Actif",
    "SUSPENDED": "Suspendu",
    "INACTIVE": "Inactif",
}

# STATUS PRÉSENCE
ATTENDANCE_STATUS = {
    "PRESENT": "Présent",
    "ABSENT": "Absent",
    "RETARD": "En retard",
    "ABSENT_JUSTIFIE": "Absent justifié",
}

# PERIODS D'ÉVALUATION (Séquences)
# The Cameroon setup uses 6 sequences distributed across 3 trimesters.
# Dates for sequences are defined by the administrator per academic year.
SEQUENCES = {
    "SEQ_1": {"number": 1, "name": "Séquence 1", "trimester": 1, "start_date": None, "end_date": None},
    "SEQ_2": {"number": 2, "name": "Séquence 2", "trimester": 1, "start_date": None, "end_date": None},
    "SEQ_3": {"number": 3, "name": "Séquence 3", "trimester": 2, "start_date": None, "end_date": None},
    "SEQ_4": {"number": 4, "name": "Séquence 4", "trimester": 2, "start_date": None, "end_date": None},
    "SEQ_5": {"number": 5, "name": "Séquence 5", "trimester": 3, "start_date": None, "end_date": None},
    "SEQ_6": {"number": 6, "name": "Séquence 6", "trimester": 3, "start_date": None, "end_date": None},
}

# Single-school deployment flag: this project instance manages a single school.
SINGLE_SCHOOL = True

# Note: Subjects are expected to be defined per class by the administrator.
# CAMEROON_SUBJECTS may be used as templates but final subjects should be
# created/assigned by an admin through the admin API per class/level.
