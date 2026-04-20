Add a calculator that will be used to determine the design space heating load of a 
residential building from the following inputs:

* The city in Alaska where the building is located.  Retrieve a list of possible cities from 
the API endpoint https://heatpump-api.energytools.com/lib/cities as documented here:
https://heatpump-api.energytools.com/docs#/Library/cities_lib_cities_get . Use a dropdown
widget to select the city and hopefully make the widget filter as a city name is typed.
* A number of inputs for each possible space heating fuel: natural gas (ccf),
#1 heating oil (gallons), propane (gallons), spruce wood (cords), birch wood (cords),
and electricity (kWh). The inputs for each fuel are:
    * Annual Fuel Use, default value = 0, numeric text box, show the units as indicated above.
    * Also Used for Domestic Hot Water?, checkbox
    * Also Used for Clothes Drying?, checkbox
    * Also Used for Cooking?, checkbox
    * Efficiency, units are %, numeric text box. The input have a default value and be limited
    to a particular range: default = 80%, range 60 - 100% for natural gas, #1 heating oil and
    propane; default = 50% range 15 - 80% for spruce wood and birch wood; default = 100% range
    90 - 350% for electricity.
* The fuel inputs should be arranged in a table, with each fuel type occupying a column of the table.
* If the annual usage of electricity is greater than zero, show a numeric input for the Building Floor area, units: square feet.
* If any of the inputs change, call a calculate() method which retrieves the inputs, but does no
actual calculations, as I will code the calculation. For the city input, retrieve the City ID, and
then call the https://heatpump-api.energytools.com/lib/cities/{city_id} API endpoint to 
retrieve information about the city. That endpoint is documented here:
https://heatpump-api.energytools.com/docs#/Library/city_lib_cities__city_id__get
