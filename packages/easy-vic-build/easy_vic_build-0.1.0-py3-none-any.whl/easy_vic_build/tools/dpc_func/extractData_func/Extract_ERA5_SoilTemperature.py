# code: utf-8
# author: Xudong Zheng
# email: z786909151@163.com

import os

import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
from rasterio.plot import show
from tqdm import *

from ...geo_func import resample, search_grids
from ...geo_func.create_gdf import CreateGDF
from .... import logger


def ExtractData(
    grid_shp,
    grid_shp_res=0.125,
    plot_layer=False,
    check_search=False,
    search_method="radius_rectangle_reverse",
):
    # plot_layer: start from 1
    # general
    home = "E:\\data\\hydrometeorology\\ERA5\\ERA5-Land monthly averaged data from 1950 to present\\US\\data_soilTemperature"

    # read data
    stls_data = []

    for i in range(1, 5):
        fn = os.path.join(home, f"Soil_temperature_level{i}_CDS_Beta.grib")
        with xr.open_dataset(fn, engine="cfgrib") as dataset:
            stl_data_ = dataset.variables[f"stl{i}"]
            stl_data_ = np.nanmean(stl_data_, axis=0)

            # unit: K->C
            stl_data_ -= 273.15

            stls_data.append(stl_data_)
            if i == 1:
                stl_lat = dataset.variables["latitude"].values  # large -> small
                stl_lon = dataset.variables["longitude"].values
                stl_all_layers_mean = stl_data_
            else:
                stl_all_layers_mean += stl_data_

    stl_all_layers_mean /= 4

    stl_lat_res = (stl_lat.max() - stl_lat.min()) / (len(stl_lat) - 1)
    stl_lon_res = (stl_lon.max() - stl_lon.min()) / (len(stl_lon) - 1)

    stl_lat_res = float(f"{stl_lat_res:.2g}")
    stl_lat_res = float(f"{stl_lat_res:.2g}")
    
    # set grids_lat, lon
    grids_lat = grid_shp.point_geometry.y.to_list()
    grids_lon = grid_shp.point_geometry.x.to_list()
    # grids_lat = [grid_shp.loc[i, :].point_geometry.y for i in grid_shp.index]
    # grids_lon = [grid_shp.loc[i, :].point_geometry.x for i in grid_shp.index]

    # search grids, 0.1 deg
    logger.info("searching grids for ERA5 ST... ...")
    
    # source data res: 0.1 deg ~= 11.1km
    if search_method == "radius":
        searched_grids_index = search_grids.search_grids_radius(
            dst_lat=grids_lat,
            dst_lon=grids_lon,
            src_lat=stl_lat,
            src_lon=stl_lon,
            lat_radius=grid_shp_res / 2,
            lon_radius=grid_shp_res / 2,
        )
        
    if search_method == "radius_rectangle":
        searched_grids_index = search_grids.search_grids_radius_rectangle(
            dst_lat=grids_lat,
            dst_lon=grids_lon,
            src_lat=stl_lat,
            src_lon=stl_lon,
            lat_radius=grid_shp_res / 2,
            lon_radius=grid_shp_res / 2,
        )
    
    elif search_method == "radius_rectangle_reverse":
        searched_grids_index = search_grids.search_grids_radius_rectangle_reverse(
            dst_lat=grids_lat,
            dst_lon=grids_lon,
            src_lat=stl_lat,
            src_lon=stl_lon,
            lat_radius=stl_lat_res / 2,
            lon_radius=stl_lon_res / 2,
        )
    
    elif search_method == "nearest":
        searched_grids_index = search_grids.search_grids_nearest(dst_lat=grids_lat, dst_lon=grids_lon,
                                                                 src_lat=stl_lat, src_lon=stl_lon,
                                                                 search_num=1,
                                                                 move_src_lat=None, move_src_lon=None)
    else:
        logger.warning(f"search method {search_method} not supported")

    # read soil temperature for each grid
    stl_all_layers_mean_Value = []

    for i in tqdm(
        grid_shp.index,
        colour="green",
        desc=f"loop for each grid to extract ST",
    ):
        searched_grid_index = searched_grids_index[i]
        dst_lat_grid = grid_shp.loc[i, :].point_geometry.y
        dst_lon_grid = grid_shp.loc[i, :].point_geometry.x
        
        searched_grid_lat = [
            stl_lat[searched_grid_index[0][j]]
            for j in range(len(searched_grid_index[0]))
        ]
        searched_grid_lon = [
            stl_lon[searched_grid_index[1][j]]
            for j in range(len(searched_grid_index[0]))
        ]
        searched_grid_data = [
            stl_all_layers_mean[searched_grid_index[0][j], searched_grid_index[1][j]]
            for j in range(len(searched_grid_index[0]))
        ]  # index: (lat, lon), namely (row, col)

        searched_resample_data = np.nanmean(np.array(searched_grid_data)) # searched_grid_data[0]
        stl_all_layers_mean_Value.append(searched_resample_data)
        
        # check
        if check_search and i == 0:
            cgdf = CreateGDF()
            grid_shp_grid = grid_shp.loc[[i], "geometry"]
            searched_grids_gdf = cgdf.createGDF_rectangle_central_coord(
                searched_grid_lon, searched_grid_lat, stl_lat_res
            )

            fig, ax = plt.subplots()
            grid_shp_grid.boundary.plot(ax=ax, edgecolor="r", linewidth=2)
            searched_grids_gdf.plot(
                ax=ax, edgecolor="k", linewidth=0.2, facecolor="b", alpha=0.5
            )
            ax.set_title("check search for ERA5 ST")

    # save
    grid_shp[f"stl_all_layers_mean_Value"] = np.array(stl_all_layers_mean_Value)

    # plot
    if plot_layer:
        # original, total
        show(
            stl_all_layers_mean,
            title=f"original data, all layers mean",
            extent=[
                stl_lon[0],
                stl_lon[-1],
                stl_lat[-1],
                stl_lat[0],
            ],
        )
        
        # readed all_layer_mean
        fig, ax = plt.subplots()
        grid_shp.plot(f"stl_all_layers_mean_Value", ax=ax, edgecolor="k", linewidth=0.2)
        ax.set_title(f"stl_all_layers_mean_Value")
        ax.set_xlim(
            [min(grids_lon) - grid_shp_res / 2, max(grids_lon) + grid_shp_res / 2]
        )
        ax.set_ylim(
            [min(grids_lat) - grid_shp_res / 2, max(grids_lat) + grid_shp_res / 2]
        )
        
    return grid_shp


if __name__ == "__main__":
    # # general
    # home = "E:\\data\\hydrometeorology\\ERA5\\ERA5-Land monthly averaged data from 1950 to present\\data_soilTemperature"
    # fpath = os.path.join(home, "Soil_temperature_level1_CDS_Beta.grib")

    # # read data
    # dataset = xr.open_dataset(fpath, engine="cfgrib")
    pass
