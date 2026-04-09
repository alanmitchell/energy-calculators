import psychrolib
from nicegui import ui

psychrolib.SetUnitSystem(psychrolib.IP)

STANDARD_PRESSURE = 14.696  # psi


@ui.page('/psychrometric')
def psychrometric():
    with ui.column().classes('w-full items-center p-8'):
        ui.button('Back to Home', on_click=lambda: ui.navigate.to('/')).classes('self-start mb-4')
        ui.label('Psychrometric Calculator').classes('text-2xl font-bold mb-4')

        db_label = ui.label('Dry-Bulb Temperature: 70 °F')
        db_input = ui.slider(min=-20, max=100, value=70, step=1).classes('w-[30rem]')

        rh_label = ui.label('Relative Humidity: 50%').classes('mt-4')
        rh_input = ui.slider(min=0, max=100, value=50, step=1).classes('w-[30rem]')

        result_dew = ui.label('')
        result_wb = ui.label('')
        result_abs = ui.label('')

        def calculate():
            t_db = float(db_input.value)
            rh = float(rh_input.value)
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
                result_dew.text = f'Calculation error: {e}'
                result_wb.text = ''
                result_abs.text = ''

        def on_db_change(e):
            db_label.set_text(f'Dry-Bulb Temperature: {e.value} °F')
            calculate()

        def on_rh_change(e):
            rh_label.set_text(f'Relative Humidity: {e.value}%')
            calculate()

        db_input.on_value_change(on_db_change)
        rh_input.on_value_change(on_rh_change)

        calculate()
