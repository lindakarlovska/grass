import os
import grass.script as gs
import grass.jupyter as gj

if os.environ.get("GRASS_JUPYTER_FROM_GUI") == "1":
    gisenv = gs.gisenv()
    gisdbase = gisenv["GISDBASE"]
    location = gisenv["LOCATION_NAME"]
    mapset = gisenv["MAPSET"]
    mapset_path = "{gisdbase}/{location}/{mapset}".format(
        gisdbase=gisdbase, location=location, mapset=mapset
    )
    gj.init(mapset_path)
    print("bla")
