# code: utf-8
# author: Xudong Zheng
# email: z786909151@163.com

"""
build_RVIC_Param - A Python module for building RVIC parameter files.

This module provides functions for constructing and modifying RVIC (Routing of VIC model)
parameter files, including flow direction files, pour point files, unit hydrograph (UH) box files,
and configuration (CFG) files essential for RVIC simulations. The module also includes utilities
for setting up and modifying the necessary inputs for hydrological routing within the VIC framework.

Functions:
----------
    - `buildRVICParam_general`: Generate general RVIC parameter files before using `rvic_parameters`.
    - `buildRVICParam`: Constructs RVIC parameters that contains rvic_parameters based on input datasets and configurations.
    - `buildRVICFlowDirectionFile`: Generates a NetCDF flow direction file using provided input datasets.
    - `buildPourPointFile`: Creates a pour point file specifying the outlet locations for routing.
    - `buildUHBOXFile`: Constructs a UHBOX file that defines the unit hydrograph characteristics.
    - `buildParamCFGFile`: Generates the parameter configuration (CFG) file for RVIC simulations.
    - `buildConvCFGFile`: Creates a conversion configuration file for RVIC execution.
    - `modifyRVICParam_for_pourpoint`: Modifies RVIC parameters to include a specific pour point and updates flow direction settings accordingly.

Usage:
------
    1. Call `buildRVICParam_general` to generate RVIC parameter files without using `rvic_parameters`, set the necessary input parameters.
    2. Call ``buildRVICParam`` to generate RVIC parameter files and execute RVIC parameter computation.

Example:
--------
    basin_index = 213
    model_scale = "6km"
    date_period = ["19980101", "19981231"]
    case_name = f"{basin_index}_{model_scale}"

    evb_dir = Evb_dir("./examples")  # cases_home="/home/xdz/code/VIC_xdz/cases"
    evb_dir.builddir(case_name)

    dpc_VIC_level0, dpc_VIC_level1, dpc_VIC_level2 = readdpc(evb_dir)
    params_dataset_level0, params_dataset_level1 = readParam(evb_dir)

    buildRVICParam_general(evb_dir, dpc_VIC_level1, params_dataset_level1,
                           ppf_kwargs=dict(), uh_params={"createUH_func": create_uh.createGUH, "uh_dt": 3600,
                                                         "tp": default_uh_params[0], "mu": default_uh_params[1], "m": default_uh_params[2],
                                                         "plot_bool": True, "max_day":None, "max_day_range": (0, 10), "max_day_converged_threshold": 0.001},
                           cfg_params={"VELOCITY": 1.5, "DIFFUSION": 800.0, "OUTPUT_INTERVAL": 86400, "SUBSET_DAYS": 10, "CELL_FLOWDAYS": 2, "BASIN_FLOWDAYS": 50})

    buildRVICParam(evb_dir, dpc_VIC_level1, params_dataset_level1,
                   ppf_kwargs=dict(), uh_params={"createUH_func": create_uh.createGUH, "uh_dt": 3600,
                                                 "tp": default_uh_params[0], "mu": default_uh_params[1], "m": default_uh_params[2],
                                                 "plot_bool": True, "max_day":None, "max_day_range": (0, 10), "max_day_converged_threshold": 0.001},
                   cfg_params={"VELOCITY": 1.5, "DIFFUSION": 800.0, "OUTPUT_INTERVAL": 86400, "SUBSET_DAYS": 10, "CELL_FLOWDAYS": 2, "BASIN_FLOWDAYS": 50})

    params_dataset_level0.close()
    params_dataset_level1.close()

Dependencies:
-------------
    - `os`: For file and directory operations.
    - `numpy`: For numerical operations.
    - `pandas`: For handling tabular data (CSV files).
    - `rasterio`: For reading and writing geospatial raster data.
    - `copy`: For creating deep copies of objects.
    - `logging`: For logging messages during file processing.
    - `xarray`: For handling multidimensional arrays and NetCDF files.
    - `.tools.params_func.createParametersDataset`: For creating flow direction files.
    - `.tools.utilities`: For reading configuration files.
    - `.tools.decoractors`: For timing function execution with `clock_decorator`.
    - `.tools.uh_func`: For creating unit hydrographs (UH).
    - `.tools.geo_func`.search_grids: For geospatial grid search functions.

"""

