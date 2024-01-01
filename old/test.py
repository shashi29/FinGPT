# import openai
# # openai.api_key = "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"

# from openai import OpenAI
# client = OpenAI()

# completion = client.chat.completions.create(
#   model="gpt-4",
#   messages=[
#     {"role": "system", "content": "You are a helpful assistant."},
#     {"role": "user", "content": "Hello!"}
#   ]
# )

# print(completion.choices[0].message)

# from langchain.chat_models import ChatOpenAI
# from langchain.prompts import ChatPromptTemplate
# from langchain_core.output_parsers import StrOutputParser
# from langchain_core.runnables import RunnablePassthrough


# prompt = ChatPromptTemplate.from_template("Extract insight from this data {topic}")
# model = ChatOpenAI(model="gpt-4")
# output_parser = StrOutputParser()

# chain = (
#     {"topic": RunnablePassthrough()} 
#     | prompt
#     | model
#     | output_parser
# )

# print(chain.invoke(''''''))

import streamlit as st
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# Define the ChatPromptTemplate
prompt = ChatPromptTemplate.from_template(''' 
Objective:
This financial analysis aims to uncover insights and address resource allocation and risk issues. Key findings: discrepancies in resource allocation efficiency and elevated risk levels. Solutions involve optimizing resource allocation and implementing risk mitigation measures. Assumptions: historical trends predict future performance, operational adjustments enhance efficiency, and risk mitigation reduces exposure. Central data point: key performance metrics, crucial for assessing organizational health.
Note: When giving insight , if possible use number or percentage
{topic}''')

# Define the ChatOpenAI model
model = ChatOpenAI(model="gpt-4", temperature=0.2)

# Define the output parser
output_parser = StrOutputParser()

# Streamlit app
def main():
    st.title("Insight Extraction from Data App")

    # Upload CSV file
    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

    if uploaded_file is not None:
        # Read the uploaded CSV file
        data = uploaded_file.read()

        # Invoke the LangChain pipeline with the data
        result = chain.invoke(data)

        # Display the result
        st.write("Insight Extracted:")
        st.write(result)

if __name__ == "__main__":
    # Define the LangChain pipeline
    chain = (
        {"topic": RunnablePassthrough()} 
        | prompt
        | model
        | output_parser
    )

    # Run the Streamlit app
    main()
