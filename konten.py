# ----------------------------------------------------------
# Erstellt ein neues Konto für einen Kunden
# ----------------------------------------------------------

def konto_eroeffnen(accounts, kunde):
    iban = kunde["iban"]

    accounts[iban] = {
        "konto_iban": iban,
        "kunde": {
            "name": kunde["name"],
            "adresse": kunde["adresse"],
            "geburtsdatum": kunde["geburtsdatum"]
        },
        "kontostand": 0.0,
        "kreditstand": 0.0,
        "status": "aktiv",
        "transaktionen": []
    }

    return accounts


# ----------------------------------------------------------
# Führt eine Einzahlung auf ein Konto aus und speichert die Transaktion
# ----------------------------------------------------------

def einzahlung(accounts, iban, betrag, timestamp):

    # Prüft, ob das Konto existiert
    if iban not in accounts:
        return accounts

    # Erhöht den Kontostand
    accounts[iban]["kontostand"] += betrag

    # Erstellt den Transaktionseintrag im geforderten Format
    tx = {
        "zeitstempel": timestamp,
        "typ": "einzahlung",
        "betrag": betrag,
        "saldo_nachher": accounts[iban]["kontostand"],
        "status": "ok"
    }

    # Fügt die Transaktion zur Historie hinzu
    accounts[iban]["transaktionen"].append(tx)

    return accounts


# ----------------------------------------------------------
# Führt eine Überweisung zwischen zwei Konten aus
# ----------------------------------------------------------

def ueberweisung(accounts, von_iban, nach_iban, betrag, timestamp):

    # Prüft, ob beide Konten existieren
    if von_iban not in accounts or nach_iban not in accounts:
        return accounts

    # Prüft, ob genügend Guthaben vorhanden ist
    if accounts[von_iban]["kontostand"] < betrag:

        # Fehlgeschlagene Transaktion wird gespeichert
        tx_fail = {
            "zeitstempel": timestamp,
            "typ": "ueberweisung",
            "betrag": betrag,
            "saldo_nachher": accounts[von_iban]["kontostand"],
            "status": "fail"
        }

        accounts[von_iban]["transaktionen"].append(tx_fail)
        return accounts

    # Betrag vom Senderkonto abziehen
    accounts[von_iban]["kontostand"] -= betrag

    # Betrag dem Empfängerkonto gutschreiben
    accounts[nach_iban]["kontostand"] += betrag

    # Erfolgreiche Transaktion beim Sender speichern
    tx_out = {
        "zeitstempel": timestamp,
        "typ": "ueberweisung_aus",
        "betrag": betrag,
        "saldo_nachher": accounts[von_iban]["kontostand"],
        "status": "ok"
    }

    # Erfolgreiche Transaktion beim Empfänger speichern
    tx_in = {
        "zeitstempel": timestamp,
        "typ": "ueberweisung_ein",
        "betrag": betrag,
        "saldo_nachher": accounts[nach_iban]["kontostand"],
        "status": "ok"
    }

    # Transaktionen zur Historie hinzufügen
    accounts[von_iban]["transaktionen"].append(tx_out)
    accounts[nach_iban]["transaktionen"].append(tx_in)

    return accounts