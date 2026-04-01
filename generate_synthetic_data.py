"""
Generate synthetic medical documents based on ColectomieFactors.

Usage:
    python -m src.event_detection.generate_synthetic_data --n-docs 10 --output-dir data/synthetic
"""
import argparse
from datetime import datetime
import json
import random
from pathlib import Path
from typing import Dict, List, Tuple
import pandas as pd
from colectomie_model import ColectomieFactors
from factor_phrases import FACTOR_PHRASES
from datetime import datetime, timedelta 

def determine_factor_from_biomarkers() -> Dict[str, Tuple[bool, Dict[str, object]]]:  
    """
    Determine factor status based on biological values (more realistic).

    Returns:
        Dict mapping factor_name to (boolean_value, placeholders_dict)
    """
    results = {}

    def add_factor(name: str, value: bool, placeholders: dict):
        results[name] = (value, placeholders)

    # Insuffisance rénale : créatinine > 1.3 mg/dL
    creat = round(random.uniform(0.6, 5.0), 1)
    kdigo = random.randint(1, 3) if creat > 1.3 else 0
    add_factor("insuffisance_renale", creat > 1.3, {"creat": creat, "kdigo": kdigo})

    # BMI élevé : BMI > 25
    bmi = round(random.uniform(18, 40), 1)
    add_factor("BMI_eleve", bmi > 25, {"bmi": bmi})

    # Anémie : Hb < 12 g/dL
    hb = round(random.uniform(7, 16), 1)
    add_factor("anemie", hb < 12, {"hb": hb})

    # Dénutrition : albumine < 35 g/L
    albumine = round(random.uniform(20, 50), 1)
    poids_perte = random.randint(3, 15) if albumine < 35 else random.randint(0, 2)
    add_factor("denutrition", albumine < 35, {"albumine": albumine, "poids_perte": poids_perte})

    # Inflammation : CRP > 120 mg/L ou leucocytes > 15000
    crp = random.randint(5, 350)
    leuco = random.randint(4000, 30000)
    add_factor("inflammation", crp > 120 or leuco > 15000, {"crp": crp, "leuco": leuco})

    return results

def create_doc(content, doc_type, service, date):
    return {
        "content": content,
        "document_type": doc_type,
        "service": service,
        "date": date,
        "source_file": f"{date[:7]}-{service}-{doc_type}.anon.html"
    }

