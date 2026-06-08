from typing import Dict, Any, Optional, List
from .base import BaseProvider
from .nvidia_service import NvidiaProvider
from backend.config import NVIDIA_API_KEY, REPLICATE_API_TOKEN

class ProviderManager:
    def __init__(self):
        self.providers: Dict[str, BaseProvider] = {}
        self._init_providers()
    
    def _init_providers(self):
        # NVIDIA для анализа
        if NVIDIA_API_KEY:
            self.providers["nvidia"] = NvidiaProvider(NVIDIA_API_KEY)
            print("[INFO] NVIDIA провайдер инициализирован")
        
        # Pollinations для генерации (всегда доступен)
        from .pollinations_service import PollinationsProvider
        self.providers["pollinations"] = PollinationsProvider()
        print("[INFO] Pollinations провайдер инициализирован")
        
        # Replicate для генерации (если есть ключ)
        if REPLICATE_API_TOKEN:
            from .replicate_service import ReplicateProvider
            self.providers["replicate"] = ReplicateProvider(REPLICATE_API_TOKEN)
            print("[INFO] Replicate провайдер инициализирован")
    
    def get_provider(self, name: str) -> Optional[BaseProvider]:
        return self.providers.get(name)
    
    def list_providers(self) -> List[str]:
        return list(self.providers.keys())
    
    def get_all_vision_models(self) -> Dict[str, Dict[str, str]]:
        result = {}
        for provider_name, provider in self.providers.items():
            try:
                result[provider_name] = provider.get_vision_models()
            except:
                result[provider_name] = {}
        return result
    
    def get_all_generation_models(self) -> Dict[str, Dict[str, str]]:
        result = {}
        for provider_name, provider in self.providers.items():
            try:
                models = provider.get_generation_models()
                if models:
                    result[provider_name] = models
            except:
                pass
        return result

manager = ProviderManager()