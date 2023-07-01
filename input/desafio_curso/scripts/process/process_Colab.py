# -*- coding: utf-8 -*-
"""tst_desafio.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1pcNy7TlpDamMeQiIaLZzFrN_ZrxFxNeM
"""

!pip install pyspark
COLAB = False

from google.colab import drive
import pandas as pd

from pyspark.sql import SparkSession, dataframe
from pyspark.sql.types import StructType, StructField
from pyspark.sql.types import DoubleType, IntegerType, StringType
from pyspark.sql import HiveContext
from pyspark.sql.functions import *
from pyspark.sql import functions as f
from pyspark.sql.types import StringType, StructField, StructType
import os
import re

def replace_null_with_not_informed(df, fields):
    df_clean = df
    for field in fields:
        # Remover caracteres indesejados e espaços em branco
        #df_clean = df_clean.withColumn(field, regexp_replace(col(field), '[^\\w\\s]', ''))
        df_clean = df_clean.withColumn(field, regexp_replace(col(field), '[^\x20-\x7E]', ''))
        df_clean = df_clean.withColumn(field, trim(col(field)))
        # Substituir valores nulos e em branco por "Não informado"
        df_clean = df_clean.withColumn(field, when((col(field) == '') | (col(field) == 'NaN') | (col(field).isNull()), 'Não Informado').otherwise(col(field)))
    return df_clean

def replace_null_with_0(df, fields):
    df_clean = df
    for field in fields:
        # Remover caracteres indesejados e espaços em branco
        #df_clean = df_clean.withColumn(field, regexp_replace(col(field), '[^\\w\\s]', ''))
        df_clean = df_clean.withColumn(field, regexp_replace(col(field), '[^\x20-\x7E]', ''))
        df_clean = df_clean.withColumn(field, trim(col(field)))
        # Substituir valores nulos e em branco por 0
        df_clean = df_clean.withColumn(field, when((col(field) == '') | (col(field).isNull()), '0').otherwise(col(field)))
    return df_clean

# criando os data frames pandas (Válido apenas enquanto estivermos no Google Colab)
caminho_google_drive='/content/drive/MyDrive/00-AreaDeTrabalho/desafio_curso'
pandas_df_clientes = pd.read_csv(caminho_google_drive+'/raw/clientes.csv', delimiter=';', dtype=str)
#pandas_df_clientes = pandas_df_clientes.astype(str)

pandas_df_divisao = pd.read_csv(caminho_google_drive+'/raw/divisao.csv', delimiter=';', dtype=str)
#pandas_df_divisao = pandas_df_divisao.astype(str)

pandas_df_endereco = pd.read_csv(caminho_google_drive+'/raw/endereco.csv', delimiter=';', dtype=str)
#pandas_df_endereco = pandas_df_endereco.astype(str)

pandas_df_regiao = pd.read_csv(caminho_google_drive+'/raw/regiao.csv', delimiter=';', dtype=str)
#pandas_df_regiao = pandas_df_regiao.astype(str)

pandas_df_vendas = pd.read_csv(caminho_google_drive+'/raw/vendas.csv', delimiter=';', dtype=str)
# criando os data frames pySpark

spark = SparkSession.builder.appName("App_Tst_Desafio").getOrCreate()

df_clientes = spark.createDataFrame(pandas_df_clientes)
df_divisao = spark.createDataFrame(pandas_df_divisao)
df_endereco = spark.createDataFrame(pandas_df_endereco)
df_regiao = spark.createDataFrame(pandas_df_regiao)
df_vendas = spark.createDataFrame(pandas_df_vendas)

df_clientes.show()

# Lista de campos para o tratamento de substituição de valores nulos
txt_fields_to_replace = ['Address Number','Business Family', 'Customer',  'CustomerKey', 'Customer Type', 'Division'
                         , 'Line of Business', 'Phone', 'Region Code', 'Regional Sales Mgr', 'Search Type']

# Aplicar a função para substituir valores nulos nos campos especificados
df_clientes_filled = replace_null_with_not_informed(df_clientes, txt_fields_to_replace)

df_clientes_filled.show()

# Lista de campos para o tratamento de substituição de valores nulos
num_fields_to_replace = ['Business Unit']

# Aplicar a função para substituir valores nulos nos campos especificados
df_clientes_filled = replace_null_with_0(df_clientes_filled, num_fields_to_replace)

df_clientes_filled.show()

