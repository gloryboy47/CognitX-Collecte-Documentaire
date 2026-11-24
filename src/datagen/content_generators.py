"""Generateurs de contenu pour chaque type de document."""

from __future__ import annotations

import random
from datetime import date, timedelta
from dataclasses import dataclass

from entities.fake_entities import EntityPool, Company, Person


def _fmt_date(d: date, style: str = "fr") -> str:
    if style == "fr":
        return d.strftime("%d/%m/%Y")
    elif style == "long":
        mois = [
            "", "janvier", "fevrier", "mars", "avril", "mai", "juin",
            "juillet", "aout", "septembre", "octobre", "novembre", "decembre",
        ]
        return f"{d.day} {mois[d.month]} {d.year}"
    return d.isoformat()


def _fmt_money(amount: float) -> str:
    return f"{amount:,.2f}".replace(",", " ").replace(".", ",")


def _rand_date(start: date, end: date) -> date:
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, max(delta, 1)))


PRESTATIONS_FACTURE = [
    "Developpement logiciel sur mesure",
    "Conseil en ingenierie des procedes",
    "Analyse et conception de systemes embarques",
    "Etude de faisabilite technique",
    "Formation technique specialisee",
    "Maintenance applicative trimestrielle",
    "Audit de securite informatique",
    "Integration de systemes d'information",
    "Conception mecanique assistee par ordinateur",
    "Essais et tests de validation",
    "Prototypage rapide de composants",
    "Redaction de specifications techniques",
    "Accompagnement a la certification",
    "Support technique niveau 2",
    "Migration et refonte d'infrastructure",
    "Analyse de donnees et reporting",
    "Gestion de projet technique",
    "Recherche bibliographique specialisee",
]

MENTIONS_LEGALES_FACTURE = [
    "En cas de retard de paiement, une penalite de 3 fois le taux d'interet legal sera appliquee, ainsi qu'une indemnite forfaitaire de 40 EUR pour frais de recouvrement.",
    "Pas d'escompte pour paiement anticipe. Penalites de retard : taux BCE + 10 points. Indemnite de recouvrement : 40 EUR.",
    "Conditions de paiement : 30 jours date de facture. Tout retard de paiement entraine l'application de penalites de retard au taux annuel de 12%.",
]

TITRES_FACTURE = ["Facture", "FACTURE", "Facture de prestations", "Note d'honoraires"]


def generate_facture(pool: EntityPool, gabarit_id: str, seed: int) -> dict:
    random.seed(seed)
    emetteur = random.choice(pool.companies)
    destinataire = random.choice([c for c in pool.companies if c != emetteur])

    date_em = _rand_date(date(2024, 1, 1), date(2026, 10, 1))
    nb_lignes = random.randint(2, 6)
    lignes = []
    for _ in range(nb_lignes):
        qte = random.randint(1, 20)
        pu = round(random.uniform(150, 2500), 2)
        lignes.append({
            "designation": random.choice(PRESTATIONS_FACTURE),
            "quantite": qte,
            "prix_unitaire": _fmt_money(pu),
            "montant_ht": _fmt_money(qte * pu),
        })

    total_ht = sum(l["quantite"] * float(l["prix_unitaire"].replace(" ", "").replace(",", ".")) for l in
                   [{"quantite": random.randint(1, 20), "prix_unitaire": l["prix_unitaire"]} for l in lignes])
    # recalculate properly
    raw_lignes = []
    for _ in range(nb_lignes):
        qte = random.randint(1, 20)
        pu = round(random.uniform(150, 2500), 2)
        raw_lignes.append({"designation": random.choice(PRESTATIONS_FACTURE), "quantite": qte, "prix_unitaire": pu, "montant_ht": round(qte * pu, 2)})

    total_ht = sum(l["montant_ht"] for l in raw_lignes)
    taux_tva = random.choice([20, 10, 5.5])
    montant_tva = round(total_ht * taux_tva / 100, 2)
    total_ttc = round(total_ht + montant_tva, 2)

    style = random.choice(["fr", "long"])
    return {
        "template": f"facture_{gabarit_id}.html",
        "classe": "facture",
        "sous_type": "facture",
        "data": {
            "emetteur": emetteur,
            "destinataire": destinataire,
            "titre_document": random.choice(TITRES_FACTURE),
            "numero": f"F-{date_em.year}-{random.randint(1000, 9999)}",
            "date_emission": _fmt_date(date_em, style),
            "date_echeance": _fmt_date(date_em + timedelta(days=random.choice([30, 45, 60])), style),
            "reference_commande": f"BC-{random.randint(2000, 9999)}" if random.random() > 0.4 else "",
            "lignes": [
                {
                    "designation": l["designation"],
                    "quantite": l["quantite"],
                    "prix_unitaire": _fmt_money(l["prix_unitaire"]),
                    "montant_ht": _fmt_money(l["montant_ht"]),
                }
                for l in raw_lignes
            ],
            "total_ht": _fmt_money(total_ht),
            "taux_tva": taux_tva,
            "montant_tva": _fmt_money(montant_tva),
            "total_ttc": _fmt_money(total_ttc),
            "mentions_legales": random.choice(MENTIONS_LEGALES_FACTURE),
        },
        "verite_terrain": {
            "montant_ht": total_ht,
            "montant_tva": montant_tva,
            "montant_ttc": total_ttc,
            "taux_tva": taux_tva,
            "date_emission": date_em.isoformat(),
            "emetteur": emetteur.name,
            "destinataire": destinataire.name,
            "numero": None,  # filled after template
        },
    }


