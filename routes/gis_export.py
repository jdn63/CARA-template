"""
GIS Export Routes for CARA Risk Assessment Data

This module provides Flask routes for downloading risk assessment data
in CSV and GeoJSON formats for use in ArcGIS and other GIS platforms.
"""

import os
import logging
from datetime import datetime
from flask import Blueprint, send_file, jsonify, request, abort
from werkzeug.exceptions import NotFound

from core import db
from models import ExportJob
from utils.gis_export import CARAGISExporter

logger = logging.getLogger(__name__)

# Create blueprint for GIS export routes
gis_export_bp = Blueprint('gis_export', __name__, url_prefix='/api/gis')

@gis_export_bp.route('/export/all', methods=['GET', 'POST'])
def export_all_data():
    """
    Start an asynchronous export job for all jurisdiction risk data.
    
    Returns job ID for status polling and eventual download.
    """
    try:
        logger.info("Starting async GIS data export job")
        
        # Create new export job
        job = ExportJob(
            export_type='all_jurisdictions',
            status='queued',
            cache_freshness_minutes=30,
            params={}
        )
        
        db.session.add(job)
        db.session.commit()
        
        logger.info(f"Created export job {job.id}")
        
        return jsonify({
            'status': 'job_created',
            'job_id': str(job.id),
            'message': 'Export job started. Use the job_id to check progress.',
            'status_url': f"/api/gis/jobs/{job.id}/status",
            'estimated_duration_minutes': 5
        })
        
    except Exception as e:
        logger.error(f"Error creating GIS export job: {e}")
        return jsonify({
            'error': 'Failed to create export job',
            'message': 'An internal error occurred. Please try again.'
        }), 500

@gis_export_bp.route('/download/csv/<filename>', methods=['GET'])
def download_csv(filename):
    """
    Download a specific CSV export file.
    
    Args:
        filename: Name of the CSV file to download
    """
    try:
        from werkzeug.utils import secure_filename
        
        # Sanitize filename to prevent path traversal
        safe_filename = secure_filename(filename)
        if not safe_filename or safe_filename != filename:
            logger.warning(f"Invalid filename rejected: {filename}")
            abort(400, description="Invalid filename")
        
        # Reject any path separators
        if '/' in filename or '\\' in filename or '..' in filename:
            logger.warning(f"Path traversal attempt rejected: {filename}")
            abort(400, description="Invalid filename")
        
        # Validate filename and path
        if not safe_filename.endswith('.csv'):
            abort(400, description="Invalid file type. Only CSV files are supported.")
        
        # Construct file path
        export_dir = 'exports'
        file_path = os.path.join(export_dir, safe_filename)
        
        # Ensure resolved path is within exports directory
        real_file_path = os.path.realpath(file_path)
        real_export_dir = os.path.realpath(export_dir)
        if not real_file_path.startswith(real_export_dir):
            logger.warning(f"Path traversal attempt blocked: {filename} -> {real_file_path}")
            abort(403, description="Access denied")
        
        if not os.path.exists(real_file_path):
            logger.warning(f"Requested CSV file not found: {real_file_path}")
            abort(404, description="Export file not found. Please regenerate the export.")
        
        logger.info(f"Serving CSV download: {filename}")
        
        return send_file(
            real_file_path,
            as_attachment=True,
            download_name=safe_filename,
            mimetype='text/csv'
        )
        
    except NotFound:
        raise
    except Exception as e:
        logger.error(f"Error serving CSV file {filename}: {e}")
        abort(500, description="Error retrieving export file")

