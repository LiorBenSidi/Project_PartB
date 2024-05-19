# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Buying(models.Model):
    # Field name made lowercase. The composite primary key (tDate, ID, Symbol) found, that is not supported. The first column is selected.
    tdate = models.OneToOneField('Stock', models.DO_NOTHING, db_column='tDate', primary_key=True)
    id = models.ForeignKey('Investor', models.DO_NOTHING, db_column='ID')  # Field name made lowercase.
    symbol = models.ForeignKey('Stock', models.DO_NOTHING, db_column='Symbol', related_name='+')
    bquantity = models.IntegerField(db_column='BQuantity', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Buying'
        unique_together = (('tdate', 'id', 'symbol'),)


class Company(models.Model):
    symbol = models.CharField(db_column='Symbol', primary_key=True, max_length=10)  # Field name made lowercase.
    sector = models.CharField(db_column='Sector', max_length=40, blank=True, null=True)  # Field name made lowercase.
    location = models.CharField(db_column='Location', max_length=40, blank=True, null=True)  # Field name made lowercase.
    founded = models.IntegerField(db_column='Founded', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Company'


class Investor(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    name = models.CharField(db_column='Name', max_length=40, blank=True, null=True)  # Field name made lowercase.
    amount = models.FloatField(db_column='Amount', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Investor'


class Stock(models.Model):
    # Field name made lowercase. The composite primary key (Symbol, tDate) found, that is not supported. The first column is selected.
    symbol = models.OneToOneField(Company, models.DO_NOTHING, db_column='Symbol', primary_key=True)
    tdate = models.DateField(db_column='tDate')  # Field name made lowercase.
    price = models.FloatField(db_column='Price', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Stock'
        unique_together = (('symbol', 'tdate'),)


class Transactions(models.Model):
    # Field name made lowercase. The composite primary key (tDate, ID) found, that is not supported. The first column is selected.
    tdate = models.DateField(db_column='tDate', primary_key=True)
    id = models.ForeignKey(Investor, models.DO_NOTHING, db_column='ID')  # Field name made lowercase.
    tamount = models.IntegerField(db_column='TAmount', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Transactions'
        unique_together = (('tdate', 'id'),)
