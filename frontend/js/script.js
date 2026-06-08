// ========== DOM элементы ==========
const imageInput = document.getElementById('imageInput');
const uploadArea = document.getElementById('uploadArea');
const previewArea = document.getElementById('previewArea');
const preview = document.getElementById('preview');
const removeBtn = document.getElementById('removeBtn');
const analyzeBtn = document.getElementById('analyzeBtn');
const loading = document.getElementById('loading');
const result = document.getElementById('result');
const visionModel = document.getElementById('visionModel');
const singleModeDiv = document.getElementById('singleMode');
const ensembleModeDiv = document.getElementById('ensembleModePanel');
const modeRadios = document.querySelectorAll('input[name="mode"]');
const ensembleCheckboxes = document.querySelectorAll('.ensemble-model');

// Генерация
const generateBtn = document.getElementById('generateBtn');
const genLoading = document.getElementById('genLoading');
const genResult = document.getElementById('genResult');
const generatedImage = document.getElementById('generatedImage');
const downloadBtn = document.getElementById('downloadBtn');
const promptInput = document.getElementById('promptInput');
const genProvider = document.getElementById('genProvider');
const genModel = document.getElementById('genModel');
const genWidth = document.getElementById('genWidth');
const genHeight = document.getElementById('genHeight');

let currentFile = null;

// ========== ПЕРЕКЛЮЧЕНИЕ МЕЖДУ РЕЖИМАМИ ==========
if (modeRadios.length) {
    modeRadios.forEach(radio => {
        radio.addEventListener('change', () => {
            if (radio.value === 'single') {
                if (singleModeDiv) singleModeDiv.style.display = 'block';
                if (ensembleModeDiv) ensembleModeDiv.style.display = 'none';
            } else {
                if (singleModeDiv) singleModeDiv.style.display = 'none';
                if (ensembleModeDiv) ensembleModeDiv.style.display = 'block';
            }
        });
    });
}

// ========== UPLOAD ЛОГИКА ==========
if (uploadArea) {
    uploadArea.addEventListener('click', () => imageInput.click());

    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = '#7a8bd9';
        uploadArea.style.background = '#000000';
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.style.borderColor = '#555555';
        uploadArea.style.background = 'transparent';
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = '#555555';
        uploadArea.style.background = 'transparent';
        
        const file = e.dataTransfer.files[0];
        if (file && file.type.startsWith('image/')) {
            handleFile(file);
        } else {
            alert('Пожалуйста, перетащите изображение');
        }
    });
}

if (imageInput) {
    imageInput.addEventListener('change', (e) => {
        if (e.target.files[0]) {
            handleFile(e.target.files[0]);
        }
    });
}

if (removeBtn) {
    removeBtn.addEventListener('click', () => {
        currentFile = null;
        if (previewArea) previewArea.style.display = 'none';
        if (uploadArea) uploadArea.style.display = 'block';
        if (analyzeBtn) analyzeBtn.disabled = true;
        if (result) result.style.display = 'none';
        if (imageInput) imageInput.value = '';
    });
}

