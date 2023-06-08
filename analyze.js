// 연간/분기 차트 생성
const financeSetChart = (className, labels, datas)=>{
    const ctx = document.querySelector(className).getContext('2d');
    const myChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: '매출액',
                data: datas[0],
                backgroundColor: 'rgba(16, 163, 127, 0.2)',
                borderColor: 'rgba(16, 163, 127, 1)',
                borderWidth: 1,
                yAxisID: 'y1',
                type: 'bar'
            }, {
                label: '영업이익률',
                data: datas[1],
                backgroundColor: 'rgba(194, 30, 86, 0.2)',
                borderColor: 'rgba(194, 30, 86, 1)',
                borderWidth: 1,
                yAxisID: 'y2',
            }, {
                label: '순이익률',
                data: datas[2],
                backgroundColor: 'rgba(0, 0, 128, 0.2)',
                borderColor: 'rgba(0, 0, 128, 1)',
                borderWidth: 1,
                yAxisID: 'y2',
            }]
        },
        options: {
            scales: {
                y1: {
                    position: 'left',
                    ticks: {
                            callback: function(value, index, ticks) {
                                return `${value.toLocaleString()}억원`;
                            }
                        }
                },
                y2: {
                    beginAtZero: true,
                    position: 'right',
                    grid: {
                        drawOnChartArea: false,
                    },
                    ticks: {
                        callback: function(value, index, ticks) {
                            return `${value.toLocaleString()}%`;
                        }
                    }
                }
            }
        }
    });
}
