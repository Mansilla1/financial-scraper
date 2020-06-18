# Financial scraper

El proyecto tiene como objetivo poder obtener información de [la bolsa de santiago](https://www.bolsadesantiago.com/) por medio de `web-scraping`.

# Tecnologías a utilizar

* [Docker](https://docs.docker.com/): Para levantar contenedores con las tecnologías que requerimos.
* [Docker-compose](https://docs.docker.com/compose/): Para administrar los contenedores del proyecto (pueden ser varios, pero actualmente tenemos dos).
* [Python](https://www.python.org/): Como lenguaje de programación.
* [Django](https://www.djangoproject.com/): Como framework web para agilizar el desarrollo de apis.
* [GIT](https://git-scm.com/): Como herramienta de versionamiento.
* [Hubflow](https://datasift.github.io/gitflow/): Para el manejo de ramas de GIT de manera ordenada (recomendado).
* [PostgreSQL](https://www.postgresql.org/): Como base de datos para almacenar procesos y demases (si se preguntan porqué `postgreSQL`, simplemente es porque me gusta).

## Extras

* [Flake8](https://flake8.pycqa.org/en/latest/): Nos ayuda a mantener el código python ordenado y legible, se puede instalar en la imagen de docker o dentro del computador personal.
* [Draw.io](https://marketplace.visualstudio.com/items?itemName=hediet.vscode-drawio): En caso de que deseemos modelar algunos procesos, lo podemos hacer dentro del mismo proyecto con esta extensión de VsCode.


# Pasos para levantar el proyecto

## Requisitos previos

* Docker
* Docker-compose
* GIT

## Pasos a ejecutar

Una vez clonado el repositorio, dentro del **directorio raíz** del proyecto, ejecutar el comando `docker-compose up`. Esto lo que hará, será levantar los contenedores correspondientes y los dejará listos para su ejecución.

Por defecto la versión de la api se levanta en el puerto `8000` y la base de datos en el puerto `5434` (todo esto es configurable y se verá más adelante).

### Probar la ejecución

Se implementó un endpoint que sirve para verificar que el proyecto esté levantado (un `health_check`). La siguiente petición cUrl debería retornar un `{"status": true}`:

```shell
curl --location --request GET 'http://localhost:8000/api/v1/health-check/'
```

Con esto ok, podemos comenzar con los desarrollos nuevos :rocket:.

## Configuración para desarrollo

Se comentó anteriormente que se pueden configurar los puertos por defecto de los servicios, esto se realiza modificando el archivo `docker-compose.yml` antes de ejecutar el comando para levantar los contenedores.

Una configuración que se puede usar es la siguiente:

```yaml
version: '3'
services:
  db:
    build: ./docker/db
    ports:
      - 5434:5432
    volumes:
      - ./docker/db/data:/var/lib/postgresql/data
  api:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - 8000:8000
    volumes:
      - .:/app
    # command: bash -c "python manage.py runserver 0.0.0.0:8000"
    tty: true
    depends_on:
      - db
```

Como se puede ver, hay una línea comentada, esto lo que hace es que no se ejecute django al iniciar el contenedor, esto es para que dentro de la imagen, nosotros lo ejecutemos y podamos debugear a gusto.

Los puertos se pueden cambiar por los que guste, **considerar que el primero es el puerto que se ve reflejado en el computador local**.

### Acceder al contenedor

Una vez que los contenedores estén levantados, se puede acceder a estos con el siguiente comando (dentro del directorio raíz del proyecto):

```shell
docker-compose exec api bash
```

Consideración: `api` corresponde al identificador de la imagen levantada con python, si se cambian los nombres o se agregan nuevos, se debe acceder por ese identificador (del ejemplo, si queremos acceder al contenedor de la base de datos, sería con `docker-compose exec db bash`).
