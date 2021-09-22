import fire
import os
import pandas as pd

from dotenv import find_dotenv, load_dotenv

from src.client import Client
from src.strategy import additional_markets_in_report, strategy

load_dotenv(find_dotenv())


def place_orders(client):
    amount_needed = sum([d['body'].get('amount', 0) + d['body'].get('amountQuote', 0) for d in strategy])
    amount_left = client.get_balance(only_euro=True)[0]['available']
    if float(amount_left) >= amount_needed:
        for entry in strategy:
            client.place_order(entry)

        # check if there are sufficient funds to make next iteration
        if float(amount_left) < 2 * amount_needed:
            print('WARNING: A total of ' + amount_left + ' EUR is in your account, while ' + str(amount_needed) +
                  ' EUR is needed the next time.')
    else:
        print('Not enough funds to place all orders. None were placed.')


def prep_trades(trades):
    trades = pd.DataFrame(trades)
    trades = trades.loc[trades['status'] == 'filled']
    trades['costs'] = round(
        pd.to_numeric(trades['filledAmountQuote'], errors='coerce') +
        pd.to_numeric(trades['feePaid'], errors='coerce'),
        2)
    trades['date'] = pd.to_datetime(trades['updated'], unit='ms')
    trades = trades[['date', 'filledAmount', 'costs', 'feeCurrency']]
    trades = trades.rename(columns={'filledAmount': 'amount', 'feeCurrency': 'currency'})

    return trades


def make_report(client, file_name):
    writer = pd.ExcelWriter(file_name, engine='xlsxwriter')

    # get all markets in strategy and manually added markets
    markets = [d.get('market', '') for d in strategy] + additional_markets_in_report

    totals = []
    workbook = writer.book
    format_euro = workbook.add_format({'num_format': '€ #,##0.00'})
    format_perc = workbook.add_format({'num_format': '0.0%'})

    for market in markets:
        # get all orders
        trades = client.get_orders(market=market)
        trades = prep_trades(trades)
        trades.to_excel(writer, sheet_name=market, engine='xlsxwriter', index=False)
        worksheet = writer.sheets[market]

        price = client.get_ticker_price(market)['price']
        totals += [{'coin': market[:3], 'amount': pd.to_numeric(trades['amount']).sum(),
                    'value': pd.to_numeric(trades['amount']).sum()*float(price), 'deposits': trades['costs'].sum()}]

        for idx, col in enumerate(trades):  # loop through all columns
            series = trades[col]
            max_len = max((
                series.astype(str).map(len).max(),  # len of largest item
                len(str(series.name))  # len of column name/header
            )) + 1  # adding a little extra space
            worksheet.set_column(idx, idx, max_len)

    sheet_total = 'Overview'
    totals = pd.DataFrame(totals)
    totals = totals.append(totals.sum(), ignore_index=True)
    totals['coin'][-1:] = 'Total'
    totals['profit'] = totals['value'] - totals['deposits']
    totals['yield'] = totals['profit'] / totals['deposits']
    totals = totals.round({'amount': 5, 'value': 2, 'deposits': 2, 'yield': 3})
    totals.to_excel(writer, sheet_name=sheet_total, engine='xlsxwriter', index=False)
    worksheet = writer.sheets[sheet_total]
    worksheet.set_column('C:E', cell_format=format_euro)
    worksheet.set_column('F:F', cell_format=format_perc)
    writer.save()


def main():
    # fetch api keys from Bitvavo and set as environment variable
    key = os.environ['BITVAVOKEY']
    secret = os.environ['BITVAVOSECRET']
    client = Client(key, secret)

    # file_name for reporting
    file_name = "portefeuille.xlsx"
    if os.path.exists(file_name):
        try:
            os.remove(file_name)
        except PermissionError:
            print('Portefeuille.xlsx is still open. Close this file first before proceeding.')
            quit()

    # place all orders
    place_orders(client)

    # create reporting
    make_report(client, file_name)


if __name__ == '__main__':
    fire.Fire(main)
