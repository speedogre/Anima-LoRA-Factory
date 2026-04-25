

// Tab handling
document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', () => {
        const tab = item.getAttribute('data-tab');
        
        // Update nav
        document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
        item.classList.add('active');
        
        // Update content
        document.querySelectorAll('.tab-content').forEach(c => c.style.display = 'none');
        document.getElementById(`tab-${tab}`).style.display = 'block';
    });
});

async function browseFolder() {
    const response = await fetch('/api/browse-folder');
    const data = await response.json();
    if (data.path) {
        document.getElementById('dataset-path').value = data.path;
    }
}

async function browseFile(inputId, titleStr) {
    const response = await fetch(`/api/browse-file?title=${encodeURIComponent(titleStr)}`);
    const data = await response.json();
    if (data.path) {
        const input = document.getElementById(inputId);
        input.value = data.path;
        localStorage.setItem(`sdxl_factory_saved_${inputId}`, data.path);
    }
}

async function browseOutput() {
    const response = await fetch('/api/browse-folder');
    const data = await response.json();
    if (data.path) {
        const input = document.getElementById('output-dir');
        input.value = data.path;
        localStorage.setItem('sdxl_factory_savedOutputDir', data.path);
    }
}

function toggleAdvancedSettings() {
    const isChecked = document.getElementById('enable-advanced').checked;
    const container = document.getElementById('advanced-settings-container');
    container.style.display = isChecked ? 'flex' : 'none';
}

async function loadGPUInfo() {
    try {
        const response = await fetch('/api/gpu-info');
        const data = await response.json();
        const display = document.getElementById('gpu-info-display');
        if (display) {
            display.innerText = `${data.name} (VRAM: ${data.memory})`;
        }
    } catch (e) {
        console.error("Failed to load GPU info", e);
    }
}

async function checkScriptsStatus() {
    const response = await fetch('/api/check-scripts');
    const data = await response.json();
    if (data.exists) {
        const btn = document.getElementById('setup-scripts-btn');
        btn.innerText = '✅ エンジン取得済み (Ready)';
        btn.disabled = true;
        btn.style.opacity = '0.5';
        btn.style.background = 'rgba(52, 211, 153, 0.2)';
        btn.style.borderColor = '#34d499';
    }
}

async function setupScripts() {
    const btn = document.getElementById('setup-scripts-btn');
    const progressText = document.getElementById('setup-progress-text');
    btn.disabled = true;
    btn.innerText = 'セットアップ中... (Setting up...)';
    
    if (progressText) {
        progressText.style.display = 'block';
    }

    try {
        const response = await fetch('/api/setup-scripts', { method: 'POST' });
        const data = await response.json();
        if (data.status === 'started' || data.status === 'exists') {
            // Poll for completion
            let attempts = 0;
            const maxAttempts = 30; // 30 * 3s = 90 seconds timeout
            const interval = setInterval(async () => {
                attempts++;
                const checkRes = await fetch('/api/check-scripts');
                const checkData = await checkRes.json();
                
                if (checkData.exists) {
                    clearInterval(interval);
                    btn.innerText = '✅ 取得完了！ (Success)';
                    if (progressText) progressText.innerText = '✅ セットアップが完了しました。 / Setup completed successfully.';
                    checkScriptsStatus(); // Update button UI
                    alert('エンジンの自動取得が完了しました！ / Engine setup completed!');
                } else if (attempts >= maxAttempts) {
                    clearInterval(interval);
                    btn.disabled = false;
                    btn.innerText = '❌ タイムアウト (Timeout)';
                    if (progressText) progressText.innerText = '❌ 取得に時間がかかりすぎています。コンソールを確認してください。';
                    alert('エンジンの確認がタイムアウトしました。');
                }
            }, 3000);
        } else {
            alert('Error: ' + data.message);
            btn.disabled = false;
            btn.innerText = '❌ 取得失敗 (Failed)';
            if (progressText) progressText.innerText = '❌ エラーが発生しました。Gitがインストールされているか確認してください。 / Error occurred. Please check if Git is installed.';
        }
    } catch (e) {
        alert('Error: ' + e.message);
        btn.disabled = false;
        btn.innerText = '学習エンジンの自動取得 (Setup sd-scripts)';
        if (progressText) progressText.style.display = 'none';
    }
}

