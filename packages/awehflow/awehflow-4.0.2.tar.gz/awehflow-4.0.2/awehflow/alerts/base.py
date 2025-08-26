from abc import ABC, abstractmethod


class Alerter(ABC):
    @abstractmethod
    def alert(self, context): #pragma: no cover
        pass
