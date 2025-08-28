# code: utf-8
# author: Xudong Zheng
# email: z786909151@163.com
import os
import re

import numpy as np
import pandas as pd
import rasterio
import rasterio.transform
from matplotlib import pyplot as plt
from netCDF4 import Dataset
from pyproj import CRS
from rasterio.plot import show
from rasterio.warp import Resampling, calculate_default_transform, reproject
from tqdm import *

from ...geo_func import resample, search_grids
from ...geo_func.create_gdf import CreateGDF
from .... import logger


def combine_MODIS_LAI_data(reverse_lat=True):
    src_home = "E:\\data\\hydrometeorology\\MODIS\\MOD15A2H v061_LAI_FPAR_8day_500m_2000_02_18_to_Present\\US\\data"
    dst_home = "E:\\data\\hydrometeorology\\MODIS\\MOD15A2H v061_LAI_FPAR_8day_500m_2000_02_18_to_Present\\US"
    suffix = ".hdf"
    src_names = [n for n in os.listdir(src_home) if n.endswith(suffix)]

    # initial array
    x_mins = []
    x_maxs = []
    y_mins = []
    y_maxs = []
    x_ress = []
    y_ress = []
    for i in tqdm(range(len(src_names)), desc="initial array", colour="g"):
        src_name = src_names[i]
        src_path = os.path.join(src_home, src_name)

        # get date
        src_date = src_name[src_name.find(".A") + 2 :]
        src_date = src_date[: src_date.find(".")]
        src_year = int(src_date[:4])
        src_day_num = int(src_date[4:])

        stand_date = pd.date_range(f"{src_year}0101", f"{src_year}1231", freq="D")
        src_stand_date = stand_date[src_day_num - 1]

        src_month = src_stand_date.month

        if src_year < 2011:
            # read data
            with Dataset(src_path, "r", format="NETCDF4_CLASSIC") as dataset:
                # get xy
                structureMetadata = dataset.__dict__["StructMetadata.0"]
                UpperLeftPointMtrs = [
                    float(x)
                    for x in re.findall(
                        r"UpperLeftPointMtrs=\((.*)\)", structureMetadata
                    )[0].split(",")
                ]
                LowerRightPointMtrs = [
                    float(x)
                    for x in re.findall(r"LowerRightMtrs=\((.*)\)", structureMetadata)[
                        0
                    ].split(",")
                ]

                x_min = UpperLeftPointMtrs[0]
                x_max = LowerRightPointMtrs[0]
                y_min = LowerRightPointMtrs[1]
                y_max = UpperLeftPointMtrs[1]

                height = int(re.findall(r"YDim=(.*?)\n", structureMetadata)[0])
                width = int(re.findall(r"XDim=(.*?)\n", structureMetadata)[0])

                x_res = (x_max - x_min) / (width - 1)
                y_res = (y_max - y_min) / (height - 1)

                x_mins.append(x_min)
                x_maxs.append(x_max)
                y_mins.append(y_min)
                y_maxs.append(y_max)
                x_ress.append(x_res)
                y_ress.append(y_res)

    array_x_min = min(x_mins)
    array_x_max = max(x_maxs)
    array_x_res = x_ress[0]
    array_y_min = min(y_mins)
    array_y_max = max(y_maxs)
    array_y_res = y_ress[0]

    array_height = round((array_y_max - array_y_min) / array_y_res) + 1
    array_width = round((array_x_max - array_x_min) / array_x_res) + 1

    array_x = np.linspace(array_x_min, array_x_max, array_width)
    array_y = (
        np.linspace(array_y_max, array_y_min, array_height)
        if reverse_lat
        else np.linspace(array_y_min, array_y_max, array_height)
    )  # large -> small

    # loop to Mosaic
    LAI_months = {}
    for i in tqdm(range(len(src_names)), desc="loop to Mosaic", colour="g"):
        src_name = src_names[i]
        src_path = os.path.join(src_home, src_name)

        # get date
        src_date = src_name[src_name.find(".A") + 2 :]
        src_date = src_date[: src_date.find(".")]
        src_year = int(src_date[:4])
        src_day_num = int(src_date[4:])

        stand_date = pd.date_range(f"{src_year}0101", f"{src_year}1231", freq="D")
        src_stand_date = stand_date[src_day_num - 1]

        src_month = src_stand_date.month

        if src_year < 2011:
            # read data
            with Dataset(src_path, "r", format="NETCDF4_CLASSIC") as dataset:
                # read LAI
                LAI = dataset.variables["Lai_500m"][:, :]
                LAI = LAI.filled(np.nan)

                # get xy
                structureMetadata = dataset.__dict__["StructMetadata.0"]
                UpperLeftPointMtrs = [
                    float(x)
                    for x in re.findall(
                        r"UpperLeftPointMtrs=\((.*)\)", structureMetadata
                    )[0].split(",")
                ]
                LowerRightPointMtrs = [
                    float(x)
                    for x in re.findall(r"LowerRightMtrs=\((.*)\)", structureMetadata)[
                        0
                    ].split(",")
                ]

                x_min = UpperLeftPointMtrs[0]
                x_max = LowerRightPointMtrs[0]
                y_min = LowerRightPointMtrs[1]
                y_max = UpperLeftPointMtrs[1]

                height = int(re.findall(r"YDim=(.*?)\n", structureMetadata)[0])
                width = int(re.findall(r"XDim=(.*?)\n", structureMetadata)[0])

                x_res = (x_max - x_min) / (width - 1)
                y_res = (y_max - y_min) / (height - 1)

                x = np.linspace(x_min, x_max, width)
                y = (
                    np.linspace(y_max, y_min, height)
                    if reverse_lat
                    else np.linspace(y_min, y_max, height)
                )  # large -> small

                # LAI array
                LAI_array = np.full((array_height, array_width), fill_value=np.nan)

                # xy -> index
                x_index_start = np.where(abs((array_x - x_min)) <= 0.001)[0][0]
                x_index_end = np.where(abs((array_x - x_max)) <= 0.001)[0][0]
                y_index_end = np.where(abs((array_y - y_min)) <= 0.001)[0][0]
                y_index_start = np.where(abs((array_y - y_max)) <= 0.001)[0][
                    0
                ]  # large is start

                if not reverse_lat:
                    y_index_start, y_index_end = y_index_end, y_index_start

                # print(x_index_start, x_index_end, y_index_start, y_index_end)

                LAI_array[
                    y_index_start : y_index_end + 1, x_index_start : x_index_end + 1
                ] = LAI

                # plt.imshow(LAI)
                # plt.imshow(LAI_array)

            # combine
            try:
                LAI_month = LAI_months[src_month]
                LAI_month = LAI_month.reshape((*LAI_month.shape, 1))
                LAI_array = LAI_array.reshape((*LAI_array.shape, 1))
                LAI_month = np.concatenate([LAI_month, LAI_array], axis=2)
                LAI_month = np.nanmean(LAI_month, axis=2)
                LAI_month_temp = {src_month: LAI_month}
            except:
                LAI_month = LAI_array
                LAI_month_temp = {src_month: LAI_month}

            LAI_months.update(LAI_month_temp)

    # transform
    projection_param = [
        float(_param)
        for _param in re.findall(r"ProjParams=\((.*?)\)", structureMetadata)[0].split(
            ","
        )
    ]
    proj4_LAI = "+proj={} +R={:0.4f} +lon_0={:0.4f} +lat_0={:0.4f} +x_0={:0.4f} +y_0={:0.4f} ".format(
        "sinu",
        projection_param[0],
        projection_param[4],
        projection_param[5],
        projection_param[6],
        projection_param[7],
    )
    crs_LAI = CRS.from_proj4(proj4_LAI)

    transform = rasterio.transform.from_origin(
        array_x_min - array_x_res / 2,
        array_y_max + array_y_res / 2,
        array_x_res,
        array_y_res,
    )
    # transformer = Transformer.from_crs(crs_LAI, "EPSG:4326")
    # lon_LAI = [transformer.transform(x, 0)[1] for x in array_x]
    # lat_LAI = [transformer.transform(0, y)[0] for y in array_y]

    # save
    with rasterio.open(
        os.path.join(dst_home, "combine_data_2000_2010_months.tif"),
        "w",
        driver="GTiff",
        height=array_height,
        width=array_width,
        count=12,
        dtype=LAI_months[1].dtype,
        crs=crs_LAI,
        transform=transform,
    ) as dst:
        for i in range(1, 13):
            dst.write(LAI_months[i], i)


