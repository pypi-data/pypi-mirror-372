# code: utf-8
# author: Xudong Zheng
# email: z786909151@163.com

"""
Module: basin_grid_func

This module provides functions for processing and managing `Basins` and `Grids` instances in hydrological
and geospatial analyses. It includes methods for grid creation, spatial data assignment, coordinate mapping,
and soil property aggregation. These functions are particularly useful for hydrological modeling and environmental
studies requiring structured grid representations.

Functions:
----------
    - createGridForBasin: Generates a grid structure within a specified basin.
    - createStand_grids_lat_lon_from_gridshp: Extracts standardized latitude and longitude grid arrays
      from a geospatial dataset.
    - createEmptyArray_from_gridshp: Creates an empty NumPy array corresponding to a given geospatial grid.
    - gridshp_index_to_grid_array_index: Maps geospatial grid indices to corresponding array indices.
    - assignValue_for_grid_array: Assigns values from a geospatial dataset to a predefined grid array.
    - createEmptyArray_and_assignValue_from_gridshp: Initializes an empty array and fills it with
      values derived from a geospatial dataset.
    - createArray_from_gridshp: Constructs a NumPy array based on geospatial grid data.
    - grids_array_coord_map: Generates mappings between longitude/latitude coordinates and array indices.
    - cal_ssc_percentile_grid_array: Computes weighted mean values for soil sand, silt, and clay
      percentages across multiple depth layers.
    - cal_bd_grid_array: Computes weighted mean bulk density across multiple soil depth layers.
    - intersectGridsWithBasins: Identifies grid cells that intersect with basin geometries and returns
      the updated basin and grid datasets.

Dependencies:
-------------
    - numpy: Provides numerical operations and array manipulations.
    - pandas: Supports data manipulation and processing of geospatial datasets.
    - geopandas: Facilitates spatial operations on basin and grid geometries.

Author:
-------
    Xudong Zheng
    Email: z786909151@163.com

"""

import numpy as np
from matplotlib import pyplot as plt

from ..geo_func.search_grids import *
from ..params_func.params_set import *
from .basin_grid_class import *


def createGridForBasin(basin_shp, grid_res, **create_grid_kwargs):
    """
    Create grid points for the given basin shape.

    Parameters
    ----------
    basin_shp : shapely.geometry
        The shape of the basin.
    grid_res : float
        The resolution of the grid.
    **kwargs : additional optional arguments

    Returns
    -------
    grid_shp_lon : list
        The longitude values of the grid points.
    grid_shp_lat : list
        The latitude values of the grid points.
    grid_shp : Grids_for_shp
        A grid shape object containing all grid points.
    """
    create_grid_kwargs_ = {
        "gshp": basin_shp,
        "res": grid_res,
        "adjust_boundary": True,
    }
    
    create_grid_kwargs_.update(**create_grid_kwargs)
    
    grid_shp = Grids_for_shp(create_grid_kwargs=create_grid_kwargs_)
    grid_shp_lon = grid_shp.point_geometry.x.to_list()
    grid_shp_lat = grid_shp.point_geometry.y.to_list()

    return grid_shp_lon, grid_shp_lat, grid_shp


def createStand_grids_lat_lon_from_gridshp(grid_shp, grid_res=None, reverse_lat=True):
    """
    Generate sorted latitude and longitude arrays from grid shape.

    Parameters
    ----------
    grid_shp : shapely.geometry
        The shape of the grid.
    grid_res : float, optional
        The resolution of the grid. If None, the grid will be a complete rectangular grid.
    reverse_lat : bool, optional
        If True, latitude will be sorted from large to small, top to bottom.

    Returns
    -------
    stand_grids_lat : numpy.ndarray
        Sorted latitude values of the grid.
    stand_grids_lon : numpy.ndarray
        Sorted longitude values of the grid.
    """
    # grid_res is None: grid_shp is a Complete rectangular grids set, else is may be a uncomplete grids set
    # create sorted stand grids
    if grid_res is None:
        stand_grids_lon = list(set(grid_shp["point_geometry"].x.to_list()))
        stand_grids_lat = list(set(grid_shp["point_geometry"].y.to_list()))

        stand_grids_lon = np.array(
            sorted(stand_grids_lon, reverse=False)
        )  # small -> large, left is zero
        stand_grids_lat = np.array(
            sorted(stand_grids_lat, reverse=reverse_lat)
        )  # if True, large -> small, top is zero, it is useful for plot directly

    else:
        min_lon = min(grid_shp["point_geometry"].x.to_list())
        max_lon = max(grid_shp["point_geometry"].x.to_list())
        num_lon = int((max_lon - min_lon) / grid_res) + 1
        stand_grids_lon = np.linspace(start=min_lon, stop=max_lon, num=num_lon)

        min_lat = min(grid_shp["point_geometry"].y.to_list())
        max_lat = max(grid_shp["point_geometry"].y.to_list())
        num_lat = int((max_lat - min_lat) / grid_res) + 1
        stand_grids_lat = (
            np.linspace(start=max_lat, stop=min_lat, num=num_lat)
            if reverse_lat
            else np.linspace(start=min_lat, stop=max_lat, num=num_lat)
        )

    return stand_grids_lat, stand_grids_lon


