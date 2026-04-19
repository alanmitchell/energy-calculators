"""Indoor relative humidity calculator page."""

import psychrolib

from matplotlib import pyplot as plt
import matplotlib.ticker as mtick
from nicegui import ui
from nicegui.events import ValueChangeEventArguments

psychrolib.SetUnitSystem(psychrolib.IP)

SEA_LEVEL_PRESSURE_PSI: float = 14.696  # psi


def altitude_to_p_atm(altitude_ft: float) -> float:
    """Return atmospheric pressure in psi for a given altitude in feet."""
    altitude_m: float = altitude_ft * 0.3048
    pressure_pa: float = 101325.0 * (1.0 - 2.25577e-5 * altitude_m) ** 5.25588
    return pressure_pa / 6894.757  # Pa → psi


def indoor_rh(
    water_gen: float,
    cfm: float,
    in_db_temp: float,
    out_db_temp: float,
    out_rh: float,
    pressure_psi: float = SEA_LEVEL_PRESSURE_PSI,
) -> float:
    """Return indoor relative humidity (0–1).

    Parameters
    ----------
    water_gen:    pounds of water vapor released indoors per day
    cfm:          air exchange rate in cubic feet per minute (at indoor air density)
    in_db_temp:   indoor dry-bulb temperature, °F
    out_db_temp:  outdoor dry-bulb temperature, °F
    out_rh:       outdoor relative humidity as a decimal fraction (0–1)
    pressure_psi: atmospheric pressure in psi (default: sea level)
    """
    out_humid: float = psychrolib.GetHumRatioFromRelHum(out_db_temp, out_rh, pressure_psi)

    # Iterate twice: first guess 35 % indoor RH, then refine.
    in_rh: float = 0.35
    for _ in range(2):
        in_hum_rat: float = psychrolib.GetHumRatioFromRelHum(in_db_temp, in_rh, pressure_psi)
        vol: float = psychrolib.GetMoistAirVolume(in_db_temp, in_hum_rat, pressure_psi)
        mass_flow: float = cfm * 1440 / vol  # lb dry air / day
        in_humid: float = out_humid + water_gen / mass_flow
        in_rh = min(psychrolib.GetRelHumFromHumRatio(in_db_temp, in_humid, pressure_psi), 1.0)

    return in_rh


# Default sensitivity-table axes (mirrors the spreadsheet)
_DEFAULT_CFM_VALUES: list[int] = [10, 20, 30, 50, 80, 120, 150, 200]
_DEFAULT_MOISTURE_VALUES: list[int] = [2, 3, 5, 8, 10, 15, 20]


