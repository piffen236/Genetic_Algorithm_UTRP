# GUI 
#
# So th eprogram is buildup on two main parts the GUI.py and the ga_funcitons.py
# Using the program:
# 1. Launch GUI.py
# 2. Open .ver file (Tested on Mandl_Visum - Timetable, Mandl_Visum - Headway & Koll_Bas2016 - edit)
#          Never work on the original file as errors while running can corrupt the .ver file
# 3. select relevant stops or open csv file with relevant stops
# 4. set the settings for your network & algorithm
# 5. run
#
#Errors
# One problem that can be incountered is :AttributeError: module 'win32com.gen_py.4BC04EF2-4B3B-4FD5-ABEA-FFF08919EA2Bx0x24x0' has no attribute 'CLSIDToClassMap'
# If so run this in console: python -m win32com.client.makepy
# And select PTV Visum Object Library...

import customtkinter as ctk
from tkinter import filedialog, Canvas, Frame, Scrollbar, IntVar, font, PhotoImage,StringVar,ttk
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import ga_functions

# Define theme colors
DARK_BG = "#242424"
LIGHT_BG = "#2b2b2b"
TEXT_COLOR = "white"
BUTTON_COLOR = "#2fa572"

def update_dropdown(values):
    global dropdown_width
    # Clear previous entries and their associated variables
    for widget in inner_frame.winfo_children():
        widget.destroy()
    Stop_list.clear()

    # Populate the dropdown with new values
    for value in values:
        var = IntVar(value=0)
        chk = ctk.CTkCheckBox(inner_frame, text=str(value), variable=var, onvalue=1, offvalue=0, text_color="dark gray",font=("Arial", 15), fg_color=None)
        chk.pack(anchor='w', padx=5, pady=2, fill='x')
        Stop_list.append((var, value))  # Store the variable and its associated value

    # Update the scrolling region to encompass the inner frame
    canvas.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

def import_file():
    global selected_file_path
    selected_file_path = filedialog.askopenfilename()
    if selected_file_path:
        print("File selected:", repr(selected_file_path))
        values = ga_functions.import_visum(selected_file_path)
        update_dropdown(values)
        dropdown_frame.grid(row=4, column=0, pady=10, padx=10, sticky="ew")  # Use grid to show dropdown frame
def import_prt_file():
    global selected_file_path_prt
    selected_file_path_prt = filedialog.askopenfilename()
    if selected_file_path_prt:
        print("PrT File selected:", repr(selected_file_path_prt))
        ga_functions.import_visum_prt(selected_file_path_prt)

def display_loading_message(results_tab):
    # Clear the results tab and show loading message
    for widget in results_tab.winfo_children():
        widget.destroy()
    loading_label = ctk.CTkLabel(results_tab, text="Loading...", font=("Arial", 15), fg_color=LIGHT_BG, text_color=TEXT_COLOR)
    loading_label.pack(pady=20)

def update_results_tab(data, results_tab, plot_data):
    # Clear the results tab
    for widget in results_tab.winfo_children():
        widget.destroy()

    # Style configuration for Treeview
    tree_style = ttk.Style()
    tree_style.configure("Custom.Treeview", background=DARK_BG, foreground=TEXT_COLOR, fieldbackground=DARK_BG, rowheight=25)
    tree_style.configure("Custom.Treeview.Heading", font=('Arial', 10, 'bold'), background=LIGHT_BG, foreground=TEXT_COLOR)
    tree_style.map("Custom.Treeview", background=[('selected', BUTTON_COLOR)])

    # Create a Treeview widget with limited height
    tree = ttk.Treeview(results_tab, style="Custom.Treeview", columns=('Parameter', 'Value'), height=3)
    tree.column("#0", width=0, stretch=ctk.NO)
    tree.column('Parameter', anchor=ctk.W, width=120)
    tree.column('Value', anchor=ctk.W, width=180)

    # Create headings
    tree.heading("#0", text='', anchor=ctk.W)
    tree.heading('Parameter', text='Parameter', anchor=ctk.W)
    tree.heading('Value', text='Value', anchor=ctk.W)

    # Adding data to the treeview
    for key, value in data.items():
        tree.insert('', ctk.END, values=(key, value))

    # Packing the Treeview
    tree.pack(pady=20, padx=20, fill='x', expand=True)

    # Create a frame for the plot
    plot_frame = ctk.CTkFrame(results_tab)
    plot_frame.pack(fill='both', expand=True)

    # Create a figure and a subplot
    fig, ax = plt.subplots(figsize=(5, 4))
    
    
    ax.plot(plot_data.index, plot_data['Score'], marker='o')
    
    # Add labels and title
    ax.set_xlabel('Generation')
    ax.set_ylabel('Score')
    ax.set_title('Score Over Time')
    
    # Create a canvas and add the plot to it
    canvas = FigureCanvasTkAgg(fig, master=plot_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill='both', expand=True)

