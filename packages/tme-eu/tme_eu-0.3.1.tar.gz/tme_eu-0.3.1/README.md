# TME.eu API Client

```py
from tmeapi import TmeApi, Ok, ErrorValidation, ErrorSignature
import os

api = TmeApi(os.environ["TME_KEY"].strip(), os.environ["TME_APP_SECRET"].strip())

print(api.autocomplete("555"))
print(api.get_prices(["EL-MAKR04120PA-TC"]))
print(api.get_prices_and_stock(["EL-MAKR04120PA-TC"]))

resp = api.get_categories(tree=True, category_id=112140)
match resp:
    case Ok(Data=categories):
        products = api.get_symbols(categories.CategoryTree.Id).unwrap()
        product_details = api.get_products([products.SymbolList[0]]).unwrap()
        print(product_details.ProductList[0])

    case ErrorSignature() | ErrorValidation():
        print(f"Failed with {resp}")
```

NOTE: currently a limited api/typing surface, if you encounter any errors please submit an issue

[project.urls]
Homepage = "https://github.com/i404788/tme-api"
Repository = "https://github.com/i404788/tme-api"
