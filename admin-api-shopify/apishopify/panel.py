from apishopify import connect
import os
from io import open
import pathlib
import requests
import shopify
import json
from dotenv import load_dotenv
load_dotenv()

class Panel:

    # Conexión bd Panel
    conx = connect.Connect()
    res_conx = conx.conexion()
    conexion = res_conx[0]
    cursor = res_conx[1]

    def validaSku(self, sku):
        sql = f'SELECT id FROM base_stock WHERE sku = "{sku}"'
        self.cursor.execute(sql)
        self.cursor.fetchall()
        tuplas = self.cursor.rowcount
        return tuplas


    def actualizarStock(self, sku, stock):
        tuplas = self.validaSku('Sku002')

        

