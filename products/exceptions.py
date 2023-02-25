class ProductException(Exception):
    ...


class SubscriptionException(ProductException):
    ...


class CurrentSubscriptionIsActive(SubscriptionException):
    ...
