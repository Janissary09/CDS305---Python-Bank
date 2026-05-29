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

### Module

- **`engine.py`**  
  Hauptprogramm und zentrale Steuerung der Verarbeitung.  
  Hier werden die Transaktionen geladen, nach Tagen gruppiert und in einer festen Reihenfolge verarbeitet.

- **`konten.py`**  
  Enthält die Funktionen für die Kundenkonten.  
  Dazu gehören Kontoeröffnung, Einzahlungen, Überweisungen, Datenänderungen, Kontogebühren und Kontoschliessung.

- **`kredit.py`**  
  Enthält die Kreditlogik.  
  Dazu gehören Kreditvergabe, Kreditzinsen, Amortisation, Strafzinsen, Rückzahlungen und Abschreibungen.

- **`buchung.py`**  
  Enthält die internen Buchungen der Bank.  
  In diesem Modul werden die Auswirkungen der Transaktionen auf die internen Bankkonten verarbeitet.

- **`speicherung.py`**  
  Zuständig für das Laden und Speichern der JSON-Dateien.  
  Dieses Modul übernimmt den Import der Eingabedaten und das Schreiben der Ergebnisdateien.

---

## Wichtige Entscheidungen

### 1. Aufteilung in mehrere Module
Der Code wurde nicht in einer einzigen Datei geschrieben, sondern auf mehrere Module verteilt.  
Dadurch bleibt die Struktur übersichtlicher und die einzelnen Aufgaben sind klar getrennt.

### 2. Verarbeitung nach Tagen
Die geladenen Transaktionen werden zuerst nach Datum gruppiert.  
So können alle Transaktionen eines Tages gemeinsam verarbeitet werden.  
Das ist besonders hilfreich für periodische Prozesse wie Zinsen, Amortisationen und Kontogebühren.

### 3. Trennung von Kundenkonten und Bankkonten
Kundenkonten und interne Bankkonten werden getrennt behandelt.  
Dadurch bleibt die Kundensicht von der buchhalterischen Sicht der Bank getrennt und die Bilanz kann einfacher kontrolliert werden.

### 4. Verwendung von Zeit-Transaktionen
Periodische Prozesse werden über eigene Zeit-Transaktionen ausgelöst.  
Dadurch können monatliche oder quartalsweise Abläufe gezielt und nachvollziehbar verarbeitet werden.

### 5. Unterscheidung zwischen internen und externen Überweisungen
Überweisungen innerhalb der Bank und Überweisungen an externe IBANs werden unterschiedlich behandelt.  
Diese Entscheidung war notwendig, weil externe Überweisungen zusätzlich die internen Bankkonten beeinflussen.

### 6. JSON als Ein- und Ausgabeformat
Für die Ein- und Ausgabedaten wurde JSON verwendet.  
Dieses Format ist einfach lesbar, gut testbar und für die Simulation strukturierter Transaktionen geeignet.

### 7. Zusätzliche Zusammenfassung der Ergebnisse
Neben den einzelnen Kontodateien wird auch eine `zusammenfassung.json` erstellt.  
Dadurch können die Endergebnisse der Simulation schneller überprüft und einfacher mit Referenzdaten verglichen werden.

---

## Input

Die Eingabedaten liegen im Ordner:

```text
data/input/
