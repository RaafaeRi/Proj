import requests
import json

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

internships = []

try:
    with open("internships.json", "r") as file:
        oldInternships = json.load(file)
except FileNotFoundError:
    oldInternships = []

oldUrls = []
for internship in oldInternships:
    oldUrls.append(internship["url"])

newInternships = []
for company in companies:
    url = f"https://boards-api.greenhouse.io/v1/boards/{company}/jobs"

    response = requests.get(url, timeout=10)
    
    print(f'Searching for {company}...')
    if response.status_code == 200:
        data = response.json()
        
        for job in data["jobs"]:
            title = job["title"]
            cleanTitle = title.lower().replace(",", "").replace("-", " ").replace("/", " ")
            titleWords = cleanTitle.split()
            location = job["location"]["name"]


            hasInternWord = any(word in titleWords for word in internWords)
            hasSoftwareWord = any(word in titleWords for word in softwareWords)
            if hasInternWord and hasSoftwareWord:
                internship = {
                    "company": company.title(),
                    "title": title,
                    "location": location,
                    "url": job["absolute_url"]
                }
                internships.append(internship)

                for internship in newInternships:
                    if internship["url"] not in oldUrls:
                        newInternships.append(internship)
    else:
        print(f"Request failed for {company}")

print("-------------------------------------")

for internship in newInternships:
    print(internship["company"].title())
    print(internship["title"])
    print(internship["location"])
    print(internship["url"])
    print()

print("-------------------------------------")
print(f"Found {len(newInternships)} new internships.")

with open("internships.json", "w") as file:
    json.dump(internships, file, indent=4)

print("Results saved.")