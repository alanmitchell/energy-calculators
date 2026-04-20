"""Design space heating load calculator for residential buildings in Alaska."""

import requests
from nicegui import ui

_CITIES_URL: str = 'https://heatpump-api.energytools.com/lib/cities'
_CITY_URL: str = 'https://heatpump-api.energytools.com/lib/cities/{city_id}'

# (display_name, unit_label, default_efficiency, min_efficiency, max_efficiency)
_FUELS: list[tuple[str, str, float, float, float]] = [
    ('Natural Gas', 'ccf', 80.0, 60.0, 100.0),
    ('#1 Heating Oil', 'gallons', 80.0, 60.0, 100.0),
    ('Propane', 'gallons', 80.0, 60.0, 100.0),
    ('Spruce Wood', 'cords', 50.0, 15.0, 80.0),
    ('Birch Wood', 'cords', 50.0, 15.0, 80.0),
    ('Electricity', 'kWh', 100.0, 90.0, 350.0),
]


@ui.page('/heating_load')
def heating_load() -> None:
    """Render the design space heating load calculator page."""

    try:
        resp = requests.get(_CITIES_URL, timeout=10)
        resp.raise_for_status()
        cities_data: list[dict] = resp.json()
    except Exception:
        cities_data = []

    city_name_to_id: dict[str, int] = {city['label']: city['id'] for city in cities_data}

    use_inputs: list[ui.number] = []
    dhw_checks: list[ui.checkbox] = []
    dry_checks: list[ui.checkbox] = []
    cook_checks: list[ui.checkbox] = []
    eff_inputs: list[ui.number] = []

    def calculate() -> None:
        """Retrieve all inputs and fetch city data from API. Calculation to be implemented."""
        city_id: int | None = city_name_to_id.get(city_select.value) if city_select.value else None
        city_data: dict = {}
        if city_id is not None:
            try:
                r = requests.get(_CITY_URL.format(city_id=city_id), timeout=10)
                r.raise_for_status()
                city_data = r.json()
            except Exception:
                pass

        fuels: dict[str, dict] = {}
        for i, (name, _unit, _def, _min, _max) in enumerate(_FUELS):
            fuels[name] = {
                'annual_use': use_inputs[i].value or 0.0,
                'dhw': dhw_checks[i].value,
                'drying': dry_checks[i].value,
                'cooking': cook_checks[i].value,
                'efficiency': eff_inputs[i].value or 0.0,
            }

        floor_area: float = floor_area_input.value or 0.0
        floor_area_row.set_visibility(fuels['Electricity']['annual_use'] > 0)
        # TODO: implement heating load calculation using city_data and fuels

    with ui.column().classes('w-full items-center p-8'):
        ui.button('Back to Home', on_click=lambda: ui.navigate.to('/')).classes('self-start mb-4')
        ui.label('Determine Design Heating Load').classes('text-2xl font-bold mb-4')

        city_select: ui.select = ui.select(
            options=list(city_name_to_id.keys()),
            label='City',
            with_input=True,
            on_change=lambda: calculate(),
        ).classes('w-80 mb-6')

        with ui.element('div').classes('overflow-x-auto w-full mb-6'):
            with ui.element('table').classes('border-collapse'):
                with ui.element('thead'):
                    with ui.element('tr'):
                        ui.element('th').classes('p-2 border bg-gray-100')
                        for name, unit, _def, _min, _max in _FUELS:
                            with ui.element('th').classes('p-2 border bg-gray-100 text-center min-w-36'):
                                ui.label(name).classes('font-semibold block')
                                ui.label(f'({unit})').classes('text-sm text-gray-500 block')

                with ui.element('tbody'):
                    with ui.element('tr'):
                        with ui.element('td').classes('p-2 border font-medium whitespace-nowrap'):
                            ui.label('Annual Fuel Use')
                        for _name, _unit, _def, _min, _max in _FUELS:
                            with ui.element('td').classes('p-2 border'):
                                inp: ui.number = ui.number(
                                    value=None, format='%.1f',
                                    on_change=lambda: calculate(),
                                ).classes('w-28')
                                use_inputs.append(inp)

                    with ui.element('tr'):
                        with ui.element('td').classes('p-2 border font-medium whitespace-nowrap'):
                            ui.label('Also Used for Domestic Hot Water?')
                        for _ in _FUELS:
                            with ui.element('td').classes('p-2 border text-center'):
                                chk: ui.checkbox = ui.checkbox(on_change=lambda: calculate())
                                dhw_checks.append(chk)

                    with ui.element('tr'):
                        with ui.element('td').classes('p-2 border font-medium whitespace-nowrap'):
                            ui.label('Also Used for Clothes Drying?')
                        for _ in _FUELS:
                            with ui.element('td').classes('p-2 border text-center'):
                                chk = ui.checkbox(on_change=lambda: calculate())
                                dry_checks.append(chk)

                    with ui.element('tr'):
                        with ui.element('td').classes('p-2 border font-medium whitespace-nowrap'):
                            ui.label('Also Used for Cooking?')
                        for _ in _FUELS:
                            with ui.element('td').classes('p-2 border text-center'):
                                chk = ui.checkbox(on_change=lambda: calculate())
                                cook_checks.append(chk)

                    with ui.element('tr'):
                        with ui.element('td').classes('p-2 border font-medium whitespace-nowrap'):
                            ui.label('Efficiency (%)')
                        for _name, _unit, default_eff, min_eff, max_eff in _FUELS:
                            with ui.element('td').classes('p-2 border'):
                                eff: ui.number = ui.number(
                                    value=default_eff,
                                    min=min_eff,
                                    max=max_eff,
                                    format='%.0f',
                                    on_change=lambda: calculate(),
                                ).classes('w-28')
                                eff_inputs.append(eff)

        with ui.row().classes('items-center gap-2') as floor_area_row:
            floor_area_input: ui.number = ui.number(
                label='Building Floor Area (sq ft)',
                value=0,
                min=0,
                format='%.0f',
                on_change=lambda: calculate(),
            ).classes('w-60')
        floor_area_row.set_visibility(False)