@gis_export_bp.route('/download/geojson/<filename>', methods=['GET'])
def download_geojson(filename):
    """
    Download a specific GeoJSON export file.
    
    Args:
        filename: Name of the GeoJSON file to download
    """
    try:
        from werkzeug.utils import secure_filename
        
        # Sanitize filename to prevent path traversal
        safe_filename = secure_filename(filename)
        if not safe_filename or safe_filename != filename:
            logger.warning(f"Invalid filename rejected: {filename}")
            abort(400, description="Invalid filename")
        
        # Reject any path separators
        if '/' in filename or '\\' in filename or '..' in filename:
            logger.warning(f"Path traversal attempt rejected: {filename}")
            abort(400, description="Invalid filename")
        
        # Validate filename and path
        if not safe_filename.endswith('.geojson'):
            abort(400, description="Invalid file type. Only GeoJSON files are supported.")
        
        # Construct file path
        export_dir = 'exports'
        file_path = os.path.join(export_dir, safe_filename)
        
        # Ensure resolved path is within exports directory
        real_file_path = os.path.realpath(file_path)
        real_export_dir = os.path.realpath(export_dir)
        if not real_file_path.startswith(real_export_dir):
            logger.warning(f"Path traversal attempt blocked: {filename} -> {real_file_path}")
            abort(403, description="Access denied")
        
        if not os.path.exists(real_file_path):
            logger.warning(f"Requested GeoJSON file not found: {real_file_path}")
            abort(404, description="Export file not found. Please regenerate the export.")
        
        logger.info(f"Serving GeoJSON download: {filename}")
        
        return send_file(
            real_file_path,
            as_attachment=True,
            download_name=safe_filename,
            mimetype='application/geo+json'
        )
        
    except NotFound:
        raise
    except Exception as e:
        logger.error(f"Error serving GeoJSON file {filename}: {e}")
        abort(500, description="Error retrieving export file")

@gis_export_bp.route('/export/jurisdiction/<jurisdiction_id>', methods=['GET', 'POST'])
def export_single_jurisdiction(jurisdiction_id):
    """
    Start an asynchronous export job for a single jurisdiction.
    
    Args:
        jurisdiction_id: ID of the jurisdiction to export
    """
    try:
        logger.info(f"Starting async export job for jurisdiction: {jurisdiction_id}")
        
        # Create new export job for single jurisdiction
        job = ExportJob(
            export_type='single_jurisdiction',
            status='queued',
            cache_freshness_minutes=30,
            params={'jurisdiction_id': jurisdiction_id}
        )
        
        db.session.add(job)
        db.session.commit()
        
        logger.info(f"Created single jurisdiction export job {job.id} for {jurisdiction_id}")
        
        return jsonify({
            'status': 'job_created',
            'job_id': str(job.id),
            'jurisdiction_id': jurisdiction_id,
            'message': f'Export job started for {jurisdiction_id}. Use the job_id to check progress.',
            'status_url': f"/api/gis/jobs/{job.id}/status",
            'estimated_duration_seconds': 30
        })
        
    except Exception as e:
        logger.error(f"Error creating export job for jurisdiction {jurisdiction_id}: {e}")
        return jsonify({
            'error': 'Failed to create export job',
            'message': 'An internal error occurred. Please try again.'
        }), 500

@gis_export_bp.route('/fields', methods=['GET'])
def get_export_fields():
    """
    Get information about available fields in the export data.
    """
    field_info = {
        'identifier_fields': {
            'jurisdiction_id': 'Unique identifier for the jurisdiction',
            'jurisdiction': 'Full name of the health department or jurisdiction',
            'county': 'Wisconsin county name',
            'fips_code': 'Federal Information Processing Standard county code'
        },
        'risk_domain_scores': {
            'total_risk_score': 'Overall composite risk score (0.0-1.0)',
            'residual_risk': 'Calculated residual risk after resilience adjustment',
            'natural_hazards_risk': 'Combined natural hazards risk score',
            'health_risk': 'Public health vulnerability score',
            'active_shooter_risk': 'Community violence risk assessment',
            'extreme_heat_risk': 'Heat-related health risk score',
            'air_quality_risk': 'Air pollution and quality risk',
            'cybersecurity_risk': 'Digital infrastructure vulnerability',
            'utilities_risk': 'Critical infrastructure risk'
        },
        'specific_hazards': {
            'flood_risk': 'Flood exposure and vulnerability',
            'tornado_risk': 'Tornado exposure and vulnerability', 
            'winter_storm_risk': 'Winter weather risk assessment',
            'thunderstorm_risk': 'Severe thunderstorm risk'
        },
        'risk_components': {
            'exposure': 'Hazard exposure level (0.0-1.0)',
            'vulnerability': 'Community vulnerability score (0.0-1.0)',
            'resilience': 'Community resilience capacity (0.0-1.0)',
            'health_impact_factor': 'Health consequence multiplier (0.8-1.5)'
        },
        'geographic_data': {
            'lat': 'Latitude of jurisdiction centroid',
            'lon': 'Longitude of jurisdiction centroid'
        },
        'metadata': {
            'calculation_timestamp': 'When the risk scores were calculated',
            'framework_version': 'CARA framework version used',
            'data_source': 'Source system identifier'
        }
    }
    
    return jsonify({
        'field_descriptions': field_info,
        'total_fields': sum(len(category) for category in field_info.values()),
        'arcgis_compatibility': 'All fields are UTF-8 encoded and ArcGIS compatible',
        'coordinate_system': 'WGS84 (EPSG:4326)'
    })

