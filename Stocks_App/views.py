from django.shortcuts import render
from .models import Transactions, Investor, Buying
from django.db import connection
from datetime import datetime

def dictfetchall(cursor):
    # Returns all rows from a cursor as a dict '''
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

def index(request):
    return render(request, 'index.html')

def Query_Results(request):
    '''
    This function is used to display the results of the queries in the Query_Results.html page.
    :param request:
    :return: Query_Results.html page with the results of the queries.
    '''

    with connection.cursor() as cursor:
        cursor.execute("""SELECT DISTINCT I.Name, SOB.TotalSum
                          FROM DiversifiedInvestor DI, SumOfBuying SOB, Investor I
                          WHERE DI.ID = SOB.ID  AND DI.ID = I.ID
                          ORDER BY SOB.TotalSum DESC;
                          """)
        sql_res = dictfetchall(cursor)

        cursor.execute("""SELECT B.Symbol, I.Name, CompanyMaxBQ.MaxCompanyBQ AS Quantity
                          FROM Buying B, PopularCompany PC, Investor I, CompanyMaxBQ
                          WHERE B.Symbol = PC.Symbol AND I.ID = B.ID
                          AND B.ID = CompanyMaxBQ.ID AND B.Symbol = CompanyMaxBQ.Symbol
                          GROUP BY B.Symbol, I.Name, CompanyMaxBQ.MaxCompanyBQ
                          ORDER BY B.Symbol ASC, I.Name ASC;
                          """)
        sql_res2 = dictfetchall(cursor)

        cursor.execute("""SELECT PC.Symbol, COUNT(B.Symbol) AS TotalBuyers
                          FROM ProfitableCompany PC LEFT OUTER JOIN Buying B
                          ON PC.Symbol = B.Symbol AND PC.tDate = B.tDate
                          GROUP BY PC.Symbol
                          ORDER BY PC.Symbol ASC;
                          """)
        sql_res3 = dictfetchall(cursor)

    return render(request, 'Query_Results.html',
                  {'sql_res': sql_res, 'sql_res2': sql_res2, 'sql_res3': sql_res3})

def Add_Transaction(request):
    '''
    This function is used to add a new transaction to the Transactions table.
    :param request:
    :return: Add_Transaction.html page with the results of the queries.
    '''

    first_try = 0
    is_ID = 0
    is_not_Tran = 0

    with connection.cursor() as cursor:
        cursor.execute("""SELECT TOP 10 *
                          FROM Transactions
                          ORDER BY tDate DESC, ID DESC;
                          """)
        sql_res4 = dictfetchall(cursor)

    if request.method == 'POST' and request.POST:
        first_try = 1
        new_id = request.POST["ID"]

        with connection.cursor() as cursor:
            cursor.execute("""SELECT ID
                              FROM Investor
                              WHERE ID = %s
                              GROUP BY ID;
                              """, [new_id])
            row = cursor.fetchone()
            if not row: # ID not exists
                return render(request, 'Add_Transaction.html', {'sql_res4': sql_res4,
                                                                'first_try': first_try, 'is_ID': is_ID,
                                                                'new_id': new_id})
            else:
                is_ID = 1
                with connection.cursor() as cursor:
                    cursor.execute("""SELECT T.ID
                                      FROM Transactions T ,(SELECT MAX(tDate) AS MaxDay
                                                            FROM Stock) LastDay
                                      WHERE T.ID = %s AND T.tDate = LastDay.MaxDay
                                      GROUP BY T.ID;
                                      """, [new_id])
                    row = cursor.fetchone()
                    if row: # Transaction exists at the last day at stock table
                        return render(request, 'Add_Transaction.html',
                                      {'sql_res4': sql_res4,
                                       'first_try': first_try,
                                       'is_ID': is_ID,
                                       'is_not_Tran': is_not_Tran})

                    else:
                        is_not_Tran = 1
                        new_amount = int(request.POST["Transaction"])
                        with connection.cursor() as cursor:
                            cursor.execute("""SELECT MAX(tDate) AS MaxDay
                                              FROM Stock;
                                              """)
                            today = dictfetchall(cursor)
                            today = today[:1]
                        today = today[0]['MaxDay'].strftime('%Y-%m-%d')

                        with connection.cursor() as cursor:
                            cursor.execute("""
                                INSERT INTO Transactions
                                VALUES (%s, %s, %s);
                                """, [today, new_id, new_amount])

                        with connection.cursor() as cursor:
                            cursor.execute("""
                                UPDATE Investor
                                SET Amount = Amount + %s
                                WHERE ID = %s;
                                """, [new_amount, new_id])

                        with connection.cursor() as cursor:
                            cursor.execute("""SELECT TOP 10 *
                            FROM Transactions
                            ORDER BY tDate DESC, ID DESC;
                            """)
                            sql_res4 = dictfetchall(cursor)

                        return render(request, 'Add_Transaction.html',
                                                      {'sql_res4': sql_res4,
                                                             'first_try' : first_try,
                                                             'is_ID' : is_ID,
                                                             'is_not_Tran' : is_not_Tran})

    return render(request, 'Add_Transaction.html', {'sql_res4': sql_res4,
                                                                       'first_try': first_try})

