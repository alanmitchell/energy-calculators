"""Entry point for the Energy Calculators web application.

Imports each calculator module to register its page route, then starts the
NiceGUI server on the home page.
"""

from nicegui import ui

import calculators.psychrometric  # noqa: F401 – registers /psychrometric page
import calculators.economics  # noqa: F401 – registers /economics page
import calculators.indoor_humidity  # noqa: F401 – registers /indoor_humidity page
import calculators.heating_load  # noqa: F401 – registers /heating_load page


@ui.page('/')
def home() -> None:
    """Render the home page with cards linking to each available calculator."""
    with ui.column().classes('w-full items-center p-8'):
        ui.label('Energy Calculators').classes('text-3xl font-bold mb-6')

        with ui.row().classes('flex-wrap justify-center gap-6'):
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
            with ui.card().on('click', lambda: ui.navigate.to('/heating_load')).classes(
                'w-80 cursor-pointer hover:shadow-lg transition-shadow'
            ):
                ui.label('Determine Design Heating Load').classes('text-xl font-semibold')
                ui.label(
                    'Estimate the design space heating load of a residential building '
                    'based on annual fuel usage.'
                )

            with ui.card().on('click', lambda: ui.navigate.to('/psychrometric')).classes(
                'w-80 cursor-pointer hover:shadow-lg transition-shadow'
            ):
                ui.label('Psychrometric Calculator').classes('text-xl font-semibold')
                ui.label(
                    'Enter dry-bulb temperature and relative humidity to calculate '
                    'dewpoint, wet-bulb temperature, and absolute humidity.'
                )


ui.run(title='Energy Calculators')
