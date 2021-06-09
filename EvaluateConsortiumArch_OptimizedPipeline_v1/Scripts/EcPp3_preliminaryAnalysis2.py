#!/usr/bin/python3

############ FLYCOP ############
# Author: Beatriz García-Jiménez, Iván Martín Martín
# April 2018, April 2021
################################

"""
EcPp3 - Glycosilation project. Preliminary Analysis of the configurationsResults.txt file:
    
    * ConfigurationsSummary_X_models.txt

"""


import re
import sys
import os.path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import seaborn as sns
# import shutil, errno
# import cobra
# import tabulate
# import getopt
# import copy
# import csv
# import math
# import cobra.flux_analysis.variability
# import massedit
# import subprocess
# import statistics
# import importlib
# import optlang
# import spec


# PARSING PARAMETERS
# -----------------------------------------------------------------------------
# Reading the arguments given by command line
cons_architecture_series = sys.argv[1]  # '2_models 3_models'
# Interesante conocer el número de runs totales (configuraciones totales)
# -----------------------------------------------------------------------------

cons_architecture_list = cons_architecture_series.split()
configResults_excel = "configurationResults_consArchitecture.xlsx"


###############################################################################
###############################################################################
# # BLOCK 3: FURTHER CLASSIFYING RECORDS and GENERATION OF 'ConfigurationsSummary'
# This 3rd block of code is performed for every single architecture evaluated through FLYCOP
# -----------------------------------------------------------------------------

# FOR EVERY POTENTIAL ARCHITECTURE EVALUATED THROUGH FLYCOP

