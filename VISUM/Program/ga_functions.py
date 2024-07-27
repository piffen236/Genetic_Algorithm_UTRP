import os.path

import win32com.client
import traceback
import sys
import importlib
import pandas as pd
import numpy as np
import platform 
import sys
print(sys.executable)


computer_name = platform.node()  # Use computer name to configure data for different run environments
# Specify the path to the helpers.py file
if computer_name == 'Josef-pc':
    helpers_path = r"C:\Program Files\PTV Vision\PTV Visum 2024\Exe\Python\Lib\site-packages\VisumPy\helpers.py"
elif computer_name == 'jesper-pc':
    helpers_path = r'D:\PTV Visum 2024\Exe\Python\Lib\site-packages\VisumPy\helpers.py'

# Load the module specified by the path
spec = importlib.util.spec_from_file_location("helpers", helpers_path)
helpers = importlib.util.module_from_spec(spec)
sys.modules["helpers"] = helpers
spec.loader.exec_module(helpers)

global stops, Visum
#Visum = win32com.client.Dispatch('Visum.Visum')
Visum = win32com.client.gencache.EnsureDispatch('Visum.Visum')
Visum_prt = win32com.client.gencache.EnsureDispatch('Visum.Visum')

def import_visum(visum_file_path):
    # Load the VISUM file
    Visum.LoadVersion(visum_file_path)
    #Visum_prt.LoadVersion(visum_file_path)
    #print("loaded") 
    stops=get_all_stop_no()
    #print(stops)
    return stops
def import_visum_prt(visum_file_path):
    # Load the VISUM file
    Visum_prt.LoadVersion(visum_file_path)

def get_all_stop_no():
    all_stops = []  # Initialize an empty list to store line route names
    # Iterate over all LineRoutes in the Visum network
    for stop in Visum.Net.StopPoints:
        # Access the 'No' attribute of each Stop
        stop_no = stop.AttValue('No')
        # Add the name to the list
        all_stops.append(stop_no)
    return all_stops
#REMOVE ALL BUSLINES
def remove_line_routes():
    for LineRoute in Visum.Net.LineRoutes:
        # Access attributes here
        #Making sure that only the new lines are rema
        if LineRoute.AttValue('LINENAME') == "ORG_1" or LineRoute.AttValue('LINENAME') == "1":
            Visum.Net.RemoveLineRoute(LineRoute)
#remove_line_routes()
import random
def generate_bus_routes(distance_matrix, all_stops, num_routes, max_stops_per_route):
    routes = []
    
    for _ in range(num_routes):
        # Randomly choose the first stop
        current_stop = random.choice(all_stops)
        route = [current_stop]

        # Randomly determine the length of the route (at least 5 stops, up to max_stops_per_route)
        route_length = random.randint(5, max_stops_per_route)

        for _ in range(route_length - 1):  # One stop is already in the route
            # Remove already selected stops from potential next stops
            potential_stops = [stop for stop in all_stops if stop not in route]
            
            # If there are no more potential stops, break out of the loop
            if not potential_stops:
                break
            
            # Get a Series of distances to all potential next stops
            distances_to_potentials = distance_matrix.loc[current_stop, potential_stops]
            
            # Manually find the minimum distance stop
            closest_stop = distances_to_potentials.idxmin()
            
            # Append closest stop to route and set as the current stop
            route.append(closest_stop)
            current_stop = closest_stop  # Update the current stop for the next iteration
        
        routes.append(route)

    return routes


