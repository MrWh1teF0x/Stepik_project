import src.PyParseFormats as PPF


class Page:
    def __init__(self):
        pass

    def parse(self, markdown: list[str]) -> None:
        pass

    def body(self):
        pass


class PageText(Page):
    def parse(self, markdown: list[str]) -> None:
        pass


class PageChoice(Page):
    pass


PAGE_DICT = {PPF.format_step_name: PageText}