// Check on load
window.addEventListener('DOMContentLoaded', () => {
    checkScriptsStatus();
    loadGPUInfo();
    
    // Load saved paths
    const savedModel = localStorage.getItem('sdxl_factory_savedModelPath');
    const savedOutput = localStorage.getItem('sdxl_factory_savedOutputDir');
    if (savedModel) document.getElementById('model-path').value = savedModel;
    if (savedOutput) document.getElementById('output-dir').value = savedOutput;

    // Add event listeners to save on manual typing
    document.getElementById('model-path')?.addEventListener('change', (e) => localStorage.setItem('sdxl_factory_savedModelPath', e.target.value));
    document.getElementById('output-dir')?.addEventListener('change', (e) => localStorage.setItem('sdxl_factory_savedOutputDir', e.target.value));
});

function validatePath() {
    const path = document.getElementById('dataset-path').value;
    if (!path) {
        alert('パスを入力してください / Please enter a path');
        return;
    }
    // Switch to tagger tab instead of config
    document.querySelector('.nav-item[data-tab="tagger"]').click();
    loadDataset(path);
}

async function loadDataset(path) {
    const container = document.getElementById('tag-editor-content');
    container.innerHTML = '<p>Loading dataset...</p>';
    
    try {
        const response = await fetch(`/api/dataset/images?path=${encodeURIComponent(path)}`);
        const data = await response.json();
        
        container.innerHTML = '';
        data.files.forEach(file => {
            const card = createTagCard(file);
            container.appendChild(card);
        });
        updateTagSuggestions();
    } catch (e) {
        container.innerHTML = `<p style="color: red;">Error: ${e.message}</p>`;
    }
}

function updateTagSuggestions() {
    const datalist = document.getElementById('tag-suggestions');
    if (!datalist) return;

    const allTags = new Set();
    document.querySelectorAll('.tag-chip').forEach(chip => {
        const tag = chip.getAttribute('data-tag');
        if (tag) allTags.add(tag);
    });

    datalist.innerHTML = '';
    Array.from(allTags).sort().forEach(tag => {
        const option = document.createElement('option');
        option.value = tag;
        datalist.appendChild(option);
    });
}

function createTagCard(file) {
    const card = document.createElement('div');
    card.className = 'card image-tag-card';
    
    // Use the proxy API for local images
    const imgUrl = `/api/image?path=${encodeURIComponent(file.path)}`;
    
    card.innerHTML = `
        <img src="${imgUrl}" class="tag-preview-img">
        <div class="tags-container" data-path="${file.path}">
            ${file.tags.map(tag => `
                <span class="tag-chip ${tag.category}" data-tag="${tag.name}">
                    ${tag.name} <span class="remove-btn" onclick="removeTag(this)">×</span>
                </span>
            `).join('')}
            <input type="text" class="add-tag-input" placeholder="+ Add" onkeydown="handleTagInput(event, this)">
        </div>
    `;
    return card;
}

function removeTag(el) {
    const chip = el.parentElement;
    const container = chip.parentElement;
    chip.remove();
    saveTags(container);
    updateTagSuggestions();
}

function handleTagInput(event, input) {
    if (event.key === 'Enter') {
        const val = input.value.trim();
        if (val) {
            const container = input.parentElement;
            const chip = document.createElement('span');
            // Simple logic for category on the fly
            const category = val.startsWith('@') ? 'tag-char' : 'tag-general';
            chip.className = `tag-chip ${category}`;
            chip.setAttribute('data-tag', val);
            chip.innerHTML = `${val} <span class="remove-btn" onclick="removeTag(this)">×</span>`;
            container.insertBefore(chip, input);
            input.value = '';
            saveTags(container);
            updateTagSuggestions();
        }
    }
}

async function saveTags(container) {
    const path = container.getAttribute('data-path');
    const tags = Array.from(container.querySelectorAll('.tag-chip')).map(c => c.getAttribute('data-tag'));
    
    await fetch('/api/dataset/update-tags', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path, tags })
    });
}