@ui.page('/indoor_humidity')
def indoor_humidity() -> None:
    """Calculator page: Indoor Relative Humidity Model.

    Replicates the Analysis North 'Indoor Humidity Model' spreadsheet
    (humid.xlsm).  Given outdoor conditions, home air-exchange rates, and
    indoor moisture-generation rates it calculates the resulting indoor
    relative humidity.
    """
    with ui.column().classes('w-full items-center p-8'):
        ui.button('Back to Home', on_click=lambda: ui.navigate.to('/')).classes('self-start mb-4')
        ui.label('Indoor Relative Humidity Calculator').classes('text-2xl font-bold mb-2')
        ui.label(
            'Calculates indoor relative humidity from outdoor conditions, '
            'ventilation rate, and indoor moisture generation.'
        ).classes('text-gray-600 mb-6')

        with ui.row().classes('w-full flex-wrap justify-center gap-8 items-start'):

            # ── Inputs ──────────────────────────────────────────────────────
            with ui.column().classes('w-[28rem]'):
                ui.label('Inputs').classes('text-lg font-semibold mb-2')

                alt_label = ui.label('Altitude: 0 ft above sea level')
                alt_slider = ui.slider(min=0, max=15000, value=0, step=100).classes('w-full')
                alt_pressure_label = ui.label(
                    f'Atmospheric Pressure: {SEA_LEVEL_PRESSURE_PSI:.3f} psi'
                ).classes('text-sm text-gray-500 mb-2')

                in_temp_label = ui.label('Indoor Temperature: 70 °F').classes('mt-2')
                in_temp = ui.slider(min=40, max=90, value=70, step=1).classes('w-full')

                cfm_label = ui.label('Ventilation / Air Exchange Rate: 80 cfm').classes('mt-4')
                cfm = ui.slider(min=5, max=300, value=80, step=5).classes('w-full')

                moisture_label = ui.label('Indoor Moisture Release: 8 lb/day').classes('mt-4')
                moisture = ui.slider(min=0, max=100, value=8, step=1).classes('w-full')

                out_temp_label = ui.label('Outdoor Temperature: 20 °F').classes('mt-4')
                out_temp = ui.slider(min=-40, max=70, value=20, step=1).classes('w-full')

                out_rh_label = ui.label('Outdoor Relative Humidity: 80%').classes('mt-4')
                out_rh_slider = ui.slider(min=0, max=100, value=80, step=1).classes('w-full')

            # ── Results ─────────────────────────────────────────────────────
            with ui.column().classes('w-[28rem]'):
                ui.label('Result').classes('text-lg font-semibold mb-2')
                result_label = ui.label('').classes('text-xl font-medium')

                ui.label('Sensitivity Table').classes('text-lg font-semibold mt-6 mb-1')
                ui.label(
                    'Indoor RH (%) for varying ventilation rates and moisture release '
                    'rates, using the outdoor conditions set above.'
                ).classes('text-sm text-gray-600 mb-2')
                table_container = ui.column().classes('w-full')

        # ── Chart ────────────────────────────────────────────────────────────
        with ui.column().classes('w-full items-center mt-6'):
            ui.label('Indoor RH vs. Ventilation Rate').classes('text-lg font-semibold mb-2')
            ui.label(
                'Shows how indoor relative humidity changes with ventilation rate '
                'for several moisture release rates.'
            ).classes('text-sm text-gray-600 mb-2')
            chart_container = ui.column().classes('w-full items-center')

        # ── Calculation ──────────────────────────────────────────────────────
        def _current_inputs() -> tuple[float, float, float, float, float, float]:
            """Return current slider values as (t_in, cfm_val, wg, t_out, rh_out, pressure_psi)."""
            pressure_psi: float = altitude_to_p_atm(float(alt_slider.value))
            return (
                float(in_temp.value),
                float(cfm.value),
                float(moisture.value),
                float(out_temp.value),
                float(out_rh_slider.value) / 100.0,
                pressure_psi,
            )

        def calculate_quick() -> None:
            """Update only the single result label — fast enough for every slider tick."""
            t_in: float
            cfm_val: float
            wg: float
            t_out: float
            rh_out: float
            pressure_psi: float
            t_in, cfm_val, wg, t_out, rh_out, pressure_psi = _current_inputs()
            rh_in: float = indoor_rh(wg, cfm_val, t_in, t_out, rh_out, pressure_psi)
            result_label.text = f'Indoor Relative Humidity: {rh_in * 100:.1f}%'

        def calculate_full() -> None:
            """Rebuild the sensitivity table and chart — called only on slider release."""
            t_in: float
            cfm_val: float
            wg: float
            t_out: float
            rh_out: float
            pressure_psi: float
            t_in, cfm_val, wg, t_out, rh_out, pressure_psi = _current_inputs()

            rh_in: float = indoor_rh(wg, cfm_val, t_in, t_out, rh_out, pressure_psi)
            result_label.text = f'Indoor Relative Humidity: {rh_in * 100:.1f}%'

            # Sensitivity table — built as an HTML string and rendered with ui.html()
            cfm_rows: list[int] = _DEFAULT_CFM_VALUES
            moisture_cols: list[int] = _DEFAULT_MOISTURE_VALUES

            th: str = 'border:1px solid #d1d5db;background:#f3f4f6;padding:4px 10px;text-align:center;'
            td_base: str = 'border:1px solid #d1d5db;padding:4px 10px;text-align:center;'
            td_hdr: str = td_base + 'background:#f9fafb;font-weight:600;'
            td_hi: str = td_base + 'background:#fef9c3;'

            nearest_cfm: int = min(cfm_rows, key=lambda c: abs(c - cfm_val))
            nearest_mc: int = min(moisture_cols, key=lambda m: abs(m - wg))

            rows_html: str = ''
            for cfm_r in cfm_rows:
                cells: str = f'<td style="{td_hdr}">{cfm_r}</td>'
                for mc in moisture_cols:
                    val: float = indoor_rh(mc, cfm_r, t_in, t_out, rh_out, pressure_psi) * 100
                    style: str = td_hi if (cfm_r == nearest_cfm and mc == nearest_mc) else td_base
                    cells += f'<td style="{style}">{val:.0f}%</td>'
                rows_html += f'<tr>{cells}</tr>'

            corner: str = (
                '<th style="position:relative;min-width:80px;height:48px;'
                'border:1px solid #d1d5db;background:#f3f4f6;padding:0;">'
                '<span style="position:absolute;top:4px;right:6px;'
                'font-size:0.75rem;line-height:1;">lb/day</span>'
                '<span style="position:absolute;bottom:4px;left:6px;'
                'font-size:0.75rem;line-height:1;">cfm</span>'
                '</th>'
            )
            header_cells: str = corner
            header_cells += ''.join(f'<th style="{th}">{mc}</th>' for mc in moisture_cols)

            html: str = (
                '<table style="border-collapse:collapse;font-size:0.875rem;">'
                f'<thead><tr>{header_cells}</tr></thead>'
                f'<tbody>{rows_html}</tbody>'
                '</table>'
            )

            table_container.clear()
            with table_container:
                ui.html(html)

            # Chart: RH vs cfm for several moisture release levels
            chart_container.clear()
            cfm_range: list[int] = list(range(5, 205, 5))
            moisture_lines: list[int] = [3, 5, 8, 12, 20]

            with chart_container:
                mp = ui.matplotlib(figsize=(7, 4)).classes('w-full max-w-3xl')
                with mp.figure as fig:
                    ax = fig.gca()
                    for wg_line in moisture_lines:
                        rh_vals: list[float] = [
                            indoor_rh(wg_line, c, t_in, t_out, rh_out, pressure_psi) * 100
                            for c in cfm_range
                        ]
                        ax.plot(cfm_range, rh_vals, label=f'{wg_line} lb/day')
                    rh_cur: float = indoor_rh(wg, cfm_val, t_in, t_out, rh_out, pressure_psi) * 100
                    ax.plot(cfm_val, rh_cur, 'ko', markersize=7, zorder=5, label='Current')
                    ax.axhline(100, color='red', linewidth=0.8, linestyle='--', label='100% RH')
                    ax.set_xlabel('Ventilation Rate (cfm)', fontsize=11)
                    ax.set_ylabel('Indoor Relative Humidity (%)', fontsize=11)
                    ax.set_ylim(0, 110)
                    ax.yaxis.set_major_formatter(mtick.PercentFormatter())
                    ax.grid(True, alpha=0.4)
                    ax.legend(title='Moisture Release', fontsize=9)
                    fig.tight_layout()

        # ── Event bindings ──────────────────────────────────────────────────
        # on_value_change fires continuously while dragging — only update labels
        # and the single result (fast).  The heavy table+chart rebuild is bound
        # to the Quasar 'change' event which fires once on mouse/touch release.
        def on_alt(e: ValueChangeEventArguments) -> None:
            """Update altitude labels and recalculate."""
            p: float = altitude_to_p_atm(e.value)
            alt_label.set_text(f'Altitude: {e.value:,} ft above sea level')
            alt_pressure_label.set_text(f'Atmospheric Pressure: {p:.3f} psi')
            calculate_quick()

        def on_in_temp(e: ValueChangeEventArguments) -> None:
            """Update indoor temperature label and recalculate."""
            in_temp_label.set_text(f'Indoor Temperature: {e.value} °F')
            calculate_quick()

        def on_cfm(e: ValueChangeEventArguments) -> None:
            """Update ventilation rate label and recalculate."""
            cfm_label.set_text(f'Ventilation / Air Exchange Rate: {e.value} cfm')
            calculate_quick()

        def on_moisture(e: ValueChangeEventArguments) -> None:
            """Update moisture release label and recalculate."""
            moisture_label.set_text(f'Indoor Moisture Release: {e.value} lb/day')
            calculate_quick()

        def on_out_temp(e: ValueChangeEventArguments) -> None:
            """Update outdoor temperature label and recalculate."""
            out_temp_label.set_text(f'Outdoor Temperature: {e.value} °F')
            calculate_quick()

        def on_out_rh(e: ValueChangeEventArguments) -> None:
            """Update outdoor relative humidity label and recalculate."""
            out_rh_label.set_text(f'Outdoor Relative Humidity: {e.value}%')
            calculate_quick()

        alt_slider.on_value_change(on_alt)
        in_temp.on_value_change(on_in_temp)
        cfm.on_value_change(on_cfm)
        moisture.on_value_change(on_moisture)
        out_temp.on_value_change(on_out_temp)
        out_rh_slider.on_value_change(on_out_rh)

        for _slider in (alt_slider, in_temp, cfm, moisture, out_temp, out_rh_slider):
            _slider.on('change', lambda _: calculate_full())

        calculate_full()
