// =====================================
// 1. GET DATA FROM FLASK / PYTHON
// =====================================

const dashboardData = window.dashboardData || {
    subjectLabels: [],
    subjectValues: [],
    passCount: 0,
    failCount: 0
};


// =====================================
// 2. SUBJECT PERFORMANCE BAR CHART
// =====================================

const subjectCanvas = document.getElementById("subjectChart");

if (subjectCanvas) {
    new Chart(subjectCanvas, {
        type: "bar",

        data: {
            labels: dashboardData.subjectLabels,

            datasets: [
                {
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
                }
            ]
        },

        options: {
            responsive: true,

            maintainAspectRatio: false,

            plugins: {
                legend: {
                    display: false
                },

                tooltip: {
                    backgroundColor: "#171a2f",

                    padding: 12,

                    callbacks: {
                        label: function (context) {
                            return " Average Marks: " + context.parsed.y;
                        }
                    }
                }
            },

            scales: {
                y: {
                    beginAtZero: true,

                    max: 100,

                    ticks: {
                        stepSize: 20,

                        color: "#858ba3",

                        font: {
                            size: 11
                        }
                    },

                    grid: {
                        color: "#edf0f6",

                        drawBorder: false
                    },

                    border: {
                        display: false
                    }
                },

                x: {
                    ticks: {
                        color: "#626981",

                        font: {
                            size: 11
                        }
                    },

                    grid: {
                        display: false
                    },

                    border: {
                        display: false
                    }
                }
            }
        }
    });
}


// =====================================
// 3. PASS VS FAIL DOUGHNUT CHART
// =====================================

const resultCanvas = document.getElementById("resultChart");

if (resultCanvas) {
    new Chart(resultCanvas, {
        type: "doughnut",

        data: {
            labels: ["Passed", "Failed"],

            datasets: [
                {
                    data: [
                        dashboardData.passCount,
                        dashboardData.failCount
                    ],

                    backgroundColor: [
                        "#16b981",
                        "#ff7373"
                    ],

                    borderWidth: 0,

                    hoverOffset: 8,

                    spacing: 4
                }
            ]
        },

        options: {
            responsive: true,

            maintainAspectRatio: false,

            cutout: "72%",

            plugins: {
                legend: {
                    display: false
                },

                tooltip: {
                    backgroundColor: "#171a2f",

                    padding: 12
                }
            }
        }
    });
}


// =====================================
// 4. CSV FILE NAME DISPLAY
// =====================================

const datasetInput = document.getElementById("dataset");

const fileNameDisplay = document.getElementById("fileName");

if (datasetInput && fileNameDisplay) {

    datasetInput.addEventListener("change", function () {

        if (this.files.length > 0) {

            const selectedFile = this.files[0];

            fileNameDisplay.textContent =
                "Selected file: " + selectedFile.name;

        } else {

            fileNameDisplay.textContent =
                "Supported format: CSV";

        }

    });

}


// =====================================
// 5. SIDEBAR ACTIVE NAVIGATION
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
// 6. DASHBOARD LOADED
// =====================================

console.log("Student Performance Analyzer loaded successfully.");

console.log("Subject data:", dashboardData.subjectValues);

console.log("Passed students:", dashboardData.passCount);

console.log("Failed students:", dashboardData.failCount);