CONVENTIONS = [
    "Syntec", "Metallurgie", "Commerce de gros", "Bureaux d'etudes techniques",
]

PRIMES_POSSIBLES = [
    "Prime de transport", "Prime d'anciennete", "Prime exceptionnelle",
    "Indemnite teletravail", "Prime de performance",
]

COTISATIONS = [
    {"nom": "Securite sociale maladie", "taux_s": 0.0, "taux_p": 7.0},
    {"nom": "Securite sociale vieillesse plafonnee", "taux_s": 6.9, "taux_p": 8.55},
    {"nom": "Securite sociale vieillesse deplafonnee", "taux_s": 0.4, "taux_p": 1.9},
    {"nom": "Assurance chomage", "taux_s": 0.0, "taux_p": 4.05},
    {"nom": "Retraite complementaire T1", "taux_s": 3.15, "taux_p": 4.72},
    {"nom": "CSG deductible", "taux_s": 6.8, "taux_p": 0.0},
    {"nom": "CSG non deductible + CRDS", "taux_s": 2.9, "taux_p": 0.0},
]

TITRES_FICHE = ["Bulletin de paie", "BULLETIN DE PAIE", "Fiche de salaire", "Bulletin de salaire"]


def generate_fiche_de_paie(pool: EntityPool, gabarit_id: str, seed: int) -> dict:
    random.seed(seed)
    employeur = random.choice(pool.companies)
    salarie = random.choice(pool.persons)

    mois = random.randint(1, 12)
    annee = random.choice([2024, 2025, 2026])
    periode_debut = date(annee, mois, 1)
    if mois == 12:
        periode_fin = date(annee, 12, 31)
    else:
        periode_fin = date(annee, mois + 1, 1) - timedelta(days=1)

    salaire_base = round(random.uniform(2200, 5500), 2)
    heures = random.choice([151.67, 169])

    primes = []
    for _ in range(random.randint(0, 2)):
        primes.append({"nom": random.choice(PRIMES_POSSIBLES), "montant": _fmt_money(round(random.uniform(50, 400), 2))})

    brut = salaire_base + sum(float(p["montant"].replace(" ", "").replace(",", ".")) for p in primes)

    cotisations_out = []
    total_salarial = 0
    total_patronal = 0
    for c in COTISATIONS:
        ps = round(brut * c["taux_s"] / 100, 2)
        pp = round(brut * c["taux_p"] / 100, 2)
        total_salarial += ps
        total_patronal += pp
        cotisations_out.append({
            "nom": c["nom"],
            "base": _fmt_money(brut),
            "taux_salarial": c["taux_s"],
            "part_salariale": _fmt_money(ps),
            "taux_patronal": c["taux_p"],
            "part_patronale": _fmt_money(pp),
        })

    net_avant_pas = round(brut - total_salarial, 2)
    taux_pas = random.choice([0, 2.5, 5, 7.5, 10, 12, 15])
    montant_pas = round(net_avant_pas * taux_pas / 100, 2)
    net_a_payer = round(net_avant_pas - montant_pas, 2)

    return {
        "template": f"fiche_de_paie_{gabarit_id}.html",
        "classe": "fiche_de_paie",
        "sous_type": "fiche_de_paie",
        "data": {
            "employeur": employeur,
            "salarie": salarie,
            "titre_document": random.choice(TITRES_FICHE),
            "numero_bulletin": f"{annee}-{mois:02d}-{random.randint(100, 999)}",
            "convention": random.choice(CONVENTIONS),
            "date_entree": _fmt_date(_rand_date(date(2018, 1, 1), date(2024, 6, 1))),
            "classification": f"Position {random.choice(['2.1', '2.2', '2.3', '3.1', '3.2'])} — Coefficient {random.choice([270, 310, 355, 400, 450])}",
            "temps_travail": f"{heures}h/mois",
            "periode_debut": _fmt_date(periode_debut),
            "periode_fin": _fmt_date(periode_fin),
            "heures_base": heures,
            "salaire_base": _fmt_money(salaire_base),
            "primes": primes,
            "cotisations": cotisations_out,
            "salaire_brut": _fmt_money(brut),
            "total_cotisations_salariales": _fmt_money(round(total_salarial, 2)),
            "taux_pas": taux_pas,
            "montant_pas": _fmt_money(montant_pas),
            "net_a_payer": _fmt_money(net_a_payer),
            "date_paiement": _fmt_date(periode_fin + timedelta(days=random.randint(0, 5))),
            "mode_paiement": random.choice(["virement bancaire", "virement", "cheque"]),
            "cumul_brut": _fmt_money(round(brut * mois, 2)),
            "cumul_net_imposable": _fmt_money(round(net_avant_pas * mois, 2)),
            "conges_acquis": random.randint(20, 30),
            "conges_pris": random.randint(0, 15),
            "conges_solde": random.randint(5, 25),
        },
        "verite_terrain": {
            "salaire_brut": round(brut, 2),
            "net_a_payer": net_a_payer,
            "periode": f"{annee}-{mois:02d}",
            "employeur": employeur.name,
            "salarie": salarie.full_name,
        },
    }