async function batchAddTags() {
    const input = document.getElementById('batch-tags-input');
    const tags = input.value.split(',').map(t => t.trim()).filter(t => t);
    if (tags.length === 0) {
        alert('タグを入力してください / Please enter tags');
        return;
    }

    const containers = document.querySelectorAll('.tags-container');
    let totalAdded = 0;
    for (const container of containers) {
        if (container.closest('.placeholder-card')) continue;

        const currentTags = Array.from(container.querySelectorAll('.tag-chip')).map(c => c.getAttribute('data-tag'));
        let addedInCard = false;
        tags.forEach(tag => {
            if (!currentTags.includes(tag)) {
                const chip = document.createElement('span');
                const category = tag.startsWith('@') ? 'tag-char' : 'tag-general';
                chip.className = `tag-chip ${category}`;
                chip.setAttribute('data-tag', tag);
                chip.innerHTML = `${tag} <span class="remove-btn" onclick="removeTag(this)">×</span>`;
                
                const inputEl = container.querySelector('.add-tag-input');
                container.insertBefore(chip, inputEl);
                addedInCard = true;
                totalAdded++;
            }
        });
        if (addedInCard) {
            await saveTags(container);
        }
    }
    updateTagSuggestions();
    alert(`一括追加が完了しました（${totalAdded}個のタグを追加） / Batch add completed (${totalAdded} tags added)`);
}

async function batchRemoveTags() {
    const input = document.getElementById('batch-tags-input');
    const tags = input.value.split(',').map(t => t.trim()).filter(t => t);
    if (tags.length === 0) {
        alert('タグを入力してください / Please enter tags');
        return;
    }

    const containers = document.querySelectorAll('.tags-container');
    let totalRemoved = 0;
    for (const container of containers) {
        if (container.closest('.placeholder-card')) continue;

        let removedInCard = false;
        tags.forEach(tag => {
            const chips = container.querySelectorAll(`.tag-chip[data-tag="${tag}"]`);
            if (chips.length > 0) {
                chips.forEach(c => {
                    c.remove();
                    totalRemoved++;
                });
                removedInCard = true;
            }
        });
        if (removedInCard) {
            await saveTags(container);
        }
    }
    updateTagSuggestions();
    alert(`一括削除が完了しました（${totalRemoved}個のタグを削除） / Batch remove completed (${totalRemoved} tags removed)`);
}

async function runAutoTagging() {
    const btn = document.getElementById('run-tagger-btn');
    const path = document.getElementById('dataset-path').value;
    
    if (!path) {
        alert('パスを入力してください / Please enter a path');
        return;
    }

    if (btn) {
        btn.disabled = true;
        btn.innerText = 'タグ付け実行中... / Tagging...';
    }
    
    // Show progress bar
    const progressContainer = document.getElementById('tagger-progress-container');
    if (progressContainer) {
        progressContainer.style.display = 'block';
        document.getElementById('tagger-progress-percent').innerText = '0%';
        document.getElementById('tagger-progress-bar').style.width = '0%';
        document.getElementById('tagger-progress-text').innerText = 'タグ付け進捗: 準備中... / Tagging Progress: Preparing...';
    }

    connectWebSocket();

    try {
        const response = await fetch('/api/run-tagger', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                path: path, 
                model: document.getElementById('model-path').value || '',
                output_dir: '',
                name: 'tagger_job',
                vram: 'balanced',
                epochs: 1,
                lr: '0'
            })
        });
        
        const data = await response.json();
        if (data.status === 'started') {
            console.log("Tagger started...");
        } else {
            const errorMsg = data.message || (data.detail ? JSON.stringify(data.detail) : "Unknown error");
            alert("Error: " + errorMsg);
            if (btn) {
                btn.disabled = false;
                btn.innerText = '自動タグ付け実行 / Run Tagger';
            }
        }
    } catch (e) {
        alert("Error: " + e.message);
        if (btn) {
            btn.disabled = false;
            btn.innerText = '自動タグ付け実行 / Run Tagger';
        }
    }
}

// Add a refresh button or logic
async function refreshDataset() {
    const path = document.getElementById('dataset-path').value;
    if (path) {
        loadDataset(path);
    }
}

