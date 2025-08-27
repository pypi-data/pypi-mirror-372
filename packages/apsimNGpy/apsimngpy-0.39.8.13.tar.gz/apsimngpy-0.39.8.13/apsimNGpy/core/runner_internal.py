import os
from apsimNGpy.core_utils.utils import timer
from apsimNGpy.core.core import Models, CoreModel, CastHelper
from apsimNGpy.core_utils.database_utils import read_db_table, get_db_table_names
from System.Collections.Generic import List
from System import Double, String
from APSIM.Core import Node
from System.IO import Path
from build.lib.apsimNGpy.core.model_tools import find_child

dotnet_list = List[String]()
dotnet_list.Add('Simulation')
path=  {}
@timer
def runner():
    # Create the APSIM model
    model = CoreModel('Maize')

    # Find simulation and datastore components
    sim = find_child(model.Simulations, 'Models.Core.Simulation', 'Simulation')
    datastore = find_child(model.Simulations, 'Models.Storage.DataStore', "DataStore")
    model.add_db_table(variable_spec=['[Maize].Total.Wt'], rename='my_table', simulation_name='Simulation', set_event_names=['[Clock].EndOfYear', '[Maize].Harvesting'])
    # Cast datastore to .NET DataStore and configure it
    cas = CastHelper.CastAs[Models.Storage.DataStore](datastore)

    cas.Open()
    cas.UseInMemoryDB = False

    # Cast simulations to IModel
    imodel = CastHelper.CastAs[Models.Core.IModel](model.Simulations)

    # Prepare the model path list (assumes dotnet_list is a List<string>)

    dotnet_list = List[String]()


    # Run the simulation using Models.Core.Run.Runner
    runner = Models.Core.Run.Runner(model.Simulations,  True, False, False, None)
    for i in dir(cas):
        print(i)
    result = runner.Run()

    # Finalize and clean up
    cas.Finalize()
    # runner.Stop()
    cs_sims = List[Models.Core.Simulation]()
    s = find_child(model.Simulations, 'Models.Core.Simulation', 'Simulation')
    cs_sims.Add(s)
    print("Progress:", runner.Progress)
    print("Status:", runner.Status)
    print("DB Path:", cas.FileName)
    print('simulations completed: ', runner.SimulationCompleted)
    print("elapsed time: ", runner.get_ElapsedTime())


    # Optionally store path in a global or passed dict

    path['p'] = cas.FileName

    # Print database contents (assumes get_db_table_names is defined elsewhere)
    print(get_db_table_names(model.datastore))


    # Close the datastore
    cas.Close()


if __name__ == '__main__':
    runner()
    model = CoreModel('Maize', out_path=os.path.abspath('xxxx.apsimx'))
    datastore = find_child(model.Simulations, 'Models.Storage.DataStore', "DataStore")
    cas =CastHelper.CastAs[Models.Storage.DataStore](datastore)