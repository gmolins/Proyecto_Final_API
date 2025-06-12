# StoreAPI

## Descripción general del proyecto
Implementaremos un sistema de gestión de pedidos que permita crear, leer, actualizar y eliminar pedidos, conectándonos a una base de datos PostgreSQL. Los pedidos se alimentan de productos procedentes de una API externa.

## Tecnologías usadas
### API
* Python 3.12
* FastAPI
* SQLModel
* Pydantic
* Pandas
### BBDD
* PostgresSQL para tablas de usuario, status, etc
* Redis para la gestión de tokens
### Despliegue
* Dockerfile
* Docker Compose

## Instrucciones para instalar y ejecutar con Docker Compose
Desde la raíz del proyecto ejecutamos en terminal
````
docker compose -f 'docker-compose.yml' up -d --build 
````

## Explicación de los flujos principales y la integración con la API externa
El cliente comienza por registrarse o iniciar sesión en la API 
* ***POST api/auth/register***
* ***POST api/auth/login***.  

A continuación puede hacer una búsqueda de los productos de la API externa
* ***GET api/products/product***

Una vez identificados los productos de interés, puede crear un pedido y añadir productos a este

* ***POST api/orders***
* ***POST api/products/order***

Puede consultar el estado de su pedido

* ***POST api/reporting/reporting/formato***

Por último puede cerrar sesión
* ***POST api/auth/logout***

## Ejemplos para realizar peticiones a endpoints más importantes

Añadir un producto al pedido:
* Método: POST
* Endpoint: /api/products/order
* Parámetros: order_id (int) ID de pedido, product_id (int) ID de producto, product_quantity (int) cantidad de producto.