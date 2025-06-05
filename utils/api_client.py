import httpx

async def fetch_product_data():
    url = f"https://dummyjson.com/products"
    
    try:
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.get(url, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            return data
    except httpx.RequestError as e:
        raise Exception(f"Error de conexión al consultar la API externa: {str(e)}")
    except httpx.HTTPStatusError as e:
        raise Exception(f"Respuesta inválida de la API externa: {e.response.status_code}")
    except Exception as e:
        raise Exception(f"Ocurrió un error inesperado: {str(e)}")