from dataclasses import dataclass


@dataclass
class StepText:
    title: str = ""
    text: str = ""

    def parse(self, markdown: list[str]) -> None:
        pass

    def body(self):
        pass


@dataclass
class StepString:
    title: str = ""
    text: str = ""

    def parse(self, markdown: list[str]) -> None:
        pass

    def body(self):
        pass


@dataclass
class StepNumber:
    title: str = ""
    text: str = ""

    def parse(self, markdown: list[str]) -> None:
        pass

    def body(self):
        pass


@dataclass
class StepQuiz:
    title: str = ""
    text: str = ""

    def parse(self, markdown: list[str]) -> None:
        pass

    def body(self):
        pass


@dataclass
class StepTask:
    title: str = ""
    text: str = ""

    def parse(self, markdown: list[str]) -> None:
        pass

    def body(self):
        pass
