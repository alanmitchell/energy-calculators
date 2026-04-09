from nicegui import ui

import calculators.psychrometric  # noqa: F401 – registers /psychrometric page
import calculators.economics  # noqa: F401 – registers /economics page


@ui.page('/')
def home():
    with ui.column().classes('w-full items-center p-8'):
        ui.label('Energy Calculators').classes('text-3xl font-bold mb-6')

        with ui.row().classes('flex-wrap justify-center gap-6'):
            with ui.card().classes('w-80'):
                ui.label('Psychrometric Calculator').classes('text-xl font-semibold')
                ui.label(
                    'Enter dry-bulb temperature and relative humidity to calculate '
                    'dewpoint, wet-bulb temperature, and absolute humidity.'
                )
                ui.button('Open', on_click=lambda: ui.navigate.to('/psychrometric')).classes('mt-4')

            with ui.card().classes('w-80'):
                ui.label('Energy Project Economics').classes('text-xl font-semibold')
                ui.label(
                    'Calculate rate of return, payback, net present value, and '
                    'benefit/cost ratio for an energy project.'
                )
                ui.button('Open', on_click=lambda: ui.navigate.to('/economics')).classes('mt-4')


ui.run(title='Energy Calculators')
