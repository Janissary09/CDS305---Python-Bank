# kredit.py

from decimal import Decimal, ROUND_HALF_EVEN


# ----------------------------------------------------------
# Vergibt einen Kredit an einen Kunden
# ----------------------------------------------------------

def kredit_vergeben(accounts, iban, betrag, timestamp):

    # Prüft, ob Konto existiert
    if iban not in accounts:
        return accounts, False
    
    # Geschlossene Konten duerfen keinen Kredit erhalten
    if accounts[iban]["status"] == "geschlossen":
        tx_fail = {
            "zeitstempel": timestamp,
            "typ": "kredit_antrag",
            "betrag": betrag,
            "saldo_nachher": accounts[iban]["kontostand"],
            "status": "fail",
            "ablehnungsgrund": "Konto ist geschlossen"
        }

        accounts[iban]["transaktionen"].append(tx_fail)
        return accounts, False

    # Prüft Betrag (min / max)
    if betrag < 1000 or betrag > 15000:
        tx_fail = {
            "zeitstempel": timestamp,
            "typ": "kredit_antrag",
            "betrag": betrag,
            "saldo_nachher": accounts[iban]["kontostand"],
            "status": "fail",
            "ablehnungsgrund": "Kreditbetrag ist ungueltig"
        }

        accounts[iban]["transaktionen"].append(tx_fail)
        return accounts, False

    # Prüft, ob bereits ein laufender Kredit existiert
    if accounts[iban]["kreditstand"] > 0:
        tx_fail = {
            "zeitstempel": timestamp,
            "typ": "kredit_antrag",
            "betrag": betrag,
            "saldo_nachher": accounts[iban]["kontostand"],
            "status": "fail",
            "ablehnungsgrund": "Es besteht bereits ein laufender Kredit"
        }

        accounts[iban]["transaktionen"].append(tx_fail)
        return accounts, False

    # Kreditbetrag zum Konto hinzufügen
    accounts[iban]["kontostand"] += betrag

    # Kreditstand erhöhen
    accounts[iban]["kreditstand"] += betrag

    # Urspruenglichen Kreditbetrag speichern
    accounts[iban]["kreditbetrag"] = betrag

    # Saldo nach Kreditauszahlung speichern
    saldo_nach_kredit = accounts[iban]["kontostand"]

    # Gebühr abziehen (250 CHF)
    accounts[iban]["kontostand"] -= 250

    # Saldo nach Gebühr speichern
    saldo_nach_gebuehr = accounts[iban]["kontostand"]

    # Transaktion: Kredit Auszahlung
    tx_kredit = {
        "zeitstempel": timestamp,
        "typ": "kredit_auszahlung",
        "betrag": betrag,
        "saldo_nachher": saldo_nach_kredit,
        "status": "ok"
    }

    # Transaktion: Gebühr
    tx_fee = {
        "zeitstempel": timestamp,
        "typ": "kredit_gebuehr",
        "betrag": -250,
        "saldo_nachher": saldo_nach_gebuehr,
        "status": "ok"
    }

    accounts[iban]["transaktionen"].append(tx_kredit)
    accounts[iban]["transaktionen"].append(tx_fee)

    return accounts, True

# ----------------------------------------------------------
# Berechnet monatliche Kreditzinsen
# ----------------------------------------------------------

def kredit_zinsen_berechnen(accounts, iban, timestamp):

    if iban not in accounts:
        return accounts, 0.0

    restschuld = accounts[iban]["kreditstand"]

    if restschuld <= 0:
        return accounts, 0.0

    # Zinsen: 15% p.a. monatlich, mit exakten Dezimalwerten auf Rappen runden
    zinsen = (
        Decimal(str(restschuld)) * Decimal("0.15") / Decimal("12")
    ).quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN)
    zinsen = float(zinsen)

    # Keine Null-Buchung im Konto-Journal speichern
    if zinsen <= 0:
        return accounts, 0.0

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

    return accounts, zinsen

# ----------------------------------------------------------
# Fuehrt die monatliche Kreditamortisation durch
# ----------------------------------------------------------

