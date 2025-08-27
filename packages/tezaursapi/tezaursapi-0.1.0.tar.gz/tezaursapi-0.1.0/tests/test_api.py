import pytest

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from tezaursapi import Tezaurs

def test_analyze():
    test = Tezaurs()
    result = test.analyze('vārds')
    assert isinstance(result, list) 
    assert all(isinstance(item, dict) for item in result) 

def test_analyze_sentence():
    test = Tezaurs()
    result = test.analyze_sentence('vārds')
    assert isinstance(result, list) 
    assert all(isinstance(item, dict) for item in result)  

def test_inflect():
    test = Tezaurs()
    result = test.inflect('vārds')
    assert isinstance(result, list) 
    assert all(isinstance(item, list) for item in result)  

def test_inflect_phrase():
    test = Tezaurs()
    result = test.inflect_phrase('Latvijas Universitātes Matemātikas un Informātikas Institūtam')
    assert isinstance(result, dict) 

def test_inflect_people():
    test = Tezaurs()
    result = test.inflect_people('Jānis Krūmiņš')
    assert isinstance(result, list) 
    assert all(isinstance(item, list) for item in result)  

def test_inflections():
    test = Tezaurs()
    result = test.inflections('vārds')
    assert isinstance(result, list) 
    assert all(isinstance(item, list) for item in result)  

def test_normalize():
    test = Tezaurs()
    result = test.normalize('vārds')
    assert isinstance(result, str) 

def test_suitable_paradigm():
    test = Tezaurs()
    result = test.suitable_paradigm('vārds')
    assert isinstance(result, list) 
    assert all(isinstance(item, dict) for item in result)

def test_morphotagger():
    test = Tezaurs()
    result = test.morphotagger('vīrs ar cirvi.')
    assert isinstance(result, str) 