def createEmptyArray_from_gridshp(
    stand_grids_lat, stand_grids_lon, third_dim_len=None, dtype=float, missing_value=np.nan
):
    """
    Create an empty grid array with the given latitude and longitude grid points.

    Parameters
    ----------
    stand_grids_lat : numpy.ndarray
        Latitude values of the grid.
    stand_grids_lon : numpy.ndarray
        Longitude values of the grid.
    dtype : data-type, optional
        The desired data type for the array. Default is float.
    missing_value : scalar, optional
        The value to use for missing data. Default is NaN.

    Returns
    -------
    grid_array : numpy.ndarray
        The empty grid array with the specified shape and missing values.
    """
    # empty array, shape is [lat(large -> small), lon(small -> large)]
    if third_dim_len is None:
        grid_array = np.full(
            (len(stand_grids_lat), len(stand_grids_lon)),
            fill_value=missing_value,
            dtype=dtype,
        )
    else:
        grid_array = np.full(
            (len(stand_grids_lat), len(stand_grids_lon), third_dim_len),
            fill_value=missing_value,
            dtype=dtype,
        )

    return grid_array


def gridshp_index_to_grid_array_index(grid_shp, stand_grids_lat, stand_grids_lon):
    """
    Convert grid shape indices to the corresponding grid array indices.

    Parameters
    ----------
    grid_shp : pd.DataFrame
        The grid shape dataframe.
    stand_grids_lat : numpy.ndarray
        The latitude values of the stand grids.
    stand_grids_lon : numpy.ndarray
        The longitude values of the stand grids.

    Returns
    -------
    rows_index : list
        The row indices of the grid array.
    cols_index : list
        The column indices of the grid array.
    """
    grid_shp_point_lon = grid_shp.point_geometry.x.to_list()
    grid_shp_point_lat = grid_shp.point_geometry.y.to_list()
    # grid_shp_point_lon = [grid_shp.loc[i, "point_geometry"].x for i in grid_shp.index]
    # grid_shp_point_lat = [grid_shp.loc[i, "point_geometry"].y for i in grid_shp.index]

    searched_grids_index = search_grids_equal(
        dst_lat=grid_shp_point_lat,
        dst_lon=grid_shp_point_lon,
        src_lat=stand_grids_lat,
        src_lon=stand_grids_lon,
        leave=False,
    )

    rows_index, cols_index = searched_grids_index_to_rows_cols_index(
        searched_grids_index
    )
    return rows_index, cols_index


def assignValue_for_grid_array(empty_grid_array, values_list, rows_index, cols_index):
    """
    Assign values to the empty grid array at the specified indices.

    Parameters
    ----------
    empty_grid_array : numpy.ndarray
        The empty grid array to which values will be assigned.
    values_list : list
        The list of values to assign.
    rows_index : list
        The row indices where values will be assigned.
    cols_index : list
        The column indices where values will be assigned.

    Returns
    -------
    grid_array : numpy.ndarray
        The grid array with assigned values.
    """
    # values_list can be grid_shp.loc[:, value_column]
    grid_array = empty_grid_array
    grid_array[rows_index, cols_index] = values_list

    return grid_array


def retriveArray_to_gridshp_values_list(
    grid_array,
    rows_index,
    cols_index
):
    # retrive values from grid_array to grid_shp (order is same as grid_shp.index)
    values_list = grid_array[rows_index, cols_index]
    
    return values_list

