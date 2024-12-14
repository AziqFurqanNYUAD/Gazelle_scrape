import requests
from bs4 import BeautifulSoup
import csv
import time

# Function to get the main page of the archive
def get_archive_page():
    try:
        url = "https://www.thegazelle.org/archives"
        response = requests.get(url)
        response.raise_for_status()  # Raises an HTTPError if the status code is 4xx/5xx
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching archive page: {e}")
        return None

# Function to scrape issue numbers and construct URLs
def get_issue_urls():
    archive_page = get_archive_page()
    if not archive_page:
        return []
    
    try:
        soup = BeautifulSoup(archive_page, 'html.parser')
        issue_elements = soup.find_all('h1', class_='font-normal text-2xl mt-1')
        issue_urls = []
        
        for issue in issue_elements:
            issue_text = issue.get_text()
            if issue_text.startswith("Issue"):
                issue_number = issue_text.split()[-1]
                issue_url = f"https://www.thegazelle.org/issue/{issue_number}"
                issue_urls.append((issue_number, issue_url))
        
        return issue_urls
    except Exception as e:
        print(f"Error extracting issue URLs: {e}")
        return []

# Function to scrape projects on each issue page
def scrape_projects_from_issue(issue_number, issue_url):
    try:
        response = requests.get(issue_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all project elements
        project_elements = soup.find_all('div', class_='flex flex-col flex-wrap w-full gap-3 md:gap-2 hover:cursor-pointer w-full w-full')
        projects = []
        
        for project in project_elements:
            title = project.find('h1', class_='text-2xl sm:text-3xl md:text-xl font-semibold capitalize font-lora peer-hover:text-sky-600 hover:text-sky-600 leading-snug md:leading-6')
            description = project.find('p', class_='text-base md:text-sm font-light text-gray-600 hover:text-sky-600')
            
            if title and description:
                project_info = {
                    'issue_number': issue_number,
                    'title': title.get_text(),
                    'description': description.get_text(),
                    'url': f"https://www.thegazelle.org{project.find('a')['href']}"
                }
                projects.append(project_info)
        
        return projects
    except requests.exceptions.RequestException as e:
        print(f"Error fetching issue {issue_number} page: {e}")
        return []
    except Exception as e:
        print(f"Error parsing issue {issue_number} page: {e}")
        return []

# Function to save data to CSV
def save_to_csv(projects):
    try:
        with open('gazelle_projects.csv', mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=['issue_number', 'title', 'description', 'url'])
            writer.writeheader()
            
            for project in projects:
                writer.writerow(project)
        print("Data saved to gazelle_projects.csv")
    except Exception as e:
        print(f"Error saving data to CSV: {e}")

# Main function to collect all issues and their project info, then save to CSV
def main():
    issue_urls = get_issue_urls()
    if not issue_urls:
        print("No issues found. Exiting.")
        return
    
    all_projects = []
    for issue_number, url in issue_urls:
        print(f"Scraping {url}...")
        projects = scrape_projects_from_issue(issue_number, url)
        all_projects.extend(projects)
        time.sleep(1)  # To avoid overwhelming the server with requests
    
    if all_projects:
        save_to_csv(all_projects)
    else:
        print("No project data found.")

if __name__ == "__main__":
    main()
