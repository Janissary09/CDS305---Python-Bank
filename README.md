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
```

Module
engine.py
Hauptprogramm und zentrale Steuerung der Verarbeitung.
Hier werden die Transaktionen geladen, nach Tagen gruppiert und in einer festen Reihenfolge verarbeitet.
konten.py
Logik für Kundenkonten.
Enthält Funktionen für Kontoeröffnung, Einzahlungen, Überweisungen, Datenänderungen, Kontogebühren und Kontoschliessung.
kredit.py
Logik für Kredite.
Enthält Kreditvergabe, Kreditzinsen, Amortisation, Strafzinsen, Rückzahlungen und Abschreibungen.
buchung.py
Verwaltung der internen Bankkonten.
Dieses Modul bildet die buchhalterische Sicht der Bank ab.
speicherung.py
Laden und Speichern der JSON-Dateien.
Dieses Modul übernimmt den Import der Transaktionen sowie das Schreiben der Output-Dateien.
Wichtige Entscheidungen
1. Modulare Struktur

Die Logik wurde auf mehrere Python-Dateien verteilt, damit der Code übersichtlicher und leichter wartbar bleibt.
Dadurch ist klar getrennt, welche Funktionen für Kundenkonten, Kredite, Buchungen und Speicherung zuständig sind.

2. Verarbeitung nach Tagen

Die Transaktionen werden zuerst geladen und anschliessend nach Datum gruppiert.
So können alle Transaktionen eines Tages gemeinsam verarbeitet werden.
Diese Entscheidung vereinfacht insbesondere die periodischen Prozesse wie Zinsen, Kontogebühren und Amortisationen.

3. Trennung zwischen Kundenkonten und internen Bankkonten

Die Kundensicht und die Banksicht wurden bewusst getrennt modelliert.
Kundenkonten speichern Salden, Kreditstände und Transaktionshistorien, während interne Bankkonten die buchhalterische Sicht der Bank abbilden.

4. Periodische Verarbeitung über Zeit-Transaktionen

Zeitabhängige Prozesse wie Kreditzinsen, Strafzinsen, Amortisation und Kontogebühren werden nicht direkt bei normalen Zahlungen ausgelöst, sondern über eigene Zeit-Transaktionen verarbeitet.
Dadurch bleibt der Ablauf kontrollierbar und nachvollziehbar.

5. Interne und externe Überweisungen

Interne Überweisungen zwischen zwei Kundenkonten derselben Bank werden anders behandelt als externe Überweisungen an fremde IBANs.
Diese Unterscheidung ist notwendig, weil externe Überweisungen zusätzlich das Zentralbankkonto beeinflussen.

6. JSON als Ein- und Ausgabeformat

Für die Ein- und Ausgabe wurde JSON verwendet, weil das Format einfach lesbar, leicht testbar und gut für strukturierte Daten geeignet ist.

7. Zusätzliche Zusammenfassung zur Kontrolle

Neben den einzelnen Kontodateien wird auch eine zusammenfassung.json erzeugt.
Diese Datei dient dazu, die Endergebnisse der Simulation schneller zu kontrollieren und mit Referenzdaten zu vergleichen.

Input

Die Eingabedaten liegen im Ordner:

data/input/

Dort befinden sich JSON-Dateien mit Transaktionen.
Jede Transaktion enthält unter anderem einen Typ, einen Zeitstempel, beteiligte IBANs und einen Betrag.

Output

Nach der Verarbeitung werden mehrere Ergebnisdateien im Ordner data/output gespeichert.

data/output/konten/*.json
Für jedes Kundenkonto wird eine eigene JSON-Datei erstellt.
Diese Datei enthält:
die IBAN des Kontos
die Kundendaten
den aktuellen Kontostand
den aktuellen Kreditstand
den Status des Kontos
die vollständige Transaktionshistorie
data/output/bank.json
Diese Datei enthält die Endstände der internen Bankkonten:
Zentralbankkonto
Verpflichtungskonto
Kreditkonto
Einnahmenkonto
data/output/zusammenfassung.json
Diese Datei enthält eine kompakte Zusammenfassung der gesamten Simulation.
Dazu gehören:
Start- und Enddatum der Simulation
Anzahl Kunden
Anzahl geladener Transaktionen
Anzahl erzeugter Buchungen
Endstände aller Kundenkonten in Kurzform
Endstände der internen Bankkonten
Ausführung
Windows
python engine.py
macOS
python3 engine.py
Hinweise
Das Projekt wurde funktional umgesetzt und verwendet keine Klassen.
Die Daten werden über Python-Dictionaries und JSON-Dateien verarbeitet.
Das System besitzt keine grafische Benutzeroberfläche und arbeitet vollständig dateibasiert.
