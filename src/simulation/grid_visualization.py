import base64
import html
import math
from pathlib import Path

import streamlit.components.v1 as components


def _number(value):
    try:
        value = float(value)
        return max(0.0, value) if math.isfinite(value) else 0.0
    except (TypeError, ValueError):
        return 0.0


def render_grid_animation(
    demand,
    wind,
    solar,
    grid_import,
    battery_charge,
    battery_discharge,
    battery_soc,
    battery_capacity=25000,
    mode="Forecast Heuristic",
    speed=2.5,
    height=760,
):
    """Render a smart-city illustration with animated energy-flow overlays.

    Power values are MW; battery state of charge is MWh. The paths are
    schematic visual connections, not measured transmission routes.
    """
    demand = _number(demand)
    wind = _number(wind)
    solar = _number(solar)
    grid_import = _number(grid_import)
    charge = _number(battery_charge)
    discharge = _number(battery_discharge)
    soc = _number(battery_soc)
    capacity = max(1.0, _number(battery_capacity))
    speed = min(8.0, max(0.5, _number(speed)))

    conventional = str(mode).lower() == "conventional"
    if conventional:
        charge = discharge = 0.0

    soc_pct = min(100.0, soc / capacity * 100.0)
    if conventional:
        status, status_color = "NOT DISPATCHED", "#A8BACB"
    elif discharge > 0:
        status, status_color = "DISCHARGING", "#43D9B5"
    elif charge > 0:
        status, status_color = "CHARGING", "#F4B84A"
    else:
        status, status_color = "IDLE", "#A8BACB"

    project_root = Path(__file__).resolve().parents[2]
    image_path = project_root / "assets" / "smart_city.png"
    if not image_path.exists():
        raise FileNotFoundError(
            f"City illustration not found: {image_path}. "
            "Place smart_city.png in the project's assets directory."
        )
    image_data = base64.b64encode(image_path.read_bytes()).decode("ascii")

    # Schematic routes aligned to the main features in the city illustration.
    # Wind turbines (upper-left) and solar array (lower-left) feed toward
    # the substation (lower-right); the substation supplies the city (right).
    wind_path = "M 180 225 L 440 300 L 790 430 L 1015 345"
    solar_path = "M 210 445 L 440 465 L 790 430 L 1015 365"
    grid_path = "M 855 555 L 930 455 L 1015 385"
    battery_charge_path = "M 590 545 L 735 485 L 855 555"
    battery_discharge_path = "M 855 555 L 930 455 L 1015 385"

    def particles(path, value, scale, color, reverse=False):
        count = min(8, max(0, round(value / scale)))
        if count == 0:
            return ""
        reverse_attrs = ' keyPoints="1;0" keyTimes="0;1"' if reverse else ""
        return "".join(
            f'<circle r="4.2" fill="{color}" filter="url(#softGlow)">'
            f'<animateMotion dur="{speed}s" begin="-{i * speed / count:.2f}s" '
            f'repeatCount="indefinite" path="{path}"{reverse_attrs}/></circle>'
            for i in range(count)
        )

    wind_particles = particles(wind_path, wind, 3500, "#43D9B5")
    solar_particles = particles(solar_path, solar, 1800, "#F4B84A")
    grid_particles = particles(grid_path, grid_import, 18000, "#75B7FF")
    charge_particles = particles(battery_charge_path, charge, 1200, "#75B7FF", True)
    discharge_particles = particles(battery_discharge_path, discharge, 1200, "#43D9B5")

    def label(x, y, title, value, color, anchor="start"):
        return f'''<g class="label" text-anchor="{anchor}">
          <text x="{x}" y="{y}" class="label-title" fill="{color}">{html.escape(title)}</text>
          <text x="{x}" y="{y + 31}" class="label-value">{html.escape(value)}</text>
        </g>'''

    labels = "".join([
        label(75, 145, "WIND GENERATION", f"{wind:,.0f} MW", "#43D9B5"),
        label(75, 535, "SOLAR GENERATION", f"{solar:,.0f} MW", "#F4B84A"),
        label(1120, 255, "CITY DEMAND", f"{demand:,.0f} MW", "#FFFFFF", "end"),
        label(850, 625, "GRID IMPORT", f"{grid_import:,.0f} MW", "#75B7FF"),
    ])

    battery_value = "—" if conventional else f"{soc:,.0f} MWh"
    battery_subtitle = "Not participating" if conventional else f"{soc_pct:.1f}% charged"
    battery_label = f'''<g class="label" text-anchor="middle">
      <text x="620" y="505" class="label-title" fill="#43D9B5">BATTERY STORAGE</text>
      <text x="620" y="536" class="label-value">{battery_value}</text>
      <text x="620" y="562" class="label-sub">{battery_subtitle}</text>
      <text x="620" y="587" class="label-status" fill="{status_color}">{status}</text>
    </g>'''

    mode_text = html.escape(str(mode).upper())
    document = f'''<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
* {{ box-sizing: border-box; }}
html, body {{ margin: 0; padding: 0; width: 100%; background: #071B2D;
  color: #EAF2F8; font-family: Inter, Arial, sans-serif; }}
.scene {{ width: 100%; padding: 14px 14px 12px; background: #071B2D;
  border: 1px solid #1B3A52; border-radius: 14px; }}
.header {{ display:flex; justify-content:space-between; align-items:center;
  gap:12px; padding: 2px 4px 12px; }}
.header strong {{ font-size:17px; letter-spacing:-.2px; }}
.mode {{ color:#43D9B5; font-size:10px; font-weight:800; letter-spacing:1.4px; }}
svg {{ display:block; width:100%; height:auto; border-radius:9px; }}
.label {{ font-family: Inter, Arial, sans-serif; paint-order:stroke; }}
.label-title {{ font-size:17px; font-weight:800; letter-spacing:.6px;
  stroke:#071B2D; stroke-width:5px; stroke-linejoin:round; }}
.label-value {{ font-size:24px; font-weight:750; fill:#FFFFFF;
  stroke:#071B2D; stroke-width:5px; stroke-linejoin:round; }}
.label-sub {{ font-size:15px; font-weight:650; fill:#D6E4EF;
  stroke:#071B2D; stroke-width:4px; stroke-linejoin:round; }}
.label-status {{ font-size:13px; font-weight:800; letter-spacing:1px;
  stroke:#071B2D; stroke-width:4px; stroke-linejoin:round; }}
.legend {{ display:flex; flex-wrap:wrap; justify-content:center; gap:10px 24px;
  padding:13px 4px 1px; color:#B9CADB; font-size:11px; }}
.legend span {{ display:flex; align-items:center; gap:7px; }}
.dot {{ width:8px; height:8px; border-radius:50%; display:inline-block; }}
@media(max-width:650px) {{ .header strong {{font-size:13px;}} .mode {{font-size:8px;}} }}
</style></head><body>
<div class="scene">
  <div class="header"><strong>Smart City Energy Network</strong><span class="mode">{mode_text}</span></div>
  <svg viewBox="0 0 1200 680" preserveAspectRatio="xMidYMid meet"
       xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Smart city energy flows">
    <defs>
      <linearGradient id="shade" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#071B2D" stop-opacity=".08"/>
        <stop offset="1" stop-color="#071B2D" stop-opacity=".22"/>
      </linearGradient>
      <filter id="softGlow" x="-100%" y="-100%" width="300%" height="300%">
        <feGaussianBlur stdDeviation="2.4" result="blur"/>
        <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
      </filter>
      <marker id="arrowWind" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0L6 3L0 6" fill="#43D9B5"/></marker>
      <marker id="arrowSolar" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0L6 3L0 6" fill="#F4B84A"/></marker>
      <marker id="arrowGrid" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0L6 3L0 6" fill="#75B7FF"/></marker>
    </defs>
    <image href="data:image/png;base64,{image_data}" x="0" y="0" width="1200" height="680" preserveAspectRatio="xMidYMid slice"/>
    <rect width="1200" height="680" fill="url(#shade)"/>
    <g fill="none" stroke-linecap="round" stroke-linejoin="round">
      <path d="{wind_path}" stroke="#43D9B5" stroke-width="9" opacity=".13"/>
      <path d="{wind_path}" stroke="#43D9B5" stroke-width="2.8" opacity=".72" marker-end="url(#arrowWind)"/>
      <path d="{solar_path}" stroke="#F4B84A" stroke-width="9" opacity=".13"/>
      <path d="{solar_path}" stroke="#F4B84A" stroke-width="2.8" opacity=".72" marker-end="url(#arrowSolar)"/>
      <path d="{grid_path}" stroke="#75B7FF" stroke-width="9" opacity=".13"/>
      <path d="{grid_path}" stroke="#75B7FF" stroke-width="2.8" opacity=".72" marker-end="url(#arrowGrid)"/>
      <path d="{battery_charge_path}" stroke="#75B7FF" stroke-width="2.5" stroke-dasharray="7 8" opacity="{'.7' if charge and not conventional else '.12'}"/>
      <path d="{battery_discharge_path}" stroke="#43D9B5" stroke-width="2.5" stroke-dasharray="7 8" opacity="{'.7' if discharge and not conventional else '.12'}"/>
    </g>
    <g>{wind_particles}{solar_particles}{grid_particles}{charge_particles}{discharge_particles}</g>
    {labels}
    {battery_label}
  </svg>
  <div class="legend">
    <span><i class="dot" style="background:#43D9B5"></i>Wind / battery discharge</span>
    <span><i class="dot" style="background:#F4B84A"></i>Solar generation</span>
    <span><i class="dot" style="background:#75B7FF"></i>Grid / battery charging</span>
  </div>
</div></body></html>'''

    components.html(document, height=height, scrolling=False)
