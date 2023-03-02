import os
import sys
import re
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from github import Github


BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
CHANNEL_ID = os.environ["SLACK_CHANNEL_ID"]
WORKSPACE = os.environ["SLACK_WORKSPACE"]

GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
USER = os.environ["GITHUB_USER"]
OWNER = os.environ['GITHUB_OWNER']
REPO = os.environ['GITHUB_REPO']

client = WebClient(token=BOT_TOKEN)

# Grab latest slack 100 messages
try:
  result = client.conversations_history(channel=CHANNEL_ID, limit=100)
  messages = result["messages"]
  print("{} messages found".format(len(messages)))
except SlackApiError as e:
  sys.exit("Error: {e}")

if not messages:
  print("No messages found.")
  sys.exit()

g = Github(GITHUB_TOKEN)
repo = g.get_repo(f"{OWNER}/{REPO}")

# get the last issue
# this returns default 30 max 100 issues per page.
issues = repo.get_issues(state="all", sort="created", direction="desc", creator=USER)
last_message_id = issues[0].body[-19:-2] if issues else "p0000000000000000"
pattern = r"p\d{16}"
match = re.match(pattern, last_message_id)

if not match:
  sys.exit("message id not found in the last issue.")

for message in reversed(messages):
  # print(f"type: {message.get('type')}")
  # print(f"subtype: {message.get('subtype')}")
  # print(f"client_msg_id: {message.get('client_msg_id')}")
  # print(f"user: {message.get('user')}")
  # print(f"ts: {message.get('ts')}")
  # print(f"text: {message.get('text')}")
  # print(f"files: {message.get('files')}")
  
  # print(message)

  # Skip existing issues
  message_id = "p{}".format(message['ts'].replace('.', ''))
  if message_id <= last_message_id:
    continue

  # create new issues
  issue_data = {}

  issue_data['title'] = message['text']
  issue_data['body'] = f"Created from Slack message.\n\n## Slack Source\n\nSlack Message ID: [{message_id}](https://{WORKSPACE}/archives/{CHANNEL_ID}/{message_id})."
  # issue_data['labels'] = ["critical"]

  issue = repo.create_issue(**issue_data)

  print(f"Created issue #{issue.number}: {issue.title}")
