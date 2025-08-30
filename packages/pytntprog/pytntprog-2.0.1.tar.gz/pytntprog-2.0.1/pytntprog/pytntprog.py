"""
pytntprog use case
"""

import argparse
import sys
import requests
import urllib.request
import xml.etree.ElementTree as ET
import os
import time
from pytntprog.args import compute_args
import datetime
import colorama
from termcolor import colored
from columnar import columnar
from pathlib import Path
import urllib.request
import lzma
import shutil
import os
import urllib.request
import lzma
import shutil
import os
import py7zr

def download_file(url, tmp_path):
    print(f"Downloading {url} ...")
    urllib.request.urlretrieve(url, tmp_path)
    if os.path.getsize(tmp_path) == 0:
        raise ValueError(f"Le fichier téléchargé est vide : {tmp_path}")
    print(f"Downloaded to {tmp_path}")
    return tmp_path

def extract_file(tmp_path, dest_path):
    # Lire les 6 premiers octets pour détecter le type
    with open(tmp_path, "rb") as f:
        magic = f.read(6)

    # XZ : FD 37 7A 58 5A 00
    if magic == b"\xfd7zXZ\x00":
        print("Detected XZ file, decompressing...")
        with lzma.open(tmp_path, "rb") as f_in, open(dest_path, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)
    else:
        # On essaie avec 7-Zip
        print("Detected 7-Zip file, extracting...")
        with py7zr.SevenZipFile(tmp_path, mode='r') as z:
            z.extractall(path=os.path.dirname(dest_path))
    print(f"File extracted to {dest_path}")
    os.remove(tmp_path)

def download_and_extract(url, dest_path):
    tmp_path = dest_path + ".tmp"
    download_file(url, tmp_path)
    extract_file(tmp_path, dest_path)
    
DOSSIER_CONFIG_PYTNTPROG = "pytntprog"

