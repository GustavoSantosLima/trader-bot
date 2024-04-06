# importe o list_report.py
from report import list_report

sum_pnl = 0
sum_cost = 0

for item in list_report:
    symbol = item['symbol']
    pnl = item['Closing PNL']
    transaction_fee = item['Transaction Fee']
    foundin_fee = item['Funding Fee']
    fee_bnb = item['Transaction Fee(BNB)']
    cost_fee = round(transaction_fee + foundin_fee + fee_bnb, 4)

    sum_pnl += pnl
    sum_cost += cost_fee

    #print(f"PNL: {pnl}, Taxax: {cost_fee}")

print(f"TOTAL: \nGanho: {round(sum_pnl, 2)} \nTaxa: {round(sum_cost, 2)} \nSaldo: {round(sum_pnl - abs(sum_cost), 2)}")
