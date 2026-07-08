# citrus
Project to extract informations from BODACC on evolution of firms

#
07/07 : 
- première API to fetch ressources from BODACC + qqes règles simples pour les ventes 
- creation fichier bodacc et citrus pour les ventes
- Equivalence champs (export citrus et response API BODACC)

08/07 : 
- continue sur API : augmentation robustesse, en lien avec schéma de données sur https://bodacc-datadila.opendatasoft.com/explore/dataset/annonces-commerciales_qualif/information/
- add logger
- add metrics for sirencedant, sirenbeneficiaire, amount, clean strings
Sur 264 annonces, résultat suivant (par rapport à citrus): 
│ sirenCedant_assert ┆ raisonSocialeCedant_assert ┆ sirenBeneficiaire_assert ┆ raisonSocialeBeneficiaire_asse… ┆ num_bodacc ┆ montantNet_assert │
│ ---                ┆ ---                        ┆ ---                      ┆ ---                             ┆ ---        ┆ ---               │
│ f64                ┆ f64                        ┆ f64                      ┆ f64                             ┆ str        ┆ f64               │
╞════════════════════╪════════════════════════════╪══════════════════════════╪═════════════════════════════════╪════════════╪═══════════════════╡
│ 1.0                ┆ 0.75                       ┆ 1.0                      ┆ 0.886364                        ┆ null       ┆ 1.0    
Vente : 

anneeCampagne : calculé
'sirenCedant' : json.loads(json.loads(response.content).get("results")[0]['listeprecedentproprietaire'])["personne"]["numeroImmatriculation"]["numeroIdentification"]   - à confirmer : que vente ? 
'raisonSocialeCedant' : json.loads(json.loads(response.content).get("results")[0]['listeprecedentproprietaire'])["personne"]["denomination"]   - à confirmer : que vente ? 
apeCedant : obtenu depuis API Sirene (tbc)
groupe_id_cedant ?
sirenBeneficiaire : json.loads(json.loads(response.content).get("results")[0]['listepersonnes'])["personne"]["numeroImmatriculation"]["numeroIdentification"]  - à confirmer : que vente ? 
raisonSocialeBeneficiaire : json.loads(json.loads(response.content).get("results")[0]['listepersonnes'])["personne"]["denomination"] - à confirmer : que vente ? 
apeBeneficiaire: obtenu depuis API Sirene (tbc) 
groupe_id_beneficiaire : ?
'typeOperation':'familleavis' + 'familleavis_lib' (pas que - à discuter ??)
'montantNet' : en ke, à extraire depuis json.loads(json.loads(response.content).get("results")[0]['listeetablissements'])["etablissement"]["origineFonds"] ('siège et établissement principal acquis par achat au prix stipulé de 155000.00 euros')
enveloppe : ?
apeEnveloppe : obtenu depuis API Sirene (tbc)
enveloppeEntreprise : ?
apeEnveloppeEntreprise : obtenu depuis API Sirene (tbc)
dateEffetComptable : extraire depuis date de commencement ou commentaires ? défaut dateparution ? 
dateRealisationJuridique : extraire depuis date de commencement ou commentaires ? 
dateCreation : obtenu depuis API Sirene (tbc) 
dateModification : ?
source : json.loads(response.content).get("results")[0]["url_complete"] ('https://www.bodacc.fr/pages/annonces-commerciales-detail/?q.id=id:A20230147853')
etat : pas à prendre
nombreCommentaire : nombre de json.loads(json.loads(response.content).get("results")[0]["acte"])["descriptif"]
"Les oppositions s'il y a lieu seront reçues dans les 10 jours en date de la dernière des publications légales. Publication dans le journal d'annonces légales en dates des 11 et 14 juillet 2023. Cession sous acte authentique en date du 06/07/2023 Adresse de l'ancien propriétaire: 9 Place de l'Etoile 67210 Obernai"


familleavis : 
Vente & cessions : 
- vente : dans les commentaires 
- apport partiel actif - comment différencier scission totale et partielle ? 
- scission totale : indiqué dans le commentaire - comment différencier scission totale et partielle ? 
- scission partielle : indiqué dans le commentaire - comment différencier scission totale et partielle ? 
- fusion : indiqué dans le commentaire
- absorption : indiqué dans le commentaire
Modifications et mutations diverses : 
- TUP + mot dans le commentaire (aller trouver SIREN tupante dans le commentaire, le SIREN de l'annonce est la tupée)
- Location / gérance : mot dans le commentaire, les deux siren sont identifiés (comme vente)

**Questions :**
- comment on dit si c'est TUP/scission totale, partielle, etc : un ensemble de règles métiers à avoir ? 
- un tableau des champs à extraire par type d'opération ? 
- comment la date est-elle définie ? 

SIREN dans la balise "registre"

**Idées :**

- Utiliser l'annuaire entreprises / partie annonce ? https://annuaire-entreprises.data.gouv.fr/annonces/953645579#annonces-bodacc 
- Utiliser le bodacc avec un siren pour voir quel est le devenir de l'entreprise ? (ici : https://www.bodacc.fr/pages/annonces-commerciales-recherche/?disjunctive.typeavis&disjunctive.familleavis&disjunctive.publicationavis&disjunctive.region_min&disjunctive.nom_dep_min&disjunctive.numerodepartement&sort=dateparution&q.registre=registre%3A792016313 pour siren 792016313- radiée 6 mois après)
- Télécharger le pdf, disponible ici pour cette annonce : https://www.bodacc.fr/telechargements/COMMERCIALES/PDF/A/2023/20230147/0/BODACC_A_PDF_Unitaire_20230147_00853.pdf 