@gis_export_bp.route('/jobs', methods=['POST'])
def create_export_job():
    """
    Create a new export job (alternative endpoint).
    """
    return export_all_data()

@gis_export_bp.route('/jobs/<job_id>/status', methods=['GET'])
def get_job_status(job_id):
    """
    Get the status of an export job.
    
    Args:
        job_id: UUID of the export job
    """
    try:
        job = db.session.query(ExportJob).filter(ExportJob.id == job_id).first()
        
        if not job:
            return jsonify({
                'error': 'Job not found'
            }), 404
        
        response_data = job.to_dict()
        
        # Add download URLs if job is completed
        if job.status == 'completed' and job.result_files:
            base_url = request.host_url.rstrip('/')
            
            downloads = {}
            if 'csv' in job.result_files:
                downloads['csv'] = {
                    'filename': os.path.basename(job.result_files['csv']),
                    'download_url': f"{base_url}/api/gis/download/csv/{os.path.basename(job.result_files['csv'])}",
                    'description': 'Risk scores in tabular CSV format'
                }
            
            if 'geojson' in job.result_files:
                downloads['geojson'] = {
                    'filename': os.path.basename(job.result_files['geojson']),
                    'download_url': f"{base_url}/api/gis/download/geojson/{os.path.basename(job.result_files['geojson'])}",
                    'description': 'Risk scores with spatial geometries'
                }
            
            response_data['downloads'] = downloads
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error getting job status for {job_id}: {e}")
        return jsonify({
            'error': 'Error retrieving job status',
            'message': 'An internal error occurred. Please try again.'
        }), 500

@gis_export_bp.route('/jobs/<job_id>/cancel', methods=['POST'])
def cancel_job(job_id):
    """
    Cancel an export job.
    
    Args:
        job_id: UUID of the export job
    """
    try:
        job = db.session.query(ExportJob).filter(ExportJob.id == job_id).first()
        
        if not job:
            return jsonify({
                'error': 'Job not found'
            }), 404
        
        if job.status in ['completed', 'failed', 'canceled']:
            return jsonify({
                'error': f'Cannot cancel job in {job.status} status'
            }), 400
        
        job.status = 'canceled'
        job.finished_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Job canceled successfully',
            'job_id': str(job.id)
        })
        
    except Exception as e:
        logger.error(f"Error canceling job {job_id}: {e}")
        return jsonify({
            'error': 'Error canceling job',
            'message': 'An internal error occurred. Please try again.'
        }), 500

@gis_export_bp.route('/status', methods=['GET'])
def export_status():
    """
    Get general status information about export system.
    """
    try:
        # Get recent jobs
        recent_jobs = db.session.query(ExportJob).order_by(
            ExportJob.created_at.desc()
        ).limit(10).all()
        
        # Get export directory info
        export_dir = 'exports'
        files = []
        if os.path.exists(export_dir):
            for filename in os.listdir(export_dir):
                if filename.endswith(('.csv', '.geojson')):
                    file_path = os.path.join(export_dir, filename)
                    file_stats = os.stat(file_path)
                    
                    files.append({
                        'filename': filename,
                        'size_bytes': file_stats.st_size,
                        'created': file_stats.st_mtime,
                        'type': 'CSV' if filename.endswith('.csv') else 'GeoJSON'
                    })
        
        return jsonify({
            'status': 'Export system operational',
            'recent_jobs': [job.to_dict() for job in recent_jobs],
            'available_files': sorted(files, key=lambda x: x['created'], reverse=True)[:20],
            'total_files': len(files)
        })
        
    except Exception as e:
        logger.error(f"Error checking export status: {e}")
        return jsonify({
            'error': 'Error checking export status',
            'message': 'An internal error occurred. Please try again.'
        }), 500