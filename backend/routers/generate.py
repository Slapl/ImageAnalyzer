from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.services.provider_manager import manager

router = APIRouter(prefix="/api", tags=["generation"])

class GenerateRequest(BaseModel):
    prompt: str
    provider: str = "pollinations"  # меняем на pollinations по умолчанию
    model: str = "flux"
    width: int = 1024
    height: int = 1024

@router.post("/generate")
async def generate_image(request: GenerateRequest):
    """Генерация изображения"""
    if not request.prompt:
        raise HTTPException(status_code=400, detail="Введите описание")
    
    prov = manager.get_provider(request.provider)
    if not prov:
        # Если провайдер не найден, пробуем pollinations
        prov = manager.get_provider("pollinations")
        if not prov:
            raise HTTPException(status_code=400, detail="Нет доступных провайдеров для генерации")
    
    try:
        result = await prov.generate_image(
            prompt=request.prompt,
            model=request.model,
            width=request.width,
            height=request.height
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка генерации: {str(e)}")