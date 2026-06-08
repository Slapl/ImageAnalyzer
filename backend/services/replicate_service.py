import base64
import httpx
import asyncio
from typing import Dict, Any, Optional
from .base import BaseProvider

class ReplicateProvider(BaseProvider):
    
    def __init__(self, api_token: str):
        self.api_token = api_token
    
    def get_vision_models(self) -> Dict[str, str]:
        return {}
    
    def get_generation_models(self) -> Dict[str, str]:
        """Модели для генерации через Replicate"""
        return {
            # Google Imagen модели
            "imagen-3": "google/imagen-3",
            "imagen-3-fast": "google/imagen-3-fast",
            # Flux модели от Black Forest Labs
            "flux-schnell": "black-forest-labs/flux-schnell",
            "flux-dev": "black-forest-labs/flux-dev",
            # SDXL
            "sdxl": "stability-ai/sdxl"
        }
    
    async def analyze_image(self, image_bytes: bytes, content_type: str, model: str, prompt: Optional[str] = None) -> Dict[str, Any]:
        return {
            "provider": "replicate",
            "success": False,
            "error": "Replicate не поддерживает анализ изображений"
        }
    
    async def generate_image(self, prompt: str, model: str = "flux-schnell", width: int = 1024, height: int = 1024) -> Dict[str, Any]:
        """Генерация изображения через Replicate"""
        
        import replicate
        
        # Маппинг моделей
        model_map = {
            "imagen-3": "google/imagen-3",
            "imagen-3-fast": "google/imagen-3-fast",
            "flux-schnell": "black-forest-labs/flux-schnell",
            "flux-dev": "black-forest-labs/flux-dev",
            "sdxl": "stability-ai/sdxl"
        }
        
        model_id = model_map.get(model, "black-forest-labs/flux-schnell")
        
        # Преобразуем размеры в aspect_ratio для Imagen моделей
        aspect_ratio = self._get_aspect_ratio(width, height)
        
        try:
            # Для Imagen моделей используем aspect_ratio
            if model in ["imagen-3", "imagen-3-fast"]:
                input_params = {
                    "prompt": prompt,
                    "aspect_ratio": aspect_ratio,
                    "output_format": "png",
                    "safety_filter_level": "block_only_high"
                }
            else:
                # Для остальных моделей используем стандартные параметры
                input_params = {
                    "prompt": prompt,
                    "num_outputs": 1
                }
                if "sdxl" in model:
                    input_params["width"] = width
                    input_params["height"] = height
            
            output = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: replicate.run(model_id, input=input_params)
            )
            
            # Получаем URL изображения из ответа
            if output and hasattr(output, '__iter__'):
                image_url = output[0] if isinstance(output, list) else output
                
                if isinstance(image_url, str) and image_url.startswith('http'):
                    async with httpx.AsyncClient() as client:
                        response = await client.get(image_url)
                        if response.status_code == 200:
                            image_base64 = base64.b64encode(response.content).decode("utf-8")
                            return {
                                "provider": "replicate",
                                "model": model,
                                "model_id": model_id,
                                "prompt": prompt,
                                "image_base64": image_base64,
                                "success": True
                            }
            
            return {"provider": "replicate", "success": False, "error": "Ошибка генерации"}
            
        except Exception as e:
            return {"provider": "replicate", "success": False, "error": str(e)}
    
    def _get_aspect_ratio(self, width: int, height: int) -> str:
        """Преобразует размеры в соотношение сторон для Imagen"""
        ratios = {
            (1024, 1024): "1:1",
            (1024, 768): "4:3",
            (768, 1024): "3:4",
            (1024, 576): "16:9",
            (576, 1024): "9:16"
        }
        return ratios.get((width, height), "1:1")