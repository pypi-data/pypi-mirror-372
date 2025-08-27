"""
                           
 _|      _|      _|_|_|_|  
 _|_|  _|_|      _|        
 _|  _|  _|      _|_|_|    
 _|      _|      _|        
 _|      _|  _|  _|    _|  
                           
 Material        Fingerprinting

"""

import matplotlib.pyplot as plt
import numpy as np
import warnings

from material_fingerprinting.Database import Database
from material_fingerprinting.Experiment import Experiment
from material_fingerprinting.Material import Material
from material_fingerprinting.Measurement import Measurement

# colors extracted from the tab20 colormap
tab20blue = [31/255, 119/255, 180/255]
tab20red = [214/255, 39/255, 40/255]

def discover(measurement_list,database="HEI",verbose=True,first=True,plot=True):

    if verbose and first:
        print("\n=== Material Fingerprinting ===")
        print("Contact moritz.flaschel@fau.de for help and bug reports.\n")

    # check data
    if not isinstance(measurement_list, list):
        if isinstance(measurement_list, Measurement):
            measurement_list = [measurement_list]
        else:
            raise TypeError("measurement_list must be a list of Measurement objects.")
    for m in measurement_list:
        if not isinstance(m, Measurement):
            raise TypeError("measurement_list must be a list of Measurement objects.")

    db = Database().load_pkl(database)

    measurement_experiment_name_list = [m.experiment_name for m in measurement_list]
    if not all(name in db.experiment_name_list for name in measurement_experiment_name_list):
        raise ValueError(f"The database does not contain fingerprints for the given measurements.")
    
    # assemble fingerprint of the measurement
    f = np.array([])
    for i, experiment_name in enumerate(db.experiment_name_list):
        if experiment_name in measurement_experiment_name_list:
            j = measurement_experiment_name_list.index(experiment_name)
            f_interp = np.interp(db.experiment_control_list[i], measurement_list[j].control, measurement_list[j].measurement, left=0.0, right=0.0)
            f = np.append(f,f_interp)
        else:
            f = np.append(f,np.zeros(db.fingerprints_list[i].shape[1]))

    # Material Fingerprinting
    print("\nMaterial Fingerprinting:")
    id, model_disc, parameters_disc = db.discover(f,verbose=True)

    # plot
    if plot: discover_plot(measurement_list,model_disc,parameters_disc)

    return model_disc, parameters_disc

def discover_plot(measurement_list,model_disc,parameters_disc):
    mat = Material(name=model_disc)

    # for m in measurement_list:
    #     r = np.abs(np.max(m.control) - np.min(m.control)) / 20
    #     s = 15
    #     exp = Experiment(name=m.experiment_name, control_min=np.min(m.control)-r, control_max=np.max(m.control)+r)
    #     mat = Material(name=model_disc)
    #     prediction = mat.conduct_experiment(exp, parameters=parameters_disc).squeeze()
    #     fig, ax = plt.subplots(1, 1, figsize=(6, 5))
    #     fig.suptitle("Discovered model: " + model_disc + " \n$W=$" + mat.get_formula(parameters_disc))
    #     ax.scatter(m.control, m.measurement, color=tab20blue, s=s, label='Data')
    #     ax.plot(exp.control, prediction, color=tab20red, linewidth=2, label='Discovered')
    #     ax.set_title(m.experiment_name)
    #     ax.set_xlabel(exp.control_str[0])
    #     ax.set_ylabel(exp.measurement_str[0])
    #     ax.legend()
    #     ax.grid(True)
    #     ax.minorticks_on() 
    #     ax.grid(True, which='minor', linestyle='--', color='lightgray', linewidth=0.5)
    #     fig.tight_layout()
    # plt.show()

    n_exp = len(measurement_list)
    fig, axes = plt.subplots(1, n_exp, figsize=(5*n_exp, 5), squeeze=False)
    fig.suptitle("Discovered model: " + model_disc + " \n$W=$" + mat.get_formula(parameters_disc))
    for i, m in enumerate(measurement_list):
        r = np.abs(np.max(m.control) - np.min(m.control)) / 20
        s = 15
        exp = Experiment(name=m.experiment_name, control_min=np.min(m.control)-r, control_max=np.max(m.control)+r)
        prediction = mat.conduct_experiment(exp, parameters=parameters_disc).squeeze()
        ax = axes[0, i]
        ax.scatter(m.control, m.measurement, color=tab20blue, s=s, label='Data')
        ax.plot(exp.control, prediction, color=tab20red, linewidth=2, label='Discovered')
        ax.set_title(m.experiment_name)
        ax.set_xlabel(exp.control_str[0])
        ax.set_ylabel(exp.measurement_str[0])
        ax.legend()
        ax.grid(True)
        ax.minorticks_on()
        ax.grid(True, which='minor', linestyle='--', color='lightgray', linewidth=0.5)
    fig.tight_layout()
    plt.show()

    return
