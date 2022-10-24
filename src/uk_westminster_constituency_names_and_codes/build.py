import requests
import json
import pandas as pd
from pathlib import Path

top_level = Path(__file__).parent.parent.parent

data_dir = Path(top_level, "data")
interim_dir = Path(data_dir, "interim")
raw_dir = Path(data_dir, "raw")
package_dir = Path(data_dir, "packages", "uk_westminster_constituency_names_and_codes")

maps = {
    "Weston-super-Mare": "Weston-Super-Mare",
}


def get_mapped_name(name):
    if name in maps:
        name = maps[name]

    return name


def get_cons_from_mapit():
    response = requests.get("https://mapit.mysociety.org/areas/WMC.json")
    cons = response.json()

    with open(Path(raw_dir, "mapit.json"), "w") as mapit_file:
        mapit_file.write(json.dumps(cons, indent=2))


def process_cons_from_mapit():
    with open(Path(raw_dir, "mapit.json"), "r") as mapit_file:
        cons = json.load(mapit_file)

    out = []
    for id, data in cons.items():
        out.append(
            [
                get_mapped_name(data["name"]),
                data["country_name"],
                data["id"],
                data["codes"]["gss"],
            ]
        )

    df = pd.DataFrame(out)
    df.columns = ["name", "country", "mapit-id", "gss-code"]

    df.to_csv(Path(interim_dir, "mapit.csv"), index=False)


def get_cons_from_parliament():
    url = "https://members-api.parliament.uk/api/Location/Constituency/Search"

    cons = []

    skip = 0
    while skip is not None:
        params = {"take": 20, "skip": skip}
        response = requests.get(url, params=params)
        data = response.json()
        if data.get("items", None) is not None:
            cons.extend(data["items"])

        skip = skip + 20
        if data["skip"] + 20 > data["totalResults"]:
            skip = None

    with open(Path(raw_dir, "parl_cons_list.json"), "w") as parl_cons_file:
        parl_cons_file.write(json.dumps(cons, indent=2))


def process_cons_from_parliament():
    with open(Path(raw_dir, "parl_cons_list.json"), "r") as parl_cons_file:
        cons = json.load(parl_cons_file)

    out = []
    for data in cons:
        out.append([get_mapped_name(data["value"]["name"]), data["value"]["id"]])

    df = pd.DataFrame(out)
    df.columns = ["name", "parliament-id"]

    df.to_csv(Path(interim_dir, "parl.csv"), index=False)


def merge_cons():
    mapit = pd.read_csv(Path(interim_dir, "mapit.csv"))
    parl = pd.read_csv(Path(interim_dir, "parl.csv"))

    merged = mapit.merge(parl)
    merged.to_csv(Path(package_dir, "constituencies_and_codes.csv"), index=False)


def build_all():
    get_cons_from_parliament()
    get_cons_from_mapit()
    process_cons_from_parliament()
    process_cons_from_mapit()
    merge_cons()


def build_from_cache():
    process_cons_from_parliament()
    process_cons_from_mapit()
    merge_cons()


if __name__ == "__main__":
    build_all()
