// This is a placeholder that does nothing so we don't get console errors on pages that don't use the map
console.log('Main.js loaded - generic version');

// These functions need to be available globally
function closeHercStats() {
    const modal = bootstrap.Modal.getInstance(document.getElementById('hercModal'));
    if (modal) {
        modal.hide();
    }
}

function showWemStats(regionId) {
    fetch(`/wem-data/${regionId}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Error:', data.error);
                return;
            }
            
            const modalContent = `
                <div class="modal fade" id="wemModal" tabindex="-1" aria-hidden="true">
                    <div class="modal-dialog modal-lg">
                        <div class="modal-content">
                            <div class="modal-header bg-danger text-white">
                                <h5 class="modal-title">WEM Region ${regionId}</h5>
                                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                            </div>
                            <div class="modal-body">
                                <div class="row">
                                    <div class="col-md-6">
                                        <h6>Emergency Management Metrics</h6>
                                        <ul class="list-group mb-3">
                                            <li class="list-group-item d-flex justify-content-between align-items-center">
                                                Disaster Preparedness
                                                <span class="badge bg-${data.metrics.preparedness_score > 0.7 ? 'success' : 'warning'} rounded-pill">
                                                    ${(data.metrics.preparedness_score * 100).toFixed(1)}%
                                                </span>
                                            </li>
                                            <li class="list-group-item d-flex justify-content-between align-items-center">
                                                Mitigation Projects Active
                                                <span class="badge bg-primary rounded-pill">${data.metrics.mitigation_projects}</span>
                                            </li>
                                            <li class="list-group-item d-flex justify-content-between align-items-center">
                                                Recovery Capacity
                                                <span class="badge bg-${data.metrics.recovery_capacity > 0.6 ? 'success' : 'warning'} rounded-pill">
                                                    ${(data.metrics.recovery_capacity * 100).toFixed(1)}%
                                                </span>
                                            </li>
                                            <li class="list-group-item d-flex justify-content-between align-items-center">
                                                Training Exercises (Annual)
                                                <span class="badge bg-primary rounded-pill">${data.metrics.training_exercises}</span>
                                            </li>
                                        </ul>
                                    </div>
                                    <div class="col-md-6">
                                        <h6>Resources & Infrastructure</h6>
                                        <ul class="list-group mb-3">
                                            <li class="list-group-item d-flex justify-content-between align-items-center">
                                                Emergency Shelters
                                                <span class="badge bg-primary rounded-pill">${data.resources.shelters}</span>
                                            </li>
                                            <li class="list-group-item d-flex justify-content-between align-items-center">
                                                Shelter Capacity
                                                <span class="badge bg-primary rounded-pill">${data.resources.shelter_capacity} people</span>
                                            </li>
                                            <li class="list-group-item d-flex justify-content-between align-items-center">
                                                Emergency Response Units
                                                <span class="badge bg-primary rounded-pill">${data.resources.response_units}</span>
                                            </li>
                                            <li class="list-group-item d-flex justify-content-between align-items-center">
                                                Critical Infrastructure Sites
                                                <span class="badge bg-primary rounded-pill">${data.resources.critical_sites}</span>
                                            </li>
                                        </ul>
                                    </div>
                                </div>
                                <div class="row mt-3">
                                    <div class="col-12">
                                        <h6>Emergency Readiness Assessment</h6>
                                        <div class="progress" style="height: 25px;">
                                            <div class="progress-bar bg-${data.readiness_score > 0.7 ? 'success' : data.readiness_score > 0.4 ? 'warning' : 'danger'}" 
                                                 role="progressbar" 
                                                 style="width: ${data.readiness_score * 100}%" 
                                                 aria-valuenow="${data.readiness_score * 100}" 
                                                 aria-valuemin="0" 
                                                 aria-valuemax="100">
                                                ${(data.readiness_score * 100).toFixed(1)}%
                                            </div>
                                        </div>
                                        <p class="mt-2 small">${data.assessment_notes}</p>
                                    </div>
                                </div>
                                <div class="row mt-3">
                                    <div class="col-12">
                                        <h6>Recent Emergency Declarations</h6>
                                        <ul class="list-group">
                                            ${data.recent_declarations.map(declaration => `
                                                <li class="list-group-item">
                                                    <div class="d-flex w-100 justify-content-between">
                                                        <h6 class="mb-1">${declaration.type}</h6>
                                                        <small>${declaration.date}</small>
                                                    </div>
                                                    <p class="mb-1">${declaration.description}</p>
                                                </li>
                                            `).join('')}
                                        </ul>
                                    </div>
                                </div>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal" onclick="closeWemStats()">Close</button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            // Remove existing modal if any
            const existingModal = document.getElementById('wemModal');
            if (existingModal) {
                existingModal.remove();
            }
            
            // Add modal to document
            document.body.insertAdjacentHTML('beforeend', modalContent);
            
            // Initialize and show modal
            const modal = new bootstrap.Modal(document.getElementById('wemModal'));
            modal.show();
        })
        .catch(error => {
            console.error('Error fetching WEM data:', error);
        });
}

function closeWemStats() {
    const modal = bootstrap.Modal.getInstance(document.getElementById('wemModal'));
    if (modal) {
        modal.hide();
    }
}