def create_route(route_vector, bus_nr, direction):
    # use constants
    C = win32com.client.constants
    
    #retreive some required objects from the network
    BusLine = Visum.Net.Lines.ItemByKey("ORG_1")
    dirTo = Visum.Net.Directions.GetAll[direction]
    stopsR1 = Visum.CreateNetElements()
    for stop in route_vector:
        stopPoint = Visum.Net.StopPoints.ItemByKey(stop)
        stopsR1.Add(stopPoint)

              
    paraR1 = Visum.IO.CreateNetReadRouteSearchTSys() #create the parameter object
    paraR1.SetAttValue("HowToHandleIncompleteRoute", 3) # search shortest path if line route has gaps
    paraR1.SetAttValue("ShortestPathCriterion", 3) # link travel time of current transport system
    paraR1.SetAttValue("IncludeBlockedLinks", False) # don't route over closed links
    paraR1.SetAttValue("IncludeBlockedTurns", False) # don't route over closed turns
    paraR1.SetAttValue("MaxDeviationFactor", 1000) # maximum deviation factor of shortest path search from direct distance
    paraR1.SetAttValue("WhatToDoIfShortestPathNotFound", 0) # if no shortest path is found, don't read
    
    LineRoute =  Visum.Net.AddLineRoute(bus_nr, BusLine, dirTo, stopsR1, paraR1) #create the line route
    
    start_time = 0  # Start at 0 minutes (midnight)
    end_time = 24 * 60 * 60  # End at 86 400seconds or 1440 minutes (24 hours)
    frequency_seconds = 10 * 60 
    
    # Create a time profile for the line route
    TimeProfileName = "TP" + str(bus_nr)
    tp1 = Visum.Net.AddTimeProfile(TimeProfileName, LineRoute)
    i = 1
    for time_in_seconds in range(start_time, end_time, frequency_seconds):
        trip1 = Visum.Net.AddVehicleJourney(bus_nr+str(i),tp1)
        trip1.SetAttValue("Dep",time_in_seconds)
        i+=1


def load_net_file(net_file):
    # use constants
    C = win32com.client.constants

    # create AddNetRead-Object and specify desired conflict avoiding method
    anrController = Visum.IO.CreateAddNetReadController()
    anrController.SetWhatToDo("Line", C.AddNetRead_Ignore)
    anrController.SetWhatToDo("LineRoute", C.AddNetRead_Ignore)
    anrController.SetWhatToDo("LineRouteItem", C.AddNetRead_Ignore)
    anrController.SetWhatToDo("TimeProfile", C.AddNetRead_Ignore)
    anrController.SetWhatToDo("TimeProfileItem", C.AddNetRead_Ignore)
    anrController.SetWhatToDo("VehJourney", C.AddNetRead_Ignore)
    anrController.SetUseNumericOffset("VehJourney", True)
    anrController.SetWhatToDo("VehJourneyItem", C.AddNetRead_DoNothing)
    anrController.SetWhatToDo("VehJourneySection", C.AddNetRead_Ignore)
    anrController.SetWhatToDo("ChainedUpVehJourneySection", C.AddNetRead_DoNothing)
    anrController.SetWhatToDo("UserAttDef", C.AddNetRead_Ignore)
    anrController.SetWhatToDo("Operator", C.AddNetRead_OverWrite)

    # anrController.SetConflictAvoidingForAll(10000, "ORG_")

    # create NetRouteSearchTSys-Object and choose route search options
    # create one object per TSys if desired
    routesearchparameters = Visum.IO.CreateNetReadRouteSearchTSys()
    routesearchparameters.SetAttValue("HowToHandleIncompleteRoute",
                                      C.RouteSearchHandleIncompleteRouteTSearchShortestPath)  # search shortest path if line route has gaps
    routesearchparameters.SetAttValue("ShortestPathCriterion",
                                      C.ShortestPathCriterion_LinkLength)  # Value 4: Link length
    routesearchparameters.SetAttValue("IncludeBlockedLinks", False)  # don't route over closed links
    routesearchparameters.SetAttValue("IncludeBlockedTurns", False)  # don't route over closed turns
    routesearchparameters.SetAttValue("MaxDeviationFactor",
                                      1000)  # maximum deviation factor of shortest path search from direct distance
    routesearchparameters.SetAttValue("WhatToDoIfShortestPathNotFound",
                                      C.IfNotFound_DontRead)  # if no shortest path is found, don't read
    routesearchparameters.SetAttValue("WhatToDoIfStopPointIsBlocked",
                                      C.ifStopPointIsBlocked_DontReadTimeProfile)  # if stop point is blocked, don't read
    routesearchparameters.SetAttValue("WhatToDoIfStopPointNotFound",
                                      C.ifStopPointNotFound_DontReadLineRoute)  # if stop point not found, don't read

    # create NetRouteSearch-Object and assign NetRouteSearchTSys-objects
    nrrsController = Visum.IO.CreateNetReadRouteSearch()
    nrrsController.SetForAllTSys(routesearchparameters)

    #Load net file
    Visum.IO.LoadNet(net_file, True, nrrsController, anrController)