def reproject_MODIS_LAI_data():
    src_home = "E:\\data\\hydrometeorology\\MODIS\\MOD15A2H v061_LAI_FPAR_8day_500m_2000_02_18_to_Present\\US"
    dst_home = src_home
    src_path = os.path.join(src_home, "combine_data_2000_2010_months.tif")
    dst_path = os.path.join(dst_home, "combine_data_2000_2010_months_reproject.tif")

    # read
    dst_crs = "EPSG:4326"
    with rasterio.open(src_path) as src:
        transform, width, height = calculate_default_transform(
            src.crs, dst_crs, src.width, src.height, *src.bounds
        )
        kwargs = src.meta.copy()
        kwargs.update(
            {"crs": dst_crs, "transform": transform, "width": width, "height": height}
        )

        # reproject
        with rasterio.open(dst_path, "w", **kwargs) as dst:
            for i in range(1, src.count + 1):
                reproject(
                    source=rasterio.band(src, i),
                    destination=rasterio.band(dst, i),
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=transform,
                    dst_crs=dst_crs,
                    resampling=Resampling.nearest,
                )


def gapfillingLAI():
    src_home = "E:\\data\\hydrometeorology\\MODIS\\MOD15A2H v061_LAI_FPAR_8day_500m_2000_02_18_to_Present\\US"
    dst_home = src_home
    src_path = os.path.join(src_home, "combine_data_2000_2010_months_reproject.tif")
    dst_path = os.path.join(
        dst_home, "combine_data_2000_2010_months_reproject_filled.tif"
    )

    with rasterio.open(src_path, "r") as src:
        kwargs = src.meta.copy()

        # reproject
        with rasterio.open(dst_path, "w", **kwargs) as dst:
            for i in range(1, dst.count + 1):
                # read
                dst_array = src.read(i)

                # fill
                df = pd.DataFrame(dst_array)
                filled_df = df.fillna(method="ffill", axis=1)
                filled_data = filled_df.to_numpy()

                # write band data into dst
                dst.write(filled_data, i)


