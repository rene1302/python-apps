import xlrd
import pathlib
class Codeexcel:

    def LeerExcel(self):
        productos = dict()
        ruta = str(pathlib.Path().absolute()) + '/excel-functions/excel/productos.xls'
        workbook = xlrd.open_workbook(ruta, formatting_info=True)
        sheet = workbook.sheet_by_index(0)
        
        for i in range(1, sheet.nrows):
            sku = str(repr(sheet.cell_value(i,0)))
            nombre = str(repr(sheet.cell_value(i,1)))
            descripcion = str(repr(sheet.cell_value(i,2)))
            precio_base = int(float(repr(sheet.cell_value(i,3))))
            precio_descuento = int(float(repr(sheet.cell_value(i,4))))
            activo = str(repr(sheet.cell_value(i,5)))
            tags = str(repr(sheet.cell_value(i,6)))
            stock = int(float(repr(sheet.cell_value(i,7))))
            peso = float(repr(sheet.cell_value(i,8)))
            unidad_peso = str(repr(sheet.cell_value(i,9)))
            proveedor = str(repr(sheet.cell_value(i,10)))
            categoria = str(repr(sheet.cell_value(i,11)))
