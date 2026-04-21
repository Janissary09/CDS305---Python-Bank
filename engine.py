# engine.py

from konten import konto_eroeffnen, einzahlung, ueberweisung
from speicherung import lade_transaktionen, speichere_konten, speichere_bank
from buchung import buche_einzahlung, buche_ueberweisung
from kredit import kredit_vergeben, kredit_zinsen_berechnen, kredit_amortisation, kredit_strafzins, kredit_abschreibung

def main():
    print("Bank system starting...")

    # ----------------------------------------------------------
    # Initialisierung
    # ----------------------------------------------------------

    # Kundenkonten
    accounts = {}

    # Interne Bankkonten
    bank = {
        "zentralbank": 0.0,
        "verpflichtung": 0.0,
        "kredit": 0.0,
        "einnahmen": 0.0
    }

    # ----------------------------------------------------------
    # Transaktionen laden
    # ----------------------------------------------------------

    transactions = lade_transaktionen("data/input/test.json")

    # ----------------------------------------------------------
    # Transaktionen nach Zeit sortieren
    # ----------------------------------------------------------

    transactions.sort(key=lambda x: x["zeitstempel"])

    # ----------------------------------------------------------
    # Transaktionen verarbeiten (Engine)
    # ----------------------------------------------------------

    for tx in transactions:

        typ = tx["typ"]
        timestamp = tx["zeitstempel"]

        # Konto eröffnen
        if typ == "konto_eroeffnen":
            accounts = konto_eroeffnen(accounts, tx["kunde"])

        # Einzahlung
        elif typ == "einzahlung":
            accounts = einzahlung(
                accounts,
                tx["ziel_iban"],
                tx["betrag"],
                timestamp
            )

            bank = buche_einzahlung(bank, tx["betrag"])

        # Überweisung
        elif typ == "ueberweisung":
            accounts = ueberweisung(
                accounts,
                tx["von_iban"],
                tx["nach_iban"],
                tx["betrag"],
                timestamp
            )

            bank = buche_ueberweisung(bank, tx["betrag"])
        
        elif typ == "kredit_antrag":
            accounts = kredit_vergeben(
                accounts,
                tx["kunden_iban"],
                tx["betrag"],
                timestamp
            )

        # ----------------------------------------------------------
        # Zeit-Transaktion (periodische Berechnungen)
        # ----------------------------------------------------------

        elif typ == "zeit":

            for iban in accounts:

                # Zinsen
                accounts = kredit_zinsen_berechnen(accounts, iban, timestamp)

                # Amortisation
                accounts = kredit_amortisation(accounts, iban, timestamp)

                # Strafzins (neu)
                accounts = kredit_strafzins(accounts, iban, timestamp)

                # Abschreibung prüfen
                accounts, bank = kredit_abschreibung(accounts, iban, bank, timestamp)

        else:
            print(f"Unbekannter Transaktionstyp: {typ}")
            

    # ----------------------------------------------------------
    # Ausgabe
    # ----------------------------------------------------------

    print(accounts)
    print(bank)

    # ----------------------------------------------------------
    # Output speichern
    # ----------------------------------------------------------

    speichere_konten(accounts, "data/output/konten")
    speichere_bank(bank, "data/output/bank.json")


if __name__ == "__main__":
    main()