df_endereco.show()

txt_fields_to_replace = ['City', 'Country', 'Customer Address 1', 'Customer Address 2', 'Customer Address 3', 'Customer Address 4', 'State', 'Zip Code']
df_endereco_filled = replace_null_with_not_informed(df_endereco, txt_fields_to_replace)
num_fields_to_replace = ['Address Number']
df_endereco_filled = replace_null_with_0(df_endereco_filled, num_fields_to_replace)
df_endereco_filled.show()

df_vendas.show()

txt_fields_to_replace = ['CustomerKey', 'Invoice Number', 'Item Class','Item Number', 'Item', 'Sales Rep', 'U/M']
df_vendas_filled = replace_null_with_not_informed(df_vendas, txt_fields_to_replace)
num_fields_to_replace = ['Discount Amount', 'Line Number', 'List Price', 'Order Number', 'Sales Amount', 'Sales Amount Based on List Price', 'Sales Cost Amount', 'Sales Margin Amount'
                         , 'Sales Price', 'Sales Quantity']
df_vendas_filled = replace_null_with_0(df_vendas_filled, num_fields_to_replace)
df_vendas_filled.show()

# criacao do modelo dimensional

df_clientes_filled.createOrReplaceTempView('clientes')
df_divisao.createOrReplaceTempView('divisao')
df_endereco_filled.createOrReplaceTempView('endereco')
df_regiao.createOrReplaceTempView('regiao')
df_vendas_filled.createOrReplaceTempView('vendas')

sql = '''
   SELECT
      v.`Actual Delivery Date` AS actual_delivery_date,
      v.CustomerKey as customerKey,
      v.DateKey as datekey,
      v.`Discount Amount` AS discount_amount,
      v.`Invoice Date` AS invoice_date,
      v.`Invoice Number` AS invoice_number,
      v.`Item Class` AS item_class,
      v.`Item Number` AS item_number,
      v.Item as item,
      v.`Line Number` AS line_number,
      v.`List Price` AS list_price,
      v.`Order Number` AS order_number,
      v.`Promised Delivery Date` AS promised_delivery_date,
      v.`Sales Amount` AS sales_amount,
      v.`Sales Amount Based on List Price` AS sales_amount_based_on_list_price,
      v.`Sales Cost Amount` AS sales_cost_amount,
      v.`Sales Margin Amount` AS sales_margin_amount,
      v.`Sales Price` AS sales_price,
      v.`Sales Quantity` AS sales_quantity,
      v.`Sales Rep` AS sales_rep,
      v.`U/M` AS u_m,
      c.`Address Number` as address_number,
      c.`Business Family` as business_family,
      c.`Business Unit` as business_unit,
      c.Customer as customer,
      c.`Customer Type` as customer_type,
      c.Division as division,
      c.`Line of Business` as line_of_business,
      c.Phone as phone,
      c.`Region Code` as region_code,
      c.`Regional Sales Mgr` as regional_sales_Mgr,
      c.`Search Type` as search_type,
      e.city,
      e.country,
      e.`Customer Address 1` as customer_address_1,
      e.`Customer Address 2` as customer_address_2,
      e.`Customer Address 3` as customer_address_3,
      e.`Customer Address 4` as customer_address_4,
      e.State as state,
      e.`Zip Code` as zip_code,
      d.`Division Name` as division_name,
      r.`Region Name` as region_name
   FROM vendas AS v
   INNER JOIN clientes AS c ON c.CustomerKey = v.CustomerKey
   LEFT JOIN endereco AS e ON c.`Address Number` = e.`Address Number`
   LEFT JOIN divisao AS d ON c.Division = d.Division
   LEFT JOIN regiao AS r ON c.`Region Code` = r.`Region Code`
'''

# Criação da STAGE
df_stage = spark.sql(sql)

df_stage.show()

# Criação dos Campos Calendario
df_stage = (df_stage
            .withColumn('ano', year(to_date(df_stage.invoice_date,'dd/MM/yyyy')))
            .withColumn('mes', month(to_date(df_stage.invoice_date,'dd/MM/yyyy')))
            .withColumn('dia', dayofmonth(to_date(df_stage.invoice_date,'dd/MM/yyyy')))
            .withColumn('trimestre', quarter(to_date(df_stage.invoice_date,'dd/MM/yyyy')))
           )

df_stage.show()

from pyspark.sql.functions import isnan
# Criação das Chaves do Modelo