// ========== АНАЛИЗ ==========
if (analyzeBtn) {
    analyzeBtn.addEventListener('click', async () => {
        if (!currentFile) {
            alert('Сначала выберите картинку');
            return;
        }
        
        const isEnsemble = document.querySelector('input[name="mode"]:checked')?.value === 'ensemble';
        
        const formData = new FormData();
        formData.append('file', currentFile);
        formData.append('provider', 'nvidia');
        formData.append('ensemble', isEnsemble);
        
        if (isEnsemble) {
            const selectedModels = [];
            ensembleCheckboxes.forEach(cb => {
                if (cb.checked) selectedModels.push(cb.value);
            });
            if (selectedModels.length === 0) {
                alert('Выберите хотя бы одну модель для ансамбля');
                return;
            }
            formData.append('models', JSON.stringify(selectedModels));
            formData.append('model', '');
        } else {
            formData.append('model', visionModel.value);
            formData.append('models', '');
        }
        
        analyzeBtn.disabled = true;
        loading.style.display = 'block';
        result.style.display = 'none';
        
        try {
            const response = await fetch('/api/analyze', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            console.log('Ответ:', data);
            
            if (response.ok && data.success !== false) {
                let html = '';
                
                if (data.mode === 'ensemble' && data.results) {
                    html = '<h3>Ансамбль (' + data.results.length + ' моделей):</h3>';
                    for (const r of data.results) {
                        if (r.success) {
                            html += '<div class="result-card">' +
                                '<div class="result-header"> ' + r.model_name + '</div>' +
                                '<div class="result-content">' + r.analysis + '</div>' +
                            '</div>';
                        } else {
                            html += '<div class="result-card error">' +
                                '<div class="result-header"> ' + r.model_name + '</div>' +
                                '<div class="result-content">' + r.error + '</div>' +
                            '</div>';
                        }
                    }
                } else if (data.analysis) {
                    html = '<div class="result-card">' +
                        '<div class="result-header"> ' + (data.model_name || data.model || 'AI') + '</div>' +
                        '<div class="result-content">' + data.analysis + '</div>' +
                    '</div>';
                } else {
                    html = '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
                }
                
                result.innerHTML = html;
                result.style.display = 'block';
            } else {
                result.innerHTML = '<div class="result-card error"> Ошибка: ' + (data.detail || data.error) + '</div>';
                result.style.display = 'block';
            }
        } catch (err) {
            result.innerHTML = '<div class="result-card error"> Ошибка: ' + err.message + '</div>';
            result.style.display = 'block';
        } finally {
            analyzeBtn.disabled = false;
            loading.style.display = 'none';
        }
    });
}

// ========== ФУНКЦИЯ ОБНОВЛЕНИЯ МОДЕЛЕЙ ГЕНЕРАЦИИ ==========
function updateGenerationModels() {
    if (!genProvider || !genModel) return;
    
    const provider = genProvider.value;
    
    if (provider === 'pollinations') {
        genModel.innerHTML = `
            <option value="flux">Flux (рекомендуется, бесплатно)</option>
            <option value="turbo">Turbo (быстрая)</option>
            <option value="sdxl">SDXL (качественная)</option>
        `;
    } else if (provider === 'replicate') {
        genModel.innerHTML = `
            <optgroup label="Google Imagen">
                <option value="imagen-3">Google Imagen 3 (высокое качество)</option>
                <option value="imagen-3-fast" selected>Google Imagen 3 Fast (быстрая)</option>
            </optgroup>
            <optgroup label="Black Forest Labs (Flux)">
                <option value="flux-schnell">Flux Schnell (быстрая)</option>
                <option value="flux-dev">Flux Dev (качественная)</option>
            </optgroup>
            <optgroup label="Stability AI">
                <option value="sdxl">SDXL Turbo</option>
            </optgroup>
        `;
    }
}

// ========== ГЕНЕРАЦИЯ ==========
if (generateBtn) {
    generateBtn.addEventListener('click', async () => {
        const prompt = promptInput?.value.trim();
        if (!prompt) {
            alert('Введите описание изображения');
            return;
        }
        
        const provider = genProvider?.value || 'pollinations';
        const model = genModel?.value || 'flux';
        const width = genWidth ? parseInt(genWidth.value) : 1024;
        const height = genHeight ? parseInt(genHeight.value) : 1024;
        
        generateBtn.disabled = true;
        genLoading.style.display = 'block';
        genResult.style.display = 'none';
        
        try {
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    prompt: prompt,
                    provider: provider,
                    model: model,
                    width: width,
                    height: height
                })
            });
            
            const data = await response.json();
            console.log('Ответ генерации:', data);
            
            if (response.ok && data.success && data.image_base64) {
                const imageSrc = 'data:image/png;base64,' + data.image_base64;
                generatedImage.src = imageSrc;
                genResult.style.display = 'block';
                
                const modelInfo = document.getElementById('genModelInfo');
                if (modelInfo) {
                    modelInfo.innerHTML = 'Сгенерировано с помощью: ' + provider + ' / ' + model;
                }
                
                downloadBtn.onclick = () => {
                    const link = document.createElement('a');
                    link.download = 'generated_' + Date.now() + '.png';
                    link.href = imageSrc;
                    link.click();
                };
            } else {
                alert('Ошибка генерации: ' + (data.detail || data.error || 'Неизвестная ошибка'));
            }
        } catch (err) {
            console.error('Ошибка:', err);
            alert('Ошибка: ' + err.message);
        } finally {
            generateBtn.disabled = false;
            genLoading.style.display = 'none';
        }
    });
}

// ========== СЛЕДИМ ЗА СМЕНОЙ ПРОВАЙДЕРА ==========
if (genProvider) {
    genProvider.addEventListener('change', updateGenerationModels);
}

// ========== ЗАГРУЗКА МОДЕЛЕЙ ПРИ СТАРТЕ ==========
updateGenerationModels();

function handleFile(file) {
    if (file.size > 10 * 1024 * 1024) {
        alert('Файл слишком большой! Максимум 10MB');
        return;
    }
    
    currentFile = file;
    
    const reader = new FileReader();
    reader.onload = (e) => {
        preview.src = e.target.result;
        previewArea.style.display = 'block';
        uploadArea.style.display = 'none';
        analyzeBtn.disabled = false;
        result.style.display = 'none';
    };
    reader.readAsDataURL(file);
}

// ========== ВКЛАДКИ ==========
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const tab = btn.dataset.tab;
        
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        
        btn.classList.add('active');
        document.getElementById(tab + 'Tab').classList.add('active');
    });
});