import os
from tkinter import *
from tkinter import filedialog
from tkinter.filedialog import askopenfile 
from io import open
import xlrd
import pathlib
import requests
import shopify
import re
import json
import cv2
import string
import base64
from dotenv import load_dotenv
from requests.exceptions import HTTPError
load_dotenv()

class Api:

    def add_quote(self, a):
        return '"{0}"'.format(a)


    def open_file(self, ventana): 
        files = filedialog.askopenfilenames()
        jpg = 0
        total = 0
        aux_sku = ""
        id_product = 0
        for file in files:
            if file[-4:] in ('.jpg', '.png'):
                name_img = os.path.basename(file)
                sku = name_img.split('_',1)[0]
                if (sku != aux_sku):
                    id_product = self.ValidaProducto(sku)
                    aux_sku = sku    
                pos = name_img.split('_',1)[1]
                pos = pos.split('.',1)[0]
                ruta = file
                if (id_product !=0 and id_product != -1):
                    self.addImagesProduct(id_product, ruta, name_img, pos)
                    print(f"La foto {name_img} se subio con exito")
                else:
                    print('no existe producto')    
                jpg += 1
            total += 1    

        print(f'total de fotos: {total}')
        print(f'fotos con buen formato (.jpg ó .png): {jpg}')    


    def ventana(self):
        ventana = Tk()
        ventana.geometry("1250x500")
        ventana.resizable(0,0)
        # frame left
        frame_left = Frame(ventana, width = "625", height = "500")
        frame_left.place(x=0, y=0)
        frame_left.config(
            bg= "#ccc",
        )
        frame_left.propagate(False)
        texto = Label(frame_left, text="Dominios")
        texto.pack(anchor=CENTER)
        texto.config(
            font = ("Verdana 24 bold italic"),
            bg = "#ccc",
            padx = 30
        )
        # frame right top
        frame_r_top = Frame(ventana, width = "625", height = "250")
        frame_r_top.place(x=625, y=0)
        frame_r_top.config(
            bg = "#cdd3da"
        )
        frame_r_top.propagate(False)
        texto = Label(frame_r_top, text="Acciones")
        texto.pack(anchor=CENTER)
        texto.config(
            font = ("Verdana 24 bold italic"),
            bg = "#cdd3da",
            padx = 30
        )
        # frame right bottom 
        frame_r_bottom = Frame(ventana, width = "625", height = "250")
        frame_r_bottom.place(x=625, y=250)
        frame_r_bottom.config(
            bg = "#bdc1c5"
        )
        frame_r_bottom.propagate(False)
        texto = Label(frame_r_bottom, text="Subir Fotos")
        texto.pack(anchor=CENTER)
        texto.config(
            font = ("Verdana 24 bold italic"),
            bg = "#bdc1c5",
            padx = 30
        )
        btn = Button(frame_r_bottom, text ='Seleccionar carpeta', command=lambda:self.open_file(ventana)) 
        btn.pack(side = TOP, pady = 10) 
        ventana.title('Panel Shopify Api')
        ventana.mainloop()      
     

    def ValidaProducto(self, sku):
        try:
            session = shopify.Session(os.getenv('DOMAIN_HBWZURICH'), os.getenv('API_VERSION'), os.getenv('CODE_TOKEN_HBWZURICH'))
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
            if (type(sheet.cell_value(i,0)) is float):
                sku = str(int(float(repr(sheet.cell_value(i,0)))))
            elif (type(sheet.cell_value(i,0)) is str):
                sku = sheet.cell_value(i,0)  
            stock = int(float(repr(sheet.cell_value(i,1))))
            if (sku is not None and stock is not None):
                id_product = self.ValidaProducto(sku)
                if (id_product !=0 and id_product != -1):
                    self.actualizaStock(id_product, stock)
                else:
                    continue    
            else:
                continue  


    def getFilePrecio(self, file_origin):
        ruta = str(pathlib.Path().absolute()) + "/admin-api-shopify/apishopify/" + file_origin
        workbook = xlrd.open_workbook(ruta, formatting_info=True)
        sheet = workbook.sheet_by_index(0)

        for i in range(1, sheet.nrows):
            if (type(sheet.cell_value(i,0)) is float):
                sku = str(int(float(repr(sheet.cell_value(i,0)))))
            elif (type(sheet.cell_value(i,0)) is str):
                sku = sheet.cell_value(i,0) 
            precio_base = int(float(repr(sheet.cell_value(i,1))))
            precio_descuento = int(float(repr(sheet.cell_value(i,2))))

            if ( sku is not None and precio_base is not None and precio_descuento is not None ):
                id_product = self.ValidaProducto(sku)
                if (id_product !=0 and id_product != -1):
                    self.actualizaPrecio(id_product, precio_base, precio_descuento)
                else:
                    continue
            else:
                continue  

    
    def getVariantIDProduct(self, id_product):

        url_variant_id = os.getenv('DOMAIN_HBWZURICH') + os.getenv('API_BASE') + "products/" + str(id_product) + "/variants.json"
        headers = { os.getenv('TOKEN_HEADER') : os.getenv('CODE_TOKEN_HBWZURICH')}
        
        try:
            result = requests.get(url_variant_id, headers = headers)
            data = json.loads(result.text)
            if (data):
                id_variant = data['variants'][0]['id']
            else:
                id_variant = 0
        except:
            id_variant = 0

        return id_variant   


    def actualizaPrecio(self, id_product, precio_base, precio_descuento):

        id_variant = self.getVariantIDProduct(id_product)
        headers = { os.getenv('TOKEN_HEADER') : os.getenv('CODE_TOKEN_HBWZURICH'), 'content-type': 'application/json'}
        if (id_variant != 0):
            url_precio = os.getenv('DOMAIN_HBWZURICH') + os.getenv('API_BASE') + 'variants/' + str(id_variant) + '.json'

            data = {
                "variant": {
                    "price": str(precio_descuento),
                    "compare_at_price": str(precio_base)
                }
            }

            try:
                requests.put(url_precio, headers = headers, data = json.dumps(data))
            except:
                return

        else:
            return            


    def actualizaStock(self, id_product, stock):
        session = shopify.Session(os.getenv('DOMAIN_HBWZURICH'), os.getenv('API_VERSION'), os.getenv('CODE_TOKEN_HBWZURICH'))
        shopify.ShopifyResource.activate_session(session) 
        product = shopify.Product.find(int(id_product))
        res_location = self.getLocations()
        self.addStock(res_location, product.variants[0].inventory_item_id, stock)


    def getFileProducts(self, file_origin):
        ruta = str(pathlib.Path().absolute()) + "/admin-api-shopify/apishopify/" + file_origin
        workbook = xlrd.open_workbook(ruta, formatting_info=True)
        sheet = workbook.sheet_by_index(0)        

        for i in range(1, sheet.nrows):
            if (type(sheet.cell_value(i,0)) is float):
                sku = str(int(float(repr(sheet.cell_value(i,0)))))
            elif (type(sheet.cell_value(i,0)) is str):
                sku = sheet.cell_value(i,0)  
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
            session = shopify.Session(os.getenv('DOMAIN_HBWZURICH'), os.getenv('API_VERSION'), os.getenv('CODE_TOKEN_HBWZURICH'))
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


    def getLocations(self):
        url_location =  os.getenv('DOMAIN_HBWZURICH') + os.getenv('API_BASE') + 'locations.json'  

        try:

            result = requests.get(url_location, headers = { os.getenv('TOKEN_HEADER') : os.getenv('CODE_TOKEN_HBWZURICH') })

            locations = result.json()['locations']

            for i in locations:
                res = i['id']
        except:
            res = 'error'        

        return res       


    def addStock(self, location_id, inventory_item_id, stock):
        url_stock = os.getenv('DOMAIN_HBWZURICH') + os.getenv('API_BASE') + 'inventory_levels/adjust.json'

        data = {
            "location_id": location_id,
            "inventory_item_id": inventory_item_id,
            "available_adjustment": stock
        }

        headers = { os.getenv('TOKEN_HEADER') : os.getenv('CODE_TOKEN_HBWZURICH')}

        requests.post(url_stock, headers = headers, data = data)


    def addImagesProduct(self, id_product, img, name, pos):

        url_images = os.getenv('DOMAIN_HBWZURICH') + os.getenv('API_BASE') + 'products/' + str(id_product) + '/images.json'

        headers = { os.getenv('TOKEN_HEADER') : os.getenv('CODE_TOKEN_HBWZURICH'), 'content-type': 'application/json' }

        with open(img, "rb") as f:
            im_bytes = f.read()        
        im_b64 = base64.b64encode(im_bytes).decode("utf8")
        im_b64 = self.add_quote(im_b64)
 
        data = {
            "image": {
                "attachment": str(im_b64),
                "filename": str(name),
                "position": int(pos)
            }
        }

        try:
            result = requests.post(url_images, headers = headers, data = json.dumps(data))
        except:
            print(f"Error al cargar la imagen {name}")

       







      