function showHercStats(regionId) {
    fetch(`/herc-data/${regionId}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Error:', data.error);
                return;
            }
            
            const modalContent = `
                <div class="modal fade" id="hercModal" tabindex="-1" aria-hidden="true">
                    <div class="modal-dialog modal-lg">
                        <div class="modal-content">
                            <div class="modal-header bg-primary text-white">
                                <h5 class="modal-title">HERC Region ${regionId}</h5>
                                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                            </div>
                            <div class="modal-body">
                                <div class="row">
                                    <div class="col-md-6">
                                        <h6>Healthcare Facility Metrics</h6>
                                        <ul class="list-group mb-3">
                                            <li class="list-group-item d-flex justify-content-between align-items-center">
                                                Hospital Bed Capacity
                                                <span class="badge bg-primary rounded-pill">${data.metrics.hospital_beds}</span>
                                            </li>
                                            <li class="list-group-item d-flex justify-content-between align-items-center">
                                                ICU Beds
                                                <span class="badge bg-primary rounded-pill">${data.metrics.icu_beds}</span>
                                            </li>
                                            <li class="list-group-item d-flex justify-content-between align-items-center">
                                                Bed Availability
                                                <span class="badge bg-${data.metrics.bed_availability > 0.2 ? 'success' : 'danger'} rounded-pill">
                                                    ${(data.metrics.bed_availability * 100).toFixed(1)}%
                                                </span>
                                            </li>
                                            <li class="list-group-item d-flex justify-content-between align-items-center">
                                                Ventilators
                                                <span class="badge bg-primary rounded-pill">${data.metrics.ventilators}</span>
                                            </li>
                                        </ul>
                                    </div>
                                    <div class="col-md-6">
                                        <h6>Regional Healthcare Resources</h6>
                                        <ul class="list-group mb-3">
                                            <li class="list-group-item d-flex justify-content-between align-items-center">
                                                Hospitals
                                                <span class="badge bg-primary rounded-pill">${data.resources.hospitals}</span>
                                            </li>
                                            <li class="list-group-item d-flex justify-content-between align-items-center">
                                                Urgent Care Centers
                                                <span class="badge bg-primary rounded-pill">${data.resources.urgent_care}</span>
                                            </li>
                                            <li class="list-group-item d-flex justify-content-between align-items-center">
                                                EMS Agencies
                                                <span class="badge bg-primary rounded-pill">${data.resources.ems_agencies}</span>
                                            </li>
                                            <li class="list-group-item d-flex justify-content-between align-items-center">
                                                Public Health Departments
                                                <span class="badge bg-primary rounded-pill">${data.resources.health_departments}</span>
                                            </li>
                                        </ul>
                                    </div>
                                </div>
                                <div class="row mt-3">
                                    <div class="col-12">
                                        <h6>Healthcare Emergency Readiness</h6>
                                        <div class="progress" style="height: 25px;">
                                            <div class="progress-bar bg-${data.readiness_score > 0.7 ? 'success' : data.readiness_score > 0.4 ? 'warning' : 'danger'}" 
                                                 role="progressbar" 
                                                 style="width: ${data.readiness_score * 100}%" 
                                                 aria-valuenow="${data.readiness_score * 100}" 
                                                 aria-valuemin="0" 
                                                 aria-valuemax="100">
                                                ${(data.readiness_score * 100).toFixed(1)}%
                                            </div>
                                        </div>
                                        <p class="mt-2 small">${data.assessment_notes}</p>
                                    </div>
                                </div>
                                <div class="row mt-3">
                                    <div class="col-md-6">
                                        <h6>Population Demographics</h6>
                                        <ul class="list-group">
                                            <li class="list-group-item d-flex justify-content-between align-items-center">
                                                Total Population
                                                <span class="badge bg-secondary rounded-pill">${data.demographics.population.toLocaleString()}</span>
                                            </li>
                                            <li class="list-group-item d-flex justify-content-between align-items-center">
                                                Over 65 Years
                                                <span class="badge bg-secondary rounded-pill">${data.demographics.over65.toLocaleString()} (${data.demographics.over65_pct}%)</span>
                                            </li>
                                            <li class="list-group-item d-flex justify-content-between align-items-center">
                                                Under 18 Years
                                                <span class="badge bg-secondary rounded-pill">${data.demographics.under18.toLocaleString()} (${data.demographics.under18_pct}%)</span>
                                            </li>
                                        </ul>
                                    </div>
                                    <div class="col-md-6">
                                        <h6>Training & Exercises</h6>
                                        <ul class="list-group">
                                            <li class="list-group-item d-flex justify-content-between align-items-center">
                                                Full Scale Exercises (Annual)
                                                <span class="badge bg-primary rounded-pill">${data.training.full_scale}</span>
                                            </li>
                                            <li class="list-group-item d-flex justify-content-between align-items-center">
                                                Tabletop Exercises (Annual)
                                                <span class="badge bg-primary rounded-pill">${data.training.tabletop}</span>
                                            </li>
                                            <li class="list-group-item d-flex justify-content-between align-items-center">
                                                Healthcare Staff Trained
                                                <span class="badge bg-primary rounded-pill">${data.training.staff_trained.toLocaleString()}</span>
                                            </li>
                                        </ul>
                                    </div>
                                </div>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal" onclick="closeHercStats()">Close</button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            // Remove existing modal if any
            const existingModal = document.getElementById('hercModal');
            if (existingModal) {
                existingModal.remove();
            }
            
            // Add modal to document
            document.body.insertAdjacentHTML('beforeend', modalContent);
            
            // Initialize and show modal
            const modal = new bootstrap.Modal(document.getElementById('hercModal'));
            modal.show();
        })
        .catch(error => {
            console.error('Error fetching HERC data:', error);
        });
}