TYPES_CONTRAT = [
    ("Contrat de prestation de services", "le Prestataire", "le Client"),
    ("Contrat de sous-traitance", "le Sous-traitant", "le Donneur d'ordre"),
    ("Convention de collaboration de recherche", "le Partenaire A", "le Partenaire B"),
    ("Contrat de travail a duree indeterminee", "l'Employeur", "le Salarie"),
]

ARTICLES_CONTRAT = {
    "prestation": [
        ("Objet", "Le Prestataire s'engage a realiser pour le compte du Client les prestations suivantes : {objet}. Ces prestations seront executees conformement aux specifications definies en annexe."),
        ("Duree", "Le present contrat est conclu pour une duree de {duree_mois} mois a compter de sa date de signature. Il pourra etre renouvele par accord ecrit des parties."),
        ("Prix et modalites de paiement", "Le prix des prestations est fixe a {montant} EUR hors taxes. Le paiement sera effectue par virement bancaire dans un delai de {delai_paiement} jours a compter de la reception de la facture."),
        ("Obligations du Prestataire", "Le Prestataire s'engage a executer les prestations avec diligence et dans les regles de l'art. Il met en oeuvre les moyens necessaires a la bonne execution du contrat."),
        ("Confidentialite", "Chaque partie s'engage a maintenir confidentielles toutes les informations techniques, commerciales et financieres portees a sa connaissance dans le cadre du present contrat, pendant toute la duree du contrat et pendant {duree_confidentialite} ans apres son terme."),
        ("Responsabilite", "La responsabilite du Prestataire est limitee au montant des sommes effectivement percues au titre du present contrat. En aucun cas, le Prestataire ne pourra etre tenu responsable des dommages indirects."),
        ("Resiliation", "Chaque partie peut resilier le contrat en cas de manquement grave de l'autre partie, apres mise en demeure restee infructueuse pendant {delai_resiliation} jours."),
        ("Loi applicable et juridiction", "Le present contrat est soumis au droit francais. Tout litige sera soumis aux tribunaux competents de {ville_tribunal}."),
    ],
}