def createEmptyArray_and_assignValue_from_gridshp(
    stand_grids_lat,
    stand_grids_lon,
    values_list,
    rows_index,
    cols_index,
    dtype=float,
    missing_value=np.nan,
):
    """
    Create an empty grid array and assign values from grid shape data.

    Parameters
    ----------
    stand_grids_lat : numpy.ndarray
        Latitude values of the stand grids.
    stand_grids_lon : numpy.ndarray
        Longitude values of the stand grids.
    values_list : list
        List of values to assign.
    rows_index : list
        Row indices for assigning values.
    cols_index : list
        Column indices for assigning values.
    dtype : data-type, optional
        The desired data type for the array. Default is float.
    missing_value : scalar, optional
        The value to use for missing data. Default is NaN.

    Returns
    -------
    grid_array : numpy.ndarray
        The grid array with assigned values.
    """
    # empty array, shape is [lat(large -> small), lon(small -> large)]
    grid_array = np.full(
        (len(stand_grids_lat), len(stand_grids_lon)),
        fill_value=missing_value,
        dtype=dtype,
    )

    # assign values
    grid_array[rows_index, cols_index] = values_list
    return grid_array


def createArray_from_gridshp(
    grid_shp,
    value_column,
    grid_res=None,
    dtype=float,
    missing_value=np.nan,
    plot=False,
    reverse_lat=True,
):
    """
    Create a grid array from the grid shape, with values assigned from a specific column.

    Parameters
    ----------
    grid_shp : pd.DataFrame
        The grid shape dataframe.
    value_column : str
        The column in the grid shape dataframe containing the values.
    grid_res : float, optional
        The resolution of the grid. Default is None.
    dtype : data-type, optional
        The desired data type for the array. Default is float.
    missing_value : scalar, optional
        The value to use for missing data. Default is NaN.
    plot : bool, optional
        If True, the grid array will be plotted. Default is False.
    reverse_lat : bool, optional
        If True, latitude will be sorted from large to small. Default is True.

    Returns
    -------
    grid_array : numpy.ndarray
        The grid array with the assigned values.
    stand_grids_lon : numpy.ndarray
        The longitude values of the stand grids.
    stand_grids_lat : numpy.ndarray
        The latitude values of the stand grids.
    """
    # create stand grids lat, lon
    stand_grids_lat, stand_grids_lon = createStand_grids_lat_lon_from_gridshp(
        grid_shp, grid_res, reverse_lat
    )

    # create empty array
    grid_array = createEmptyArray_from_gridshp(
        stand_grids_lat, stand_grids_lon, dtype=dtype, missing_value=missing_value
    )

    # grid_shp.index to grid_array index
    rows_index, cols_index = gridshp_index_to_grid_array_index(
        grid_shp, stand_grids_lat, stand_grids_lon
    )

    # assign values
    grid_array = assignValue_for_grid_array(
        grid_array, grid_shp.loc[:, value_column], rows_index, cols_index
    )
    
    # plot
    if plot:
        plt.imshow(grid_array)

    return grid_array, stand_grids_lon, stand_grids_lat, rows_index, cols_index


def createmaskArray_for_gridshp_intersect_basinshp(
    grid_shp,
    basin_shp,
    grid_res=None,
    missing_value=np.nan,
    plot=False,
    reverse_lat=True,
):
    grid_shp.loc[:, "mask"] = ~grid_shp.geometry.intersects(basin_shp.geometry.iloc[0])
    grid_array_mask, _, _ = createArray_from_gridshp(
        grid_shp,
        "mask",
        grid_res,
        int,
        missing_value,
        plot,
        reverse_lat,
    )
    
    return grid_shp, grid_array_mask


def createmaskArray_for_gridshp_intersect_gridshpRef(
    grid_shp,
    grid_shpRef,
    grid_res=None,
    missing_value=np.nan,
    plot=False,
    reverse_lat=True,
):
    grid_shp.loc[:, "mask"] = ~grid_shp.geometry.intersects(grid_shpRef.unary_union)
    grid_array_mask, _, _ = createArray_from_gridshp(
        grid_shp,
        "mask",
        grid_res,
        int,
        missing_value,
        plot,
        reverse_lat,
    )
    
    return grid_shp, grid_array_mask

    
