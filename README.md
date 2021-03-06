# PortfolioTracker

v0.1-beta

I had been looking for a nice way to aggregate and track my crypto portfolios over multiple sites, but everything I found I thought charged too much, didn't offer the metrics I was looking for, and I wasn't thrilled about the idea of putting data into what is essentially a black box.  I'm fairly new to python so I'm sure there are a better ways of doing things. 

<img width="1503" alt="Screen Shot 2021-09-24 at 8 51 05 AM" src="https://user-images.githubusercontent.com/89819081/134685696-d2162887-9a5f-467b-9975-dde0281d941b.png">

## Supports

### Importing Transactions

#### APIs:
- Binance.US
- Celsius
- Coinbase
- Coinbase Pro
- Gemini

#### Upload Transaction Summaries
- BlockFi
- Coinbase Pro
- Crypto.com
- Gemini
- Gemini Earn
- Ledn: Bitcoin
- Uphold

#### Manually Adding Transactions
Supports manually adding buys, sells, trades/swaps, interest, and fees

### Exporting Transactions
Export detailed or summarized transaction histories

## How to:
- Getting this to work should be pretty straightforward. Linux/macOS instructions below. (Windows should be similar)
- Need to have python 3 installed: https://www.python.org/downloads/
1. Download entire `PortfolioTracker` folder
2. Open terminal
3. Within the terminal, navigate to where you have everything stored: `cd path/to/PortfolioTracker`
4. Type the following: `mkdir summaries temp jsonUser` to create 3 folders with those names.
5. Run the script: `python3 main.py`
6. If you need to install a package you'll get an error saying which package needs to be installed. To install type: `pip3 [package name]`
7. You might need to restart the app after you add your first transaction.
8. Updating the current prices is done in the File menu. 

## Issues/Comments:
- I'm sure this is pretty buggy as I only have access to my own transactions to troublshoot. If you sell or trade crypto I'd greatly appreciate knowing how those are coded for the various exchanges in their transaction histories. 

## Things I'd like to add:
- Support for currencies other than USD
- Abilty to sync wallets
- More exchanges
- Graphs

## Want to support the project?

Not expected, but certainly appreciated.

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/10dollarbanana)

Or consider donating some crypto:

### Bitcoin: 
<img width="292" alt="Bitcoin" src="https://user-images.githubusercontent.com/89819081/134095057-8dd9867f-0210-4889-bfb6-60040aa405cd.png">
- Address: 1q9ndvpdx2272mmstt4hhtq07mlr5mlrxfznhhzx

### Ethereum:
<img width="300" alt="Ethereum" src="https://user-images.githubusercontent.com/89819081/134095136-301f957a-6dc2-4c4b-a6de-ea7df1f5eb01.png">
- Address: 0x7A3f21ba4292B019534dc73951592f9E25390064

### Litecoin:
<img width="291" alt="Screen Shot 2021-09-23 at 2 32 04 PM" src="https://user-images.githubusercontent.com/89819081/134572014-2ce299fc-92b5-45f7-bd27-8ab9a743c4ba.png">
- Address: LQt29xnfGzQiYAyy8Qv9oXXmC558QUcXa4
