import base64
import httpx
import urllib.parse
import asyncio
from typing import Dict, Any, Optional
from .base import BaseProvider

class PollinationsProvider(BaseProvider):
    
    def get_vision_models(self) -> Dict[str, str]:
        return {}
    
    def get_generation_models(self) -> Dict[str, str]:
        return {
            "flux": "flux",
            "turbo": "turbo",
            "sdxl": "sdxl"
        }
    
    async def analyze_image(self, image_bytes: bytes, content_type: str, model: str, prompt: Optional[str] = None) -> Dict[str, Any]:
        return {
            "provider": "pollinations",
            "success": False,
            "error": "Pollinations не поддерживает анализ изображений. Используйте NVIDIA."
        }
    
    async def generate_image(self, prompt: str, model: str = "flux", width: int = 1024, height: int = 1024) -> Dict[str, Any]:
        """Генерация изображения через Pollinations с правильными заголовками"""
        
        # Ждем 3 секунды чтобы не перегружать
        await asyncio.sleep(3)
        
        encoded_prompt = urllib.parse.quote(prompt)
        
        # Используем другой эндпоинт который стабильнее
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}"
        
        params = {
            "width": width,
            "height": height,
            "model": model,
            "nologo": "true",
            "seed": int(asyncio.get_event_loop().time() * 1000) % 1000000  # динамический seed
        }
        
        # Важно: добавляем User-Agent чтобы сервер думал что это браузер
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7"
        }
        
        print(f"[DEBUG] Pollinations запрос к: {url}")
        print(f"[DEBUG] Параметры: {params}")
        
        async with httpx.AsyncClient(timeout=120.0, follow_redirects=True) as client:
            try:
                response = await client.get(url, params=params, headers=headers)
                
                print(f"[DEBUG] Статус: {response.status_code}")
                print(f"[DEBUG] Content-Type: {response.headers.get('content-type', 'unknown')}")
                
                if response.status_code == 200:
                    content_type_header = response.headers.get("content-type", "")
                    
                    if "image" in content_type_header:
                        image_base64 = base64.b64encode(response.content).decode("utf-8")
                        return {
                            "provider": "pollinations",
                            "model": model,
                            "prompt": prompt,
                            "image_base64": image_base64,
                            "success": True
                        }
                    else:
                        # Пробуем альтернативный эндпоинт
                        return await self._try_alternative_endpoint(prompt, model, width, height)
                else:
                    # Пробуем альтернативный эндпоинт
                    return await self._try_alternative_endpoint(prompt, model, width, height)
                    
            except Exception as e:
                print(f"[ERROR] Pollinations ошибка: {str(e)}")
                return await self._try_alternative_endpoint(prompt, model, width, height)
    
    async def _try_alternative_endpoint(self, prompt: str, model: str, width: int, height: int) -> Dict[str, Any]:
        """Альтернативный эндпоинт Pollinations"""
        
        encoded_prompt = urllib.parse.quote(prompt)
        url = f"https://pollinations.ai/p/{encoded_prompt}"
        
        params = {
            "width": width,
            "height": height,
            "model": model
        }
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        async with httpx.AsyncClient(timeout=120.0, follow_redirects=True) as client:
            try:
                response = await client.get(url, params=params, headers=headers)
                
                if response.status_code == 200 and "image" in response.headers.get("content-type", ""):
                    image_base64 = base64.b64encode(response.content).decode("utf-8")
                    return {
                        "provider": "pollinations",
                        "model": model,
                        "prompt": prompt,
                        "image_base64": image_base64,
                        "success": True
                    }
                else:
                    return {
                        "provider": "pollinations",
                        "success": False,
                        "error": "Сервер Pollinations временно перегружен. Попробуйте использовать Replicate провайдер."
                    }
            except Exception as e:
                return {
                    "provider": "pollinations",
                    "success": False,
                    "error": f"Ошибка: {str(e)}. Рекомендуется использовать Replicate провайдер."
                }