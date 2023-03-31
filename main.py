raise AssertionError(
  "unfortuantely this suffers from a showstopping bug that's a year old https://github.com/arXiv/arxiv-search/issues/292 and therefore is going to be missing papers relevant to the topic you want"
)

import urllib.request
import feedparser
import time
import openai
import os


def is_relevant(abstract):
  response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[{
      "role": "system",
      "content": "You are a helpful assistant."
    }, {
      "role":
      "user",
      "content":
      f"Here is an abstract: '{abstract}'. Please start your response with 'Yes' if it contains key concepts related to hierarchical representation of sound for ML papers, such as hierarchy, long-range structure, long-term structure, or coarse-to-fine representations. Otherwise, start with 'No'."
    }])
  answer = response['choices'][0]['message']['content'].strip().lower()
  return answer.startswith("yes")


# Your OpenAI API key
openai.api_key = os.environ['OPENAI_KEY']


# The original script to get unique papers
def get_author_papers(author_name):
  search_url = f'http://export.arxiv.org/api/query?search_query=au:{urllib.parse.quote(author_name)}'
  search_data = urllib.request.urlopen(search_url)
  search_feed = feedparser.parse(search_data.read().decode('utf-8'))
  return search_feed.entries


# Get the paper details
paper_url = 'http://export.arxiv.org/api/query?id_list=2209.03143'
paper_data = urllib.request.urlopen(paper_url)
paper_feed = feedparser.parse(paper_data.read().decode('utf-8'))

# Extract the authors' names
authors = [author.name for author in paper_feed.entries[0].authors]

# Get papers for all authors while respecting the rate limit
all_papers = []
for author in authors:
  time.sleep(3)  # Wait for 3 seconds to respect the API rate limit
  author_papers = get_author_papers(author)
  all_papers.extend(author_papers)

# Remove duplicates
unique_papers = {paper.id: paper for paper in all_papers}.values()

# Filter relevant papers and print their information
relevant_papers = []
for paper in unique_papers:
  if is_relevant(paper.summary):
    relevant_papers.append(paper)
    print(
      f"Title: {paper.title}\nAbstract: {paper.summary}\nURL: https://arxiv.org/abs/{paper.id}\n"
    )
  else:
    print(
      f"found irrelevant paper {paper.title} at url https://arxiv.org/abs/{paper.id}"
    )
  time.sleep(3)  # Wait for 3 seconds to respect the API rate limit

print(f"Total relevant papers found: {len(relevant_papers)}")
