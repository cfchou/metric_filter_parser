
class JsonFilterException(Exception):
    pass


class ParsingException(JsonFilterException):
    pass


class VisitorException(JsonFilterException):
    pass


class SelectorException(VisitorException):
    pass


