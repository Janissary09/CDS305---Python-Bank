# CDS305 – Python Banking System

## Kurzbeschreibung

Dieses Projekt implementiert ein vereinfachtes Banksystem in Python.  
Die Software verarbeitet Transaktionen aus JSON-Dateien, verwaltet Kundenkonten, bearbeitet Kredite und führt periodische Bankprozesse wie Zinsen, Amortisationen und Kontogebühren aus.

Das Ziel des Projekts ist es, die Verarbeitung von Banktransaktionen sowie die internen Buchungen einer Bank in einer klaren und modularen Form zu simulieren.

---

## Architektur

Die Anwendung ist in mehrere Module aufgeteilt, damit die einzelnen Aufgaben klar getrennt bleiben.

```text
Python Bank/
├── engine.py
├── konten.py
├── kredit.py
├── buchung.py
├── speicherung.py
└── data/
    ├── input/
    └── output/
        ├── konten/
        ├── bank.json
        └── zusammenfassung.json
