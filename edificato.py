# coding=UTF-8

'''
ogr2osm translation rules for DBSN building data

Author: Andrea Musuruane <musuruan@gmail.com>

Adapted by Marcello Arcangeli <arcanma@gmail.com> for building data of the Umbria region after data analysis

DBSN data distributed under the Open Data Commons Open Database License (ODbL) ver. 1.0

Data download available at:
https://www.igmi.org/it/dbsn-database-di-sintesi-nazionale

More info at:
https://wiki.openstreetmap.org/wiki/Italy/DBSN

This script requires ogr2osm v1.0.0 or later:
https://github.com/roelderickx/ogr2osm

Open the GDB package with QGIS, buildings data are in layers named "edifc", one per province, after filtered out geometries with attribute meta_ist=03 (OSM source) merge layers then merge geometries that were split on different layers, check for geometries very near to region limit (need to be checked before the use in OSM for possible incomplete shape).
Add municipality code and name to geometries using the function "Join attributes by location" then save the buildings inside a municipality in GeoPackage files using the split vector layer function, using the municipality name field as UniqueID Field to have individual files named according to the municipality.

The following fields are dropped from the source shapefile:

Field          Original Definition        Reason
fid            Chiave primaria            Primary key
OBJECTID       Object ID                  Internal use
classid        Classid                    Internal use
edifc_at       Altezza edificio           Not populated (for DBSN Umbria)
scril          Scale Level                Not useful
meta_ist       Fonte del dato             Not useful
shape_Leng     Perimetro                  Not useful
shape_Area     Area                       Not useful
comune_ist     Codice comune              Not useful
comune_nom     Nome comune                Not useful
edifc_mon      Edificio monumentale       Possible monument (only 1 in Umbria)

The following fields are used:

Field          Original Definition               Reason
edifc_stat     Stato costruzione dell'edificio   Main indicator for object existence
edifc_uso      Destinazione uso edificio         Use destination
edifc_ty       Tipologia edilizia                Building type
edifc_sot      Edificio sotterraneo              Underground building
edifc_nome     Nome edificio                     Building name
check_geom     Da controllare x bordo reg        The shape could be incomplete if it extend out of Umbria

the command to be used is:

ogr2osm --suppress-empty-tags -t edificato.py -f edificato_*.gpkg (replace the * with the municipality name)

'''

import ogr2osm

class EdifTranslation(ogr2osm.TranslationBase):

    def filter_tags(self, attrs):
        if not attrs:
            return

        tags = {}

        if str.lower(attrs["edifc_nome"]) != "unk":
            tags["name"] = attrs["edifc_nome"]
        else:
            tags["name"] = ""

        if attrs["edifc_sot"] == "02":
            tags["location"] = "underground"
            tags["building:levels"] = "0"
            tags["fixme:buildind"] = "Check location, if not verifiable remove geometry" 

        match attrs["edifc_ty"]:
            case "04":
                tags["building"] = "house"
            case "07":
                tags["building"] = "tower"
                tags["man_made"] = "tower"
                tags["tower:type"] = "bell_tower"
            case "10":
                tags["building"] = "castle"
            case "11":
                tags["building"] = "church"
            case "14":
                tags["building"] = "hangar"
            case "16":
                tags["building"] = "temple"
            case "19":
                tags["building"] = "sports_hall"
            case "21":
                tags["building"] = "stadium"
            case "22":
                tags["building"] = "cathedral"
            case "23":
                tags["building"] = "roof"
                tags["layer"] = "1"
            case "24":
                tags["building"] = "yes"
                tags["defensive_works"] = "bastion"
            case "25":
                tags["building"] = "yes"
                tags["historic"] = "citywalls"
            case _:
                tags["building"] = "yes"

        match attrs["edifc_uso"]:
            case "02":
                tags["building"] = "office"
            case "0201":
                tags["amenity"] = "townhall"
            case "0203":
                tags["office"] = "government"
                tags["admin_level"] = "4"
            case "030101":
                tags["amenity"] = "social_facility"
            case "030102":
                tags["amenity"] = "hospital"
                tags["healthcare"] = "hospital"
            case "030103":
                tags["amenity"] = "clinic"
                tags["healthcare"] = "clinic"
            case "030104":
                tags["amenity"] = "hospital"
                tags["healthcare"] = "hospital"
                tags["fixme:classify"] = "if it doesn't allows hospitalization it should be tagged as amenity=clinic"
            case "030301":
                tags["amenity"] = "school"
            case "030302":
                tags["amenity"] = "university"
            case "0304":
                tags["amenity"] = "post_office"
            case "0306":
                tags["amenity"] = "police"
            case "0307":
                tags["amenity"] = "fire_station"
            case "05":
                tags["amenity"] = "place_of_worship"
            case "060101":
                tags["aeroway"] = "aerodrome"
            case "060102":
                tags["aeroway"] = "heliport"
            case "060201":
                tags["amenity"] = "bus_station"
                tags["public_transport"] = "station"
            case "060202":
                tags["amenity"] = "parking"
                tags["parking"] = "multi-storey"
            case "060301":
                tags["railway"] = "station"
            case "060404":
                tags["aerialway"] = "station"
            case "0701":
                tags["amenity"] = "bank"
            case "0702":
                tags["shop"] = "department_store"
            case "0703" | "0704":
                tags["shop"] = "supermarket"
            case "0801":
                tags["building"] = "industrial"
            case "0802" | "080201" | "080202" | "080203" | "080206":
                tags["building"] = "service"
                tags["utility"] = "power"
            case "0804":
                tags["man_made"] = "wastewater_plant"
            case "0806":
                tags["building"] = "service"
                tags["utility"] = "telecom"
            case "0901":
                tags["building"] = "house"
            case "0902" | "0903" | "0904":
                tags["building"] = "farm_auxiliary"
            case "1001":
                tags["building"] = "public"
            case "100101":
                tags["amenity"] = "library"
            case "100102":
                tags["amenity"] = "cinema"
            case "100103":
                tags["amenity"] = "theatre"
            case "100104":
                tags["tourism"] = "museum"
            case "1002":
                tags["building"] = "sports_centre"
            case "100201":
                tags["leisure"] = "swimming_pool"
                tags["indoor"] = "yes"
            case "100202":
                tags["leisure"] = "sports_hall"
            case "11":
                tags["amenity"] = "prison"
            case "1201" | "1202":
                tags["building"] = "hotel"
            case "1203":
                tags["tourism"] = "camp_site"
            case "1204":
                tags["tourism"] = "alpine_hut"

        match attrs["check_geom"]:
            case "01":
                tags["fixme:geometry"] = "check if the building is cut on regional border"

        match attrs["edifc_stat"]:
            case "01":
                if tags["building"] != "yes":
                    tags["construction"] = tags["building"]
                tags["building"] = "construction"
                tags["fixme:building"] = "resurvey construction type and status"
            case "02":
                tags["ruins"] = "yes"
                tags["fixme:building"] = "resurvey status"

#            case "91":
#                tags["fixme:building"] = "resurvey status (unknown)"
# ******
# 1/4 of the geometries have this status, doing a sample test out of 30 of them only one is not a real building,
# so this check is skipped for all of them
#******

        return tags
