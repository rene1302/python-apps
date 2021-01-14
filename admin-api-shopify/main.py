from apishopify import api

xx = api.Api()

# xx.getProducts()
# xx.getFileProducts("productos_relog.xls")
# xx.ValidaProducto("987654329")
# xx.getFileActualizaStock("carga_stock.xls")
xx.getFilePrecio("carga_precio.xls")
# xx.ventana()
# xx.prueba()