def run_ga():
    # Disable the Run button to prevent multiple clicks
    print_button.configure(state="disabled")
    display_loading_message(results_tab)

    try:
        selected_items = [value for (var, value) in Stop_list if var.get() == 1]
        input_data = {
            "Selected Stops": selected_items,
            "Number of Buses": num_buses.get(),
            "Number of Stops per Bus": num_stops_per_bus.get(),
            "Number of Iterations": num_itterations.get(),
            "Population size": pop_size.get(),
            "Dynamic Mutation Rate Enabled": dynamic_mutation_rate.get() == "on",
            "Start Rate": start_rate.get(),
            "Change Rate": change_rate.get() if dynamic_mutation_rate.get() == "on" else None,
            "End Rate": end_rate.get() if dynamic_mutation_rate.get() == "on" else None,
            "Seeding Enabled": seeding.get() == "on",
            "Headway-Based": headway_value.get() != "NaN",
            "TSYSCODE": Tsys_value.get()
        }

        plot_data = ga_functions.genetic_algorithm(int(num_itterations.get()), int(pop_size.get()) ,int(num_buses.get()) ,int(num_stops_per_bus.get()), selected_file_path, selected_items, dynamic_mutation_rate.get() == "on", float(start_rate.get()),float(change_rate.get()),float(end_rate.get()), seeding.get() == "on", headway_value.get(), Tsys_value.get())
        #print(plot_data)
        update_results_tab(input_data, results_tab,plot_data)

        # Switch to the results tab
        notebook.select(results_tab)
    finally:
        # Re-enable the Run button after the operations are done
        print_button.configure(state="normal")


def adjust_dropdown_width():
    dropdown_width = int(window.winfo_width() * 0.30) - scrollbar.winfo_width()
    # Update canvas width
    canvas.config(width=dropdown_width)
    # Update the frame width inside the canvas
    canvas.itemconfig(canvas_frame_id, width=dropdown_width)
def customize_notebook_style():
    style = ttk.Style()
    style.theme_create("customtkinter", parent="alt", settings={
        "TNotebook": {"configure": {"background": DARK_BG, "borderwidth": 0}},
        "TNotebook.Tab": {
            "configure": {"padding": [5, 1], "background": LIGHT_BG, "foreground": TEXT_COLOR, "focuscolor": ""},  # Set focuscolor to an empty string
            "map": {
                "background": [("selected", BUTTON_COLOR)],
                "expand": [("selected", [1, 1, 1, 0])]
            }
        }
    })
    style.theme_use("customtkinter")
def on_closing():
    # Close all matplotlib figures
    plt.close('all')
    # Destroy the main window
    window.destroy()
def toggle_all_checks():
    global all_selected
    new_state = not all_selected  # Determine the new state for checkboxes
    
    for var, _ in Stop_list:
        var.set(1 if new_state else 0)  # Set all checkboxes to the new state
    
    all_selected = new_state  # Invert the tracking variable for the next toggle
def select_stops_from_csv():
    csv_file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if not csv_file_path:  # User canceled the dialog
        return

    try:
        import csv
        with open(csv_file_path, newline='') as csvfile:
            reader = csv.reader(csvfile)
            relevant_stops = set() 

            for row in reader:
                try:
                    stop_number = int(row[0])
                    relevant_stops.add(stop_number)
                except ValueError:
                   
                    continue

        # Select the checkboxes based on the stops in the CSV
        for var, value in Stop_list:
            if value in relevant_stops:
                var.set(1)  # Select the checkbox
            else:
                var.set(0)  # Deselect the checkbox
    except Exception as e:
        print(f"Error reading the CSV file: {e}")