import os
from copy import deepcopy

import numpy as np
import pandas as pd
import rasterio
import rasterio.transform

from . import logger
from .tools.decoractors import clock_decorator
from .tools.geo_func.search_grids import *
from .tools.params_func.createParametersDataset import createFlowDirectionFile
from .tools.routing_func import create_uh
from .tools.utilities import (read_cfg_to_dict,
                              read_rvic_conv_cfg_file_reference,
                              read_rvic_param_cfg_file_reference)

try:
    from rvic.parameters import parameters as rvic_parameters

    HAS_RVIC = True
except:
    HAS_RVIC = False


def buildRVICParam_basic(
    evb_dir,
    domain_dataset,
    ppf_kwargs=dict(),
    uh_params={
        "createUH_func": create_uh.createGUH,
        "uh_dt": 3600,
        "tp": 1.4,
        "mu": 5.0,
        "m": 3.0,
        "plot_bool": True,
        "max_day": None,
        "max_day_range": (0, 10),
        "max_day_converged_threshold": 0.001,
    },
    cfg_params={
        "VELOCITY": 1.5,
        "DIFFUSION": 800.0,
        "OUTPUT_INTERVAL": 86400,
        "SUBSET_DAYS": 10,
        "CELL_FLOWDAYS": 2,
        "BASIN_FLOWDAYS": 50,
    },
):
    """
    Generate general RVIC parameter files before using `rvic_parameters`.

    This function sequentially builds the required input files for the RVIC model, including:
    - Flow direction file
    - Pour point file
    - Unit hydrograph (UH) file
    - Parameter configuration file

    Parameters
    ----------
    evb_dir : `Evb_dir`
        An instance of the `Evb_dir` class, containing paths for VIC deployment.
    
    dpc_VIC_level1 : `dpc_VIC_level1`
        An instance of the `dpc_VIC_level1` class to determine pour points..

    params_dataset_level1 : `netCDF.Dataset`
        The parameter dataset for level 1, containing flow direction and routing parameters.
    
    ppf_kwargs : dict, optional
        Keyword arguments for `buildPourPointFile`, by default an empty dictionary.
        
    uh_params : dict, optional
        Parameters for `buildUHBOXFile`, including:
        - createUH_func: Function to create UH.
        - uh_dt: Time step for UH computation.
        - tp, mu, m: Shape parameters for UH function.
        - plot_bool: Whether to generate UH plots.
        - max_day, max_day_range, max_day_converged_threshold: Parameters for convergence criteria.
        
    cfg_params : dict, optional
        Configuration parameters for `buildParamCFGFile`, including:
        - VELOCITY: Flow velocity.
        - DIFFUSION: Diffusion parameter.
        - OUTPUT_INTERVAL: Output time interval.
        - SUBSET_DAYS: Days for subset computation.
        - CELL_FLOWDAYS: Days for cell flow accumulation.
        - BASIN_FLOWDAYS: Days for basin flow accumulation.

    Returns
    -------
    None
        The function generates necessary RVIC parameter files and does not return any values.

    Notes
    -----
    This function calls the following sub-functions in order:
    - `buildRVICFlowDirectionFile`
    - `buildPourPointFile`
    - `buildUHBOXFile`
    - `buildParamCFGFile`
    """
    logger.info(
        "Starting to generate RVIC parameter file without using rvic_parameters... ..."
    )

    # general RVICParam before using rvic_parameters
    # buildRVICFlowDirectionFile
    buildRVICFlowDirectionFile(evb_dir, domain_dataset)

    # buildPourPointFile
    buildPourPointFile(evb_dir, **ppf_kwargs)

    # buildUHBOXFile
    max_day = buildUHBOXFile(evb_dir, **uh_params)

    # buildParamCFGFile
    if cfg_params["CELL_FLOWDAYS"] is None:
        cfg_params["CELL_FLOWDAYS"] = max_day
        
    buildParamCFGFile(evb_dir, **cfg_params)

    logger.info(
        "RVIC parameter file generation without using rvic_parameters successfully"
    )