def generate_synthetic_documents() -> Tuple[List[Dict], Dict[str, bool]]:
    """
    Generate multiple synthetic medical documents for one patient (simulating realistic medical journey).
    Creates: pre-op consultation, anesthesia consult, operative report, post-op notes, discharge summary.
    
    Returns:
        Tuple of (list of document dicts, ground_truth_dict)
    """    
    factors = ColectomieFactors.model_fields
    ground_truth = {}
    biomarker_factors = determine_factor_from_biomarkers()
    colectomy_types = ["colectomie_sigmoidienne", "hemicolectomie_gauche", "hemicolectomie_droite"]
    chosen_colectomy = random.choice(colectomy_types)
    forced_colectomy_values = {ctype: (ctype == chosen_colectomy) for ctype in colectomy_types}
    has_conversion = random.choice([True, False, False])
    
    if has_conversion:
        forced_approach_values = {k: True for k in ["laparoscopique", "laparotomie", "conversion_laparotomie"]}
    else:
        is_laparoscopic = random.choice([True, False])
        forced_approach_values = {
            "laparoscopique": is_laparoscopic,
            "laparotomie": not is_laparoscopic,
            "conversion_laparotomie": False,
        }
    
    factor_data = {}
    def get_placeholders():
        return {
            "hba1c": round(random.uniform(5.0, 12), 1),
            "ta_sys": random.randint(100, 180),
            "ta_dias": random.randint(60, 110),
            "gold": random.randint(2, 4),
            "tabac": random.randint(20, 60),
            "t_stage": random.randint(1, 4),
            "n_stage": random.randint(0, 2),
            "taille_abces": round(random.uniform(2, 8), 1),
            "duree_laparo": random.randint(30, 120),
            "jour": random.randint(3, 15),
            "quantite_drain": random.randint(50, 500),
        }
    
    for factor_name, field in factors.items():
        if factor_name in forced_approach_values: # laparoscopic/laparotomy/conversion
            value = forced_approach_values[factor_name]
            specific_placeholders = {}
        elif factor_name in forced_colectomy_values: # sigmoidectomy/left/right
            value = forced_colectomy_values[factor_name]
            specific_placeholders = {}
        elif factor_name in biomarker_factors:
            value, specific_placeholders = biomarker_factors[factor_name] # biomarker-determined
        else:
            value = random.choice([True, False])
            specific_placeholders = {}
        
        ground_truth[factor_name] = value
        
        if factor_name in FACTOR_PHRASES:
            phrase_list = FACTOR_PHRASES[factor_name]["positive" if value else "negative"]
            template = random.choice(phrase_list)
            placeholders = get_placeholders()
            placeholders.update(specific_placeholders)
            try:
                phrase = template.format(**placeholders)
            except KeyError:
                phrase = template
        else:
            desc = field.description or factor_name
            phrase = f"Le patient présente : {desc}" if value else f"Pas de {desc.lower()}"
        
        factor_data[factor_name] = {
            "value": value,
            "phrase": phrase,
            "placeholders": {**get_placeholders(), **specific_placeholders}
        }
    
    # Now build realistic document with dispersed information
    sections = []
    
    # Generate dates
    hospi_date = datetime.now() - timedelta(days=random.randint(10, 60))
    chir_date = hospi_date + timedelta(days=random.randint(1, 5))
    
    # 1. Evénement médical (admission info)
    sections.append("#### Evénement médical\n")
    sections.append("|  |  |")
    sections.append("| --- | --- |")
    sections.append("| Type d'admission | Hospitalisation classique |")
    
    # Insert surgical indication based on factors
    indication_parts = []
    if ground_truth.get("adenocarcinome"):
        indication_parts.append("Cancer du côlon")
    if ground_truth.get("sigmoidite_abcedee"):
        indication_parts.append("Sigmoidite compliquée")
    if ground_truth.get("volvulus_caecal"):
        indication_parts.append("Volvulus caecal")
    if ground_truth.get("colite_ischemique"):
        indication_parts.append("Colite ischémique")
    if not indication_parts:
        indication_parts.append("Pathologie colique")
    
    sections.append(f"| Motif d'hospi/consult | {', '.join(indication_parts)} |")
    sections.append(f"| Dt Hospi/transf | {hospi_date.strftime('%d/%m/%Y')} |")
    sections.append(f"| Fenetre | Hospitalisation du {hospi_date.strftime('%Y-%m-%d %H:%M:%S')} SERVICE - CHIRURGIE ABDOMINALE |\n")
    
    # 2. Anamnèse sociale (social context)
    sections.append("#### Anamnèse sociale\n")
    sections.append("|  |  |")
    sections.append("| --- | --- |")
    
    if ground_truth.get("soutien_familial"):
        sections.append("| Etat Civil | Epoux(se) |")
        sections.append("| Situation familiale | Vit en famille |\n")
    else:
        sections.append("| Etat Civil | Célibataire/Veuf(ve) |")
        sections.append("| Situation familiale | Vit seul(e) |\n")
    
    # 3. Antécédents médicaux (pre-op section)
    sections.append("#### Antécédents personnels\n")
    antecedents = []
    
    if ground_truth.get("diabete"):
        antecedents.append(factor_data["diabete"]["phrase"])
    if ground_truth.get("hta"):
        antecedents.append(factor_data["hta"]["phrase"])
    if ground_truth.get("bpco"):
        antecedents.append(factor_data["bpco"]["phrase"])
    
    if antecedents:
        sections.append(" ".join(antecedents) + "\n")
    else:
        sections.append("Pas d'antécédent médical majeur.\n")
    
    # 4. Bilan préopératoire (lab values in table)
    sections.append("#### Bilan biologique préopératoire\n")
    sections.append("|  |  |")
    sections.append("| --- | --- |")
    
    # Insert biomarker values
    bio_values = factor_data.get("BMI_eleve", {}).get("placeholders", {})
    sections.append(f"| BMI | {bio_values.get('bmi', 24)} kg/m² |")
    
    hb_val = factor_data.get("anemie", {}).get("placeholders", {}).get("hb", 13)
    sections.append(f"| Hémoglobine | {hb_val} g/dL |")
    
    alb_val = factor_data.get("denutrition", {}).get("placeholders", {}).get("albumine", 38)
    sections.append(f"| Albumine | {alb_val} g/L |")
    
    crp_val = factor_data.get("inflammation", {}).get("placeholders", {}).get("crp", 20)
    leuco_val = factor_data.get("inflammation", {}).get("placeholders", {}).get("leuco", 8000)
    sections.append(f"| CRP | {crp_val} mg/L |")
    sections.append(f"| Leucocytes | {leuco_val}/mm³ |")
    
    creat_val = factor_data.get("insuffisance_renale", {}).get("placeholders", {}).get("creat", 0.9)
    sections.append(f"| Créatinine | {creat_val} mg/dL |\n")
    
    # Add clinical interpretation
    if ground_truth.get("anemie"):
        sections.append(factor_data["anemie"]["phrase"] + "\n")
    if ground_truth.get("denutrition"):
        sections.append(factor_data["denutrition"]["phrase"] + "\n")
    if ground_truth.get("inflammation"):
        sections.append(factor_data["inflammation"]["phrase"] + "\n")
    
    # 5. Compte-rendu opératoire
    sections.append(f"#### Compte-rendu opératoire - {chir_date.strftime('%d/%m/%Y')}\n")
    
    # Surgical approach
    if ground_truth.get("laparoscopique") and not ground_truth.get("conversion_laparotomie"):
        sections.append(factor_data["laparoscopique"]["phrase"])
    elif ground_truth.get("laparotomie") and not ground_truth.get("laparoscopique"):
        sections.append(factor_data["laparotomie"]["phrase"])
    elif ground_truth.get("conversion_laparotomie"):
        sections.append(factor_data["conversion_laparotomie"]["phrase"])
    
    # Type of colectomy with detailed operative description
    if ground_truth.get("colectomie_sigmoidienne"):
        sections.append(" " + factor_data["colectomie_sigmoidienne"]["phrase"])
        sections.append(" Résection sigmoïdienne étendue avec mobilisation de l'angle colique gauche.")
        sections.append(" Section vasculaire de l'artère mésentérique inférieure préservant l'artère colique gauche.")
        sections.append(" Anastomose colo-rectale termino-terminale mécanique réalisée.")
    elif ground_truth.get("hemicolectomie_gauche"):
        sections.append(" Hémicolectomie gauche réalisée avec mobilisation de l'angle colique gauche et une partie du côlon transverse.")
        sections.append(" Ligature de l'artère mésentérique inférieure à son origine.")
        sections.append(" Résection incluant l'angle colique gauche, le côlon descendant et le sigmoïde proximal.")
        sections.append(" Anastomose colo-colique termino-terminale mécanique entre côlon transverse et rectum.")
    elif ground_truth.get("hemicolectomie_droite"):
        sections.append(" Hémicolectomie droite réalisée incluant caecum, côlon ascendant et angle colique droit.")
        sections.append(" Ligature de l'artère iléo-colique et artère colique droite.")
        sections.append(" Mobilisation complète du cadre colique droit jusqu'au côlon transverse proximal.")
        sections.append(" Anastomose iléo-colique latéro-latérale mécanique selon technique de Riolan.")
    
    # Stomie
    if ground_truth.get("stomie"):
        sections.append(" " + factor_data["stomie"]["phrase"])
    
    # Drains
    if ground_truth.get("drain_abdominal"):
        sections.append(" " + factor_data["drain_abdominal"]["phrase"])
    
    sections.append("\n")
    
    # 6. Suites postopératoires (scattered across multiple notes)
    sections.append("#### Suites postopératoires\n")
    
    # Day 1-3
    sections.append(f"J{random.randint(1,3)} post-op: ")
    postop_notes = []
    if ground_truth.get("ileus_postop"):
        postop_notes.append(factor_data["ileus_postop"]["phrase"])
    if ground_truth.get("sonde_nasogastrique"):
        postop_notes.append(factor_data["sonde_nasogastrique"]["phrase"])
    if not postop_notes:
        postop_notes.append("Suites immédiates simples.")
    sections.append(" ".join(postop_notes) + "\n")
    
    # Day 5-7
    if any([ground_truth.get("infection_postop"), ground_truth.get("infection_urinaire"), 
            ground_truth.get("lachage_suture"), ground_truth.get("abces")]):
        sections.append(f"\nJ{random.randint(5,7)} post-op: ")
        comp_notes = []
        if ground_truth.get("lachage_suture"):
            comp_notes.append(factor_data["lachage_suture"]["phrase"])
        if ground_truth.get("abces"):
            comp_notes.append(factor_data["abces"]["phrase"])
        if ground_truth.get("infection_postop"):
            comp_notes.append(factor_data["infection_postop"]["phrase"])
        if ground_truth.get("infection_urinaire"):
            comp_notes.append(factor_data["infection_urinaire"]["phrase"])
        sections.append(" ".join(comp_notes) + "\n")
    
    # Complications sévères
    if ground_truth.get("choc_septique") or ground_truth.get("occlusion_intestinale") or ground_truth.get("embolie_pulmonaire"):
        sections.append(f"\nJ{random.randint(8,12)} post-op - Complication: ")
        severe_comp = []
        if ground_truth.get("choc_septique"):
            severe_comp.append(factor_data["choc_septique"]["phrase"])
        if ground_truth.get("occlusion_intestinale"):
            severe_comp.append(factor_data["occlusion_intestinale"]["phrase"])
        if ground_truth.get("embolie_pulmonaire"):
            severe_comp.append(factor_data["embolie_pulmonaire"]["phrase"])
        if ground_truth.get("insuffisance_renale"):
            severe_comp.append(factor_data["insuffisance_renale"]["phrase"])
        sections.append(" ".join(severe_comp) + "\n")
    
    # 7. Planning de sortie
    sections.append("\n#### Planning de sortie\n")
    if ground_truth.get("soutien_familial"):
        sections.append(factor_data["soutien_familial"]["phrase"])
    else:
        sections.append(factor_data["soutien_familial"]["phrase"])
        sections.append(" Orientation vers structure de rééducation envisagée.")
    
    # Assemble main operative document
    main_content = "\n".join(sections)
    
    # Generate additional documents for realistic patient journey
    documents = []
    
    # Document 1: Pre-operative consultation (2-4 weeks before surgery)
    preop_date = hospi_date - timedelta(days=random.randint(14, 28))
    preop_content = f"""#### Consultation pré-opératoire - {preop_date.strftime('%d/%m/%Y')}

SERVICE - CHIRURGIE ABDOMINALE

Motif: Consultation préopératoire pour colectomie programmée

Antécédents:
"""
    if ground_truth.get("diabete"):
        preop_content += f"\n- {factor_data['diabete']['phrase']}"
    if ground_truth.get("hta"):
        preop_content += f"\n- {factor_data['hta']['phrase']}"
    if ground_truth.get("bpco"):
        preop_content += f"\n- {factor_data['bpco']['phrase']}"
    
    preop_content += f"\n\nIndication chirurgicale:\n"
    if ground_truth.get("adenocarcinome"):
        preop_content += factor_data["adenocarcinome"]["phrase"]
    elif ground_truth.get("sigmoidite_abcedee"):
        preop_content += factor_data["sigmoidite_abcedee"]["phrase"]
    elif ground_truth.get("volvulus_caecal"):
        preop_content += factor_data["volvulus_caecal"]["phrase"]
    elif ground_truth.get("colite_ischemique"):
        preop_content += factor_data["colite_ischemique"]["phrase"]
    
    documents.append(
        create_doc(
            content=preop_content,
            doc_type="CONSULTATION",
            service="CHIRURGIE ABDOMINALE",
            date=preop_date.strftime('%Y-%m-%d')
        )
    )
    
    # Document 2: Anesthesia consultation (1-2 weeks before)
    anesth_date = hospi_date - timedelta(days=random.randint(7, 14))
    anesth_content = f"""#### Consultation anesthésique - {anesth_date.strftime('%d/%m/%Y')}

SERVICE - ANESTHESIOLOGIE

Evaluation pré-anesthésique:

Score ASA: {random.randint(2, 3)}

Comorbidités:
"""
    if ground_truth.get("BMI_eleve"):
        anesth_content += f"\n- {factor_data['BMI_eleve']['phrase']}"
    if ground_truth.get("anemie"):
        anesth_content += f"\n- {factor_data['anemie']['phrase']}"
    if ground_truth.get("insuffisance_renale"):
        anesth_content += f"\n- {factor_data['insuffisance_renale']['phrase']}"
    
    anesth_content += "\n\nPatient informé des risques anesthésiques. Consentement signé."
    
    documents.append(
        create_doc(
            content=anesth_content,
            doc_type="CONSULTATION",
            service="ANESTHESIOLOGIE",
            date=anesth_date.strftime('%Y-%m-%d')
        )
    )
    
    # Document 3: Main operative and hospitalization document
    documents.append(
        create_doc(
            content=main_content,
            doc_type="HOSPITALISATION",
            service="CHIRURGIE ABDOMINALE",
            date=chir_date.strftime('%Y-%m-%d')
        )
    )
    
    # Document 4: Post-operative day 3-5 note (if complications)
    if any([ground_truth.get("ileus_postop"), ground_truth.get("infection_postop"), 
            ground_truth.get("infection_urinaire")]):
        postop_early_date = chir_date + timedelta(days=random.randint(3, 5))
        postop_early_content = f"""#### Note postopératoire J{(postop_early_date - chir_date).days}

SERVICE - CHIRURGIE ABDOMINALE

Evolution postopératoire:
"""
        if ground_truth.get("ileus_postop"):
            postop_early_content += f"\n- {factor_data['ileus_postop']['phrase']}"
        if ground_truth.get("infection_postop"):
            postop_early_content += f"\n- {factor_data['infection_postop']['phrase']}"
        if ground_truth.get("infection_urinaire"):
            postop_early_content += f"\n- {factor_data['infection_urinaire']['phrase']}"
        
        documents.append(
            create_doc(
                content=postop_early_content,
                doc_type="HOSPITALISATION",
                service="CHIRURGIE ABDOMINALE",
                date=postop_early_date.strftime('%Y-%m-%d')
            )
        )
    
    # Document 5: Severe complications note (if any)
    if any([ground_truth.get("lachage_suture"), ground_truth.get("abces"), 
            ground_truth.get("choc_septique"), ground_truth.get("occlusion_intestinale")]):
        postop_compl_date = chir_date + timedelta(days=random.randint(6, 10))
        postop_compl_content = f"""#### Complication postopératoire - Urgence

SERVICE - CHIRURGIE ABDOMINALE / SOINS INTENSIFS

Date: {postop_compl_date.strftime('%d/%m/%Y')}

Complication sévère:
"""
        if ground_truth.get("lachage_suture"):
            postop_compl_content += f"\n{factor_data['lachage_suture']['phrase']}"
        if ground_truth.get("abces"):
            postop_compl_content += f"\n{factor_data['abces']['phrase']}"
        if ground_truth.get("choc_septique"):
            postop_compl_content += f"\n{factor_data['choc_septique']['phrase']}"
        if ground_truth.get("occlusion_intestinale"):
            postop_compl_content += f"\n{factor_data['occlusion_intestinale']['phrase']}"
        
        postop_compl_content += "\n\nPrise en charge en urgence. Surveillance rapprochée."
        
        documents.append(
            create_doc(
                content=postop_compl_content,
                doc_type="HOSPITALISATION",
                service="SOINS INTENSIFS" if ground_truth.get("choc_septique") else "CHIRURGIE ABDOMINALE",
                date=postop_compl_date.strftime('%Y-%m-%d')
            )
        )
    
    # Document 6: Discharge summary
    discharge_date = chir_date + timedelta(days=random.randint(7, 21))
    discharge_content = f"""#### Résumé de sortie - {discharge_date.strftime('%d/%m/%Y')}

SERVICE - CHIRURGIE ABDOMINALE
Séjour hospitalier: du {hospi_date.strftime('%d/%m/%Y')} au {discharge_date.strftime('%d/%m/%Y')}

Durée de séjour: {(discharge_date - hospi_date).days} jours

Intervention réalisée:
"""
    if ground_truth.get("colectomie_sigmoidienne"):
        discharge_content += "\nSigmoidectomie"
    elif ground_truth.get("hemicolectomie_gauche"):
        discharge_content += "\nHémicolectomie gauche"
    elif ground_truth.get("hemicolectomie_droite"):
        discharge_content += "\nHémicolectomie droite"
    
    discharge_content += f"\n\Suites opératoires:\n"
    if any([ground_truth.get("infection_postop"), ground_truth.get("lachage_suture"), 
            ground_truth.get("abces"), ground_truth.get("choc_septique")]):
        discharge_content += "Suites compliquées. Voir notes opératoires."
    else:
        discharge_content += "Suites simples."
    
    discharge_content += f"\n\nSortie:\n"
    if ground_truth.get("soutien_familial"):
        discharge_content += "Retour à domicile avec soutien familial."
    else:
        discharge_content += "Transfert en centre de rééducation."
    
    documents.append(
        create_doc(
            content=discharge_content,
            doc_type="HOSPITALISATION",
            service="CHIRURGIE ABDOMINALE",
            date=discharge_date.strftime('%Y-%m-%d')
        )
    )
        
    # Add dietetic consultation (nutrition assessment)
    # More frequent for patients with malnutrition or high BMI
    if ground_truth.get("denutrition") or ground_truth.get("BMI_eleve") or random.choice([True, False]):
        diet_date = hospi_date + timedelta(days=random.randint(1, 3))
        
        # Get patient measurements
        bio_values = factor_data.get("BMI_eleve", {}).get("placeholders", {})
        bmi = bio_values.get('bmi', round(random.uniform(20, 30), 1))
        taille = bio_values.get('taille', random.randint(160, 185))
        poids = bio_values.get('poids', round(bmi * (taille/100)**2, 1))
        poids_ideal = round(22 * (taille/100)**2, 1)
        poids_max = round(poids * random.uniform(1.0, 1.1), 1)
        
        alb_val = factor_data.get("denutrition", {}).get("placeholders", {}).get("albumine", random.randint(35, 42))
        
        # Determine nutritional status
        if ground_truth.get("denutrition"):
            prises_alim = random.choice(["Moins de 25 %", "De 25 à 50 %"])
            nrs_score = random.randint(3, 5)
            perte_poids = round(random.uniform(3, 8), 1)
            conseils = "Supplémentation nutritionnelle orale prescrite. Enrichissement protéique des repas. Suivi rapproché."
        elif ground_truth.get("BMI_eleve"):
            prises_alim = random.choice(["De 75 à 100 %", "Plus de 100 %"])
            nrs_score = random.randint(1, 2)
            perte_poids = 0
            conseils = "Régime hypocalorique équilibré post-opératoire. Conseils nutritionnels pour perte de poids progressive."
        else:
            prises_alim = random.choice(["De 50 à 75 %", "De 75 à 100 %"])
            nrs_score = random.randint(0, 2)
            perte_poids = round(random.uniform(0, 2), 1)
            conseils = "Alimentation normale progressive post-opératoire. Conseils d'épargne intestinale."
        
        diet_content = f"""#### Rubrique Journalière1

|  |  |
| --- | --- |
| Dernier poids | {poids_max} |
| Poids | Poids idéal |
| Choix prot pour le gap | {random.choice(['1.2', '1.3', '1.5'])} g/kg PI |
| Choix cal | {random.choice(['25', '30', '35'])} kcal/kg |
| Prises alimentaires | {prises_alim} |
| nRS | {nrs_score} |
| Sévérité de la maladie | {random.choice(['Au lit une partie de la journée', 'Mobilisation autonome', 'Alité la majorité du temps'])} |
| 5% de P max | {round(poids_max * 0.05, 1)} |
| taille | {taille} |
| Bmi | {bmi} |
| Suivi diététique | Perte de {perte_poids}kg en pré op - {conseils} |
| Parentérale prot | 0 |
| Parentérale cal | 0 |
| Entérale prot | 0 |
| Entérale cal | 0 |
| Suppléments prot | {random.randint(0, 40) if ground_truth.get('denutrition') else 0} |
| Suppléments cal | {random.randint(0, 400) if ground_truth.get('denutrition') else 0} |
| Ingesta prot | {random.randint(30, 70)} |
| Ingesta cal | {random.randint(800, 1800)} |
| poids ideal | {poids_ideal} |
| poids max | {poids_max} |
| poids | {poids} |
| Albumine | {alb_val} g/L |

#### Rubrique Journalière2

|  |  |
| --- | --- |
| Date | {diet_date.strftime('%d/%m/%Y')} |
| Service | CHIRURGIE ABDOMINALE |
| Type de consultation | Bilan nutritionnel post-opératoire |

Evaluation diététique:

"""
        
        # Calculate nutritional values for evaluation section
        suppl_prot = random.randint(0, 40) if ground_truth.get('denutrition') else 0
        suppl_cal = random.randint(0, 400) if ground_truth.get('denutrition') else 0
        ingesta_prot = random.randint(30, 70)
        ingesta_cal = random.randint(800, 1800)
        
        if ground_truth.get("denutrition"):
            diet_content += f"Patient présentant une dénutrition avec albumine à {alb_val} g/L et perte pondérale de {perte_poids}kg.\n"
            diet_content += "Mise en place de suppléments nutritionnels oraux hyperprotéinés.\n"
            diet_content += "Objectif: augmenter les apports à 1.5g/kg de protéines et 30 kcal/kg.\n"
        elif ground_truth.get("BMI_eleve"):
            diet_content += f"Patient en surpoids (BMI {bmi}).\n"
            diet_content += "Conseils diététiques pour alimentation équilibrée post-opératoire.\n"
            diet_content += "Encourager activité physique progressive et portions contrôlées.\n"
        else:
            diet_content += "Etat nutritionnel satisfaisant.\n"
            diet_content += "Reprise alimentaire progressive selon tolérance digestive.\n"
            diet_content += "Conseils d'épargne intestinale: éviter fibres, laitages initialement.\n"
        
        # Add nutritional intake table
        diet_content += f"\nApports nutritionnels:\n\n"
        diet_content += "|  |  |\n"
        diet_content += "| --- | --- |\n"
        diet_content += "| Parentérale prot | 0 |\n"
        diet_content += "| Parentérale cal | 0 |\n"
        diet_content += "| Entérale prot | 0 |\n"
        diet_content += "| Entérale cal | 0 |\n"
        diet_content += f"| Suppléments prot | {suppl_prot} |\n"
        diet_content += f"| Suppléments cal | {suppl_cal} |\n"
        diet_content += f"| Ingesta prot | {ingesta_prot} |\n"
        diet_content += f"| Ingesta cal | {ingesta_cal} |\n"
        
        diet_content += f"\nPlan de suivi: {random.choice(['Réévaluation à J+7', 'Suivi en externe à 1 mois', 'Pas de suivi spécifique nécessaire'])}"
        
        documents.append({
            'content': diet_content,
            'document_type': 'CONSULTATION',
            'service': 'NUTRITION',
            'date': diet_date.strftime('%Y-%m-%d'),
            'source_file': f'{diet_date.year}-{diet_date.month}-NUTRITION-CONSULTATION.anon.html'
        })
    
    # Add social service records 
    # Social evaluation before surgery
    social_preop_date = hospi_date - timedelta(days=random.randint(3, 10))
    social_preop_content = f"""#### Evaluation sociale préopératoire - {social_preop_date.strftime('%d/%m/%Y')}

SERVICE - SERVICE SOCIAL

Entretien avec l'assistante sociale

Situation familiale: {"En couple, vit en famille" if ground_truth.get("soutien_familial") else "Célibataire, vit seul(e)"}

Situation professionnelle: {"En activité professionnelle" if random.choice([True, False]) else "Retraité(e)"}

Logement: Domicile personnel, {"avec ascenseur" if random.choice([True, False]) else f"sans ascenseur, étage {random.randint(1,4)}"}

Evaluation des besoins pour le retour à domicile post-opératoire.
"""
    if not ground_truth.get("soutien_familial"):
        social_preop_content += "\n Patient isolé. Evaluation pour aide à domicile ou placement temporaire à prévoir."
    
    documents.append(
        create_doc(
            content=social_preop_content,
            doc_type="CONSULTATION",
            service="SERVICE SOCIAL",
            date=social_preop_date.strftime('%Y-%m-%d')
        )
    )
        
    # Social follow-up during hospitalization
    social_hospi_date = chir_date + timedelta(days=random.randint(3, 7))
    social_hospi_content = f"""#### Suivi social - Hospitalisation - {social_hospi_date.strftime('%d/%m/%Y')}

SERVICE - SERVICE SOCIAL

Entretien de suivi pendant l'hospitalisation

Patient vu en chambre. Discussion sur le retour à domicile.
"""
    if ground_truth.get("soutien_familial"):
        social_hospi_content += "\nFamille présente et impliquée. Retour à domicile envisageable."
    else:
        social_hospi_content += "\nPatient seul. Difficultés anticipées pour le retour à domicile."
        social_hospi_content += f"\nDossier de demande d'aide à domicile initié."
    
    if any([ground_truth.get("lachage_suture"), ground_truth.get("choc_septique"), 
            ground_truth.get("abces")]):
        social_hospi_content += "\n\n Complications post-opératoires. Durée de séjour prolongée. Réevaluation nécessaire."
    
    documents.append(
        create_doc(
            content=social_hospi_content,
            doc_type="CONSULTATION",
            service="SERVICE SOCIAL",
            date=social_hospi_date.strftime('%Y-%m-%d')
        )
    )
    
    # Social discharge planning
    if not ground_truth.get("soutien_familial") or ground_truth.get("stomie"):
        social_discharge_date = discharge_date - timedelta(days=random.randint(1, 3))
        social_discharge_content = f"""#### Planning de sortie - Evaluation sociale - {social_discharge_date.strftime('%d/%m/%Y')}

SERVICE - SERVICE SOCIAL

Organisation de la sortie
"""
        if ground_truth.get("soutien_familial"):
            social_discharge_content += "\nRetour à domicile avec famille."
            if ground_truth.get("stomie"):
                social_discharge_content += "\nFormation stomie pour le patient et l'aidant organisée."
                social_discharge_content += "\nSuivi par infirmière à domicile mis en place."
        else:
            social_discharge_content += "\n- Dossier transfert centre de rééducation validé"
            social_discharge_content += "\n- Aide à domicile organisée (2 passages/jour)"
            social_discharge_content += "\n- Livraison repas à domicile activée"
            if ground_truth.get("stomie"):
                social_discharge_content += "\n- Suivi stomathérapeute à domicile organisé"
        
        social_discharge_content += f"\n\nDate de sortie prévue: {discharge_date.strftime('%d/%m/%Y')}"
        
        documents.append(
            create_doc(
                content=social_discharge_content,
                doc_type="CONSULTATION",
                service="SERVICE SOCIAL",
                date=social_discharge_date.strftime('%Y-%m-%d')
            )
        )
    
    # Add cardiac evaluation documents
    # Add for patients with cardiac risk factors or age > 60
    if ground_truth.get("hta") or ground_truth.get("diabete") or random.choice([True, False, False]):
        # ECG report
        ecg_date = hospi_date - timedelta(days=random.randint(7, 21))
        ecg_content = f"""#### Electrocardiogramme - {ecg_date.strftime('%d/%m/%Y')}

SERVICE - CARDIOLOGIE

Résultat ECG 12 dérivations

Rythme: {random.choice(['Sinusal régulier', 'Sinusal', 'Rythme sinusal'])}
Fréquence cardiaque: {random.randint(60, 90)} bpm

Analyse:
"""
        if ground_truth.get("hta"):
            ecg_content += f"- Hypertrophie ventriculaire gauche modérée (compatible avec HTA)\n"
            ecg_content += f"- Axe QRS dévié à gauche\n"
        else:
            ecg_content += f"- Axe QRS normal\n"
        
        ecg_findings = random.choice([
            "- Pas d'anomalie de repolarisation\n- Pas de trouble de conduction",
            "- Bloc de branche droit incomplet\n- QT normal",
            "- Ondes T négatives en territoire antéro-septal (séquelle)\n- PR normal"
        ])
        ecg_content += ecg_findings + "\n"
        
        ecg_content += f"\nConclusion: ECG {random.choice(['normal', 'dans les limites de la normale', 'sans anomalie significative'])} pour l'âge."
        
        if ground_truth.get("hta"):
            ecg_content += " Signes d'hypertrophie ventriculaire gauche."
        
        ecg_content += "\n\nAvis: Pas de contre-indication cardiologique à la chirurgie programmée."
        
        documents.append(
            create_doc(
                content=ecg_content,
                doc_type="PROTOCOL",
                service="CARDIOLOGIE",
                date=ecg_date.strftime('%Y-%m-%d')
            )
        )
        
        # Add echocardiography for 40% of these patients
        if random.choice([True, False, False, False, False]):
            echo_date = hospi_date - timedelta(days=random.randint(10, 30))
            echo_content = f"""#### Echocardiographie transthoracique - {echo_date.strftime('%d/%m/%Y')}

SERVICE - CARDIOLOGIE

Indication: Bilan préopératoire - Evaluation de la fonction cardiaque

Conditions techniques: Fenêtre acoustique {random.choice(['satisfaisante', 'bonne', 'moyenne'])}

Mesures:
- Ventricule gauche:
  * Diamètre télédiastolique: {random.randint(45, 55)} mm
  * Fraction d'éjection (Simpson): {random.randint(55, 65)}%
  * Epaisseur septum: {random.randint(9, 13)} mm
  * Epaisseur paroi postérieure: {random.randint(9, 12)} mm
  
- Ventricule droit:
  * Taille normale
  * Fonction systolique conservée (TAPSE {random.randint(18, 24)} mm)

- Oreillettes:
  * Oreillette gauche: {random.choice(['non dilatée', 'taille normale', 'légèrement dilatée'])}
  * Oreillette droite: taille normale

Valves:
- Valve mitrale: {random.choice(['continente', 'fuite minime', 'fuite triviale'])}
- Valve aortique: {random.choice(['continente', 'sclérose sans sténose', 'remaniements dégénératifs'])}
- Valve tricuspide: {random.choice(['continente', 'fuite triviale'])}

Péricarde: Pas d'épanchement

Conclusion:
"""
            if ground_truth.get("hta"):
                echo_content += "- Hypertrophie ventriculaire gauche concentrique (contexte d'HTA)\n"
            
            echo_content += f"- Fonction systolique VG conservée (FE {random.randint(55, 65)}%)\n"
            echo_content += "- Pas de valvulopathie significative\n"
            echo_content += "\nAvis cardiologique: Pas de contre-indication à la chirurgie abdominale programmée."
            
            documents.append({
                'content': echo_content,
                'document_type': 'PROTOCOL',
                'service': 'CARDIOLOGIE',
                'date': echo_date.strftime('%Y-%m-%d'),
                'source_file': f'{echo_date.year}-{echo_date.month}-CARDIOLOGIE-PROTOCOL.anon.html'
            })
    
    # Add specialist consultations for antécédents
    # Cardiology consult for HTA
    if ground_truth.get("hta"):
        cardio_date = hospi_date - timedelta(days=random.randint(14, 45))
        echo_line = "- Echocardiographie: cf. rapport séparé" if random.choice([True, False]) else ""
        cardio_content = f"""#### Consultation cardiologie - {cardio_date.strftime('%d/%m/%Y')}

SERVICE - CARDIOLOGIE

Motif: Bilan préopératoire - Patient hypertendu

Antécédents cardiovasculaires:
- Hypertension artérielle connue depuis {random.randint(5, 15)} ans
- Traitement actuel: {random.choice(['IEC + diurétique', 'Sartan + inhibiteur calcique', 'Bêtabloquant + diurétique'])}

Examen clinique:

|  |  |
| --- | --- |
| TA | {random.randint(130, 150)}/{random.randint(75, 90)} mmHg |
| FC | {random.randint(65, 85)} bpm |
| Auscultation cardiaque | B1 B2 réguliers, pas de souffle |
| Oedèmes MI | Absents |

Examens complémentaires:
- ECG: cf. rapport séparé
{echo_line}

Conclusion:
HTA équilibrée sous traitement. Pas de cardiopathie ischémique connue.
Risque cardiologique faible pour chirurgie abdominale programmée.

Recommandations:
- Poursuivre traitement antihypertenseur jusqu'à la veille de la chirurgie
- Reprendre dès J1 post-opératoire selon tolérance hémodynamique
- Surveillance TA en post-opératoire
"""
        
        documents.append(
            create_doc(
                content=cardio_content,
                doc_type="CONSULTATION",
                service="CARDIOLOGIE",
                date=cardio_date.strftime('%Y-%m-%d')
            )
        )
    
    # Pneumology consult for BPCO
    if ground_truth.get("bpco"):
        pneumo_date = hospi_date - timedelta(days=random.randint(14, 30))
        # Prepare smoking status outside f-string to avoid nested function calls
        tabac_years = random.randint(1, 10)
        paquets = random.randint(30, 50)
        tabac_status = f"sevré depuis {tabac_years} ans" if random.choice([True, False]) else f"{paquets} paquets-années"
        
        pneumo_content = f"""#### Consultation pneumologie - {pneumo_date.strftime('%d/%m/%Y')}

SERVICE - PNEUMOLOGIE

Motif: Bilan préopératoire - Patient BPCO

Antécédents pneumologiques:
- BPCO stade {random.choice(['GOLD 2', 'GOLD 3', 'modéré'])}
- Tabagisme: {tabac_status}
- Dyspnée stade mMRC {random.randint(1, 3)}

Traitement actuel:
- {random.choice(['LABA + corticoïde inhalé', 'Tiotropium', 'LABA/LAMA + corticoïde inhalé'])}

Examen clinique:

|  |  |
| --- | --- |
| SpO2 | {random.randint(92, 97)}% air ambiant |
| FR | {random.randint(14, 20)}/min |
| Auscultation pulmonaire | {random.choice(['MV diminué aux bases', 'Râles bronchiques diffus', 'Sibilants expiratoires'])} |

Spirométrie:

|  |  |
| --- | --- |
| VEMS | {random.randint(50, 75)}% de la théorique |
| CVF | {random.randint(70, 85)}% |
| Rapport VEMS/CVF | {random.randint(55, 68)}% |

Radiographie thorax:
- Distension thoracique
- Pas d'image de condensation
- Pas d'épanchement pleural

Conclusion:
BPCO stable sous traitement.
Risque respiratoire modéré pour chirurgie abdominale.

Recommandations péri-opératoires:
- Optimisation traitement bronchodilatateur
- Kinésithérapie respiratoire pré et post-opératoire
- Analgésie optimale pour permettre toux efficace
- Oxygénothérapie post-opératoire si nécessaire
"""
        
        documents.append(
            create_doc(
                content=pneumo_content,
                doc_type="CONSULTATION",
                service="PNEUMOLOGIE",
                date=pneumo_date.strftime('%Y-%m-%d')
            )
        )
    
    # Endocrinology consult for diabetes
    if ground_truth.get("diabete"):
        endo_date = hospi_date - timedelta(days=random.randint(14, 30))
        
        # Prepare treatment text outside f-string
        treatments = [
            '- Metformine 1000mg x2/j\n- Gliclazide 60mg/j',
            '- Metformine 850mg x2/j\n- Insuline basale (Lantus 20U le soir)',
            '- Metformine 1000mg x2/j\n- Inhibiteur DPP4'
        ]
        traitement_txt = random.choice(treatments)
        hba1c_val = round(random.uniform(6.5, 8.5), 1)
        
        endo_content = f"""#### Consultation endocrinologie - {endo_date.strftime('%d/%m/%Y')}

SERVICE - ENDOCRINOLOGIE

Motif: Bilan préopératoire - Patient diabétique

Antécédents endocriniens:
- Diabète type {random.choice(['2', '2'])} depuis {random.randint(5, 15)} ans

- HbA1c récente: {hba1c_val}%

Traitement actuel:
{traitement_txt}

Examen clinique:

|  |  |
| --- | --- |
| Glycémie à jeun | {round(random.uniform(1.1, 1.6), 2)} g/L |
| Poids | {round(random.uniform(70, 95), 1)} kg |
| Signes hypoglycémie | Absents |

Complications dégénératives:
- {random.choice(['Pas de rétinopathie', 'Rétinopathie minime', 'Pas de complication dégénérative'])}
- Fonction rénale: créatinine {round(random.uniform(0.8, 1.2), 2)} mg/dL
- Recherche microalbuminurie: négative

Conclusion:
Diabète relativement équilibré (HbA1c {hba1c_val}%).
Pas de contre-indication endocrinologique à la chirurgie.

Recommandations péri-opératoires:
- Arrêt Metformine 48h avant chirurgie
- Relais par insulinothérapie si nécessaire en péri-opératoire
- Surveillance glycémique rapprochée (objectif 1.4-1.8 g/L)
- Reprise traitement habituel dès reprise alimentaire
"""
        
        documents.append(
            create_doc(
                content=endo_content,
                doc_type="CONSULTATION",
                service="ENDOCRINOLOGIE",
                date=endo_date.strftime('%Y-%m-%d')
            )
        )
    
    # Add multiple daily internal medicine/infectious disease notes
    num_daily_notes = random.randint(4, 7)
    los_days = (discharge_date - hospi_date).days
    
    for day_num in range(min(num_daily_notes, los_days)):
        note_date = hospi_date + timedelta(days=day_num)
        day_post_op = (note_date - chir_date).days
        
        # Build daily progress note
        daily_note = f"""#### Note d'hospitalisation - Jour {day_num + 1}

SERVICE - MED._INTERNE_ET_INFECTIOLOGIE

Date: {note_date.strftime('%d/%m/%Y')}
{"J" + str(day_post_op) + " post-opératoire" if day_post_op >= 0 else "Préopératoire"}

Etat général:
Patient {"stable" if day_post_op < 0 or not any([ground_truth.get("choc_septique"), ground_truth.get("lachage_suture")]) else "surveillance rapprochée"}

Signes vitaux:

|  |  |
| --- | --- |
| TA | {random.randint(110, 145)}/{random.randint(65, 90)} mmHg |
| FC | {random.randint(65, 95)} bpm |
| T° | {round(random.uniform(36.5, 38.5), 1)}°C |
| SpO2 | {random.randint(94, 99)}% |
"""        
        # Pre-operative notes
        if day_post_op < 0:
            daily_note += "Préparation chirurgicale:\n"
            intervention = random.choice(['colectomie programmée', 'intervention chirurgicale colique', 'résection colique'])
            daily_note += f"Patient admis pour {intervention}. "
            if ground_truth.get("inflammation"):
                daily_note += f"Syndrome inflammatoire présent (CRP {factor_data['inflammation']['placeholders']['crp']} mg/L). "
            if ground_truth.get("anemie"):
                daily_note += f"Anémie préopératoire documentée (Hb {factor_data['anemie']['placeholders']['hb']} g/dL). "
            daily_note += "Bilan préopératoire complété.\n"
            
        # Post-operative notes
        elif day_post_op == 0:
            daily_note += "Retour de bloc opératoire:\n"
            intervention_type = 'colectomie laparoscopique' if ground_truth.get('laparoscopique') and not ground_truth.get('conversion_laparotomie') else 'colectomie par laparotomie'
            daily_note += f"Intervention réalisée: {intervention_type}. "
            daily_note += "Installation en salle de réveil, puis retour en chambre. "
            daily_note += f"Analgésie: PCA morphine + paracétamol. "
            if ground_truth.get("drain_abdominal"):
                daily_note += "Drain abdominal en place. "
            daily_note += "\n"
            
        elif day_post_op <= 3:
            daily_note += "Evolution postopératoire précoce:\n"
            mobilisation = random.choice(['au fauteuil', 'déambulation couloir', 'autonome'])
            douleur = random.randint(2, 5)
            transit = random.choice(['pas encore repris', 'gaz', 'gaz +', 'ralenti']) if ground_truth.get('ileus_postop') else random.choice(['gaz', 'selles J' + str(day_post_op)])
            daily_note += f"Mobilisation: {mobilisation}. "
            daily_note += f"Douleur: {douleur}/10. "
            daily_note += f"Transit: {transit}. "
            if ground_truth.get("sonde_nasogastrique"):
                daily_note += "SNG en place, aspiration digestive. "
            if ground_truth.get("drain_abdominal"):
                drain_vol = random.randint(50, 200)
                daily_note += f"Drain: {drain_vol} mL/24h séro-hématique. "
            daily_note += "\n"
                
        elif day_post_op <= 7:
            daily_note += "Evolution postopératoire:\n"
            
            if ground_truth.get("infection_postop"):
                daily_note += f"{factor_data['infection_postop']['phrase']}. "
                daily_note += "Antibiothérapie adaptée débutée. "
            elif ground_truth.get("lachage_suture"):
                daily_note += f"{factor_data['lachage_suture']['phrase']}. "
                daily_note += "Scanner abdominal réalisé. "
            elif ground_truth.get("abces"):
                daily_note += f"{factor_data['abces']['phrase']}. "
                daily_note += "Drainage radiologique envisagé. "
            else:
                transit_state = 'repris normalement' if not ground_truth.get('ileus_postop') else 'toujours ralenti'
                alimentation = random.choice(['liquides clairs', 'semi-solide', 'normale progressive'])
                daily_note += f"Transit: {transit_state}. "
                daily_note += f"Alimentation: {alimentation}. "
                daily_note += "Cicatrisation correcte. "
                
            if ground_truth.get("infection_urinaire"):
                daily_note += f"{factor_data['infection_urinaire']['phrase']}. "
            daily_note += "\n"
                
        else:  # > J7
            daily_note += "Evolution tardive:\n"
            
            if ground_truth.get("choc_septique"):
                daily_note += f"{factor_data['choc_septique']['phrase']}. "
                daily_note += "Transfert en soins intensifs. "
            elif ground_truth.get("occlusion_intestinale"):
                daily_note += f"{factor_data['occlusion_intestinale']['phrase']}. "
            elif ground_truth.get("embolie_pulmonaire"):
                daily_note += f"{factor_data['embolie_pulmonaire']['phrase']}. "
                daily_note += "Anticoagulation thérapeutique. "
            else:
                daily_note += "Evolution favorable. "
                daily_note += "Autonomie progressive. "
                daily_note += f"Préparation à la sortie. "
            daily_note += "\n"
        
        # Add biological results
        if day_post_op >= 0 and random.choice([True, False]):
            daily_note += f"\nBiologie du jour:\n\n"
            daily_note += "|  |  |\n"
            daily_note += "| --- | --- |\n"
            daily_note += f"| Hb | {round(random.uniform(9, 13), 1)} g/dL |\n"
            daily_note += f"| Leucocytes | {random.randint(6000, 18000)}/mm³ |\n"
            daily_note += f"| CRP | {random.randint(10, 200)} mg/L |\n"
            daily_note += f"| Créatinine | {round(random.uniform(0.7, 1.4), 2)} mg/dL |\n"
        
        # Treatment plan
        daily_note += f"\nConduite à tenir: \n"
        if day_post_op < 0:
            daily_note += "Intervention prévue demain. "
            daily_note += "Jeûne à partir de minuit. "
        elif day_post_op <= 3:
            daily_note += "Poursuivre surveillance. "
            daily_note += f"Analgésie adaptée. "
            if ground_truth.get("drain_abdominal"):
                daily_note += "Surveillance drainage. "
            daily_note += "\n"
        else:
            daily_note += "Poursuite soins. "
            if any([ground_truth.get("infection_postop"), ground_truth.get("lachage_suture"), ground_truth.get("abces")]):
                daily_note += "Antibiothérapie IV. "
                daily_note += "Surveillance rapprochée. "
            else:
                daily_note += "Favoriser mobilisation. "
                daily_note += "Reprise alimentaire progressive. "
            daily_note += "\n"
        
        documents.append(
            create_doc(
                content=daily_note,
                doc_type="HOSPITALISATION",
                service="MED._INTERNE_ET_INFECTIOLOGIE",
                date=note_date.strftime('%Y-%m-%d')
            )
        )
    
    return documents, ground_truth

def main():
    parser = argparse.ArgumentParser(
        description="Generate synthetic medical documents (dpi_documents.csv)"
    )
    parser.add_argument(
        "--n-docs",
        type=int,
        default=10,
        help="Number of synthetic patients to generate"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="data/cohorts/synthetic",
        help="Output directory for synthetic data"
    )
    
    args = parser.parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for i in range(args.n_docs):
        patient_id = f"synthetic-{i}"
        patient_folder = output_dir / patient_id
        patient_folder.mkdir(exist_ok=True)
        
        # Generate synthetic documents
        documents, gt = generate_synthetic_documents()
        
        # Save dpi_documents.csv (only content column)
        df_documents = pd.DataFrame(documents)
        dpi_csv_path = patient_folder / "dpi_documents.csv"
        df_documents[['content']].to_csv(dpi_csv_path, index=False, encoding='utf-8')

        # Save ground truth as JSON
        gt_json_path = patient_folder / "ground_truth.json"
        with open(gt_json_path, 'w', encoding='utf-8') as f:
            json.dump(gt, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()