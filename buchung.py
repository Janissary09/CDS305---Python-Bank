# buchung.py


# ----------------------------------------------------------
# Verbucht eine Einzahlung im Banksystem (Double Entry)
# ----------------------------------------------------------

def buche_einzahlung(bank, betrag):

    # Zentralbankkonto erhöhen (Aktiva)
    bank["zentralbank"] += betrag

    # Verpflichtung gegenüber Kunde erhöhen (Passiva)
    bank["verpflichtung"] += betrag

    return bank


# ----------------------------------------------------------
# Verbucht eine Überweisung im Banksystem
# ----------------------------------------------------------

def buche_ueberweisung(bank, betrag):

    # Bei interner Überweisung ändert sich nur Verpflichtung nicht
    # → Geld bleibt im System (nur Kunde A → Kunde B)

    return bank