@clock_decorator(print_arg_ret=False)
def buildRVICParam(
    evb_dir,
    domain_dataset,
    ppf_kwargs=dict(),
    uh_params={
        "createUH_func": create_uh.createGUH,
        "uh_dt": 3600,
        "tp": 1.4,
        "mu": 5.0,
        "m": 3.0,
        "plot_bool": True,
        "max_day": None,
        "max_day_range": (0, 10),
        "max_day_converged_threshold": 0.001,
    },
    cfg_params={
        "VELOCITY": 1.5,
        "DIFFUSION": 800.0,
        "OUTPUT_INTERVAL": 86400,
        "SUBSET_DAYS": 10,
        "CELL_FLOWDAYS": 2,
        "BASIN_FLOWDAYS": 50,
    },
):
    """
    Generate RVIC parameter files and execute RVIC parameter computation.

    This function first builds the necessary RVIC input files using `buildRVICParam_general`,
    then reads the parameter configuration file and runs the RVIC parameter computation.

    Parameters
    ----------
    evb_dir : `Evb_dir`
        An instance of the `Evb_dir` class, containing paths for VIC deployment.
    
    dpc_VIC_level1 : `dpc_VIC_level1`
        An instance of the `dpc_VIC_level1` class to determine pour points..

    params_dataset_level1 : `netCDF.Dataset`
        The parameter dataset for level 1, containing flow direction and routing parameters.
    
    ppf_kwargs : dict, optional
        Keyword arguments for `buildPourPointFile`, by default an empty dictionary.
        
    uh_params : dict, optional
        Parameters for `buildUHBOXFile`, including:
        - createUH_func: Function to create UH.
        - uh_dt: Time step for UH computation.
        - tp, mu, m: Shape parameters for UH function.
        - plot_bool: Whether to generate UH plots.
        - max_day, max_day_range, max_day_converged_threshold: Parameters for convergence criteria.
        
    cfg_params : dict, optional
        Configuration parameters for `buildParamCFGFile`, including:
        - VELOCITY: Flow velocity.
        - DIFFUSION: Diffusion parameter.
        - OUTPUT_INTERVAL: Output time interval.
        - SUBSET_DAYS: Days for subset computation.
        - CELL_FLOWDAYS: Days for cell flow accumulation.
        - BASIN_FLOWDAYS: Days for basin flow accumulation.

    Returns
    -------
    None
        The function generates RVIC parameter files and executes the RVIC parameter computation.

    Raises
    ------
    ImportError
        If the RVIC module is not available.

    Notes
    -----
    This function performs the following steps:
    1. Calls `buildRVICParam_general` to generate the required input files.
    2. Reads the RVIC parameter configuration file.
    3. Runs `rvic_parameters` if RVIC is available; otherwise, raises an ImportError.
    """
    logger.info("Starting to generate RVIC parameter file... ...")

    # buildRVICParam_general
    buildRVICParam_basic(
        evb_dir,
        domain_dataset,
        ppf_kwargs,
        uh_params,
        cfg_params,
    )

    # build rvic parameters
    logger.debug(
        f"Reading RVIC parameter configuration from {evb_dir.rvic_param_cfg_file_path}... ..."
    )
    param_cfg_file_dict = read_cfg_to_dict(evb_dir.rvic_param_cfg_file_path)

    if HAS_RVIC:
        logger.info("Executing RVIC parameter computation... ...")
        rvic_parameters(param_cfg_file_dict, numofproc=1)
        logger.info("RVIC parameter computation completed")
    else:
        logger.error("RVIC module is not available. Cannot proceed with buildRVICParam")
        raise ImportError("no rvic for buildRVICParam")

    logger.info("RVIC parameter file generation successfully")


