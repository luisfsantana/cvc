## Tecnologia

- Linguagem: Python 3
- Servidor: Gunicorn
- Framework: Falcon
- Armazenamento: PostgreSQL 

## Instar

Para instalar execute *install.sh*, na raiz do projeto.


## Rodar

Para criar o banco de dados execute *install-db.sh*.

Para iniciar o servico execute `./main-app.sh`. A porta usada sera a  8000.


### Endpoints

#### /

Mostra a saude e os endpoints

#### /titulo_tesouro

Used by the first four functionalities described.

###### 1. POST /titulo_tesouro

**Request body:**

```json
{
    "categoria_titulo": "NTN-B",
    "mês": 4,
    "ano": 2017,
    "ação": "venda",
    "valor": 15321.99
}
```
**Response body:**

```json
{
    "success": {
        "id": <NEXT_INTEGER>
        "categoria_titulo": "NTN-B",
        "mês": 4,
        "ano": 2017,
        "ação": "venda",
        "valor": 15321.99
    }
}
```

or

```json
{
    "err": <error>
}
```

###### 2. DELETE /titulo_tesouro/{id}

**Response body:**

```json
{
  "success": "Deleted."
}
```

or

```json
{
  "err": "\"titulo_id\" has no register."
}
```

###### 3. PUT /titulo_tesouro/{id}

###### 4. GET /titulo_tesouro/{id}

**Parametros:**

- data_inicio (optional): in the format **YYYY-mm**
- data_fim (optional): in the format **YYYY-mm**
- group_by (optional): boolean

###### 5. GET /titulo_tesouro/comparar/

###### 6. GET /titulos_tesouro/venda/{id} and 7. GET /titulos_tesouro/resgate/{id}

**Response body:** for path **titulo_tesouro/venda/1488?data_inicio=2014-05&data_fim=2016-09**

```json
{
    "success": {
        "id": 1488,
        "categoria_titulo": "NTN-F",
        "valores_venda": [
            {
                "valor": "R$16.540.000,00",
                "mes": 5,
                "ano": 2014
            },
            ...
            {
                "valor": "R$17.000.000,00",
                "mes": 4,
                "ano": 2016
            }
        ]
    }
}
```

## Testing

Para testar execute o scrip *tests.sh*.
