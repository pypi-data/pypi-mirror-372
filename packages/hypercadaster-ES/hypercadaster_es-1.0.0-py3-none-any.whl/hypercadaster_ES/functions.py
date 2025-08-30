"""Main functions module for hypercadaster_ES.

This module provides the primary entry points for downloading and merging
Spanish cadastral data with external geographic datasets.

Main functions:
    - download(): Downloads cadastral and related geographic data
    - merge(): Merges all downloaded data into a unified GeoDataFrame
"""

import os
import geopandas as gpd
from zipfile import ZipFile, BadZipFile

from hypercadaster_ES import mergers
from hypercadaster_ES import utils
from hypercadaster_ES import downloaders

def download(wd, province_codes=None, ine_codes=None, cadaster_codes=None,
             neighborhood_layer=True, postal_code_layer=True, census_layer=True,
             elevation_layer=True, open_data_layers=True, force=False):

    if force:
        try:
            os.removedirs(wd)
        except FileNotFoundError:
            pass
    utils.create_dirs(data_dir=wd)
    downloaders.download_file(dir=utils.cadaster_dir_(wd),
                              url="https://www.catastro.minhap.es/regularizacion/Regularizacion_municipios_finalizados.xlsx",
                              file="ine_inspire_codes.xlsx")

    # Convert inputs to list format
    if province_codes is not None:
        province_codes = province_codes if isinstance(province_codes, list) else [province_codes]
    if ine_codes is not None:
        ine_codes = ine_codes if isinstance(ine_codes, list) else [ine_codes]
    if cadaster_codes is not None:
        cadaster_codes = cadaster_codes if isinstance(cadaster_codes, list) else [cadaster_codes]

    # Filter which geographical area to download
    all_cadaster_codes = []
    
    if province_codes is None and ine_codes is None and cadaster_codes is None:
        raise ValueError("At least one of the arguments must be provided: province codes (province_codes), "
                         "municipality INE codes (ine_codes), or cadaster codes (cadaster_codes)")
    
    # Add cadaster codes from province_codes
    if province_codes is not None:
        municipalities = utils.list_municipalities(province_codes=province_codes, echo=False)
        province_cadaster_codes = [item['name'].split("-")[0] for item in municipalities]
        all_cadaster_codes.extend(province_cadaster_codes)
    
    # Add cadaster codes from ine_codes
    if ine_codes is not None:
        ine_cadaster_codes = utils.ine_to_cadaster_codes(utils.cadaster_dir_(wd), ine_codes)
        all_cadaster_codes.extend(ine_cadaster_codes)
    
    # Add directly provided cadaster codes
    if cadaster_codes is not None:
        all_cadaster_codes.extend(cadaster_codes)
    
    # Remove duplicates and set final cadaster_codes
    cadaster_codes = list(set(all_cadaster_codes))
    
    # Generate derived codes
    ine_codes = utils.cadaster_to_ine_codes(utils.cadaster_dir_(wd), cadaster_codes)
    province_codes = list(set([code[:2] for code in ine_codes]))

    # Download the cadaster datasets of that area
    downloaders.cadaster_downloader(cadaster_dir=utils.cadaster_dir_(wd), cadaster_codes=cadaster_codes)
    # Districts and neighborhoods definition are only available for the city of Barcelona
    if '08019' in ine_codes and neighborhood_layer:
        downloaders.download_file(dir=utils.districts_dir_(wd),
                                  url="https://opendata-ajuntament.barcelona.cat/data/dataset/808daafa-d9ce-48c0-"
                                      "925a-fa5afdb1ed41/resource/576bc645-9481-4bc4-b8bf-f5972c20df3f/download",
                                  file="districts.csv")
        downloaders.download_file(dir=utils.neighborhoods_dir_(wd),
                                  url="https://opendata-ajuntament.barcelona.cat/data/dataset/808daafa-d9ce-48c0-"
                                      "925a-fa5afdb1ed41/resource/b21fa550-56ea-4f4c-9adc-b8009381896e/download",
                                  file="neighbourhoods.csv")
    # Postal codes
    if postal_code_layer or elevation_layer:
        downloaders.download_postal_codes(postal_codes_dir=utils.postal_codes_dir_(wd), province_codes=province_codes)
    # Digital Elevation Model layer
    if elevation_layer:
        postal_codes_gdf = gpd.read_file(f"{utils.postal_codes_dir_(wd)}/postal_codes.geojson")
        postal_codes_gdf = gpd.GeoDataFrame(postal_codes_gdf, geometry='geometry', crs='EPSG:4326')
        bbox_postal_code = utils.get_bbox(gdf = postal_codes_gdf)
        downloaders.download_DEM_raster(raster_dir=utils.DEM_raster_dir_(wd), bbox=bbox_postal_code)
    # Census tracts and districts
    if census_layer:
        downloaders.download_census_tracts(census_tracts_dir=utils.census_tracts_dir_(wd), year=2022)
    # OpenDataBarcelona
    if '08019' in ine_codes and open_data_layers:
        downloaders.download_file(dir=utils.open_data_dir_(wd),
                                  url="https://opendata-ajuntament.barcelona.cat/data/dataset/3dc277bf-ff89-4b49-8f"
                                      "29-48a1122bb813/resource/2e123ea9-1819-46cf-a545-be61151fa97d/download",
                                  file="barcelona_establishments.csv")
        downloaders.download_file(dir=utils.open_data_dir_(wd),
                                  url="https://opendata-ajuntament.barcelona.cat/data/dataset/fe177673-0f83-42e7-b3"
                                      "5a-ddea901be8bc/resource/99764d55-b1be-4281-b822-4277442cc721/download/22093"
                                      "0_censcomercialbcn_opendata_2022_v10_mod.csv",
                                  file="barcelona_ground_premises.csv")
        downloaders.download_file(dir=utils.open_data_dir_(wd),
                                  url="https://opendata-ajuntament.barcelona.cat/data/dataset/6b5cfa7b-1d8d-45f0-990a-"
                                      "d1844d43ffd1/resource/26c6be33-44f5-4596-8a29-7ac152546ca7/download",
                                  file="barcelona_carrerer.zip")
        try:
            with ZipFile(f"{utils.open_data_dir_(wd)}/barcelona_carrerer.zip", 'r') as zip:
                zip.extractall(utils.open_data_dir_(wd))
                os.rename(f"{utils.open_data_dir_(wd)}/Adreces_elementals.gpkg",
                          f"{utils.open_data_dir_(wd)}/barcelona_carrerer.gpkg")
                os.remove(f"{utils.open_data_dir_(wd)}/barcelona_carrerer.zip")
        except BadZipFile:
            os.remove(f"{utils.open_data_dir_(wd)}/barcelona_carrerer.zip")