def kredit_amortisation(accounts, iban, timestamp):

    # Prüft, ob Konto existiert
    if iban not in accounts:
        return accounts, 0.0, False

    kreditstand = accounts[iban]["kreditstand"]

    # Kein Kredit vorhanden
    if kreditstand <= 0:
        return accounts, 0.0, False

    # Monatliche Tilgung als fester Betrag auf Rappen berechnen
    tilgung = round(accounts[iban]["kreditbetrag"] / 12, 2)

    # Letzte Tilgung darf die Restschuld nicht uebersteigen
    tilgung = min(tilgung, kreditstand)
    
    # Prüft, ob genug Guthaben vorhanden ist
    if accounts[iban]["kontostand"] < tilgung:

        # Konto sperren
        accounts[iban]["status"] = "gesperrt"

        # Zaehler fuer Monate ohne Tilgung erhoehen
        accounts[iban]["monate_ohne_tilgung"] += 1

        # Fehlgeschlagene Amortisation speichern
        tx_fail = {
            "zeitstempel": timestamp,
            "typ": "kredit_amortisation",
            "betrag": -tilgung,
            "saldo_nachher": accounts[iban]["kontostand"],
            "status": "fail"
        }

        accounts[iban]["transaktionen"].append(tx_fail)
        return accounts, 0.0, False

    # Betrag vom Konto abbuchen
    accounts[iban]["kontostand"] -= tilgung

    # Kreditstand reduzieren
    accounts[iban]["kreditstand"] = round(accounts[iban]["kreditstand"] - tilgung, 2)

    # Erfolgreiche Tilgung setzt den Zaehler zurueck
    accounts[iban]["monate_ohne_tilgung"] = 0

    # Erfolgreiche Transaktion speichern
    tx = {
        "zeitstempel": timestamp,
        "typ": "kredit_amortisation",
        "betrag": -tilgung,
        "saldo_nachher": accounts[iban]["kontostand"],
        "status": "ok"
    }

    accounts[iban]["transaktionen"].append(tx)

    return accounts, tilgung, True

# ----------------------------------------------------------
# Berechnet taegliche Strafzinsen bei gesperrtem Konto
# ----------------------------------------------------------

def kredit_strafzins(accounts, iban, timestamp, transaktion_speichern=True):

    # Prüft, ob Konto existiert
    if iban not in accounts:
        return accounts

    # Strafzins nur bei gesperrtem Konto
    if accounts[iban]["status"] != "gesperrt":
        return accounts

    restschuld = accounts[iban]["kreditstand"]

    # Kein Kredit vorhanden
    if restschuld <= 0:
        return accounts

    # Strafzins berechnen (30% p.a. / 365 Tage)
    strafzins = restschuld * (0.30 / 365)

    # Strafzins erhoeht die Restschuld
    accounts[iban]["kreditstand"] += strafzins

    # Transaktion nur speichern, wenn sie im Konto-Journal sichtbar sein soll
    if transaktion_speichern:
        tx = {
            "zeitstempel": timestamp,
            "typ": "strafzins",
            "betrag": strafzins,
            "saldo_nachher": accounts[iban]["kontostand"],
            "status": "ok"
        }

        accounts[iban]["transaktionen"].append(tx)

    return accounts

# ----------------------------------------------------------
# Prueft, ob ein Kredit abgeschrieben werden muss
# ----------------------------------------------------------