def find():
    alll = compute_args().all
    idd = compute_args().id
    ffilter = compute_args().filter
    ffilterfull = compute_args().Filter
    ccurrent = compute_args().current
    nocolor = compute_args().nocolor
    duree_max = compute_args().length
    full = compute_args().full
    colorama.init()


    xml_tnt = "xmltv_tnt.xml"
    xml_tnt_full = "xmltv_fr.xml"
    if (
        compute_args().cache
        or not os.path.exists(
            get_user_config_directory_pytntprog() + xml_tnt
        )
        or (
            time.time()
            - os.stat(
                get_user_config_directory_pytntprog() + xml_tnt
            ).st_mtime
            > 86400 * 1
        )
    ):

        # Répertoire de config utilisateur
        config_dir = get_user_config_directory_pytntprog()
        os.makedirs(config_dir, exist_ok=True)


        # Télécharger et décompresser
        download_and_extract("https://xmltvfr.fr/xmltv/xmltv_tnt.xz", os.path.join(config_dir, xml_tnt))
        download_and_extract("https://xmltvfr.fr/xmltv/xmltv_fr.xz", os.path.join(config_dir, xml_tnt_full))

        print("Download finished, XML files ready!")
    
    if not full:
        tree = ET.parse(get_user_config_directory_pytntprog() + xml_tnt)
    else:
        tree = ET.parse(get_user_config_directory_pytntprog() + xml_tnt_full)    
    root = tree.getroot()
    T = []
    i = 1
    for neighbor in root.iter("programme"):
        start = neighbor.get("start")
        stop = neighbor.get("stop")
        channel = neighbor.get("channel")
        for c in root.iter("channel"):
            if c.get("id") == channel:
                channel = c.find("display-name").text
                break
        title = neighbor.find("title").text
        subtitle = ""
        if neighbor.find("sub-title") != None:
            subtitle = neighbor.find("sub-title").text
        desc = ""
        if neighbor.find("desc") != None:
            desc = neighbor.find("desc").text
        category = ""
        if neighbor.find("category") != None:
            category = neighbor.find("category").text
        episode = ""
        if neighbor.find("episode-num") != None:
            episode = neighbor.find("episode-num").text
        age = ""
        if neighbor.find("rating") != None:
            age = neighbor.find("rating").find("value").text
        length = ""
        fmt = "%Y%m%d%H%M%S %z"
        dt_start = datetime.datetime.strptime(start, fmt)
        dt_stop = datetime.datetime.strptime(stop, fmt)
        length = int((dt_stop - dt_start).total_seconds() / 60)    
        T.append(
            {
                "time": start,
                "time_end": stop,
                "day": start[0:8],
                "start": start[8:10] + ":" + start[10:12],
                "end": stop[8:10] + ":" + stop[10:12],
                "channel": channel,
                "title": title,
                "id": str(i).zfill(5),
                "subtitle": subtitle,
                "description": desc,
                "category": category,
                "age": age,
                "episode": episode,
                "length": length
            }
        )

        i = i + 1
    T.sort(key=lambda x: x["time"])

    if idd:
        for w in T:
            if w["id"] == idd.zfill(5):
                print(
                    "titre       : "
                    + w["title"]
                    + " "
                    + w["subtitle"]
                )
                print("chaine      : " + w["channel"])
                print("jour        : " + w["day"])
                print("heure debut : " + w["start"])
                print("heure fin   : " + w["end"])
                print("durée min.  : " + str(w["length"]))
                print("resume      : " + w["description"])
                print("episode     : " + w["episode"])
                print("categorie   : " + w["category"])
                print("age         : " + w["age"])
                break
    else:
        if alll:
            headers = ["id", "jour", "heure", "chaine", "programmes"]
        else:
            headers = ["id", "heure", "chaine", "programmes"]
        data = []
        for w in T:

            if alll:
                resume = [
                    my_colored("[" + w["id"] + "] ", "red", nocolor),
                    w["day"],
                    my_colored(w["start"], "green", nocolor),
                    my_colored(w["channel"], "yellow", nocolor),
                    my_colored(
                        w["title"] + " " + w["subtitle"],
                        "cyan",
                        nocolor,
                    ),
                ]

            else:
                resume = [
                    my_colored("[" + w["id"] + "] ", "red", nocolor),
                    my_colored(w["start"], "green", nocolor),
                    my_colored(w["channel"], "yellow", nocolor),
                    my_colored(
                        w["title"] + " " + w["subtitle"],
                        "cyan",
                        nocolor,
                    ),
                ]

            trouve = False

            if not ffilter:
                trouve = True
            else:
                trouve = True
                for search in ffilter:
                    if search.lower() not in " ".join(resume).lower():
                        trouve = False

                        
            if trouve and ffilterfull:
                trouve = True
                for search in ffilterfull:
                    if (search.lower() not in " ".join(resume).lower() and search.lower() not in w["category"].lower()) and (search.lower() not in w["description"].lower()):
                        trouve = False

     

            if ccurrent:
                until = (
                    datetime.datetime(
                        int(w["time"][0:4]),
                        int(w["time"][4:6]),
                        int(w["time"][6:8]),
                        int(w["time"][8:10]),
                        int(w["time"][10:12]),
                        0,
                    ).timestamp()
                    - time.time()
                )
                since = (
                    datetime.datetime(
                        int(w["time_end"][0:4]),
                        int(w["time_end"][4:6]),
                        int(w["time_end"][6:8]),
                        int(w["time_end"][8:10]),
                        int(w["time_end"][10:12]),
                        0,
                    ).timestamp()
                    - time.time()
                )
                if (until > 3600) or (since < 0):
                    trouve = False
                if until > 3600:
                    break
            if alll:
                if trouve and w["length"]>duree_max:
                    data.append(resume)
            else:
                if (
                    w["day"]
                    == datetime.date.today().strftime("%Y%m%d")
                    and trouve and int(w["length"])>duree_max
                ): 
                    data.append(resume)
                if w["day"] > datetime.date.today().strftime(
                    "%Y%m%d"
                ):
                    break
        if data != []:        
            table = columnar(data, headers, no_borders=True, wrap_max=0)
            print(table)
        else:
            print(my_colored("attention : aucun résultat", "yellow", nocolor))  


def my_colored(message, color, nocolor):
    if nocolor:
        return message
    return colored(message, color)

def get_user_config_directory_pytntprog():
    nocolor = compute_args().nocolor
    if os.name == "nt":
        appdata = os.getenv("LOCALAPPDATA")
        if appdata:
            ze_path = os.path.join(
                appdata, DOSSIER_CONFIG_PYTNTPROG, ""
            )
            Path(ze_path).mkdir(parents=True, exist_ok=True)
            return ze_path
        appdata = os.getenv("APPDATA")
        if appdata:
            ze_path = os.path.join(
                appdata, DOSSIER_CONFIG_PYTNTPROG, ""
            )
            Path(ze_path).mkdir(parents=True, exist_ok=True)
            return ze_path
        print(
            my_colored(
                "erreur : impossible de créer le dossier de config",
                "red",nocolor
            )
        )
        sys.exit(1)
    xdg_config_home = os.getenv("XDG_CONFIG_HOME")
    if xdg_config_home:
        ze_path = os.path.join(xdg_config_home, "")
        Path(ze_path).mkdir(parents=True, exist_ok=True)
        return ze_path
    ze_path = os.path.join(
        os.path.expanduser("~"),
        ".config",
        DOSSIER_CONFIG_PYTNTPROG,
        "",
    )
    Path(ze_path).mkdir(parents=True, exist_ok=True)
    return ze_path    
