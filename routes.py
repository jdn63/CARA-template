"""
CARA Template — URL routes.

This file registers all routes with the Flask application. Routes are organized
into logical groups using Flask blueprints. Copy this pattern to add new pages.

For a full-featured deployment, you will want to adapt the routes from the
Wisconsin implementation (routes/ directory) to use the template's
jurisdiction_manager and connector_registry.
"""

import logging
import os
import yaml
from flask import Flask, render_template, jsonify, redirect, url_for
from utils.geography.jurisdiction_manager import JurisdictionManager
from utils.risk_engine import load_weights, calculate_phrat, classify_risk, compute_all_domains

logger = logging.getLogger(__name__)


def register_routes(app: Flask) -> None:
    """Register all URL routes with the Flask application."""

    @app.route('/')
    def index():
        """Home page — jurisdiction selection."""
        try:
            manager = JurisdictionManager()
            jurisdictions = manager.get_all()
            config = manager.get_country_config()
            return render_template(
                'index.html',
                jurisdictions=jurisdictions,
                jurisdiction_name=config.get('name', 'CARA'),
            )
        except Exception as e:
            logger.error(f"Index route error: {e}")
            return render_template('error.html', message=str(e)), 500

    @app.route('/dashboard/<jurisdiction_id>')
    def dashboard(jurisdiction_id: str):
        """Main risk assessment dashboard for a jurisdiction."""
        try:
            manager = JurisdictionManager()
            jurisdiction = manager.get_by_id(jurisdiction_id)
            if not jurisdiction:
                return render_template('error.html',
                                       message=f"Jurisdiction '{jurisdiction_id}' not found"), 404

            profile = os.environ.get('CARA_PROFILE', 'international')
            jconfig_path = os.path.join('config', 'jurisdiction.yaml')
            with open(jconfig_path, 'r') as f:
                jconfig = yaml.safe_load(f) or {}

            from utils.connector_registry import ConnectorRegistry
            registry = ConnectorRegistry(profile=profile, jurisdiction_config=jconfig)
            connector_data = {}
            for name, connector in registry.get_all_available().items():
                connector_data[name] = connector.fetch(jurisdiction_id)

            domain_results = compute_all_domains(
                connector_data=connector_data,
                jurisdiction_config=jconfig,
                profile=profile,
            )

            weights = load_weights(
                profile=profile,
                jurisdiction_overrides=jconfig.get('overrides', {}).get('weights'),
            )
            domain_scores = {k: v.get('score', 0.0) for k, v in domain_results.items()}
            total_score, breakdown = calculate_phrat(domain_scores, weights)
            risk_class = classify_risk(total_score)

            regional_group = manager.get_group_for_jurisdiction(jurisdiction_id)

            return render_template(
                'dashboard.html',
                jurisdiction=jurisdiction,
                total_score=total_score,
                risk_level=risk_class,
                domain_results=domain_results,
                breakdown=breakdown,
                profile=profile,
                regional_group=regional_group,
            )
        except Exception as e:
            logger.error(f"Dashboard error for {jurisdiction_id}: {e}", exc_info=True)
            return render_template('error.html', message=str(e)), 500

    @app.route('/api/status')
    def api_status():
        """Health check endpoint."""
        return jsonify({'status': 'ok', 'version': _get_version()})

    @app.route('/health')
    def health():
        """Render health check for deployment platforms."""
        return 'OK', 200

    @app.route('/methodology')
    def methodology():
        """Methodology documentation page."""
        profile = os.environ.get('CARA_PROFILE', 'international')
        framework = _load_framework(profile)
        return render_template('methodology.html', profile=profile, framework=framework)

    @app.route('/about')
    def about():
        """About and attribution page."""
        return render_template('about.html')

    @app.errorhandler(404)
    def not_found(e):
        return render_template('error.html', message='Page not found'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('error.html', message='Internal server error'), 500


def _get_version() -> str:
    if os.path.exists('VERSION.txt'):
        with open('VERSION.txt') as f:
            return f.read().strip()
    return '0.1.0'


def _load_framework(profile: str):
    try:
        if profile == 'who_ihr' or profile == 'international':
            from utils.frameworks.who_ihr import WHOIHRFramework
            return WHOIHRFramework()
        else:
            from utils.frameworks.cdc_phep import CDCPHEPFramework
            return CDCPHEPFramework()
    except Exception:
        return None
