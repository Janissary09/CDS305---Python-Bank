# engine.py


from buchung import (
    buche_einzahlung,
    buche_ueberweisung,
    buche_kredit_auszahlung,
    buche_einnahme,
    buche_kontogebuehr,
    buche_kredittilgung,
    buche_strafzins,
    pruefe_bilanz,
)

from konten import (
    konto_eroeffnen,
    einzahlung,
    ueberweisung,
    kontogebuehr_belasten,
    kunden_daten_aendern,
    konto_schliessen,
)

from kredit import (
    kredit_vergeben,
    kredit_zinsen_berechnen,
    kredit_amortisation,
    kredit_strafzins,
    kredit_abschreibung,
    kredit_rueckzahlung,
)

from speicherung import (
    lade_transaktionen,
    lade_transaktionen_aus_ordner,
    speichere_konten,
    speichere_bank,
    speichere_zusammenfassung,
)



def main():
    print("Bank system starting...")

    # ----------------------------------------------------------
    # Initialisierung
    # ----------------------------------------------------------

    # Kundenkonten
    accounts = {}

    # Naechste Kontonummer fuer die IBAN-Generierung
    naechste_nummer = 1

    # Interne Bankkonten
    bank = {
        "zentralbank": 0.0,
        "verpflichtung": 0.0,
        "kredit": 0.0,
        "einnahmen": 0.0,
        "anzahl_buchungen": 0,
        "buchungen": []
    }

    # ----------------------------------------------------------
    # Transaktionen laden
    # ----------------------------------------------------------

    transactions = lade_transaktionen_aus_ordner("data/input")
    
    # ----------------------------------------------------------
    # Transaktionen nach Tag gruppieren
    # ----------------------------------------------------------

    tage = {}

    for tx in transactions:
        datum = tx["zeitstempel"][:10]

        if datum not in tage:
            tage[datum] = []

        tage[datum].append(tx)

    # Letzter verarbeiteter Periodenmonat
    letzter_periodenmonat = None

    # Tage chronologisch verarbeiten
    for datum in sorted(tage.keys()):

        tages_transaktionen = tage[datum]

        # ----------------------------------------------------------
        # 1. Kontoeroeffnungen
        # ----------------------------------------------------------

        for tx in tages_transaktionen:
            if tx["typ"] == "konto_eroeffnen":
                accounts, neue_iban, naechste_nummer = konto_eroeffnen(
                    accounts,
                    tx["kunde"],
                    naechste_nummer,
                    tx["zeitstempel"]
                )

        # ----------------------------------------------------------
        # 2. Einzahlungen
        # ----------------------------------------------------------

        for tx in tages_transaktionen:
            if tx["typ"] == "ueberweisung_ein":
                accounts, nachzahlung = einzahlung(
                    accounts,
                    tx["ziel_iban"],
                    tx["betrag"],
                    tx["zeitstempel"]
                )

                bank = buche_einzahlung(bank, tx["betrag"], tx["zeitstempel"], tx.get("referenz", ""))

                if nachzahlung > 0:
                    bank = buche_kredittilgung(
                        bank,
                        nachzahlung,
                        tx["zeitstempel"],
                        "kredit_rueckzahlung",
                        f"Nachzahlung {tx['ziel_iban']}"
                    )

        # ----------------------------------------------------------
        # 3. Zeit-Transaktion / periodische Verarbeitung
        # ----------------------------------------------------------

        for tx in tages_transaktionen:
            if tx["typ"] == "zeit":
                
                aktueller_monat = tx["zeitstempel"][:7]
                ist_monatsanfang = aktueller_monat != letzter_periodenmonat

                for iban in accounts:

                    # Geschlossene Konten werden nicht mehr periodisch verarbeitet
                    if accounts[iban]["status"] == "geschlossen":
                        continue

                    amortisation_fehlgeschlagen = False
                    
                    # Monatliche Kreditzinsen nur am Monatsanfang
                    if ist_monatsanfang:
                        accounts, zinsbetrag = kredit_zinsen_berechnen(accounts, iban, tx["zeitstempel"])

                        if zinsbetrag > 0:
                            bank = buche_einnahme(
                                bank,
                                zinsbetrag,
                                tx["zeitstempel"],
                                "kredit_zinsen",
                                f"Kreditzinsen {iban}"
                            )

                    # Quartalsweise Kontogebuehr nur am Quartalsanfang
                    # und nicht im Eroeffnungsmonat
                    if (
                        tx["zeitstempel"][5:7] in ["01", "04", "07", "10"]
                        and tx["zeitstempel"][8:10] == "01"
                        and accounts[iban]["eroeffnungsdatum"][:7] != tx["zeitstempel"][:7]
                    ):
                        accounts = kontogebuehr_belasten(accounts, iban, tx["zeitstempel"])
                        bank = buche_kontogebuehr(
                            bank,
                            25.0,
                            tx["zeitstempel"],
                            f"Kontogebuehr Q {iban}"
                        )

                    # Monatliche Amortisation nur am Monatsanfang
                    if ist_monatsanfang:
                        accounts, tilgung, erfolg = kredit_amortisation(accounts, iban, tx["zeitstempel"])

                        if erfolg:
                            bank = buche_kredittilgung(
                                bank,
                                tilgung,
                                tx["zeitstempel"],
                                "kredit_amortisation",
                                f"Amortisation {iban}"
                            )
                        else:
                            amortisation_fehlgeschlagen = tilgung == 0.0 and accounts[iban]["status"] == "gesperrt"
                    
                    # Strafzinsen berechnen und im Banksystem verbuchen
                    # Direkt nach fehlgeschlagener Amortisation nicht im Konto-Journal speichern.
                    abschreibung_faellig = (
                        ist_monatsanfang
                        and accounts[iban]["kreditstand"] > 0
                        and accounts[iban]["monate_ohne_tilgung"] >= 6
                    )

                    if not abschreibung_faellig:
                        vorher = accounts[iban]["kreditstand"]
                        accounts = kredit_strafzins(
                            accounts,
                            iban,
                            tx["zeitstempel"],
                            transaktion_speichern=not amortisation_fehlgeschlagen
                        )
                        nachher = accounts[iban]["kreditstand"]

                        strafzins_betrag = nachher - vorher

                        if strafzins_betrag > 0:
                            bank = buche_strafzins(
                                bank,
                                strafzins_betrag,
                                tx["zeitstempel"],
                                f"Strafzinsen {iban}"
                            )
                    
                    # Abschreibung nur am Monatsanfang pruefen
                    if ist_monatsanfang:
                        accounts, bank = kredit_abschreibung(accounts, iban, bank, tx["zeitstempel"])

                letzter_periodenmonat = aktueller_monat

        # ----------------------------------------------------------
        # 4. Kreditantraege
        # ----------------------------------------------------------

        for tx in tages_transaktionen:
            if tx["typ"] == "kredit_antrag":
                accounts, erfolg = kredit_vergeben(
                    accounts,
                    tx["kunden_iban"],
                    tx["betrag"],
                    tx["zeitstempel"]
                )

                if erfolg:
                    bank = buche_kredit_auszahlung(
                        bank,
                        tx["betrag"],
                        tx["zeitstempel"],
                        f"Kredit {tx['kunden_iban']}"
                    )
                    bank = buche_einnahme(
                        bank,
                        250,
                        tx["zeitstempel"],
                        "kredit_gebuehr",
                        f"Kreditgebuehr {tx['kunden_iban']}"
                    )

        # ----------------------------------------------------------
        # 5a. Freiwillige Kreditrueckzahlung
        # ----------------------------------------------------------

        for tx in tages_transaktionen:
            if tx["typ"] == "kredit_rueckzahlung":
                accounts, rueckzahlung, erfolg = kredit_rueckzahlung(
                    accounts,
                    tx["kunden_iban"],
                    tx["betrag"],
                    tx["zeitstempel"]
                )

                if erfolg:
                    bank = buche_kredittilgung(
                        bank,
                        rueckzahlung,
                        tx["zeitstempel"],
                        "kredit_rueckzahlung",
                        f"Rueckzahlung {tx['kunden_iban']}"
                    )
        
        # ----------------------------------------------------------
        # 5b. Kundendaten aendern
        # ----------------------------------------------------------

        for tx in tages_transaktionen:
            if tx["typ"] == "daten_aendern":
                accounts, erfolg = kunden_daten_aendern(
                    accounts,
                    tx["kunden_iban"],
                    tx["neue_daten"],
                    tx["zeitstempel"]
                )
        
        # ----------------------------------------------------------
        # 5c. Konto schliessen
        # ----------------------------------------------------------

        for tx in tages_transaktionen:
            if tx["typ"] == "konto_schliessen":
                accounts, erfolg = konto_schliessen(
                    accounts,
                    tx["kunden_iban"],
                    tx["zeitstempel"]
                )

        # ----------------------------------------------------------
        # 6. Ausgehende Ueberweisungen
        # ----------------------------------------------------------

        for tx in tages_transaktionen:
            if tx["typ"] == "ueberweisung_aus":
                accounts, erfolg = ueberweisung(
                    accounts,
                    tx["quell_iban"],
                    tx["ziel_iban"],
                    tx["betrag"],
                    tx["zeitstempel"]
                )

                if erfolg:
                    interne_ueberweisung = tx["ziel_iban"] in accounts
                    bank = buche_ueberweisung(
                        bank,
                        tx["betrag"],
                        interne_ueberweisung,
                        tx["zeitstempel"],
                        tx.get("referenz", "")
                    )

            

    # ----------------------------------------------------------
    # Ausgabe
    # ----------------------------------------------------------

    print("Verarbeitung abgeschlossen.")
    print(f"Anzahl Konten: {len(accounts)}")
    print("Bankkonten wurden aktualisiert.")

    # ----------------------------------------------------------
    # Bilanz pruefen
    # ----------------------------------------------------------

    if not pruefe_bilanz(bank):
        print("Warnung: Bilanz ist nicht ausgeglichen!")

    # ----------------------------------------------------------
    # Output speichern
    # ----------------------------------------------------------

    speichere_konten(accounts, "data/output/konten")
    speichere_bank(bank, "data/output/bank.json")
    speichere_zusammenfassung(
        accounts,
        bank,
        "data/input",
        "data/output/zusammenfassung.json"
    )


if __name__ == "__main__":
    main()