def generate_contrat(pool: EntityPool, gabarit_id: str, seed: int) -> dict:
    random.seed(seed)
    type_contrat, denom_a, denom_b = random.choice(TYPES_CONTRAT)
    partie_a = random.choice(pool.companies)
    rep_a = random.choice(pool.persons)

    is_travail = "travail" in type_contrat.lower()
    if is_travail:
        partie_b_nom = random.choice(pool.persons).full_name
        partie_b_siren = ""
        partie_b_adresse = f"{random.randint(1, 150)} {random.choice(['rue', 'avenue', 'boulevard'])} {random.choice(['de la Paix', 'Victor Hugo', 'des Lilas', 'Jean Jaures'])}, {random.choice(['75001 Paris', '69003 Lyon', '31000 Toulouse'])}"
        rep_b = ""
        partie_b_personne = True
    else:
        b = random.choice([c for c in pool.companies if c != partie_a])
        partie_b_nom = b.name
        partie_b_siren = b.siren
        partie_b_adresse = f"{b.address}, {b.zip_code} {b.city}"
        rep_b = random.choice(pool.persons).full_name
        partie_b_personne = False

    date_contrat = _rand_date(date(2023, 1, 1), date(2026, 9, 1))
    duree_mois = random.choice([6, 12, 18, 24, 36])
    montant = _fmt_money(round(random.uniform(5000, 150000), 2))

    articles = []
    art_templates = ARTICLES_CONTRAT.get("prestation", [])
    for i, (titre, contenu) in enumerate(art_templates, 1):
        filled = contenu.format(
            objet=random.choice(["developpement d'un module logiciel", "audit technique des installations", "etude de marche sectorielle", "conception d'un prototype mecanique"]),
            duree_mois=duree_mois,
            montant=montant,
            delai_paiement=random.choice([30, 45, 60]),
            duree_confidentialite=random.choice([2, 3, 5]),
            delai_resiliation=random.choice([15, 30]),
            ville_tribunal=random.choice(["Paris", "Lyon", "Marseille", "Toulouse", "Nantes"]),
        )
        articles.append({"numero": i, "titre": titre, "contenu": filled})

    return {
        "template": f"contrat_{gabarit_id}.html",
        "classe": "contrat",
        "sous_type": type_contrat.lower().replace(" ", "_")[:30],
        "data": {
            "titre_document": type_contrat,
            "sous_titre": f"N° {date_contrat.year}-{random.randint(100, 999)}",
            "lieu": random.choice(["Paris", "Lyon", "Marseille", "Bordeaux", "Nantes", "Fes", "Casablanca"]),
            "date_contrat": _fmt_date(date_contrat, "long"),
            "partie_a": partie_a,
            "representant_a": rep_a.full_name,
            "qualite_a": random.choice(["Directeur general", "Gerant", "President"]),
            "denomination_a": denom_a,
            "partie_b_nom": partie_b_nom,
            "partie_b_siren": partie_b_siren,
            "partie_b_adresse": partie_b_adresse,
            "representant_b": rep_b,
            "partie_b_personne": partie_b_personne,
            "denomination_b": denom_b,
            "articles": articles,
        },
        "verite_terrain": {
            "type_contrat": type_contrat,
            "partie_a": partie_a.name,
            "partie_b": partie_b_nom,
            "date": date_contrat.isoformat(),
        },
    }


