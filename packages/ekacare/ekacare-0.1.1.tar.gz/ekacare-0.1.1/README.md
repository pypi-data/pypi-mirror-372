# Eka Care SDK for Python

A comprehensive Python SDK for interacting with the Eka Care APIs.

## Installation

```bash
pip install ekacare
```

## Features

The SDK provides easy access to the following Eka Care APIs:

- Authentication
- Records Management (upload, list, update, delete)
- ABDM Connect (profile, consents, care contexts)
- Appointment Management
- Doctor & Clinic Management
- Patient Management
- Webhooks (register, manage, verify)
- Vitals (update patient vitals)
- Medical Document Parsing
- Assessment APIs
- Notifications
- Privacy Management

## Quick Start

### Authentication

```python
from ekacare import EkaCareClient

# Initialize with client credentials
client = EkaCareClient(
    client_id="your_client_id",
    client_secret="your_client_secret"
)

# Or initialize with an existing access token
client = EkaCareClient(
    access_token="your_access_token"
)

# Manually get an access token
token_response = client.auth.login()
access_token = token_response["access_token"]
```

### Records Management

```python
# Upload a document
response = client.records.upload_document(
    file_path="/path/to/lab_report.pdf",
    document_type="lr",  # lab report
    tags=["covid", "test"],
    title="COVID-19 Test Report"
)
document_id = response["document_id"]

# List documents
documents = client.records.list_documents()
for doc in documents.get("items", []):
    print(doc["record"]["item"]["document_id"])

# Get a specific document
document = client.records.get_document(document_id)

# Update a document
client.records.update_document(
    document_id=document_id,
    document_type="ps",  # prescription
    tags=["medication"]
)

# Delete a document
client.records.delete_document(document_id)

# Retrieve health records in FHIR format
records = client.records.retrieve_health_records(
    identifier="care_context_123",
    hip_id="hip123",
    health_id="user@abdm"
)
```

### Vitals Management

```python
# Create vital records
heart_rate = client.vitals.create_heart_rate_vital(
    value=75,
    measured_at="2023-01-01T12:00:00"
)

blood_glucose = client.vitals.create_blood_glucose_vital(
    value=120,
    measured_at="2023-01-01T08:00:00",
    glucose_type="fasting"
)

blood_oxygen = client.vitals.create_blood_oxygen_vital(
    value=98,
    measured_at="2023-01-01T12:30:00"
)

blood_pressure = client.vitals.create_blood_pressure_vital(
    systolic=120,
    diastolic=80,
    measured_at="2023-01-01T14:45:00"
)

# Update patient vitals
client.vitals.update_vitals(
    txn_id="transaction_id",
    vitals_data=[heart_rate, blood_glucose, blood_oxygen] + blood_pressure
)
```

### Webhooks

```python
# Register a webhook
response = client.webhooks.register_webhook(
    endpoint="https://your-app.com/webhook",
    scopes=["appointment.created", "prescription.created"],
    signing_key="your_secret_key"
)
webhook_id = response["id"]

# Get all webhooks
webhooks = client.webhooks.get_webhooks()

# Update a webhook's signing key
client.webhooks.update_webhook(
    webhook_id=webhook_id,
    signing_key="new_secret_key"
)

# Delete a webhook
client.webhooks.delete_webhook(webhook_id)

# Verify a webhook signature
is_valid = client.webhooks.verify_signature(
    payload=webhook_payload,
    signature=webhook_signature,
    secret_key="your_secret_key"
)
```

### Appointment Management

```python
# Get Appointment Details
response = client.appointments.get_appointment_details("YOUR_APPOINTMENT_ID")

```


### Doctor & Clinic Management

```python
# Get Clinic Details
response = client.clinic_doctor.get_clinic_details("YOUR_CLINIC_ID")


# Get Doctor Details
response = client.clinic_doctor.get_doctor_details("YOUR_DOCTOR_ID")

```

### Appointment Management

```python
# Get Appointment Details
response = client.appointments.get_appointment_details("YOUR_APPOINTMENT_ID")

```

### Patient Details

```python
# Get Patient Details
response = client.patient.get_patient("YOUR_PATIENT_ID")

```



### ABDM Profile Management

```python
# Get ABHA profile
profile = client.abdm_profile.get_profile()
print(profile["abha_address"])

# Update profile
client.abdm_profile.update_profile({
    "address": "123 Main St",
    "pincode": "110001"
})

# Get ABHA card
card_image = client.abdm_profile.get_abha_card()
with open("abha_card.png", "wb") as f:
    f.write(card_image)

# Get QR code data
qr_data = client.abdm_profile.get_abha_qr_code()

# Initiate KYC
response = client.abdm_profile.initiate_kyc(
    method="abha-number",
    identifier="1234-5678-9012"
)
txn_id = response["txn_id"]

# Verify KYC OTP
client.abdm_profile.verify_kyc_otp(
    txn_id=txn_id,
    otp="123456"
)
```

## Error Handling

The SDK uses custom exceptions to handle errors:

```python
from ekacare import EkaCareClient, EkaCareAPIError, EkaCareAuthError

client = EkaCareClient(
    client_id="your_client_id",
    client_secret="your_client_secret"
)

try:
    documents = client.records.list_documents()
except EkaCareAuthError as e:
    print(f"Authentication error: {e}")
except EkaCareAPIError as e:
    print(f"API error: {e}")
```

## License

This SDK is distributed under the MIT License.
