<p align="center">
  <img align="center" width="350" src="https://github.com/user-attachments/assets/779356f9-84af-4247-83f0-32be2229c569" />

  <h1 align="center">TonViewer</h1>
  <h3 align="center"></h3>
</p>


<p align="center">

<a href="https://pypi.org/project/Tonviewer/">
    <img src="https://img.shields.io/pypi/v/Tonviewer?color=red&logo=pypi&logoColor=red">
  </a>

  <a href="https://t.me/Pycodz">
    <img src="https://img.shields.io/badge/Telegram-Channel-blue.svg?logo=telegram">
  </a>
  
  <a href="https://t.me/DevZ44d" target="_blank">
    <img alt="Telegram Owner" src="https://img.shields.io/badge/Telegram-Owner-red.svg?logo=telegram" />
  </a>
</p>

#### 🚀 Quick Start
```python
## Prints TON and USDT balance of wallet
from Tonviewer import Wallet , Coin
wallet = Wallet("")    #wallet_address_here
wallet.balance()
wallet.transactions(limit=3)    #limit Parameter : int , get transactions of Wallet default = 1

# Prints live price
coin = Coin("")   #ex: "toncoin" , "bitcoin" , ...
coin.price()    # Prints live price
coin.about()    # Prints description of the coin
```

### Installation and Development 🚀

### Via PyPi ⚡️
```shell
# via PyPi
pip install Tonviewer -U
```

### 💎 TON Crypto Info Scraper

- TON Crypto Info Scraper is a Python library that allows you to fetch real-time data from the TON blockchain and CoinGecko without needing any APIs.

- It enables users to view wallet **balances** and **live coin information** and get **transactions** of Wallet with ease, making it perfect for TON developers, analysts, and bot creators.


### ⚙️ What This Library Can Do ?

- Retrieve the current **TON and USDT balance** from any TON wallet address.
- Get the **live price** of any coin listed on CoinGecko.
- get **transactions** of Wallet .

### Example response of transactions ,
```json
{
"Time":"1 Aug, 12:31",
"Action":"Sent TON",
"to": "Fragment · Telegram Stars",
"Paid For":"50 Telegram Stars ",
"ton":"− 0.2171 TON",
"limit ":"1"
}
```

### ✨ Features

- Real-time TON wallet balance fetching
- Live cryptocurrency price lookup
- Instant coin description extraction
- Fast and lightweight scraping
- get **transactions** of Wallet
- No API keys or authentication needed



### 💡 Why Use This?
- ✅ No API rate limits .

- ✅ No API keys .

- ✅ Fully customizable .

- ✅ Great for bots, dashboards, or automation .


### 🧠 Author's Note
- This tool was crafted with **[deep](https://t.me/ddllId)** for developers in the TON ecosystem who want a fast and API-free way to monitor wallets and market data.

- New Features coming soon .
- 
## 💬 Help & Support .
- Follow updates via the **[Telegram Channel](https://t.me/Pycodz)**.
- For general questions and help, join our **[Telegram chat](https://t.me/PyChTz)**.


