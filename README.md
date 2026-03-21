# Scraper Liga Cántabra de Pádel 2026

Extrae partidos y clasificaciones de la web de la Federación Cántabra de Pádel y genera archivos JSON y CSV.

## Instalación

```bash
pip install -r requirements.txt
```

## Uso

```bash
# Scrape TODOS los grupos (tarda ~2-3 minutos)
python scraper_liga_cantabra.py

# Solo un grupo específico
python scraper_liga_cantabra.py --grupo 31269

# Solo masculino
python scraper_liga_cantabra.py --genero M

# Solo una categoría (ej: 6ª categoría)
python scraper_liga_cantabra.py --categoria 6

# Cambiar directorio de salida
python scraper_liga_cantabra.py --output datos
```

## Archivos generados

```
output/
├── liga_cantabra_2026.json   # Todo en un JSON (partidos + clasificación por grupo)
├── partidos.csv              # Todos los partidos en formato tabular
└── clasificacion.csv         # Clasificación de todos los grupos
```

## Estructura del JSON

```json
{
  "liga": "Liga Cántabra de Pádel 2026",
  "liga_id": "28074",
  "fecha_scrape": "2026-03-18T...",
  "grupos": {
    "31269": {
      "info": {
        "genero": "M",
        "categoria": 6,
        "grupo": "B",
        "label": "6ª CATEGORÍA MASCULINA - GRUPO B"
      },
      "partidos": [
        {
          "equipo_local": "P.A.G. ASTILLERO GUARNIZO B",
          "equipo_visitante": "BATHCO PADEL TEAM ATP C",
          "estado": "pendiente",
          "fecha_texto": "27 - 29 Mar",
          "resultado": null
        },
        {
          "equipo_local": "P.A.G. ASTILLERO GUARNIZO B",
          "equipo_visitante": "C.D. SALAS C",
          "estado": "jugado",
          "resultado": "5/0",
          "resultado_local": 5,
          "resultado_visitante": 0
        }
      ],
      "clasificacion": [
        {
          "posicion": 1,
          "equipo": "BATHCO PADEL TEAM ATP C",
          "puntos": 8,
          "enfrentamientos_disputados": 8,
          "partidos_ganados": 28,
          "sets_favor": 55,
          "sets_contra": 31
        }
      ]
    }
  }
}
```

## Estructura del CSV de partidos

| Campo | Descripción |
|-------|-------------|
| grupo_id | ID interno del grupo |
| grupo_label | Nombre legible (ej: "6ª CATEGORÍA MASCULINA - GRUPO B") |
| genero | M o F |
| categoria | 1-6 |
| grupo_letra | A, B, C... |
| equipo_local | Nombre del equipo local |
| equipo_visitante | Nombre del equipo visitante |
| estado | "jugado" o "pendiente" |
| resultado | "5/0", "3/2", etc. (solo si jugado) |
| resultado_local | Partidos ganados por local (solo si jugado) |
| resultado_visitante | Partidos ganados por visitante (solo si jugado) |
| fecha_texto | "27 - 29 Mar" (solo si pendiente) |

## IDs de grupos

### Masculino
| ID | Categoría |
|----|-----------|
| 31249 | 1ª Cat - Grupo A |
| 31256 | 1ª Cat - Grupo B |
| 31250 | 2ª Cat - Grupo A |
| 31257 | 2ª Cat - Grupo B |
| 31258 | 2ª Cat - Grupo C |
| 31251 | 3ª Cat - Grupo A |
| 31259 | 3ª Cat - Grupo B |
| 31260 | 3ª Cat - Grupo C |
| 31261 | 3ª Cat - Grupo D |
| 31254 | 4ª Cat - Grupo A |
| 31262 | 4ª Cat - Grupo B |
| 31263 | 4ª Cat - Grupo C |
| 31264 | 4ª Cat - Grupo D |
| 31255 | 5ª Cat - Grupo A |
| 31265 | 5ª Cat - Grupo B |
| 31266 | 5ª Cat - Grupo C |
| 31267 | 5ª Cat - Grupo D |
| 31268 | 6ª Cat - Grupo A |
| 31269 | 6ª Cat - Grupo B |
| 31270 | 6ª Cat - Grupo C |
| 31369 | 6ª Cat - Grupo D |
| 31344 | 6ª Cat - Grupo E |
| 31377 | 6ª Cat - Grupo F |

### Femenino
| ID | Categoría |
|----|-----------|
| 31247 | 1ª Cat - Grupo A |
| 31271 | 1ª Cat - Grupo B |
| 31248 | 2ª Cat - Grupo A |
| 31272 | 2ª Cat - Grupo B |
| 31273 | 2ª Cat - Grupo C |
| 31252 | 3ª Cat - Grupo A |
| 31274 | 3ª Cat - Grupo B |
| 31275 | 3ª Cat - Grupo C |
| 31253 | 4ª Cat - Grupo A |
| 31276 | 4ª Cat - Grupo B |
| 31277 | 4ª Cat - Grupo C |
| 31278 | 5ª Cat - Grupo A |
| 31279 | 5ª Cat - Grupo B |
| 31280 | 5ª Cat - Grupo C |
| 31341 | 5ª Cat - Grupo D |

## Cómo funciona

La web de la federación usa un formulario POST clásico (sin API REST):

```
POST https://federacioncantabradepadel.com/Liga_Calendario
Content-Type: application/x-www-form-urlencoded

id=28074&genero=M&fase=1&grupo=31269&jornada=--
```

El servidor devuelve HTML con una tabla grid (Local vs Visitante) y una tabla de clasificación. El scraper parsea ambas tablas con BeautifulSoup.
