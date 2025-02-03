from lightrag import QueryParam
from live_rag import calling_rag, calling_vector_db
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

async def calling_prompt(category, channel_num):
    db_path = calling_vector_db(category, channel_num)
    rag = calling_rag(db_path)
    
    stt_data = await rag.query('방송에서 말하는 상품과 이벤트를 파악하고 전체적인 내용을 분석해', param=QueryParam(mode='hybrid'))
    recommend_data = await rag.query('방송에서 말하는 상품과 관련된 similarity score 중심 기반 추천시스템 목록들을 파악해', param=QueryParam(mode='hybrid'))
    
    role_prompts = [
        '당신은 라이브 커머스 방송을 시청하는 시청자들에게 정보를 제공하는 기능을 가지고 있습니다.',
        '당신은 사용자와 어떤 내용의 주제이든 상관없이 대화를 나눌 수 있습니다.'
    ] 
    template = '''
        Answer the following question in Korean.
        #Answer: 
    '''
    
    llm_prompt = ChatPromptTemplate.from_messages(
        [
            *[SystemMessagePromptTemplate.from_template(prompt) for prompt in role_prompts],
            SystemMessagePromptTemplate.from_template(stt_data),
            SystemMessagePromptTemplate.from_template(recommend_data),
            SystemMessagePromptTemplate.from_template(template),
            HumanMessagePromptTemplate.from_template('{input}')
        ]
    )
    
    return llm_prompt