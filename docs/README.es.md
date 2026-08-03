# Bucle cuantitativo de frecuencia media-baja para acciones A

Un flujo semanal de investigación para acciones A: medir primero, descartar evidencia débil y actuar solo cuando las reglas coinciden.

[English](../README.md) | [Español](README.es.md) | [简体中文](README.zh-CN.md)

> Solo para investigación y apoyo a decisiones. No conecta con brókers ni envía órdenes.

## Idea central

El proyecto convierte una revisión semanal en un proceso auditable:

1. Mide la semana desde la primera apertura real hasta el último cierre real.
2. Verifica precio, volumen, fecha y acuerdo entre fuentes antes de interpretar.
3. Tras los controles de riesgo, da prioridad a la evidencia histórica BOLL; después revisa precio-volumen, flujos de 5/10/20 días, comunicados y contexto macro.
4. Una narrativa sin fuente verificable y fechada no es una razón de trading.
5. Una revisión solo puede usar información pública antes de `evidence_cutoff`; un anuncio posterior es un evento nuevo, no una predicción fallida del informe anterior.

## Inicio rápido

```bash
git clone https://github.com/marqosjiang-gif/A-Share-Antifragile-Trading-Loop.git
cd A-Share-Antifragile-Trading-Loop
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt

cp watchlist.example.json watchlist.local.json
python3 quant_loop.py --watchlist watchlist.local.json
```

Configure solo sus propios símbolos en `watchlist.local.json`. El archivo está ignorado por Git: no incluya posiciones, costes, cuentas ni credenciales.

## Límites

La salida es un andamiaje de investigación con estado `research_only`. Las decisiones reales requieren datos actuales verificados y las restricciones de riesgo del usuario. No publique listas personales, posiciones, informes generados, cachés, correos electrónicos, tokens o claves API.

Reglas completas: [`PUBLIC_PROTOCOL.md`](../PUBLIC_PROTOCOL.md).

## Licencia

[MIT License](../LICENSE)
