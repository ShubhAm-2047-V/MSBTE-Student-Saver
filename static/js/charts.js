// MSBTE Dashboard Charts with Modern Gradient Styling
document.addEventListener('DOMContentLoaded', function() {
    fetch('/api/dashboard-charts')
        .then(response => response.json())
        .then(data => {
            // Chart 1: Average Marks by Subject (Bar Chart with Gradient)
            const ctx1 = document.getElementById('chartSubjectAvg');
            if (ctx1) {
                const chartCtx1 = ctx1.getContext('2d');
                const gradient1 = chartCtx1.createLinearGradient(0, 0, 0, 300);
                gradient1.addColorStop(0, '#4f46e5');
                gradient1.addColorStop(1, '#3b82f6');

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
                            barPercentage: 0.6
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: { display: false },
                            tooltip: {
                                backgroundColor: '#0f172a',
                                titleFont: { size: 13, family: 'Plus Jakarta Sans', weight: '700' },
                                bodyFont: { size: 12, family: 'Plus Jakarta Sans' },
                                padding: 12,
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
                                    font: { family: 'Plus Jakarta Sans' },
                                    callback: v => v + '%'
                                }
                            },
                            x: {
                                grid: { display: false },
                                ticks: { font: { family: 'Plus Jakarta Sans', size: 11 } }
                            }
                        }
                    }
                });
            }

            // Chart 2: Student Performance Categories (Doughnut)
            const ctx2 = document.getElementById('chartPerformanceCategories');
            if (ctx2) {
                new Chart(ctx2, {
                    type: 'doughnut',
                    data: {
                        labels: data.chart2.labels,
                        datasets: [{
                            data: data.chart2.data,
                            backgroundColor: [
                                '#10b981', // Excellent
                                '#4f46e5', // Good
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
                        plugins: {
                            legend: {
                                position: 'bottom',
                                labels: {
                                    font: { family: 'Plus Jakarta Sans', size: 12, weight: '600' },
                                    padding: 15,
                                    usePointStyle: true,
                                    pointStyle: 'circle'
                                }
                            },
                            tooltip: {
                                backgroundColor: '#0f172a',
                                padding: 12,
                                cornerRadius: 8
                            }
                        },
                        cutout: '70%'
                    }
                });
            }

            // Chart 3: Attendance Breakdown
            const ctx3 = document.getElementById('chartAttendanceDist');
            if (ctx3) {
                new Chart(ctx3, {
                    type: 'bar',
                    data: {
                        labels: data.chart3.labels,
                        datasets: [{
                            label: 'Students',
                            data: data.chart3.data,
                            backgroundColor: ['#ef4444', '#f59e0b', '#3b82f6', '#10b981'],
                            borderRadius: 6,
                            barPercentage: 0.65
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: { display: false },
                            tooltip: {
                                backgroundColor: '#0f172a',
                                padding: 10,
                                cornerRadius: 8
                            }
                        },
                        scales: {
                            y: { beginAtZero: true, grid: { color: '#f1f5f9' } },
                            x: { grid: { display: false }, ticks: { font: { size: 10 } } }
                        }
                    }
                });
            }

            // Chart 4: Pass vs Fail
            const ctx4 = document.getElementById('chartPassFail');
            if (ctx4) {
                new Chart(ctx4, {
                    type: 'pie',
                    data: {
                        labels: data.chart4.labels,
                        datasets: [{
                            data: data.chart4.data,
                            backgroundColor: ['#10b981', '#ef4444'],
                            borderWidth: 2,
                            borderColor: '#ffffff'
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                position: 'bottom',
                                labels: {
                                    font: { family: 'Plus Jakarta Sans', size: 11 },
                                    usePointStyle: true
                                }
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

            // Chart 5: Semester Comparison
            const ctx5 = document.getElementById('chartSemesterPerf');
            if (ctx5) {
                const chartCtx5 = ctx5.getContext('2d');
                const gradient5 = chartCtx5.createLinearGradient(0, 0, 0, 200);
                gradient5.addColorStop(0, '#8b5cf6');
                gradient5.addColorStop(1, '#6d28d9');

                new Chart(ctx5, {
                    type: 'bar',
                    data: {
                        labels: data.chart5.labels,
                        datasets: [{
                            label: 'Average Score (%)',
                            data: data.chart5.data,
                            backgroundColor: gradient5,
                            borderRadius: 6,
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
                                padding: 10,
                                cornerRadius: 8
                            }
                        },
                        scales: {
                            y: {
                                beginAtZero: true,
                                max: 100,
                                grid: { color: '#f1f5f9' },
                                ticks: { callback: v => v + '%' }
                            },
                            x: { grid: { display: false } }
                        }
                    }
                });
            }
        })
        .catch(err => console.error('Error loading dashboard charts:', err));
});
