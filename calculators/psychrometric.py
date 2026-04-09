import psychrolib
from nicegui import ui

psychrolib.SetUnitSystem(psychrolib.IP)

STANDARD_PRESSURE = 14.696  # psi


@ui.page('/psychrometric')
def psychrometric():
    with ui.column().classes('w-full items-center p-8'):
        ui.button('Back to Home', on_click=lambda: ui.navigate.to('/')).classes('self-start mb-4')
        ui.label('Psychrometric Calculator').classes('text-2xl font-bold mb-4')

        db_input = ui.number(label='Dry-Bulb Temperature (°F)', format='%.1f')
        rh_input = ui.number(label='Relative Humidity (%)', format='%.1f')

        result_dew = ui.label('')
        result_wb = ui.label('')
        result_abs = ui.label('')

        def calculate():
            if db_input.value is None or rh_input.value is None:
                ui.notify('Please enter both values.', type='warning')
                return

            t_db = float(db_input.value)
            rh = float(rh_input.value)

            if not (0 <= rh <= 100):
                ui.notify('Relative humidity must be between 0 and 100.', type='warning')
                return

            rh_frac = rh / 100.0

            try:
                t_dp = psychrolib.GetTDewPointFromRelHum(t_db, rh_frac)
                t_wb = psychrolib.GetTWetBulbFromRelHum(t_db, rh_frac, STANDARD_PRESSURE)
                w = psychrolib.GetHumRatioFromRelHum(t_db, rh_frac, STANDARD_PRESSURE)
                w_grains = w * 7000

                result_dew.text = f'Dewpoint Temperature: {t_dp:.1f} °F'
                result_wb.text = f'Wet-Bulb Temperature: {t_wb:.1f} °F'
                result_abs.text = f'Absolute Humidity: {w_grains:.1f} grains/lb  ({w:.5f} lb/lb)'
            except Exception as e:
                ui.notify(f'Calculation error: {e}', type='negative')

        ui.button('Calculate', on_click=calculate).classes('mt-4')
