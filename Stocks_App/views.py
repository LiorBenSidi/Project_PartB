from django.shortcuts import render
from .models import Transactions
from django.db import connection
from datetime import datetime


# Create your views here.

def dictfetchall(cursor):
    # Returns all rows from a cursor as a dict '''
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

def index(request):
    return render(request, 'index.html')

def Query_Results(request):
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
    first_try = 0
    is_ID = 0
    is_not_Tran = 0
    if request.method == 'POST' and request.POST:
        with connection.cursor() as cursor:
            cursor.execute("""SELECT  TOP 10 *
                              FROM Transactions
                              ORDER BY tDate DESC;
                              """)
            sql_res4 = dictfetchall(cursor)

        first_try = 1
        new_id = request.POST["ID"]
        with connection.cursor() as cursor:
            cursor.execute("""SELECT ID
                              FROM Investor
                              WHERE ID = %s
                              GROUP BY ID;
                              """, [new_id])
            row = cursor.fetchone()
            if not row:
                return render(request, 'Add_Transaction.html', {'sql_res4': sql_res4,
                                                                'first_try': first_try, 'is_ID': is_ID})
            else:
                is_ID = 1
                with connection.cursor() as cursor:
                    cursor.execute("""SELECT B.ID
                                      FROM Buying B ,(SELECT MAX(tDate) AS MaxDay
                                                      FROM Stock) LastDay
                                      WHERE B.ID = %s AND B.tDate = LastDay.MaxDay
                                      GROUP BY B.ID;
                                      """, [new_id])
                    row = cursor.fetchone()
                    if not row:
                        return render(request, 'Add_Transaction.html',
                                      {'sql_res4': sql_res4,
                                       'first_try': first_try,
                                       'is_ID': is_ID,
                                       'is_not_Tran': is_not_Tran})
                    else:
                        is_not_Tran = 1
                        new_id = dictfetchall(cursor)
                        new_amount = request.POST["Transaction"]
                        with connection.cursor() as cursor:
                            cursor.execute("""SELECT MAX(tDate) AS MaxDay
                                              FROM Stock;
                                              """)
                            today = dictfetchall(cursor)

                        new_Transaction = Transactions(ID=new_id,
                                              TAmount=new_amount,
                                              tdate=today)
                        new_Transaction.save()

                        #TODO: update the amount in the investor table
                        with connection.cursor() as cursor:
                            cursor.execute("""
                                UPDATE Investor
                                SET Amount = Amount + %s
                                WHERE ID = %s;
                                """, [new_amount, new_id])

                        return render(request, 'Add_Transaction.html',
                                                      {'sql_res4': sql_res4,
                                                             'first_try' : first_try,
                                                             'is_ID' : is_ID,
                                                             'is_not_Tran' : is_not_Tran})
    else:
        return render(request, 'Add_Transaction.html', {'first_try': first_try})