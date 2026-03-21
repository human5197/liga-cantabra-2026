#!/usr/bin/env python3
"""
Scraper - Liga Cántabra de Pádel 2026
======================================
Extrae partidos y clasificaciones de federacioncantabradepadel.com
y genera archivos JSON y CSV listos para usar en una interfaz.

Uso:
  python scraper_liga_cantabra.py                    # Scrape todos los grupos
  python scraper_liga_cantabra.py --grupo 31269      # Scrape un grupo específico
  python scraper_liga_cantabra.py --genero M         # Solo masculino
  python scraper_liga_cantabra.py --categoria 6      # Solo 6ª categoría
"""

import requests
from bs4 import BeautifulSoup
import json
import csv
import os
import re
import argparse
from datetime import datetime

# ============================================================
# CONFIGURACIÓN
# ============================================================

LIGA_ID = "28074"  # Liga Cántabra 2026
BASE_URL = "https://federacioncantabradepadel.com/Liga_Calendario"

GRUPOS = {
    # FEMENINO
    "31247": {"genero": "F", "categoria": 1, "grupo": "A", "label": "1ª CATEGORÍA FEMENINA - GRUPO A"},
    "31271": {"genero": "F", "categoria": 1, "grupo": "B", "label": "1ª CATEGORÍA FEMENINA - GRUPO B"},
    "31248": {"genero": "F", "categoria": 2, "grupo": "A", "label": "2ª CATEGORÍA FEMENINA - GRUPO A"},
    "31272": {"genero": "F", "categoria": 2, "grupo": "B", "label": "2ª CATEGORÍA FEMENINA - GRUPO B"},
    "31273": {"genero": "F", "categoria": 2, "grupo": "C", "label": "2ª CATEGORÍA FEMENINA - GRUPO C"},
    "31252": {"genero": "F", "categoria": 3, "grupo": "A", "label": "3ª CATEGORÍA FEMENINA - GRUPO A"},
    "31274": {"genero": "F", "categoria": 3, "grupo": "B", "label": "3ª CATEGORÍA FEMENINA - GRUPO B"},
    "31275": {"genero": "F", "categoria": 3, "grupo": "C", "label": "3ª CATEGORÍA FEMENINA - GRUPO C"},
    "31253": {"genero": "F", "categoria": 4, "grupo": "A", "label": "4ª CATEGORÍA FEMENINA - GRUPO A"},
    "31276": {"genero": "F", "categoria": 4, "grupo": "B", "label": "4ª CATEGORÍA FEMENINA - GRUPO B"},
    "31277": {"genero": "F", "categoria": 4, "grupo": "C", "label": "4ª CATEGORÍA FEMENINA - GRUPO C"},
    "31278": {"genero": "F", "categoria": 5, "grupo": "A", "label": "5ª CATEGORÍA FEMENINA - GRUPO A"},
    "31279": {"genero": "F", "categoria": 5, "grupo": "B", "label": "5ª CATEGORÍA FEMENINA - GRUPO B"},
    "31280": {"genero": "F", "categoria": 5, "grupo": "C", "label": "5ª CATEGORÍA FEMENINA - GRUPO C"},
    "31341": {"genero": "F", "categoria": 5, "grupo": "D", "label": "5ª CATEGORÍA FEMENINA - GRUPO D"},
    # MASCULINO
    "31249": {"genero": "M", "categoria": 1, "grupo": "A", "label": "1ª CATEGORÍA MASCULINA - GRUPO A"},
    "31256": {"genero": "M", "categoria": 1, "grupo": "B", "label": "1ª CATEGORÍA MASCULINA - GRUPO B"},
    "31250": {"genero": "M", "categoria": 2, "grupo": "A", "label": "2ª CATEGORÍA MASCULINA - GRUPO A"},
    "31257": {"genero": "M", "categoria": 2, "grupo": "B", "label": "2ª CATEGORÍA MASCULINA - GRUPO B"},
    "31258": {"genero": "M", "categoria": 2, "grupo": "C", "label": "2ª CATEGORÍA MASCULINA - GRUPO C"},
    "31251": {"genero": "M", "categoria": 3, "grupo": "A", "label": "3ª CATEGORÍA MASCULINA - GRUPO A"},
    "31259": {"genero": "M", "categoria": 3, "grupo": "B", "label": "3ª CATEGORÍA MASCULINA - GRUPO B"},
    "31260": {"genero": "M", "categoria": 3, "grupo": "C", "label": "3ª CATEGORÍA MASCULINA - GRUPO C"},
    "31261": {"genero": "M", "categoria": 3, "grupo": "D", "label": "3ª CATEGORÍA MASCULINA - GRUPO D"},
    "31254": {"genero": "M", "categoria": 4, "grupo": "A", "label": "4ª CATEGORÍA MASCULINA - GRUPO A"},
    "31262": {"genero": "M", "categoria": 4, "grupo": "B", "label": "4ª CATEGORÍA MASCULINA - GRUPO B"},
    "31263": {"genero": "M", "categoria": 4, "grupo": "C", "label": "4ª CATEGORÍA MASCULINA - GRUPO C"},
    "31264": {"genero": "M", "categoria": 4, "grupo": "D", "label": "4ª CATEGORÍA MASCULINA - GRUPO D"},
    "31255": {"genero": "M", "categoria": 5, "grupo": "A", "label": "5ª CATEGORÍA MASCULINA - GRUPO A"},
    "31265": {"genero": "M", "categoria": 5, "grupo": "B", "label": "5ª CATEGORÍA MASCULINA - GRUPO B"},
    "31266": {"genero": "M", "categoria": 5, "grupo": "C", "label": "5ª CATEGORÍA MASCULINA - GRUPO C"},
    "31267": {"genero": "M", "categoria": 5, "grupo": "D", "label": "5ª CATEGORÍA MASCULINA - GRUPO D"},
    "31268": {"genero": "M", "categoria": 6, "grupo": "A", "label": "6ª CATEGORÍA MASCULINA - GRUPO A"},
    "31269": {"genero": "M", "categoria": 6, "grupo": "B", "label": "6ª CATEGORÍA MASCULINA - GRUPO B"},
    "31270": {"genero": "M", "categoria": 6, "grupo": "C", "label": "6ª CATEGORÍA MASCULINA - GRUPO C"},
    "31369": {"genero": "M", "categoria": 6, "grupo": "D", "label": "6ª CATEGORÍA MASCULINA - GRUPO D"},
    "31344": {"genero": "M", "categoria": 6, "grupo": "E", "label": "6ª CATEGORÍA MASCULINA - GRUPO E"},
    "31377": {"genero": "M", "categoria": 6, "grupo": "F", "label": "6ª CATEGORÍA MASCULINA - GRUPO F"},
}