def ExtractData(
    grid_shp,
    grid_shp_res=0.125,
    plot_month=False,
    save_original=False,
    check_search=False,
):
    # read LAI, months: 1-12
    LAI_home = "E:\\data\\hydrometeorology\\MODIS\\MOD15A2H v061_LAI_FPAR_8day_500m_2000_02_18_to_Present\\US"
    LAI_path = os.path.join(
        LAI_home, "combine_data_2000_2010_months_reproject_filled.tif"
    )

    # read landcover, classes: 0-14
    umd_landcover_1km_path = "E:\\data\\LULC\\UMD_landcover_classification\\UMD_GLCF_GLCDS_data\\differentFormat\\data.tiff"

    # set grids_lat, lon
    grids_lat = grid_shp.point_geometry.y.to_list()
    grids_lon = grid_shp.point_geometry.x.to_list()
    # grids_lat = [grid_shp.loc[i, :].point_geometry.y for i in grid_shp.index]
    # grids_lon = [grid_shp.loc[i, :].point_geometry.x for i in grid_shp.index]

    # read LAI, lat, lon, res
    LAI_months_clip = dict(zip(list(range(1, 13)), [[] for m in range(1, 13)]))
    LAI_months = dict(zip(list(range(1, 13)), [[] for m in range(1, 13)]))
    with rasterio.open(LAI_path, "r") as src:
        src_transform = src.transform
        width = src.width
        height = src.height

        ul = src_transform * (0, 0)
        lr = src_transform * (width, height)

        LAI_lon = np.linspace(ul[0], lr[0], width)
        LAI_lat = np.linspace(ul[1], lr[1], height)  # large -> small

        LAI_lat_res = (max(LAI_lat) - min(LAI_lat)) / (len(LAI_lat) - 1)
        LAI_lon_res = (max(LAI_lon) - min(LAI_lon)) / (len(LAI_lon) - 1)
        LAI_lat_res = float(f"{LAI_lat_res:.5g}")  # 0.0072277 deg ~= 0.8km
        LAI_lon_res = float(f"{LAI_lon_res:.5g}")

        # clip
        xindex_start = np.where(LAI_lon <= min(grids_lon) - grid_shp_res)[0][-1]
        xindex_end = np.where(LAI_lon >= max(grids_lon) + grid_shp_res)[0][0]

        yindex_start = np.where(LAI_lat >= max(grids_lat) + grid_shp_res)[0][
            -1
        ]  # large -> small
        yindex_end = np.where(LAI_lat <= min(grids_lat) - grid_shp_res)[0][0]

        LAI_lon_clip = LAI_lon[xindex_start : xindex_end + 1]
        LAI_lat_clip = LAI_lat[yindex_start : yindex_end + 1]

        for m in range(1, 13):
            LAI_month = src.read(m)
            LAI_month_clip = LAI_month[
                yindex_start : yindex_end + 1, xindex_start : xindex_end + 1
            ]

            # append
            LAI_months[m] = LAI_month
            LAI_months_clip[m] = LAI_month_clip

    # read umd
    with rasterio.open(umd_landcover_1km_path, mode="r") as dataset:
        # umd lat lon
        width = dataset.width
        height = dataset.height

        umd_lon = np.array([dataset.xy(0, i)[0] for i in range(width)])
        umd_lat = np.array([dataset.xy(i, 0)[1] for i in range(height)])
        # test: row, column = dataset.index(umd_lon[103], umd_lat[95])

    umd_lat_res = (max(umd_lat) - min(umd_lat)) / (len(umd_lat) - 1)
    umd_lon_res = (max(umd_lon) - min(umd_lon)) / (len(umd_lon) - 1)
    umd_lat_res = float(f"{umd_lat_res:.5g}")
    umd_lon_res = float(f"{umd_lon_res:.5g}")

    # clip umd
    xindex_start = np.where(umd_lon <= min(grids_lon) - grid_shp_res)[0][-1]
    xindex_end = np.where(umd_lon >= max(grids_lon) + grid_shp_res)[0][0]

    yindex_start = np.where(umd_lat >= max(grids_lat) + grid_shp_res)[0][
        -1
    ]  # large -> small
    yindex_end = np.where(umd_lat <= min(grids_lat) - grid_shp_res)[0][0]

    umd_lon_clip = umd_lon[xindex_start : xindex_end + 1]
    umd_lat_clip = umd_lat[yindex_start : yindex_end + 1]

    # search grids
    logger.info("searching grids for LAI... ...")

    # source data res: 1km (UMD LULC)
    searched_grids_index = search_grids.search_grids_radius_rectangle(
        dst_lat=grids_lat,
        dst_lon=grids_lon,
        src_lat=umd_lat_clip,
        src_lon=umd_lon_clip,
        lat_radius=grid_shp_res / 2,
        lon_radius=grid_shp_res / 2,
    )

    # read umd grids and extract LAI
    LAI_mean_Value = dict(zip(list(range(1, 13)), [[] for m in range(1, 13)]))
    if save_original:
        original_Value = dict(zip(list(range(1, 13)), [[] for m in range(1, 13)]))
        original_lat = []
        original_lon = []

    for i in tqdm(
        grid_shp.index, colour="green", desc="loop for each grid to extract LAI"
    ):
        # umd grids
        searched_grid_index = searched_grids_index[i]
        searched_grids_lat_umd = [
            umd_lat_clip[searched_grid_index[0][j]]
            for j in range(len(searched_grid_index[0]))
        ]
        searched_grids_lon_umd = [
            umd_lon_clip[searched_grid_index[1][j]]
            for j in range(len(searched_grid_index[0]))
        ]

        # LAI grids
        searched_match_grids_data = dict(
            zip(list(range(1, 13)), [[] for m in range(1, 13)])
        )
        searched_match_grids_lat = []
        searched_match_grids_lon = []

        # match LAI grid with umd grid
        for j in range(len(searched_grid_index[0])):
            searched_grid_lat = umd_lat_clip[searched_grid_index[0][j]]
            searched_grid_lon = umd_lon_clip[searched_grid_index[1][j]]

            # search neartest LAI grid with umd grid, 1km to 0.8km
            searched_grids_index_match = search_grids.search_grids_nearest(
                dst_lat=[searched_grid_lat],
                dst_lon=[searched_grid_lon],
                src_lat=LAI_lat_clip,
                src_lon=LAI_lon_clip,
                search_num=1,
                leave=False,
            )[0]

            searched_match_grid_lat = LAI_lat_clip[searched_grids_index_match[0][0]]
            searched_match_grid_lon = LAI_lon_clip[searched_grids_index_match[1][0]]

            searched_match_grids_lat.append(searched_match_grid_lat)
            searched_match_grids_lon.append(searched_match_grid_lon)

            # loop for months
            for m in range(1, 13):
                LAI_month_clip = LAI_months_clip[m]
                searched_match_grid_data = LAI_month_clip[
                    searched_grids_index_match[0][0], searched_grids_index_match[1][0]
                ]
                searched_match_grids_data[m].append(searched_match_grid_data)

        # resample and save
        for m in range(1, 13):
            LAI_mean_value = resample.resampleMethod_SimpleAverage(
                searched_match_grids_data[m],
                searched_match_grids_lat,
                searched_match_grids_lon,
            )

            # save
            LAI_mean_Value[m].append(LAI_mean_value)

            if save_original:
                original_Value[m].append(searched_match_grids_data[m])
                if m == 1:
                    original_lat.append(searched_match_grids_lat)
                    original_lon.append(searched_match_grids_lon)

        # check
        if check_search and i == 0:
            cgdf = CreateGDF()
            grid_shp_grid = grid_shp.loc[[i], "geometry"]
            searched_umd_grids_gdf = cgdf.createGDF_rectangle_central_coord(
                searched_grids_lon_umd, searched_grids_lat_umd, umd_lat_res
            )
            searched_match_LAI_grids_gdf = cgdf.createGDF_rectangle_central_coord(
                searched_match_grids_lon, searched_match_grids_lat, LAI_lat_res
            )

            fig, ax = plt.subplots()
            grid_shp_grid.boundary.plot(ax=ax, edgecolor="r", linewidth=2)
            searched_umd_grids_gdf.plot(
                ax=ax, edgecolor="k", linewidth=1, facecolor="g", alpha=0.5
            )
            searched_match_LAI_grids_gdf.plot(
                ax=ax, edgecolor="k", linewidth=1, facecolor="b", alpha=0.5
            )
            ax.set_title("check search for MODIS LAI")

    # save in grid_shp
    for m in range(1, 13):
        grid_shp[f"MODIS_LAI_mean_Value_month{m}"] = np.array(LAI_mean_Value[m])
        if save_original:
            grid_shp["MODIS_LAI_original_lat"] = original_lat
            grid_shp["MODIS_LAI_original_lon"] = original_lon
            grid_shp[f"MODIS_LAI_original_Value_month{m}"] = original_Value[m]

    # plot
    if plot_month:
        # original, total
        plt.figure()
        show(
            LAI_months[plot_month],
            title=f"total_data_LAI_month{plot_month}",
            extent=[LAI_lon[0], LAI_lon[-1], LAI_lat[-1], LAI_lat[0]],
        )

        # original, clip
        plt.figure()
        show(
            LAI_months_clip[plot_month],
            title=f"total_data_LAI_clip_month{plot_month}",
            extent=[
                LAI_lon_clip[0],
                LAI_lon_clip[-1],
                LAI_lat_clip[-1],
                LAI_lat_clip[0],
            ],
        )

        # readed mean
        fig, ax = plt.subplots()
        grid_shp.plot(
            f"MODIS_LAI_mean_Value_month{plot_month}",
            ax=ax,
            edgecolor="k",
            linewidth=0.2,
        )
        ax.set_title(f"readed mean LAI month{plot_month}")
        ax.set_xlim(
            [min(grids_lon) - grid_shp_res / 2, max(grids_lon) + grid_shp_res / 2]
        )
        ax.set_ylim(
            [min(grids_lat) - grid_shp_res / 2, max(grids_lat) + grid_shp_res / 2]
        )

    return grid_shp


if __name__ == "__main__":
    # combine_MODIS_LAI_data(reverse_lat=True)
    # reproject_MODIS_LAI_data()
    # gapfillingLAI()
    pass
