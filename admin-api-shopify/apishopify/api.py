import os
from io import open
import pathlib
import requests
import shopify
import json
from dotenv import load_dotenv
from requests.exceptions import HTTPError
load_dotenv()

class Api:

    def createNewProduct(self):

        try:
            session = shopify.Session(os.getenv('DOMAIN_STOREPRUEBASHOP'), os.getenv('API_VERSION'), os.getenv('CODE_TOKEN_STOREPRUEBASHOP'))
            shopify.ShopifyResource.activate_session(session)  
            new_product = shopify.Product()
            new_product.title = "Shopify Logo T-Shirt 22"
            new_product.status = 'active'
            new_product.vendor = 'Nike'
            new_product.tags = "Acero inoxidable, Automatico, Cristal Mineral, Hombre, Reloj"
            new_product.product_type = 'Copas'
            new_product.body_html = "<b>Test description</b>"
            variant = shopify.Variant()
            variant.price = 59890
            variant.sku = 'H0101q'
            variant.compare_at_price = 150000
            variant.grams = 10
            variant.weight = 10.0
            variant.inventory_management = 'shopify'
            variant.inventory_policy = 'deny'
            variant.weight_unit = 'g'
            variant.requires_shipping = True
            new_product.variants = [variant]
            new_product.save()  
            res_location = self.getLocations()
            if ( res_location != 'error' ):
                self.addStock(res_location, new_product.variants[0].inventory_item_id)  
            self.addImagesProduct(new_product.id)
            shopify.ShopifyResource.clear_session()
        except:
            print('error de conexion b')  


    def addStock(self, location_id, inventory_item_id):

        url_stock = os.getenv('DOMAIN_STOREPRUEBASHOP') + os.getenv('API_BASE') + 'inventory_levels/adjust.json'

        data = {
            "location_id": location_id,
            "inventory_item_id": inventory_item_id,
            "available_adjustment": 34
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
                print(result)
            except:
                print('error cargar imagen')







      
