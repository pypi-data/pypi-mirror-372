import requests
from typing import Dict, List, Optional, Literal, Tuple
import xmltodict
from .exceptions import *
import json

class TezaursAPI:
    """
    Tezaura API ietvars. 
    Nodrošina metodes latviešu valodas vārdu un frāžu analīzei, locīšanai un morfoloģiskai marķēšanai.
    """
    def __init__(self):
       self.url = 'http://api.tezaurs.lv:8182'
       self.version = 'v1'

    def analyze(self, word: str, lang: Optional[Literal['en']] = None) -> List[Dict]:
        """
        Analizē vārdu, izmantojot Tezaura API.

        Izsauc `/analyze` servisu un atgriež morfoloģisko informāciju par vārdu.

        Argumenti:
            word (str): Vārds, ko analizēt.
            lang (Optional[Literal['en']]): Atbildes valoda 'lv' (pēc noklusējuma) vai 'en'.

        Atgrieztais:
            List[Dict]: Morfoloģiskās analīzes rezultāti JSON formātā.
        """
        if not isinstance(word, str):
            raise TezaursTypeError(f"Parametram 'word' jābūt str, bet saņēma {type(word).__name__}")
        
        if lang is not None:
            url = f'{self.url}/analyze/{lang}/{word}'
        else: 
            url = f'{self.url}/analyze/{word}'

        try:
            response = requests.get(url)    
            data = response.json()
            if data == []:
                return f'Vārds "{word}" neeksistē'
            return data
        
        except json.JSONDecodeError:
            raise TezaursJSONError("Kļūda: serveris neatgrieza derīgu JSON!")
        except requests.exceptions.RequestException as e:
            raise TezaursNetworkError(f"Tīkla kļūda: {e}")

    
    def analyze_sentence(self, sentence: str) -> List[Dict]:
        """
        Analizē teikumu, izmantojot Tezaura API.

        Izsauc `/analyze_sentence` servisu un atgriež informāciju par katru vārdu teikumā.

        Argumenti:
            sentence (str): Teikums, ko analizēt.
        Atgrieztais:
            List[Dict]: Analīzes rezultāti JSON formātā.
        """
        sentence = sentence.replace(' ', '%20')
        url = f'{self.url}/analyzesentence/{sentence}'

        try:
            response = requests.get(url)
            data = response.json()
            if data == []:
                return f'"{sentence}" nav derīgs teikums'
            return data
        
        except json.JSONDecodeError:
            raise TezaursJSONError("Kļūda: serveris neatgrieza derīgu JSON!")
        except requests.exceptions.RequestException as e:
            raise TezaursNetworkError(f"Tīkla kļūda: {e}")

    def inflect(self, word: str, format: Optional[Literal['xml']] = 'json', lang: Optional[Literal['en']] = None) -> List[Dict]:
        """
            Izloka vārdu, izmantojot Tezaura API.

            Izsauc `/inflect` servisu un atgriež dotā vārda formas izvēlētajā formātā.

            Argumenti:
                word (str): Vārds, kuru nepieciešams locīt.
                format (Optional[Literal['xml']]): Atbildes formāts ('json' pēc noklusējuma vai 'xml').
                lang (Optional[Literal['en']]): Atbildes valoda 'lv' (pēc noklusējuma) vai 'en'.

            Atgrieztais:
                List[Dict]: Locījumu formas JSON formātā vai XML (ja izvēlēts).

            Kļūdas:
                TezaursJSONError: Ja serveris neatgriež derīgu JSON.
                TezaursNetworkError: Ja notiek tīkla kļūda.
        """
        if lang is not None:
            url = f'{self.url}/inflect/{format}/{lang}/{word}'
        else:
            url = f'{self.url}/inflect/{format}/{word}'

        try:
            response = requests.get(url)
            if format == 'xml':
                result = xmltodict.parse(response.text)  
            else:
                return response.json()
            return result
        
        except json.JSONDecodeError:
            raise TezaursJSONError("Kļūda: serveris neatgrieza derīgu JSON!")
        except requests.exceptions.RequestException as e:
            raise TezaursNetworkError(f"Tīkla kļūda: {e}")

        
    def inflect_phrase(self, phrase: str, category: Optional[Literal['person', 'org', 'loc']] = None) -> List[Dict]:
        """
        Izloka frāzi (piem., īpašvārdus), izmantojot Tezaura API.

        Izsauc `/inflect_phrase` servisu un atgriež frāzes locījumus.

        Argumenti:
            phrase (str): Frāze, kuru nepieciešams locīt.
            category (Optional[Literal['person', 'org', 'loc']]): Kategorija
                - 'person' cilvēku vārdiem,
                - 'org' organizācijām,
                - 'loc' vietvārdiem.

        Atgrieztais:
            List[Dict]: Locījumu formas JSON formātā.
        """
        phrase.strip("%20") 
        url = f'{self.url}/inflect_phrase/{phrase}'
        if category is not None:
            url += f"?category={category}"
        response = requests.get(url)
        return response.json()
    
    def inflect_people(self, name: str, format: Optional[Literal['xml']] = 'json', gender: Optional[Literal['m', 'f']] = None) -> List[Dict]:
        """
        Izloka personvārdus (cilvēku vārdus un uzvārdus).

        Izsauc `/inflect_people` servisu un atgriež dotā vārda locījumus.

        Argumenti:
            name (str): Vārds, uzvārds, vārds un uzvārds, kuru nepieciešams locīt.
            format (Optional[Literal['xml']]): Atbildes formāts ('json' pēc noklusējuma vai 'xml').
            gender (Optional[Literal['m','f']]): Dzimums ('m' – vīriešu, 'f' – sieviešu).

        Atgrieztais:
            List[Dict]: Locījumu formas JSON vai XML formātā.

        Kļūdas:
            TezaursJSONError: Ja serveris neatgriež derīgu JSON.
            TezaursNetworkError: Ja notiek tīkla kļūda.
        """
        url =  f'{self.url}/inflect_people/{format}/{name}'
        if gender is not None:
            url += f'?gender={gender}'

        try:
            response = requests.get(url)
            if(format == 'xml'):
                result = xmltodict.parse(response.text)  
            else:
                return response.json()
            return result

        except json.JSONDecodeError:
            raise TezaursJSONError("Kļūda: serveris neatgrieza derīgu JSON!")
        except requests.exceptions.RequestException as e:
            raise TezaursNetworkError(f"Tīkla kļūda: {e}")


    def inflections(self, word: str, paradigm: Optional[Literal['noun-4f', 'verb-1']] = None, stems: Tuple[str, str, str] = None) -> List[Dict]:
        """
        Atrod vārda visas iespējamās formas.

        Izsauc `/inflections` servisu, kas atgriež visus locījumus un konjugācijas.

        Argumenti:
            word (str): Vārds, kuru analizēt.
            paradigm (Optional[Literal['noun-4f', 'verb-1']]): Paradigmas tips (ja zināms).
            stems (Tuple[str, str, str]): Trīs saknes formas, ja nepieciešamas.

        Atgrieztais:
            List[Dict]: Vārda locījumu formas JSON formātā.

        Kļūdas:
            TezaursJSONError: Ja serveris neatgriež derīgu JSON.
            TezaursNetworkError: Ja notiek tīkla kļūda.
        """
        url = f'{self.url}/{self.version}/inflections/{word}'
        if paradigm is not None:
            url += f'?paradigm={paradigm}'
            if stems is not None:
                url += f'&stem1={stems[0]}&stem2={stems[1]}&stem3={stems[2]}'

        try:
            response = requests.get(url)
            return response.json()

        except json.JSONDecodeError:
            raise TezaursJSONError("Kļūda: serveris neatgrieza derīgu JSON!")
        except requests.exceptions.RequestException as e:
            raise TezaursNetworkError(f"Tīkla kļūda: {e}")

    def normalize(self, phrase: str, category: Optional[Literal['person', 'org', 'loc']] = None) -> List[Dict]:
        """
        Normalizē frāzi (piemēram, īpašvārdus).

        Izsauc `/normalize_phrase` servisu un atgriež frāzes normalizēto formu.

        Argumenti:
            phrase (str): Frāze, kuru normalizēt.
            category (Optional[Literal['person', 'org', 'loc']]): Kategorija
                - 'person' cilvēku vārdiem,
                - 'org' organizācijām,
                - 'loc' vietvārdiem.

        Atgrieztais:
            str: Normalizēta frāze (teksts).
        """
        phrase.strip("%20")
        url = f'{self.url}/normalize_phrase/{phrase}'
        if category is not None:
            url += f"?category={category}"
    
        try:
            response = requests.get(url)
            return response.text
    
        except json.JSONDecodeError:
            raise TezaursJSONError("Kļūda: serveris neatgrieza derīgu JSON!")
        except requests.exceptions.RequestException as e:
            raise TezaursNetworkError(f"Tīkla kļūda: {e}")

    def suitable_paradigm(self, word: str) -> List[Dict]:
        """
        Nosaka atbilstošās paradigmas vārdam.

        Izsauc `/suitable_paradigm` servisu un atgriež iespējamos paradigmu tipus.

        Argumenti:
            word (str): Vārds, kam noteikt paradigmu.

        Atgrieztais:
            List[Dict]: Saraksts ar iespējamiem paradigmu ID un aprakstiem.
        """
        url = f'{self.url}/suitable_paradigm/{word}'
        
        try:
            response = requests.get(url)
            return response.json()
        
        except json.JSONDecodeError:
            raise TezaursJSONError("Kļūda: serveris neatgrieza derīgu JSON!")
        except requests.exceptions.RequestException as e:
            raise TezaursNetworkError(f"Tīkla kļūda: {e}")

    def morphotagger(self, phrase: str) -> List[Dict]:
        """
        Veic morfoloģisko frāzes marķēšanu.

        Izsauc `/morphotagger` servisu un atgriež katra vārda morfoloģisko marķējumu.

        Argumenti:
            phrase (str): Frāze vai teikums, ko analizēt.

        Atgrieztais:
            List[Dict]: Marķēšanas rezultāti JSON formātā.
        """
        url = f'{self.url}/morphotagger/{phrase}'

        try:
            response = requests.get(url)
            return response.json()

        except json.JSONDecodeError:
            raise TezaursJSONError("Kļūda: serveris neatgrieza derīgu JSON!")
        except requests.exceptions.RequestException as e:
            raise TezaursNetworkError(f"Tīkla kļūda: {e}")

    def __str__(self):
        return f'[{self.url}] version {self.version}'
