from apishopify import api

xx = api.Api()

# xx.getProducts()
# xx.getFileProducts("productos.xls")
# xx.ValidaProducto("12345678")
xx.getFileActualizaStock("carga_stock.xls")
# xx.prueba()