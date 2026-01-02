#!/usr/bin/env python3
"""
Command-line interface for the job application tracker
"""
import click
from datetime import datetime, date
from app.database import SessionLocal
from app.models.application import Application, ApplicationStatus


@click.group()
def cli():
    """Job Application Tracker CLI"""
    pass


@cli.command(name='add-application')
@click.argument('company')
@click.argument('role')
@click.argument('applied_date')
def add_application(company, role, applied_date):
    """Add a new job application.
    
    COMPANY: Company name
    ROLE: Job role/title
    APPLIED_DATE: Date applied (YYYY-MM-DD format)
    """
    # Parse the date
    try:
        applied_date_obj = datetime.strptime(applied_date, '%Y-%m-%d').date()
    except ValueError:
        click.echo(f"❌ Error: Invalid date format. Use YYYY-MM-DD (e.g., 2024-01-15)", err=True)
        return
    
    # Extract company_keyword (first word, lowercase)
    company_keyword = company.split()[0].lower()
    
    # Create database session
    db = SessionLocal()
    try:
        # Create new application
        application = Application(
            company_name=company,
            company_keyword=company_keyword,
            role_title=role,
            applied_date=applied_date_obj,
            status=ApplicationStatus.APPLIED
        )
        
        db.add(application)
        db.commit()
        
        click.echo(f"✓ Added {company} - {role}")
    except Exception as e:
        db.rollback()
        click.echo(f"❌ Error: {str(e)}", err=True)
    finally:
        db.close()


@cli.command(name='list-applications')
def list_applications():
    """List all job applications."""
    db = SessionLocal()
    try:
        # Get all applications ordered by applied_date (newest first)
        applications = db.query(Application).order_by(Application.applied_date.desc()).all()
        
        if not applications:
            click.echo("No applications found.")
            return
        
        click.echo(f"\n📋 Your Applications ({len(applications)} total):\n")
        
        for i, app in enumerate(applications, 1):
            # Count emails for this application
            email_count = len(app.emails) if app.emails else 0
            
            click.echo(f"{i}. {app.company_name} - {app.role_title}")
            click.echo(f"   Status: {app.status.value}")
            click.echo(f"   Applied: {app.applied_date}")
            click.echo(f"   Emails: {email_count}")
            click.echo()
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
    finally:
        db.close()


@cli.command()
def status():
    """Show pipeline breakdown by status."""
    db = SessionLocal()
    try:
        # Count applications by status
        counts = {
            ApplicationStatus.APPLIED: db.query(Application).filter(Application.status == ApplicationStatus.APPLIED).count(),
            ApplicationStatus.SCREENING: db.query(Application).filter(Application.status == ApplicationStatus.SCREENING).count(),
            ApplicationStatus.INTERVIEW: db.query(Application).filter(Application.status == ApplicationStatus.INTERVIEW).count(),
            ApplicationStatus.OFFER: db.query(Application).filter(Application.status == ApplicationStatus.OFFER).count(),
            ApplicationStatus.REJECTED: db.query(Application).filter(Application.status == ApplicationStatus.REJECTED).count(),
        }
        
        click.echo("\n📊 Your Job Search Pipeline:\n")
        click.echo(f"Applied: {counts[ApplicationStatus.APPLIED]}")
        click.echo(f"Screening: {counts[ApplicationStatus.SCREENING]}")
        click.echo(f"Interview Scheduled: {counts[ApplicationStatus.INTERVIEW]}")
        click.echo(f"Offer: {counts[ApplicationStatus.OFFER]}")
        click.echo(f"Rejected: {counts[ApplicationStatus.REJECTED]}")
        click.echo()
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
    finally:
        db.close()


@cli.command(name='get-application')
@click.argument('company')
def get_application(company):
    """Get details for a specific company.
    
    COMPANY: Company name or keyword to search for
    """
    db = SessionLocal()
    try:
        # Search by company_name or company_keyword (case-insensitive)
        application = db.query(Application).filter(
            (Application.company_name.ilike(f"%{company}%")) |
            (Application.company_keyword.ilike(f"%{company.lower()}%"))
        ).first()
        
        if not application:
            click.echo(f"❌ No application found for '{company}'")
            return
        
        # Count emails
        email_count = len(application.emails) if application.emails else 0
        
        click.echo(f"\n📄 Application Details:\n")
        click.echo(f"Company: {application.company_name}")
        click.echo(f"Company Keyword: {application.company_keyword}")
        click.echo(f"Role: {application.role_title}")
        click.echo(f"Status: {application.status.value}")
        click.echo(f"Applied Date: {application.applied_date}")
        click.echo(f"Emails: {email_count}")
        
        if application.job_description:
            click.echo(f"\nJob Description:")
            click.echo(f"{application.job_description}")
        
        click.echo(f"\nCreated: {application.created_at}")
        click.echo(f"Updated: {application.updated_at}")
        click.echo()
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
    finally:
        db.close()


@cli.command(name='update-status')
@click.argument('company')
@click.argument('new_status')
def update_status(company, new_status):
    """Update application status.
    
    COMPANY: Company name or keyword to search for
    NEW_STATUS: New status (applied, screening, interview, offer, rejected)
    """
    db = SessionLocal()
    try:
        # Validate status
        try:
            status_enum = ApplicationStatus(new_status.lower())
        except ValueError:
            valid_statuses = [s.value for s in ApplicationStatus]
            click.echo(f"❌ Error: Invalid status. Valid options: {', '.join(valid_statuses)}", err=True)
            return
        
        # Search by company_name or company_keyword (case-insensitive)
        application = db.query(Application).filter(
            (Application.company_name.ilike(f"%{company}%")) |
            (Application.company_keyword.ilike(f"%{company.lower()}%"))
        ).first()
        
        if not application:
            click.echo(f"❌ No application found for '{company}'")
            return
        
        # Update status
        application.status = status_enum
        db.commit()
        
        click.echo(f"✓ Updated {application.company_name} to {new_status.lower()}")
    except Exception as e:
        db.rollback()
        click.echo(f"❌ Error: {str(e)}", err=True)
    finally:
        db.close()


if __name__ == '__main__':
    cli()

