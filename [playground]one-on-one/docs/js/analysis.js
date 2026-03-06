// analysis.js - 분석 결과 표시 및 차트 렌더링

let analysisData = null;
let commitChart = null;

function displayAnalysisResults(data) {
    analysisData = data;

    // 결과 영역 표시
    const resultsSection = document.getElementById('results');
    resultsSection.classList.remove('hidden');

    // 통계 업데이트
    document.getElementById('statCommits').textContent = data.totalCommits || 0;
    document.getElementById('statFiles').textContent = data.totalFiles || 0;
    document.getElementById('statAdded').textContent = formatNumber(data.linesAdded || 0);
    document.getElementById('statDeleted').textContent = formatNumber(data.linesDeleted || 0);

    // 차트 렌더링
    renderCommitChart(data);

    // 결과로 스크롤
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
}

function renderCommitChart(data) {
    const ctx = document.getElementById('commitChart').getContext('2d');

    // 기존 차트가 있으면 제거
    if (commitChart) {
        commitChart.destroy();
    }

    // 날짜별 커밋 데이터 준비 (예시)
    // 실제로는 백엔드에서 날짜별 통계를 받아와야 함
    const labels = data.commitsByDate ? Object.keys(data.commitsByDate) : ['Week 1', 'Week 2', 'Week 3', 'Week 4'];
    const commitCounts = data.commitsByDate ? Object.values(data.commitsByDate) : [5, 12, 8, 15];

    commitChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: '커밋 수',
                data: commitCounts,
                borderColor: 'rgb(59, 130, 246)',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: '시간별 커밋 활동',
                    font: {
                        size: 16
                    }
                },
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
}

// 분석 데이터 조회 함수 (문서 생성 시 사용)
function getAnalysisData() {
    return analysisData;
}
