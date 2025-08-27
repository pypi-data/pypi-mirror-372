# Tezaurs API Wrapper

Tezaurs API Wrapper ir Python bibliotēka, kas ļauj ērti piekļūt [Tezaurs.lv](https://tezaurs.lv/) latviešu valodas vārdnīcas datubāzei caur API. Šī bibliotēka atvieglo vārdu locījumu, datu, un informācijas meklēšanu.

## Iespējas

- Atgriezt morfoloģisko vārda analīzi json formātā.
- Atgriezt informaciju par katru teikuma vārdu json formātā.
- Atgriezt katru vārda locījumu izvēlētajā formātā (json vai xml).
- Atgriezt frāzi katrā locījumā json formātā.
- Atrgiezt cilvēka vārdu un/vai uzvārdu katrā locījumā izvēlētajā formātā (json vai xml).
- Atgriezt vārda visas formas, locījumus un konjugācijas json formātā.
- Atgriezt frāzes normalizēto formu kā string.
- Atgriezt vārda iespējamos paradigmu tipus json formātā.
- Atgriezt katra vārda morfoloģisko marķējumu kā string.
- Vienkārša piekļuve vārdnīcas ierakstiem
- API pieprasījumu un atbilžu apstrāde ar kļūdu apstrādi
- Paplašināma dažādiem pielietojumiem

## Uzstādīšana

Klonējiet šo repozitoriju un instalējiet dependencies:

```bash
git clone https://github.com/nrenars/tezaurs-api-wrapper.git
cd tezaurs-api-wrapper
pip install -r requirements.txt
```

## Lietošana

Piemērs, kā izmantot API wrapperi:

Vārda morfoloģiskās analīzes atgriešana json formātā ar analyze() funkciju:
```python
from tezaurs_api_wrapper import TezaursAPI

tezaurs = TezaursAPI()

rezultats = tezaurs.analyze('vārds')
print(rezultats)
```
Katra teikuma vārda informācijas atgriešana json formātā ar analyze_sentence() funkciju:
```python
from tezaurs_api_wrapper import TezaursAPI

tezaurs = TezaursAPI()

rezultats = tezaurs.analyze_sentence('Vīrs ar cirvi.')
print(rezultats)
```

### API Metodes

- `analyze(word: str) -> dict`  
- `analyze_sentence(word_id: str) -> dict`  
- `inflect(word: str, target_lang: str) -> dict`  
- `inflect_phrase(word: str, target_lang: str) -> dict`
- `inflections(word: str, target_lang: str) -> dict`
- `normalize(word: str, target_lang: str) -> dict`
- `suitable_paradigm(word: str, target_lang: str) -> dict`
- `morphotagger()`

## Licence

Projekts ir licencēts saskaņā ar MIT licenci. Skatiet [LICENSE](LICENSE) failu.

## Resursi

- [Tezaurs.lv](https://tezaurs.lv/)

---

_Šis projekts nav saistīts ar Tezaurs.lv._




