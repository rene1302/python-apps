import os
from io import open
import xlrd
import pathlib
import requests
import shopify
import re
import json
from dotenv import load_dotenv
from requests.exceptions import HTTPError
load_dotenv()

class Api:

    def prueba(self):
        print('todo bien')

    def ValidaProducto(self, sku):
        try:
            session = shopify.Session(os.getenv('DOMAIN_STOREPRUEBASHOP'), os.getenv('API_VERSION'), os.getenv('CODE_TOKEN_STOREPRUEBASHOP'))
            shopify.ShopifyResource.activate_session(session) 
            id_product = '''
                query ($sku : String){
                    productVariants(first:1, query: $sku){
                        edges{
                            node{
                                product{
                                    id
                                }
                            }
                        }
                    }
                }
            '''    
            variable = {"sku": sku}
            product = shopify.GraphQL().execute(id_product, variable)
            data = json.loads(product)
            if (data['data']['productVariants']['edges'] == []):
                res = 0
            else:    
                edges = data['data']['productVariants']['edges']
                for x in edges:
                    id = x['node']['product']['id']
                    res = str(id[22:])
            shopify.ShopifyResource.clear_session()
        except:
            res = -1 

        return res     

    def getFileActualizaStock(self, file_origin): 
        ruta = str(pathlib.Path().absolute()) + "/admin-api-shopify/apishopify/" + file_origin
        workbook = xlrd.open_workbook(ruta, formatting_info=True)
        sheet = workbook.sheet_by_index(0)
        
        for i in range(1, sheet.nrows):
            sku = str(int(float(repr(sheet.cell_value(i,0)))))
            stock = int(float(repr(sheet.cell_value(i,1))))
            if (sku is not None and stock is not None):
                id_product = self.ValidaProducto(sku)
                if (id_product !=0 and id_product != -1):
                    self.actualizaStock(id_product, stock)
                else:
                    continue    
            else:
                continue    


    def actualizaStock(self, id_product, stock):
        session = shopify.Session(os.getenv('DOMAIN_STOREPRUEBASHOP'), os.getenv('API_VERSION'), os.getenv('CODE_TOKEN_STOREPRUEBASHOP'))
        shopify.ShopifyResource.activate_session(session) 
        product = shopify.Product.find(int(id_product))
        res_location = self.getLocations()
        self.addStock(res_location, product.variants[0].inventory_item_id, stock)





    def getFileProducts(self, file_origin):
        ruta = str(pathlib.Path().absolute()) + "/admin-api-shopify/apishopify/" + file_origin
        workbook = xlrd.open_workbook(ruta, formatting_info=True)
        sheet = workbook.sheet_by_index(0)        

        for i in range(1, sheet.nrows):
            sku =  str(int(float(repr(sheet.cell_value(i,0)))))
            nombre =  sheet.cell_value(i,1)
            descripcion =  sheet.cell_value(i,2)
            precio_base = int(float(repr(sheet.cell_value(i,3))))
            precio_descuento = int(float(repr(sheet.cell_value(i,4))))
            activo =  sheet.cell_value(i,5)
            tags =  sheet.cell_value(i,6)
            stock = int(float(repr(sheet.cell_value(i,7))))
            peso = float(repr(sheet.cell_value(i,8)))
            unidad_peso =  sheet.cell_value(i,9)
            proveedor =  sheet.cell_value(i,10)
            categoria =  sheet.cell_value(i,11)
            res_existe = self.ValidaProducto(sku)
            if (res_existe == 0):
                res_producto = self.createNewProduct(sku, nombre, descripcion, precio_base, precio_descuento, activo, tags, stock, peso, unidad_peso, proveedor, categoria, res_existe)
                if (res_producto == 0):
                    print(f"el producto con el sku {sku} se creo correctamente.")
                else:
                    print("hubo un error al crear el producto.")    
            elif (res_existe == -1):
                print('hubo un error al verificar el sku en la web.')    
                continue
            else:
                res_producto = self.createNewProduct(sku, nombre, descripcion, precio_base, precio_descuento, activo, tags, stock, peso, unidad_peso, proveedor, categoria, res_existe)
                if (res_producto == 0):
                    print(f"el producto con el sku {sku} se actualizó correctamente.")
                else:
                    print('hubo un error al actualizar el sku en la web.')


    def createNewProduct(self, sku, nombre, descripcion, precio_base, precio_descuento, activo, tags, stock, peso, unidad_peso, proveedor, categoria, producto_existe):
        try:
            session = shopify.Session(os.getenv('DOMAIN_STOREPRUEBASHOP'), os.getenv('API_VERSION'), os.getenv('CODE_TOKEN_STOREPRUEBASHOP'))
            shopify.ShopifyResource.activate_session(session)  
     
            if (producto_existe == 0):
                new_product = shopify.Product()
            else:
                new_product = shopify.Product.find(int(producto_existe)) 

            new_product.title = nombre
            new_product.status = activo
            new_product.vendor = proveedor
            new_product.tags = tags
            new_product.product_type = categoria
            new_product.body_html = descripcion
            variant = shopify.Variant()
            variant.price = precio_descuento
            variant.sku = sku
            variant.compare_at_price = precio_base
            variant.grams = peso
            variant.weight = peso
            variant.inventory_management = 'shopify'
            variant.inventory_policy = 'deny'
            variant.weight_unit = unidad_peso
            variant.requires_shipping = True
            new_product.variants = [variant]
            new_product.save() 
            res_location = self.getLocations()
            if ( res_location != 'error' ):
                self.addStock(res_location, new_product.variants[0].inventory_item_id, stock)  
            shopify.ShopifyResource.clear_session()
            res = 0
        except:
            res = -1

        return res      

    def addStock(self, location_id, inventory_item_id, stock):
        url_stock = os.getenv('DOMAIN_STOREPRUEBASHOP') + os.getenv('API_BASE') + 'inventory_levels/adjust.json'

        data = {
            "location_id": location_id,
            "inventory_item_id": inventory_item_id,
            "available_adjustment": stock
        }

        headers = { os.getenv('TOKEN_HEADER') : os.getenv('CODE_TOKEN_STOREPRUEBASHOP')}

        requests.post(url_stock, headers = headers, data = data)

    def getLocations(self):
        url_location =  os.getenv('DOMAIN_STOREPRUEBASHOP') + os.getenv('API_BASE') + 'locations.json'  

        try:

            result = requests.get(url_location, headers = { os.getenv('TOKEN_HEADER') : os.getenv('CODE_TOKEN_STOREPRUEBASHOP') })

            locations = result.json()['locations']

            for i in locations:
                res = i['id']
        except:
            res = 'error'        
        
        return res

    def addImagesProduct(self, id_product):
        ruta_img1 = "https://cdn.shopify.com/s/files/1/0516/6989/3287/files/ff.jpg?v=1608810812"
        ruta_img2 = "https://cdn.shopify.com/s/files/1/0516/6989/3287/files/foto.jpg?v=1608749484"

        url_images = os.getenv('DOMAIN_STOREPRUEBASHOP') + os.getenv('API_BASE') + 'products/' + str(id_product) + '/images.json'

        headers = { os.getenv('TOKEN_HEADER') : os.getenv('CODE_TOKEN_STOREPRUEBASHOP'), 'Content-Type': 'application/json', 'Accept': 'text/plain'}

        for i in range(2):
            if( i == 0 ):
                img = ruta_img1
                pos = 1
            else:
                img = ruta_img2  
                pos = 2  
            data = {
                "image": {
                    "src": img,
                    "position": pos 
                }
            }

            try:
                result = requests.post(url_images, headers=headers, data=json.dumps(data))
            except:
                print('error cargar imagen')







      
