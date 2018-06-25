from zconnect.testutils.factories import ProductFactory


class FridgeFactory(ProductFactory):
    name="sim-fridge"
    iot_name="sim-fridge"
    sku="123456"
    manufacturer="Demo"
    url="http://www.google.co.uk"
    support_url="http://www.google.co.uk"
    version="0.0.1"
    # no previous_version
    periodic_data=True
    periodic_data_interval_short=900
    periodic_data_num_intervals_short=24
    periodic_data_interval_long=21600
    periodic_data_num_intervals_long=112
    periodic_data_retention_short=2592000
    server_side_events=True
    battery_voltage_full=3.0
    battery_voltage_critical=2.5
    battery_voltage_low=2.7
