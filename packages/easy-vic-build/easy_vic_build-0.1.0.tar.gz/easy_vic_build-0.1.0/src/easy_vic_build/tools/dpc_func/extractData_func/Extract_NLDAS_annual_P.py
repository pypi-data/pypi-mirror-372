# code: utf-8
# author: Xudong Zheng
# email: z786909151@163.com

import matplotlib.pyplot as plt
import numpy as np
from rasterio.plot import show
from tqdm import *

from ...geo_func import search_grids
from ...geo_func.create_gdf import CreateGDF
from .... import logger

def ExtractData(
    grid_shp,
    grid_shp_res=0.125,
    plot=False,
    check_search=False,
    search_method="radius_rectangle_reverse",
):
    # read
    # NLDAS_annual_P_path = os.path.join(Evb_dir.__data_dir__, "NLDAS_annual_prec.npy")
    # data_annual_P = np.load(NLDAS_annual_P_path)
    # annual_P_lon = np.loadtxt(os.path.join(Evb_dir.__data_dir__, "annual_prec_lon.txt"))
    # annual_P_lat = np.loadtxt(os.path.join(Evb_dir.__data_dir__, "annual_prec_lat.txt"))
    from ...utilities import read_NLDAS_annual_prec
    data_annual_P, annual_P_lon, annual_P_lat = read_NLDAS_annual_prec()

    annual_P_lat_res = (max(annual_P_lat) - min(annual_P_lat)) / (len(annual_P_lat) - 1)
    annual_P_lon_res = (max(annual_P_lon) - min(annual_P_lon)) / (len(annual_P_lon) - 1)
    annual_P_lat_res = float(f"{annual_P_lat_res:.3g}")  # 0.125 deg ~= 13.875km
    annual_P_lon_res = float(f"{annual_P_lon_res:.3g}")

    # set grids_lat, lon
    grids_lat = grid_shp.point_geometry.y.to_list()
    grids_lon = grid_shp.point_geometry.x.to_list()
    # grids_lat = [grid_shp.loc[i, :].point_geometry.y for i in grid_shp.index]
    # grids_lon = [grid_shp.loc[i, :].point_geometry.x for i in grid_shp.index]

    # search grids
    logger.info("searching grids for NLDSA annual P... ...")
    
    # source data res: 0.125 deg ~= 13.875km
    if search_method == "radius":
        searched_grids_index = search_grids.search_grids_radius(
            dst_lat=grids_lat,
            dst_lon=grids_lon,
            src_lat=annual_P_lat,
            src_lon=annual_P_lon,
            lat_radius=grid_shp_res / 2,
            lon_radius=grid_shp_res / 2,
        )
        
    if search_method == "radius_rectangle":
        searched_grids_index = search_grids.search_grids_radius_rectangle(
            dst_lat=grids_lat,
            dst_lon=grids_lon,
            src_lat=annual_P_lat,
            src_lon=annual_P_lon,
            lat_radius=grid_shp_res / 2,
            lon_radius=grid_shp_res / 2,
        )
    
    elif search_method == "radius_rectangle_reverse":
        searched_grids_index = search_grids.search_grids_radius_rectangle_reverse(
            dst_lat=grids_lat,
            dst_lon=grids_lon,
            src_lat=annual_P_lat,
            src_lon=annual_P_lon,
            lat_radius=annual_P_lat_res / 2,
            lon_radius=annual_P_lon_res / 2,
        )
    
    elif search_method == "nearest":
        searched_grids_index = search_grids.search_grids_nearest(dst_lat=grids_lat, dst_lon=grids_lon,
                                                                 src_lat=annual_P_lat, src_lon=annual_P_lon,
                                                                 search_num=1,
                                                                 move_src_lat=None, move_src_lon=None)
    else:
        logger.warning(f"search method {search_method} not supported")
        
    # searched_grids_index = search_grids.search_grids_radius_rectangle_reverse(
    #     dst_lat=grids_lat,
    #     dst_lon=grids_lon,
    #     src_lat=annual_P_lat,
    #     src_lon=annual_P_lon,
    #     lat_radius=annual_P_lat_res / 2,
    #     lon_radius=annual_P_lon_res / 2,
    # )

    # read annual_P for each grid
    annual_P_in_src_grid_Value = []

    for i in tqdm(
        grid_shp.index, colour="green", desc=f"loop for each grid to extract annual P"
    ):
        searched_grid_index = searched_grids_index[i]
        searched_grid_lat = [
            annual_P_lat[searched_grid_index[0][j]]
            for j in range(len(searched_grid_index[0]))
        ]
        searched_grid_lon = [
            annual_P_lon[searched_grid_index[1][j]]
            for j in range(len(searched_grid_index[0]))
        ]
        searched_grid_data = [
            data_annual_P[searched_grid_index[0][j], searched_grid_index[1][j]]
            for j in range(len(searched_grid_index[0]))
        ]  # index: (lat, lon), namely (row, col)

        annual_P_in_src_grid_value = searched_grid_data[0]

        annual_P_in_src_grid_Value.append(annual_P_in_src_grid_value)

        # check
        if check_search and i == 0:
            cgdf = CreateGDF()
            grid_shp_grid = grid_shp.loc[[i], "geometry"]
            searched_grids_gdf = cgdf.createGDF_rectangle_central_coord(
                searched_grid_lon, searched_grid_lat, annual_P_lat_res
            )

            fig, ax = plt.subplots()
            grid_shp_grid.boundary.plot(ax=ax, edgecolor="r", linewidth=2)
            searched_grids_gdf.plot(
                ax=ax, edgecolor="k", linewidth=0.2, facecolor="b", alpha=0.5
            )
            ax.set_title("check search for NLDAS_annual_P")

    grid_shp[f"annual_P_in_src_grid_Value"] = np.array(annual_P_in_src_grid_Value)

    # plot
    if plot:
        # original, total
        plt.figure()
        show(
            data_annual_P,
            title=f"total_data_annual_P",
            extent=[
                annual_P_lon[0],
                annual_P_lon[-1],
                annual_P_lat[-1],
                annual_P_lat[0],
            ],
        )

        # original, clip
        # clip: extract before to improve speed
        xindex_start = np.where(annual_P_lon <= min(grids_lon) - grid_shp_res)[0][-1]
        xindex_end = np.where(annual_P_lon >= max(grids_lon) + grid_shp_res)[0][0]

        yindex_start = np.where(annual_P_lat >= max(grids_lat) + grid_shp_res)[0][
            -1
        ]  # large -> small
        yindex_end = np.where(annual_P_lat <= min(grids_lat) - grid_shp_res)[0][0]
        annual_P_lon_clip = annual_P_lon[xindex_start : xindex_end + 1]
        annual_P_lat_clip = annual_P_lat[yindex_start : yindex_end + 1]

        data_annual_P_clip = data_annual_P[
            yindex_start : yindex_end + 1, xindex_start : xindex_end + 1
        ]

        plt.figure()
        show(
            data_annual_P_clip,
            title=f"clip_data_data_annual_P",
            extent=[
                annual_P_lon_clip[0],
                annual_P_lon_clip[-1],
                annual_P_lat_clip[-1],
                annual_P_lat_clip[0],
            ],
        )

        # readed data_annual_P
        fig, ax = plt.subplots()
        grid_shp.plot(
            f"annual_P_in_src_grid_Value", ax=ax, edgecolor="k", linewidth=0.2
        )
        ax.set_title(f"annual_P_in_src_grid_Value")
        ax.set_xlim(
            [min(grids_lon) - grid_shp_res / 2, max(grids_lon) + grid_shp_res / 2]
        )
        ax.set_ylim(
            [min(grids_lat) - grid_shp_res / 2, max(grids_lat) + grid_shp_res / 2]
        )

    return grid_shp
