import pytest

from url_discovery import _run_url_discovery
import url_discovery

def test_url_discovery_file():
    urlOut = _run_url_discovery('file:///Users/joeyd/Documents/JoeyDCareer/GitHub/MasteringSpacy/Spacy_Tutorials/ner_food_ingredients/assets/test/bs4_tester.html', 'file:')
    print(urlOut)
    return urlOut


# def test_url_discovery():
#     # THIS TEST IS NOT DETERMINISTIC - PLEASE REMOVE URL
#     urlOut = _run_url_discovery('https://www.printatestpage.com/', 'printatestpage')
#     print(urlOut)
#     return urlOut

def test_url_discovery_grocery_explode_one():
    # THIS TEST IS NOT DETERMINISTIC - PLEASE REMOVE URL
    urlDiscovery = _run_url_discovery('https://groceries.asda.com', 'asda.com', explodeTimes = 1, saveOut=None)
    # print(urlDiscovery)
    return urlDiscovery

def test_url_discovery_grocery_explode_twice():
    # THIS TEST IS NOT DETERMINISTIC - PLEASE REMOVE URL
    urlDiscovery = _run_url_discovery('https://groceries.asda.com', 'asda.com', explodeTimes = 2, saveOut=None)
    # print(urlDiscovery)
    return urlDiscovery