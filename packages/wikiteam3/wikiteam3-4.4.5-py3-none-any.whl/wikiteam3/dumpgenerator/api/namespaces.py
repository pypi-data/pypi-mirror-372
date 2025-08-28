import re

import requests

from wikiteam3.dumpgenerator.cli import Delay
from wikiteam3.dumpgenerator.api import get_JSON
from wikiteam3.dumpgenerator.config import Config
from wikiteam3.utils.util import ALL_NAMESPACE_FLAG

def getNamespacesScraper(config: Config, session: requests.Session):
    """Hackishly gets the list of namespaces names and ids from the dropdown in the HTML of Special:AllPages"""
    """Function called if no API is available"""
    namespaces = config.namespaces
    namespacenames = {0: ""}  # main is 0, no prefix
    if namespaces:
        r = session.post(
            url=config.index, params={"title": "Special:Allpages"}, timeout=30
        )
        raw = r.text
        Delay(config=config)

        # [^>]*? to include selected="selected"
        m = re.compile(
            r'<option [^>]*?value=[\'"](?P<namespaceid>\d+)[\'"][^>]*?>(?P<namespacename>[^<]+)</option>'
        ).finditer(raw)
        if ALL_NAMESPACE_FLAG in namespaces:
            namespaces = []
            for i in m:
                namespaces.append(int(i.group("namespaceid")))
                namespacenames[int(i.group("namespaceid"))] = i.group("namespacename")
        else:
            # check if those namespaces really exist in this wiki
            namespaces2 = []
            for i in m:
                if int(i.group("namespaceid")) in namespaces:
                    namespaces2.append(int(i.group("namespaceid")))
                    namespacenames[int(i.group("namespaceid"))] = i.group(
                        "namespacename"
                    )
            namespaces = namespaces2
    else:
        namespaces = [0]

    namespaces = list(set(namespaces))  # uniques
    print("%d namespaces found" % (len(namespaces)))
    return namespaces, namespacenames


def getNamespacesAPI(config: Config, session: requests.Session):
    """Uses the API to get the list of namespaces names and ids"""
    namespaces = config.namespaces
    namespace_names = {0: ""}  # main is 0, no prefix
    if namespaces:
        r = session.get(
            url=config.api,
            params={
                "action": "query",
                "meta": "siteinfo",
                "siprop": "namespaces",
                "format": "json",
            },
            timeout=30,
        )
        result = get_JSON(r)
        Delay(config=config)
        try:
            nsquery = result["query"]["namespaces"]
        except KeyError:
            print("Error: could not get namespaces from the API request.")
            print("HTTP %d" % r.status_code)
            print(r.text)
            raise

        if ALL_NAMESPACE_FLAG in namespaces:
            namespaces = []
            for i in nsquery.keys():
                if int(i) < 0:  # -1: Special, -2: Media, excluding
                    continue
                namespaces.append(int(i))
                namespace_names[int(i)] = nsquery[i]["*"]
        else:
            # check if those namespaces really exist in this wiki
            namespaces2 = []
            for i in nsquery.keys():
                bi = i
                i = int(i)
                if i < 0:  # -1: Special, -2: Media, excluding
                    continue
                if i in namespaces:
                    namespaces2.append(i)
                    namespace_names[i] = nsquery[bi]["*"]
            namespaces = namespaces2
    else:
        namespaces = [0]

    namespaces = list(set(namespaces))  # uniques
    print("%d namespaces found" % (len(namespaces)))
    return namespaces, namespace_names
