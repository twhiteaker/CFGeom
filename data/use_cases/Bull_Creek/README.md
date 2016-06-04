# Bull Creek

nwm_bullcreek.cdl is a CDL representation of a netCDF file extracted from example National Water Model results. The file includes modeled stream discharge for a single time step for streams within the Bull Creek Watershed in Austin, Texas. Streamflow values are indexed by a station_id, which is actually the National Hydrography Dataset COMID uniquely identifying the stream feature for which the streamflow value applies. The line geometry for each COMID is stored in the GeoJSON file named nhd_flowline.json.

This use case would demonstrate how simple line features (LineString WKT type) could be used to provide the spatial coordinates for modeled values associate with discrete river features.

The original model results from which the Bull Creek data were extracted can be found at http://para.nomads.ncep.noaa.gov/pub/data/nccf/com/nwm/para/nwm.20160526/medium_range/ in a file named nwm.t06z.medium_range.channel_rt.f018.conus.nc.gz.

For more about the National Water Model, see http://water.noaa.gov/about/nwm.