def Buy_Stocks(request):
    '''
    This function is used to add a new buying to the Buying table.
    :param request:
    :return: Buy_Stocks.html page with the results of the queries.
    '''
    first_try = 0
    is_ID = 0
    is_symbol = 0
    is_large = 0
    is_not_Buy = 0

    with connection.cursor() as cursor:
        cursor.execute("""SELECT TOP 10 *
                          FROM Buying
                          ORDER BY tDate DESC, ID DESC, Symbol ASC;
                          """)
        sql_res5 = dictfetchall(cursor)

    if request.method == 'POST' and request.POST:
        first_try = 1
        new_id = request.POST["ID"]

        with connection.cursor() as cursor:
            cursor.execute("""SELECT ID
                                  FROM Investor
                                  WHERE ID = %s
                                  GROUP BY ID;
                                  """, [new_id])
            row = cursor.fetchone()
            if row: # ID exists
                is_ID = 1

        new_symbol = request.POST["Symbol"]
        with connection.cursor() as cursor:
            cursor.execute("""SELECT S.Symbol
                              FROM Stock S, (SELECT MAX(tDate) AS MaxDay
                                              FROM Stock LastDay) LastDay
                              WHERE S.Symbol = %s AND S.tDate = LastDay.MaxDay
                              GROUP BY S.Symbol;
                              """, [new_symbol])
            row = cursor.fetchone()
            print(row)
            if row: # Symbol exists
                is_symbol = 1

        if (is_ID == 0) or (is_symbol == 0): # ID or Symbol not exists
            return render(request, 'Buy_Stocks.html',
                          {'sql_res5': sql_res5,
                           'first_try' : first_try,
                           'is_ID' : is_ID,
                           'is_symbol' : is_symbol})

        with connection.cursor() as cursor:
            cursor.execute("""SELECT MAX(tDate) AS MaxDay
                              FROM Stock LastDay
                          """)
            StockMaxDay = dictfetchall(cursor)
            cursor.execute("""SELECT MAX(tDate) AS MaxDay
                              FROM Buying LastDay
                          """)
            BuyingMaxDay = dictfetchall(cursor)

        # Buying table is updated to the last day at stock table
        if StockMaxDay[0]['MaxDay'] == BuyingMaxDay[0]['MaxDay']:
            with connection.cursor() as cursor:
                cursor.execute("""SELECT B.ID
                                  FROM Buying B ,(SELECT MAX(tDate) AS MaxDay
                                                        FROM Buying) LastDay
                                  WHERE B.ID = %s AND B.Symbol = %s AND B.tDate = LastDay.MaxDay
                                  GROUP BY B.ID;
                                  """, [new_id, new_symbol])
                row = cursor.fetchone()

            if not row: # Buying not exists at the last day at stock table
                is_not_Buy = 1

        else:
            is_not_Buy = 1

        new_quantity = int(request.POST["Quantity"])

        with connection.cursor() as cursor:
            cursor.execute("""SELECT I.ID
                                FROM Investor I, Stock S,(SELECT MAX(tDate) AS MaxDay
                                                  FROM Stock) LastDay
                                WHERE I.ID = %s AND S.Symbol = %s AND S.tDate = LastDay.MaxDay
                                AND I.Amount >= S.Price * (%s)
                                GROUP BY I.ID;
                                  """, [new_id, new_symbol, new_quantity])
            row = cursor.fetchone()

        if row: # The investor has enough money to buy the quantity of stocks he wants of the company
            is_large = 1

        # The investor doesn't have enough money or the buying exists at the last day at stock table
        if (is_large == 0) or (is_not_Buy == 0):
            return render(request, 'Buy_Stocks.html',
                          {'sql_res5': sql_res5,
                                  'first_try' : first_try,
                                  'is_ID' : is_ID,
                                  'is_symbol' : is_symbol,
                                  'is_not_Buy' : is_not_Buy,
                                  'is_large' : is_large})

        if is_ID and is_symbol and is_not_Buy and is_large: # All the conditions are met

            today = StockMaxDay[:1]
            today = today[0]['MaxDay'].strftime('%Y-%m-%d')

            with connection.cursor() as cursor:
                cursor.execute("""
                                INSERT INTO Buying
                                VALUES (%s, %s, %s, %s);
                                """, [today, new_id, new_symbol, new_quantity])

            with connection.cursor() as cursor:
                cursor.execute("""
                        UPDATE Investor
                        SET Amount = Amount - (%s * (SELECT Price FROM Stock
                                                    WHERE Symbol = %s AND tDate = %s))
                        WHERE ID = %s;
                        """, [new_quantity, new_symbol, today, new_id])

            with connection.cursor() as cursor:
                cursor.execute("""SELECT TOP 10 *
                                  FROM Buying
                                  ORDER BY tDate DESC, ID DESC, Symbol ASC;
                                  """)
                sql_res5 = dictfetchall(cursor)

            return render(request, 'Buy_Stocks.html',
                            {'sql_res5': sql_res5,
                                   'first_try' : first_try,
                                   'is_ID' : is_ID,
                                   'is_symbol' : is_symbol,
                                   'is_large' : is_large,
                                   'is_not_Buy' : is_not_Buy})

    return render(request, 'Buy_Stocks.html', {'sql_res5': sql_res5,
                                                                  'first_try': first_try})