# 📊 Price Tracker Bot

A Python-based multi-product price tracking tool that collects product data from websites and generates structured CSV and Excel reports.

## 🚀 Features

- Track multiple product URLs
- Extract product name, price, and currency
- Store historical price data (CSV)
- Generate Excel reports with:
  - History sheet
  - Summary sheet
  - Styled headers
  - Color-coded price status
- Detect price changes:
  - Price increase 📈
  - Price drop 📉
  - No change ➖

## 🛠️ Tech Stack

- Python
- Requests
- BeautifulSoup
- Pandas
- OpenPyXL

## 📂 Project Structure

price-tracker-bot/
│
├── app.py
├── parser.py
├── utils.py
├── config.py
├── data/
│ ├── price_history.csv
│ └── price_report.xlsx


## ⚙️ Installation

```bash
pip install -r requirements.txt

▶️ Usage

1. Add product URLs in config.py
2. Run the script: python app.py

📈 Output

CSV file with full history
Excel report with summary and styling

💡 Use Cases

E-commerce price monitoring
Competitor tracking
Market analysis
Automation workflows

📌 Note

This project is designed for educational and automation purposes.
Always respect website terms of service when collecting data.