from datetime import datetime, timedelta
def save_as_net_file(filepath, network_data, selected_row=0, headway = "NaN"):
    #This funciton takes a DF with bus informaiton, It will save a specific row in a .NET format, the row is set by "selected_row"
    #The format of the dataframe is as follows
    """
    NET Score Line 	TSYSCODE  FARESYSTEMSET   VEHCOMBNO 	 Bus_nr 	       Bus_tp 	          Bus_routes 	      frequency MIN 	 time_offset MIN

    With example values such ass 

    1;  352  ;ORG_1   B;      BLANK;           BLANK;     [[110],[111]];   [[tp110],[tp111]];   [[1,2,3],[3,6,2]]      [[10],[5]]          [[0],[1]]
    """
    with open(filepath, 'w', encoding='utf-8') as file:
        # Header
        file.write("$VISION\n* Table: Version block\n$VERSION:VERSNR;FILETYPE;LANGUAGE;UNIT\n15;Net;ENG;KM\n")

        # Only one row expected for compacted data, handling accordingly
        row = network_data.iloc[selected_row]


        # user defined attributes

        file.write("$USERATTDEF:OBJID;ATTID;CODE;NAME;VALUETYPE;DEFAULTSTRINGVALUE;MAXSTRINGLENGTH;DATASOURCETYPE;FORMULA;SCALEDBYLENGTH;CROSSSECTIONLOGIC;CSLIGNORECLOSED;SUBATTRS;CANBEEMPTY;USERDEFINEDGROUPNAME;OPERATIONREFERENCE")
        file.write("NETWORK;SCORE;Score;FLOAT;Double;;0;Data;;0;SUM;0;;0;;")
        # Line 
        file.write("* \n* Table: Lines\n$LINE:NAME;TSYSCODE;FARESYSTEMSET;VEHCOMBNO\n")
        file.write(f"{row['Line']};{row['TSYSCODE']};{row['FARESYSTEMSET']};{row['VEHCOMBNO']}\n")

        # Line Route 
        if headway != "NaN": 
            file.write(f"\n* Table: Line routes\n$LINEROUTE:LINENAME;NAME;DIRECTIONCODE;ISCIRCLELINE;{headway}\n")
            for bus_nr, freq in zip(row['Bus_nr'], row['frequency']):
                if freq != 0:
                    file.write(f"{row['Line']};{bus_nr};>;0;{freq*18}\n")
                    file.write(f"{row['Line']};{bus_nr+'0'};<;0;{freq*18}\n")
        else:
            file.write("\n* Table: Line routes\n$LINEROUTE:LINENAME;NAME;DIRECTIONCODE;ISCIRCLELINE\n")
            for bus_nr in row['Bus_nr']:
                file.write(f"{row['Line']};{bus_nr};>;0\n")
                file.write(f"{row['Line']};{bus_nr+'0'};<;0\n")

        # Line route items 
        file.write("\n* Table: Line route items\n$LINEROUTEITEM:LINENAME;LINEROUTENAME;DIRECTIONCODE;INDEX;ISROUTEPOINT;NODENO;STOPPOINTNO\n")
        for bus_nr_org, bus_route in zip(row['Bus_nr'], row['Bus_routes']):
            for dir in ['>','<']:
                for index, j in enumerate(bus_route, start=1):
                    if dir == '<':
                        bus_nr = bus_nr_org + '0'
                    else:
                        bus_nr = bus_nr_org
                    file.write(f"{row['Line']};{bus_nr};{dir};{index};1;{int(j)};{int(j)}\n")

        # Time profiles 
        file.write("\n* Table: Time profiles\n$TIMEPROFILE:LINENAME;LINEROUTENAME;DIRECTIONCODE;NAME;VEHCOMBNO;REFITEMINDEX;FIXREFDEP\n")
        for bus_nr_org, bus_tp in zip(row['Bus_nr'], row['Bus_tp']):
            for dir in ['>','<']:
                if dir == '<':
                    bus_nr = bus_nr_org + '0'
                else:
                    bus_nr = bus_nr_org
                file.write(f"{row['Line']};{bus_nr};{dir};{bus_tp};;0;1\n")

        # Time profile items 
        file.write("\n* Table: Time profile items\n$TIMEPROFILEITEM:LINENAME;LINEROUTENAME;DIRECTIONCODE;TIMEPROFILENAME;INDEX;LRITEMINDEX;ALIGHT;BOARD;ARR;DEP\n")
        for bus_nr_org, bus_tp, bus_route_list in zip(row['Bus_nr'], row['Bus_tp'], row['Bus_routes']):
            for dir in ['>','<']:
                if dir == '<':
                    bus_nr = bus_nr_org + '0'
                else:
                    bus_nr = bus_nr_org
                dep_time = datetime.strptime("00:00:00", "%H:%M:%S")
                for stop_index, j in enumerate(bus_route_list, start=1):
                    alight = 0 if stop_index == 1 else 1
                    board = 1 if stop_index == len(bus_route_list) else 1
                    file.write(f"{row['Line']};{bus_nr};{dir};{bus_tp};{stop_index};{stop_index};{alight};{board};{dep_time.strftime('%H:%M:%S')};{dep_time.strftime('%H:%M:%S')}\n")
                    dep_time += timedelta(minutes=1)

        # Vehicle journeys 
        
        if headway == "NaN":
            file.write("\n* Table: Vehicle journeys\n$VEHJOURNEY:NO;DEP;LINENAME;LINEROUTENAME;DIRECTIONCODE;TIMEPROFILENAME;FROMTPROFITEMINDEX;TOTPROFITEMINDEX\n")
            journey_no = 11101
            journeys=[]
            for bus_nr_org, bus_tp, bus_route_list, freq, time_offset in zip(row['Bus_nr'], row['Bus_tp'], row['Bus_routes'], row['frequency'], row['time_offset']):
                freq = 60/freq
                for dir in ['>','<']:
                    if dir == '<':
                        bus_nr = bus_nr_org + '0'
                    else:
                        bus_nr = bus_nr_org
                    # Initial start time for the first journey
                    start_time = datetime.strptime("00:00:00", "%H:%M:%S") + timedelta(minutes=time_offset)
                    current_time = start_time
                    end_time = datetime.strptime("23:59:59", "%H:%M:%S")
                    while current_time <= end_time:
                        file.write(f"{journey_no};{current_time.strftime('%H:%M:%S')};{row['Line']};{bus_nr};{dir};{bus_tp};{1};{len(bus_route_list)}\n")
                        current_time += timedelta(minutes=freq)
                        journeys.append([journey_no, len(bus_route_list)])
                        journey_no += 1
           
            # Vehicle journey sections
            file.write("\n* Table: Vehicle journey sections\n$VEHJOURNEYSECTION:VEHJOURNEYNO;NO;FROMTPROFITEMINDEX;TOTPROFITEMINDEX;VALIDDAYSNO\n")
            index=1
            for jouney_index in journeys:
                file.write(f"{jouney_index[0]};{1};{1};{jouney_index[1]};1\n")
    
