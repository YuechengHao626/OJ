VALID_LABS = {
    "4CT24811", "4CT41211", "4CT41221", "4CT41231", "4CT41232",
    "4CT41651", "4CT42131", "4CT42132", "4CT42133", "4CT42134",
    "4CT42801", "4CT42851", "4CT42852", "4CT42853", "4CT43111",
    "4CT45151", "4CT45521", "4CT45811", "4CT46601", "ACL24851",
    "ACL40121", "ACL40131", "ACL40191", "ACL40201", "ACL40691",
    "ACL41141", "ACL41151", "ACL41221", "ACL42071", "ACL42151",
    "ACL42161", "ACL42162", "ACL42163", "ACL42171", "ACL42231",
    "ACL42801", "ACL45091", "ACL45092", "ACL45561", "ACL45581",
    "ACL45582", "HAC26021", "QHD40011", "QML40671", "QML41011",
    "QML41201", "QML41202", "QML41203", "QML45701", "QML45702",
    "QML45703", "QML45704", "QML46551", "QML46552", "QML46701",
    "QML46702", "QML46703", "QML47001", "QML47002", "QML47011",
    "QML47012", "QML47401", "QML47402", "QML47403", "QML47404",
    "QML47405", "QML48021", "QML48022", "QML48121", "QML48122",
    "QML48123", "QML48201", "QML48251", "QML48601", "QML48771",
    "QML48791", "SNP40011", "SNP40651", "SNP43051", "SNP45701"
}

def is_valid_lab(lab_id: str) -> bool:
    return lab_id in VALID_LABS

def is_valid_patient_id(patient_id: str) -> bool:
    return patient_id.isdigit() and len(patient_id) == 11