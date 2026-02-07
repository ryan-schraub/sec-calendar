import requests
import pandas as pd
import time
from datetime import datetime

# Tell the SEC who you are
headers = {'User-Agent': 'Ryan (ryan.schraub@gmail.com)'}

def get_data():
    # 1. Get the list of all companies
    ticker_url = "https://www.sec.gov/files/company_tickers.json"
    mapping = requests.get(ticker_url, headers=headers).json()
    
    # Let's do the first 500 for now
    tickers_list = [(v['ticker'], str(v['cik_str']).zfill(10)) for k, v in mapping.items()][:500]
    
    results = []
    for ticker, cik in tickers_list:
        try:
            # 2. Get the specific company's filings
            url = f"https://data.sec.gov/submissions/CIK{cik}.json"
            data = requests.get(url, headers=headers).json()
            
            # Default "Guess" (Legal Deadline)
            status = data.get('category', '')
            deadline = "2026-03-02" if "Large Accelerated" in status else "2026-03-31"
            label = "⚖️ Legal Limit"
            
            # 3. Check for a "Confirmed" date in recent 8-Ks
            recent = data['filings']['recent']
            for i in range(min(5, len(recent['form']))):
                if recent['form'][i] == '8-K' and '2.02' in str(recent.get('items', [""]*5)[i]):
                    deadline = recent['filingDate'][i]
                    label = "🎯 Confirmed (8-K)"
                    break
            
            results.append({"Ticker": ticker, "Date": deadline, "Source": label})
            time.sleep(0.12) # Don't go too fast!
        except:
            continue
    
    # 4. Save to a CSV file
    pd.DataFrame(results).to_csv("calendar.csv", index=False)

if __name__ == "__main__":
    get_data()
