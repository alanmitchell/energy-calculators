from nicegui import ui


@ui.page('/temp-convert')
def temp_convert():
    with ui.column().classes('w-full items-center p-8'):
        ui.button('Back to Home', on_click=lambda: ui.navigate.to('/')).classes('self-start mb-4')
        ui.label('Celsius / Fahrenheit Converter').classes('text-2xl font-bold mb-4')

        celsius_input = ui.number(label='Celsius', format='%.2f')
        fahrenheit_input = ui.number(label='Fahrenheit', format='%.2f')

        def c_to_f():
            if celsius_input.value is not None:
                fahrenheit_input.value = round(celsius_input.value * 9 / 5 + 32, 2)

        def f_to_c():
            if fahrenheit_input.value is not None:
                celsius_input.value = round((fahrenheit_input.value - 32) * 5 / 9, 2)

        with ui.row().classes('gap-4 mt-4'):
            ui.button('Celsius → Fahrenheit', on_click=c_to_f)
            ui.button('Fahrenheit → Celsius', on_click=f_to_c)
