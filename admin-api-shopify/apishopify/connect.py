import mysql.connector

class Connect:

    def conexion(self):
        conn = mysql.connector.connect(
            host='138.255.101.220',
            user="webconsu",
            password="5seJ3F6j0Y:vY!",
            database="webconsu_panel_stock_shopify"
        )
        cursor = conn.cursor()

        return [conn, cursor]


