from nicegui import ui

import calculators.psychrometric  # noqa: F401 – registers /psychrometric page
import calculators.economics  # noqa: F401 – registers /economics page
import calculators.indoor_humidity  # noqa: F401 – registers /indoor_humidity page


@ui.page('/')
def home():
    with ui.column().classes('w-full items-center p-8'):
        ui.label('Energy Calculators').classes('text-3xl font-bold mb-6')

        with ui.row().classes('flex-wrap justify-center gap-6'):
            with ui.card().on('click', lambda: ui.navigate.to('/psychrometric')).classes(
                'w-80 cursor-pointer hover:shadow-lg transition-shadow'
            ):
                ui.label('Psychrometric Calculator').classes('text-xl font-semibold')
                ui.label(
                    'Enter dry-bulb temperature and relative humidity to calculate '
                    'dewpoint, wet-bulb temperature, and absolute humidity.'
                )

            with ui.card().on('click', lambda: ui.navigate.to('/economics')).classes(
                'w-80 cursor-pointer hover:shadow-lg transition-shadow'
            ):
                ui.label('Energy Project Economics').classes('text-xl font-semibold')
                ui.label(
                    'Calculate rate of return, payback, net present value, and '
                    'benefit/cost ratio for an energy project.'
                )

            with ui.card().on('click', lambda: ui.navigate.to('/indoor_humidity')).classes(
                'w-80 cursor-pointer hover:shadow-lg transition-shadow'
            ):
                ui.label('Indoor Humidity Model').classes('text-xl font-semibold')
                ui.label(
                    'Calculate indoor relative humidity from outdoor conditions, '
                    'ventilation rate, and indoor moisture generation rate. '
                    'Includes a sensitivity table and chart.'
                )


ui.run(title='Energy Calculators')
