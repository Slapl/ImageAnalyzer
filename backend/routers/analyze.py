from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from backend.services.provider_manager import manager
from typing import Optional, List
import json

router = APIRouter(prefix="/api", tags=["analysis"])

@router.post("/analyze")
async def analyze_image(
    file: UploadFile = File(...),
    provider: str = Form("nvidia"),
    model: str = Form("nemotron-vision"),
    models: Optional[str] = Form(None),  # JSON строка со списком моделей для ансамбля
    prompt: Optional[str] = Form(None),
    ensemble: bool = Form(False)
):
    """
    Анализ изображения
    - models: JSON массив моделей для ансамбля, например '["nemotron-vision", "llama-vision"]'
    """
    print(f"[DEBUG] analyze: provider={provider}, model={model}, ensemble={ensemble}, models={models}")
    
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Загрузите изображение")
    
    contents = await file.read()
    
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Файл слишком большой")
    
    try:
        prov = manager.get_provider(provider)
        if not prov:
            raise HTTPException(status_code=400, detail=f"Провайдер {provider} не найден")
        
        if ensemble and models:
            # Ансамбль с выбранными моделями
            model_list = json.loads(models)
            result = await prov.analyze_multiple_models(contents, file.content_type, model_list, prompt)
        else:
            # Обычный режим
            result = await prov.analyze_image(contents, file.content_type, model, prompt)
        
        return result
    except Exception as e:
        print(f"[DEBUG] Exception: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка: {str(e)}")

@router.get("/providers")
async def get_providers():
    """Список доступных провайдеров и моделей"""
    result = {
        "providers": manager.list_providers(),
        "vision_models": {},
        "generation_models": {}
    }
    
    for provider_name in manager.list_providers():
        prov = manager.get_provider(provider_name)
        if prov:
            result["vision_models"][provider_name] = prov.get_vision_models()
            result["generation_models"][provider_name] = prov.get_generation_models()
    
    return result