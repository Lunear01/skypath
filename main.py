"""
json file processing
"""
import json

from datetime import datetime
from computation import Airport
from computation import Flight
from computation import FlightNetwork
from visualization import visualize_single_skypath, visualize_multiple_skypaths


# The following two methods cannot be placed in computations.py because a circular import error occurs
def get_airline_reputation(airline_icao_code: str) -> float:
    """
    Return the reputation score for a specific airline identified by its ICAO code, between 0.0 (worst) and 5.0 (best).

    Preconditions:
        - airline_icao_code must be a valid 3-letter ICAO code (uppercase letters only)
        - airline_icao_code must exist in the airline_reputations dictionary
        - airline_reputations dictionary must be initialized and populated
    """

    return airline_reputations[airline_icao_code]


def get_route_airline_reputations(path: list[Flight]) -> float:
    """
    Calculate the average reputation score for all airlines in a given flight route.

    Preconditions:
        - path must contain at least one Flight object
        - All Flight objects must have a valid airline_icao attribute
        - All airline_icao codes must exist in the airline_reputations dictionary
        - airline_reputations must contain float values between 0.0 and 5.0

    Representation Invariants:
        - Return value will always be between 0.0 and 5.0 (inclusive)
        - All flights contribute equally to the average
    """

    total_rep = 0

    for method_flight in path:
        total_rep += airline_reputations[method_flight.airline_icao]

    return total_rep / len(path)


if __name__ == "__main__":
    import python_ta

    python_ta.check_all(config={
        'max-line-length': 120,
        'extra-imports': ['json', 'computation', 'datetime', 'visualization', 'requests'],
        'max-nested-blocks': 4
    })

    # airline_reputations = {}
    network = FlightNetwork()

    # Create and add all airport objects to network
    with open('airport_information.json') as file:
        data = json.load(file)

        for airport in data["data"]:
            airport_icao = airport["icao_code"]
            name = airport["airport_name"]
            city_iata = airport["city_iata_code"]
            country = airport["country_name"]
            latitude = airport["latitude"]
            longitude = airport["longitude"]

            curr_airport = Airport(airport_icao, name, city_iata, country, latitude, longitude)

            network.add_airport(curr_airport)

    # Create and add all flight objects to network
    with open('flight_information.json') as file:
        data = json.load(file)

        for flight in data["data"]:  # Renamed loop variable to avoid confusion
            try:
                flight_number = flight["flight"]["iata"]
                airline_name = flight["airline"]["name"]
                airline_icao = flight["airline"]["icao"]
                origin = network.airports[flight["departure"]["icao"]]
                destination = network.airports[flight["arrival"]["icao"]]
                departure_time = datetime.fromisoformat(flight["departure"]["scheduled"])
                arrival_time = datetime.fromisoformat(flight["arrival"]["scheduled"])

                current_flight = Flight(flight_number, airline_name, airline_icao, origin, destination, departure_time,
                                        arrival_time)

                network.add_flight(current_flight)

            except KeyError as e:
                print(f"Missing data in flight record: {e}")
            except (ValueError, TypeError, AttributeError) as e:
                print(f"Error processing flight: {e}")

    # Opens airline reputation data and store it in the airline_reputations variable
    with open('airline_reputation.json') as file:
        airline_reputations = json.load(file)

    ongoing = True

    while ongoing is True:
        print("\n===== Flight Route Finder =====")

        passport = input("Enter your passport country code (e.g. HK, US, CA)"
                         "\nOr type 'quit' to quit program: ").strip().upper()

        if passport == 'QUIT':
            ongoing = False
            break

        origin = input("Enter origin airport ICAO code: ").strip().upper()
        while origin not in network.airports:
            print("Invalid airport code. Please try again.")
            origin = input("Enter origin airport ICAO code: ").strip().upper()

        destination = input("Enter destination airport ICAO code: ").strip().upper()
        while destination not in network.airports:
            print("Invalid airport code. Please try again.")
            destination = input("Enter destination airport ICAO code: ").strip().upper()

        print("1: Filter by shortest travelling time")
        print("2: Filter by shortest layover time")
        print("3: Filter by airline reputation")
        print("4: Filter by specfic airlines")
        print("5: Filter by visa-free routes")
        print("6: Quit the program")
        choice = input("\nEnter a number (1-6): ").strip()
        while choice not in {'1', '2', '3', '4', '5', '6'}:
            print("Invalid choice. Please enter a number between 1-6.")
            choice = input("Enter a number (1-6): ").strip()

        if choice == '1':
            top_route = network.find_shortest_time_path(origin, destination)
            if top_route:
                print("\n=== Route with Shortest travelling time ===")
                print(top_route[0])
                visualize_single_skypath(top_route[0], "Shortest Travelling Time Skypath")
            else:
                print(f"No routes found for between {origin} and {destination}")

        elif choice == '2':
            top_route = network.find_shortest_layover(origin, destination)
            if top_route:
                print("\n=== Route with Shortest Layover Times ===")
                print(top_route)
                visualize_single_skypath(top_route, "Shortest Layover Time Skypath")
            else:
                print(f"No routes found for between {origin} and {destination}")

        elif choice == '3':
            print("\n=== Route with Best Airline Reputation ===")
            all_routes = network.find_all_routes(origin, destination)
            if all_routes:
                best_route_reputation = 0
                best_route = []
                for route in all_routes:
                    if get_route_airline_reputations(route) > best_route_reputation:
                        best_route_reputation = get_route_airline_reputations(route)
                        best_route = route
                print(str(round(best_route_reputation, 2)), best_route)
                visualize_single_skypath(best_route, "Best Airline Reputation Skypath")
            else:
                print(f"No routes found for between {origin} and {destination}")

        elif choice == '4':
            airline = input("Enter airline name: ").strip().upper()
            routes = network.find_routes_by_airline(origin, destination, airline)
            if routes:
                print(f"\n=== Routes operated by {airline} ===")
                for i in range(0, len(routes)):
                    print(f"\n--- Option {i} ---")
                    for flight in routes[i]:
                        print(flight)
                visualize_multiple_skypaths(routes, "Routes with Desired Airline Skypaths")

            else:
                print(f"No routes found for {airline} between {origin} and {destination}")

        elif choice == '5':
            print("\n=== Visa-Free Routes ===")
            valid_routes = network.find_valid_routes(passport, origin, destination)
            if valid_routes:
                for i in range(0, len(valid_routes)):
                    print(f"\n--- Option {i} ---")
                    print(valid_routes[i])
                visualize_multiple_skypaths(valid_routes, "Visa-Free Skypaths")
            else:
                print(f"No visa-free routes found for between {origin} and {destination}")

        elif choice == '6':
            ongoing = False
            break

        choice = input("\nDo you want to restart?: ").strip().upper()
        while choice not in {'Y', 'N'}:
            print("Invalid choice. Please enter either Y/N")
            choice = input("Enter Y/N: ").strip().upper()

        if choice == 'N':
            ongoing = False