TRAVAUX_RD = [
    "L'equipe a poursuivi les travaux d'optimisation de l'algorithme de detection. Les tests sur le jeu de donnees elargi montrent une amelioration de la precision de 12 points par rapport au mois precedent. Plusieurs pistes ont ete explorees, notamment l'utilisation de techniques de regularisation avancees et l'augmentation des donnees d'entrainement.",
    "Les essais de caracterisation des materiaux composites ont ete realises sur la nouvelle serie d'echantillons. Les resultats preliminaires indiquent une resistance a la traction superieure de 15% aux valeurs attendues, ce qui ouvre des perspectives interessantes pour l'application visee.",
    "Le prototype du module de traitement a ete assemble et les premiers tests fonctionnels ont ete conduits. Le systeme repond aux specifications dans 85% des cas de test. Les cas d'echec ont ete identifies et analyses.",
    "La phase d'etude bibliographique sur les methodes de synthese catalytique a ete completee. Vingt-trois articles pertinents ont ete identifies et analyses. Les approches les plus prometteuses ont ete selectionnees pour la phase experimentale.",
    "L'integration du module de vision par ordinateur dans la chaine de production pilote a ete realisee. Les tests en conditions reelles montrent un taux de detection des defauts de 92%, avec un temps de traitement moyen de 150 ms par piece.",
]

VERROUS_RD = [
    {"titre": "Convergence de l'algorithme", "description": "L'algorithme ne converge pas de maniere stable au-dela de 10 000 iterations. L'equipe explore des strategies de learning rate adaptatif et des architectures alternatives."},
    {"titre": "Reproductibilite des essais", "description": "Les resultats experimentaux montrent une variabilite de 8% entre les series d'essais. L'identification des sources de variabilite est en cours."},
    {"titre": "Passage a l'echelle", "description": "Le procede fonctionne a l'echelle du laboratoire mais le passage a l'echelle pilote pose des problemes de dissipation thermique non anticipes."},
    {"titre": "Compatibilite des materiaux", "description": "L'interface entre les deux couches du composite presente des zones de delaminage apres cyclage thermique. Des traitements de surface sont a l'etude."},
]

TITRES_CR_RD = [
    "Compte-rendu de reunion de projet R&D",
    "Point d'avancement — Projet de recherche",
    "Compte-rendu de suivi technique",
    "Cahier de suivi des travaux de R&D",
]

NOMS_PROJETS = [
    "OPTIFLOW", "THERMOPACK", "NANOBUILD", "COGNITEST", "SMARTFAB",
    "BIOSYNTH", "DEEPVISION", "GREENCHEM", "AUTOFORGE", "QUANTISENSE",
]


def generate_compte_rendu_rd(pool: EntityPool, gabarit_id: str, seed: int) -> dict:
    random.seed(seed)
    entreprise = random.choice(pool.companies)
    participants = random.sample(pool.persons, min(random.randint(3, 6), len(pool.persons)))
    domaine = random.choice(pool.rd_domains) if pool.rd_domains else "logiciel"

    date_reunion = _rand_date(date(2024, 1, 1), date(2026, 10, 1))

    return {
        "template": f"compte_rendu_rd_{gabarit_id}.html",
        "classe": "compte_rendu_rd",
        "sous_type": "reunion_rd",
        "data": {
            "entreprise": entreprise,
            "titre_document": random.choice(TITRES_CR_RD),
            "nom_projet": random.choice(NOMS_PROJETS),
            "domaine_rd": domaine,
            "date_reunion": _fmt_date(date_reunion, random.choice(["fr", "long"])),
            "lieu": random.choice(["Salle de reunion A", "Visioconference", "Laboratoire", "Bureau d'etudes"]),
            "duree": f"{random.choice(['1h', '1h30', '2h', '2h30', '3h'])}",
            "redacteur": participants[0].full_name,
            "reference": f"CR-{date_reunion.year}-{random.randint(100, 999)}",
            "participants": participants,
            "ordre_du_jour": random.sample([
                "Revue de l'avancement des travaux",
                "Presentation des resultats experimentaux",
                "Discussion des verrous techniques identifies",
                "Planification des prochaines etapes",
                "Point sur le budget et les ressources",
                "Validation du protocole de test",
                "Analyse des ecarts par rapport au planning",
            ], random.randint(3, 5)),
            "travaux_realises": random.choice(TRAVAUX_RD),
            "resultats": random.choice([
                "Les resultats confirment la faisabilite technique de l'approche retenue. Les indicateurs de performance sont conformes aux objectifs intermediaires definis dans le plan de recherche.",
                "Les mesures realisees montrent que le systeme atteint les specifications cibles sur 4 des 5 criteres evalues. Le cinquieme critere necessite des ajustements qui sont en cours.",
                "L'analyse comparative des trois methodes testees montre un avantage significatif de la methode B en termes de precision, au prix d'un temps de calcul superieur de 30%.",
            ]),
            "verrous": random.sample(VERROUS_RD, random.randint(1, 2)),
            "prochaines_etapes": [
                {"description": random.choice(["Finaliser les tests de validation", "Rediger le rapport intermediaire", "Preparer la revue de conception"]),
                 "responsable": random.choice(participants).full_name,
                 "echeance": _fmt_date(date_reunion + timedelta(days=random.randint(7, 30)))}
                for _ in range(random.randint(2, 4))
            ],
        },
        "verite_terrain": {
            "date_reunion": date_reunion.isoformat(),
            "domaine_rd": domaine,
            "entreprise": entreprise.name,
            "nb_participants": len(participants),
        },
    }