def buildRVICFlowDirectionFile(evb_dir, domain_dataset):
    """
    Generate an RVIC flow direction file in NetCDF format.

    This function reads flow direction, flow accumulation, and flow distance data from GeoTIFF files,
    applies a mask based on the VIC parameter dataset, and stores the processed data in a NetCDF file.

    Parameters
    ----------
    evb_dir : `Evb_dir`
        An instance of the `Evb_dir` class, containing paths for VIC deployment.
    
    params_dataset_level1 : `netCDF.Dataset`
        The parameter dataset for level 1, containing flow direction and routing parameters.

    Returns
    -------
    None
        The function creates a NetCDF file containing flow direction-related information.

    Notes
    -----
    The function performs the following steps:
    1. Sets paths for input and output files.
    2. Reads general information from the VIC parameter dataset.
    3. Reads flow direction, flow accumulation, and flow distance data from GeoTIFF files.
    4. Combines the data into a NetCDF file, applying masks where necessary.
    """
    logger.info("Starting to generate RVIC flow direction file... ...")
    # ====================== set dir and path ======================
    # set path
    flow_direction_file_path = os.path.join(
        evb_dir.RVICParam_dir, "flow_direction_file.nc"
    )
    flow_direction_path = os.path.join(evb_dir.Hydroanalysis_dir, "flow_direction.tif")
    flow_acc_path = os.path.join(evb_dir.Hydroanalysis_dir, "flow_acc.tif")
    flow_distance_path = os.path.join(evb_dir.Hydroanalysis_dir, "flow_distance.tif")

    # ====================== read general information ======================
    logger.debug("Reading latitude, longitude, and mask data from VIC parameters... ...")
    domain_lat = domain_dataset.variables["lat"][:]
    domain_lon = domain_dataset.variables["lon"][:]
    domain_mask = domain_dataset.variables["mask"][:, :]

    # ====================== read flow_direction and flow_acc ======================
    logger.debug(f"Reading flow direction data from {flow_direction_path}... ...")
    with rasterio.open(flow_direction_path, "r", driver="GTiff") as dataset:
        flow_direction_array = dataset.read(1)

    logger.debug(f"Reading flow accumulation data from {flow_acc_path}... ...")
    with rasterio.open(flow_acc_path, "r", driver="GTiff") as dataset:
        flow_acc_array = dataset.read(1)

    logger.debug(f"Reading flow distance data from {flow_distance_path}... ...")
    with rasterio.open(flow_distance_path, "r", driver="GTiff") as dataset:
        flow_distance_array = dataset.read(1)

    # ====================== combine them into a nc file ======================
    # create nc file
    logger.debug(f"Creating NetCDF file: {flow_direction_file_path}... ...")
    flow_direction_dataset = createFlowDirectionFile(
        flow_direction_file_path, domain_lat, domain_lon
    )

    # change type
    logger.debug("Processing and masking data... ...")
    domain_mask_array = deepcopy(domain_mask)
    domain_mask_array = domain_mask_array.astype(int)
    flow_direction_array = flow_direction_array.astype(int)
    flow_distance_array = flow_distance_array.astype(float)
    flow_acc_array = flow_acc_array.astype(float)

    # mask
    # domain_mask_array[domain_mask == 0] = int(-9999)
    # flow_direction_array[domain_mask == 0] = int(-9999)
    # flow_distance_array[domain_mask == 0] = float(-9999.0)
    # flow_acc_array[domain_mask == 0] = float(-9999.0)

    # assign values
    flow_direction_dataset.variables["lat"][:] = np.array(domain_lat)
    flow_direction_dataset.variables["lon"][:] = np.array(domain_lon)
    flow_direction_dataset.variables["Basin_ID"][:, :] = np.array(domain_mask_array)
    flow_direction_dataset.variables["Flow_Direction"][:, :] = np.array(
        flow_direction_array
    )
    flow_direction_dataset.variables["Flow_Distance"][:, :] = np.array(
        flow_distance_array
    )
    flow_direction_dataset.variables["Source_Area"][:, :] = np.array(flow_acc_array)

    flow_direction_dataset.close()

    logger.info(
        f"RVIC flow direction file generation successfully, saved to: {flow_direction_file_path}"
    )


