import httpx

async def fetch_weather_data(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,relative_humidity_2m,rain"
    
    try:
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.get(url, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            hourly = data.get("hourly", {})
            return {
                "time": hourly.get("time", []),
                "temperature_2m": hourly.get("temperature_2m", []),
                "relative_humidity_2m": hourly.get("relative_humidity_2m", []),
                "rain": hourly.get("rain", [])
            }
    except httpx.RequestError as e:
        raise Exception(f"Error de conexión al consultar la API externa: {str(e)}")
    except httpx.HTTPStatusError as e:
        raise Exception(f"Respuesta inválida de la API externa: {e.response.status_code}")
    except Exception as e:
        raise Exception(f"Ocurrió un error inesperado: {str(e)}")