TYPES_REUNION_NON_RD = [
    "Reunion commerciale", "Comite de direction", "Reunion de service RH",
    "Point hebdomadaire equipe", "Reunion de copropriete", "Comite social et economique",
]


def generate_compte_rendu_non_rd(pool: EntityPool, gabarit_id: str, seed: int) -> dict:
    random.seed(seed)
    entreprise = random.choice(pool.companies)
    participants = random.sample(pool.persons, min(random.randint(3, 6), len(pool.persons)))
    date_reunion = _rand_date(date(2024, 1, 1), date(2026, 10, 1))

    return {
        "template": f"compte_rendu_non_rd_{gabarit_id}.html",
        "classe": "autre",
        "sous_type": "compte_rendu_non_rd",
        "data": {
            "entreprise": entreprise,
            "titre_document": "Compte-rendu de reunion",
            "type_reunion": random.choice(TYPES_REUNION_NON_RD),
            "date_reunion": _fmt_date(date_reunion),
            "lieu": random.choice(["Salle de reunion B", "Visioconference", "Bureau du directeur"]),
            "duree": f"{random.choice(['45min', '1h', '1h30', '2h'])}",
            "redacteur": participants[0].full_name,
            "participants": participants,
            "ordre_du_jour": random.sample([
                "Bilan de l'activite commerciale du trimestre",
                "Presentation du budget previsionnel",
                "Point sur les recrutements en cours",
                "Organisation des evenements d'equipe",
                "Revue des indicateurs de performance",
                "Discussion sur la politique de teletravail",
            ], random.randint(2, 4)),
            "points_abordes": random.choice([
                "Le directeur commercial a presente le bilan du trimestre echelon. Le chiffre d'affaires est en hausse de 8% par rapport a l'annee precedente. Les objectifs de prospection ont ete atteints a 95%.",
                "Le service RH a fait le point sur les recrutements en cours. Trois postes sont ouverts et les entretiens debuteront la semaine prochaine. La campagne d'evaluation annuelle est lancee.",
                "Le comite a examine les resultats financiers de l'exercice. Les charges d'exploitation sont maitrisees. Un investissement dans la renovation des locaux est envisage pour le prochain exercice.",
            ]),
            "decisions": [
                {"titre": random.choice(["Validation du budget", "Recrutement approuve", "Report du projet"]),
                 "detail": random.choice(["Le comite approuve le budget previsionnel presente.", "Le recrutement d'un charge de projet est valide.", "Le lancement du projet est reporte au prochain trimestre."])}
            ],
            "actions": [
                {"responsable": random.choice(participants).full_name,
                 "description": random.choice(["Envoyer le compte-rendu aux absents", "Preparer le dossier pour la prochaine reunion", "Mettre a jour le tableau de suivi"]),
                 "echeance": _fmt_date(date_reunion + timedelta(days=random.randint(3, 14)))}
                for _ in range(random.randint(2, 3))
            ],
        },
        "verite_terrain": {},
    }


