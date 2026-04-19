"""Psychrometric calculator page."""

import psychrolib
from nicegui import ui
from nicegui.events import ValueChangeEventArguments

psychrolib.SetUnitSystem(psychrolib.IP)

SEA_LEVEL_PRESSURE_PSI: float = 14.696  # psi


def altitude_to_pressure_psi(altitude_ft: float) -> float:
    """Convert altitude in feet to atmospheric pressure in psi.

    Uses the standard atmosphere barometric formula.
    """
    # Standard atmosphere: P = P0 * (1 - L*h/T0)^(g*M/(R*L))
    # For IP units we work in SI then convert.
    altitude_m: float = altitude_ft * 0.3048
    pressure_pa: float = 101325.0 * (1.0 - 2.25577e-5 * altitude_m) ** 5.25588
    pressure_psi: float = pressure_pa / 6894.757
    return pressure_psi


@ui.page('/psychrometric')
def psychrometric() -> None:
    """Page that provides a psychrometric calculator."""
    with ui.column().classes('w-full items-center p-8'):
        ui.button('Back to Home', on_click=lambda: ui.navigate.to('/')).classes('self-start mb-4')
        ui.label('Psychrometric Calculator').classes('text-2xl font-bold mb-4')

        db_label = ui.label('Dry-Bulb Temperature: 70 °F')
        db_input = ui.slider(min=-20, max=100, value=70, step=1).classes('w-[30rem]')

        rh_label = ui.label('Relative Humidity: 50%').classes('mt-4')
        rh_input = ui.slider(min=0, max=100, value=50, step=1).classes('w-[30rem]')

        alt_label = ui.label('Altitude: 0 ft above sea level').classes('mt-4')
        alt_input = ui.slider(min=0, max=15000, value=0, step=100).classes('w-[30rem]')

        result_pressure = ui.label('').classes('mt-4')
        result_density = ui.label('')
        result_dew = ui.label('')
        result_wb = ui.label('')
        result_abs = ui.label('')

        def calculate() -> None:
            """Compute psychrometric properties from current slider values and update result labels."""
            t_db: float = float(db_input.value)
            rh: float = float(rh_input.value)
            rh_frac: float = rh / 100.0
            altitude: float = float(alt_input.value)
            pressure_psi: float = altitude_to_pressure_psi(altitude)
            atm: float = pressure_psi / SEA_LEVEL_PRESSURE_PSI

            result_pressure.text = f'Atmospheric Pressure: {pressure_psi:.3f} psi  ({atm:.4f} atm)'

            try:
                t_dp: float = psychrolib.GetTDewPointFromRelHum(t_db, rh_frac)
                t_wb: float = psychrolib.GetTWetBulbFromRelHum(t_db, rh_frac, pressure_psi)
                w: float = psychrolib.GetHumRatioFromRelHum(t_db, rh_frac, pressure_psi)
                w_grains: float = w * 7000
                density: float = psychrolib.GetMoistAirDensity(t_db, w, pressure_psi)

                result_dew.text = f'Dewpoint Temperature: {t_dp:.1f} °F'
                result_wb.text = f'Wet-Bulb Temperature: {t_wb:.1f} °F'
                result_abs.text = f'Absolute Humidity: {w_grains:.1f} grains/lb  ({w:.5f} lb/lb)'
                result_density.text = f'Air Density: {density:.4f} lb/ft³'
            except Exception as e:
                result_dew.text = f'Calculation error: {e}'
                result_wb.text = ''
                result_abs.text = ''
                result_density.text = ''

        def on_db_change(e: ValueChangeEventArguments) -> None:
            """Update dry-bulb label and recalculate."""
            db_label.set_text(f'Dry-Bulb Temperature: {e.value} °F')
            calculate()

        def on_rh_change(e: ValueChangeEventArguments) -> None:
            """Update relative humidity label and recalculate."""
            rh_label.set_text(f'Relative Humidity: {e.value}%')
            calculate()

        def on_alt_change(e: ValueChangeEventArguments) -> None:
            """Update altitude label and recalculate."""
            alt_label.set_text(f'Altitude: {e.value:,} ft above sea level')
            calculate()

        db_input.on_value_change(on_db_change)
        rh_input.on_value_change(on_rh_change)
        alt_input.on_value_change(on_alt_change)

        calculate()
