"""
graph visualizatioin
"""
from datetime import timedelta

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from computation import Flight


def visualize_single_skypath(flights: list[Flight], title: str = "Skypath") -> None:
    """
     Visualizes a single flight journey on an interactive world map with detailed flight information that displays

    Preconditions:
        - len(flights) >= 1
        - all(flight.destination == flights[i+1].origin for i in range(len(flights)-1))
        - All Flight objects must be valid

    Representation Invariants:
        - All displayed airports exist in the flight segments
        - Flight paths connect consecutively without gaps
        - Time calculations use consistent UTC timezone
        - Map projection maintains geographical accuracy
    """

    # Collect all unique airports
    airports = {}
    for flight in flights:
        airports[flight.origin.icao] = flight.origin
        airports[flight.destination.icao] = flight.destination

    # Create airports dataframe with all available attributes
    airports_df = pd.DataFrame([
        {
            'ICAO': airport.icao,
            'Name': airport.name,
            'City': airport.city_iata,
            'Country': airport.country,
            'Latitude': airport.latitude,
            'Longitude': airport.longitude,
            'FullInfo': f"{airport.name} ({airport.icao})<br>{airport.city_iata}, {airport.country}"
        }
        for airport in airports.values()
    ])

    # Prepare flight segments with all details
    segments = []
    total_duration = timedelta()

    for i, flight in enumerate(flights, 1):
        segments.append({
            'Segment': i,
            'FlightNumber': flight.flight_number,
            'Airline': flight.airline_name,
            'Origin': flight.origin.icao,
            'OriginInfo': f"{flight.origin.name} ({flight.origin.icao})",
            'Destination': flight.destination.icao,
            'DestinationInfo': f"{flight.destination.name} ({flight.destination.icao})",
            'Departure': flight.departure_time.strftime("%Y-%m-%d %H:%M"),
            'Arrival': flight.arrival_time.strftime("%Y-%m-%d %H:%M"),
            'Duration': str(flight.get_duration()),
            'Coordinates': [
                (flight.origin.longitude, flight.origin.latitude),
                (flight.destination.longitude, flight.destination.latitude)
            ]
        })
        total_duration += flight.get_duration()

    # Create base map
    fig = px.scatter_geo(airports_df,
                         lat='Latitude',
                         lon='Longitude',
                         hover_name='ICAO',
                         hover_data={'Name': True, 'City': True, 'Country': True, 'FullInfo': False},
                         projection='natural earth',
                         title=f"{title}<br>Total Duration: {total_duration}")

    # Add each flight segment with detailed information
    colors = px.colors.qualitative.Plotly
    for idx, segment in enumerate(segments):
        fig.add_trace(
            go.Scattergeo(
                lon=[segment['Coordinates'][0][0], segment['Coordinates'][1][0]],
                lat=[segment['Coordinates'][0][1], segment['Coordinates'][1][1]],
                mode='lines+markers',
                line={"width": 3, "color": colors[idx % len(colors)]},
                marker={"size": 10, "color": colors[idx % len(colors)]},
                hoverinfo='text',
                text=f"<b>{segment['Airline']} {segment['FlightNumber']}</b><br>"
                     f"<b>From:</b> {segment['OriginInfo']}<br>"
                     f"<b>To:</b> {segment['DestinationInfo']}<br>"
                     f"<b>Departure:</b> {segment['Departure']}<br>"
                     f"<b>Arrival:</b> {segment['Arrival']}<br>"
                     f"<b>Duration:</b> {segment['Duration']}<br>",
                name=f"Flight {segment['Segment']}: {segment['Airline']} {segment['FlightNumber']}",
                showlegend=True
            )
        )

    # Highlight origin and destination
    origin = flights[0].origin
    destination = flights[-1].destination

    fig.add_trace(
        go.Scattergeo(
            lon=[origin.longitude],
            lat=[origin.latitude],
            mode='markers',
            marker={"size": 20, "color": 'green', "symbol": 'circle'},
            hoverinfo='text',
            text=f"<b>ORIGIN</b><br>{origin.name} ({origin.icao})<br>{origin.city_iata}, {origin.country}",
            name='Origin Airport',
            showlegend=True
        )
    )

    fig.add_trace(
        go.Scattergeo(
            lon=[destination.longitude],
            lat=[destination.latitude],
            mode='markers',
            marker={"size": 20, "color": 'blue', "symbol": 'circle'},
            hoverinfo='text',
            text=f"<b>DESTINATION</b><br>{destination.name} ({destination.icao})<br>{destination.city_iata}, "
                 f"{destination.country}",
            name='Destination Airport',
            showlegend=True
        )
    )
    # Enhance layout
    fig.update_layout(
        geo={
            "showland": True,
            "landcolor": 'rgb(240, 240, 240)',
            "countrycolor": 'rgb(200, 200, 200)',
            "showocean": True,
            "oceancolor": 'rgb(220, 240, 255)',
            "showcountries": True,
            "showframe": False,
            "coastlinewidth": 1
        },
        margin={"l": 0, "r": 0, "t": 100, "b": 0},
        legend={
            "title": 'Flight Segments',
            "yanchor": "top",
            "y": 0.99,
            "xanchor": "left",
            "x": 0.01,
            "bgcolor": 'rgba(255,255,255,0.8)',
            "bordercolor": 'rgba(0,0,0,0.2)'
        },
        hoverlabel={"bgcolor": 'white', "font_size": 12, "font_family": 'Arial'}
    )

    fig.show()


