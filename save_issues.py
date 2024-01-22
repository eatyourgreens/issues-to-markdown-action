import mimetypes
import os
import re
import requests
from pathlib import Path

# create the default image directory, if it doesn't exist
image_root = Path('images')
image_root.mkdir(parents=True, exist_ok=True)
# change this if you want to save the markdown files to a subdirectory
markdown_root = Path.cwd()

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
            image_name = Path(f"{url}").name
            image_folder = image_root / f'issue-{issue_number}'
            image_folder.mkdir(parents=True, exist_ok=True)
            path = image_folder / image_name
            if not path.suffix:
                mime_type = response.headers['Content-Type']
                extension = mimetypes.guess_extension(mime_type)
                path = path.with_suffix(extension)
            path.write_bytes(response.content)
            # return the file path as a string for our markdown file
            return str(path)
        else:
            print(f"Failed to download image: {url}")
            return None
    except Exception as e:
        print(f"Error downloading image {url}: {e}")
        return None

def save_issue(issue):
    try:
        issue_number = issue.get('number', 'Unknown')
        issue_title = issue.get('title', 'Untitled')
        issue_body = issue.get('body', '')
        md_filename = f"{issue_number}_{issue_title}.md".replace(' ', '_')
        md_file = markdown_root / md_filename
        md_file.write_text(f"# {issue_title}\n\n")
        image_urls = extract_image_urls(issue_body)
        for url in image_urls:
            image_path = download_and_save_image(url, issue_number)
            if image_path:
                issue_body = issue_body.replace(url, image_path)
        md_file.write_text(issue_body)
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