def grids_array_coord_map(grid_shp, reverse_lat=True):
    """
    Generates mapping between geographical coordinates (longitude/latitude) and array indices.

    Parameters
    ----------
    grid_shp : GeoDataFrame
        A geospatial dataframe containing a 'point_geometry' column with x (longitude) and y (latitude) coordinates.
    reverse_lat : bool, optional
        If True, sorts latitude values in descending order (useful for direct plotting), by default True.

    Returns
    -------
    tuple
        - lon_list : list
            Sorted unique longitude values.
        - lat_list : list
            Sorted unique latitude values (descending if `reverse_lat=True`).
        - lon_map_index : dict
            Mapping from longitude values to array indices.
        - lat_map_index : dict
            Mapping from latitude values to array indices.
    """
    # lon/lat grid map into index to construct array
    lon_list = sorted(list(set(grid_shp["point_geometry"].x.values)))
    lat_list = sorted(
        list(set(grid_shp["point_geometry"].y.values)), reverse=reverse_lat
    )  # if True, large -> small, top is zero, it is useful for plot directly

    lon_map_index = dict(zip(lon_list, list(range(len(lon_list)))))
    lat_map_index = dict(zip(lat_list, list(range(len(lat_list)))))

    return lon_list, lat_list, lon_map_index, lat_map_index


def intersectGridsWithBasins(grids: Grids, basins: Basins):
    """
    Identifies grid cells that intersect with basin geometries.

    Parameters
    ----------
    grids : Grids
        A geospatial grid dataset.
    basins : Basins
        A geospatial dataset containing basin geometries.

    Returns
    -------
    tuple
        - basins : Basins
            The basins dataset with an added column storing intersecting grids.
        - intersects_grids : Grids
            The subset of grid cells that intersect with any basin.
    """
    intersects_grids_list = []
    intersects_grids = Grids()

    for i in basins.index:
        basin = basins.loc[i, "geometry"]
        intersects_grids_ = grids[grids.intersects(basin)]
        intersects_grids = pd.concat([intersects_grids, intersects_grids_], axis=0)
        intersects_grids_list.append(intersects_grids_)

    intersects_grids["grids_index"] = intersects_grids.index
    intersects_grids.index = list(range(len(intersects_grids)))

    droped_index = intersects_grids["grids_index"].drop_duplicates().index
    intersects_grids = intersects_grids.loc[droped_index, :]

    basins["intersects_grids"] = intersects_grids_list

    return basins, intersects_grids


def build_grid_shp(
    basin_shp,
    grid_res_level0,
    grid_res_level1,
    grid_res_level2,
    expand_grids_num=1,
    plot=False,
):
    # build grid_shp (Grids) for level1 (modeling scale), expand_grids_num=1 to avoid 0 (edge) flow direction in hydroanalysis
    grid_shp_lon_level1, grid_shp_lat_level1, grid_shp_level1 = createGridForBasin(basin_shp, grid_res_level1, expand_grids_num=expand_grids_num)
    _, _, _, boundary_grids_edge_x_y_level1 = grid_shp_level1.createBoundaryShp()
    
    # build grid_shp for level0 and level2 based on the boundary of level1
    grid_shp_lon_level0, grid_shp_lat_level0, grid_shp_level0 = createGridForBasin(basin_shp, grid_res_level0, boundary=boundary_grids_edge_x_y_level1)
    grid_shp_lon_level2, grid_shp_lat_level2, grid_shp_level2 = createGridForBasin(basin_shp, grid_res_level2, boundary=boundary_grids_edge_x_y_level1)
    
    # build grid_shp for level3 based on the shp file
    grid_shp_lon_level3, grid_shp_lat_level3, grid_shp_level3 = createGridForBasin(basin_shp, None, boundary=boundary_grids_edge_x_y_level1)
    
    # plot
    if plot:
        fig, axes = plt.subplots(1, 4)
        basin_shp.plot(ax=axes[0], edgecolor="k", alpha=0.5, facecolor="b")
        grid_shp_level0.plot(ax=axes[0], alpha=0.5, edgecolor="k", linewidth=0.5)
        
        basin_shp.plot(ax=axes[1], edgecolor="k", alpha=0.5, facecolor="b")
        grid_shp_level1.plot(ax=axes[1], alpha=0.5, edgecolor="k", linewidth=0.5)
        grid_shp_level1.point_geometry.plot(ax=axes[1], alpha=0.5, color="darkblue", markersize=1)
        
        basin_shp.plot(ax=axes[2], edgecolor="k", alpha=0.5, facecolor="b")
        grid_shp_level2.plot(ax=axes[2], alpha=0.5, edgecolor="k", linewidth=0.5)
        grid_shp_level2.point_geometry.plot(ax=axes[2], alpha=0.5, color="darkblue", markersize=1)
        
        basin_shp.plot(ax=axes[3], edgecolor="k", alpha=0.5, facecolor="b")
        plt.show(block=True)
        
    return grid_shp_level0, grid_shp_level1, grid_shp_level2, grid_shp_level3
