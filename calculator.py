"""Výpočetní logika hypoteční kalkulačky (bez závislosti na Flasku)."""
from dataclasses import dataclass

# Orientační limity – před odevzdáním ověřit podle aktuálních doporučení ČNB
LIMITY = {"ltv": 90.0, "dsti": 45.0, "dti": 8.5}


@dataclass
class Vstup:
    prijem: float    # čistý měsíční příjem (Kč)
    vydaje: float    # měsíční výdaje na živobytí (Kč)
    splatky: float   # splátky stávajících úvěrů (Kč/měs.)
    cena: float      # cena nemovitosti (Kč)
    vlastni: float   # vlastní zdroje (Kč)
    urok: float      # úroková sazba (% p. a.)
    roky: int        # doba splácení (roky)


def mesicni_splatka(jistina: float, urok_pa: float, roky: int) -> float:
    """Měsíční splátka anuitního úvěru."""
    if jistina <= 0:
        return 0.0
    n = roky * 12
    r = urok_pa / 100 / 12
    if r == 0:
        return jistina / n
    return jistina * r / (1 - (1 + r) ** -n)


def max_uver(splatka: float, urok_pa: float, roky: int) -> float:
    """Nejvyšší úvěr, který lze splácet danou měsíční splátkou."""
    if splatka <= 0:
        return 0.0
    n = roky * 12
    r = urok_pa / 100 / 12
    if r == 0:
        return splatka * n
    return splatka * (1 - (1 + r) ** -n) / r


def amortizace(jistina: float, urok_pa: float, roky: int) -> list[dict]:
    """Roční přehled splácení: úroky, splacená jistina a zůstatek na konci roku."""
    splatka = mesicni_splatka(jistina, urok_pa, roky)
    r = urok_pa / 100 / 12
    zustatek = jistina
    plan = []
    for rok in range(1, roky + 1):
        urok_rok = jistina_rok = 0.0
        for _ in range(12):
            urok_m = zustatek * r
            jistina_m = splatka - urok_m
            zustatek -= jistina_m
            urok_rok += urok_m
            jistina_rok += jistina_m
        plan.append({"rok": rok, "urok": urok_rok, "jistina": jistina_rok,
                     "zustatek": max(zustatek, 0.0)})
    return plan


def scenare(jistina: float, urok_pa: float, roky: int) -> list[dict]:
    """Porovnání splátky při změně úrokové sazby o -1, 0, +1 a +2 procentní body."""
    vysledek = []
    for zmena in (-1.0, 0.0, 1.0, 2.0):
        urok = max(urok_pa + zmena, 0.0)
        splatka = mesicni_splatka(jistina, urok, roky)
        vysledek.append({"zmena": zmena, "urok": urok, "splatka": splatka,
                         "celkem_urok": splatka * roky * 12 - jistina})
    return vysledek


def validuj(v: Vstup) -> list[str]:
    """Vrátí seznam chyb (prázdný seznam = vstup je v pořádku)."""
    chyby = []
    if v.prijem <= 0:
        chyby.append("Příjem musí být větší než 0.")
    if v.cena <= 0:
        chyby.append("Cena nemovitosti musí být větší než 0.")
    if min(v.vydaje, v.splatky, v.vlastni, v.urok) < 0:
        chyby.append("Hodnoty nesmějí být záporné.")
    if v.vlastni > v.cena:
        chyby.append("Vlastní zdroje nemohou být vyšší než cena nemovitosti.")
    if not 5 <= v.roky <= 30:
        chyby.append("Doba splácení musí být 5 až 30 let.")
    return chyby


def vypocitej(v: Vstup) -> dict:
    uver = v.cena - v.vlastni
    splatka = mesicni_splatka(uver, v.urok, v.roky)
    ltv = uver / v.cena * 100
    dsti = (splatka + v.splatky) / v.prijem * 100
    dti = (uver + v.splatky * 12) / (v.prijem * 12)

    limit_dsti = v.prijem * LIMITY["dsti"] / 100 - v.splatky
    limit_rozpocet = v.prijem - v.vydaje - v.splatky
    max_splatka = max(0.0, min(limit_dsti, limit_rozpocet))

    podminky = {
        f"LTV do {LIMITY['ltv']:g} %": ltv <= LIMITY["ltv"],
        f"DSTI do {LIMITY['dsti']:g} %": dsti <= LIMITY["dsti"],
        f"DTI do {LIMITY['dti']:g}násobku ročního příjmu": dti <= LIMITY["dti"],
        "Splátka se vejde do rozpočtu po výdajích": splatka <= limit_rozpocet,
    }
    splneno = sum(podminky.values())
    if splneno == len(podminky):
        verdikt = ("ok", "Hypotéku by pravděpodobně bylo možné získat")
    elif splneno >= 2:
        verdikt = ("warn", "Hraniční situace – některé podmínky nejsou splněny")
    else:
        verdikt = ("bad", "Podle zadaných údajů by hypotéka byla obtížná")

    return {
        "uver": uver, "splatka": splatka, "ltv": ltv, "dsti": dsti, "dti": dti,
        "max_splatka": max_splatka,
        "max_uver": max_uver(max_splatka, v.urok, v.roky),
        "podminky": podminky, "verdikt": verdikt,
        "plan": amortizace(uver, v.urok, v.roky),
        "scenare": scenare(uver, v.urok, v.roky),
        "limity": LIMITY,
        "celkem_zaplaceno": splatka * v.roky * 12,
        "celkem_urok": splatka * v.roky * 12 - uver,
    }
