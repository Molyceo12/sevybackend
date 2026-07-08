import requests
import xml.etree.ElementTree as ET
from django.conf import settings

# DPO Pay API Endpoint (v6 is standard)
DPO_API_URL = "https://secure.3gdirectpay.com/API/v6/"
# To redirect user to payment page
DPO_PAYMENT_URL = "https://secure.3gdirectpay.com/payv3.php?ID="

def process_dpo_payment(amount, email, phone_number, name, reference, currency="RWF"):
    """
    Initialize a DPO Pay transaction by requesting a payment token.
    Returns the checkout link to redirect the user.
    """
    company_token = getattr(settings, 'DPO_COMPANY_TOKEN', 'YOUR_DPO_COMPANY_TOKEN')
    service_type = getattr(settings, 'DPO_SERVICE_TYPE', '3854') # Example service type
    
    # Build the XML Request
    root = ET.Element("API3G")
    
    # 1. CompanyToken
    ET.SubElement(root, "CompanyToken").text = company_token
    ET.SubElement(root, "Request").text = "createToken"
    
    # 2. Transaction Level
    transaction = ET.SubElement(root, "Transaction")
    ET.SubElement(transaction, "PaymentAmount").text = str(amount)
    ET.SubElement(transaction, "PaymentCurrency").text = currency
    ET.SubElement(transaction, "CompanyRef").text = reference
    ET.SubElement(transaction, "RedirectURL").text = getattr(settings, 'DPO_REDIRECT_URL', "https://your-frontend-url.com/payment-success")
    ET.SubElement(transaction, "BackURL").text = getattr(settings, 'DPO_BACK_URL', "https://your-frontend-url.com/payment-failed")
    ET.SubElement(transaction, "CompanyRefUnique").text = "0"
    ET.SubElement(transaction, "PTL").text = "5" # Payment Time Limit in minutes
    ET.SubElement(transaction, "CustomerEmail").text = email
    ET.SubElement(transaction, "CustomerFirstName").text = name
    ET.SubElement(transaction, "CustomerPhone").text = phone_number
    
    # 3. Services Level
    services = ET.SubElement(root, "Services")
    service = ET.SubElement(services, "Service")
    ET.SubElement(service, "ServiceType").text = service_type
    ET.SubElement(service, "ServiceDescription").text = "Payment for Sevy Mobility Booking"
    ET.SubElement(service, "ServiceDate").text = "2026/07/08 19:00" # Should be dynamic in production
    
    # Convert to XML string
    xml_data = ET.tostring(root, encoding='utf8', method='xml')
    
    headers = {'Content-Type': 'application/xml'}
    
    try:
        response = requests.post(DPO_API_URL, data=xml_data, headers=headers)
        
        if response.status_code == 200:
            # Parse the XML response
            response_tree = ET.fromstring(response.content)
            result = response_tree.find('Result').text
            result_explanation = response_tree.find('ResultExplanation').text
            
            if result == '000':
                trans_token = response_tree.find('TransToken').text
                return {
                    "status": True,
                    "payment_url": f"{DPO_PAYMENT_URL}{trans_token}",
                    "trans_token": trans_token,
                    "message": "Token generated successfully"
                }
            else:
                return {
                    "status": False,
                    "message": result_explanation
                }
        else:
            return {
                "status": False,
                "message": f"HTTP Error: {response.status_code}"
            }
    except Exception as e:
        return {
            "status": False,
            "message": str(e)
        }

def verify_dpo_payment(trans_token):
    """
    Verify a DPO payment using the TransToken.
    """
    company_token = getattr(settings, 'DPO_COMPANY_TOKEN', 'YOUR_DPO_COMPANY_TOKEN')
    
    # Build the XML Request
    root = ET.Element("API3G")
    ET.SubElement(root, "CompanyToken").text = company_token
    ET.SubElement(root, "Request").text = "verifyToken"
    ET.SubElement(root, "TransactionToken").text = trans_token
    
    xml_data = ET.tostring(root, encoding='utf8', method='xml')
    headers = {'Content-Type': 'application/xml'}
    
    try:
        response = requests.post(DPO_API_URL, data=xml_data, headers=headers)
        
        if response.status_code == 200:
            response_tree = ET.fromstring(response.content)
            result = response_tree.find('Result').text
            result_explanation = response_tree.find('ResultExplanation').text
            
            if result == '000':
                return {
                    "status": True,
                    "message": "Payment successful",
                    "amount": response_tree.find('TransactionAmount').text,
                    "currency": response_tree.find('TransactionCurrency').text,
                    "customer_name": response_tree.find('CustomerName').text,
                }
            else:
                return {
                    "status": False,
                    "message": result_explanation
                }
        else:
            return {
                "status": False,
                "message": f"HTTP Error: {response.status_code}"
            }
    except Exception as e:
        return {
            "status": False,
            "message": str(e)
        }
