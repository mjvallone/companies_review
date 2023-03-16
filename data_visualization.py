import json
import folium
from streamlit_folium import folium_static


def create_map(country_counts):
    # country_counts = data.groupby(["user_location_process"]).size().reset_index(name="Counts")
    geo_json_data = json.load(open("custom.geo.json", encoding="utf-8"))
    m = folium.Map(location=[0, 0], zoom_start=2)
    folium.Choropleth(
      geo_data=geo_json_data,
      name='choropleth',
      data=country_counts,
      columns=['user_location_process', 'Counts'],
      key_on='feature.properties.iso_a2',
      # fill_color='YlGnBu',
      fill_color='YlGnBu',
      # fill_color='OrRd',
      fill_opacity=1,
      line_opacity=0.2,
      nan_fill_color = "White",
    ).add_to(m)
    return m


def select_data(data, option):
    if option == 'All':
        data = data.groupby(["user_location_process"]).size().reset_index(name="Counts")
    elif option == 'Positive':
        data = data.groupby(["user_location_process", "sentiment_label" ]).size().reset_index(name="Counts")
        data = data[data['sentiment_label'] == 'positive']
    elif option == 'Negative':
        data = data.groupby(["user_location_process", "sentiment_label" ]).size().reset_index(name="Counts")
        data = data[data['sentiment_label'] == 'negative']
    return data