def generate_devis(pool: EntityPool, gabarit_id: str, seed: int) -> dict:
    random.seed(seed)
    emetteur = random.choice(pool.companies)
    destinataire = random.choice([c for c in pool.companies if c != emetteur])
    date_em = _rand_date(date(2024, 1, 1), date(2026, 10, 1))

    raw_lignes = []
    for _ in range(random.randint(2, 5)):
        qte = random.randint(1, 15)
        pu = round(random.uniform(200, 3000), 2)
        raw_lignes.append({"designation": random.choice(PRESTATIONS_FACTURE), "quantite": qte, "prix_unitaire": pu, "montant_ht": round(qte * pu, 2)})

    total_ht = sum(l["montant_ht"] for l in raw_lignes)
    taux_tva = random.choice([20, 10])
    montant_tva = round(total_ht * taux_tva / 100, 2)
    total_ttc = round(total_ht + montant_tva, 2)

    return {
        "template": f"devis_{gabarit_id}.html",
        "classe": "autre",
        "sous_type": "devis",
        "data": {
            "emetteur": emetteur,
            "destinataire": destinataire,
            "titre_document": random.choice(["Devis", "DEVIS", "Proposition commerciale", "Estimation"]),
            "numero": f"D-{date_em.year}-{random.randint(1000, 9999)}",
            "date_emission": _fmt_date(date_em),
            "date_validite": _fmt_date(date_em + timedelta(days=random.choice([30, 60, 90]))),
            "objet": random.choice(["Prestation de conseil technique", "Developpement d'une application", "Audit et optimisation", "Etude de faisabilite"]),
            "lignes": [{"designation": l["designation"], "quantite": l["quantite"], "prix_unitaire": _fmt_money(l["prix_unitaire"]), "montant_ht": _fmt_money(l["montant_ht"])} for l in raw_lignes],
            "total_ht": _fmt_money(total_ht),
            "taux_tva": taux_tva,
            "montant_tva": _fmt_money(montant_tva),
            "total_ttc": _fmt_money(total_ttc),
            "conditions": random.choice([
                "Delai d'execution : 4 a 6 semaines apres acceptation. Paiement : 30% a la commande, solde a la livraison.",
                "Ce devis est valable pour une duree de 30 jours. Toute modification fera l'objet d'un avenant.",
                "Les prix s'entendent hors frais de deplacement. Un acompte de 40% sera demande a la signature.",
            ]),
        },
        "verite_terrain": {},
    }


def generate_releve_bancaire(pool: EntityPool, gabarit_id: str, seed: int) -> dict:
    random.seed(seed)
    titulaire_co = random.choice(pool.companies)
    mois = random.randint(1, 12)
    annee = random.choice([2024, 2025, 2026])
    date_debut = date(annee, mois, 1)
    if mois == 12:
        date_fin = date(annee, 12, 31)
    else:
        date_fin = date(annee, mois + 1, 1) - timedelta(days=1)

    solde_prec = round(random.uniform(5000, 50000), 2)
    operations = []
    solde = solde_prec
    for day in sorted(random.sample(range(1, date_fin.day + 1), min(random.randint(8, 15), date_fin.day))):
        is_debit = random.random() > 0.4
        montant = round(random.uniform(50, 5000), 2)
        libelles_debit = ["VIREMENT EMIS", "PRELEVEMENT", "CB ACHAT", "CHEQUE", "FRAIS BANCAIRES"]
        libelles_credit = ["VIREMENT RECU", "REMISE CHEQUE", "ENCAISSEMENT", "AVOIR"]
        if is_debit:
            operations.append({"date": _fmt_date(date(annee, mois, day)), "libelle": f"{random.choice(libelles_debit)} {random.choice(['REF', 'N°'])}{random.randint(10000, 99999)}", "debit": _fmt_money(montant), "credit": ""})
            solde -= montant
        else:
            operations.append({"date": _fmt_date(date(annee, mois, day)), "libelle": f"{random.choice(libelles_credit)} {random.choice(['REF', 'N°'])}{random.randint(10000, 99999)}", "debit": "", "credit": _fmt_money(montant)})
            solde += montant

    total_debits = sum(float(op["debit"].replace(" ", "").replace(",", ".")) for op in operations if op["debit"])
    total_credits = sum(float(op["credit"].replace(" ", "").replace(",", ".")) for op in operations if op["credit"])

    return {
        "template": f"releve_bancaire_{gabarit_id}.html",
        "classe": "autre",
        "sous_type": "releve_bancaire",
        "data": {
            "nom_banque": random.choice(["Banque Fictive Nationale", "Credit Academique", "Banque du Projet", "Caisse Exemple"]),
            "banque_color": random.choice(["#1a5276", "#7d3c98", "#1e8449", "#b9770e"]),
            "titulaire": titulaire_co.name,
            "adresse_titulaire": titulaire_co.address,
            "cp_titulaire": titulaire_co.zip_code,
            "ville_titulaire": titulaire_co.city,
            "numero_compte": f"{random.randint(10000, 99999)}{random.randint(10000, 99999)}",
            "iban": titulaire_co.iban,
            "bic": f"FICX{''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=4))}",
            "date_debut": _fmt_date(date_debut),
            "date_fin": _fmt_date(date_fin),
            "solde_precedent": _fmt_money(solde_prec),
            "operations": operations,
            "total_debits": _fmt_money(round(total_debits, 2)),
            "total_credits": _fmt_money(round(total_credits, 2)),
            "nouveau_solde": _fmt_money(round(solde, 2)),
        },
        "verite_terrain": {},
    }


