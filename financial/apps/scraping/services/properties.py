URL_BASE = 'https://www.bolsadesantiago.com/'

props = {
    'headers': {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
        'Connection': 'keep-alive',
        # 'Content-Length': '2',
        'Content-Type': 'application/json;charset=UTF-8',
        # 'Cookie': 'BCS-HTML5_corporativa-443-PROD=684715681.20480.0000; gb-wbchtbt-uid=1591892299902; _csrf=GjqJBqBp8g2utqY0YXHvFOYc; _ga=GA1.2.2090315841.1591892304; _gid=GA1.2.1663141191.1591892304; __gads=ID=da6dac373caf459c:T=1591892304:S=ALNI_MbLcJ6pcWmMhI61KvNMEF1unZ-CmA; _gat=1',
        'DNT': '1',
        'Host': 'www.bolsadesantiago.com',
        'Origin': 'https://www.bolsadesantiago.com',
        'Referer': 'https://www.bolsadesantiago.com/acciones_precios',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36',
        # 'X-CSRF-Token': 'lzN0ykSE-zU-dYStFUocaGAp-KbeF3HtzndQ',
    },
    'uri': {
        'csrf': 'api/Securities/csrfToken',
        'nemos': 'api/RV_ResumenMercado/getAccionesPrecios',
        'get_resumen_precios': 'api/RV_Instrumentos/getResumenPrecios'
    },
    'mapping_values': {
        'nemos': {
            'BONO_VERDE': 'green_bonus',
            'DJSI': 'djsi',
            'ETFs_EXTRANJERO': 'etfs_foreign',
            'ISIN': 'isin',
            'MONEDA': 'coin',
            'MONTO': 'amount',
            'NEMO': 'nemo',
            'PESO': 'weight',
            'PRECIO_CIERRE': 'close_price',
            'PRECIO_COMPRA': 'buy_price',
            'PRECIO_VENTA': 'sell_price',
            'UN_TRANSADAS': 'traded_units',
            'VARIACION': 'variant',
        },
    },
}