def generate_Visum_network_net(df_distance,network_no,num_routes, max_stops_per_route, net_file, stops = get_all_stop_no(), headway = "NaN", Tsys = "B", seeding = False):
    """
    Generate a Visum timetable and save it as .net file

    :param num_routes:
    :param max_stops_per_route:
    :param net_file:
    :param stops: the stops you want to generate routes from, default is all stops in network
    :return:
    """

    bus_routes = generate_bus_routes(df_distance,stops, num_routes, max_stops_per_route)
    bus_nr = []
    for i in range(num_routes):
        if i >= 10:
            bus_nr.append("1" + str(i + 10) + ("9" if seeding else ""))
        else:
            bus_nr.append("11" + str(i) + ("9" if seeding else ""))
    lines = [{'NAME': 'ORG_1', 'TSYSCODE': Tsys, 'FARESYSTEMSET': '', 'VEHCOMBNO': ''}]
    
    # Preparing data for DataFrame
    data = {
        'NET': [network_no] * num_routes,
        'Line': ['ORG_1'] * num_routes,
        'TSYSCODE': [Tsys] * num_routes,
        'FARESYSTEMSET': [''] * num_routes,
        'VEHCOMBNO': [''] * num_routes,
        'Bus_nr': bus_nr,
        'Bus_tp': ["TP" + nr for nr in bus_nr],
        'Bus_routes': bus_routes,
        'frequency': [1] * num_routes,
        'time_offset': [0] * num_routes,
    }

    # Create DataFrame
    network_data = pd.DataFrame(data)
    
    
    
    network_row = network_data.groupby(['NET', 'Line', 'TSYSCODE', 'FARESYSTEMSET','VEHCOMBNO']).agg({
    'Bus_nr': lambda x: list(x),
    'Bus_tp': lambda x: list(x),
    'Bus_routes': lambda x: list(x),
    'frequency': lambda x: list(x),
    'time_offset': lambda x: list(x)
    }).reset_index()
    save_as_net_file(net_file, network_row,selected_row=0, headway=headway)
    return network_row
