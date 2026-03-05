            // Initialize readiness chart
            const readinessCtx = document.getElementById('readinessChart').getContext('2d');
            
            // Clean up any existing chart
            if (currentChart) {
                currentChart.destroy();
            }
            
            currentChart = new Chart(readinessCtx, {
