import os
from langchain_community.llms.huggingface_pipeline import HuggingFacePipeline
from langchain_core.output_parsers import StrOutputParser
from live_prompt import calling_prompt
from langchain import LLMChain
from dotenv import load_dotenv

load_dotenv

def calling_llm(category, channel_num, question):
    model_path = 'dPwlek/llama-3.2-3b_korquad'
 
    llm_model = HuggingFacePipeline.from_model_id(
        model_id = model_path,
        task = 'text-generation',
        device=0,
        pipeline_kwargs={'max_new_tokens': 64},
    )
    
    llm_prompt = calling_prompt(category, channel_num)
   
    llm_chain = LLMChain(
        llm = llm_model,
        prompt = llm_prompt
    )
    
    response = llm_chain.predict(input = question)
    
    
    return response.split('Answer:')[2].strip('\n')