import warnings

def generate_intial_population(pop_size, num_routes, max_stops_per_route, net_file, distance_matrix, stops = get_all_stop_no(), headway = "NaN", Tsys = "B", seeding = False):
    """
    Generate a dataframe with a intial populaiton and score
    :pop_size: population size
    :param num_routes:
    :param max_stops_per_route:
    :param net_file:
    :return:
    """

    warnings.filterwarnings('ignore', category=FutureWarning)
    population_df = pd.DataFrame(columns=['NET','Score', 'Line', 'TSYSCODE', 'FARESYSTEMSET', 'VEHCOMBNO','Bus_nr', 'Bus_tp', 'Bus_routes', 'frequency', 'time_offset'])
    for i in range(pop_size):
        network_df = generate_Visum_network_net(distance_matrix,i,num_routes, max_stops_per_route,net_file,stops, headway, Tsys, seeding)
        remove_line_routes()
        load_net_file(net_file)

        Visum.Procedures.Execute()

        score = Visum.Net.AttValue('Score')
        network_df.insert(1,"Score",score)
        population_df = pd.concat([population_df, network_df], ignore_index=True)
        #print(i, cp_score)
    #print(population_df)
    return population_df
    
def uniform_crossover(routes1, routes2):
    # Initialize the offspring with empty lists
    child1_routes = []
    child2_routes = []

    # For each route, randomly choose which parent it comes from
    for i in range(len(routes1)):
        if random.random() < 0.5:
            child1_routes.append(list(routes1[i]))  # Use list() to create a copy
            child2_routes.append(list(routes2[i]))  # Use list() to create a copy
        else:
            child1_routes.append(list(routes2[i]))  # Use list() to create a copy
            child2_routes.append(list(routes1[i]))  # Use list() to create a copp
    return child1_routes, child2_routes


import random

import random

def mutate_route(route, all_stops, stops_per_route, mutation_rate, distance_matrix):
    if random.random() < mutation_rate:  # Check if mutation should occur
        selected_route_index = random.randint(0, len(route) - 1)  # Select a sub-route randomly
        selected_route = route[selected_route_index]
        
        # Decide mutation type based on sub-route length constraints
        if len(selected_route) < 5:
            mutation_type = 'insert'  # Only insert if sub-route is too short
        elif len(selected_route) >= stops_per_route:
            mutation_type = 'remove'  # Only remove if sub-route is at max length
        else:
            mutation_type = random.choice(['insert', 'remove'])  # Both options are viable
        
        if mutation_type == 'insert':
            # Only consider stops that are not already in the route
            potential_stops = [stop for stop in all_stops if stop not in selected_route]
            
            if potential_stops:  # Ensure there are stops to add
                # Choose between inserting before the first stop or after the last stop
                if random.random() < 0.5:
                    # Insert before the first stop
                    insert_position = 0
                else:
                    # Insert after the last stop
                    insert_position = len(selected_route)
                
                # No need to find the closest stops as insertion is at the beginning or end
                new_stop = random.choice(potential_stops)
                selected_route.insert(insert_position, new_stop)

        elif mutation_type == 'remove' and len(selected_route) > 2:
            # Choose to remove a stop that is not the first or last stop
            remove_position = random.randint(1, len(selected_route) - 2)
            del selected_route[remove_position]
        
        route[selected_route_index] = selected_route  # Update the mutated sub-route back into the route
    return route

    
