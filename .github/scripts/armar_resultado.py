#!/usr/bin/env python3
"""Arma `resultado.json` (esquema 1) para Solbeet Run a partir de los reportes de las pruebas.

Lo llama `.github/workflows/solbeet-run-verificacion.yml` (autoprueba por cambio). Run no
ejecuta código del cliente: dispara ese workflow, baja el artefacto con este archivo y decide
con reglas. Acá solo se informan cifras; el veredicto no se da en este script.

Fuentes (todas opcionales; la que falta no se inventa):

- `--junit`: JUnit XML de pytest sobre `tests/aceptacion/` (el id del criterio sale del
  nombre `test_ca_<issue>_<n>_...`).
- `--playwright`: reporte JSON de Playwright (el id sale del tag `@CA-<issue>-<n>`).
- `--zap-json`: reporte JSON de `zap-baseline.py -J`.

Sin ninguna fuente de e2e, la sección queda `ausente` con el motivo: Run lo trata como «sin
evidencia», nunca como verde. Solo biblioteca estándar.
"""

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

SCHEMA = 1
MAX_FALLOS = 10
_ID_PYTEST = re.compile(r"test_ca_(\d+)_(\d+)", re.IGNORECASE)
_ID_TAG = re.compile(r"@?CA-(\d+)-(\d+)", re.IGNORECASE)
_ANSI = re.compile(r"\x1b\[[0-9;]*m")
_RIESGO_ZAP = {"3": "alta", "2": "media", "1": "baja", "0": "informativa"}


def _corto(texto: str, maximo: int) -> str:
    limpio = _ANSI.sub("", texto or "").strip()
    return limpio if len(limpio) <= maximo else limpio[: maximo - 1] + "…"


def _seccion() -> dict[str, Any]:
    return {"total": 0, "pasaron": 0, "fallaron": 0, "omitidos": 0, "criterios": set(), "fallos": []}


def _fallo(s: dict[str, Any], criterio: str, test: str, mensaje: str) -> None:
    s["fallaron"] += 1
    s["total"] += 1
    s["fallos"].append(
        {"criterio": criterio, "test": _corto(test, 300), "mensaje": _corto(mensaje, 2000)}
    )


def leer_junit(ruta: Path) -> dict[str, Any]:
    """Cuenta los casos del JUnit XML de pytest. Un error de colección cuenta como falla."""
    s = _seccion()
    for caso in ET.parse(ruta).getroot().iter("testcase"):
        nombre = caso.get("name", "")
        m = _ID_PYTEST.search(nombre) or _ID_PYTEST.search(caso.get("classname", ""))
        criterio = f"CA-{m.group(1)}-{m.group(2)}" if m else ""
        malo = caso.find("failure")
        if malo is None:
            malo = caso.find("error")
        if malo is not None:
            _fallo(s, criterio, nombre, malo.get("message") or (malo.text or ""))
        elif caso.find("skipped") is not None:
            s["omitidos"] += 1
            s["total"] += 1
        else:
            s["pasaron"] += 1
            s["total"] += 1
            if criterio:
                s["criterios"].add(criterio)
    return s


def _specs_playwright(suite: dict[str, Any]) -> Any:
    yield from suite.get("specs", [])
    for hija in suite.get("suites", []):
        yield from _specs_playwright(hija)


def leer_playwright(ruta: Path) -> dict[str, Any]:
    """Cuenta los tests del reporte JSON de Playwright (cada proyecto/tamaño cuenta aparte)."""
    s = _seccion()
    crudo = json.loads(ruta.read_text(encoding="utf-8"))
    for suite in crudo.get("suites", []):
        for spec in _specs_playwright(suite):
            titulo = spec.get("title", "")
            m = _ID_TAG.search(titulo) or next(
                (x for t in spec.get("tags", []) if (x := _ID_TAG.search(t))), None
            )
            criterio = f"CA-{m.group(1)}-{m.group(2)}" if m else ""
            for prueba in spec.get("tests", []):
                estado = prueba.get("status")
                if estado == "skipped":
                    s["omitidos"] += 1
                    s["total"] += 1
                elif estado in ("expected", "flaky"):
                    s["pasaron"] += 1
                    s["total"] += 1
                    if criterio:
                        s["criterios"].add(criterio)
                else:
                    resultados = prueba.get("results") or [{}]
                    error = (resultados[-1].get("error") or {}).get("message", "")
                    _fallo(s, criterio, titulo, error or f"estado {estado}")
    return s


