from abc import ABC, abstractmethod
from typing import Any, Dict


class AIModel(ABC):
    """
    Abstract class that defines the interface for all AI models in this project.
    """

    def __init__(self, model_path: str):
        self.model_path = model_path
        self.model = None
        self.load_model()

    @abstractmethod
    def load_model(self) -> None:
        """
        Load weights and initialize the model.
        Must be implemented by the subclass.
        """
        pass

    @abstractmethod
    def predict(self, input_data: Any, **kwargs: Any) -> Any:
        """
        Run inference on the input data.
        Must be implemented by the subclass.
        """
        pass
