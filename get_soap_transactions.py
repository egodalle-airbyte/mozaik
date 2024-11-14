import requests
import xml.etree.ElementTree as ET
from xml.dom.minidom import parseString
import csv
import os

# Define the API URL
url = "https://37357.magayacloud.com/api/Invoke?Handler=CSSoapService"

# Define the headers for the request
headers = {
    "Content-Type": "text/xml; charset=utf-8"
}


# Function to pretty-print XML
def pretty_print_xml(xml_string):
    dom = parseString(xml_string)
    print(dom.toprettyxml(indent="  "))


# Function to save XML data as CSV
def save_csv_format(xml_string, file_path):
    root = ET.fromstring(xml_string)
    data = {}

    # Collecting all elements and their values in a dictionary
    for elem in root.iter():
        if elem.text and elem.text.strip():
            data[elem.tag] = elem.text.strip()

    # Write data to a CSV file
    with open(file_path, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(data.keys())  # Write CSV headers
        writer.writerow(data.values())  # Write CSV row

    print(f"CSV file saved at {file_path}")


# Define SOAP payload for StartSession
start_session_payload = """<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">
    <s:Body s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
        <q1:StartSession xmlns:q1="urn:CSSoapService">
            <user xsi:type="xsd:string">37357.admin</user>
            <pass xsi:type="xsd:string">VW_wq5!T#&amp;!7</pass>
        </q1:StartSession>
    </s:Body>
</s:Envelope>"""


# Function to make the API call
def call_api(payload):
    response = requests.post(url, headers=headers, data=payload)
    if response.status_code == 200:
        return response.text
    else:
        print("Failed to call API. Status code:", response.status_code)
        return None


# Extract access_key from StartSession response
print("Calling StartSession...")
start_response = call_api(start_session_payload)
if start_response:
    pretty_print_xml(start_response)  # Pretty print StartSession response
    start_tree = ET.fromstring(start_response)
    access_key_element = start_tree.find(".//access_key")
    if access_key_element is None:  # Check with namespace
        namespaces = {'soap': 'http://schemas.xmlsoap.org/soap/envelope/', 'snp': 'urn:CSSoapService'}
        access_key_element = start_tree.find(".//snp:access_key", namespaces)

    if access_key_element is not None and access_key_element.text:
        access_key = access_key_element.text
        print("Access Key Retrieved:", access_key)
    else:
        raise ValueError("Access key not found in StartSession response")

# Define SOAP payloads for subsequent calls, inserting the retrieved access_key dynamically
query_log_payload = f"""<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">
  <s:Body s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
    <q1:QueryLog xmlns:q1="urn:CSSoapService">
      <access_key xsi:type="xsd:int">{access_key}</access_key>
      <start_date xsi:type="xsd:string">2024-07-01</start_date>
      <end_date xsi:type="xsd:string">2024-07-02</end_date>
      <log_entry_type xsi:type="xsd:int">1</log_entry_type>
      <trans_type xsi:type="xsd:string">IN</trans_type>
      <flags xsi:type="xsd:int">0</flags>
    </q1:QueryLog>
  </s:Body>
</s:Envelope>"""

get_transaction_payload = f"""<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">
    <s:Body s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
        <q1:GetTransaction xmlns:q1="urn:CSSoapService">
            <access_key xsi:type="xsd:int">{access_key}</access_key>
            <type xsi:type="xsd:string">IN</type>
            <flags xsi:type="xsd:string">128</flags>
            <number xsi:type="xsd:string">83b49914-3076-441a-9d0a-4b863af97df6</number>
        </q1:GetTransaction>
    </s:Body>
</s:Envelope>"""

end_session_payload = f"""<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">
    <s:Body s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
        <q1:EndSession xmlns:q1="urn:CSSoapService">
            <access_key xsi:type="xsd:int">{access_key}</access_key>
        </q1:EndSession>
    </s:Body>
</s:Envelope>"""

# Call QueryLog
print("\nCalling QueryLog...")
query_log_response = call_api(query_log_payload)
if query_log_response:
    pretty_print_xml(query_log_response)

# Call GetTransaction and save to CSV
print("\nCalling GetTransaction...")
get_transaction_response = call_api(get_transaction_payload)
if get_transaction_response:
    file_path = "/Users/egodalle/mozaik/transactions.csv"
    save_csv_format(get_transaction_response, file_path)

# Call EndSession
print("\nCalling EndSession...")
end_session_response = call_api(end_session_payload)
if end_session_response:
    pretty_print_xml(end_session_response)