def visualize_multiple_skypaths(flight_journeys: list[list[Flight]],
                                overall_title: str = "Multiple Flight Journeys") -> None:
    """
    Visualizes multiple independent flight journeys on a shared interactive world map.

    Preconditions:
        - len(flight_journeys) >= 1
        - all(len(journey) >= 1 for journey in flight_journeys)
        - all(flight.destination == journey[i+1].origin for i in range(len(journey)-1))
        - All Flight objects must be valid

    Representation Invariants:
        - Color consistency within each journey
        - Journey isolation (no accidental path connections between journeys)
        - Accurate duration calculations per journey
        - Geographical projection consistency
        - Legend accurately reflects visible elements
    """
    # Collect all unique airports from all journeys
    airports = {}
    for journey in flight_journeys:
        for flight in journey:
            airports[flight.origin.icao] = flight.origin
            airports[flight.destination.icao] = flight.destination

    # Create airports dataframe with all available attributes
    airports_df = pd.DataFrame([
        {
            'ICAO': airport.icao,
            'Name': airport.name,
            'City': airport.city_iata,
            'Country': airport.country,
            'Latitude': airport.latitude,
            'Longitude': airport.longitude,
            'FullInfo': f"{airport.name} ({airport.icao})<br>{airport.city_iata}, {airport.country}"
        }
        for airport in airports.values()
    ])

    # Create base map
    fig = px.scatter_geo(airports_df,
                         lat='Latitude',
                         lon='Longitude',
                         hover_name='ICAO',
                         hover_data={'Name': True, 'City': True, 'Country': True, 'FullInfo': False},
                         projection='natural earth',
                         title=overall_title)

    # Define a color sequence for the different journeys
    colors = px.colors.qualitative.Plotly + px.colors.qualitative.Dark24

    # Process each journey
    for journey_idx, journey in enumerate(flight_journeys):
        journey_color = colors[journey_idx % len(colors)]
        total_duration = timedelta()

        # Prepare flight segments for this journey
        for i, flight in enumerate(journey, 1):
            segment_duration = flight.get_duration()
            total_duration += segment_duration

            fig.add_trace(
                go.Scattergeo(
                    lon=[flight.origin.longitude, flight.destination.longitude],
                    lat=[flight.origin.latitude, flight.destination.latitude],
                    mode='lines+markers',
                    line={"width": 3, "color": journey_color},
                    marker={"size": 10, "color": journey_color},
                    hoverinfo='text',
                    text=f"<b>Journey {journey_idx + 1}</b><br>"
                         f"<b>{flight.airline_name} {flight.flight_number}</b><br>"
                         f"<b>From:</b> {flight.origin.name} ({flight.origin.icao})<br>"
                         f"<b>To:</b> {flight.destination.name} ({flight.destination.icao})<br>"
                         f"<b>Departure:</b> {flight.departure_time.strftime('%Y-%m-%d %H:%M')}<br>"
                         f"<b>Arrival:</b> {flight.arrival_time.strftime('%Y-%m-%d %H:%M')}<br>"
                         f"<b>Duration:</b> {segment_duration}",
                    name=f"Journey {journey_idx + 1} - Flight {i}: {flight.airline_name} {flight.flight_number}",
                    legendgroup=f"journey_{journey_idx}",
                    showlegend=True
                )
            )

        # Highlight origin and destination for this journey
        origin = journey[0].origin
        destination = journey[-1].destination

        fig.add_trace(
            go.Scattergeo(
                lon=[origin.longitude],
                lat=[origin.latitude],
                mode='markers',
                marker={"size": 15, "color": journey_color, "symbol": 'circle'},
                hoverinfo='text',
                text=f"<b>Journey {journey_idx + 1} ORIGIN</b><br>{origin.name} ({origin.icao})<br>"
                     f"{origin.city_iata}, {origin.country}",
                name=f"Journey {journey_idx + 1} Origin",
                legendgroup=f"journey_{journey_idx}",
                showlegend=True
            )
        )

        fig.add_trace(
            go.Scattergeo(
                lon=[destination.longitude],
                lat=[destination.latitude],
                mode='markers',
                marker={"size": 15, "color": journey_color, "symbol": 'star'},
                hoverinfo='text',
                text=f"<b>Journey {journey_idx + 1} DESTINATION</b><br>{destination.name} ({destination.icao})<br>"
                     f"{destination.city_iata}, {destination.country}<br>"
                     f"<b>Total Journey Duration:</b> {total_duration}",
                name=f"Journey {journey_idx + 1} Destination",
                legendgroup=f"journey_{journey_idx}",
                showlegend=True
            )
        )

    # Enhance layout
    fig.update_layout(
        geo={
            "showland": True,
            "landcolor": 'rgb(240, 240, 240)',
            "countrycolor": 'rgb(200, 200, 200)',
            "showocean": True,
            "oceancolor": 'rgb(220, 240, 255)',
            "showcountries": True,
            "showframe": False,
            "coastlinewidth": 1
        },
        margin={"l": 0, "r": 0, "t": 100, "b": 0},
        legend={
            "title": 'Flight Journeys',
            "yanchor": "top",
            "y": 0.99,
            "xanchor": "left",
            "x": 0.01,
            "bgcolor": 'rgba(255,255,255,0.8)',
            "bordercolor": 'rgba(0,0,0,0.2)'
        },
        hoverlabel={"bgcolor": 'white', "font_size": 12, "font_family": 'Arial'}
    )

    fig.show()


if __name__ == "__main__":
    import python_ta

    python_ta.check_all(config={
        'max-line-length': 120,
        'extra-imports': ['json', 'computation', 'datetime', 'visualization', 'requests',
                          'plotly.express', 'plotly.graph_objects', 'pandas'],
        'max-nested-blocks': 4
    })