def merge(wd, province_codes=None, ine_codes=None, cadaster_codes=None,
          neighborhood_layer=True, postal_code_layer=True, census_layer=True, elevations_layer=True,
          open_data_layers=True, building_parts_inference=False, building_parts_plots=False,
          plot_zones_ratio=0.01, use_CAT_files=False, CAT_files_rel_dir="CAT_files"):

    # Convert inputs to list format
    if province_codes is not None:
        province_codes = province_codes if isinstance(province_codes, list) else [province_codes]
    if ine_codes is not None:
        ine_codes = ine_codes if isinstance(ine_codes, list) else [ine_codes]
    if cadaster_codes is not None:
        cadaster_codes = cadaster_codes if isinstance(cadaster_codes, list) else [cadaster_codes]

    # Filter which geographical area to download
    all_cadaster_codes = []
    
    if province_codes is None and ine_codes is None and cadaster_codes is None:
        raise ValueError("At least one of the arguments must be provided: province codes (province_codes), "
                         "municipality INE codes (ine_codes), or cadaster codes (cadaster_codes)")
    
    # Add cadaster codes from province_codes
    if province_codes is not None:
        municipalities = utils.list_municipalities(province_codes=province_codes, echo=False)
        province_cadaster_codes = [item['name'].split("-")[0] for item in municipalities]
        all_cadaster_codes.extend(province_cadaster_codes)
    
    # Add cadaster codes from ine_codes
    if ine_codes is not None:
        ine_cadaster_codes = utils.ine_to_cadaster_codes(utils.cadaster_dir_(wd), ine_codes)
        all_cadaster_codes.extend(ine_cadaster_codes)
    
    # Add directly provided cadaster codes
    if cadaster_codes is not None:
        all_cadaster_codes.extend(cadaster_codes)
    
    # Remove duplicates and set final cadaster_codes
    cadaster_codes = list(set(all_cadaster_codes))
    
    # Validate building analysis constraints
    if (building_parts_inference or building_parts_plots) and len(cadaster_codes) > 1:
        raise ValueError(
            f"Building parts inference and plots are computationally intensive and can only be enabled "
            f"for single municipality processing. Found {len(cadaster_codes)} municipalities: {cadaster_codes}. "
            f"Please process municipalities individually when using building_parts_inference=True or "
            f"building_parts_plots=True."
        )

    gdf = mergers.join_cadaster_data(
        cadaster_dir=utils.cadaster_dir_(wd),
        cadaster_codes=cadaster_codes,
        results_dir=utils.results_dir_(wd),
        open_street_dir=utils.open_street_dir_(wd),
        building_parts_inference=building_parts_inference,
        use_CAT_files=use_CAT_files,
        building_parts_plots=building_parts_plots,
        plot_zones_ratio=plot_zones_ratio,
        open_data_layers=open_data_layers,
        open_data_layers_dir=utils.open_data_dir_(wd),
        CAT_files_dir=f"{wd}/{CAT_files_rel_dir}"
    )

    if census_layer:
        gdf = mergers.join_by_census_tracts(
            gdf = gdf,
            census_tract_dir=utils.census_tracts_dir_(wd))
    if neighborhood_layer:
        gdf = mergers.join_by_neighbourhoods(
            gdf = gdf,
            neighbourhoods_dir=utils.neighborhoods_dir_(wd))
    if postal_code_layer:
        gdf = mergers.join_by_postal_codes(
            gdf = gdf,
            postal_codes_dir=utils.postal_codes_dir_(wd))
    if elevations_layer:
        gdf = mergers.join_DEM_raster(
            gdf = gdf,
            raster_dir = utils.DEM_raster_dir_(wd)
        )
    if "index" in gdf.columns:
        gdf.drop("index", axis=1, inplace=True)

    # columns that have dicts
    cols_with_dicts = [c for c in gdf.columns
                       if gdf[c].apply(lambda v: isinstance(v, dict) or isinstance(v,list)).any()]

    subset = [c for c in gdf.columns if c not in cols_with_dicts + ['geometry']]
    gdf = gdf.drop_duplicates(subset=subset, keep='first')

    return gdf

