# AI Image Studio

Анализ и генерация изображений с использованием передовых AI моделей. Поддерживает несколько провайдеров для анализа и генерации изображений.

## Возможности

- Анализ изображений через NVIDIA NIM (бесплатно)
- Генерация изображений через Pollinations (бесплатно, без ключа)
- Генерация изображений через Replicate (Google Imagen, Flux, SDXL)
- Ансамбль моделей для анализа (параллельный запуск нескольких моделей)
- Drag & Drop загрузка изображений
- Современный адаптивный интерфейс

## Технологии

- Backend: FastAPI (Python 3.12)
- Frontend: HTML5, CSS3, JavaScript
- AI провайдеры: NVIDIA NIM, Replicate API, Pollinations API
- Контейнеризация: Docker + Docker Compose

## API ключи

| Провайдер | Назначение | Где получить | Стоимость |
|-----------|------------|--------------|-----------|
| NVIDIA NIM | Анализ изображений | [build.nvidia.com](https://build.nvidia.com) | Бесплатно |
| Replicate | Генерация изображений | [replicate.com](https://replicate.com) | Платно (есть стартовые кредиты) |
| Pollinations | Генерация изображений | Не требуется | Бесплатно |

## API Endpoints

| Метод | Эндпоинт | Описание | Тело запроса |
|-------|----------|----------|--------------|
| POST | `/api/analyze` | Анализ изображения | `file` (multipart/form-data) |
| POST | `/api/generate` | Генерация изображения | JSON с полями `prompt`, `provider`, `model`, `width`, `height` |
| GET | `/api/providers` | Получение списка провайдеров и моделей | - |
| GET | `/health` | Проверка статуса сервера | - |
| GET | `/api/status` | Статус доступности провайдеров | - |

### Пример запроса на анализ

```bash
curl -X POST http://localhost:8000/api/analyze \
  -F "file=@image.jpg" \
  -F "provider=nvidia" \
  -F "models=[\"nemotron-3-omni\", \"llama-3.2-11b-vision\"]"
```

## Доступные модели 

### Анализ изображений (NVIDIA)

| Модель | Описание |
|--------|----------|
| Nemotron 3 Nano Omni | Омни-модальная модель, понимает изображения, видео, речь |
| Nemotron Nano 12B VL | Мульти-изображения, видео, визуальные Q&A |
| Llama 3.2 11B Vision | Vision-language модель от Meta |
| Llama 3.2 90B Vision | Улучшенная версия 11B |
| Phi-4 Multimodal | Мультимодальная модель от Microsoft |
| Ministral 14B | Общего назначения VLM |

### Генерация изображений (Replicate)

| Модель | Описание | Стоимость |
|--------|----------|-----------|
| Google Imagen 3 | Высокое качество, фотореализм | $0.05/изобр |
| Google Imagen 3 Fast | Быстрая версия | $0.025/изобр |
| Flux Schnell | Быстрая генерация | $0.003/изобр |
| Flux Dev | Высокое качество | $0.005/изобр |
| SDXL Turbo | Баланс скорость/качество | $0.002/изобр |

### Генерация изображений (Pollinations)

| Модель | Описание | Стоимость |
|--------|----------|-----------|
| Flux | Основная модель | Бесплатно |
| Turbo | Быстрая генерация | Бесплатно |
| SDXL | Качественная генерация | Бесплатно |

## Быстрый старт

### Требования

- Docker и Docker Compose
- API ключи (для некоторых провайдеров)

### Установка и запуск

1. Клонируйте репозиторий

```bash
git clone https://github.com/your-username/ai-image-studio.git
cd ai-image-studio
```
2. Настройте переменные окружения

```bash
cp .env.example .env
```
3. docker-compose up --build -d
```bash
docker-compose up --build -d
```
## Лицензия

MIT