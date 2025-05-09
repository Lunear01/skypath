# Skypath
SkyPath: A Highly Unobjective Graph-Based Travel Planning System for User-defined Optimal Travel

# Introduction  

As the final exam dates were released not long ago, many students planning to travel have been looking for the best flights customized to personal preferences. One thing we’ve realized is that international air travel is a complex and dynamic system involving thousands of flights, routes, and constraints. Challenges include finding flights based on factors such as:  
- Shortest travel time  
- Shortest layover time  
- Airline reputation  
- Specific airline preferences  
- Visa-free transfer restrictions  

Existing flight search tools are often too restricted, overly complex, or lack effective graphical visualization of flight paths. This project addresses modern needs, as air travel has become a critical part of daily life. By optimizing search algorithms and integrating graphical representations, we aim to help users save effort, time, and reduce stress.  

**Goal**: Create a user-friendly tool that efficiently visualizes potential routes based on customizable criteria (e.g., travel time, layovers, airline preferences, and visa restrictions).  

---

# Datasets  

**SkyPath** utilizes four datasets:  
1. `airline_reputations.json`  
2. `airport_information.json`  
3. `flight_information.json`  
4. Passport/visa information (via *Pangers* API)  

### 1. `airline_reputations.json`  
- **Source**: Mock data based on International Air Transport Association (IATA) standards.  
- **Method**: Random mapping of Airline ICAO codes to a float value between `0.0` (worst) and `5.0` (best).  

### 2. `airport_information.json` & `flight_information.json`  
- **Sources**:  
  - AviationStack API (flight data)  
  - OurAirports (airport data)  
  - FlightConnections (route data)  
- **Scope**: Custom dataset of flights from **Toronto Pearson International Airport (YYZ)** to **Singapore Changi Airport (SIN)**.  
  - Guarantees multiple routes (no direct flights) for testing filtering methods.  

### 3. Passport/Visa Information  
- **Source**: *Pangers* Passport Visa API (via Python `requests` library).  
- **Categories**:  
  - Visa Free  
  - Visa on Arrival (including eTA)  
  - eVisa  
  - Visa Required  
  - No Admission  
