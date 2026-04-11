import numpy as np
import numpy_financial as nf
from matplotlib import pyplot as plt
import matplotlib.ticker as mtick
from nicegui import ui

TOOLTIP_ROR = (
    'The project is cost-effective if this Rate of Return exceeds that available '
    'from an alternative investment of comparable risk. Most residential energy '
    'projects provide tax-free income. This is a nominal rate of return; it has '
    'not been reduced for general inflation.'
)
TOOLTIP_PAYBACK = (
    'Initial cost divided by first-year savings. Represents the number of years '
    'to return the investment if first-year savings continued without change.'
)
TOOLTIP_NPV = (
    'If the Net Present Value is greater than $0, the project is cost-effective. '
    'It is the benefits minus the costs, with future benefits discounted to '
    'account for the time value of money.'
)
TOOLTIP_BC = (
    'The project is cost-effective if the Benefit/Cost Ratio is greater than 1.0. '
    'It is the sum of the benefits divided by the sum of the costs, accounting '
    'for the time value of money.'
)
TOOLTIP_CHART = (
    'Cumulatively adds up the cash flow of the project over its life. The graph '
    'starts negative due to the initial cost but grows as savings accumulate. '
    'No time-value of money is considered. Savings escalation is included.'
)

TOOLTIP_CLASSES = 'bg-white text-black text-sm shadow-lg max-w-[400px]'


def styled_tooltip(element, text):
    """Add a styled tooltip with white background and black text to an element."""
    with element:
        ui.tooltip(text).classes(TOOLTIP_CLASSES)
    return element


