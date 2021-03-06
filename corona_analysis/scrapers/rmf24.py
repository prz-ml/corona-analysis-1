"""
This module gathers data from RMF24 chart
"""

import re
from urllib import request

import pandas as pd
from bs4 import BeautifulSoup

from corona_analysis.utils.affixes import remove_prefix
from corona_analysis.utils.affixes import remove_suffix

URL = "https://www.rmf.fm/inc/outer/korona-wykres/wykres.html"


def scrape(data_url: str = URL) -> dict:
    """
    Scrapes data from rmf's chart

    ...

    Attributes
    ----------
    data_url : str
        url of the website with data
    """
    # Load web page
    page = request.urlopen(data_url)

    # Create parser
    soup = BeautifulSoup(page.read(), "html.parser")
    # Data is stored in the last script
    data = str(soup.body.find("script"))

    # find lists of data
    (sick, deaths, recovers) = re.findall(r"\[\[.*\]\]", data)

    sick = sick.split("],[")
    deaths = deaths.split("],[")
    recovers = recovers.split("],[")

    sick = [
        remove_suffix(remove_prefix(remove_prefix(i, "[["), "Date.UTC"), "]]")
        for i in sick
    ]
    deaths = [
        remove_suffix(remove_prefix(remove_prefix(i, "[["), "Date.UTC"), "]]")
        for i in deaths
    ]
    recovers = [
        remove_suffix(remove_prefix(remove_prefix(i, "[["), "Date.UTC"), "]]")
        for i in recovers
    ]

    sick = [i.split("),") for i in sick]
    deaths = [i.split("),") for i in deaths]
    recovers = [i.split("),") for i in recovers]

    sick = [["-".join(i[0][1:].split(",")), i[1]] for i in sick]
    deaths = [["-".join(i[0][1:].split(",")), i[1]] for i in deaths]
    recovers = [["-".join(i[0][1:].split(",")), i[1]] for i in recovers]

    return {"sick": sick, "deaths": deaths, "recovers": recovers}


def get_data(sick: list, deaths: list, recovers: list) -> dict:
    """
    Returns dataframe of deaths, recovered and sick people

    ...

    Attributes
    ----------
    sick : list
        list of lists with date and amount of sick people
    deaths : list
        list of lists with date and amount of dead people
    recovers : list
        list of lists with date and amount of recovered people
    """

    sick = pd.DataFrame(sick)
    sick.columns = ("date", "sick")

    deaths = pd.DataFrame(deaths)
    deaths.columns = ("date", "deaths")

    recovers = pd.DataFrame(recovers)
    recovers.columns = ("date", "recovers")

    tmp = pd.merge(sick, deaths, how="outer", on="date")
    tmp = pd.merge(tmp, recovers, how="outer", on="date")

    return {"rmf24": tmp}
