#!/usr/bin/env python
# coding: utf-8

# ### Computational Guided Inquiry for Modeling Earth's Climate (Neshyba, 2025)
#
# # Cambio Comparisons
# This code takes as input a user-generated emission scenario and runs four versions of Cambio:
#
# - Cambio 1.0 has the five basic equations of motion, with $CO_2$ fertilization but no other feedbacks
# - Cambio 2.0 adds in Henry's Law feedbacks
# - Cambio 3.0 adds in ice-albedo feedback
# - Cambio 4.0 adds in terrestrial sequestion feedback that reduces $CO_2$ fertilization
#
# The code then runs the four simulations, and compares the output of a selected two of them.

# In[2]:


import numpy as np
import matplotlib.pyplot as plt
import meclib as CL


# In[3]:


# get_ipython().run_line_magic('matplotlib', 'inline')


# ### Loading your emission scenario
# In the cell below, load in your scheduled flows file. It'll be most convenient if you use the following naming convention:
#
#     time, eps, epsdictionary_from_file = CL.LoadMyScenario('...')
#
# (but of course supplying the name of a particular emission scenario).

# In[5]:


filename = "Peaks_in_2040_LTE_default.pkl"
time, eps, epsdictionary_from_file = CL.LoadMyScenario(filename, verbose=True)


# ### Creating a dictionary for climate parameters consistent with this emission scenario
# In the cell below, we use the CreateClimateParams function to create a dictionary of climate parameters.

# In[7]:


ClimateParams = CL.CreateClimateParams(epsdictionary_from_file)


# ### Running Cambio
# The cell below runs Cambio versions 1-4.

# In[9]:


CS_Cambio1_list = CL.run_Cambio(
    CL.PropagateClimateState_Cambio1, ClimateParams, time, eps
)
CS_Cambio2_list = CL.run_Cambio(
    CL.PropagateClimateState_Cambio2, ClimateParams, time, eps
)
CS_Cambio3_list = CL.run_Cambio(
    CL.PropagateClimateState_Cambio3, ClimateParams, time, eps
)
CS_Cambio4_list = CL.run_Cambio(
    CL.PropagateClimateState_Cambio4, ClimateParams, time, eps
)


# ### Individual reports using display

# In[11]:


print("Starting state:")
print(CS_Cambio1_list[0])
print("Ending state:")
print(CS_Cambio1_list[-1])


# ### Individual reports using CS_list_plots

# In[13]:


items_to_plot = [
    ["C_atm", "C_ocean"],
    ["F_ha", "F_ocean_net", "F_land_net"],
    "T_anomaly",
]
CL.CS_list_plots(CS_Cambio1_list, "Cambio1.0", items_to_plot)


# ### Comparison plots using CS_list_compare

# In[15]:


items_to_plot = [
    ["C_atm", "C_ocean"],
    ["F_ha", "F_ocean_net", "F_land_net"],
    "T_anomaly",
    "OceanSurfacepH",
]
CL.CS_list_compare(
    [CS_Cambio1_list, CS_Cambio4_list],
    ["Cambio1.0", "Cambio4.0"],
    items_to_plot,
)
