// MSBTE Dashboard Charts with Modern Gradient & Donut Styling matching reference
document.addEventListener('DOMContentLoaded', function() {
    // Custom ChartJS Plugin to draw center text in Doughnut charts
    const centerTextPlugin = {
        id: 'centerTextPlugin',
        beforeDraw(chart) {
            if (chart.config.type !== 'doughnut') return;
            const { ctx, chartArea: { width, height, top, left } } = chart;
            const centerConfig = chart.config.options.plugins?.centerText;
            if (!centerConfig) return;

            ctx.save();
            const centerX = left + width / 2;
            const centerY = top + height / 2;

            // Draw Big Value
            ctx.font = 'bold 22px Outfit, sans-serif';
            ctx.fillStyle = '#0f172a';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText(centerConfig.value || '120', centerX, centerY - 8);

            // Draw Subtitle
            ctx.font = '500 11px Plus Jakarta Sans, sans-serif';
            ctx.fillStyle = '#64748b';
            ctx.fillText(centerConfig.label || 'Students', centerX, centerY + 14);

            ctx.restore();
        }
    };

    Chart.register(centerTextPlugin);

    fetch('/api/dashboard-charts')
        .then(response => response.json())
        .then(data => {
            // 1. Chart 1: Average Marks by Subject (Bar Chart with Rounded Gradient Bars)
            const ctx1 = document.getElementById('chartSubjectAvg');
            if (ctx1) {
                const chartCtx1 = ctx1.getContext('2d');
                const gradient1 = chartCtx1.createLinearGradient(0, 0, 0, 260);
                gradient1.addColorStop(0, '#3b82f6');
                gradient1.addColorStop(1, '#60a5fa');

                new Chart(ctx1, {
                    type: 'bar',
                    data: {
                        labels: data.chart1.labels,
                        datasets: [{
                            label: 'Average Score (%)',
                            data: data.chart1.data,
                            backgroundColor: gradient1,
                            borderRadius: 8,
                            borderSkipped: false,
                            barPercentage: 0.55
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: { display: false },
                            tooltip: {
                                backgroundColor: '#0f172a',
                                titleFont: { size: 12, family: 'Plus Jakarta Sans', weight: '700' },
                                bodyFont: { size: 11, family: 'Plus Jakarta Sans' },
                                padding: 10,
                                cornerRadius: 8,
                                callbacks: {
                                    label: function(context) {
                                        return ' ' + context.parsed.y + '% Average Marks';
                                    }
                                }
                            }
                        },
                        scales: {
                            y: {
                                beginAtZero: true,
                                max: 100,
                                grid: { color: '#f1f5f9' },
                                ticks: {
                                    font: { family: 'Plus Jakarta Sans', size: 10 },
                                    callback: v => v + '%'
                                }
                            },
                            x: {
                                grid: { display: false },
                                ticks: { font: { family: 'Plus Jakarta Sans', size: 10 } }
                            }
                        }
                    }
                });
            }

            // 2. Chart 2: Student Performance Categories (Doughnut with Center Text)
            const ctx2 = document.getElementById('chartPerformanceCategories');
            if (ctx2) {
                const totalStudents = data.chart2.data.reduce((a, b) => a + b, 0) || 120;
                new Chart(ctx2, {
                    type: 'doughnut',
                    data: {
                        labels: data.chart2.labels,
                        datasets: [{
                            data: data.chart2.data,
                            backgroundColor: [
                                '#10b981', // Excellent
                                '#3b82f6', // Good
                                '#06b6d4', // Average
                                '#f59e0b', // Needs Improvement
                                '#ef4444'  // At Risk
                            ],
                            borderWidth: 3,
                            borderColor: '#ffffff',
                            hoverOffset: 6
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        cutout: '72%',
                        plugins: {
                            legend: { display: false },
                            centerText: {
                                value: totalStudents.toString(),
                                label: 'Students'
                            },
                            tooltip: {
                                backgroundColor: '#0f172a',
                                padding: 10,
                                cornerRadius: 8
                            }
                        }
                    }
                });
            }

            // 3. Chart 3: Attendance Trend (Smooth Area Line Chart across Months)
            const ctx3 = document.getElementById('chartAttendanceDist');
            if (ctx3) {
                const chartCtx3 = ctx3.getContext('2d');
                const fillGradient = chartCtx3.createLinearGradient(0, 0, 0, 180);
                fillGradient.addColorStop(0, 'rgba(59, 130, 246, 0.2)');
                fillGradient.addColorStop(1, 'rgba(59, 130, 246, 0.0)');

                new Chart(ctx3, {
                    type: 'line',
                    data: {
                        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep'],
                        datasets: [{
                            label: 'Attendance %',
                            data: [72, 76, 75, 78, 77, 74, 73, 75, 74],
                            borderColor: '#3b82f6',
                            borderWidth: 2.5,
                            backgroundColor: fillGradient,
                            fill: true,
                            tension: 0.35,
                            pointRadius: 3,
                            pointBackgroundColor: '#3b82f6'
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: { display: false },
                            tooltip: {
                                backgroundColor: '#0f172a',
                                padding: 8,
                                cornerRadius: 6,
                                callbacks: { label: ctx => ` ${ctx.parsed.y}% Attendance` }
                            }
                        },
                        scales: {
                            y: {
                                min: 0,
                                max: 100,
                                grid: { color: '#f8fafc' },
                                ticks: { font: { size: 9 }, callback: v => v + '%' }
                            },
                            x: {
                                grid: { display: false },
                                ticks: { font: { size: 9 } }
                            }
                        }
                    }
                });
            }

            // 4. Chart 4: Pass vs Backlogs (Doughnut with Center Text)
            const ctx4 = document.getElementById('chartPassFail');
            if (ctx4) {
                const totalPassed = data.chart4.data[0] || 100;
                const totalBacklogs = data.chart4.data[1] || 20;
                const total = totalPassed + totalBacklogs;

                new Chart(ctx4, {
                    type: 'doughnut',
                    data: {
                        labels: ['Passed (No Backlogs)', 'Has Backlogs'],
                        datasets: [{
                            data: [totalPassed, totalBacklogs],
                            backgroundColor: ['#10b981', '#ef4444'],
                            borderWidth: 3,
                            borderColor: '#ffffff',
                            hoverOffset: 4
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        cutout: '72%',
                        plugins: {
                            legend: { display: false },
                            centerText: {
                                value: total.toString(),
                                label: 'Students'
                            },
                            tooltip: {
                                backgroundColor: '#0f172a',
                                padding: 8,
                                cornerRadius: 6
                            }
                        }
                    }
                });
            }

            // 5. Chart 5: Semester Wise Breakdown (Stacked Bar Chart)
            const ctx5 = document.getElementById('chartSemesterPerf');
            if (ctx5) {
                new Chart(ctx5, {
                    type: 'bar',
                    data: {
                        labels: ['Sem 1', 'Sem 2', 'Sem 3', 'Sem 4', 'Sem 5', 'Sem 6'],
                        datasets: [
                            {
                                label: 'Pass %',
                                data: [85, 82, 88, 80, 84, 86],
                                backgroundColor: '#3b82f6',
                                borderRadius: 4,
                                barPercentage: 0.5
                            },
                            {
                                label: 'Backlog %',
                                data: [15, 18, 12, 20, 16, 14],
                                backgroundColor: '#c084fc',
                                borderRadius: 4,
                                barPercentage: 0.5
                            }
                        ]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                position: 'bottom',
                                labels: {
                                    font: { family: 'Plus Jakarta Sans', size: 9 },
                                    boxWidth: 8,
                                    usePointStyle: true
                                }
                            },
                            tooltip: {
                                backgroundColor: '#0f172a',
                                padding: 8,
                                cornerRadius: 6
                            }
                        },
                        scales: {
                            x: { stacked: true, grid: { display: false }, ticks: { font: { size: 9 } } },
                            y: { stacked: true, max: 100, grid: { color: '#f8fafc' }, ticks: { font: { size: 9 }, callback: v => v + '%' } }
                        }
                    }
                });
            }
        })
        .catch(err => console.error('Error loading dashboard charts:', err));
});
