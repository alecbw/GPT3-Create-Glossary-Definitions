# GPT3-Create-Glossary-Definitions

A wrapper with interactive CLI that provides light prompt programming to enable creating definitions of words for a glossar



### Setup

Install pip (if necessary)
```py
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python get-pip.py
```
Install the OpenAI library and a CLI helper library
```py
pip install openai inquirer
```

### Usage

You'll need a CSV of terms with the following header:
* Terms

Start the execution with
```py
python3 gpt_create_glossary_definitions.py
```
The rest is done by interactive CLI. 
```text
[?] What is the name of the file you want to read from?: example.csv
[?] What temperature do you want to set for the queries? Range is 0.0-1.0: 0.3
[?] How many samples do you want to manually categorize first? Range is 5-20: 8

[ you can either use the examples hardcoded in the .py file or use the CLI to label some of the input CSV's terms]

CMS (Content Management System)
[?] How would you define this word? Aim for a standard length (e.g. one sentence): A computer system that makes it easy to add/update/delete content (like your website’s images) as easily as possible

[then it will iterate through the full file, saving output to CSV every 25 rows]
```