# ============================================================
# SCRAPER
# ============================================================

def fetch_grupo(grupo_id: str) -> BeautifulSoup:
    """Hace el POST y devuelve el HTML parseado."""
    info = GRUPOS[grupo_id]
    data = {
        "id": LIGA_ID,
        "genero": info["genero"],
        "fase": "1",
        "grupo": grupo_id,
        "jornada": "--",
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://federacioncantabradepadel.com",
        "Referer": f"https://federacioncantabradepadel.com/Liga_Calendario?id={LIGA_ID}",
    }
    resp = requests.post(BASE_URL, data=data, headers=headers, timeout=30)
    resp.encoding = "utf-8"
    return BeautifulSoup(resp.text, "html.parser")


def parse_partidos(soup: BeautifulSoup, grupo_id: str) -> list[dict]:
    """
    Parsea la tabla grid de Local/Visitante.
    Cada celda contiene un resultado (ej: '5/0') o una fecha pendiente (ej: '27 - 29 Mar').
    """
    partidos = []
    info = GRUPOS[grupo_id]

    # Buscar la tabla grid (la primera tabla grande con class estiloequipos)
    tables = soup.find_all("table", attrs={"width": "100%", "border": "0"})
    grid_table = None
    for t in tables:
        if t.find("td", class_="estiloequipos"):
            grid_table = t
            break

    if not grid_table:
        return partidos

    rows = grid_table.find_all("tr")
    if not rows:
        return partidos

    # Primera fila = cabecera con nombres de equipos visitantes
    header_cells = rows[0].find_all("td", class_="estiloequipos")
    # El primer td es "Local/Visitante", los demás son nombres de equipos
    equipos_visitante = [td.get_text(strip=True) for td in header_cells[1:]]

    # Filas siguientes = cada fila es un equipo local
    for row in rows[1:]:
        cells = row.find_all("td")
        if not cells:
            continue

        # Primera celda = nombre del equipo local
        equipo_local_cell = cells[0]
        if "estiloequipos" not in equipo_local_cell.get("class", []):
            continue
        equipo_local = equipo_local_cell.get_text(strip=True)

        # Resto de celdas = resultados contra cada equipo visitante
        data_cells = cells[1:]
        for i, cell in enumerate(data_cells):
            if i >= len(equipos_visitante):
                break

            equipo_visitante = equipos_visitante[i]
            cell_class = " ".join(cell.get("class", []))
            cell_text = cell.get_text(strip=True)

            # Saltar la diagonal (mismo equipo)
            if "nulo" in cell_class or not cell_text:
                continue

            partido = {
                "grupo_id": grupo_id,
                "grupo_label": info["label"],
                "genero": info["genero"],
                "categoria": info["categoria"],
                "grupo_letra": info["grupo"],
                "equipo_local": equipo_local,
                "equipo_visitante": equipo_visitante,
            }

            # Determinar el estado del partido
            links = cell.find_all("a")

            if "cerrados" in cell_class:
                # Partido jugado - tiene resultado
                resultado_link = links[0] if links else None
                if resultado_link:
                    resultado_text = resultado_link.get_text(strip=True)
                    match = re.match(r"(\d+)/(\d+)", resultado_text)
                    if match:
                        partido["resultado_local"] = int(match.group(1))
                        partido["resultado_visitante"] = int(match.group(2))
                        partido["resultado"] = resultado_text

                    # URL del resultado
                    href = resultado_link.get("href", "")
                    if href:
                        partido["url_resultado"] = f"https://federacioncantabradepadel.com/{href}"

                # URL del acta
                acta_link = cell.find("a", string=re.compile("Acta", re.I))
                if acta_link:
                    partido["url_acta"] = f"https://federacioncantabradepadel.com/{acta_link.get('href', '')}"

                partido["estado"] = "jugado"

            elif "cercanos" in cell_class or "abiertos" in cell_class:
                # Partido pendiente - tiene fecha
                fecha_link = links[0] if links else None
                if fecha_link:
                    partido["fecha_texto"] = fecha_link.get_text(strip=True)
                    href = fecha_link.get("href", "")
                    if href:
                        partido["url_horario"] = f"https://federacioncantabradepadel.com/{href}"

                partido["estado"] = "pendiente"

            elif "ultima" in cell_class:
                # Última jornada pendiente
                fecha_link = links[0] if links else None
                if fecha_link:
                    partido["fecha_texto"] = fecha_link.get_text(strip=True)
                    href = fecha_link.get("href", "")
                    if href:
                        partido["url_horario"] = f"https://federacioncantabradepadel.com/{href}"

                partido["estado"] = "pendiente"
            else:
                partido["estado"] = "desconocido"
                partido["cell_text"] = cell_text

            partidos.append(partido)

    return partidos


