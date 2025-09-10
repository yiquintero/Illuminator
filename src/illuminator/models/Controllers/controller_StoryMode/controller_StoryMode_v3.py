from illuminator.builder import ModelConstructor

# construct the model
class Controller_StoryMode(ModelConstructor):
    """
    Controller for managing power flows between renewable generation, load, and battery storage.
    
    This controller determines how power should be distributed between renewable sources (wind, solar),
    load demands, and battery storage. It implements basic control logic for battery charging and
    discharging based on state of charge limits and power constraints.

    Parameters
    ----------
    soc_min : float
        Minimum state of charge of the battery before discharging stops (%)
    soc_max : float
        Maximum state of charge of the battery before charging stops (%)
    max_p : float
        Maximum power to/from the battery (kW)
    battery_active : bool
        Flag to enable/disable battery operation
    
    Inputs
    ----------
    physical_connections : list
        List of physical connections with ID's of the LED strips

    Outputs
    ----------
    None
    
    States
    ----------
    file_index_Load : int
        Index to select which load file to read from in the CSV model
        
    """
    parameters={}
    inputs={'physical_connections': []}
    outputs={}
    states={'file_index_Load': 0}

    # define other attributes
    time_step_size = 1
    time = None


    def __init__(self, **kwargs) -> None:
        """
        Initialize the Controller model with the provided parameters.

        Parameters
        ----------
        kwargs
        """
        super().__init__(**kwargs)
        self.file_indeces = {'file_index_Load': 0}


    def step(self, time: int, inputs: dict=None, max_advance: int=900) -> None:  # step function always needs arguments self, time, inputs and max_advance. Max_advance needs an initial value.
        """
        Advances the simulation one time step.
        """
        input_data = self.unpack_inputs(inputs, return_sources=True)  # make input data easily accessible
        self.time = time

        connections = self.determine_connectivity(input_data['physical_connections'])

        if ('PV_LED-0.time-based_0', 'Wind_LED-0.time-based_0') in connections or ('Wind_LED-0.time-based_0', 'PV_LED-0.time-based_0') in connections:
            print("PV and Wind connected")

        if time > 40:
            self.file_indeces['file_index_Load'] = 1
        else:
            self.file_indeces['file_index_Load'] = 0

        self.set_states(self.file_indeces)

        # return the time of the next step (time untill current information is valid)
        return time + self._model.time_step_size


    def determine_connectivity(self, physical_connections):
        """
        Determine the connectivity of the LED strips based on the provided physical connections.
        Each LED strip has an ID. If two models have the same ID, they are connected.
        This function function determines model-pairs that are connected based on their IDs.

        Parameters
        ----------
        physical_connections : dict
            

        Returns
        -------
        list of connections
        """
        connections = []
        for i, (id1, model1) in enumerate(zip(physical_connections['value'], physical_connections['sources'])):
            for id2, model2 in zip(physical_connections['value'][i+1:], physical_connections['sources'][i+1:]):
                common_ids = list(set(id1) & set(id2))
                if len(common_ids) > 0 and model1 != model2:
                    connections.append((model1, model2))
        return connections
        