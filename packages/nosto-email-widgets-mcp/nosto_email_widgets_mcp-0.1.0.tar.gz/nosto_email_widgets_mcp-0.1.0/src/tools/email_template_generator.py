"""
Email Template Generator Tool

Generates customizable email templates with various layouts and content.
"""

from typing import Literal, Optional
from mcp import Tool
from pydantic import BaseModel, Field
import jinja2


class EmailTemplateRequest(BaseModel):
    """Request model for email template generation."""
    
    template_type: Literal["newsletter", "promotional", "welcome", "transactional"] = Field(
        description="The type of email template to generate"
    )
    
    company_name: str = Field(
        description="Name of the company/brand"
    )
    
    primary_color: str = Field(
        default="#007bff",
        description="Primary color for the template (hex code)"
    )
    
    logo_url: Optional[str] = Field(
        default=None,
        description="URL to the company logo"
    )
    
    content_sections: list[str] = Field(
        default=["header", "main_content", "footer"],
        description="Sections to include in the template"
    )
    
    custom_message: Optional[str] = Field(
        default=None,
        description="Custom message to include in the template"
    )


class EmailTemplateGenerator(Tool):
    """Tool for generating customizable email templates."""
    
    name: str = "email_template_generator"
    description: str = "Generate customizable email templates with various layouts and content"
    inputSchema: type[EmailTemplateRequest] = EmailTemplateRequest
    
    def __call__(self, request: EmailTemplateRequest) -> str:
        """Generate an email template based on the request."""
        
        # Define template based on type
        if request.template_type == "newsletter":
            template_content = self._generate_newsletter_template(request)
        elif request.template_type == "promotional":
            template_content = self._generate_promotional_template(request)
        elif request.template_type == "welcome":
            template_content = self._generate_welcome_template(request)
        elif request.template_type == "transactional":
            template_content = self._generate_transactional_template(request)
        else:
            template_content = self._generate_basic_template(request)
        
        return template_content
    
    def _generate_newsletter_template(self, request: EmailTemplateRequest) -> str:
        """Generate a newsletter-style email template."""
        
        template = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{request.company_name} Newsletter</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f4f4f4; }}
        .container {{ max-width: 600px; margin: 0 auto; background-color: white; }}
        .header {{ background-color: {request.primary_color}; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; }}
        .footer {{ background-color: #333; color: white; padding: 20px; text-align: center; font-size: 12px; }}
        .logo {{ max-width: 150px; height: auto; }}
        .section {{ margin-bottom: 20px; }}
        .cta-button {{ display: inline-block; background-color: {request.primary_color}; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            {f'<img src="{request.logo_url}" alt="{request.company_name}" class="logo">' if request.logo_url else ''}
            <h1>{request.company_name}</h1>
            <p>Newsletter</p>
        </div>
        
        <div class="content">
            {f'<div class="section"><p>{request.custom_message}</p></div>' if request.custom_message else ''}
            
            <div class="section">
                <h2>Latest Updates</h2>
                <p>Stay up to date with the latest news and updates from {request.company_name}.</p>
            </div>
            
            <div class="section">
                <h2>Featured Content</h2>
                <p>Discover our most popular products and services.</p>
                <a href="#" class="cta-button">Learn More</a>
            </div>
        </div>
        
        <div class="footer">
            <p>&copy; 2024 {request.company_name}. All rights reserved.</p>
            <p>Unsubscribe | Privacy Policy | Contact Us</p>
        </div>
    </div>
</body>
</html>
        """
        
        return template.strip()
    
    def _generate_promotional_template(self, request: EmailTemplateRequest) -> str:
        """Generate a promotional email template."""
        
        template = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Special Offer from {request.company_name}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f4f4f4; }}
        .container {{ max-width: 600px; margin: 0 auto; background-color: white; }}
        .header {{ background-color: {request.primary_color}; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; }}
        .footer {{ background-color: #333; color: white; padding: 20px; text-align: center; font-size: 12px; }}
        .logo {{ max-width: 150px; height: auto; }}
        .offer-box {{ background-color: #fff3cd; border: 1px solid #ffeaa7; padding: 20px; margin: 20px 0; text-align: center; }}
        .cta-button {{ display: inline-block; background-color: {request.primary_color}; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-size: 18px; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            {f'<img src="{request.logo_url}" alt="{request.company_name}" class="logo">' if request.logo_url else ''}
            <h1>Special Offer!</h1>
        </div>
        
        <div class="content">
            {f'<div class="section"><p>{request.custom_message}</p></div>' if request.custom_message else ''}
            
            <div class="offer-box">
                <h2>🎉 Limited Time Deal</h2>
                <p>Don't miss out on this exclusive offer from {request.company_name}!</p>
                <a href="#" class="cta-button">Claim Offer Now</a>
            </div>
            
            <div class="section">
                <h3>Why Choose {request.company_name}?</h3>
                <ul>
                    <li>Premium quality products</li>
                    <li>Excellent customer service</li>
                    <li>Fast and reliable delivery</li>
                </ul>
            </div>
        </div>
        
        <div class="footer">
            <p>&copy; 2024 {request.company_name}. All rights reserved.</p>
            <p>Unsubscribe | Privacy Policy | Contact Us</p>
        </div>
    </div>
</body>
</html>
        """
        
        return template.strip()
    
    def _generate_welcome_template(self, request: EmailTemplateRequest) -> str:
        """Generate a welcome email template."""
        
        template = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Welcome to {request.company_name}!</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f4f4f4; }}
        .container {{ max-width: 600px; margin: 0 auto; background-color: white; }}
        .header {{ background-color: {request.primary_color}; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; }}
        .footer {{ background-color: #333; color: white; padding: 20px; text-align: center; font-size: 12px; }}
        .logo {{ max-width: 150px; height: auto; }}
        .welcome-message {{ text-align: center; padding: 30px 20px; }}
        .cta-button {{ display: inline-block; background-color: {request.primary_color}; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            {f'<img src="{request.logo_url}" alt="{request.company_name}" class="logo">' if request.logo_url else ''}
            <h1>Welcome!</h1>
        </div>
        
        <div class="content">
            <div class="welcome-message">
                <h2>Welcome to {request.company_name}!</h2>
                <p>We're excited to have you on board. Thank you for joining our community!</p>
                {f'<p>{request.custom_message}</p>' if request.custom_message else ''}
            </div>
            
            <div class="section">
                <h3>Getting Started</h3>
                <p>Here are some things you can do to get started:</p>
                <ul>
                    <li>Explore our products and services</li>
                    <li>Complete your profile</li>
                    <li>Check out our latest offers</li>
                </ul>
            </div>
            
            <div class="section" style="text-align: center;">
                <a href="#" class="cta-button">Get Started</a>
            </div>
        </div>
        
        <div class="footer">
            <p>&copy; 2024 {request.company_name}. All rights reserved.</p>
            <p>Unsubscribe | Privacy Policy | Contact Us</p>
        </div>
    </div>
</body>
</html>
        """
        
        return template.strip()
    
    def _generate_transactional_template(self, request: EmailTemplateRequest) -> str:
        """Generate a transactional email template."""
        
        template = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Transaction Confirmation - {request.company_name}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f4f4f4; }}
        .container {{ max-width: 600px; margin: 0 auto; background-color: white; }}
        .header {{ background-color: {request.primary_color}; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; }}
        .footer {{ background-color: #333; color: white; padding: 20px; text-align: center; font-size: 12px; }}
        .logo {{ max-width: 150px; height: auto; }}
        .transaction-details {{ background-color: #f8f9fa; border: 1px solid #dee2e6; padding: 20px; margin: 20px 0; }}
        .cta-button {{ display: inline-block; background-color: {request.primary_color}; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            {f'<img src="{request.logo_url}" alt="{request.company_name}" class="logo">' if request.logo_url else ''}
            <h1>Transaction Confirmation</h1>
        </div>
        
        <div class="content">
            {f'<div class="section"><p>{request.custom_message}</p></div>' if request.custom_message else ''}
            
            <div class="transaction-details">
                <h3>Transaction Details</h3>
                <p><strong>Order ID:</strong> #12345</p>
                <p><strong>Date:</strong> {request.custom_message or "Today"}</p>
                <p><strong>Status:</strong> Confirmed</p>
            </div>
            
            <div class="section">
                <h3>Next Steps</h3>
                <p>Your order has been confirmed and is being processed. You'll receive updates on your order status.</p>
            </div>
            
            <div class="section" style="text-align: center;">
                <a href="#" class="cta-button">View Order</a>
            </div>
        </div>
        
        <div class="footer">
            <p>&copy; 2024 {request.company_name}. All rights reserved.</p>
            <p>Privacy Policy | Contact Us | Support</p>
        </div>
    </div>
</body>
</html>
        """
        
        return template.strip()
    
    def _generate_basic_template(self, request: EmailTemplateRequest) -> str:
        """Generate a basic email template."""
        
        template = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Message from {request.company_name}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f4f4f4; }}
        .container {{ max-width: 600px; margin: 0 auto; background-color: white; }}
        .header {{ background-color: {request.primary_color}; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; }}
        .footer {{ background-color: #333; color: white; padding: 20px; text-align: center; font-size: 12px; }}
        .logo {{ max-width: 150px; height: auto; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            {f'<img src="{request.logo_url}" alt="{request.company_name}" class="logo">' if request.logo_url else ''}
            <h1>{request.company_name}</h1>
        </div>
        
        <div class="content">
            {f'<p>{request.custom_message}</p>' if request.custom_message else '<p>Thank you for your interest in our services.</p>'}
        </div>
        
        <div class="footer">
            <p>&copy; 2024 {request.company_name}. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
        """
        
        return template.strip()
