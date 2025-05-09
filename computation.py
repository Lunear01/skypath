"""
Airport and Flight classes computations.
"""

from datetime import datetime, timedelta
from typing import Optional
import requests


class Airport:
    """A vertex used to represent an airport.

        Instance Attributes:
            - icao: Airport ICAO code.
            - name: Airport name e.g. 'Singapore Changi Airport'
            - city_iata: City IATA code of airport.
            - country: Country where airport is located.
            - latitude: Latitude of airport.
            - longitude: Longitude of airport.

        Representation Invariants:
            - len(self.icao) == 4 and self.icao.isalpha() and self.icao == self.icao.upper()
            - len(self.name) > 0
            - len(self.city_iata) == 3 and self.city_iata.isalpha() and self.city_iata == city_iata.upper()
            - len(self.country) > 0
            - 90.0 <= self.latitude <= 90.0
            - -180.0 <= self.longitude <= 180.0
    """

    icao: str
    name: str
    city_iata: str
    country: str
    latitude: float
    longitude: float

    def __init__(self, icao: str, name: str, city_iata: str, country: str,
                 latitude: float, longitude: float) -> None:
        """Initialize a new airport with the given data. """
        self.icao = icao
        self.name = name
        self.city_iata = city_iata
        self.country = country
        self.latitude = latitude
        self.longitude = longitude

    def __str__(self) -> str:
        return f"{self.icao} ({self.name})"

    def __repr__(self) -> str:
        return f"Airport('{self.icao}', '{self.name}', '{self.country}')"


class Flight:
    """A vertex used to represent a Flight.

        Instance Attributes:
            - flight_number: Flight number
            - airline_name: Flight's airline's name
            - airline_icao: Flight's airline's icao code
            - origin: Flight origin's Airport Object
            - destination: Flight destination's airport object.
            - departure_time: Flight's depature time
            - arrival_time: Flight's arrival time

        Representation Invariants:
            - Representation Invariants:
            - len(self.flight_number) > 0
            - len(self.airline) > 0
            - self.origin != self.destination
            - self.departure_time < self.arrival_time
    """
    flight_number: str
    airline_name: str
    airline_icao: str
    origin: Airport
    destination: Airport
    departure_time: datetime
    arrival_time: datetime

    def __init__(self, flight_number: str, airline_name: str, airline_icao: str, origin: Airport, destination: Airport,
                 departure_time: datetime, arrival_time: datetime) -> None:
        """Initialize a new flight with the given data. """

        self.flight_number = flight_number
        self.airline_name = airline_name
        self.airline_icao = airline_icao
        self.origin = origin
        self.destination = destination
        self.departure_time = departure_time
        self.arrival_time = arrival_time

    def __str__(self) -> str:
        return (f"Flight('{self.flight_number}', '{self.airline_name}', '{self.airline_icao}', '{self.origin.icao}', "
                f"'{self.destination.icao}', '{self.departure_time}, '{self.arrival_time})")

    def __repr__(self) -> str:
        return f"{self.origin.name} ({self.flight_number})"

    def get_duration(self) -> timedelta:
        """Get the total duration of a single flight"""

        return self.arrival_time - self.departure_time