def buildPourPointFile(evb_dir, names=None, lons=None, lats=None):
    """
    Generate a pour point CSV file for RVIC.

    This function creates a CSV file containing longitude, latitude, and names of pour points.
    If `dpc_VIC_level1` is provided, it extracts pour point coordinates from the basin shapefile;
    otherwise, it uses the manually provided `lons`, `lats`, and `names` lists.

    Parameters
    ----------
    evb_dir : `Evb_dir`
        An instance of the `Evb_dir` class, containing paths for VIC deployment.
    
    dpc_VIC_level1 : `dpc_VIC_level1`
        An instance of the `dpc_VIC_level1` class to determine pour points..

    names : list, optional
        List of names for the pour points.
        
    lons : list, optional
        List of longitude coordinates for pour points.
        
    lats : list, optional
        List of latitude coordinates for pour points.

    Returns
    -------
    None
        The function writes the pour point data to a CSV file.

    Notes
    -----
    - If `dpc_VIC_level1` is used, the function extracts pour point locations from the "camels_topo" attributes.
    - If `dpc_VIC_level1` is not provided, manually specified coordinates must be supplied.
    - Ensure that flow accumulation data is checked to verify pour point locations.
    """
    #! you should check it with FlowAcc (source area)

    logger.info("Starting to generate pour point file... ...")
    # ====================== set dir and path ======================
    RVICParam_dir = evb_dir.RVICParam_dir
    pourpoint_file_path = os.path.join(RVICParam_dir, "pour_points.csv")

    # ====================== build PourPointFile ======================
    # df
    pourpoint_file = pd.DataFrame(columns=["lons", "lats", "names"])
    
    if lons is None or lats is None or names is None:
        logger.error("Missing longitude, latitude, or name data for pour points")
        raise ValueError(
            "Longitude, latitude, and name lists must be provided when dpc_VIC_level1 is None"
        )

    pourpoint_file.lons = lons
    pourpoint_file.lats = lats
    pourpoint_file.names = names

    # ====================== Save pour point file ======================
    pourpoint_file.to_csv(pourpoint_file_path, header=True, index=False)
    logger.info(
        f"Pour point file generation successfully, saved to {pourpoint_file_path}"
    )


def buildUHBOXFile(evb_dir, createUH_func=create_uh.createGUH, **kwargs):
    """
    Generate and save the UHBOX (Unit Hydrograph Box) file.

    This function creates a UHBOX file using a specified unit hydrograph creation function.
    The resulting UHBOX data is then saved to a CSV file.

    Parameters
    ----------
    evb_dir : `Evb_dir`
        An instance of the `Evb_dir` class, containing paths for VIC deployment.
    
    createUH_func : function, optional
        Function used to generate the unit hydrograph, default is `create_uh.createGUH`.
        
    **kwargs : dict
        Additional parameters to be passed to the `createUH_func`.

    Returns
    -------
    max_day : float
        Maximum duration (in days) used in the unit hydrograph generation.

    Notes
    -----
    - The function relies on `createUH_func` to generate the UHBOX data.
    - The resulting UHBOX file is stored in `evb_dir.uhbox_file_path`.
    """
    logger.info("Starting to generate UHBOX file... ...")

    # build
    max_day, UHBOX_file = createUH_func(evb_dir, **kwargs)

    # save
    UHBOX_file.to_csv(evb_dir.uhbox_file_path, header=True, index=False)

    logger.info(
        f"UHBOX file generation successfully, saved to {evb_dir.uhbox_file_path}"
    )

    return max_day


