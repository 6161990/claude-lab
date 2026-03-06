// document.js - 문서 생성 및 관리

async function generateDocument(type) {
    const data = getAnalysisData();

    if (!data) {
        alert('먼저 저장소를 분석해주세요.');
        return;
    }

    const apiEndpoint = document.getElementById('apiEndpoint').value.trim();
    const userName = document.getElementById('userName').value.trim();
    const quarter = document.getElementById('quarter').value;

    // 문서 생성 버튼들 비활성화
    const buttons = document.querySelectorAll('#results button');
    buttons.forEach(btn => {
        btn.disabled = true;
        btn.innerHTML = `
            <svg class="animate-spin h-5 w-5 mx-auto" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
        `;
    });

    try {
        // API 호출
        const response = await fetch(`${apiEndpoint}/api/generate/${type}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                analysisId: data.id,
                userName: userName,
                quarter: quarter,
                statistics: {
                    totalCommits: data.totalCommits,
                    totalFiles: data.totalFiles,
                    linesAdded: data.linesAdded,
                    linesDeleted: data.linesDeleted
                }
            })
        });

        if (!response.ok) {
            throw new Error(`문서 생성 실패: ${response.status}`);
        }

        const result = await response.json();
        displayGeneratedDocument(type, result.content);

    } catch (error) {
        console.error('문서 생성 오류:', error);
        alert(`문서 생성 중 오류가 발생했습니다: ${error.message}`);
    } finally {
        // 버튼 복원
        buttons.forEach((btn, index) => {
            btn.disabled = false;
            const labels = ['회고 생성', '이력서 생성', '피드백 받기'];
            btn.textContent = labels[index];
        });
    }
}

function displayGeneratedDocument(type, content) {
    const docSection = document.getElementById('generatedDocument');
    const docTitle = document.getElementById('docTitle');
    const docContent = document.getElementById('docContent');

    const titles = {
        'retrospective': '분기 회고',
        'resume': '이력서 프로젝트 설명',
        'feedback': '성장 피드백'
    };

    docTitle.textContent = titles[type] || '생성된 문서';
    docContent.textContent = content;

    docSection.classList.remove('hidden');
    docSection.scrollIntoView({ behavior: 'smooth' });
}

function copyDocument() {
    const content = document.getElementById('docContent').textContent;

    navigator.clipboard.writeText(content).then(() => {
        // 복사 완료 알림
        const btn = event.target.closest('button');
        const originalHTML = btn.innerHTML;

        btn.innerHTML = `
            <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
            </svg>
        `;

        setTimeout(() => {
            btn.innerHTML = originalHTML;
        }, 2000);
    }).catch(err => {
        alert('복사에 실패했습니다: ' + err);
    });
}
