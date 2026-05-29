# konten.py

        
# ----------------------------------------------------------
# Erstellt eine neue IBAN für die Bank
# ----------------------------------------------------------

def generiere_iban(naechste_nummer):

    # Kontonummer als 12-stellige Zahl formatieren
    kontonummer = str(naechste_nummer).zfill(12)

    # Vereinfachte Pruefziffer: letzte Stelle der Kontonummer
    pruefziffer_konto = kontonummer[-1]

    # IBAN ohne Leerzeichen zusammenbauen
    iban = f"CH0000762{kontonummer}{pruefziffer_konto}"

    return iban


# ----------------------------------------------------------
# Erstellt ein neues Konto fuer einen Kunden
# ----------------------------------------------------------

def konto_eroeffnen(accounts, kunde, naechste_nummer, timestamp):

    # Prüft, ob fuer dieselbe Person bereits ein Konto existiert
    for bestehende_iban, konto in accounts.items():
        if (
            konto["kunde"]["name"] == kunde["name"]
            and konto["kunde"]["adresse"] == kunde["adresse"]
            and konto["kunde"]["geburtsdatum"] == kunde["geburtsdatum"]
        ):
            tx_fail = {
                "zeitstempel": timestamp,
                "typ": "konto_eroeffnen",
                "betrag": 0.0,
                "saldo_nachher": konto["kontostand"],
                "status": "fail",
                "ablehnungsgrund": "Kunde hat bereits ein Konto"
            }

            accounts[bestehende_iban]["transaktionen"].append(tx_fail)
            return accounts, bestehende_iban, naechste_nummer

    # Neue IBAN generieren
    iban = generiere_iban(naechste_nummer)

    accounts[iban] = {
        "konto_iban": iban,
        "kunde": {
            "name": kunde["name"],
            "adresse": kunde["adresse"],
            "geburtsdatum": kunde["geburtsdatum"]
        },
        "kontostand": 0.0,
        "kreditstand": 0.0,
        "kreditbetrag": 0.0,
        "status": "aktiv",
        "eroeffnungsdatum": timestamp[:10],
        "monate_ohne_tilgung": 0,
        "transaktionen": []
    }

    tx = {
        "zeitstempel": timestamp,
        "typ": "konto_eroeffnen",
        "betrag": 0.0,
        "saldo_nachher": 0.0,
        "status": "ok"
    }

    accounts[iban]["transaktionen"].append(tx)

    return accounts, iban, naechste_nummer + 1


# ----------------------------------------------------------
# Fuehrt eine Einzahlung auf ein Konto aus und speichert die Transaktion
# ----------------------------------------------------------

def einzahlung(accounts, iban, betrag, timestamp):

    # Prüft, ob das Konto existiert
    if iban not in accounts:
        return accounts, 0.0
    
    # Geschlossene Konten nehmen keine Einzahlungen mehr an
    if accounts[iban]["status"] == "geschlossen":
        tx_fail = {
            "zeitstempel": timestamp,
            "typ": "ueberweisung_ein",
            "betrag": betrag,
            "saldo_nachher": accounts[iban]["kontostand"],
            "status": "fail",
            "ablehnungsgrund": "Konto ist geschlossen"
        }

        accounts[iban]["transaktionen"].append(tx_fail)
        return accounts, 0.0

    # Erhöht den Kontostand
    accounts[iban]["kontostand"] += betrag

    # Erstellt den Einzahlungseintrag
    tx = {
        "zeitstempel": timestamp,
        "typ": "ueberweisung_ein",
        "betrag": betrag,
        "saldo_nachher": accounts[iban]["kontostand"],
        "status": "ok"
    }

    accounts[iban]["transaktionen"].append(tx)

    # Standardwert: keine Nachzahlung
    nachzahlung = 0.0

    # Prüft, ob ein gesperrtes Konto wieder aktiviert werden kann
    if accounts[iban]["status"] == "gesperrt" and accounts[iban]["kreditstand"] > 0:

        tilgung = accounts[iban]["kreditstand"] / 12

        # Konto entsperren und Nachzahlung sofort abbuchen
        if accounts[iban]["kontostand"] >= tilgung:
            accounts[iban]["status"] = "aktiv"
            accounts[iban]["kontostand"] -= tilgung
            accounts[iban]["kreditstand"] -= tilgung
            
            nachzahlung = tilgung

            tx_nachzahlung = {
                "zeitstempel": timestamp,
                "typ": "kredit_rueckzahlung",
                "betrag": -tilgung,
                "saldo_nachher": accounts[iban]["kontostand"],
                "status": "ok"
            }

            accounts[iban]["transaktionen"].append(tx_nachzahlung)

    return accounts, nachzahlung


# ----------------------------------------------------------
# Fuehrt eine Ueberweisung aus (intern oder extern)
# ----------------------------------------------------------

