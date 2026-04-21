# kredit.py

# ----------------------------------------------------------
# Vergibt einen Kredit an einen Kunden
# ----------------------------------------------------------

def kredit_vergeben(accounts, iban, betrag, timestamp):

    # Prüft, ob Konto existiert
    if iban not in accounts:
        return accounts

    # Prüft Betrag (min / max)
    if betrag < 1000 or betrag > 15000:
        return accounts

    # Kreditbetrag zum Konto hinzufügen
    accounts[iban]["kontostand"] += betrag

    # Kreditstand erhöhen
    accounts[iban]["kreditstand"] += betrag

    # Gebühr abziehen (250 CHF)
    accounts[iban]["kontostand"] -= 250

    # Transaktion: Kredit Auszahlung
    tx_kredit = {
        "zeitstempel": timestamp,
        "typ": "kredit_auszahlung",
        "betrag": betrag,
        "saldo_nachher": accounts[iban]["kontostand"],
        "status": "ok"
    }

    # Transaktion: Gebühr
    tx_fee = {
        "zeitstempel": timestamp,
        "typ": "kredit_gebuehr",
        "betrag": -250,
        "saldo_nachher": accounts[iban]["kontostand"],
        "status": "ok"
    }

    accounts[iban]["transaktionen"].append(tx_kredit)
    accounts[iban]["transaktionen"].append(tx_fee)

    return accounts

# ----------------------------------------------------------
# Berechnet monatliche Kreditzinsen
# ----------------------------------------------------------

def kredit_zinsen_berechnen(accounts, iban, timestamp):

    if iban not in accounts:
        return accounts

    restschuld = accounts[iban]["kreditstand"]

    if restschuld <= 0:
        return accounts

    # Zinsen: 15% p.a. → monatlich
    zinsen = restschuld * (0.15 / 12)

    # Zinsen vom Konto abbuchen
    accounts[iban]["kontostand"] -= zinsen

    tx = {
        "zeitstempel": timestamp,
        "typ": "kredit_zinsen",
        "betrag": -zinsen,
        "saldo_nachher": accounts[iban]["kontostand"],
        "status": "ok"
    }

    accounts[iban]["transaktionen"].append(tx)

    return accounts

# ----------------------------------------------------------
# Führt die monatliche Kreditamortisation durch
# ----------------------------------------------------------

def kredit_amortisation(accounts, iban, timestamp):

    # Prüft, ob Konto existiert
    if iban not in accounts:
        return accounts

    kreditstand = accounts[iban]["kreditstand"]

    # Kein Kredit vorhanden
    if kreditstand <= 0:
        return accounts

    # Monatliche Tilgung (lineare Rückzahlung)
    tilgung = kreditstand / 12

    # Betrag vom Konto abbuchen
    accounts[iban]["kontostand"] -= tilgung

    # Kreditstand reduzieren
    accounts[iban]["kreditstand"] -= tilgung

    # Transaktion speichern
    tx = {
        "zeitstempel": timestamp,
        "typ": "kredit_amortisation",
        "betrag": -tilgung,
        "saldo_nachher": accounts[iban]["kontostand"],
        "status": "ok"
    }

    accounts[iban]["transaktionen"].append(tx)

    return accounts

# ----------------------------------------------------------
# Berechnet tägliche Strafzinsen bei negativem Kontostand
# ----------------------------------------------------------

def kredit_strafzins(accounts, iban, timestamp):

    # Prüft, ob Konto existiert
    if iban not in accounts:
        return accounts

    kontostand = accounts[iban]["kontostand"]

    # Nur bei negativem Kontostand
    if kontostand >= 0:
        return accounts

    # Strafzins berechnen (30% p.a. / 365 Tage)
    strafzins = abs(kontostand) * (0.30 / 365)

    # Strafzins zum Konto hinzufügen (noch mehr Minus)
    accounts[iban]["kontostand"] -= strafzins

    # Transaktion speichern
    tx = {
        "zeitstempel": timestamp,
        "typ": "strafzins",
        "betrag": -strafzins,
        "saldo_nachher": accounts[iban]["kontostand"],
        "status": "ok"
    }

    accounts[iban]["transaktionen"].append(tx)

    return accounts

# ----------------------------------------------------------
# Prüft, ob ein Kredit abgeschrieben werden muss (vereinfachte Logik)
# ----------------------------------------------------------

def kredit_abschreibung(accounts, iban, bank, timestamp):

    # Prüft, ob Konto existiert
    if iban not in accounts:
        return accounts, bank

    kreditstand = accounts[iban]["kreditstand"]

    # Kein Kredit vorhanden
    if kreditstand <= 0:
        return accounts, bank

    # Abschreibung nur bei negativem Kontostand (vereinfachte Regel)
    if accounts[iban]["kontostand"] >= 0:
        return accounts, bank

    # Gesamten Kredit abschreiben
    abgeschrieben = kreditstand

    # Kreditstand auf 0 setzen
    accounts[iban]["kreditstand"] = 0

    # Verlust in der Bank verbuchen
    bank["kredit"] -= abgeschrieben
    bank["einnahmen"] -= abgeschrieben

    # Transaktion speichern
    tx = {
        "zeitstempel": timestamp,
        "typ": "abschreibung",
        "betrag": -abgeschrieben,
        "saldo_nachher": accounts[iban]["kontostand"],
        "status": "ok"
    }

    accounts[iban]["transaktionen"].append(tx)

    return accounts, bank
