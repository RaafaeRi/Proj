import requests

company = input("Enter company to search for: ").lower().strip()

url = f"https://boards-api.greenhouse.io/v1/boards/{company}/jobs"

response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    print(f'Searching for {company}...')
    print("-------------------------------------")
    counter = 0
    for job in data["jobs"]:
        title = job["title"]
        titleWords = title.lower().split()
        location = job["location"]["name"]


        if "intern" in titleWords:
            print(title)
            print(location)
            print(job["absolute_url"])
            print()
            counter += 1
    
    print("-------------------------------------")
    print(f"Found {counter} internship(s).")
else:
    print("Request failed:", response.status_code)