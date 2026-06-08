import base64
import httpx
import asyncio
from typing import Dict, Any, Optional, List
from .base import BaseProvider

class NvidiaProvider(BaseProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://integrate.api.nvidia.com/v1"
    
    def _get_headers(self):
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def get_vision_models(self) -> Dict[str, str]:
        """Все доступные бесплатные мультимодальные модели NVIDIA"""
        return {
            # Основные модели для анализа изображений
            "nemotron-3-omni": "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning",
            "nemotron-nano-vl": "nvidia/nemotron-nano-12b-v2-vl",
            "llama-3.2-11b-vision": "meta/llama-3.2-11b-vision-instruct",
            "llama-3.2-90b-vision": "meta/llama-3.2-90b-vision-instruct",
            
            # Дополнительные модели от других провайдеров (доступны через NVIDIA API)
            "moonshot-kimi": "moonshotai/kimi-k2.6",
            "ministral-14b": "mistralai/ministral-14b-instruct-2512",
            "phi-4-multimodal": "microsoft/phi-4-multimodal-instruct",
            "google-palindrome": "google/palindrome"
        }
    
    def get_generation_models(self) -> Dict[str, str]:
        """Модели для генерации изображений"""
        return {
            "sdxl-turbo": "nvidia/sdxl-turbo",
            "flux-schnell": "nvidia/flux-schnell",
        }
    
    async def analyze_image(
        self, 
        image_bytes: bytes, 
        content_type: str, 
        model: str,
        prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Анализ изображения через NVIDIA API
        """
        model_id = self.get_vision_models().get(model)
        if not model_id:
            # Если модель не найдена, используем первую попавшуюся
            model_id = list(self.get_vision_models().values())[0]
            print(f"[WARN] Модель {model} не найдена, используем {model_id}")
        
        base64_image = base64.b64encode(image_bytes).decode("utf-8")
        
        default_prompt = "Опиши подробно, что изображено на этой картинке. Назови объекты, действия, атмосферу. Если есть текст — прочитай его. Отвечай на русском языке."
        
        print(f"[DEBUG] NVIDIA анализ. Модель: {model_id}")
        
        async with httpx.AsyncClient(timeout=90.0) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self._get_headers(),
                    json={
                        "model": model_id,
                        "messages": [
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": prompt or default_prompt},
                                    {"type": "image_url", "image_url": {"url": f"data:{content_type};base64,{base64_image}"}}
                                ]
                            }
                        ],
                        "max_tokens": 1500,
                        "temperature": 0.7
                    }
                )
                
                print(f"[DEBUG] NVIDIA статус: {response.status_code}")
                
                if response.status_code != 200:
                    error_text = response.text[:300]
                    print(f"[DEBUG] NVIDIA ошибка: {error_text}")
                    return {
                        "provider": "nvidia",
                        "success": False,
                        "error": f"API ошибка ({response.status_code}): {error_text}"
                    }
                
                data = response.json()
                
                if "choices" in data and len(data["choices"]) > 0:
                    content = data["choices"][0].get("message", {}).get("content", "")
                    if content:
                        return {
                            "provider": "nvidia",
                            "model_name": model,
                            "model_id": model_id,
                            "analysis": content,
                            "success": True
                        }
                
                return {
                    "provider": "nvidia",
                    "success": False,
                    "error": "Пустой ответ от модели"
                }
                
            except httpx.TimeoutException:
                return {
                    "provider": "nvidia",
                    "success": False,
                    "error": "Таймаут. Модель отвечает слишком долго"
                }
            except Exception as e:
                print(f"[DEBUG] NVIDIA exception: {str(e)}")
                return {
                    "provider": "nvidia",
                    "success": False,
                    "error": str(e)
                }
    
    async def analyze_multiple_models(
        self, 
        image_bytes: bytes, 
        content_type: str, 
        models: List[str],
        prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Анализ одной картинки несколькими моделями параллельно
        """
        async def analyze_one(model_key: str):
            try:
                return await self.analyze_image(image_bytes, content_type, model_key, prompt)
            except Exception as e:
                return {
                    "provider": "nvidia",
                    "model_name": model_key,
                    "success": False,
                    "error": str(e)
                }
        
        tasks = [analyze_one(model) for model in models]
        results = await asyncio.gather(*tasks)
        
        successful = [r for r in results if r.get("success")]
        
        return {
            "success": True,
            "mode": "ensemble",
            "models_count": len(successful),
            "total_models": len(results),
            "results": results
        }
    
    async def generate_image(
        self,
        prompt: str,
        model: str,
        width: int = 1024,
        height: int = 1024
    ) -> Dict[str, Any]:
        """
        Генерация изображения (пока не поддерживается в бесплатных моделях NVIDIA)
        """
        return {
            "provider": "nvidia",
            "success": False,
            "error": "Генерация изображений через NVIDIA API требует платной подписки. Используйте Replicate или другой сервис."
        }