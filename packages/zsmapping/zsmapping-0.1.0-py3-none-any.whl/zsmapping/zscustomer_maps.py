#import yaml, requests, folium
from zsmapping.zsclouds import *
import pandas as pd
from geopy.geocoders import Nominatim

def assign_quartile(rxtx_max, quantile_2):
    interval_range = pd.interval_range(start=0, freq=(rxtx_max) / 4, end=rxtx_max)
    if quantile_2 == interval_range[0]:
        return (1)
    elif quantile_2 == interval_range[1]:
        return (2)
    elif quantile_2 == interval_range[2]:
        return (3)
    elif quantile_2 == interval_range[3]:
        return (4)

def get_coords(city, country, state=None):
    geolocator = Nominatim(user_agent="zs_mapp_app")
    if state:
        location = '{},{},{}'.format(city, state, country)
    else:
        location = '{},{}'.format(city, country)
    coords = geolocator.geocode(location)
    return coords

def create_zscaler_cloud_customer_use_dc_map(cloud_name, customer_name, single_cloud_dataframe, cloudview_output, pse_rollup=None,
                                             george=False, find_bruno=False):
    # section to load the CSV
    my_df = pd.read_csv(cloudview_output)
    # section to filter out all uneeded columns
    new_df = my_df.filter(['Datacenter', 'Rx+Tx Bytes', '% Org Transactions'])
    # section to arrange by size of percentage of total org transactions
    sorted_df = new_df.sort_values(by='% Org Transactions', ascending=False)
    # section to drop any transactions associated with Private Service Edges
    filtered_df = sorted_df[sorted_df['Datacenter'] != 'Private']
    filtered_df['Rx+Tx Bytes'] = filtered_df['Rx+Tx Bytes'].apply(lambda x: int(x.replace(',', '')))
    # section to calculate quartileinto 4 equal sections by the % of data center transactions and add a value to a new quantile column
    # filtered_df['quantile'] = pd.qcut(filtered_df['% Org Transactions'], 5, duplicates='drop', labels=False)
    interval_range = pd.interval_range(start=0, freq=(filtered_df['Rx+Tx Bytes'].max()) / 4,
                                       end=filtered_df['Rx+Tx Bytes'].max())
    filtered_df['quantile_2'] = pd.cut(filtered_df['Rx+Tx Bytes'], bins=interval_range, labels=[1, 2, 3, 4])
    filtered_df['quantile_3'] = filtered_df['quantile_2'].apply(
        lambda y: assign_quartile(filtered_df['Rx+Tx Bytes'].max(), y))

    # section deals with creating the actual maps

    newmap_centers = ["15.6134137", "19.0156172"]
    leaflet_tile = 'https://server.arcgisonline.com/ArcGIS/rest/services/NatGeo_World_Map/MapServer/tile/{z}/{y}/{x}'
    leaflet_attr = 'Tiles &copy; Esri &mdash; National Geographic, Esri, DeLorme, NAVTEQ, UNEP-WCMC, USGS, NASA, ESA, METI, NRCAN, GEBCO, NOAA, iPC'
    # leaflet_tile = 'https://tiles.stadiamaps.com/tiles/stamen_toner_background/{z}/{x}/{y}{r}'
    # leaflet_attr = 'https://www.stadiamaps.com/'

    # m = folium.Map(["15.6134137", "19.0156172"],tiles="Cartodb dark_matter", zoom_start=3)
    m = folium.Map(["15.6134137", "19.0156172"], tiles="Cartodb Positron", zoom_start=2.5)

    # section adds floating legend to map
    if george == False:
        from branca.element import Template, MacroElement

        template = ("""
        {% macro html(this, kwargs) %}

        <!doctype html>
        <html lang="en">
        <head>
          <meta charset="utf-8">
          <meta name="viewport" content="width=device-width, initial-scale=1">
          <title>jQuery UI Draggable - Default functionality</title>
          <link rel="stylesheet" href="//code.jquery.com/ui/1.12.1/themes/base/jquery-ui.css">

          <script src="https://code.jquery.com/jquery-1.12.4.js"></script>
          <script src="https://code.jquery.com/ui/1.12.1/jquery-ui.js"></script>

          <script>
          $( function() {
            $( "#maplegend" ).draggable({
                            start: function (event, ui) {
                                $(this).css({
                                    right: "auto",
                                    top: "auto",
                                    bottom: "auto"
                                });
                            }
                        });
        });

          </script>
        </head>
        <body>


        <div id='maplegend' class='maplegend' 
            style='position: absolute; z-index:9999; border:2px solid grey; background-color:rgba(255, 255, 255, 0.8);
             border-radius:6px; padding: 10px; font-size:14px; right: 20px; bottom: 20px;'>""" +
                    """
                    <div class='legend-title'>Legend</div>
                    <div class='legend-scale'>
                      <ul class='legend-labels'>
                        <li><span style='background:Red;opacity:1.0;'></span>Top 25% used Datacenters</li>
                        <li><span style='background:Orange;opacity:1.0;'></span>50-75% used Datacenters</li>
                        <li><span style='background:Yellow;opacity:1.0;'></span>Bottom 50% used Datacenters</li>
                        <li><span style='background:Green;opacity:1.0;'></span>Datacenters used by {}</li>
                        <li><span style='background:#52B2BF;opacity:1.0;'></span> {} Public Service Edge</li>
            
            
            
                      </ul>
                    </div>
                    </div>
            
                    </body>
                    </html>""".format(customer_name, cloud_name.upper()) +

                    """
                    <style type='text/css'>
                      .maplegend .legend-title {
                        text-align: left;
                        margin-bottom: 5px;
                        font-weight: bold;
                        font-size: 90%;
                        }
                      .maplegend .legend-scale ul {
                        margin: 0;
                        margin-bottom: 5px;
                        padding: 0;
                        float: left;
                        list-style: none;
                        }
                      .maplegend .legend-scale ul li {
                        font-size: 80%;
                        list-style: none;
                        margin-left: 0;
                        line-height: 18px;
                        margin-bottom: 2px;
                        }
                      .maplegend ul.legend-labels li span {
                        display: block;
                        float: left;
                        height: 16px;
                        width: 30px;
                        margin-right: 5px;
                        margin-left: 0;
                        border: 1px solid #999;
                        }
                      .maplegend .legend-source {
                        font-size: 80%;
                        color: #777;
                        clear: both;
                        }
                      .maplegend a {
                        color: #777;
                        }
                    </style>
                    {% endmacro %}""")
        macro = MacroElement()
        macro._template = Template(template)
        m.get_root().add_child(macro)

    zscaler_group = folium.map.FeatureGroup(name='Zscaler Internet Access DC Map')
    customer_dc_group = folium.map.FeatureGroup(name='{} DC in Use'.format(customer_name))
    customer_utilization_group = folium.map.FeatureGroup(name='{} DC Utilization'.format(customer_name), show=False)
    for record in single_cloud_dataframe:
        label = record['datacenter']
        if george == False:
            zscaler_group.add_child(folium.Marker(
                location=[record['lat'], record['lon']],
                tooltip='Zscaler DC: {}'.format(label),
                popup='Zscaler DC: {}'.format(label),
                icon=folium.features.CustomIcon('./icons/zscaler_pse.png', icon_size=(25, 25))))
        elif george == True:
            zscaler_group.add_child(folium.Circle(fill=True,
                                                  location=[record['lat'], record['lon']],
                                                  tooltip='{}'.format(label), radius=(100000), color='blue',
                                                  fill_opacity=.5))

        # adding circles for datacenters in use
        if record['datacenter'] in filtered_df['Datacenter'].values:
            #print("ZS DC is: " + record['datacenter'])
            dc_in_use = filtered_df.loc[filtered_df['Datacenter'] == record['datacenter']]
            dc_in_use
            dc_in_use = dc_in_use.to_dict('records')
            #print("Cust DC is: " + str(dc_in_use))
            if dc_in_use[0]['quantile_3'] == 1:
                customer_utilization_group.add_child(folium.Circle(fill=True,
                                                                   location=[record['lat'], record['lon']],
                                                                   tooltip='{}'.format(label),
                                                                   radius=(250000), color='yellow', fill_opacity=0.15))

                # customer_dc_group.add_child(folium.Circle( fill=True,
                # location=[record['lat'], record['lon']],popup='Zscaler DC: {}'.format(label),radius=(100000),color='green',fill_opacity=.5))

                customer_dc_group.add_child(folium.Circle(fill=True,
                                                          location=[record['lat'], record['lon']],
                                                          tooltip='{}'.format(label), radius=(300000),
                                                          color='green', fill_opacity=0.15))


            elif dc_in_use[0]['quantile_3'] == 2:
                customer_utilization_group.add_child(folium.Circle(fill=True,
                                                                   location=[record['lat'], record['lon']],
                                                                   radius=(450000), color='yellow', fill_opacity=0.25))

                # customer_dc_group.add_child(folium.Circle( fill=True,
                # location=[record['lat'], record['lon']],popup='Zscaler DC: {}'.format(label),radius=(100000),color='green',fill_opacity=.5))

                customer_dc_group.add_child(folium.Circle(fill=True,
                                                          location=[record['lat'], record['lon']],
                                                          tooltip='{}'.format(label), radius=(300000),
                                                          color='green', fill_opacity=0.15))

            elif dc_in_use[0]['quantile_3'] == 3:
                customer_utilization_group.add_child(folium.Circle(fill=True,
                                                                   location=[record['lat'], record['lon']],
                                                                   radius=(650000), color='orange', fill_opacity=0.45))

                # customer_dc_group.add_child(folium.Circle( fill=True,
                # location=[record['lat'], record['lon']],popup='Zscaler DC: {}'.format(label),radius=(100000),color='green',fill_opacity=.5))

                customer_dc_group.add_child(folium.Circle(fill=True,
                                                          location=[record['lat'], record['lon']],
                                                          tooltip='{}'.format(label), radius=(300000),
                                                          color='green', fill_opacity=0.15))

            elif dc_in_use[0]['quantile_3'] == 4:
                customer_utilization_group.add_child(folium.Circle(fill=True,
                                                                   location=[record['lat'], record['lon']],
                                                                   radius=(850000), color='orange', fill_opacity=0.65))

                # customer_dc_group.add_child(folium.Circle( fill=True,
                # location=[record['lat'], record['lon']],popup='Zscaler DC: {}'.format(label),radius=(100000),color='green',fill_opacity=.5))

                customer_dc_group.add_child(folium.Circle(fill=True,
                                                          location=[record['lat'], record['lon']],
                                                          tooltip='{}'.format(label), radius=(300000),
                                                          color='green', fill_opacity=0.15))
    magic_bruno_group = folium.map.FeatureGroup(name="Where's Bruno?", show=False)
    magic_bruno_group.add_child(folium.Marker(
        location=['45.5019', '-73.5674'],
        tooltip='Zscaler DC: {}'.format(label),
        popup='Zscaler DC: {}'.format(label),
        icon=folium.features.CustomIcon('./icons/bruno.png', icon_size=(25, 25))))
    if find_bruno == True:
        m.add_child(magic_bruno_group)
    if pse_rollup != None:
        pse_df = pd.read_csv(pse_rollup)
        my_pses = pse_df.to_dict('records')

        for site in my_pses:
            if type(site['state']) is 'float':
                #print(site['city'], site['state'], site['country'])
                my_coords = get_coords(site['city'], site['state'], site['country'])
                else:
                    #print(site['city'], site['country'])
                    my_coords = get_coords(site['city'], site['country'])

                label = site['city'] + ' : ' + site['cluster']

            zscaler_group.add_child(folium.Circle(fill=True,
                                                  location=[my_coords.point.latitude, my_coords.point.longitude],
                                                  tooltip='{}'.format(label), radius=(100000), color='purple',
                                                  fill_opacity=.5))
            # customer_dc_group.add_child(folium.Circle( fill=True,
            # location=[record['lat'], record['lon']],popup='Zscaler DC: {}'.format(label),radius=(100000),color='green',fill_opacity=.5))

            customer_dc_group.add_child(folium.Circle(fill=True,
                                                      location=[my_coords.point.latitude, my_coords.point.longitude],
                                                      tooltip='{}'.format(label), radius=(300000),
                                                      color='green', fill_opacity=0.15))


    m.add_child(zscaler_group)
    m.add_child(customer_dc_group)
    m.add_child(customer_utilization_group)


    m.add_child(folium.map.LayerControl())
    map_name = './cloudview_maps/{}_{}.html'.format(cloud_name, customer_name)
    m.save(map_name)
    return m
