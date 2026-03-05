/**
 * Legacy Browser Support for CARA Platform
 * 
 * Provides basic functionality for browsers that don't support ES6 modules.
 * This is a fallback implementation of core features.
 */

// Only load if ES6 modules are not supported
if (typeof window.moduleSupported === 'undefined') {
    console.log('Loading legacy browser support');

    // Basic localStorage utilities
    function setSelectedJurisdiction(id, name) {
        localStorage.setItem('selectedJurisdictionId', id);
        localStorage.setItem('selectedJurisdictionName', name);
    }

    function getSelectedJurisdiction() {
        var id = localStorage.getItem('selectedJurisdictionId');
        var name = localStorage.getItem('selectedJurisdictionName');
        return id && name ? { id: id, name: name } : null;
    }

    // Basic risk utilities
    function getRiskLevel(score) {
        if (score < 0.3) return 'Low';
        if (score < 0.6) return 'Medium';
        return 'High';
    }

    function getRiskColor(level) {
        switch (level) {
            case 'Low': return 'success';
            case 'Medium': return 'warning';
            case 'High': return 'danger';
            default: return 'secondary';
        }
    }

    function getColorForRisk(score) {
        return score > 0.6 ? '#dc3545' :  // High risk - red
               score > 0.3 ? '#ffc107' :  // Medium risk - yellow
                            '#28a745';    // Low risk - green
    }

    // Basic navigation functions
    function selectJurisdiction(jurisdictionId, jurisdictionName) {
        if (jurisdictionId) {
            setSelectedJurisdiction(jurisdictionId, jurisdictionName);
            updateNavbarDisplay();
            window.location.href = '/dashboard/' + jurisdictionId;
        }
    }

    function selectHercRegion(hercId, hercName) {
        if (hercId) {
            localStorage.setItem('selectedHercId', hercId);
            localStorage.setItem('selectedHercName', hercName);
            window.location.href = '/herc-dashboard/' + hercId;
        }
    }

    // Update navbar display
    function updateNavbarDisplay() {
        var jurisdiction = getSelectedJurisdiction();
        var display = document.getElementById('jurisdiction-display');
        
        if (display && jurisdiction) {
            display.innerHTML = jurisdiction.name;
        } else if (display) {
            display.innerHTML = '';
        }
    }

    // Return to top functionality
    function setupReturnToTop() {
        var button = document.getElementById('return-to-top');
        if (!button) return;

        window.addEventListener('scroll', function() {
            if (window.pageYOffset > 200) {
                button.style.display = 'flex';
                button.classList.remove('d-none');
            } else {
                button.style.display = 'none';
                button.classList.add('d-none');
            }
        });

        button.addEventListener('click', function(e) {
            e.preventDefault();
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }

    // Initialize when DOM is ready
    document.addEventListener('DOMContentLoaded', function() {
        updateNavbarDisplay();
        setupReturnToTop();
        
        // Dashboard-specific initialization
        if (typeof window.templateData !== 'undefined') {
            setSelectedJurisdiction(
                window.templateData.jurisdictionId,
                window.templateData.jurisdictionName
            );
            updateNavbarDisplay();
        }
    });

    // Make functions available globally
    window.selectJurisdiction = selectJurisdiction;
    window.selectHercRegion = selectHercRegion;
    window.getRiskLevel = getRiskLevel;
    window.getRiskColor = getRiskColor;
    window.getColorForRisk = getColorForRisk;

    console.log('Legacy browser support loaded');
}