ARTICLES_CGV = [
    ("Objet", "Les presentes conditions generales de vente regissent l'ensemble des relations commerciales entre la societe et ses clients. Toute commande implique l'acceptation sans reserve des presentes conditions."),
    ("Prix", "Les prix sont indiques en euros hors taxes. La societe se reserve le droit de modifier ses tarifs a tout moment, les prestations etant facturees sur la base des prix en vigueur au moment de la commande."),
    ("Modalites de paiement", "Le paiement est exigible a reception de la facture, sauf accord contraire ecrit. Tout retard de paiement entrainera l'application de penalites de retard au taux legal en vigueur."),
    ("Livraison et delais", "Les delais de livraison sont donnes a titre indicatif. Un retard de livraison ne peut donner lieu a aucune penalite ni indemnite, ni motiver l'annulation de la commande."),
    ("Garantie", "Les prestations sont garanties conformes aux specifications convenues. Toute reclamation devra etre formulee par ecrit dans un delai de 30 jours suivant la livraison."),
    ("Responsabilite", "La responsabilite de la societe ne saurait exceder le montant de la commande. Elle ne pourra en aucun cas etre tenue responsable des dommages indirects."),
    ("Propriete intellectuelle", "L'ensemble des travaux realises reste la propriete de la societe jusqu'au paiement integral. Les droits de propriete intellectuelle sont cedes au client apres paiement complet."),
    ("Donnees personnelles", "Les informations recueillies font l'objet d'un traitement destine a la gestion de la relation commerciale, conformement a la reglementation en vigueur."),
    ("Attribution de competence", "Tout litige relatif a l'interpretation ou a l'execution des presentes conditions sera soumis aux tribunaux competents du siege social de la societe."),
]


def generate_cgv_notice(pool: EntityPool, gabarit_id: str, seed: int) -> dict:
    random.seed(seed)
    entreprise = random.choice(pool.companies)
    nb_articles = random.randint(5, len(ARTICLES_CGV))
    articles = [{"numero": i + 1, "titre": a[0], "contenu": a[1]} for i, a in enumerate(random.sample(ARTICLES_CGV, nb_articles))]

    return {
        "template": f"cgv_notice_{gabarit_id}.html",
        "classe": "autre",
        "sous_type": "cgv_notice",
        "data": {
            "titre_document": random.choice(["Conditions Generales de Vente", "CONDITIONS GENERALES DE VENTE", "Notice d'information", "Conditions Generales"]),
            "date_maj": _fmt_date(_rand_date(date(2023, 1, 1), date(2026, 6, 1)), "long"),
            "entreprise": entreprise.name,
            "articles": articles,
        },
        "verite_terrain": {},
    }


GENERATORS = {
    "facture": generate_facture,
    "fiche_de_paie": generate_fiche_de_paie,
    "contrat": generate_contrat,
    "compte_rendu_rd": generate_compte_rendu_rd,
    "devis": generate_devis,
    "compte_rendu_non_rd": generate_compte_rendu_non_rd,
    "releve_bancaire": generate_releve_bancaire,
    "cgv_notice": generate_cgv_notice,
}