def kredit_abschreibung(accounts, iban, bank, timestamp):

    # Prüft, ob Konto existiert
    if iban not in accounts:
        return accounts, bank

    kreditstand = accounts[iban]["kreditstand"]

    # Kein Kredit vorhanden
    if kreditstand <= 0:
        return accounts, bank

    # Abschreibung erst nach 6 Monaten ohne Tilgung
    if accounts[iban]["monate_ohne_tilgung"] < 6:
        return accounts, bank

    # Gesamten Kredit abschreiben
    abgeschrieben = kreditstand

    # Kreditstand auf 0 setzen
    accounts[iban]["kreditstand"] = 0

    # Konto bleibt nach der Abschreibung gesperrt, falls es nicht geschlossen ist
    if accounts[iban]["status"] != "geschlossen":
        accounts[iban]["status"] = "gesperrt"

    # Zaehler zuruecksetzen
    accounts[iban]["monate_ohne_tilgung"] = 0

    # Verlust in der Bank verbuchen
    bank["kredit"] -= abgeschrieben
    bank["einnahmen"] -= abgeschrieben

    # Bankbuchung zaehlen
    bank["anzahl_buchungen"] += 1
    bank["buchungen"].append({
        "zeitstempel": timestamp,
        "vorgang": "kredit_abschreibung",
        "referenz": f"Abschreibung {iban}",
        "soll_konto": "einnahmenkonto",
        "soll_betrag": round(abgeschrieben, 2),
        "haben_konto": "kreditkonto_aktiva",
        "haben_betrag": round(abgeschrieben, 2)
    })

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


# ----------------------------------------------------------
# Fuehrt eine freiwillige Kreditrueckzahlung durch
# ----------------------------------------------------------

def kredit_rueckzahlung(accounts, iban, betrag, timestamp):

    # Prüft, ob Konto existiert
    if iban not in accounts:
        return accounts, 0.0, False
    
    # Geschlossene Konten duerfen keine Rueckzahlung mehr ausfuehren
    if accounts[iban]["status"] == "geschlossen":
        tx_fail = {
            "zeitstempel": timestamp,
            "typ": "kredit_rueckzahlung",
            "betrag": -betrag,
            "saldo_nachher": accounts[iban]["kontostand"],
            "status": "fail",
            "ablehnungsgrund": "Konto ist geschlossen"
        }

        accounts[iban]["transaktionen"].append(tx_fail)
        return accounts, 0.0, False

    # Kein Kredit vorhanden
    if accounts[iban]["kreditstand"] <= 0:
        tx_fail = {
            "zeitstempel": timestamp,
            "typ": "kredit_rueckzahlung",
            "betrag": -betrag,
            "saldo_nachher": accounts[iban]["kontostand"],
            "status": "fail",
            "ablehnungsgrund": "Kein laufender Kredit vorhanden"
        }

        accounts[iban]["transaktionen"].append(tx_fail)
        return accounts, 0.0, False

    # Rückzahlung kann nicht groesser als Restschuld sein
    rueckzahlung = min(betrag, accounts[iban]["kreditstand"])

    # Prüft, ob genügend Guthaben vorhanden ist
    if accounts[iban]["kontostand"] < rueckzahlung:
        tx_fail = {
            "zeitstempel": timestamp,
            "typ": "kredit_rueckzahlung",
            "betrag": -rueckzahlung,
            "saldo_nachher": accounts[iban]["kontostand"],
            "status": "fail",
            "ablehnungsgrund": "Ungenuegendes Guthaben"
        }

        accounts[iban]["transaktionen"].append(tx_fail)
        return accounts, 0.0, False
    

    # Betrag vom Konto abbuchen
    accounts[iban]["kontostand"] -= rueckzahlung

    # Kreditstand reduzieren
    accounts[iban]["kreditstand"] -= rueckzahlung

    # Gesperrtes Konto bei ausreichender Deckung wieder aktiv setzen
    if accounts[iban]["status"] == "gesperrt":
        naechste_tilgung = 0.0

        if accounts[iban]["kreditstand"] > 0:
            naechste_tilgung = accounts[iban]["kreditstand"] / 12

        if accounts[iban]["kontostand"] >= naechste_tilgung:
            accounts[iban]["status"] = "aktiv"

    # Erfolgreiche Rückzahlung setzt Zaehler zurück
    accounts[iban]["monate_ohne_tilgung"] = 0

    tx = {
        "zeitstempel": timestamp,
        "typ": "kredit_rueckzahlung",
        "betrag": -rueckzahlung,
        "saldo_nachher": accounts[iban]["kontostand"],
        "status": "ok"
    }

    accounts[iban]["transaktionen"].append(tx)

    return accounts, rueckzahlung, True
