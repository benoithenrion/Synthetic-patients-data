"""
Factor phrases for synthetic data generation and evaluation.
Contains positive and negative phrases for each ColectomieFactors field.
"""

# Phrases personnalisées pour chaque facteur (positives et négatives)
FACTOR_PHRASES = {
    "BMI_eleve": {
        "positive": [
            "Le patient présente un surpoids avec un IMC de {bmi} kg/m².",
            "BMI calculé à {bmi} kg/m², indiquant un surpoids.",
            "Patient obèse avec IMC à {bmi} kg/m².",
        ],
        "negative": [
            "IMC normal à {bmi} kg/m².",
            "Pas de surpoids documenté. IMC : {bmi} kg/m².",
            "Patient normopondéral (IMC {bmi} kg/m²).",
        ],
    },
    "denutrition": {
        "positive": [
            "Dénutrition sévère constatée avec perte de poids de {poids_perte} kg en 3 mois.",
            "Patient dénutri : albumine basse à {albumine} g/L, amaigrissement visible.",
            "Hypoalbuminémie à {albumine} g/L témoignant d'une dénutrition.",
        ],
        "negative": [
            "Pas de dénutrition. Albumine normale à {albumine} g/L.",
            "État nutritionnel satisfaisant, pas de perte de poids.",
            "Bon état nutritionnel général.",
        ],
    },
    "anemie": {
        "positive": [
            "Anémie préopératoire avec hémoglobine à {hb} g/dL.",
            "Hb préop basse : {hb} g/dL, transfusion envisagée.",
            "Anémie modérée (Hb {hb} g/dL) documentée avant chirurgie.",
        ],
        "negative": [
            "Hémoglobine normale à {hb} g/dL.",
            "Pas d'anémie préopératoire (Hb {hb} g/dL).",
            "Bilan hématologique préopératoire normal.",
        ],
    },
    "diabete": {
        "positive": [
            "Diabète de type 2 sous metformine et insuline.",
            "Patient diabétique, HbA1c à {hba1c}%, équilibre glycémique médiocre.",
            "Antécédent de diabète traité par antidiabétiques oraux.",
            "| Diabète | O |",
        ],
        "negative": [
            "Pas de diabète connu.",
            "Glycémie à jeun normale, pas de diabète.",
            "Aucun antécédent de diabète.",
        ],
    },
    "hta": {
        "positive": [
            "HTA connue sous traitement par ramipril et amlodipine.",
            "Hypertension artérielle traitée, TA préop {ta_sys}/{ta_dias} mmHg.",
            "Patient hypertendu, suivi régulier en cardiologie.",
            "| HTA | O |",
        ],
        "negative": [
            "Pas d'HTA. TA préop normale à {ta_sys}/{ta_dias} mmHg.",
            "Tension artérielle normale, pas d'antécédent d'HTA.",
            "Aucune hypertension documentée.",
        ],
    },
    "bpco": {
        "positive": [
            "BPCO sévère, dyspnée au moindre effort, sous oxygène à domicile.",
            "Patient BPCO GOLD {gold}, tabagisme actif {tabac} PA.",
            "Bronchopneumopathie chronique obstructive documentée, exacerbations fréquentes.",
            "| BPCO | O |",
        ],
        "negative": [
            "Pas de BPCO connue, fonction respiratoire normale.",
            "Aucun antécédent respiratoire chronique.",
            "Fonction pulmonaire normale, pas de BPCO.",
        ],
    },
    "adenocarcinome": {
        "positive": [
            "Adénocarcinome colique confirmé par biopsie, stade T{t_stage}N{n_stage}.",
            "Cancer du côlon diagnostiqué, indication opératoire oncologique.",
            "Tumeur maligne du côlon gauche, adénocarcinome bien différencié.",
        ],
        "negative": [
            "Pas de néoplasie maligne identifiée.",
            "Indication chirurgicale bénigne.",
            "Anatomopathologie bénigne, pas de cancer.",
        ],
    },
    "sigmoidite_abcedee": {
        "positive": [
            "Sigmoidite diverticulaire compliquée d'abcès pelvien de {taille_abces} cm.",
            "Tableau de diverticulite aiguë avec collection abcédée au scanner.",
            "Abcès péri-sigmoïdien nécessitant drainage chirurgical urgent.",
        ],
        "negative": [
            "Pas de sigmoidite abcédée.",
            "Diverticulose non compliquée.",
            "Aucun abcès identifié au scanner.",
        ],
    },
    "volvulus_caecal": {
        "positive": [
            "Volvulus du caecum confirmé au scanner, urgence chirurgicale.",
            "Torsion caecale avec dilatation importante, indication opératoire en urgence.",
            "Volvulus du côlon droit nécessitant hémicolectomie droite urgente.",
        ],
        "negative": [
            "Pas de volvulus.",
            "Scanner abdominal normal, pas de torsion intestinale.",
            "Aucun signe de volvulus caecal.",
        ],
    },
    "colite_ischemique": {
        "positive": [
            "Colite ischémique du côlon gauche avec nécrose partielle au scanner.",
            "Ischémie colique documentée, nécessitant résection segmentaire.",
            "Aspect de souffrance ischémique du côlon à la coloscopie.",
        ],
        "negative": [
            "Pas de colite ischémique.",
            "Vascularisation colique normale.",
            "Aucun signe d'ischémie intestinale.",
        ],
    },
    "inflammation": {
        "positive": [
            "Syndrome inflammatoire majeur : CRP à {crp} mg/L, leucocytes {leuco}/mm³.",
            "Inflammation sévère avec CRP > 200 mg/L et hyperleucocytose.",
            "État septique avec marqueurs inflammatoires très élevés.",
        ],
        "negative": [
            "CRP normale à {crp} mg/L.",
            "Pas de syndrome inflammatoire biologique.",
            "Bilan inflammatoire négatif.",
        ],
    },
    "laparoscopique": {
        "positive": [
            "Colectomie réalisée par voie laparoscopique sans difficulté.",
            "Chirurgie cœlioscopique réussie, 4 trocarts utilisés.",
            "Intervention mini-invasive par laparoscopie.",
        ],
        "negative": [
            "Chirurgie ouverte d'emblée (laparotomie).",
            "Pas d'approche laparoscopique.",
            "Laparotomie médiane réalisée.",
        ],
    },
    "laparotomie": {
        "positive": [
            "Laparotomie médiane réalisée d'emblée.",
            "Chirurgie ouverte par incision médiane xypho-pubienne.",
            "Laparotomie exploratrice avec résection colique.",
        ],
        "negative": [
            "Pas de laparotomie, chirurgie laparoscopique.",
            "Approche mini-invasive exclusive.",
            "Aucune conversion en laparotomie.",
        ],
    },
    "conversion_laparotomie": {
        "positive": [
            "Conversion en laparotomie pour adhérences majeures.",
            "Échec de la voie laparoscopique, conversion nécessaire.",
            "Laparotomie de conversion après {duree_laparo} min de cœlioscopie.",
        ],
        "negative": [
            "Pas de conversion, chirurgie laparoscopique complète.",
            "Intervention menée à bien par laparoscopie sans conversion.",
            "Aucune conversion nécessaire.",
        ],
    },
    "colectomie_sigmoidienne": {
        "positive": [
            "Sigmoidectomie réalisée avec anastomose colo-rectale.",
            "Résection sigmoïdienne pour diverticulite récidivante.",
            "Colectomie segmentaire sigmoïdienne.",
        ],
        "negative": [
            "Pas de colectomie sigmoïdienne.",
            "Autre type de résection colique.",
            "Chirurgie ne concernant pas le sigmoïde.",
        ],
    },
    "colectomie_gauche": {
        "positive": [
            "Hémicolectomie gauche avec anastomose colo-colique.",
            "Résection du côlon gauche descendant.",
            "Colectomie gauche étendue.",
        ],
        "negative": [
            "Pas d'hémicolectomie gauche.",
            "Résection limitée au sigmoïde.",
            "Autre localisation de résection.",
        ],
    },
    "colectomie_droite": {
        "positive": [
            "Hémicolectomie droite avec anastomose iléo-colique.",
            "Résection du côlon droit et caecum.",
            "Colectomie droite élargie au colon transverse.",
        ],
        "negative": [
            "Pas d'hémicolectomie droite.",
            "Résection colique gauche uniquement.",
            "Chirurgie ne concernant pas le côlon droit.",
        ],
    },
    "sonde_nasogastrique": {
        "positive": [
            "Sonde nasogastrique mise en place en postopératoire pour vomissements.",
            "SNG posée au J{jour} postop pour distension abdominale.",
            "Aspiration gastrique nécessaire, SNG en place.",
        ],
        "negative": [
            "Pas de sonde nasogastrique.",
            "Reprise alimentaire sans SNG.",
            "Aucune aspiration gastrique nécessaire.",
        ],
    },
    "drain_abdominal": {
        "positive": [
            "Drain de Redon laissé en place en postopératoire.",
            "Drainage abdominal en fosse iliaque gauche.",
            "Drain aspiratif ramenant {quantite_drain} mL/24h.",
        ],
        "negative": [
            "Pas de drain abdominal.",
            "Chirurgie sans drainage.",
            "Aucun drain laissé en place.",
        ],
    },
    "stomie": {
        "positive": [
            "Iléostomie de protection confectionnée.",
            "Colostomie terminale réalisée (intervention de Hartmann).",
            "Stomie temporaire prévue pour fermeture à 3 mois.",
        ],
        "negative": [
            "Pas de stomie.",
            "Anastomose sans stomie de protection.",
            "Rétablissement de continuité sans dérivation.",
        ],
    },
    "infection_postop": {
        "positive": [
            "Infection de paroi au J{jour} postop, pus collecté.",
            "Abcès de paroi drainé au lit, antibiothérapie débutée.",
            "Suppuration de la plaie opératoire à J{jour}.",
        ],
        "negative": [
            "Pas d'infection de paroi.",
            "Cicatrisation normale, pas de suppuration.",
            "Aucune infection du site opératoire.",
        ],
    },
    "infection_urinaire": {
        "positive": [
            "Infection urinaire documentée (ECBU positif à E. coli).",
            "Cystite postopératoire traitée par antibiotiques.",
            "Leucocyturie et bactériurie, IU confirmée.",
        ],
        "negative": [
            "Pas d'infection urinaire.",
            "ECBU stérile.",
            "Aucune infection urinaire documentée.",
        ],
    },
    "ileus_postop": {
        "positive": [
            "Iléus postopératoire prolongé jusqu'à J{jour}.",
            "Reprise du transit retardée, iléus réflexe.",
            "Paralysie intestinale transitoire, amélioration progressive.",
        ],
        "negative": [
            "Transit repris à J{jour}, pas d'iléus.",
            "Reprise du transit normale.",
            "Aucun iléus postopératoire.",
        ],
    },
    "occlusion_intestinale": {
        "positive": [
            "Occlusion intestinale sur bride au J{jour} postop.",
            "Tableau occlusif nécessitant reprise chirurgicale.",
            "Sub-occlusion résolue sous traitement conservateur.",
        ],
        "negative": [
            "Pas d'occlusion postopératoire.",
            "Transit normal, aucun syndrome occlusif.",
            "Aucune occlusion documentée.",
        ],
    },
    "lachage_suture": {
        "positive": [
            "Fistule anastomotique diagnostiquée au J{jour} postop.",
            "Lâchage de suture confirmé au scanner, collection péritonéale.",
            "Désunion anastomotique nécessitant reprise chirurgicale.",
        ],
        "negative": [
            "Anastomose étanche, pas de fistule.",
            "Aucun lâchage de suture.",
            "Suites opératoires simples, anastomose parfaite.",
        ],
    },
    "abces": {
        "positive": [
            "Abcès intra-abdominal de {taille_abces} cm drainé au J{jour}.",
            "Collection abcédée en scanner, drainage percutané réalisé.",
            "Abcès pelvien post-opératoire traité.",
        ],
        "negative": [
            "Pas d'abcès postopératoire.",
            "Scanner de contrôle normal, pas de collection.",
            "Aucun abcès identifié.",
        ],
    },
    "choc_septique": {
        "positive": [
            "Choc septique au J{jour}, admission en USI.",
            "État de choc avec hypotension, noradrénaline débutée.",
            "Sepsis sévère avec défaillance hémodynamique.",
        ],
        "negative": [
            "Pas de choc septique.",
            "Suites opératoires sans complication septique.",
            "Aucun sepsis documenté.",
        ],
    },
    "insuffisance_renale": {
        "positive": [
            "Insuffisance rénale aiguë avec créatinine à {creat} mg/dL.",
            "IRA KDIGO stade {kdigo}, surveillance néphrologique.",
            "Fonction rénale altérée en postopératoire.",
        ],
        "negative": [
            "Fonction rénale normale (créatinine {creat} mg/dL).",
            "Pas d'insuffisance rénale.",
            "Bilan rénal normal.",
        ],
    },
    "embolie_pulmonaire": {
        "positive": [
            "Embolie pulmonaire au J{jour}, angio-scanner positif.",
            "EP confirmée, anticoagulation thérapeutique débutée.",
            "Thrombose pulmonaire segmentaire droite.",
        ],
        "negative": [
            "Pas d'embolie pulmonaire.",
            "Angio-scanner négatif.",
            "Aucune complication thromboembolique.",
        ],
    },
    "soutien_familial": {
        "positive": [
            "Patient bénéficie d'un bon soutien familial à domicile.",
            "Époux(se) présent(e) et aidant(e), retour à domicile possible.",
            "Famille aidante, pas de problème social pour la sortie.",
        ],
        "negative": [
            "Patient isolé, pas de soutien familial.",
            "Vit seul(e), orientation vers structure de rééducation.",
            "Absence de famille proche, placement envisagé.",
        ],
    },
}
