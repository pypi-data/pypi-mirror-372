from abc import ABC, abstractmethod


class BaseAdvancedEnvironments(ABC):
    @abstractmethod
    async def get_advanced_environments(self, logger):
        pass
