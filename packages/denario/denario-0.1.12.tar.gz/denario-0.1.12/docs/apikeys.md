# API keys

## OpenAI API keys

In order to get an OpenAI API key go to [this website](https://platform.openai.com/api-keys) and get your OpenAI API key.

## Gemini API keys

To get a Gemini API key go to [this website](https://ai.google.dev/gemini-api/docs/api-key) and click in the first link (Google AI studio). You can then get your API key there.

## Anthropic API keys

To get an Anthropic API key go to [this website](https://console.anthropic.com/settings/keys) and get your Anthropic API key there.

## Perplexity API keys

To get a perplexity API key go to [this wbsite](https://docs.perplexity.ai/getting-started/quickstart) and get your Perplexity API key there.

## Vertex AI

In Denario, agents built with LangGraph can be run using a Gemini API key (see above on how to create a Gemini API Key). However, agents built using [AG2](https://ag2.ai/), require a different setup to access Gemini models. 

In this case, you need to access the Gemini models via the [Vertex AI](https://cloud.google.com/vertex-ai?hl=en) API. 

If you plan to run the analysis module with Gemini models (necessarily accessed through Vertex AI), e.g.:

```python
den.get_results(engineer_model='gemini-2.5-pro',
	        researcher_model='gemini-2.5-pro')
```

you need to:
- create Google service account key fil (a JSON file – see instructions below)
- download it on the machine where you run Denario
- rename it `gemini.json` 
- set a `GOOGLE_APPLICATION_CREDENTIALS` environment variable with the path to that file, i.e., 

```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/gemini.json
```

Whenever you run Denario and need Vertex AI access, this environment variable should be correctly set. 


To enable Vertex AI, you first need a Google account (if you don't yet have a Google account, visit [this page](https://www.google.com/intl/en-GB/account/about/) and create one).

- Log into Google Cloud: https://console.cloud.google.com/
- Create a project
- Go to IAM & Admin
- Go to Service Accounts
- Create a Service Account
- Choose a name
- Create and Continue
- Grant the "Vertex AI User" role
- Click Continue and then Done
- Click on the three dots and Manage keys
- Add key --> Create new key --> JSON --> Create
- Change the name of that file to gemini.json

## Where to put the keys?

In order to use the different keys, you can

1. Add these lines (inserting your API keys) to your ~/.bashrc file. If you dont have an optional API key (e.g. Anthropic), leave the API key value blank.

```sh
export GOOGLE_API_KEY=your_gemini_api_key
export GOOGLE_APPLICATION_CREDENTIALS=path_to_your_gemini.json_file
export OPENAI_API_KEY=your_openai_api_key
export PERPLEXITY_API_KEY=your_perplexity_api_key
export ANTHROPIC_API_KEY=your_anthropic_api_key
```

2. Copy and paste these lines (inserting your API keys) to your terminal. If you dont have an optional API key (e.g. Anthropic), leave the API key value blank.

```sh
export GOOGLE_API_KEY=your_gemini_api_key
export GOOGLE_APPLICATION_CREDENTIALS=path_to_your_gemini.json_file
export OPENAI_API_KEY=your_openai_api_key
export PERPLEXITY_API_KEY=your_perplexity_api_key
export ANTHROPIC_API_KEY=your_anthropic_api_key
```

3. In the folder where you plan to run Denario, create a ``.env`` file and put inside that file this:

```sh
GOOGLE_API_KEY=your_gemini_api_key
GOOGLE_APPLICATION_CREDENTIALS=path_to_your_gemini.json_file
OPENAI_API_KEY=your_openai_api_key
PERPLEXITY_API_KEY=your_perplexity_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
```