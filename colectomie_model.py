from pydantic import BaseModel, Field
from typing import Optional

class ColectomieFactors(BaseModel):

    BMI_eleve: bool = Field(False, description="Le patient présente un indice de masse corporelle (BMI) supérieur à 25 kg/m²")
    denutrition: bool = Field(False, description="Le patient présente une dénutrition documentée (perte de poids, hypoalbuminémie, amaigrissement)")
    anemie: bool = Field(False, description="Le patient présente une anémie préopératoire (hémoglobine basse)")
    diabete: bool = Field(False, description="Le patient est diabétique (diabète de type 1 ou 2)")
    hta: bool = Field(False, description="Le patient souffre d'hypertension artérielle (HTA)")
    bpco: bool = Field(False, description="Le patient souffre de bronchopneumopathie chronique obstructive (BPCO)")

    # --- Pathologie / indication ---
    adenocarcinome: bool = Field(False, description="Le patient présente un adénocarcinome colique (cancer du côlon)")
    sigmoidite_abcedee: bool = Field(False, description="Le patient présente une sigmoidite diverticulaire abcédée (urgence chirurgicale)")
    volvulus_caecal: bool = Field(False, description="Le patient présente un volvulus du caecum ou du côlon droit (torsion intestinale)")
    colite_ischemique: bool = Field(False, description="Le patient présente une colite ischémique (nécrose colique par hypoperfusion vasculaire)")
    inflammation: bool = Field(False, description="Le patient présente une inflammation importante (CRP > 120 mg/L ou leucocytes > 15000/mm³)")

    # --- Technique opératoire ---
    laparoscopique: bool = Field(False, description="Le patient a bénéficié d'une colectomie par laparoscopie (cœlioscopie)")
    laparotomie: bool = Field(False, description="Le patient a bénéficié d'une colectomie ouverte par laparotomie")
    conversion_laparotomie: bool = Field(False, description="La chirurgie laparoscopique a été convertie en laparotomie")
    colectomie_sigmoidienne: bool = Field(False, description="Le patient a bénéficié d'une colectomie sigmoïdienne")
    hemicolectomie_gauche: bool = Field(False, description="Le patient a bénéficié d'une colectomie gauche (hémicolectomie gauche)")
    hemicolectomie_droite: bool = Field(False, description="Le patient a bénéficié d'une colectomie droite (hémicolectomie droite)")

    # --- Complications postopératoires ---
    sonde_nasogastrique: bool = Field(False, description="Le patient a nécessité la pose d'une sonde nasogastrique en postopératoire")
    drain_abdominal: bool = Field(False, description="Le patient a bénéficié de la pose d'un drain abdominal en postopératoire (indicateur de complexité chirurgicale ou risque de collection)")
    stomie: bool = Field(False, description="Le patient a bénéficié de la confection d'une stomie (colostomie ou iléostomie) en peropératoire ou postopératoire")
    infection_postop: bool = Field(False, description="Le patient a développé une infection postopératoire (site opératoire, infection de paroi)")
    infection_urinaire: bool = Field(False, description="Le patient a développé une infection urinaire en postopératoire")
    ileus_postop: bool = Field(False, description="Le patient a présenté un iléus postopératoire (paralysie intestinale transitoire)")
    occlusion_intestinale: bool = Field(False, description="Le patient a présenté une occlusion intestinale en postopératoire (bride, volvulus, sub-occlusion)")
    lachage_suture: bool = Field(False, description="Le patient a présenté un lâchage de suture anastomotique ou une fistule anastomotique en postopératoire")
    abces: bool = Field(False, description="Le patient a développé un abcès intra-abdominal en postopératoire")
    choc_septique: bool = Field(False, description="Le patient a présenté un choc septique postopératoire")
    insuffisance_renale: bool = Field(False, description="Le patient a développé une insuffisance rénale en postopératoire (IRA, KDIGO)")
    embolie_pulmonaire: bool = Field(False, description="Le patient a présenté une embolie pulmonaire en postopératoire")
  
    # --- Facteur social ---
    soutien_familial: bool = Field(False, description="Le patient bénéficie d'un soutien familial à domicile")