def buildParamCFGFile(
    evb_dir,
    VELOCITY=1.5,
    DIFFUSION=800.0,
    OUTPUT_INTERVAL=86400,
    SUBSET_DAYS=10,
    CELL_FLOWDAYS=2,
    BASIN_FLOWDAYS=50,
):
    """
    Generate and save the RVIC parameter configuration file.

    This function creates a configuration (CFG) file for RVIC parameter settings based on
    a reference configuration file and specified routing parameters.

    Parameters
    ----------
    evb_dir : `Evb_dir`
        An instance of the `Evb_dir` class, containing paths for VIC deployment.
    
    VELOCITY : float, optional
        Flow velocity parameter, default is 1.5, and the acceptable range is 1.0 to 3.0 m/s.
        
    DIFFUSION : float, optional
        Diffusion coefficient for routing, default is 800.0, and the acceptable range is 200 to 4000m3/s.
        
    OUTPUT_INTERVAL : int, optional
        Time interval (seconds) for output, default is 86400 seconds (1 day), and should typically be set as a multiple of 60.
        
    SUBSET_DAYS : int, optional
        Number of days used for subset processing, default is 10.
        
    CELL_FLOWDAYS : int, optional
        Flow duration at the cell level (days), default is 2.
        
    BASIN_FLOWDAYS : int, optional
        Flow duration at the basin level (days), default is 50.

    Notes
    -----
    - Reads a reference configuration file and modifies key parameters.
    - Saves the updated configuration file to `evb_dir.rvic_param_cfg_file_path`.
    """
    logger.info("Starting to generate RVIC parameter configuration file... ...")
    # ====================== build CFGFile ======================
    # read reference cfg
    # param_cfg_file = ConfigParser()
    # param_cfg_file.optionxform = str  # import to keep case
    # param_cfg_file.read(evb_dir.rvic_param_cfg_file_reference_path)
    param_cfg_file = read_rvic_param_cfg_file_reference()

    # set cfg
    param_cfg_file.set("OPTIONS", "CASEID", evb_dir._case_name)
    param_cfg_file.set("OPTIONS", "CASE_DIR", evb_dir.RVICParam_dir)
    param_cfg_file.set("OPTIONS", "TEMP_DIR", evb_dir.RVICTemp_dir)
    param_cfg_file.set("OPTIONS", "SUBSET_DAYS", str(SUBSET_DAYS))
    param_cfg_file.set("POUR_POINTS", "FILE_NAME", evb_dir.pourpoint_file_path)
    param_cfg_file.set("UH_BOX", "FILE_NAME", evb_dir.uhbox_file_path)
    param_cfg_file.set("ROUTING", "FILE_NAME", evb_dir.flow_direction_file_path)
    param_cfg_file.set("ROUTING", "VELOCITY", str(VELOCITY))
    param_cfg_file.set("ROUTING", "DIFFUSION", str(DIFFUSION))
    param_cfg_file.set("ROUTING", "OUTPUT_INTERVAL", str(OUTPUT_INTERVAL))
    param_cfg_file.set("ROUTING", "CELL_FLOWDAYS", str(CELL_FLOWDAYS))
    param_cfg_file.set("ROUTING", "BASIN_FLOWDAYS", str(BASIN_FLOWDAYS))
    param_cfg_file.set("DOMAIN", "FILE_NAME", evb_dir.domainFile_path)

    # write cfg
    with open(evb_dir.rvic_param_cfg_file_path, "w") as configfile:
        param_cfg_file.write(configfile)

    logger.info(
        f"RVIC parameter configuration file generation successfully, saved to {evb_dir.rvic_param_cfg_file_path}"
    )


def buildConvCFGFile(
    evb_dir,
    RUN_STARTDATE="1979-09-01-00",
    DATL_FILE="rasm_sample_runoff.nc",
    PARAM_FILE_PATH="sample_rasm_parameters.nc",
):
    """
    Generate and save the RVIC convolution configuration file.

    This function creates a configuration (CFG) file for RVIC convolution settings
    based on a reference configuration file and specified parameters.

    Parameters
    ----------
    evb_dir : `Evb_dir`
        An instance of the `Evb_dir` class, containing paths for VIC deployment.
    
    RUN_STARTDATE : str, optional
        The start date for the RVIC run in "YYYY-MM-DD-HH" format.
        
    DATL_FILE : str, optional
        The name of the input runoff file. Default is "rasm_sample_runoff.nc".
        
    PARAM_FILE_PATH : str, optional
        The path to the RVIC parameter file. Default is "sample_rasm_parameters.nc".

    Notes
    -----
    - Reads a reference configuration file and modifies key parameters.
    - Saves the updated configuration file to `evb_dir.rvic_conv_cfg_file_path`.
    """
    logger.info("Starting to generate RVIC convolution configuration file... ...")
    # ====================== build CFGFile ======================
    # read reference cfg
    # conv_cfg_file = ConfigParser()
    # conv_cfg_file.optionxform = str  # import to keep case
    # conv_cfg_file.read(evb_dir.rvic_conv_cfg_file_reference_path)
    conv_cfg_file = read_rvic_conv_cfg_file_reference()

    # set cfg
    conv_cfg_file.set("OPTIONS", "CASEID", evb_dir._case_name)
    conv_cfg_file.set("OPTIONS", "CASE_DIR", evb_dir.RVICConv_dir)
    conv_cfg_file.set("OPTIONS", "RUN_STARTDATE", RUN_STARTDATE)

    conv_cfg_file.set("DOMAIN", "FILE_NAME", evb_dir.domainFile_path)

    conv_cfg_file.set("PARAM_FILE", "FILE_NAME", PARAM_FILE_PATH)

    conv_cfg_file.set("INPUT_FORCINGS", "DATL_PATH", evb_dir.VICResults_dir)
    conv_cfg_file.set("INPUT_FORCINGS", "DATL_FILE", DATL_FILE)

    # write cfg
    with open(evb_dir.rvic_conv_cfg_file_path, "w") as configfile:
        conv_cfg_file.write(configfile)

    logger.info(
        f"RVIC convolution configuration file generation successfully, saved to {evb_dir.rvic_conv_cfg_file_path}"
    )


