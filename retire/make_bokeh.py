import numpy as np

from bokeh.layouts import row, widgetbox
from bokeh.models import CustomJS, Slider, Legend
from bokeh.plotting import figure, output_file, show, ColumnDataSource

# Unchanged variables
N_years = 50

# Slider variables
annual_ROI = .06
annual_inflation = .03
annual_savings = 10
retired_tax_rate = .2
savings_start = 10
retired_income = 35

# Compute savings over time
x = np.arange(N_years)
y_savings = [savings_start * (1 - retired_tax_rate)]
y_interest = [0]
y_todays_dollar = [1]
retire_year = 0
for i in range(1, N_years):
    y_todays_dollar.append(y_todays_dollar[-1] * (1 + annual_inflation))
    y_interest.append(
        (y_savings[-1] * annual_ROI * (1 - retired_tax_rate)) / y_todays_dollar[-1])
    y_savings.append((y_savings[-1] * (1 + annual_ROI) + annual_savings * y_todays_dollar[i]))
    if y_interest[-1] >= retired_income and retire_year == 0:
        retire_year = i

# Create data for retirement indicators
y_ri = np.ones(N_years) * retired_income
x_rt = np.ones(N_years) * retire_year
y_rt = np.linspace(0, retired_income, N_years)

# Create data source for plotting and Slider callback
source = ColumnDataSource(
    data=dict(x=x, y=y_interest, y2=y_savings, y3=y_todays_dollar,
              y_ri=y_ri, x_rt=x_rt, y_rt=y_rt))

# Make initial figure of net income vs years of saving
plot = figure(plot_width=400, plot_height=400,
              x_axis_label='Years from start of savings',
              y_axis_label='Annual net income on interest (1000\'s of today\'s $)',
              x_range=(0, N_years))
r1 = plot.line('x', 'y', source=source, line_width=3, line_alpha=0.6, line_color='black', legend='income on interest')
r2 = plot.line('x', 'y_ri', source=source, line_width=3, line_alpha=0.6, line_color='red', legend='retirement threshold')
r3 = plot.line('x_rt', 'y_rt', source=source, line_width=3, line_alpha=0.6, line_color='green', legend='year of retirement')
plot.legend.location = 'top_left'
plot.legend.label_text_font_size = '10pt'

# Declare how to update plot on slider change
callback = CustomJS(args=dict(source=source), code="""
    var data = source.data;
    var savings_start = savings_start.value;
    var annual_ROI = annual_ROI.value;
    var annual_savings = annual_savings.value;
    var retired_tax_rate = retired_tax_rate.value;
    var annual_inflation = annual_inflation.value;
    var retired_income = retired_income.value;
    var found_retired = 0;
    x = data['x']
    y = data['y']
    y2 = data['y2']
    y3 = data['y3']
    y_ri = data['y_ri']
    x_rt = data['x_rt']
    y_rt = data['y_rt']
    y[0] = 0
    y2[0] = savings_start * (1 - retired_tax_rate)
    y3[0] = 1
    y_ri[0] = retired_income
    for (i = 1; i < x.length; i++) {
        y3[i] = y3[i-1] * (1 + annual_inflation);
        y[i] = (y2[i-1] * annual_ROI * (1 - retired_tax_rate)) / y3[i];
        y2[i] = (y2[i-1] * (1 + annual_ROI) + annual_savings * y3[i]);
        y_ri[i] = retired_income;
        if (y[i] >= retired_income) {
            if (found_retired == 0) {
                for (j = 0; j < x.length; j++) {
                    x_rt[j] = i;
                    y_rt[j] = retired_income * j / (x.length - 1);
                }
                found_retired = 1;
            }
        }
        if (i == x.length - 1) {
            if (found_retired == 0) {
                for (j = 0; j < x.length; j++) {
                    x_rt[j] = 0;
                    y_rt[j] = 0;
                }
            }
        }
    }
    source.change.emit();
""")

# Define all sliders
savings_start_slider = Slider(start=0, end=100, value=savings_start, step=1,
                              title="Starting savings (1000\'s of today\'s $)", callback=callback)
annual_savings_slider = Slider(start=0, end=50, value=annual_savings, step=1,
                               title="Annual savings (1000\'s of today\'s $)", callback=callback)
annual_ROI_slider = Slider(start=0, end=.2, value=annual_ROI, step=.01,
                           title="Annual ROI", callback=callback)
annual_inflation_slider = Slider(start=0, end=.05, value=annual_inflation, step=.001,
                                 title="Annual inflation", callback=callback)
retired_tax_rate_slider = Slider(start=0, end=.5, value=retired_tax_rate, step=.01,
                                 title="Tax rate (when retired)", callback=callback)
retired_income_slider = Slider(start=10, end=100, value=retired_income, step=1,
                               title="Retired net income (1000\'s of today\'s $)", callback=callback)

# Define which parameter each slider refers to
callback.args["savings_start"] = savings_start_slider
callback.args["annual_savings"] = annual_savings_slider
callback.args["annual_ROI"] = annual_ROI_slider
callback.args["annual_inflation"] = annual_inflation_slider
callback.args["retired_tax_rate"] = retired_tax_rate_slider
callback.args["retired_income"] = retired_income_slider

# Define layout of plot and sliders
layout = row(
    plot,
    widgetbox(savings_start_slider, annual_ROI_slider, annual_savings_slider,
              annual_inflation_slider, retired_tax_rate_slider, retired_income_slider),
)

# Output and show
output_file("/gh/srcole.github.io/assets/misc/retirement_bokeh.html", title="Retirement calculator")
show(layout)
