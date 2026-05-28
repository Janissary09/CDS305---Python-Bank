# speicherung.py

import json
import os


# ----------------------------------------------------------
# Liest Transaktionen aus einer JSON-Datei ein
# ----------------------------------------------------------

def lade_transaktionen(dateipfad):

    with open(dateipfad, "r", encoding="utf-8") as f:
        daten = json.load(f)

    return daten


# ----------------------------------------------------------
# Liest alle monatlichen Transaktionsdateien aus einem Ordner ein
# ----------------------------------------------------------

def lade_transaktionen_aus_ordner(ordnerpfad):

    alle_transaktionen = []

    # Alle JSON-Dateien im Ordner sortiert einlesen
    for dateiname in sorted(os.listdir(ordnerpfad)):
        dateipfad = os.path.join(ordnerpfad, dateiname)

        if os.path.isfile(dateipfad) and dateiname.endswith(".json"):
            with open(dateipfad, "r", encoding="utf-8") as f:
                daten = json.load(f)

            alle_transaktionen.extend(daten)

    return alle_transaktionen


# ----------------------------------------------------------
# Speichert alle Kundenkonten als einzelne JSON-Dateien
# ----------------------------------------------------------

def speichere_konten(accounts, ordner):

    # Ordner erstellen, falls nicht vorhanden
    os.makedirs(ordner, exist_ok=True)

    # Alte Kontodateien entfernen, damit keine IBAN-Dateien im Output bleiben
    for dateiname in os.listdir(ordner):
        if dateiname.endswith(".json"):
            os.remove(os.path.join(ordner, dateiname))

    for iban, konto in accounts.items():
        kundenname = konto["kunde"]["name"].replace(" ", "_")
        dateipfad = os.path.join(ordner, f"{kundenname}.json")

        with open(dateipfad, "w", encoding="utf-8") as f:
            json.dump(konto, f, indent=4, ensure_ascii=False)


# ----------------------------------------------------------
# Speichert die Bankdaten als JSON-Datei
# ----------------------------------------------------------

def speichere_bank(bank, dateipfad):

    bank_ausgabe = {
        "zentralbankkonto": round(bank["zentralbank"], 2),
        "verpflichtungskonto": round(bank["verpflichtung"], 2),
        "kreditkonto_aktiva": round(bank["kredit"], 2),
        "einnahmenkonto": round(bank["einnahmen"], 2),
        "buchungen": bank["buchungen"]
    }

    with open(dateipfad, "w", encoding="utf-8") as f:
        json.dump(bank_ausgabe, f, indent=4, ensure_ascii=False)


# ----------------------------------------------------------
# Speichert eine Zusammenfassung der Simulation
# ----------------------------------------------------------

def speichere_zusammenfassung(accounts, bank, input_pfad, output_datei):
    alle_dateien = sorted(
        [datei for datei in os.listdir(input_pfad) if datei.endswith(".json")]
    )

    simulation_start = ""
    simulation_end = ""
    anzahl_transaktionen = 0

    if alle_dateien:
        erste_datei = os.path.join(input_pfad, alle_dateien[0])
        letzte_datei = os.path.join(input_pfad, alle_dateien[-1])

        with open(erste_datei, "r", encoding="utf-8") as file:
            erste_transaktionen = json.load(file)
            if erste_transaktionen:
                simulation_start = erste_transaktionen[0]["zeitstempel"][:10]

        with open(letzte_datei, "r", encoding="utf-8") as file:
            letzte_transaktionen = json.load(file)
            if letzte_transaktionen:
                simulation_end = letzte_transaktionen[-1]["zeitstempel"][:10]

        for datei in alle_dateien:
            pfad = os.path.join(input_pfad, datei)
            with open(pfad, "r", encoding="utf-8") as file:
                transaktionen = json.load(file)
                anzahl_transaktionen += len(transaktionen)

    zusammenfassung = {
        "simulation_start": simulation_start,
        "simulation_end": simulation_end,
        "anzahl_kunden": len(accounts),
        "anzahl_transaktionen": anzahl_transaktionen,
        "anzahl_buchungen": bank["anzahl_buchungen"],
        "kontostande": {},
        "bankkonten": {
            "zentralbankkonto": round(bank["zentralbank"], 2),
            "verpflichtungskonto": round(bank["verpflichtung"], 2),
            "kreditkonto_aktiva": round(bank["kredit"], 2),
            "einnahmenkonto": round(bank["einnahmen"], 2)
        }
    }

    for iban, konto in accounts.items():
        zusammenfassung["kontostande"][iban] = {
            "name": konto["kunde"]["name"],
            "kontostand": round(konto["kontostand"], 2),
            "kredit_stand": round(konto["kreditstand"], 2),
            "status": konto["status"],
            "anzahl_transaktionen": len(konto["transaktionen"])
        }

    with open(output_datei, "w", encoding="utf-8") as file:
        json.dump(zusammenfassung, file, ensure_ascii=False, indent=2)
