# CDS305 – Python Banking System

This project implements a simplified digital banking system in Python. The system processes transactions from JSON files, manages customer accounts, handles credits, and simulates time-based financial operations.

## 🚀 Features

- Account management (create, update, close)
- Transactions:
  - Deposits
  - Transfers
- Credit system:
  - Credit approval and payout
  - Credit fees
  - Monthly interest calculation (15% p.a.)
  - Linear amortisation (12 months)
- Time simulation:
  - Automatic processing via "Zeit-Transaktion"
- Risk handling:
  - Failed transactions
  - Penalty interest (Strafzins)
  - Credit write-off (Abschreibung)
- Internal bank accounting:
  - Zentralbank
  - Verpflichtung
  - Kreditkonto
  - Einnahmen
- JSON input and output

## 📂 Project Structure

Python Bank/
│
├── engine.py         # Main processing loop
├── konten.py         # Customer account logic
├── kredit.py         # Credit system
├── buchung.py        # Internal bank accounting
├── speicherung.py    # JSON input/output
│
└── data/
    ├── input/        # Transaction files (JSON)
    └── output/       # Generated results (JSON)

## ⚙️ How It Works

1. Transactions are loaded from a JSON file  
2. They are processed chronologically  
3. Each transaction updates:
   - Customer accounts
   - Internal bank accounts  
4. Time-based transactions trigger:
   - Interest calculation
   - Amortisation
   - Penalty interest  
5. Results are stored as JSON files  

## ▶️ Run the Project

```bash
python engine.py

📥 Input Format (Example)

{
  "typ": "einzahlung",
  "zeitstempel": "2026-01-01T10:00:00Z",
  "iban": "CH001",
  "betrag": 500
}

📤 Output
One JSON file per customer account
One JSON file for the bank

Example:
data/output/konten/CH001.json
data/output/bank.json

📌 Notes
The system is implemented without classes (functional programming)
All data structures are based on JSON / Python dictionaries
No UI is used – everything is file-based
👨‍💻 Author

CDS305 Project – Python Banking System