def mutate_time_offset(time_offset_list, mutation_rate):
    #print("offset")
    #print(time_offset_list)
    """
    Mutates the offset by randomly adding or subtracting one minute, ensuring offset remain > 0.
    
    :param offset: List of offset values for each route.
    :param mutation_rate: Probability of mutation occurring for each offset.
    :return: Mutated list of offset.
    """
    mutated_time_offset_list = []
    for offsets in time_offset_list:  # Iterate over each list of offset
        mutated_time_offset = []
        for offset in offsets:  # Iterate over each offset value
            if random.random() < mutation_rate:  # Mutation occurs
                mutation_action = random.choice(["add", "subtract"])
                if mutation_action == "add":
                    mutated_time_offset.append(offset + 1)
                elif mutation_action == "subtract" and offset > 1:  # Ensure offset remains positive
                    mutated_time_offset.append(offset - 1)
                else:
                    mutated_time_offset.append(offset)
            else:
                mutated_time_offset.append(offset)  # No mutation
        mutated_time_offset_list.append(mutated_time_offset)
    #print(mutated_time_offset_list)
    return mutated_time_offset_list


def mutate_frequency(frequency_list, possible_frequencies, mutation_rate):
    #print("freq")
    #print(frequency_list)
    """
    Mutates the frequency list for each bus route.

    :param frequency_list: A list of frequencies for each bus route.
    :param possible_frequencies: A list of possible frequencies to choose from.
    :param mutation_rate: The probability of mutation occurring for each frequency in the list.
    :return: A mutated list of frequencies.
    """
    mutated_frequency_list = []
    for frequencies in frequency_list:
        mutated_frequency = []
        for frequency in frequencies:
            if random.random() < mutation_rate:
                new_frequency = random.choice([f for f in possible_frequencies if f != frequency])
                mutated_frequency.append(new_frequency)
            else:
                mutated_frequency.append(frequency)
        mutated_frequency_list.append(mutated_frequency)
    #print(mutated_frequency_list)
    return mutated_frequency_list


