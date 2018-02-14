# Bull Creek

bull_creek_streamflow.cdl is a text representation of a netCDF file storing stream discharge data for river segments within the Bull Creek Watershed in Austin, Texas. Streamflow values are indexed by a comid, which is the National Hydrography Dataset Plus (NHDPlus) COMID uniquely identifying the stream feature for which the streamflow value applies. The line geometry for each COMID is stored in the GeoJSON file named nhd_flowline.json.  NHDPlus flowlines typically include polygons representing local catchment area for each flowline; those catchments are stored in the GeoJSON file named nhd_catchment.json. In bull_creek_streamflow.cdl, the upstream node of each stream segment is used as the stream location. These points are also stored in the GeoJSON file named upstream_point.json.

This use case demonstrates how line and polygon features could provide the spatial coordinates for modeled values associated with discrete river features.  CDL files which associate line geometries with the streamflow data are provided using the contiguous ragged array (CRA) and VLEN approaches.

The source of the streamflow values is the National Water Model. For more about the National Water Model, see http://water.noaa.gov/about/nwm.