def combinar(partes: list[dict[str, Any]]) -> dict[str, Any]:
    """Suma las secciones de e2e de varias fuentes."""
    total = _seccion()
    for p in partes:
        for k in ("total", "pasaron", "fallaron", "omitidos"):
            total[k] += p[k]
        total["criterios"] |= p["criterios"]
        total["fallos"] += p["fallos"]
    return total


def seccion_e2e(junit: Path | None, playwright: Path | None) -> dict[str, Any]:
    """Sección `e2e`: `corrio` si alguna fuente dejó reporte, si no `ausente` con el motivo."""
    partes: list[dict[str, Any]] = []
    motivos: list[str] = []
    for nombre, ruta, leer in (
        ("pytest (tests/aceptacion)", junit, leer_junit),
        ("Playwright (e2e/)", playwright, leer_playwright),
    ):
        if ruta is None or not ruta.is_file():
            motivos.append(f"{nombre}: sin reporte")
            continue
        try:
            partes.append(leer(ruta))
        except (ET.ParseError, json.JSONDecodeError, OSError) as exc:
            motivos.append(f"{nombre}: reporte ilegible ({_corto(str(exc), 80)})")
    if not partes:
        return {
            "estado": "ausente",
            "motivo": _corto(
                "no hay pruebas de aceptación que hayan corrido (" + "; ".join(motivos) + ")", 300
            ),
        }
    t = combinar(partes)
    return {
        "estado": "corrio",
        "total": t["total"],
        "pasaron": t["pasaron"],
        "fallaron": t["fallaron"],
        "omitidos": t["omitidos"],
        "criterios": sorted(t["criterios"])[:200],
        "fallos": t["fallos"][:MAX_FALLOS],
    }


def seccion_zap(ruta: Path | None) -> dict[str, Any]:
    """Sección `zap` desde el JSON de zap-baseline (`riskcode` 3 alta ... 0 informativa)."""
    if ruta is None or not ruta.is_file():
        return {"estado": "ausente", "motivo": "ZAP baseline no dejó reporte"}
    try:
        crudo = json.loads(ruta.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return {"estado": "ausente", "motivo": _corto(f"reporte de ZAP ilegible ({exc})", 300)}
    alertas = {"alta": 0, "media": 0, "baja": 0, "informativa": 0}
    altas: list[dict[str, str]] = []
    for sitio in crudo.get("site", []):
        for a in sitio.get("alerts", []):
            nivel = _RIESGO_ZAP.get(str(a.get("riskcode")), "informativa")
            alertas[nivel] += 1
            if nivel == "alta" and len(altas) < 200:
                instancias = a.get("instances") or [{}]
                altas.append(
                    {
                        "nombre": _corto(a.get("name") or a.get("alert", ""), 200),
                        "ruta": _corto(instancias[0].get("uri", ""), 300),
                    }
                )
    return {"estado": "corrio", "alertas": alertas, "altas": altas}


def armar(
    *,
    base_url: str,
    ref: str,
    e2e: bool,
    zap: bool,
    junit: Path | None = None,
    playwright: Path | None = None,
    zap_json: Path | None = None,
) -> dict[str, Any]:
    """`resultado.json` completo; solo incluye las secciones que el ambiente declaró."""
    r: dict[str, Any] = {"schema": SCHEMA, "base_url": base_url.rstrip("/"), "ref": ref}
    if e2e:
        r["e2e"] = seccion_e2e(junit, playwright)
    if zap:
        r["zap"] = seccion_zap(zap_json)
    return r


def _bool(valor: str) -> bool:
    return valor.strip().lower() == "true"


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--base-url", required=True)
    p.add_argument("--ref", required=True)
    p.add_argument("--e2e", default="false")
    p.add_argument("--zap", default="false")
    p.add_argument("--junit", type=Path)
    p.add_argument("--playwright", type=Path)
    p.add_argument("--zap-json", type=Path)
    p.add_argument("--salida", type=Path, default=Path("resultado.json"))
    a = p.parse_args(argv)
    r = armar(
        base_url=a.base_url,
        ref=a.ref,
        e2e=_bool(a.e2e),
        zap=_bool(a.zap),
        junit=a.junit,
        playwright=a.playwright,
        zap_json=a.zap_json,
    )
    a.salida.write_text(json.dumps(r, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"resultado.json: e2e={r.get('e2e', {}).get('estado', 'no declarado')}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
