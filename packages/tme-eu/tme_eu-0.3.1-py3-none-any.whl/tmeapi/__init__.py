from tmeapi.models import GetProducts, Autocomplete, GetCategories, GetSymbols, Cursorable
from typing import TypeVar
from math import ceil
from typing import Callable
from collections import OrderedDict
from urllib.parse import urlencode, quote
import base64
import hmac
import hashlib
from typing import Any
from pydantic import TypeAdapter

import httpx

from .models import Ok, GetPricesData, ErrorSignature, ErrorValidation, GetPricesAndStocksData


def sign_body(action: str, params: dict[str, Any], token: str, app_secret: str):
    api_url = "https://api.tme.eu/" + action + ".json"

    params["Token"] = token

    # NOTE: the params need to be alphanumerically and then lexically sorted
    #  this makes our life absolute pain since indexes >10 do not have equivalent sortings in both cases
    #  so for arrays we need to seperately lexically sort them
    #
    # UPDATE: TME suggests padding the indexes, i.e. `01`, `02` ..., `10`, ... `99`,
    #   such that lexical & alphanumeric sortings are equivalent
    param_list: list[tuple[str, str | list[str]]] = list(sorted(params.items()))

    # Flatten lists into urlencoding format
    for pi in range(len(param_list)):
        if isinstance(param_list[pi][1], list):
            contents = param_list.pop(pi)
            key = contents[0]
            for i, v in enumerate(contents[1]):
                param_list.insert(pi + i, (f"{key}[{i}]", v))

    encoded_params = urlencode(param_list, False)
    signature_base = "POST" + "&" + quote(api_url, "") + "&" + quote(encoded_params, "")

    api_signature = base64.encodebytes(
        hmac.new(app_secret.encode(), signature_base.encode(), hashlib.sha1).digest()
    ).rstrip()

    param_list.append(("ApiSignature", api_signature))

    return api_url, urlencode(param_list)


class TmeApi:
    def __init__(self, token: str, app_secret: str):
        self.token = token
        self.app_secret = app_secret

    def _sync_call(self, api_url: str, body: str):
        return httpx.post(api_url, content=body, headers={"Content-type": "application/x-www-form-urlencoded"})

    def _cursor(
        fn: Callable[..., ErrorSignature | ErrorValidation | Ok[Cursorable]], batch_data: list, limit: int = 50
    ):
        collated: Cursorable | None = None
        for i in range(ceil(len(batch_data) / limit)):
            resp = fn(batch_data[limit * i : limit * (i + 1)])
            match resp:
                case Ok(Data=data):
                    if collated is None:
                        collated = data
                    else:
                        collated.extend(data)
                case _:
                    return resp

        return Ok(Data=collated)

    def get_prices(
        self, symbol_list: list[str], gross_prices=False, currency="EUR", lang="en", country="NL"
    ) -> Ok[GetPricesData] | ErrorSignature | ErrorValidation:
        def _get_prices(symbol_list: list[str]):
            api_url, body = sign_body(
                "Products/GetPrices",
                {
                    "SymbolList": symbol_list,
                    "GrossPrices": gross_prices,
                    "Currency": currency,
                    "Country": country,
                    "Language": lang,
                },
                self.token,
                self.app_secret,
            )

            adapter = TypeAdapter(Ok[GetPricesData] | ErrorSignature | ErrorValidation)
            return adapter.validate_python(self._sync_call(api_url, body).json())

        return TmeApi._cursor(_get_prices, symbol_list)

    def get_prices_and_stock(
        self, symbol_list: list[str], gross_prices=False, currency="EUR", lang="en", country="NL"
    ) -> Ok[GetPricesAndStocksData] | ErrorSignature | ErrorValidation:
        def _get_prices_and_stock(symbol_list: list[str]):
            api_url, body = sign_body(
                "Products/GetPricesAndStocks",
                {
                    "SymbolList": symbol_list,
                    "GrossPrices": gross_prices,
                    "Currency": currency,
                    "Country": country,
                    "Language": lang,
                },
                self.token,
                self.app_secret,
            )

            adapter = TypeAdapter(Ok[GetPricesAndStocksData] | ErrorSignature | ErrorValidation)
            return adapter.validate_python(self._sync_call(api_url, body).json())

        return TmeApi._cursor(_get_prices_and_stock, symbol_list)

    def get_products(
        self, symbol_list: list[str], lang="en", country="NL"
    ) -> Ok[GetProducts] | ErrorSignature | ErrorValidation:
        def _get_prices_and_stock(symbol_list: list[str]):
            api_url, body = sign_body(
                "Products/GetProducts",
                {
                    "SymbolList": symbol_list,
                    "Country": country,
                    "Language": lang,
                },
                self.token,
                self.app_secret,
            )

            adapter = TypeAdapter(Ok[GetProducts] | ErrorSignature | ErrorValidation)
            return adapter.validate_python(self._sync_call(api_url, body).json())

        return TmeApi._cursor(_get_prices_and_stock, symbol_list)

    def get_symbols(
        self, category_id: int, lang="en", country="NL"
    ) -> Ok[GetSymbols] | ErrorSignature | ErrorValidation:
        api_url, body = sign_body(
            "Products/GetSymbols",
            {"CategoryId": category_id, "Country": country, "Language": lang},
            self.token,
            self.app_secret,
        )

        adapter = TypeAdapter(Ok[GetSymbols] | ErrorSignature | ErrorValidation)
        return adapter.validate_python(self._sync_call(api_url, body).json())

    def get_categories(
        self, tree=True, category_id: int | None = None, lang="en", country="NL"
    ) -> Ok[GetCategories] | ErrorSignature | ErrorValidation:
        api_url, body = sign_body(
            "Products/GetCategories",
            {"CategoryId": category_id, "Tree": tree, "Country": country, "Language": lang},
            self.token,
            self.app_secret,
        )

        adapter = TypeAdapter(Ok[GetCategories] | ErrorSignature | ErrorValidation)
        return adapter.validate_python(self._sync_call(api_url, body).json())

    def autocomplete(self, phrase: str, lang="en", country="NL") -> Ok[Autocomplete] | ErrorSignature | ErrorValidation:
        api_url, body = sign_body(
            "Products/Autocomplete",
            {"Phrase": phrase, "Country": country, "Language": lang},
            self.token,
            self.app_secret,
        )

        adapter = TypeAdapter(Ok[Autocomplete] | ErrorSignature | ErrorValidation)
        return adapter.validate_python(self._sync_call(api_url, body).json())
