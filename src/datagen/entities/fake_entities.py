"""Generateur d'entites fictives avec pools disjoints (A=train, B=val, C=test)."""

from __future__ import annotations

import random
import string
from dataclasses import dataclass, field
from faker import Faker

fake = Faker("fr_FR")


@dataclass
class Company:
    name: str
    siren: str
    tva: str
    address: str
    city: str
    zip_code: str
    phone: str
    email: str
    iban: str
    logo_color: str = ""

    def __post_init__(self):
        if not self.logo_color:
            self.logo_color = random.choice([
                "#2563eb", "#dc2626", "#059669", "#7c3aed",
                "#d97706", "#0891b2", "#be185d", "#4f46e5",
            ])


@dataclass
class Person:
    first_name: str
    last_name: str
    full_name: str = ""
    email: str = ""
    phone: str = ""
    job_title: str = ""
    department: str = ""
    social_security: str = ""

    def __post_init__(self):
        if not self.full_name:
            self.full_name = f"{self.first_name} {self.last_name}"


def _generate_fake_siren() -> str:
    digits = "".join([str(random.randint(0, 9)) for _ in range(9)])
    return f"{digits[:3]} {digits[3:6]} {digits[6:9]}"


def _generate_fake_tva(siren: str) -> str:
    clean = siren.replace(" ", "")
    key = random.randint(10, 99)
    return f"FR{key} {clean}"


def _generate_fake_iban() -> str:
    bank = "".join([str(random.randint(0, 9)) for _ in range(10)])
    account = "".join([str(random.randint(0, 9)) for _ in range(11)])
    rib = str(random.randint(10, 99))
    return f"FR76 {bank[:4]} {bank[4:8]} {bank[8:10]}{account[:2]} {account[2:6]} {account[6:10]} {account[10]}{rib}"


COMPANY_PREFIXES = [
    "Alpha", "Beta", "Nexus", "Orion", "Vertex", "Sigma", "Delta", "Zenith",
    "Nova", "Helix", "Prism", "Cobalt", "Titan", "Vesta", "Pulsar", "Axiom",
    "Quasar", "Lyra", "Atlas", "Boreal", "Celsius", "Dynamo", "Eclipse",
    "Flux", "Genix", "Hydra", "Ionic", "Jade", "Krypton", "Lumen",
    "Magnet", "Nebula", "Optic", "Phenix", "Quantum", "Radix", "Solaris",
    "Triton", "Ultra", "Volton", "Watt", "Xenon", "Yotta", "Zephyr",
]

COMPANY_SUFFIXES = [
    "Solutions", "Technologies", "Conseil", "Ingenierie", "Systemes",
    "Services", "Industries", "Lab", "Groupe", "Digital", "Innovation",
    "Consulting", "Engineering", "Robotics", "Analytics", "Dynamics",
    "Materials", "Energy", "Biotech", "Software",
]

JOB_TITLES = [
    "Ingenieur R&D", "Chef de projet", "Directeur technique",
    "Responsable innovation", "Data scientist", "Architecte logiciel",
    "Ingenieur procedes", "Chercheur", "Technicien superieur",
    "Responsable qualite", "Ingenieur systemes", "Charge de recherche",
    "Directeur R&D", "Ingenieur materiaux", "Responsable production",
]

DEPARTMENTS = [
    "R&D", "Innovation", "Bureau d'etudes", "Production",
    "Qualite", "Informatique", "Mecanique", "Chimie",
    "Electronique", "Logiciel", "Materiaux", "Procedes",
]

RD_DOMAINS_POOL = {
    "A": ["chimie", "logiciel", "mecanique", "energie"],
    "B": ["materiaux", "electronique", "agronomie"],
    "C": ["sante", "robotique", "environnement"],
}


def _generate_company(used_names: set[str]) -> Company:
    for _ in range(100):
        name = f"{random.choice(COMPANY_PREFIXES)} {random.choice(COMPANY_SUFFIXES)}"
        if name not in used_names:
            used_names.add(name)
            break
    else:
        suffix = "".join(random.choices(string.ascii_uppercase, k=3))
        name = f"Societe {suffix}"
        used_names.add(name)

    siren = _generate_fake_siren()
    return Company(
        name=name,
        siren=siren,
        tva=_generate_fake_tva(siren),
        address=fake.street_address(),
        city=fake.city(),
        zip_code=fake.postcode(),
        phone=fake.phone_number(),
        email=f"contact@{name.lower().replace(' ', '-')}.example.org",
        iban=_generate_fake_iban(),
    )


def _generate_person() -> Person:
    first = fake.first_name()
    last = fake.last_name()
    ss = "".join([str(random.randint(0, 9)) for _ in range(13)])
    return Person(
        first_name=first,
        last_name=last,
        email=f"{first.lower()}.{last.lower()}@example.org",
        phone=fake.phone_number(),
        job_title=random.choice(JOB_TITLES),
        department=random.choice(DEPARTMENTS),
        social_security=f"{ss[:1]} {ss[1:3]} {ss[3:5]} {ss[5:7]} {ss[7:10]} {ss[10:13]}",
    )


@dataclass
class EntityPool:
    pool_id: str
    companies: list[Company] = field(default_factory=list)
    persons: list[Person] = field(default_factory=list)
    rd_domains: list[str] = field(default_factory=list)


def generate_pools(
    companies_per_pool: int = 8,
    persons_per_pool: int = 15,
    seed: int = 42,
) -> dict[str, EntityPool]:
    random.seed(seed)
    Faker.seed(seed)

    used_names: set[str] = set()
    pools: dict[str, EntityPool] = {}

    for pool_id in ("A", "B", "C"):
        companies = [_generate_company(used_names) for _ in range(companies_per_pool)]
        persons = [_generate_person() for _ in range(persons_per_pool)]
        domains = RD_DOMAINS_POOL.get(pool_id, [])

        pools[pool_id] = EntityPool(
            pool_id=pool_id,
            companies=companies,
            persons=persons,
            rd_domains=domains,
        )

    return pools