def parse_clasificacion(soup: BeautifulSoup, grupo_id: str) -> list[dict]:
    """Parsea la tabla de clasificación."""
    clasificacion = []
    info = GRUPOS[grupo_id]

    # Buscar la tabla con class "table"
    tabla = soup.find("table", class_="table")
    if not tabla:
        return clasificacion

    rows = tabla.find_all("tr", class_="lineas")
    for row in rows:
        cells = row.find_all("td")
        if len(cells) < 12:
            continue

        equipo_link = cells[1].find("a")
        equipo_nombre = equipo_link.get_text(strip=True) if equipo_link else cells[1].get_text(strip=True)
        equipo_url = ""
        if equipo_link and equipo_link.get("href"):
            equipo_url = f"https://federacioncantabradepadel.com/{equipo_link['href']}"

        entry = {
            "grupo_id": grupo_id,
            "grupo_label": info["label"],
            "genero": info["genero"],
            "categoria": info["categoria"],
            "grupo_letra": info["grupo"],
            "posicion": int(cells[0].get_text(strip=True) or 0),
            "equipo": equipo_nombre,
            "equipo_url": equipo_url,
            "enfrentamientos_disputados": int(cells[2].get_text(strip=True) or 0),
            "puntos": int(cells[3].get_text(strip=True) or 0),
            "partidos_disputados": int(cells[4].get_text(strip=True) or 0),
            "partidos_ganados": int(cells[5].get_text(strip=True) or 0),
            "sets_favor": int(cells[6].get_text(strip=True) or 0),
            "sets_contra": int(cells[7].get_text(strip=True) or 0),
            "average_sets": int(cells[8].get_text(strip=True) or 0),
            "juegos_favor": int(cells[9].get_text(strip=True) or 0),
            "juegos_contra": int(cells[10].get_text(strip=True) or 0),
            "average_juegos": int(cells[11].get_text(strip=True) or 0),
        }
        clasificacion.append(entry)

    return clasificacion