def ueberweisung(accounts, von_iban, nach_iban, betrag, timestamp):

    # Prüft, ob das Senderkonto existiert
    if von_iban not in accounts:
        return accounts, False
    
    # Geschlossene Konten duerfen keine Ueberweisungen ausfuehren
    if accounts[von_iban]["status"] == "geschlossen":

        tx_fail = {
            "zeitstempel": timestamp,
            "typ": "ueberweisung_aus",
            "betrag": betrag,
            "saldo_nachher": accounts[von_iban]["kontostand"],
            "status": "fail",
            "ablehnungsgrund": "Konto ist geschlossen"
        }

        accounts[von_iban]["transaktionen"].append(tx_fail)
        return accounts, False

    # Prüft, ob das Senderkonto gesperrt ist
    if accounts[von_iban]["status"] == "gesperrt":

        tx_fail = {
            "zeitstempel": timestamp,
            "typ": "ueberweisung_aus",
            "betrag": betrag,
            "saldo_nachher": accounts[von_iban]["kontostand"],
            "status": "fail",
            "ablehnungsgrund": "Konto ist gesperrt"
        }

        accounts[von_iban]["transaktionen"].append(tx_fail)
        return accounts, False

    # Prüft, ob genügend Guthaben vorhanden ist
    if accounts[von_iban]["kontostand"] < betrag:

        tx_fail = {
            "zeitstempel": timestamp,
            "typ": "ueberweisung_aus",
            "betrag": betrag,
            "saldo_nachher": accounts[von_iban]["kontostand"],
            "status": "fail",
            "ablehnungsgrund": "Ungenuegendes Guthaben"
        }

        accounts[von_iban]["transaktionen"].append(tx_fail)
        return accounts, False

    # Betrag vom Senderkonto abziehen
    accounts[von_iban]["kontostand"] -= betrag

    tx_out = {
        "zeitstempel": timestamp,
        "typ": "ueberweisung_aus",
        "betrag": betrag,
        "saldo_nachher": accounts[von_iban]["kontostand"],
        "status": "ok"
    }

    accounts[von_iban]["transaktionen"].append(tx_out)

    # Interne Ueberweisung: Empfaengerkonto gutschreiben
    if nach_iban in accounts:
        accounts[nach_iban]["kontostand"] += betrag

        tx_in = {
            "zeitstempel": timestamp,
            "typ": "ueberweisung_ein",
            "betrag": betrag,
            "saldo_nachher": accounts[nach_iban]["kontostand"],
            "status": "ok"
        }

        accounts[nach_iban]["transaktionen"].append(tx_in)

    return accounts, True


# ----------------------------------------------------------
# Belastet die quartalsweise Kontofuehrungsgebuehr
# ----------------------------------------------------------

def kontogebuehr_belasten(accounts, iban, timestamp):

    # Prüft, ob Konto existiert
    if iban not in accounts:
        return accounts

    # Kontogebuehr immer belasten
    gebuehr = 25.0
    accounts[iban]["kontostand"] -= gebuehr

    tx = {
        "zeitstempel": timestamp,
        "typ": "kontogebuehr",
        "betrag": -gebuehr,
        "saldo_nachher": accounts[iban]["kontostand"],
        "status": "ok"
    }

    accounts[iban]["transaktionen"].append(tx)

    return accounts


# ----------------------------------------------------------
# Aendert die Kundendaten eines bestehenden Kontos
# ----------------------------------------------------------

def kunden_daten_aendern(accounts, iban, neue_daten, timestamp):

    # Prüft, ob Konto existiert
    if iban not in accounts:
        return accounts, False
    
    # Geschlossene Konten koennen nicht mehr geaendert werden
    if accounts[iban]["status"] == "geschlossen":
        tx_fail = {
            "zeitstempel": timestamp,
            "typ": "daten_aendern",
            "betrag": 0.0,
            "saldo_nachher": accounts[iban]["kontostand"],
            "status": "fail",
            "ablehnungsgrund": "Konto ist geschlossen"
        }

        accounts[iban]["transaktionen"].append(tx_fail)
        return accounts, False

    # Vorhandene Kundendaten aktualisieren
    for feld in ["name", "adresse", "geburtsdatum"]:
        if feld in neue_daten:
            accounts[iban]["kunde"][feld] = neue_daten[feld]

    tx = {
        "zeitstempel": timestamp,
        "typ": "daten_aendern",
        "betrag": 0.0,
        "saldo_nachher": accounts[iban]["kontostand"],
        "status": "ok"
    }

    accounts[iban]["transaktionen"].append(tx)

    return accounts, True


# ----------------------------------------------------------
# Schliesst ein Konto, wenn Kontostand und Kreditstand null sind
# ----------------------------------------------------------

def konto_schliessen(accounts, iban, timestamp):

    # Prüft, ob Konto existiert
    if iban not in accounts:
        return accounts, False
    
    # Bereits geschlossene Konten koennen nicht erneut geschlossen werden
    if accounts[iban]["status"] == "geschlossen":

        tx_fail = {
            "zeitstempel": timestamp,
            "typ": "konto_schliessen",
            "betrag": 0.0,
            "saldo_nachher": accounts[iban]["kontostand"],
            "status": "fail",
            "ablehnungsgrund": "Konto ist bereits geschlossen"
        }

        accounts[iban]["transaktionen"].append(tx_fail)
        return accounts, False

    # Konto darf nur geschlossen werden, wenn alles null ist
    if abs(accounts[iban]["kontostand"]) > 0.0001 or abs(accounts[iban]["kreditstand"]) > 0.0001:

        tx_fail = {
            "zeitstempel": timestamp,
            "typ": "konto_schliessen",
            "betrag": 0.0,
            "saldo_nachher": accounts[iban]["kontostand"],
            "status": "fail",
            "ablehnungsgrund": "Kontostand oder Kreditstand ist nicht null"
        }

        accounts[iban]["transaktionen"].append(tx_fail)
        return accounts, False

    # Status auf geschlossen setzen
    accounts[iban]["status"] = "geschlossen"

    accounts[iban]["monate_ohne_tilgung"] = 0

    tx = {
        "zeitstempel": timestamp,
        "typ": "konto_schliessen",
        "betrag": 0.0,
        "saldo_nachher": accounts[iban]["kontostand"],
        "status": "ok"
    }

    accounts[iban]["transaktionen"].append(tx)

    return accounts, True