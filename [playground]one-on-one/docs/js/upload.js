// upload.js - 파일 업로드 및 드래그앤드롭 처리

let selectedFiles = [];

// DOM 요소
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const fileList = document.getElementById('fileList');
const analyzeBtn = document.getElementById('analyzeBtn');
const userName = document.getElementById('userName');

// 드래그앤드롭 이벤트
['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    dropZone.addEventListener(eventName, preventDefaults, false);
});

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

['dragenter', 'dragover'].forEach(eventName => {
    dropZone.addEventListener(eventName, () => {
        dropZone.classList.add('border-blue-500', 'bg-blue-50');
    }, false);
});

['dragleave', 'drop'].forEach(eventName => {
    dropZone.addEventListener(eventName, () => {
        dropZone.classList.remove('border-blue-500', 'bg-blue-50');
    }, false);
});

dropZone.addEventListener('drop', handleDrop, false);
dropZone.addEventListener('click', () => fileInput.click());

function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    handleFiles(files);
}

fileInput.addEventListener('change', (e) => {
    handleFiles(e.target.files);
});

function handleFiles(files) {
    const zipFiles = Array.from(files).filter(file => file.name.endsWith('.zip'));

    if (zipFiles.length === 0) {
        alert('ZIP 파일만 업로드할 수 있습니다.');
        return;
    }

    selectedFiles = [...selectedFiles, ...zipFiles];
    displayFileList();
    updateAnalyzeButton();
}

function displayFileList() {
    if (selectedFiles.length === 0) {
        fileList.innerHTML = '';
        return;
    }

    fileList.innerHTML = `
        <div class="border border-gray-200 rounded-lg p-4">
            <h4 class="font-semibold mb-2">선택된 파일 (${selectedFiles.length}개)</h4>
            <ul class="space-y-2">
                ${selectedFiles.map((file, index) => `
                    <li class="flex justify-between items-center text-sm">
                        <span class="text-gray-700">
                            <svg class="w-4 h-4 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"></path>
                            </svg>
                            ${file.name}
                        </span>
                        <button onclick="removeFile(${index})" class="text-red-600 hover:text-red-800">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                            </svg>
                        </button>
                    </li>
                `).join('')}
            </ul>
        </div>
    `;
}

function removeFile(index) {
    selectedFiles.splice(index, 1);
    displayFileList();
    updateAnalyzeButton();
}

function updateAnalyzeButton() {
    const hasFiles = selectedFiles.length > 0;
    const hasUserName = userName.value.trim().length > 0;
    analyzeBtn.disabled = !(hasFiles && hasUserName);
}

// 사용자 이름 입력 감지
userName.addEventListener('input', updateAnalyzeButton);

// 분석 시작 버튼
analyzeBtn.addEventListener('click', async () => {
    const userNameValue = userName.value.trim();
    const quarter = document.getElementById('quarter').value;
    const apiEndpoint = document.getElementById('apiEndpoint').value.trim();

    if (!apiEndpoint) {
        alert('백엔드 API URL을 입력해주세요.');
        return;
    }

    if (selectedFiles.length === 0 || !userNameValue) {
        alert('파일과 사용자 이름을 모두 입력해주세요.');
        return;
    }

    // 로딩 표시
    analyzeBtn.disabled = true;
    analyzeBtn.innerHTML = `
        <svg class="animate-spin h-5 w-5 mx-auto" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        분석 중...
    `;

    try {
        // FormData 생성
        const formData = new FormData();
        selectedFiles.forEach(file => {
            formData.append('repositories', file);
        });
        formData.append('userName', userNameValue);
        formData.append('quarter', quarter);

        // API 호출
        const response = await fetch(`${apiEndpoint}/api/analyze`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`서버 오류: ${response.status}`);
        }

        const result = await response.json();

        // 분석 결과 표시
        displayAnalysisResults(result);

    } catch (error) {
        console.error('분석 실패:', error);
        alert(`분석 중 오류가 발생했습니다: ${error.message}\n\n백엔드 서버가 실행 중인지 확인해주세요.`);
    } finally {
        // 버튼 복원
        analyzeBtn.disabled = false;
        analyzeBtn.textContent = '분석 시작';
    }
});

function scrollToUpload() {
    document.getElementById('upload').scrollIntoView({ behavior: 'smooth' });
}
