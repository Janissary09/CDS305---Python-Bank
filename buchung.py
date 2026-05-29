# buchung.py


# ----------------------------------------------------------
# Speichert eine Bankbuchung fuer die Ausgabe
# ----------------------------------------------------------

def speichere_bankbuchung(bank, zeitstempel, vorgang, referenz, soll_konto, soll_betrag, haben_konto, haben_betrag):

    bank["buchungen"].append({
        "zeitstempel": zeitstempel,
        "vorgang": vorgang,
        "referenz": referenz,
        "soll_konto": soll_konto,
        "soll_betrag": round(soll_betrag, 2),
        "haben_konto": haben_konto,
        "haben_betrag": round(haben_betrag, 2)
    })


# ----------------------------------------------------------
# Verbucht eine Einzahlung im Banksystem (Double Entry)
# ----------------------------------------------------------

def buche_einzahlung(bank, betrag, zeitstempel="", referenz=""):

    # Bankbuchung zaehlen
    bank["anzahl_buchungen"] += 1
    speichere_bankbuchung(
        bank, zeitstempel, "ueberweisung_ein", referenz,
        "zentralbankkonto", betrag,
        "verpflichtungskonto", betrag
    )

    # Zentralbankkonto erhöhen (Aktiva)
    bank["zentralbank"] += betrag

    # Verpflichtung gegenüber Kunde erhöhen (Passiva)
    bank["verpflichtung"] += betrag

    return bank


# ----------------------------------------------------------
# Verbucht eine ausgehende Ueberweisung im Banksystem
# ----------------------------------------------------------

def buche_ueberweisung(bank, betrag, intern, zeitstempel="", referenz=""):

    # Interne Ueberweisung: kein Effekt auf Bankkonten
    if intern:
        return bank

    # Bankbuchung zaehlen
    bank["anzahl_buchungen"] += 1
    speichere_bankbuchung(
        bank, zeitstempel, "ueberweisung_aus", referenz,
        "verpflichtungskonto", betrag,
        "zentralbankkonto", betrag
    )

    # Externe Ueberweisung:
    # Verpflichtung gegenueber Kunde sinkt
    bank["verpflichtung"] -= betrag

    # Geld verlaesst die Bank
    bank["zentralbank"] -= betrag

    return bank


# ----------------------------------------------------------
# Verbucht eine Kreditauszahlung im Banksystem
# ----------------------------------------------------------

def buche_kredit_auszahlung(bank, betrag, zeitstempel="", referenz=""):

    # Bankbuchung zaehlen
    bank["anzahl_buchungen"] += 1
    speichere_bankbuchung(
        bank, zeitstempel, "kredit_auszahlung", referenz,
        "kreditkonto_aktiva", betrag,
        "verpflichtungskonto", betrag
    )

    # Kreditkonto erhöhen (Aktiva)
    bank["kredit"] += betrag

    # Verpflichtung gegenüber Kunde erhöhen (Passiva)
    bank["verpflichtung"] += betrag

    return bank


# ----------------------------------------------------------
# Verbucht Kreditgebuehren oder Kreditzinsen im Banksystem
# ----------------------------------------------------------

def buche_einnahme(bank, betrag, zeitstempel="", vorgang="einnahme", referenz=""):

    # Bankbuchung zaehlen
    bank["anzahl_buchungen"] += 1
    speichere_bankbuchung(
        bank, zeitstempel, vorgang, referenz,
        "verpflichtungskonto", betrag,
        "einnahmenkonto", betrag
    )

    # Verpflichtung gegenüber Kunde reduzieren
    bank["verpflichtung"] -= betrag

    # Einnahmen erhöhen
    bank["einnahmen"] += betrag

    return bank


# ----------------------------------------------------------
# Verbucht die Kontofuehrungsgebuehr im Banksystem
# ----------------------------------------------------------

def buche_kontogebuehr(bank, betrag, zeitstempel="", referenz=""):

    # Bankbuchung zaehlen
    bank["anzahl_buchungen"] += 1
    speichere_bankbuchung(
        bank, zeitstempel, "kontogebuehr", referenz,
        "verpflichtungskonto", betrag,
        "einnahmenkonto", betrag
    )

    # Verpflichtung gegenueber Kunde reduzieren
    bank["verpflichtung"] -= betrag

    # Einnahmen erhoehen
    bank["einnahmen"] += betrag

    return bank


# ----------------------------------------------------------
# Verbucht eine Kredittilgung im Banksystem
# ----------------------------------------------------------

def buche_kredittilgung(bank, betrag, zeitstempel="", vorgang="kredit_amortisation", referenz=""):

    # Bankbuchung zaehlen
    bank["anzahl_buchungen"] += 1
    speichere_bankbuchung(
        bank, zeitstempel, vorgang, referenz,
        "verpflichtungskonto", betrag,
        "kreditkonto_aktiva", betrag
    )

    # Verpflichtung gegenueber Kunde reduzieren
    bank["verpflichtung"] -= betrag

    # Kreditkonto reduzieren
    bank["kredit"] -= betrag

    return bank


# ----------------------------------------------------------
# Verbucht Strafzinsen im Banksystem
# ----------------------------------------------------------

def buche_strafzins(bank, betrag, zeitstempel="", referenz=""):

    # Bankbuchung zaehlen
    bank["anzahl_buchungen"] += 1
    speichere_bankbuchung(
        bank, zeitstempel, "strafzinsen", referenz,
        "kreditkonto_aktiva", betrag,
        "einnahmenkonto", betrag
    )

    # Kreditkonto erhoehen
    bank["kredit"] += betrag

    # Einnahmen erhoehen
    bank["einnahmen"] += betrag

    return bank


# ----------------------------------------------------------
# Prueft die Bilanzgleichung der Bank
# ----------------------------------------------------------

def pruefe_bilanz(bank):

    aktiva = bank["zentralbank"] + bank["kredit"]
    passiva_und_erfolg = bank["verpflichtung"] + bank["einnahmen"]

    return abs(aktiva - passiva_und_erfolg) <= 0.0001
