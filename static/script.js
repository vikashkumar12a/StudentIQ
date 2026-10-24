```javascript
// =====================================
// 1. GET DASHBOARD DATA
// =====================================

const dashboardData = window.dashboardData || {
    subjectLabels: [],
    subjectValues: [],
    passCount: 0,
    failCount: 0
};


// =====================================
// 2. CHECK CHART.JS
// =====================================

if (typeof Chart === "undefined") {
    console.error(
        "Chart.js is not loaded. Check the Chart.js CDN in index.html."
    );
} else {

    // Destroy existing chart before recreating it.
    function createChart(canvasId, config) {
        const canvas = document.getElementById(canvasId);

        if (!canvas) {
            console.warn(`Canvas not found: ${canvasId}`);
            return;
        }

        const existingChart = Chart.getChart(canvas);

        if (existingChart) {
            existingChart.destroy();
        }

        return new Chart(canvas, config);
    }


    // =====================================
    // 3. SUBJECT PERFORMANCE CHART
    // =====================================

    createChart("subjectChart", {
        type: "bar",

        data: {
            labels: dashboardData.subjectLabels,

            datasets: [{
                label: "Average Marks",
                data: dashboardData.subjectValues,

                backgroundColor: [
                    "#635bff",
                    "#3985f7",
                    "#16b981",
                    "#f5a742"
                ],

                borderRadius: 8,
                borderSkipped: false,
                maxBarThickness: 55
            }]
        },

        options: {
            responsive: true,
            maintainAspectRatio: false,

            plugins: {
                legend: {
                    display: false
                },

                tooltip: {
                    callbacks: {
                        label: function (context) {
                            return " Average Marks: " +
                                context.parsed.y;
                        }
                    }
                }
            },

            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,

                    ticks: {
                        stepSize: 20
                    }
                },

                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });


    // =====================================
    // 4. PASS VS FAIL DOUGHNUT CHART
    // =====================================

    createChart("resultChart", {
        type: "doughnut",

        data: {
            labels: ["Passed", "Failed"],

            datasets: [{
                data: [
                    Number(dashboardData.passCount) || 0,
                    Number(dashboardData.failCount) || 0
                ],

                backgroundColor: [
                    "#16b981",
                    "#ff7373"
                ],

                borderWidth: 0,
                hoverOffset: 8,
                spacing: 4
            }]
        },

        options: {
            responsive: true,
            maintainAspectRatio: false,

            cutout: "72%",

            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });


    // =====================================
    // 5. GRADE DISTRIBUTION CHART
    // =====================================

    if (
        Array.isArray(window.gradeLabels) &&
        Array.isArray(window.gradeValues)
    ) {
        createChart("gradeChart", {
            type: "bar",

            data: {
                labels: window.gradeLabels,

                datasets: [{
                    label: "Students",
                    data: window.gradeValues,

                    backgroundColor: [
                        "#16b981",
                        "#3985f7",
                        "#635bff",
                        "#f5a742",
                        "#ff7373",
                        "#dc2626"
                    ],

                    borderRadius: 6
                }]
            },

            options: {
                responsive: true,
                maintainAspectRatio: false,

                plugins: {
                    legend: {
                        display: false
                    }
                },

                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            precision: 0
                        }
                    }
                }
            }
        });
    }
}


// =====================================
// 6. CSV FILE NAME DISPLAY
// =====================================

const datasetInput = document.getElementById("dataset");
const fileNameDisplay = document.getElementById("fileName");

if (datasetInput && fileNameDisplay) {
    datasetInput.addEventListener("change", function () {
        if (this.files.length > 0) {
            fileNameDisplay.textContent =
                "Selected file: " + this.files[0].name;
        } else {
            fileNameDisplay.textContent = "Supported format: CSV";
        }
    });
}


// =====================================
// 7. SIDEBAR NAVIGATION
// =====================================

const navLinks = document.querySelectorAll(".nav-link");

navLinks.forEach(function (link) {
    link.addEventListener("click", function () {
        navLinks.forEach(function (item) {
            item.classList.remove("active");
        });

        this.classList.add("active");
    });
});


// =====================================
// 8. DEBUG INFORMATION
// =====================================

console.log("StudentIQ dashboard loaded.");
console.log("Dashboard data:", dashboardData);
```