# ============================================================
# EXPORTACIÓN
# ============================================================

def save_json(data: dict, filepath: str):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  ✅ {filepath}")


def save_csv(rows: list[dict], filepath: str):
    if not rows:
        return
    all_keys = dict.fromkeys(k for row in rows for k in row.keys())
    with open(filepath, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=all_keys, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    print(f"  ✅ {filepath}")


# ============================================================
# MAIN
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="Scraper Liga Cántabra de Pádel 2026")
    parser.add_argument("--grupo", type=str, help="ID de un grupo específico (ej: 31269)")
    parser.add_argument("--genero", type=str, choices=["M", "F"], help="Solo masculino (M) o femenino (F)")
    parser.add_argument("--categoria", type=int, help="Solo una categoría (1-6)")
    parser.add_argument("--output", type=str, default="output", help="Directorio de salida (default: output)")
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)

    # Filtrar grupos
    grupos_to_scrape = dict(GRUPOS)
    if args.grupo:
        grupos_to_scrape = {args.grupo: GRUPOS[args.grupo]}
    else:
        if args.genero:
            grupos_to_scrape = {k: v for k, v in grupos_to_scrape.items() if v["genero"] == args.genero}
        if args.categoria:
            grupos_to_scrape = {k: v for k, v in grupos_to_scrape.items() if v["categoria"] == args.categoria}

    all_partidos = []
    all_clasificacion = []
    resultados_por_grupo = {}

    total = len(grupos_to_scrape)
    print(f"\n🏓 Scrapeando {total} grupos de la Liga Cántabra de Pádel 2026\n")

    for i, (grupo_id, info) in enumerate(grupos_to_scrape.items(), 1):
        print(f"[{i}/{total}] {info['label']}...")

        try:
            soup = fetch_grupo(grupo_id)
            partidos = parse_partidos(soup, grupo_id)
            clasificacion = parse_clasificacion(soup, grupo_id)

            all_partidos.extend(partidos)
            all_clasificacion.extend(clasificacion)

            resultados_por_grupo[grupo_id] = {
                "info": info,
                "partidos": partidos,
                "clasificacion": clasificacion,
            }

            jugados = sum(1 for p in partidos if p["estado"] == "jugado")
            pendientes = sum(1 for p in partidos if p["estado"] == "pendiente")
            print(f"         → {jugados} jugados, {pendientes} pendientes, {len(clasificacion)} equipos en clasificación")

        except Exception as e:
            print(f"         ❌ Error: {e}")

    # Guardar JSON completo
    output_data = {
        "liga": "Liga Cántabra de Pádel 2026",
        "liga_id": LIGA_ID,
        "fecha_scrape": datetime.now().isoformat(),
        "grupos": resultados_por_grupo,
        "resumen": {
            "total_grupos": len(grupos_to_scrape),
            "total_partidos": len(all_partidos),
            "partidos_jugados": sum(1 for p in all_partidos if p["estado"] == "jugado"),
            "partidos_pendientes": sum(1 for p in all_partidos if p["estado"] == "pendiente"),
            "total_equipos_clasificacion": len(all_clasificacion),
        },
    }

    print(f"\n📁 Guardando en {args.output}/\n")
    save_json(output_data, os.path.join(args.output, "liga_cantabra_2026.json"))
    save_csv(all_partidos, os.path.join(args.output, "partidos.csv"))
    save_csv(all_clasificacion, os.path.join(args.output, "clasificacion.csv"))

    # Resumen
    r = output_data["resumen"]
    print(f"\n📊 Resumen:")
    print(f"   Grupos scrapeados: {r['total_grupos']}")
    print(f"   Partidos totales:  {r['total_partidos']}")
    print(f"   Jugados:           {r['partidos_jugados']}")
    print(f"   Pendientes:        {r['partidos_pendientes']}")
    print(f"   Equipos:           {r['total_equipos_clasificacion']}")
    print()


if __name__ == "__main__":
    main()
