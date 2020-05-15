import os
import sys

sys.path.append("/home/hero/.local/lib/python3.5/site-packages")
import argparse


def add_doc(org_name, git_token, service_name):
    from github import Github, InputGitAuthor
    g = Github(git_token)
    org = g.get_organization(org_name)
    repository = org.get_repo(service_name)
    read_me_file = open("README.md", "r")
    content = read_me_file.read()

    author = InputGitAuthor("Architects Bot", "architect.gdp@allainz.com")
    response = repository.create_file(path="README.md", message="Add ReadMe", content=content, branch="master",
                                      author=author)

    read_api_file = open("Apis/IrisApi.md", "r")
    api_content = read_api_file.read()
    response = repository.create_file(path="Apis/README.md", message="Add API", content=api_content, branch="master",
                                      author=author)
    print(response)


def main(org_name, git_token, service_name):
    from atlassian import Confluence

    wiki = "https://allianz.atlassian.net/wiki"
    user = "wu.qunfei@gmail.com"
    password = "LarHDKttUiWfRgV60a9x9D55"
    confluence = Confluence(url=wiki, username=user, password=password)

    os.system("java -jar openapi-generator-cli-4.3.1.jar generate -i openapi.yaml -g markdown")
    file_handler = open("README.md", "r")
    body = file_handler.read()
    status = confluence.update_or_create(parent_id=146866244, title="IRIS Service", body=body)
    print(status)
    add_doc(org_name, git_token, service_name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--service_name', type=str, default='iris-service')
    parser.add_argument('--git_token', type=str)
    parser.add_argument('--org_name', type=str, default='aistrawberry')
    args = parser.parse_args()
    if os.path.exists("openapi.yaml") and os.path.getsize("openapi.yaml") > 100:
        main(args.org_name, args.git_token, args.service_name)
