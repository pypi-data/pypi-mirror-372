# speedy

📦 A simple Python wrapper for the Speedy.bg REST API

```python
# Example usage of SpeedyAPI
from speedy_bg.api import SpeedyAPI


if __name__ == "__main__":
    api = SpeedyAPI("your_username", "your_password")

    # 1) Find a country
    country = api.find_country(name="BULGARIA")
    print("Country:", country)

    # 2) Get contract clients (useful to know your clientId)
    clients = api.get_contract_clients()
    print("Clients:", clients)

    # 3) Find site by post code
    site = api.find_site(country_id=100, post_code="1000")  # 100 = Bulgaria ID
    print("Site by postcode:", site)

    # 4) Find office in Sofia
    office = api.find_office(name="SOFIA")
    print("Offices:", office)

    # 5) Create shipment
    sender = {
        "clientId": 123456,  # from get_contract_clients
        "contactName": "Sender Name",
        "phone1": "0888123456"
    }
    recipient = {
        "privatePerson": True,
        "contactName": "John Doe",
        "phone1": "0899123456",
        "addressLocation": {
            "countryId": 100,
            "siteId": 68134  # e.g. Sofia
        }
    }
    service = {"serviceId": 505}   # example: delivery service ID
    content = {"parcelsCount": 1, "totalWeight": 2.5}
    payment = {"courierServicePayer": "SENDER"}

    shipment = api.create_shipment(sender, recipient, service, content, payment)
    print("Created shipment:", shipment)

    # 6) Print waybill as PDF
    if "parcels" in shipment:
        parcel_ids = [p["id"] for p in shipment["parcels"]]
        pdf_data = api.print_waybill(parcel_ids)
        with open("waybill.pdf", "wb") as f:
            f.write(pdf_data)
        print("Waybill saved as waybill.pdf")

    # 7) Calculate price for a destination
    calc = api.calculate(sender={"clientId": 123456},
                         recipient={"privatePerson": True, "addressLocation": {"countryId": 100, "siteId": 68134}})
    print("Calculation:", calc)
```
