import os
import re
import requests
from pathlib import Path, PurePath

# create the default image directory, if it doesn't exist
image_root = Path('images').mkdir(parents=True, exist_ok=True)
# edit this if you want to save the markdown files to a subdirectory
markdown_root = Path('./').mkdir(parents=True, exist_ok=True)

def get_issues(repo, token, label):
    url = f"https://api.github.com/repos/{repo}/issues"
    headers = {'Authorization': f'token {token}'}
    params = {'state': 'all', 'labels': label}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        raise Exception(f"GitHub API error: {response.status_code}")
    return response.json()

def extract_image_urls(issue_body):
    # Regular expression to find Markdown image syntax
    pattern = r'!\[.*?\]\((.*?)\)'
    urls = re.findall(pattern, issue_body)
    return urls

def download_and_save_image(url, issue_number):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            image_name = PurePath(url).name
            image_folder = image_root / f'issue-{issue_number}'
            image_folder.mkdir(parents=True, exist_ok=True)
            path = image_folder / image_name
            with open(path, 'wb') as file:
                file.write(response.content)
            return path
        else:
            print(f"Failed to download image: {url}")
            return None
    except Exception as e:
        print(f"Error downloading image {url}: {e}")
        return None

def save_issue(issue):
    try:
        title = issue.get('title', 'Untitled').replace(' ', '_')
        issue_number = issue.get('number', 'Unknown')
        issue_title = issue.get('title', 'Untitled')
        md_file = markdown_root / f"{issue_number}_{title}.md"
        with open(md_file, 'w') as file:
            file.write(f"# {issue_title}\n\n")
            body = issue.get('body', '')
            image_urls = extract_image_urls(body)
            for url in image_urls:
                image_path = download_and_save_image(url, issue_number)
                if image_path:
                    body = body.replace(url, image_path)
            file.write(body)
    except Exception as e:
        print(f"Error processing issue: {e}")

def main():
    repo = 'eatyourgreens/issues-to-markdown-action'  # Replace with your username/repo
    token = os.getenv('GITHUB_TOKEN')
    try:
        issues = get_issues(repo, token, 'done')
        for issue in issues:
            save_issue(issue)
    except Exception as e:
        print(f"Error fetching issues: {e}")

if __name__ == "__main__":
    main()


