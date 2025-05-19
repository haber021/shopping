
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string

def send_order_confirmation(order):
    """Send order confirmation email to customer"""
    subject = f'Order Confirmation - {order.order_number}'
    message = render_to_string('emails/order_confirmation.html', {
        'order': order
    })
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [order.customer.email],
        html_message=message
    )

def send_order_status_update(order):
    """Send order status update email to customer"""
    subject = f'Order Status Update - {order.order_number}'
    message = render_to_string('emails/order_status_update.html', {
        'order': order
    })
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [order.customer.email],
        html_message=message
    )
