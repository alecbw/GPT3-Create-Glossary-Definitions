from gpt_utils import * # local import

import os
import sys
import random
import csv

import inquirer
import openai



def read_input_csv(filename, necessary_csv_headers):
    with open(filename) as f:
        file_as_list_of_dictionaries = [{k:v for k, v in row.items()} for row in csv.DictReader(f, skipinitialspace=True)] # LOD

    if any(x for x in necessary_csv_headers if x not in file_as_list_of_dictionaries[0].keys()):
        sys.exit(f"Exiting. Your CSV needs to have these headers: {necessary_csv_headers}")
    return file_as_list_of_dictionaries


def write_output_csv(filename, output_lod):
    with open("Output " + filename, 'w') as output_file:
        dict_writer = csv.DictWriter(output_file, output_lod[0].keys())
        dict_writer.writeheader()
        dict_writer.writerows(output_lod)
    print("Write to csv was successful\n")


def prompt_user_response(response_type):
    question_bank = {
        "GPT": "Enter your secret GPT Key (to disable this, set it as an environment variable)",
        "filename": "What is the name of the file you want to read from?",
        "description": "How would you define this word? Aim for a standard length (e.g. one sentence)",
        "temperature": "How creative do you want the tag results to be? Range is 0.0-1.0. 0.3 seems to work well",
        "training_samples": "How many samples do you want to manually categorize first? Range is 5-20",
        "examples": "Do you want to use the existing (in-code) examples? Enter No to set your own",
    }

    questions = [inquirer.Text(response_type, message=question_bank[response_type])]
    answers = inquirer.prompt(questions)
    return answers[response_type.lower()]


def add_glossary_examples(gpt):
    gpt.add_example(Example("CDN (Content Delivery Network):", "A network of computer systems that aims to deliver content (like your website’s images) to end users as fast and reliably as possible."))
    gpt.add_example(Example("CMS (Content Management System):", "A computer system that makes it easy to add/update/delete content (like your website’s images) as easily as possible."))
    gpt.add_example(Example("CI (Continuous Integration):", "Automatically detecting code changes (e.g. through a Pull Request) and running a suite of tests against code before it is deployed"))
    gpt.add_example(Example("CD (Continous Delivery):", "The process of building, packaging, and (generally) deploying code to the production environment. CI and CD are commonly coupled to create a deployment pipeline"))
    gpt.add_example(Example("Metadata:", "This is the data about your data. For example for videos on a site like YouTube, metadata is the title, description, thumbnail, and tags"))
    gpt.add_example(Example("Local:", "On your computer (a local environment is effectively the opposite of the production environment)"))
    gpt.add_example(Example("Endpoint:", "The specific link that performs a specific API function. API providers dictate which endpoints exist and are publicly available."))
    gpt.add_example(Example("VM (Virtual Machine):", "A partition of a larger server that emulates a ‘regular’ computing environment. More here"))
    gpt.add_example(Example("NoSQL (Not Only SQL):", "Databases that store and retrieve data via key value. Different from relational databases in that NoSQL DB's don't have a heavily structured schema and don't support ad hoc queries"))
    gpt.add_example(Example("CRUD (Create/Read/Update/Delete):", "the basic functions of a database. So-called CRUD apps allow users to perform these actions through a GUI"))

    return gpt


if __name__ == "__main__":
    GPT_KEY = os.getenv("GPT_KEY") if os.getenv("GPT_KEY") else prompt_user_response('GPT')
    set_openai_key(GPT_KEY)

    filename = prompt_user_response('filename')
    filename = filename + ".csv" if ".csv" not in filename else filename

    necessary_csv_headers = ["Terms"]
    input_lod = read_input_csv(filename, necessary_csv_headers)
    print(f"Length of input CSV is: {len(input_lod)}")

    temperature = prompt_user_response('temperature')

    gpt = GPT(engine="davinci",
          temperature=float(temperature),
          # stop="\n", # TODO
          max_tokens=30)

    example_option = prompt_user_response('examples')
    
    if example_option not in ["No", "no", "N", "n", "False", False]:
        gpt = add_glossary_examples(gpt)
    else:
        training_samples = prompt_user_response('training_samples')

        # We pick random rows to manually tag as examples
        random_row_numbers = random.sample(range(0, len(input_lod)), int(training_samples))
        for n in random_row_numbers:
            print(f"{input_lod[n]['Terms']}")
            tags = prompt_user_response("description")
            gpt.add_example(Example(input_lod[n]['Terms'], tags))

    for n, row in enumerate(input_lod):
        if not row['Terms']:
            print('skipping empty row')
            continue

        gpt_result = gpt.submit_request(row['Terms'])
        gpt_tags = gpt_result.get("choices", [])[0].get("text").replace("output: ", "")
        input_lod[n]["GPT-Tags"] = gpt_tags
        print(row['Terms'] + " - " + gpt_tags)

        if n != 0 and n % 25 == 0:
            write_output_csv(filename, input_lod)

    write_output_csv(filename, input_lod)