import os
import re
import requests

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
            image_name = url.split("/")[-1]
            image_folder = f'images/issue-{issue_number}'
            if not os.path.exists(image_folder):
                os.makedirs(image_folder)
            path = os.path.join(image_folder, image_name)
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
        filename = f"{issue.get('number', 'Unknown')}_{title}.md"
        with open(filename, 'w') as file:
            file.write(f"# {issue.get('title', 'Untitled')}\n\n")
            body = issue.get('body', '')
            image_urls = extract_image_urls(body)
            for url in image_urls:
                image_path = download_and_save_image(url, issue['number'])
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