df_stage = df_stage.withColumn("DW_CLIENTE", sha2(concat_ws("", df_stage.customerKey, df_stage.customer, df_stage.address_number, df_stage.division, df_stage.region_code), 256))
df_stage = df_stage.withColumn("DW_DIVISAO", sha2(concat_ws("", df_stage.division, df_stage.division_name), 256))
df_stage = df_stage.withColumn("DW_ENDERECO", sha2(concat_ws("", df_stage.address_number, df_stage.city, df_stage.country, df_stage.state), 256))
df_stage = df_stage.withColumn("DW_REGIAO", sha2(concat_ws("", df_stage.region_code, df_stage.region_name), 256))
df_stage = df_stage.withColumn("DW_TEMPO", sha2(concat_ws("", df_stage.invoice_date, df_stage.ano, df_stage.mes, df_stage.dia), 256))

df_stage.createOrReplaceTempView('stage')

#df_stage.show()

df_filtered = df_stage.filter(col("sales_amount").isNull())
df_filtered.show()
df_filtered = df_stage.filter(isnan(col("sales_amount").cast("decimal")))
df_filtered.show()

#Criando a dimensão Clientes
dim_clientes = spark.sql('''
    SELECT DISTINCT
        DW_CLIENTE,
        customerKey,
        customer,
        address_number,
        business_family,
        business_unit,
        customer_type,
        division,
        line_of_business,
        phone,
        region_code,
        regional_sales_Mgr,
        search_type
    FROM stage
''')

#Criando a dimensão Divisao
dim_divisao = spark.sql('''
    SELECT DISTINCT
        DW_DIVISAO,
        division,
        division_name
    FROM stage
''')

#Criando a dimensão Endereco
dim_endereco = spark.sql('''
    SELECT DISTINCT
        DW_ENDERECO,
        address_number,
        city,
        country,
        customer_address_1,
        customer_address_2,
        customer_address_3,
        customer_address_4,
        state,
        zip_code
    FROM stage
''')

#Criando a dimensão Regiao
dim_regiao = spark.sql('''
    SELECT DISTINCT
        DW_REGIAO,
        region_code,
        region_name
    FROM stage
''')

#Criando a dimensão Tempo
dim_tempo = spark.sql('''
    SELECT DISTINCT
        DW_TEMPO,
        invoice_date,
        ano,
        mes,
        dia
    FROM stage
''')

#Criando a Fato vendas
ft_vendas = spark.sql('''
    SELECT
        DW_CLIENTE,
        DW_DIVISAO,
        DW_ENDERECO,
        DW_REGIAO,
        DW_TEMPO,
        sum(sales_amount) as valor_de_Venda
    FROM stage
    group by
        DW_CLIENTE,
        DW_DIVISAO,
        DW_ENDERECO,
        DW_REGIAO,
        DW_TEMPO
''')


dim_regiao.show()

ft_vendas.show()

# função para salvar os dados
def salvar_df(df, file):
   if COLAB:
      # Salvar DataFrame como arquivo CSV localmente
      caminho_local = "C:\\tmp\\desafio_curso\\"+file+".csv"
      df_pandas = df.toPandas()
      df_pandas.to_csv(caminho_local, sep=";", index=False)
      # Mover o arquivo para uma pasta no Google Drive
      import shutil
      # Mover o arquivo CSV para a pasta do Google Drive
      shutil.move(caminho_local, caminho_google_drive+'/gold/'+file+".csv")
   else:
      output = "/input/desafio_curso/gold/" + file
      erase = "hdfs dfs -rm " + output + "/*"
      rename = "hdfs dfs -get /datalake/gold/"+file+"/part-* /input/desafio_curso/gold/"+file+".csv"
      print(rename)
      df.coalesce(1).write\
          .format("csv")\
          .option("header", True)\
          .option("delimiter", ";")\
          .mode("overwrite")\
          .save("/datalake/gold/"+file+"/")
      os.system(erase)
      os.system(rename)

# salvando as tabelas de dimensão e fato em GOLD
salvar_df(ft_vendas, 'ft_vendas')
salvar_df(dim_clientes, 'dim_clientes')
salvar_df(dim_divisao, 'dim_divisao')
salvar_df(dim_endereco, 'dim_endereco')
salvar_df(dim_regiao, 'dim_regiao')
salvar_df(dim_tempo, 'dim_tempo')