with pd.ExcelFile(configResults_excel) as xls:
    for architecture in xls.sheet_names:  # Every sheet_name is a different architecture
        if architecture == "Sheet": continue
    
        # INITIAL READING OF EXCEL FILE
        configResults = pd.read_excel(xls, sheet_name=architecture)
        configResults["ConfigKey"] = "Acceptable"  # New binary classification column
    
    
        # INITIAL FILTERING: NON-ACCEPTABLE (NonOptimalConfig_Error) vs. ACCEPTABLE configurations
        # ----------------------------------------------------------------------------------------
        # Check if the file with non-acceptable configurations is empty (i.e. no 'nonOptimal' configurations found)
        nonOptimal_flag = True if os.path.getsize("nonOptimalConfigsasStrings"+architecture+".txt") else False
        
        if nonOptimal_flag: 
            nonOptimal_file = pd.read_csv("nonOptimalConfigsasStrings"+architecture+".txt", sep="\t", header='infer')  # Single column (configuration of parameters)
            
            for row in nonOptimal_file.itertuples():
                bad_config = row[1]
                
                for row in configResults.itertuples():
                    if configResults[configResults.BaseConfig == bad_config]: configResults[row[0], "ConfigKey"] = "NonOptimal"
                    
        else: os.remove("nonOptimalConfigsasStrings"+architecture+".txt")
        
        # FURTHER SORTING:   
        # -------------------------------------------------------------------------
        # Sorting by 'ConfigKey': first 'Acceptable', then 'NonOptimal' configurations // Asegurar
        # Sorting by 'ID_SD': excessive SD at the end of each group
        # Within the last group, from highest to lowest fitness value
        configResults = configResults.sort_values(by=["ConfigKey", 'ID_SD', 'fitFunc'], ascending=[True, True, False])
        
        
        # SAVE MODIFIED SHEET (update last arch_model sheet)
        # -------------------------------------------------------------------------
        with pd.ExcelWriter(configResults_excel, engine='openpyxl', mode='a') as writer:
            configResults_excelfile = writer.book
            try:
                configResults_excelfile.remove(configResults_excelfile[architecture])
            except:
                print("Worksheet does not exist")
            finally:
                configResults.to_excel(writer, sheet_name=architecture, header=True, index=False, index_label=None)
                writer.save()
    
    
        # WRITE A BRIEF SUMMARY OF ACCEPTABLE vs. NON-ACCEPTABLE
        # ------------------------------------------------------
        configs_summary = open("ConfigurationsSummary_"+architecture+".txt", "a")  # in PreliminaryAnalysis directory   
        configs_summary.write("-------------------------------------------------------\n")
        configs_summary.write("BRIEF SUMMARY OF CONFIGURATIONS\n")
        configs_summary.write("-------------------------------------------------------\n")
    
    
        # -------------------------
        # ACCEPTABLE configurations
        # -------------------------
        configResults_acceptable = configResults[configResults["ConfigKey"] == "Acceptable"]  # Fraction of dataframe 'Acceptable'
        
        # Biomass Loss
        biomass_loss_cases_acc = configResults_acceptable[configResults_acceptable["DeadTracking"] == 1] 
        biomass_loss_cases_accSD_acc = biomass_loss_cases_acc[biomass_loss_cases_acc["ID_SD"] == 0]
        
        # No Biomass Loss
        non_biomass_loss_cases_acc = configResults_acceptable[configResults_acceptable["DeadTracking"] == 0]
        non_biomass_loss_cases_accSD_acc = non_biomass_loss_cases_acc[non_biomass_loss_cases_acc["ID_SD"] == 0]
        
        configs_summary.write("\nACCEPTABLE CONFIGURATIONS\n")
        configs_summary.write("-------------------------------------------------------")
        
        configs_summary.write("\nTotal of acceptable configurations: "+str(len(configResults_acceptable))+"\n")
        configs_summary.write("\nTotal of acceptable configurations with biomass loss: "+str(biomass_loss_cases_acc.count()[0])+"\n")
        configs_summary.write("\t - of which, the number of configurations with ACCEPTABLE SD (< 10% avgFit) is: "+str(biomass_loss_cases_accSD_acc.count()[0])+"\n")
        
        configs_summary.write("\nTotal of acceptable configurations with NO biomass loss: "+str(non_biomass_loss_cases_acc.count()[0])+"\n")
        configs_summary.write("\t - of which, the number of configurations with ACCEPTABLE SD (< 10% avgFit) is: "+str(non_biomass_loss_cases_accSD_acc.count()[0])+"\n\n")
        
        
        # Fraction of dataframe 'Acceptable' with acceptable SD for further plotting
        # NO further subdivision in biomass loss vs. non-biomass loss
        # -----------------------------------------------------------------------------
        configResults_acceptable_SDok = configResults_acceptable[configResults_acceptable["ID_SD"] == 0]  # No sé si lo utilizamos en este script
    
    
        # ------------------------------------------------------
        # NON-ACCEPTABLE (NonOptimalConfig_Error) configurations
        # ------------------------------------------------------
        
        configs_summary.write("\nNON-OPTIMAL CONFIGURATIONS\n")
        configs_summary.write("-------------------------------------------------------")
        
        if nonOptimal_flag:
            configResults_nonOpt = configResults[configResults["ConfigKey"] == "NonOptimal"]  # Fraction of dataframe 'NonOptimal'
            
            # Biomass Loss
            biomass_loss_cases_nonOpt = configResults_nonOpt[configResults_nonOpt["DeadTracking"] == 1]
            biomass_loss_cases_accSD_nonOpt = biomass_loss_cases_nonOpt[biomass_loss_cases_nonOpt["ID_SD"] == 0]
            
            # No Biomass Loss
            non_biomass_loss_cases_nonOpt = configResults_nonOpt[configResults_nonOpt["DeadTracking"] == 0]
            non_biomass_loss_cases_accSD_nonOpt = non_biomass_loss_cases_nonOpt[non_biomass_loss_cases_nonOpt["ID_SD"] == 0]
            
            
            configs_summary.write("\nTotal of configurations with NonOptimalConfig_error: "+str(len(configResults_nonOpt))+"\n")
            configs_summary.write("\nTotal of configurations with NonOptimalConfig_error and biomass loss: "+str(biomass_loss_cases_nonOpt.count()[0])+"\n")
            configs_summary.write("\t - of which, the number of configurations with ACCEPTABLE SD (< 10% avgFit) is: "+str(biomass_loss_cases_accSD_nonOpt.count()[0])+"\n")
            
            configs_summary.write("\nTotal of configurations with NonOptimalConfig_error and NO biomass loss: "+str(non_biomass_loss_cases_nonOpt.count()[0])+"\n")
            configs_summary.write("\t - of which, the number of configurations with ACCEPTABLE SD (< 10% avgFit) is: "+str(non_biomass_loss_cases_accSD_nonOpt.count()[0])+"\n\n")
            
            # Fraction of dataframe 'NonOptimal' with acceptable SD for further plotting
            # NO further subdivision in biomass loss vs. non-biomass loss
            # -------------------------------------------------------------------------
            configResults_nonOpt_SDok = configResults_nonOpt[configResults_nonOpt["ID_SD"] == 0]  # No sé si lo utilizamos en este script
        
        else:
            configs_summary.write("\nNon-optimal configurations not found\n")
        
        
        # ---------------------
        configs_summary.close()
###############################################################################
###############################################################################























