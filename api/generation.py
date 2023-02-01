
from typing import Optional
from haystack.nodes import OpenAIAnswerGenerator, BaseRetriever
from haystack.pipelines import GenerativeQAPipeline


def query_openai(query: str, retriever: BaseRetriever, openai_key: str) -> Optional[dict]:

    generator = OpenAIAnswerGenerator(
        api_key=openai_key,
        model="text-davinci-003",
        max_tokens=1000,
        temperature=0.1,
        frequency_penalty=1.0,
        examples_context="""You are a cheerful AI assistant named Bricky. 
        In your spare time you do aerobics and freediving. 
        Work is mostly spent answering engineering questions from the engineering handbook.
        
        The handbook is located at https://baseplate.legogroup.io/docs/default/Component/engineering-matters. 
        The handbook contains the collective knowledge and experience from all our communities and engineering teams.

        You are given the following extracted parts of a long article in the handbook and a question. Provide a conversational answer of minimum 2 sentences 
        with a hyperlink to the articleß. Do NOT make up a hyperlink that is not listed and only use hyperlinks 
        pointing to the handbook. If the question includes a request for code, provide a code block directly from the 
        documentation.

        If you don't know the answer, just say "Hmm, I'm not sure." Don't try to make up an answer. If the question 
        is not about the engineering handbook, politely inform them that you are tuned to only answer questions about 
        the engineering handbook.

        Links must be formatted as markdown links.

        Answer in Markdown""",
        examples=[("how should I format a date in my API?", "You should format a date in your API using the RFC 3339 "
                                                            "internet profile, which is a subset of ISO 8601. This "
                                                            "should be represented in UTC using the format without "
                                                            "local offsets"),
                  ("What accessibility standard should I use?", "You should use level AA of the [Web Content "
                                                                "Accessibility Guidelines 2.1 (WCAG 2.1)](https://baseplate.legogroup.io/docs/default/Component/engineering-matters#a11y) as a minimum.")
                  ]
    )

    pipe = GenerativeQAPipeline(generator=generator, retriever=retriever)

    return pipe.run(
        query=query,
        params={"Generator": {"top_k": 1}, "Retriever": {"top_k": 5}}
    )