def main():

    global window, import_button, dropdown_frame, canvas, inner_frame, Stop_list, canvas_frame_id, scrollbar, num_buses, num_stops_per_bus, num_itterations, dynamic_mutation_rate, seeding,results_tab, notebook,print_button, start_rate, change_rate, end_rate, pop_size,headway_value, all_selected, Tsys_value    
    Stop_list = []  # Initialize list to track checkboxes and their variables


    ctk.set_appearance_mode("dark")  # Set the theme of customtkinter
    ctk.set_default_color_theme("green")
    window = ctk.CTk()
    window.protocol("WM_DELETE_WINDOW", on_closing)
    window.title("Genetic Algorithm GUI")
    window.geometry("1000x550")
    window.resizable(False, False)  # Lock the window size
    #current_dir = os.path.dirname(__file__)  # Get the directory where the script is located
    #icon_path = os.path.join(current_dir, 'ICON.png') 
    #window.iconbitmap()
    #window.iconphoto(False, PhotoImage(file=icon_path))
    
    # Configure the grid weights
    window.grid_rowconfigure(0, weight=1)

    customize_notebook_style()
    
    # Notebook for tabs
    notebook = ttk.Notebook(window)
    notebook.grid(row=0, column=0, columnspan=4, pady=10, padx=10, sticky="nsew")

    # Tab for Controls
    controls_tab = ctk.CTkFrame(notebook)
    notebook.add(controls_tab, text="Controls")

    # Tab for Results
    results_tab = ctk.CTkFrame(notebook)
    notebook.add(results_tab, text="Results")

    controls_tab.grid_rowconfigure(0, weight=0)
    controls_tab.grid_columnconfigure(0, weight=1)

    results_tab.grid_rowconfigure(0, weight=1)
    results_tab.grid_columnconfigure(0, weight=1)

    # Create a frame for the import button within the controls_tab
    import_frame = ctk.CTkFrame(controls_tab,fg_color=LIGHT_BG)
    import_frame.grid(row=0, column=0, pady=10, padx=10, sticky="ew")
    import_frame.grid_columnconfigure(0, weight=1)  # Button column
    import_frame.grid_columnconfigure(1, weight=1)  # Empty column to take up the rest of the space

    # place the import button in the first column of the import_frame
    import_button = ctk.CTkButton(import_frame, text="Import PuT", command=import_file,width=100)
    import_button.grid(row=0, column=0, sticky="w")  # Stick to the west side
    
    selected_file_path_prt = None
    import_prt_button = ctk.CTkButton(import_frame, text="Import PrT", command=import_prt_file, width=100)
    import_prt_button.grid(row=0, column=1, sticky="w", padx=(0,10)) 

    num_buses = StringVar(value='6')
    num_stops_per_bus = StringVar(value='8')
    num_itterations = StringVar(value='5')
    pop_size = StringVar(value='10')
    dynamic_mutation_rate = StringVar(value="on")
    seeding = StringVar(value="off")

    # Add a thin line under the import button
    line = ctk.CTkFrame(controls_tab, height=2, fg_color="gray")
    line.grid(row=1, column=0, columnspan=1, sticky="ew")  # Stretch the line across the grid cell eastwest
    line = ctk.CTkFrame(controls_tab, height=2, fg_color="gray")
    line.grid(row=1, column=1, columnspan=1, sticky="ew")
    line = ctk.CTkFrame(controls_tab, height=2, fg_color="gray")
    line.grid(row=1, column=2, columnspan=1, sticky="ew")
    
    # Add a heading label above the dropdown list
    heading_label = ctk.CTkLabel(controls_tab, text=" Available stops", text_color="white", font=("Arial", 25),fg_color=None)
    heading_label.grid(row=3, column=0, pady=10, padx=10, sticky="w")
    

    # Frame to act as a dropdown menu container with scrollbar
    dropdown_frame = ctk.CTkFrame(controls_tab)
    dropdown_frame.grid(row=4, column=0, pady=10, padx=10, sticky="ew")  # Use grid to show dropdown frame

    # Create a canvas within the dropdown frame for scrollable content
    canvas = Canvas(dropdown_frame, highlightthickness=0)
    canvas.grid(row=0, column=0, sticky="nswe")

    # Add a scrollbar to the canvas
    scrollbar = Scrollbar(dropdown_frame, orient="vertical", command=canvas.yview)
    scrollbar.grid(row=0, column=1, sticky="ns")

    # Configure canvas to be scrollable
    canvas.configure(yscrollcommand=scrollbar.set)

    # Create a frame within the canvas for the checkable items
    inner_frame = Frame(canvas)
    canvas_frame_id = canvas.create_window((0, 0), window=inner_frame, anchor="nw")
    inner_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    # Adjust the width of the dropdown whenever the window size changes
    window.bind('<Configure>', lambda e: adjust_dropdown_width())
    
    #chack all stops
    Stop_list = []
    all_selected = False

    toggle_btn_frame = ctk.CTkFrame(dropdown_frame, fg_color='transparent', height=40)
    toggle_btn_frame.grid(row=1, column=0, pady=(5, 5), sticky="ew")
    toggle_btn_frame.grid_propagate(False)
    toggle_btn_frame.grid_columnconfigure(0, weight=1) 
    toggle_btn_frame.grid_columnconfigure(1, weight=1) 

    toggle_all_btn = ctk.CTkButton(toggle_btn_frame, text="Select All", command=toggle_all_checks)
    toggle_all_btn.grid(row=0, column=0, pady=(5, 5),padx=(5,5))

    #relevant sotps
    select_relevant_btn = ctk.CTkButton(toggle_btn_frame, text="Select From CSV", command=select_stops_from_csv)
    select_relevant_btn.grid(row=0, column=1, pady=(5, 5),padx=(5,0))

    # Row for input fields
    input_fields_frame = ctk.CTkFrame(controls_tab, fg_color='transparent')
    input_fields_frame.grid(row=4, column=1, padx=10, sticky="nsew")

    # Number of buses input
    buses_frame = ctk.CTkFrame(input_fields_frame, fg_color='transparent')
    buses_frame.pack(fill='x', pady=2)
    buses_label = ctk.CTkLabel(buses_frame, text="Number of buses   ")
    buses_label.pack(side='left')
    buses_input = ctk.CTkEntry(buses_frame, textvariable=num_buses)
    buses_input.pack(side='right', fill='x', expand=True)

    # Max number of stops per bus input
    max_stops_frame = ctk.CTkFrame(input_fields_frame, fg_color='transparent')
    max_stops_frame.pack(fill='x', pady=10)
    max_stops_label = ctk.CTkLabel(max_stops_frame, text="Max number of stops per bus   ")
    max_stops_label.pack(side='left')
    max_stops_input = ctk.CTkEntry(max_stops_frame, textvariable=num_stops_per_bus)
    max_stops_input.pack(side='right', fill='x', expand=True)

    # Iterations input
    iterations_frame = ctk.CTkFrame(input_fields_frame, fg_color='transparent')
    iterations_frame.pack(fill='x', pady=2)
    iterations_label = ctk.CTkLabel(iterations_frame, text="Iterations   ")
    iterations_label.pack(side='left')
    iterations_input = ctk.CTkEntry(iterations_frame, textvariable=num_itterations)
    iterations_input.pack(side='right', fill='x', expand=True)
    
    # Iterations input
    population_frame = ctk.CTkFrame(input_fields_frame, fg_color='transparent')
    population_frame.pack(fill='x', pady=2)
    population_label = ctk.CTkLabel(population_frame, text="Population size   ")
    population_label.pack(side='left')
    population_input = ctk.CTkEntry(population_frame, textvariable=pop_size)
    population_input.pack(side='right', fill='x', expand=True)

    ENTRY_ENABLED_COLOR = "#343638"  
    ENTRY_DISABLED_COLOR = "#CCCCCC"

    def on_dynamic_mutation_toggle():
        if dynamic_mutation_rate.get() == "on":
            start_rate_input.configure(state='normal', fg_color=ENTRY_ENABLED_COLOR)
            change_rate_input.configure(state='normal', fg_color=ENTRY_ENABLED_COLOR)
            end_rate_input.configure(state='normal', fg_color=ENTRY_ENABLED_COLOR)
        else:
            start_rate_input.configure(state='normal', fg_color=ENTRY_ENABLED_COLOR)
            change_rate_input.configure(state='disabled', fg_color=ENTRY_DISABLED_COLOR)
            end_rate_input.configure(state='disabled', fg_color=ENTRY_DISABLED_COLOR)
    

    # Dynamic mutation rate switch
    dynamic_mutation_frame = ctk.CTkFrame(input_fields_frame, fg_color='transparent')
    dynamic_mutation_frame.pack(fill='x', pady=2)
    dynamic_mutation_label = ctk.CTkLabel(dynamic_mutation_frame, text="Dynamic Mutation Rate    " )
    dynamic_mutation_label.pack(side='left')
    dynamic_mutation_switch = ctk.CTkSwitch(dynamic_mutation_frame, text="", variable=dynamic_mutation_rate, onvalue="on", offvalue="off", command=on_dynamic_mutation_toggle)
    dynamic_mutation_switch.pack(side='right', fill='x', expand=True)

    # Start rate input

    start_rate = StringVar(value='0.5')
    change_rate = StringVar(value='0.005')
    end_rate = StringVar(value='0.01')

    start_rate_frame = ctk.CTkFrame(input_fields_frame, fg_color='transparent')
    start_rate_frame.pack(fill='x', pady=2)
    start_rate_label = ctk.CTkLabel(start_rate_frame, text="Start rate    ")
    start_rate_label.pack(side='left')
    start_rate_input = ctk.CTkEntry(start_rate_frame, textvariable=start_rate, state='disabled')
    start_rate_input.pack(side='right', fill='x', expand=True)

    # Change rate input
    change_rate_frame = ctk.CTkFrame(input_fields_frame, fg_color='transparent')
    change_rate_frame.pack(fill='x', pady=2)
    change_rate_label = ctk.CTkLabel(change_rate_frame, text="Change rate    ")
    change_rate_label.pack(side='left')
    change_rate_input = ctk.CTkEntry(change_rate_frame, textvariable=change_rate, state='disabled')
    change_rate_input.pack(side='right', fill='x', expand=True)

    # End rate input
    end_rate_frame = ctk.CTkFrame(input_fields_frame, fg_color='transparent')
    end_rate_frame.pack(fill='x', pady=2)
    end_rate_label = ctk.CTkLabel(end_rate_frame, text="End rate    ")
    end_rate_label.pack(side='left')
    end_rate_input = ctk.CTkEntry(end_rate_frame, textvariable=end_rate, state='disabled')
    end_rate_input.pack(side='right', fill='x', expand=True)
    on_dynamic_mutation_toggle()


    # Seeding switch
    seeding_frame = ctk.CTkFrame(input_fields_frame, fg_color='transparent')
    seeding_frame.pack(fill='x', pady=2)
    seeding_label = ctk.CTkLabel(seeding_frame, text="Seeding   ")
    seeding_label.pack(side='left')
    seeding_switch = ctk.CTkSwitch(seeding_frame, text="", variable=seeding, onvalue="on", offvalue="off")
    seeding_switch.pack(side='right', fill='x', expand=True)
    def on_headway_toggle():
        # Enable or disable the headway input based on the switch state
        if headway_based.get() == "on":
            headway_value_input.configure(state='normal', fg_color=ENTRY_ENABLED_COLOR) 
            headway_value.set("")
        else:
            headway_value_input.configure(state='disabled', fg_color=ENTRY_DISABLED_COLOR) 
            headway_value.set("NaN")

    # Additional variables for new features
    headway_based = StringVar(value="off")  # Toggle state for Headway-based option
    headway_value = StringVar(value="NaN")  # Value for Headway (NaN when toggled off)
    Tsys_value = StringVar(value="B")
    # Network Specifications frame
    network_specs_frame = ctk.CTkFrame(controls_tab, fg_color='transparent')
    network_specs_frame.grid(row=4, column=2, padx=10, sticky="nsew")  

    # Headway-based toggle
    headway_based_frame = ctk.CTkFrame(network_specs_frame, fg_color='transparent')
    headway_based_frame.pack(fill='x', pady=2)
    headway_based_label = ctk.CTkLabel(headway_based_frame, text="Headway-based On/Off    ")
    headway_based_label.pack(side='left')
    headway_based_switch = ctk.CTkSwitch(headway_based_frame, text ="", variable=headway_based, onvalue="on", offvalue="off", command=on_headway_toggle)
    headway_based_switch.pack(side='right', fill='x', expand=True)

    # Headway value input
    headway_value_frame = ctk.CTkFrame(network_specs_frame, fg_color='transparent')
    headway_value_frame.pack(fill='x', pady=2)
    headway_value_label = ctk.CTkLabel(headway_value_frame, text="Variable name \n [number of bus departures]:    ")
    headway_value_label.pack(side='left')
    headway_value_input = ctk.CTkEntry(headway_value_frame, textvariable=headway_value, state='disabled')  # Disabled by default
    headway_value_input.pack(side='right', fill='x', expand=True)

    # Initial call to set the headway input state correctly
    on_headway_toggle()
    print_button = ctk.CTkButton(controls_tab, text="Run", command=run_ga)
    print_button.place(relx=0.5, rely=0.95, anchor='center')

    # Headway value input
    Tsys_value_frame = ctk.CTkFrame(network_specs_frame, fg_color='transparent')
    Tsys_value_frame.pack(fill='x', pady=2)
    Tsys_value_label = ctk.CTkLabel(Tsys_value_frame, text="Variable name \n[TSYSCODE]:       ")
    Tsys_value_label.pack(side='left')
    Tsys_value_input = ctk.CTkEntry(Tsys_value_frame, textvariable=Tsys_value, ) 
    Tsys_value_input.pack(side='right', fill='x', expand=True)
    window.mainloop()

if __name__ == "__main__":
    main()
