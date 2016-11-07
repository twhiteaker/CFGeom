# Bull Creek

nwm_bullcreek.cdl is a CDL representation of a netCDF file generated from the 2016-11-07T19Z short range forecast from the National Water Model. The file includes modeled stream discharge for streams within the Bull Creek Watershed in Austin, Texas. Streamflow values are indexed by a station_id, which is the National Hydrography Dataset Plus (NHDPlus) COMID uniquely identifying the stream feature for which the streamflow value applies. The line geometry for each COMID is stored in the GeoJSON file named nhd_flowline.json.  NHDPlus flowlines typically include polygons representing local catchments area for each flowline; those catchments are stored in the GeoJSON file named nhd_catchment. The National Water Center, which runs the National Water Model, includes coordinates of the upstream end of each modeled river segment to support spatial display. These points for Bull Creek are in the GeoJSON file named upstream_point.json.

This use case would demonstrate how simple point, line, and polygon features could provide the spatial coordinates for modeled values associated with discrete river features.

For more about the National Water Model, see http://water.noaa.gov/about/nwm.