from tqdm import tqdm
def genetic_algorithm(num_generations = 1, population_size = 10, num_routes = 6, stops_per_route = 3, net_file="Nan",
                      stops = get_all_stop_no(), dynamic_mutation = True, start_rate = 0.01,change_rate = 0.005,end_rate = 0.005, 
                      seeding = False, headway = "NaN", Tsys = "B"):


    distance = helpers.GetSkimMatrixRaw(Visum, 18)
    df_distance = pd.DataFrame(distance)
    new_index_numbers = list(range(1, len(distance) + 1))
    # Set the DataFrame's index and columns to match stop numbers.
    df_distance.index = new_index_numbers
    df_distance.columns = new_index_numbers

    original_jrt = helpers.GetSkimMatrixRaw(Visum, 2)
    df_original_jrt = pd.DataFrame(original_jrt)
    new_index_numbers = list(range(1, len(original_jrt) + 1))
    # Set the DataFrame's index and columns to match stop numbers.
    df_original_jrt.index = new_index_numbers
    df_original_jrt.columns = new_index_numbers

    population = generate_intial_population(population_size, num_routes, stops_per_route, net_file,df_distance,stops, headway, Tsys, seeding)
    generation_results = []
    best_networks = pd.DataFrame()
    mutation_rate = start_rate
    possible_frequencies = [0, 1/6,1/3,0.5,1,2,4,8]

    for generation in tqdm(range(num_generations), desc="Generation"):
        if (generation + 1) % 25 == 0:
            # Fetch the current JRT matrix
            save_as_net_file(net_file, best_networks.iloc[-1:],selected_row=0, headway=headway)
            load_net_file(net_file)
            Visum.Procedures.Execute()
            current_jrt = helpers.GetSkimMatrixRaw(Visum, 2)
            df_current_jrt = pd.DataFrame(current_jrt, index=new_index_numbers, columns=new_index_numbers)

            # Calculate the percentage change for each cell from the original
            percent_change = np.abs((df_current_jrt - df_original_jrt) / df_original_jrt) * 100
            
            # Determine if the average percentage change across all cells exceeds 5%
            average_percent_change = np.nanmean(percent_change.values)  # Using np.nanmean to safely ignore NaN values
            print(f"test jrt generation: {generation+1}")
            if average_percent_change >= 5:
                Visum_prt.Procedures.Execute()
                df_original_jrt = df_current_jrt.copy()
                print(f"successfull jrt generation: {generation+1}, at average change of: {average_percent_change}")

        if dynamic_mutation == True:
            mutation_rate-=change_rate
            mutation_rate = max(mutation_rate, end_rate)
            
        population.sort_values(by="Score", ascending=True, inplace=True)
        
        if len(population) > (population_size // 2): # Elitism: Take the top 50% of the networks as elites
            elite_count = (population_size // 2)
            if seeding == True:
                genetic_variation_count = (population_size // 10)
        # If the population is too small due to purge if identical genes we fill the rest of the population 
        # With new chromosomes
        else: 
            elite_count = len(population)
            if seeding == True:
                genetic_variation_count = 2 #(population_size // 2)-elite_count
        
        elite_population = population.head(elite_count).copy()
        if seeding == True:
            genetic_variation_population = generate_intial_population(genetic_variation_count, num_routes, stops_per_route,net_file,df_distance,stops, headway, Tsys, seeding)
            elite_population = pd.concat([elite_population, genetic_variation_population], ignore_index=True)
        offspring_population = pd.DataFrame()

        while len(offspring_population) <= population_size - len(elite_population):
            # Randomly select two parents from the elite population
            parents = elite_population.sample(2, replace=False)
            parent1, parent2 = parents.iloc[0:1], parents.iloc[1:2]
    
            # Perform crossover on the parent routes to generate offspring routes
            child1_routes, child2_routes = uniform_crossover(parent1['Bus_routes'].values[0], parent2['Bus_routes'].values[0])

            child1 = parent1.copy()
            child2 = parent2.copy()

            child1.at[child1.index[0], 'Bus_routes'] = mutate_route(child1_routes, stops, stops_per_route, mutation_rate, df_distance)
            child2.at[child2.index[0], 'Bus_routes'] = mutate_route(child2_routes, stops, stops_per_route, mutation_rate, df_distance)
            
            if headway == "NaN":
                child1['time_offset'] = mutate_time_offset(child1['time_offset'], mutation_rate)
                child2['time_offset'] = mutate_time_offset(child2['time_offset'], mutation_rate)
            
            #print("frequency before: ", child1['frequency'])
            child1['frequency'] = mutate_frequency(child1['frequency'], possible_frequencies, mutation_rate)
            child2['frequency'] = mutate_frequency(child2['frequency'], possible_frequencies, mutation_rate)
            #print("frequency after: ", child1['frequency'])
            #save .NET
            save_as_net_file(net_file, child1,selected_row=0, headway=headway)
            remove_line_routes()
            # Load the NET in VISUM and run procedures replace score
            load_net_file(net_file)
            Visum.Procedures.Execute()
            #demand = helpers.GetSkimMatrixRaw(Visum, 1)
            #df_demand = pd.DataFrame(demand)
            #jrt = helpers.GetSkimMatrixRaw(Visum, 2)
            #df_jrd = pd.DataFrame(jrt)
            score = Visum.Net.AttValue('Score')
            child1["Score"]=score
            
            #save .NET
            save_as_net_file(net_file, child2,selected_row=0, headway=headway)
            remove_line_routes()
            # Load the NET in VISUM and run procedures replace score
            load_net_file(net_file)
            Visum.Procedures.Execute()
            #demand = helpers.GetSkimMatrixRaw(Visum, 1)
            #df_demand = pd.DataFrame(demand)
            #jrt = helpers.GetSkimMatrixRaw(Visum, 2)
            #df_jrd = pd.DataFrame(jrt)
            score = Visum.Net.AttValue('Score')
            child2["Score"]=score
            offspring_population = pd.concat([offspring_population, child1, child2], ignore_index=True)

        population = pd.concat([elite_population, offspring_population], ignore_index=True)
        
        population.sort_values(by="Score", ascending=True, inplace=True)
        
        best_network = population.iloc[0:1]
        best_networks =  pd.concat([best_networks, best_network], ignore_index=True)
        print(best_network)
        if generation >= 100 and best_networks.iloc[-1]['Score'] == best_networks.iloc[-101]['Score']:
            print(f"Terminating early at generation {generation + 1} due to no improvement over the last 20 generations.")
            break
    save_as_net_file(net_file, best_network,selected_row=0, headway=headway)
    remove_line_routes()
    # Load the NET in VISUM and run procedures replace score
    load_net_file(net_file)
    Visum.Procedures.Execute()
    final_score = Visum.Net.AttValue('Score')
    print("final Score:", final_score)
    return best_networks