class FlightNetwork:
    """A directed graph representing airports as vertices and flights as edges.

    Instance Attributes:
        - airports: Mapping of airport ICAO code to corresponding airport object
        - flights: Mapping of flight origin's airport ICAO code to the set of departing flights

    Representation Invariants:
        - all(flight.origin in self.airports for flight in self._get_all_flights())
        - all(flight.destination in self.airports for flight in self._get_all_flights())
        - all(icao_code == airport.icao_code for icao_code, airport in self.airports.items())
        - all(flight.origin == origin_icao for origin_icao, flights in self.flights.items() for flight in flights)
        - all(icao_code in self.airports for icao_code in self.flights.keys())
    """

    airports: dict[str, Airport]
    flights: dict[str, set[Flight]]

    def __init__(self) -> None:
        """Initialise a new flight network that stores the Flight-Airport relationships."""

        self.airports = {}
        self.flights = {}

    def add_airport(self, airport: Airport) -> None:
        """Add an airport to the network.

        Preconditions:
            - airport.icao not in self.airports
        """

        self.airports[airport.icao] = airport

    def add_flight(self, flight: Flight) -> None:
        """Add a flight to the network.

        Preconditions:
            - flight.origin.icao in self.airports
            - flight.destination.icao in self.airports
        """

        # Ensure origin airport is in the network.
        if flight.origin.icao not in self.airports:
            raise ValueError("Origin airport not in network")

        # Ensure destination airport is in the network.
        if flight.destination.icao not in self.airports:
            raise ValueError("Destination airport not in network")

        if flight.origin.icao in self.flights:
            # if flight.origin.icao exists, add flight to set.
            self.flights[flight.origin.icao].add(flight)
        else:
            # if flight.origin.icao doesn't exist, create a new set with flight inside.
            self.flights[flight.origin.icao] = {flight}

    def total_layover(self, route: list[Flight]) -> timedelta:  # object that represents time difference in dates
        """Return the total layover time in timedelta for one route of flights

        Preconditions:
            - len(route) >= 2
            - all(flight.destination == route[i+1].origin for i, flight in enumerate(route[:-1]))
            - all(route[i].arrival_time <= route[i+1].departure_time for i in range(len(route)-1))
        """

        total = timedelta()

        for i in range(1, len(route)):
            total += (route[i].departure_time - route[i - 1].arrival_time)

        return total

    def find_all_routes(self, from_code: str, to_code: str) -> list[list[Flight]]:
        """Return all possible paths of flight objects in a list from one destination to another.

        Preconditions:
            - from_code in self.airports  # Departure airport exists
            - to_code in self.airports  # Destination airport exists
            - from_code != to_code  # Not the same airport (unless you allow empty routes)

        """
        if from_code not in self.airports:
            raise ValueError("Departure airport not found")
        elif to_code not in self.airports:
            raise ValueError("Destination airport not found")

        all_paths = []
        self.find_paths(from_code, to_code, [], set(), all_paths)

        return all_paths

    def find_paths(self, current_code: str, target_code: str, paths: list[Flight], visited: set[str],
                   all_paths: list[list[Flight]]) -> None:
        """Recursively find all paths from `current_code` to `target_code`. This method is a helper function of find_all
        routes that mutates the arguments.

        Instance Attributes:
            - current_code: The current airport code.
            - target_code: The destination airport code.
            - path: The current path being explored.
            - visited: A set of airport codes that have already been visited.
            - all_paths: A list to store all valid paths.

        Preconditions:
            - current_code in self.airports  # Current airport exists in the network
            - target_code in self.airports  # Target airport exists in the network
            - all(flight.origin.icao == current_code for flight in self.flights.get(current_code, set()))
            - all(flight.destination.icao in self.airports for flight in self._get_all_flights())
        """
        visited.add(current_code)

        # If the current airport is the target, add the path to the result
        if current_code == target_code:
            all_paths.append(paths.copy())
        else:
            # Explore all flights from the current airport
            for flight in self.flights.get(current_code, set()):
                if flight.destination.icao not in visited:
                    paths.append(flight)
                    self.find_paths(flight.destination.icao, target_code, paths, visited, all_paths)
                    paths.pop()
        visited.remove(current_code)

    def find_shortest_time_path(
            self,
            start_code: str,
            end_code: str,
            visited: Optional[set[str]] = None,
            current_time: timedelta = timedelta(0),
            current_flights: Optional[list[Flight]] = None,
            best_path: Optional[tuple[list[Flight], timedelta]] = None
    ) -> tuple[list[Flight], timedelta]:
        """
        Returns the shortest travelling path (by total flight time) as a list of Flight objects.

        Instance attributes:
            - start_code: ICAO code of departure airport
            - end_code: ICAO code of destination airport
            - visited: Set of visited airport codes (internal use)
            - current_time: Accumulated flight time (internal use)
            - current_flights: Current path of Flight objects (internal use)
            - best_path: Best path found so far (internal use)

        Preconditions:
            - start_code in self.airports  # Departure airport exists in network
            - end_code in self.airports  # Destination airport exists in network
            - start_code != end_code or (start_code == end_code and current_flights is None)  # Non-trivial case or
            initial call
            - visited is None or isinstance(visited, set)  # Visited is None or a set of strings
            - current_time >= timedelta(0)  # Time is non-negative
            - current_flights is None or isinstance(current_flights, list)  # Flights is None or a list
            - best_path is None or (isinstance(best_path, tuple) and len(best_path) == 2)  # Valid best_path structure
            - all(flight.origin.icao == start_code for flight in self.flights.get(start_code, set()))  # Flight origins
            match key
        """
        if start_code not in self.airports:
            raise ValueError(f"Departure airport not found")
        if end_code not in self.airports:
            raise ValueError(f"Destination airport not found")

        # Initialize recursion parameters
        if visited is None:
            visited = set()
        if current_flights is None:
            current_flights = []
        if best_path is None:
            best_path = ([], timedelta.max)

        visited.add(start_code)

        # Base case
        if start_code == end_code:
            if current_time < best_path[1]:
                return current_flights.copy(), current_time
            return best_path

        # Recursive case: explore all flights from current airport
        for flight in self.flights.get(start_code, set()):
            dest_code = flight.destination.icao
            if dest_code not in visited:
                new_time = current_time + flight.get_duration()

                if new_time < best_path[1]:
                    current_flights.append(flight)
                    found_path, found_time = self.find_shortest_time_path(
                        dest_code,
                        end_code,
                        visited.copy(),
                        new_time,
                        current_flights,
                        best_path
                    )
                    current_flights.pop()

                    if found_time < best_path[1]:
                        best_path = (found_path, found_time)

        visited.remove(start_code)
        return best_path if best_path[0] else ([], timedelta.max)

    def find_shortest_layover(self, start_code: str, end_code: str) -> list[Flight]:
        """Returns the list of Flights that has the shortest_layover

        Preconditions:
            - start_code in self.airports  # Departure airport exists
            - end_code in self.airports  # Destination airport exists
            - start_code != end_code  # Not the same airport (unless empty routes are allowed)
            - len(self.find_all_routes(start_code, end_code)) >= 1  # At least one valid route exists
        """

        all_routes = self.find_all_routes(start_code, end_code)

        best_route = all_routes[0]
        min_layover = self.total_layover(best_route)

        # Compare against all other routes
        for route in all_routes[1:]:
            current_layover = self.total_layover(route)
            if current_layover < min_layover:
                best_route = route
                min_layover = current_layover

        return best_route

    def find_routes_by_airline(self, origin_code: str, destination_code: str, airline: str) -> list[list[Flight]]:
        """
        Returns all routes between origin and destination where all flights in the route
        are operated by the specified airline.

        Preconditions:
            - origin_code in self.airports  # Origin airport exists in the network
            - destination_code in self.airports  # Destination airport exists in the network
            - len(airline.strip()) > 0  # Airline name is not empty
            - origin_code != destination_code  # Not the same airport (unless empty routes are allowed)
            - any(flight.airline_name.lower() == airline.lower() for flight in self._get_all_flights())
        """

        all_routes = self.find_all_routes(origin_code, destination_code)
        airline_routes = []

        for route in all_routes:
            # Check if any flight in route is operated by the specified airline
            if any(flight.airline_name.lower() == airline.lower() for flight in route):
                airline_routes.append(route)

        return airline_routes

    def find_valid_routes(self, passport: str, origin_code: str, destination_code: str) -> list[list[Flight]]:
        """
        Find all routes between origin and destination that don't require visas
        for the passport holder.

        Preconditions:
            - len(passport.strip()) > 0  # Passport is not empty
            - origin_code in self.airports  # Origin airport exists
            - destination_code in self.airports  # Destination airport exists
            - origin_code != destination_code  # Not the same airport (unless empty routes are allowed)
        """

        print("Getting Visa Information....")  # Get list of visa-required countries based on passport

        response = requests.get(f'https://rough-sun-2523.fly.dev/country/{passport}')
        passport_data = response.json()
        countries_required_visa = []

        for i in passport_data["VR"]:
            countries_required_visa.append(i["name"])

        all_routes = self.find_all_routes(origin_code, destination_code)
        valid_routes = []

        for route in all_routes:
            countries = []
            for flight in route:
                if flight.destination.country not in countries_required_visa:
                    countries.append(flight.destination.country)

            if countries:
                valid_routes.append(route)

        return valid_routes


if __name__ == "__main__":
    import python_ta

    python_ta.check_all(config={
        'max-line-length': 120,
        'extra-imports': ['json', 'computation', 'datetime', 'visualization', 'requests'],
        'max-nested-blocks': 4
    })
