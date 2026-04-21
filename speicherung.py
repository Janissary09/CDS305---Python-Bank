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
# Speichert alle Kundenkonten als einzelne JSON-Dateien
# ----------------------------------------------------------

def speichere_konten(accounts, ordner):

    # Ordner erstellen, falls nicht vorhanden
    os.makedirs(ordner, exist_ok=True)

    for iban, konto in accounts.items():
        dateipfad = os.path.join(ordner, f"{iban}.json")

        with open(dateipfad, "w", encoding="utf-8") as f:
            json.dump(konto, f, indent=4)


# ----------------------------------------------------------
# Speichert die Bankdaten als JSON-Datei
# ----------------------------------------------------------

def speichere_bank(bank, dateipfad):

    with open(dateipfad, "w", encoding="utf-8") as f:
        json.dump(bank, f, indent=4)