from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseProvider(ABC):
    #Абстрактный класс для всех AI провайдеров
    @abstractmethod
    async def analyze_image(
        self, 
        image_bytes: bytes, 
        content_type: str, 
        model: str,
        prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        #Анализ изображения
        pass
    
    @abstractmethod
    async def generate_image(
        self,
        prompt: str,
        model: str,
        width: int = 1024,
        height: int = 1024
    ) -> Dict[str, Any]:
        #Генерация изображения
        pass
    
    @abstractmethod
    def get_vision_models(self) -> Dict[str, str]:
        #Список доступных моделей для анализа
        pass
    
    @abstractmethod
    def get_generation_models(self) -> Dict[str, str]:
        #Список доступных моделей для генерации
        pass