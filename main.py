import requests

companies = [
    "stripe",
    "mongodb",
    "openai",
    "cloudflare",
    "plaid",
    "discord",
    "notion",
]

internWords = [
    "intern",
    "internship",
    "internships",
]

softwareWords = [
    "software",
    "swe",
    "developer",
    "development",
    "frontend",
    "backend",
    "fullstack",
    "firmware",
    "embedded"
]


for company in companies:
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


            hasInternWord = any(word in titleWords for word in internWords)
            hasSoftwareWord = any(word in titleWords for word in softwareWords)
            if hasInternWord and hasSoftwareWord:
                print(title)
                print(location)
                print(job['absolute_url'])
                print()
                counter += 1

                
        print("-------------------------------------")
        print(f"Found {counter} internship(s).")
        print("\n")
    else:
        print(f"Request failed for {company}")

