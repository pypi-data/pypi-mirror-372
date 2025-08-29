from builtins import ValueError
from typing import Any
from builtins import NotImplementedError
from typing_extensions import Self
from pydantic import BaseModel
from typing import TypeVar, Literal, Generic

DataT = TypeVar("DataT")

Currencies = Literal["EUR"]
Languages = Literal["EN"]
PriceTypes = Literal["NET", "GROSS"]
Units = Literal["pcs", "m", "rol"]
VatType = Literal["VAT"]


class ValidationDetailsInner(BaseModel):
    value: list[str]
    message: str


class ErrorValidationDetails(BaseModel):
    Validation: dict[str, ValidationDetailsInner]


class ErrorType(BaseModel):
    ErrorCode: int
    ErrorMessage: str
    Error: Any

    def unwrap(self):
        raise ValueError(f"TME Api request failed with {self.ErrorCode=} {self.ErrorMessage=} {self.Error=}")


class ErrorValidation(ErrorType):
    Status: Literal["E_INPUT_PARAMS_VALIDATION_ERROR"]
    Error: ErrorValidationDetails


class ErrorSignature(ErrorType):
    Status: Literal["E_INVALID_SIGNATURE"]
    Error: list


class Ok(BaseModel, Generic[DataT]):
    Status: Literal["OK"] = "OK"
    Data: DataT

    def unwrap(self) -> DataT:
        return self.Data


class PriceQty(BaseModel):
    Amount: int
    PriceValue: float
    PriceBase: int
    Special: bool


class PriceDetails(BaseModel):
    Symbol: str
    PriceList: list[PriceQty]
    Unit: Units
    VatRate: float
    VatType: VatType


class Cursorable(BaseModel):
    pass

    def extend(self, other: Self) -> Self:
        raise NotImplementedError()


class GetPricesData(Cursorable):
    Currency: Currencies
    Language: Languages
    PriceType: PriceTypes
    ProductList: list[PriceDetails]

    def extend(self, other: Self) -> Self:
        return GetPricesData.parse_obj(
            {
                "Currency": self.Currency,
                "Language": self.Language,
                "PriceType": self.PriceType,
                "ProductList": [*self.ProductList, *other.ProductList],
            }
        )


class PriceAndStockDetails(BaseModel):
    Symbol: str
    PriceList: list[PriceQty]
    Unit: Units
    VatRate: float
    VatType: VatType
    Amount: int


class GetPricesAndStocksData(Cursorable):
    Currency: Currencies
    Language: Languages
    PriceType: PriceTypes
    ProductList: list[PriceAndStockDetails]

    def extend(self, other: Self) -> Self:
        return GetPricesAndStocksData.parse_obj(
            {
                "Currency": self.Currency,
                "Language": self.Language,
                "PriceType": self.PriceType,
                "ProductList": [*self.ProductList, *other.ProductList],
            }
        )


class GetSymbols(BaseModel):
    SymbolList: list[str]


class CategoryNode(BaseModel):
    Id: int
    ParentId: int
    Depth: int
    Name: str
    TotalProducts: int
    SubTreeCount: int
    Thumbnail: str
    SubTree: list["CategoryNode"]


class GetCategories(BaseModel):
    CategoryTree: CategoryNode


class ProductDescriptor(BaseModel):
    Symbol: str
    OriginalSymbol: str
    CustomerSymbol: str
    Photo: str
    Thumbnail: str
    Description: str


class MatchData(BaseModel):
    Field: str
    Similarity: str


class MatchDescriptor(BaseModel):
    Product: ProductDescriptor
    MatchData: MatchData


class Autocomplete(BaseModel):
    Result: list[MatchDescriptor]


class Warranty(BaseModel):
    Type: Literal["period", "lifetime"]
    Period: int


class ProductDetails(BaseModel):
    Symbol: str
    OriginalSymbol: str
    Producer: str
    Description: str
    OfferId: int | None
    CategoryId: int
    Category: str
    Photo: str
    Thumbnail: str
    Weight: float
    SuppliedAmount: int
    MinAmount: int
    Multiplies: int | None = None
    Unit: str
    ProductInformationPage: str
    Guarantee: list[Warranty] | None
    ProductStatusList: list[str]


class GetProducts(BaseModel):
    ProductList: list[ProductDetails]
    Language: str