def modifyRVICParam_for_pourpoint(
    evb_dir,
    pourpoint_lon,
    pourpoint_lat,
    pourpoint_direction_code,
    params_dataset_level1,
    domain_dataset,
    reverse_lat=True,
    stream_acc_threshold=100.0,
    flow_direction_pkg="wbw",
    crs_str="EPSG:4326",
):
    """
    Modify RVIC parameters to integrate a specified pour point.

    This function updates the pour point file and modifies the RVIC flow direction file
    to adjust the direction of the pour point at the edge.

    Parameters
    ----------
    evb_dir : `Evb_dir`
        An instance of the `Evb_dir` class, containing paths for VIC deployment.
    
    pourpoint_lon : float
        Longitude of the pour point.
        
    pourpoint_lat : float
        Latitude of the pour point.
        
    pourpoint_direction_code : int
        Flow direction code for the pour point (e.g., based on D8 direction encoding).
        
    params_dataset_level1 : Dataset
        Parameter dataset at level 1, used to extract grid-based information.
    
    domain_dataset : `netCDF.Dataset`, optional
        Domain dataset containing spatial attributes.
    
    reverse_lat : bool
        Boolean flag to indicate whether to reverse latitudes (Northern Hemisphere: large -> small, set as True).

    stream_acc_threshold : float, optional
        The threshold value for stream accumulation. Default is 100.0. It affect the results generated by hydroanalysis_arcpy.

    flow_direction_pkg : str, optional
        The package used to calculate flow direction. Options are "arcpy" and "wbw". Default is "wbw".

    crs_str : str, optional
        Coordinate reference system (CRS) in EPSG format (default is "EPSG:4326").

    Notes
    -----
    - First, the pour point file is created or updated.
    - Then, the RVIC flow direction file is modified to include the pour point and adjust its flow direction.
    """
    logger.info(
        "Starting to modifying RVIC parameters for pour point integration... ..."
    )

    # ====================== Modify PourPointFile ======================
    buildPourPointFile(
        evb_dir, None, names=["pourpoint"], lons=[pourpoint_lon], lats=[pourpoint_lat]
    )
    logger.info(f"Pourpoint is set to lon ({pourpoint_lon}), lat (pourpoint_lat)")

    # ====================== Modify RVIC Flow Direction File ======================
    # modify buildRVICFlowDirectionFile, modify 0 direction (edge) of pourpoint to pourpoint_direction_code
    buildRVICFlowDirectionFile(
        evb_dir,
        params_dataset_level1,
        domain_dataset,
        reverse_lat=reverse_lat,
        stream_acc_threshold=stream_acc_threshold,
        flow_direction_pkg=flow_direction_pkg,
        crs_str=crs_str,
        pourpoint_lon=pourpoint_lon,
        pourpoint_lat=pourpoint_lat,
        pourpoint_direction_code=pourpoint_direction_code,
    )

    logger.info("RVIC parameter modification for pour point successfully")
