from dotenv import load_dotenv
import time
import os

def llm_factory(provider_and_model: str, template, content: str):

    load_dotenv()  # Loads variables from .env into environment
    provider = provider_and_model.split(":")[0].lower()
    model = provider_and_model.split(":")[1].lower()
    prompt = template.substitute(content=content)

    if provider == "openai":
        import openai
        import os
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are an invoice extracter."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.0,
        max_tokens=300,
    )
        return response.choices[0].message.content
    elif provider == "huggingface":
        from transformers import pipeline

        generator = pipeline(
        "text-generation",
        model=model,
        device_map="auto"  # uses GPU if available
        )

        response = generator(
            prompt,
            max_new_tokens=300,
            temperature=0.0
        )

        print(response[0]["generated_text"])
        return response[0]["generated_text"]
    elif provider_and_model.startswith("langchainAQ:"):
        from langchain_community.chat_models import ChatOpenAI
        from langchain.chains.question_answering import load_qa_chain
        from langchain.schema import Document

        if "OPENAI_API_KEY" not in os.environ:
            raise ValueError("OPENAI_API_KEY is not set in environment variables.")

        openai_model_name = provider_and_model.split("langchain:")[1]
        llm = ChatOpenAI(model=openai_model_name, temperature=0)

        # Your input text as a string
        input_text = "Hugging Face is a company based in New York that specializes in natural language processing."

        # Wrap input text in a Document (LangChain expects docs)
        docs = [Document(page_content=input_text)]

        # Load a QA chain with "stuff" method (no vectorstore, no retrieval)
        qa_chain = load_qa_chain(llm, chain_type="stuff")

        # Your question
        question = "Where is Hugging Face based?"

        start = time.time()
        result = qa_chain.run(input_documents=docs, question=question)
        end = time.time()

        print(f"Question answering time: {end - start:.2f} seconds")
        print("Answer:", result)

    elif provider == "huggingface":
        from transformers import pipeline, AutoModelForQuestionAnswering, AutoTokenizer
        from huggingface_hub import snapshot_download
        i
        model_name = model
        cache_dir = "./hf_cache"

        start = time.time()
        local_path = snapshot_download(model_name, cache_dir=cache_dir, resume_download=False)
        end = time.time()
        print(f"Model download time: {end - start:.2f} seconds")

        if os.path.exists(local_path):
            print("Model is already downloaded.")
        else:
            print("Model is not downloaded.")

        start = time.time()
        model = AutoModelForQuestionAnswering.from_pretrained(model_name, cache_dir=cache_dir)
        end = time.time()
        print(f"Model loading time: {end - start:.2f} seconds")

        start = time.time()
        tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=cache_dir)
        end = time.time()
        print(f"Tokenizer loading time: {end - start:.2f} seconds")

        start = time.time()
        qa_pipeline = pipeline(
            "question-answering",
            model=model,
            tokenizer=tokenizer,
            do_sample=False,
        )
        end = time.time()
        print(f"Pipeline setup time: {end - start:.2f} seconds")

        start = time.time()
        result = qa_pipeline(question=template.template, context=content)
        end = time.time()
        print(f"Question answering time: {end - start:.2f} seconds")

        print("Answer:", result['answer'])
        print("Confidence score:", result['score'])
        print(content[result['start']:result['end']])  # prints "New York"    else:
    elif provider == "databricks":
        from openai import OpenAI
        import os

        # How to get your Databricks token: https://docs.databricks.com/en/dev-tools/auth/pat.html
        DATABRICKS_TOKEN = os.environ.get('DATABRICKS_TOKEN')
        # Alternatively in a Databricks notebook you can use this:
        # DATABRICKS_TOKEN = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().get()

        client = OpenAI(
            api_key=DATABRICKS_TOKEN,
            base_url="https://adb-1162512624986336.16.azuredatabricks.net/serving-endpoints"
        )

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are an AI assistant"
                },
                {
                    "role": "user",
                    "content": "Tell me about Large Language Models"
                }
            ],
            model="databricks-meta-llama-3-3-70b-instruct",
            max_tokens=256
        )

        print(chat_completion.choices[0].message.content)


    else:
        raise ValueError(
            f"Unsupported provider {model}. Use 'openai:' or 'huggingface:' prefix."
        )