async function startTraining() {
    const consoleOut = document.getElementById('console-output');
    consoleOut.innerHTML = '学習プロセスを開始しています...<br>';
    
    // Switch to train tab
    document.querySelector('.nav-item[data-tab="train"]').click();

    try {
        const response = await fetch('/api/start-training', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                path: document.getElementById('dataset-path').value,
                model: document.getElementById('model-path').value,
                vae: document.getElementById('vae-path').value,
                output_dir: document.getElementById('output-dir').value,
                name: document.getElementById('output-name').value,
                vram: document.getElementById('vram-mode').value,
                epochs: parseInt(document.getElementById('epochs').value) || 10,
                lr: document.querySelector('input[name="learning-rate"]:checked').value,
                rank: parseInt(document.getElementById('lora-rank').value) || 4,
                alpha: parseInt(document.getElementById('lora-alpha').value) || 1,
                shutdown: document.getElementById('auto-shutdown').checked
            })
        });
        
        const data = await response.json();
        if (data.status === 'started') {
            connectWebSocket();
            // Disable UI
            document.getElementById('start-train-btn').disabled = true;
            document.getElementById('start-train-btn').innerText = '学習準備中... / Preparing...';
            document.getElementById('auto-shutdown').disabled = true;
        } else {
            consoleOut.innerHTML += `<span style="color: #ef4444;">Error: ${data.message}</span>`;
        }
    } catch (e) {
        consoleOut.innerHTML += `<span style="color: #ef4444;">Error: ${e.message}</span>`;
    }
}



function connectWebSocket() {
    const consoleOut = document.getElementById('console-output');
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const ws = new WebSocket(`${protocol}//${window.location.host}/ws/logs`);
    
    ws.onmessage = (event) => {
        const data = event.data.trim();
        // Append log line
        const line = document.createElement('div');
        line.innerText = data;
        consoleOut.appendChild(line);
        consoleOut.scrollTop = consoleOut.scrollHeight;

        if (data.includes("[TAGGER_PROGRESS]")) {
            const match = data.match(/\[TAGGER_PROGRESS\]\s+(\d+)\/(\d+)/);
            if (match) {
                const current = parseInt(match[1]);
                const total = parseInt(match[2]);
                const percent = Math.round((current / total) * 100);
                
                const progressText = document.getElementById('tagger-progress-text');
                const progressPercent = document.getElementById('tagger-progress-percent');
                const progressBar = document.getElementById('tagger-progress-bar');
                
                if (progressText) {
                    progressText.innerText = `タグ付け進捗 / Tagging Progress: ${current} / ${total}`;
                    progressPercent.innerText = `${percent}%`;
                    progressBar.style.width = `${percent}%`;
                }
                
                if (current === total) {
                    setTimeout(() => {
                        refreshDataset();
                        document.getElementById('tagger-progress-container').style.display = 'none';
                        const btn = document.getElementById('run-tagger-btn');
                        if (btn) {
                            btn.disabled = false;
                            btn.innerText = '自動タグ付け実行 / Run Tagger';
                        }
                    }, 1000);
                }
            }
        }

        if (data.includes("steps:")) {
            const match = data.match(/steps:\s+(\d+)%\|.*\| (\d+)\/(\d+)/);
            if (match) {
                const percent = match[1];
                const current = match[2];
                const total = match[3];
                
                // Update button
                const btn = document.getElementById('start-train-btn');
                if (btn) {
                    btn.innerText = `学習中 / Training: ${percent}% (${current}/${total})`;
                }
                
                // Update page title
                document.title = `(${percent}%) SDXL LoRA Factory`;
            }
        }

        if (data.includes("--- TRAIN Finished ---") || data.includes("All Processes Finished Successfully")) {
            const btn = document.getElementById('start-train-btn');
            if (btn) {
                btn.disabled = false;
                btn.innerText = '🚀 LoRA学習開始 / Start Training';
            }
            document.getElementById('auto-shutdown').disabled = false;
            
            // Reset title
            document.title = "SDXL LoRA Factory";
        }
    };
    
    ws.onclose = () => {
        consoleOut.innerHTML += '<br>--- WebSocket Disconnected ---';
    };
}

document.addEventListener('DOMContentLoaded', () => {
    ['dataset-path', 'model-path', 'vae-path', 'output-dir', 'lora-rank', 'lora-alpha'].forEach(id => {
        const saved = localStorage.getItem('sdxl_factory_saved_' + id);
        const el = document.getElementById(id);
        if (saved && el) el.value = saved;
        if (el) {
            el.addEventListener('change', (e) => {
                localStorage.setItem('sdxl_factory_saved_' + id, e.target.value);
            });
        }
    });

    ['auto-shutdown', 'enable-advanced'].forEach(id => {
        const saved = localStorage.getItem('sdxl_factory_saved_' + id);
        const el = document.getElementById(id);
        if (saved !== null && el) {
            el.checked = saved === 'true';
            if (id === 'enable-advanced') {
                toggleAdvancedSettings();
            }
        }
        if (el) {
            el.addEventListener('change', () => {
                localStorage.setItem('sdxl_factory_saved_' + id, el.checked);
            });
        }
    });
});