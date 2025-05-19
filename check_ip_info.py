import requests, argparse

parser = argparse.ArgumentParser(description="Fetch IP information from ipinfo.io")
parser.add_argument("ip", help="IP address to fetch information for")
parser.add_argument("output_type", help="Output type: json or text", choices=["json", "text"])
# Parse the arguments
args = parser.parse_args()


def fetch_ip_info(ip: str):
    # Fetch IP information from an external API
    response = requests.get(ip)

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return "Failed to retrieve data:"


url = "https://ipinfo.io/"+args.ip+"/json"
data = fetch_ip_info(url)
if args.output_type == "json":
    print(data)
else:
    # Print the data in a readable format
    print("IP Information:")
    data = fetch_ip_info(url)
    for key, value in data.items():
        print(f"{key}: {value}")