@ui.page('/economics')
def economics():
    """Page that provides an energy project economics calculator.

    Computes rate of return (IRR), simple payback, net present value, and
    benefit/cost ratio from user-supplied project cost, savings, escalation,
    inflation, and discount rate inputs.  Also renders a cumulative cash flow
    chart.  Results update automatically when any input changes.
    """
    with ui.column().classes('w-full items-center p-8'):
        ui.button('Back to Home', on_click=lambda: ui.navigate.to('/')).classes('self-start mb-4')
        ui.label('Energy Project Economics Calculator').classes('text-2xl font-bold mb-2')
        ui.label(
            'Determines various measures of cost-effectiveness for an energy project.'
        ).classes('text-gray-600 mb-4')

        with ui.row().classes('w-full flex-wrap justify-center gap-8 items-start'):
            # --- Inputs column ---
            with ui.column().classes('w-[28rem]'):
                ui.label('Project Inputs').classes('text-lg font-semibold mb-2')

                ui.textarea(label='Description of the Analysis').props('rows=2').classes('w-full')

                init_cost = ui.number(
                    label='Initial Project Cost ($)',
                    value=1000, min=0, step=1, format='%.0f',
                    on_change=lambda: calculate(),
                ).classes('w-full')

                life_label = ui.label('Project Life: 20 years').classes('mt-4 mb-0')
                life = ui.slider(min=3, max=50, value=20, step=1).classes('w-full')

                def on_life_change(e):
                    """Update the project life label and recalculate."""
                    life_label.set_text(f'Project Life: {e.value} years')
                    calculate()

                life.on_value_change(on_life_change)

                savings_yr1 = ui.number(
                    label='First Year Savings or Net Revenue ($)',
                    value=100, step=1, format='%.0f',
                    on_change=lambda: calculate(),
                ).classes('w-full')

                esc_label = ui.label('Savings Escalation: 0.5% / yr above inflation').classes('mt-4 mb-0')
                savings_esc = ui.slider(min=-1.0, max=3.0, value=0.5, step=0.1).classes('w-full')

                def update_esc_label(e):
                    """Update the escalation label text and recalculate."""
                    v = e.value
                    if v > 0:
                        esc_label.set_text(f'Savings Escalation: {v}% / yr above inflation')
                    elif v == 0:
                        esc_label.set_text('Savings Escalation: at general inflation rate')
                    else:
                        esc_label.set_text(f'Savings Escalation: {-v}% / yr below inflation')
                    calculate()

                savings_esc.on_value_change(update_esc_label)

                with ui.expansion('Advanced Inputs').classes('w-full mt-2'):
                    ui.label(
                        'The inflation rate should reflect expected average general inflation '
                        'over the project lifetime.'
                    ).classes('text-sm text-gray-600 mb-2')
                    infl_label = ui.label('General Inflation Rate: 2.5% / year').classes('mb-0')
                    general_inflation = ui.slider(min=1.0, max=4.0, value=2.5, step=0.1).classes('w-full')

                    def on_infl_change(e):
                        """Update the inflation rate label and recalculate."""
                        infl_label.set_text(f'General Inflation Rate: {e.value}% / year')
                        calculate()

                    general_inflation.on_value_change(on_infl_change)

                    ui.label(
                        'The Discount Rate indicates how much future cash flows are reduced '
                        'due to the time value of money. Set it to the rate of return achievable '
                        'by an alternative investment of equivalent risk. The US DOE typically '
                        'uses 3% / year above inflation.'
                    ).classes('text-sm text-gray-600 mb-2')
                    disc_label = ui.label('Discount Rate: 3.0% / yr above inflation').classes('mb-0')
                    discount_rate = ui.slider(min=1.0, max=8.0, value=3.0, step=0.25).classes('w-full')

                    def on_disc_change(e):
                        """Update the discount rate label and recalculate."""
                        disc_label.set_text(f'Discount Rate: {e.value}% / yr above inflation')
                        calculate()

                    discount_rate.on_value_change(on_disc_change)

            # --- Results column ---
            with ui.column().classes('w-[28rem]') as results_col:
                ui.label('Results').classes('text-lg font-semibold mb-1')
                ui.label('Hover over an output for explanation.').classes('text-sm text-gray-500 mb-2')
                results_col.set_visibility(False)

                lbl_ror = styled_tooltip(ui.label(''), TOOLTIP_ROR)
                lbl_payback = styled_tooltip(ui.label(''), TOOLTIP_PAYBACK)
                lbl_npv = styled_tooltip(ui.label(''), TOOLTIP_NPV)
                lbl_bc = styled_tooltip(ui.label(''), TOOLTIP_BC)
                styled_tooltip(
                    ui.label('Cumulative Cash Flow').classes('text-base font-semibold mt-4'),
                    TOOLTIP_CHART,
                )
                plot_container = ui.column().classes('w-full')

        def calculate():
            """Read current input values, compute economic metrics, and update
            the result labels and cumulative cash flow chart.
            """
            cost = init_cost.value or 0
            years = int(life.value or 20)
            sav1 = savings_yr1.value or 0
            esc = savings_esc.value or 0
            infl = general_inflation.value or 2.5
            disc = discount_rate.value or 3.0

            if cost <= 0 or sav1 == 0:
                ui.notify('Please enter a positive cost and non-zero savings.', type='warning')
                return

            # Build cash flow array
            cash_arr = np.array([-cost] + [0.0] * years)
            sav_mult = (1.0 + infl / 100.0) * (1.0 + esc / 100.0)
            savings = np.cumprod(np.array([1.0] + [sav_mult] * (years - 1))) * sav1
            savings = np.insert(savings, 0, 0.0)
            cash_arr = cash_arr + savings

            # Calculations
            irr = nf.irr(cash_arr)
            disc_rate_nom = (1 + disc / 100) * (1 + infl / 100) - 1.0
            npv = nf.npv(disc_rate_nom, cash_arr)
            bc = (npv + cost) / cost
            simple_pb = cost / sav1

            # Update result labels
            if np.isnan(irr):
                lbl_ror.text = 'Rate of Return: N/A'
            else:
                lbl_ror.text = f'Rate of Return: {irr * 100:.1f}% / year'
            lbl_payback.text = f'Simple Payback: {simple_pb:.1f} years'
            lbl_npv.text = f'Net Present Value: ${npv:,.0f}'
            lbl_bc.text = f'Benefit/Cost Ratio: {bc:.3g}'

            # Cumulative cash flow chart
            plot_container.clear()
            with plot_container:
                mp = ui.matplotlib(figsize=(6, 3.5)).classes('w-full')
                with mp.figure as fig:
                    ax = fig.gca()
                    yr = range(0, years + 1)
                    cum_cash = np.cumsum(cash_arr)
                    ax.plot(yr, cum_cash)
                    ax.grid(True)
                    ax.set_xlabel('Year', fontsize=12)
                    ax.set_ylabel('Cumulative Cash Flow', fontsize=12)
                    ax.yaxis.set_major_formatter(mtick.StrMethodFormatter('${x:,.0f}'))
                    ax.xaxis.set_major_locator(mtick.MaxNLocator(integer=True))
                    ax.fill_between(
                        yr, cum_cash, 0,
                        where=(cum_cash >= 0),
                        facecolor='lightgreen', interpolate=True, alpha=0.6,
                    )
                    ax.fill_between(
                        yr, cum_cash, 0,
                        where=(cum_cash <= 0),
                        facecolor='lightcoral', interpolate=True, alpha=0.6,
                    )
                    ax.axhline(0, color='black', linewidth=0.8)
                    fig.tight_layout()

            results_col.set_visibility(True)

        calculate()
