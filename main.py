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
    "nvidia",
    "lockheed martin",
    "boeing"
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


def loadInternships():
    try:
        with open("internships.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def getOldUrls(oldInternships):
    oldUrls = []

    for internship in oldInternships:
        oldUrls.append(internship['url'])
    
    return oldUrls

def matchesInternship(title):
    cleanTitle = title.lower().replace(",", "").replace("-", " ").replace("/", " ")

    titleWords = cleanTitle.split()

    hasInternWord = any(word in titleWords for word in internWords)

    hasSoftwareWord = any(word in titleWords for word in softwareWords)

    return hasInternWord and hasSoftwareWord

def searchCompany(company):
    companyInternships = []

    url = f"https://boards-api.greenhouse.io/v1/boards/{company}/jobs"
    print(f'Searching for {company}...')

    response = requests.get(url, timeout=10)

    if response.status_code != 200:
        print(f"Request failed for {company}")
        return companyInternships

    data = response.json()

    for job in data["jobs"]:
            title = job["title"]

            location = job["location"]["name"]
            if matchesInternship(title):
                internship = {
                    "company": company.title(),
                    "title": title,
                    "location": location,
                    "url": job["absolute_url"]
                }

                companyInternships.append(internship)
    
    return companyInternships

def companySearching(companies):
    internships = []

    for company in companies:
        companyInternships = searchCompany(company)
        internships.extend(companyInternships)
    
    return internships

def findNewInternships(internships, oldUrls):
    newInternships = []

    for internship in internships:
        if internship['url'] not in oldUrls:
            newInternships.append(internship)
    
    return newInternships

def printInternships(internships):
    print("-------------------------------------")

    for internship in internships:
        print(internship["company"])
        print(internship["title"])
        print(internship["location"])
        print(internship["url"])
        print()

    print("-------------------------------------")
    print(f"Found {len(internships)} new internships.")

def saveInternships(internships):
    with open("internships.json", "w") as file:
        json.dump(internships, file, indent=4)

    print("Results saved.")

oldInternships = loadInternships()
oldUrls = getOldUrls(oldInternships)

internships = companySearching(companies)
newInternships = findNewInternships(internships, oldUrls)

printInternships(newInternships)
saveInternships(internships)