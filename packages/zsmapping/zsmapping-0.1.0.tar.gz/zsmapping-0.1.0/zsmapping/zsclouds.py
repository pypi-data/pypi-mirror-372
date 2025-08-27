#list of zcaler clouds from needs to be updated quarterly to confirm we haven't added more clouds
import yaml, requests, folium

all_clouds = yaml.safe_load('''
- zscaler.net
- zscalerone.net
- zscalertwo.net
- zscalerthree.net
- zscloud.net
- zscalerbet.net
- zscalergov.net
- zscalerten.net
''')


def get_clouds_json(all_clouds = all_clouds):
    ''' Function to fetch all of the JSON data center documents listing the data centers and related attributes for each zscaler cloud
    inputs
    all_clouds: object of type list where each element is the name of a zscaler cloud
    output
    cloud_json: object of type dict where each root element is the entire json document for a specific zscaler cloud.
    '''
    cloud_json = {}
    for cloud in all_clouds:
        f_url = 'https://config.zscaler.com/api/{}/cenr/json'.format(cloud)
        #print (f_url)
        try:
            cloud_json.update(requests.get(f_url).json())
        except:
            #print (e)
            pass
    return cloud_json

def create_single_cloud_data_frame(single_cloud_json):
    cloud_dc_list = []
    for region in single_cloud_json.keys():
        #print (region)
        region_name = (region.split(':')[1:])[0].lstrip()
        #print(region_name)
        for data_center in single_cloud_json[region].keys():
            #print (data_center)
            data_center_name = (data_center.split(':')[1:])[0].lstrip()
            #print ((data_center))
            #print (data_center_name)
            record = {"cloud" : "ZS2",
                     "region" : region_name,
                      "datacenter" : data_center_name,
                     "lat" : single_cloud_json[region][data_center][0]['latitude'],
                     "lon": single_cloud_json[region][data_center][0]['longitude'],
                     }
            cloud_dc_list.append(record)
    return cloud_dc_list




def create_zscaler_cloud_dc_map(cloud_name, single_cloud_dataframe):
    newmap_centers = ["15.6134137", "19.0156172"] #sets map center to chad which roughly centers the map on the screen
    leaflet_tile = 'https://server.arcgisonline.com/ArcGIS/rest/services/NatGeo_World_Map/MapServer/tile/{z}/{y}/{x}'
    leaflet_attr = 'Tiles &copy; Esri &mdash; National Geographic, Esri, DeLorme, NAVTEQ, UNEP-WCMC, USGS, NASA, ESA, METI, NRCAN, GEBCO, NOAA, iPC'
    # leaflet_tile = 'https://tiles.stadiamaps.com/tiles/stamen_toner_background/{z}/{x}/{y}{r}'
    # leaflet_attr = 'https://www.stadiamaps.com/'

    # m = folium.Map(["15.6134137", "19.0156172"],tiles="Cartodb dark_matter", zoom_start=3)
    m = folium.Map(["15.6134137", "19.0156172"], tiles="Cartodb Positron", zoom_start=2.5)

    # section adds floating legend to map
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
                    <li><span style='background:#52B2BF;opacity:1.0;'></span> {} Public Service Edge</li>
            
            
                  </ul>
                </div>
                </div>
            
                </body>
                </html>""".format(cloud_name.upper()) +

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
    for record in single_cloud_dataframe:
        label = record['datacenter']
        #zscaler_group.add_child(folium.Marker(
        #    location=[record['lat'], record['lon']],
        #    tooltip='Zscaler DC: {}'.format(label),
        #    popup='Zscaler DC: {}'.format(label),
        #    icon=folium.features.CustomIcon('./icons/zscaler_pse.png', icon_size=(25, 25))))
        zscaler_group.add_child(folium.Circle(fill=True,
                                              location=[record['lat'], record['lon']], tooltip='{}'.format(label),
                                              popup= '{}'.format(label), radius=(100000), color='blue',
                                              fill_opacity=.5))

    m.add_child(zscaler_group)
    map_name = './{}.html'.format(cloud_name)
    m.save(map_name)
    return m

def create_all_zs_cloud_maps(cloud_json):
    for cloud in cloud_json.keys():
        try:
            cloud_name = cloud
            cloud_df = create_single_cloud_data_frame(cloud_json[cloud_name])
            create_zscaler_cloud_dc_map(cloud_name, cloud_df)
        except:
            pass