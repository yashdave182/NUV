from fastapi.testclient import TestClient
from agritech_api.main import app

client = TestClient(app)

def test_send_otp():
    response = client.post("/auth/otp/send", json={"phone": "9099314955", "purpose": "login"})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["otp_code"] == "123456"

def test_verify_otp_existing_user():
    response = client.post("/auth/otp/verify", json={"phone": "9099314955", "otp_code": "123456"})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "access_token" in data
    assert data["user"]["name"] == "Ramesh Patel"
    assert data["user"]["state"] == "Gujarat"

def test_verify_otp_invalid_code():
    response = client.post("/auth/otp/verify", json={"phone": "9099314955", "otp_code": "999999"})
    assert response.status_code == 400

def test_login_pin():
    response = client.post("/auth/login/pin", json={"phone": "9099314955", "pin": "1234"})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["user"]["phone"] == "9099314955"

def test_register_farmer():
    payload = {
        "phone": "9123456789",
        "name": "Kishan Patel",
        "state": "Gujarat",
        "district": "Vadodara",
        "language": "Gujarati",
        "land_holding_acres": 4.2,
        "soil_type": "alluvial",
        "primary_crops": ["cotton", "maize"],
        "pin": "4321"
    }
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["user"]["name"] == "Kishan Patel"
    assert data["user"]["phone"] == "9123456789"

def test_get_me():
    response = client.get("/auth/me?phone=9123456789")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Kishan Patel"

if __name__ == "__main__":
    test_send_otp()
    test_verify_otp_existing_user()
    test_verify_otp_invalid_code()
    test_login_pin()
    test_register_farmer()
    test_get_me()
    print("ALL AUTHENTICATION BACKEND TESTS PASSED SUCCESSFULLY!")

