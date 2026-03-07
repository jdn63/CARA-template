# CARA Application Deployment Guide

## Pre-Deployment Checklist

### Required Environment Variables
Ensure these environment variables are configured in your hosting environment:

```bash
DATABASE_URL=postgresql://username:password@host:port/database
AIRNOW_API_KEY=your_airnow_api_key
SESSION_SECRET=your_secure_session_secret
```

### Database Setup
1. PostgreSQL database with PostGIS extension enabled
2. Database will auto-initialize on first run
3. Ensure adequate storage space (minimum 10GB recommended)

### System Requirements
- Python 3.11+
- 2GB+ RAM
- Reliable internet connection for API data
- SSL certificate for production use

## Deployment Steps

### 1. Environment Setup
```bash
# Install Python dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="your_database_url"
export AIRNOW_API_KEY="your_airnow_key"
# ... other environment variables
```

### 2. Database Initialization
The application will automatically:
- Create necessary database tables
- Initialize scheduler configuration
- Set up feedback tracking system

### 3. Start Application
```bash
# Production deployment
gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 120 main:app

# Development
python main.py
```

### 4. Initial Configuration
1. Access the application at your domain
2. Verify all jurisdictions load correctly
3. Test risk assessment calculations
4. Confirm maps and visualizations work

### 5. Admin Access
Admin features are available at:
- `/admin/feedback` - Feedback monitoring dashboard
- `/admin/feedback-alerts` - Quick feedback alerts
- `/admin/scheduler` - Data refresh management

## Post-Deployment Verification

### Test Core Functionality
- [ ] Main map loads with all jurisdictions
- [ ] Individual jurisdiction dashboards work
- [ ] Risk calculations display correctly
- [ ] Action plans generate properly
- [ ] Print summaries format correctly

### Test Data Integration
- [ ] Weather alerts populate
- [ ] Census data loads from local files
- [ ] Scheduler runs automatically
- [ ] Feedback system captures submissions

### Test Regional Features
- [ ] Regional dashboards load
- [ ] Regional aggregation calculations work
- [ ] HVA exports generate correctly

## Monitoring and Maintenance

### Data Refresh Schedule
The application automatically refreshes data sources:
- Weather patterns: Every 6 hours
- Census data: Daily
- Climate projections: Weekly
- Vaccination rates: Weekly

### Log Monitoring
Monitor these log files for issues:
- Application logs for errors
- Scheduler logs for data refresh status
- Database logs for performance issues

### Feedback Monitoring
Check admin dashboards regularly:
- New feedback submissions
- System usage patterns
- Error reports from users

## Troubleshooting Common Issues

### Database Connection Issues
- Verify DATABASE_URL format
- Check PostgreSQL service status
- Ensure PostGIS extension is enabled

### API Integration Problems
- Verify all API keys are valid
- Check rate limits haven't been exceeded
- Confirm internet connectivity

### Performance Issues
- Monitor database query performance
- Check memory usage during peak times
- Optimize map rendering if needed

### Data Refresh Failures
- Check scheduler logs in `/admin/scheduler`
- Verify API credentials are still valid
- Restart scheduler if needed

## Security Considerations

### Production Security
- Use HTTPS only in production
- Implement proper firewall rules
- Regular security updates
- Secure API key storage

### Admin Interface Security
- Admin URLs are intentionally hidden
- Monitor access logs for admin endpoints
- Implement IP restrictions if needed

## Backup and Recovery

### Database Backups
- Regular PostgreSQL backups recommended
- Include geospatial data in backups
- Test restore procedures periodically

### Configuration Backups
- Back up environment variable configurations
- Save scheduler configuration files
- Document custom modifications

## Performance Optimization

### Database Optimization
- Regular VACUUM and ANALYZE operations
- Index optimization for geospatial queries
- Connection pooling configuration

### Application Optimization
- Enable caching where appropriate
- Optimize map rendering performance
- Monitor memory usage patterns

## Support and Updates

### Getting Help
- Review application logs for error details
- Check the FAQ at `/docs/faq`
- Use feedback system for user reports

### Future Updates
- Monitor for security updates
- Test updates in staging environment
- Backup before applying updates
- Document any custom modifications

This deployment guide ensures successful implementation of the CARA application in your production environment.
