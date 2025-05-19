from django.http import HttpResponse
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from decimal import Decimal


def generate_salary_slip_pdf(salary_slip):
    """
    Generate a PDF for a salary slip
    """
    # Create a file-like buffer to receive PDF data
    buffer = BytesIO()
    
    # Create the PDF object, using the buffer as its "file"
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Set up some variables for positioning
    margin = 50
    current_y = height - margin
    line_height = 20
    
    # Add company logo/header
    p.setFont("Helvetica-Bold", 18)
    p.drawString(margin, current_y, "RetailPay System")
    current_y -= line_height
    
    p.setFont("Helvetica", 12)
    p.drawString(margin, current_y, "Salary Slip")
    current_y -= line_height * 1.5
    
    # Add payroll period info
    p.setFont("Helvetica-Bold", 12)
    p.drawString(margin, current_y, f"Payroll Period: {salary_slip.payroll.start_date.strftime('%d %b %Y')} to {salary_slip.payroll.end_date.strftime('%d %b %Y')}")
    current_y -= line_height * 1.5
    
    # Add employee details
    p.setFont("Helvetica-Bold", 12)
    p.drawString(margin, current_y, "Employee Details")
    current_y -= line_height
    
    p.setFont("Helvetica", 10)
    p.drawString(margin, current_y, f"Name: {salary_slip.employee.full_name}")
    p.drawString(margin + 250, current_y, f"Dept: {salary_slip.employee.department.name}")
    current_y -= line_height
    
    p.drawString(margin, current_y, f"Employee ID: {salary_slip.employee.employee_id}")
    p.drawString(margin + 250, current_y, f"Type: {salary_slip.employee.get_employment_type_display()}")
    current_y -= line_height
    
    if salary_slip.employee.bank_name and salary_slip.employee.bank_account:
        p.drawString(margin, current_y, f"Bank: {salary_slip.employee.bank_name} ({salary_slip.employee.masked_bank_account})")
    current_y -= line_height * 1.5
    
    # Add earnings and deductions in a table format
    p.setFont("Helvetica-Bold", 12)
    p.drawString(margin, current_y, "Earnings")
    p.drawString(margin + 250, current_y, "Deductions")
    current_y -= line_height
    
    # Get earnings and deductions
    earnings = salary_slip.details.filter(type='earning')
    deductions = salary_slip.details.filter(type='deduction')
    
    # Determine the number of rows needed (use whichever is larger)
    num_rows = max(earnings.count(), deductions.count())
    
    # Create data for earnings table
    earnings_data = []
    for earn in earnings:
        earnings_data.append([earn.pay_head_name, f"${earn.amount:.2f}"])
    
    # Pad with empty rows if needed
    while len(earnings_data) < num_rows:
        earnings_data.append(["", ""])
    
    # Create data for deductions table
    deductions_data = []
    for deduct in deductions:
        deductions_data.append([deduct.pay_head_name, f"${deduct.amount:.2f}"])
    
    # Pad with empty rows if needed
    while len(deductions_data) < num_rows:
        deductions_data.append(["", ""])
    
    # Create and draw earnings table
    earnings_table = Table(earnings_data, colWidths=[150, 70])
    earnings_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    earnings_table.wrapOn(p, width, height)
    earnings_table.drawOn(p, margin, current_y - (line_height * num_rows))
    
    # Create and draw deductions table
    deductions_table = Table(deductions_data, colWidths=[150, 70])
    deductions_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    deductions_table.wrapOn(p, width, height)
    deductions_table.drawOn(p, margin + 250, current_y - (line_height * num_rows))
    
    current_y -= (line_height * (num_rows + 1.5))
    
    # Add totals
    p.setFont("Helvetica-Bold", 10)
    p.drawString(margin, current_y, "Total Earnings:")
    p.drawString(margin + 150, current_y, f"${salary_slip.total_earnings:.2f}")
    
    p.drawString(margin + 250, current_y, "Total Deductions:")
    p.drawString(margin + 400, current_y, f"${salary_slip.total_deductions:.2f}")
    current_y -= line_height * 1.5
    
    # Add net pay
    p.setFont("Helvetica-Bold", 12)
    p.drawString(margin, current_y, "Net Payable:")
    p.drawString(margin + 150, current_y, f"${salary_slip.net_salary:.2f}")
    
    # Add footer
    p.setFont("Helvetica", 8)
    p.drawString(margin, margin, f"Generated on: {salary_slip.created_at.strftime('%d %b %Y %H:%M')}")
    p.drawString(width - margin - 100, margin, "This is a system generated slip")
    
    # Close the PDF object cleanly
    p.showPage()
    p.save()
    
    # File response with PDF
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="salary_slip_{salary_slip.employee.employee_id}_{salary_slip.payroll.start_date.strftime("%Y%m%d")}.pdf"'
    
    return response
