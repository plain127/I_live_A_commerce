from transformers import TextStreamer
import pandas as pd
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
)


# 이전에 처리된 댓글의 식별 정보를 저장
processed_comments = set()


def load_new_comments(category, channel):
    """새로운 댓글을 로드합니다."""
    df = pd.read_csv(f'./DB/{category}_{channel}/{category}_{channel}_comment_log.csv')
    new_comments = []

    for _, row in df.iterrows():
        comment = row['댓글']
        timestamp = row['시간']
        id = f'{timestamp}_{comment}'

        if id not in processed_comments:
            if comment == 'empty':
                new_comments.append('무반응')
            new_comments.append(comment)
            processed_comments.add(id)

    return new_comments


def analyze_sentiment(comment, tokenizer, model):
    """단일 댓글의 감정을 분석합니다."""
    prompt = f"""
        Determine the emotion of the following sentence. The emotion must be classified into one of the following categories: 중립, 긍정, 부정 
        For each sentence, output only the emotion as a single word.
        ### Instruction:
        {comment}

        ### Response:"""

    encoded_input = tokenizer(prompt, return_tensors="pt", add_special_tokens=True)

    # 모델이 위치한 디바이스로 입력 데이터를 이동
    device = next(model.parameters()).device
    model_inputs = encoded_input.to(device)

    text_streamer = TextStreamer(tokenizer)
    generated_ids = model.generate(
        **model_inputs,
        max_new_tokens=3,
        do_sample=True,
        pad_token_id=tokenizer.eos_token_id,
        streamer=text_streamer,
    )

    decoded_output = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)
    # Prompt를 제거하고 감정 분석 결과만 반환
    return decoded_output[0].replace(prompt, "").strip()


def calculate_sentiment_score(comments, tokenizer, model):
    """댓글 목록에 대해 감정 분석을 수행하고 점수를 계산합니다."""
    scores = []
    for comment in comments:
        sentiment = analyze_sentiment(comment, tokenizer, model)  # 감정 분석 수행
        if sentiment == '긍정':
            scores.append(1)
        elif sentiment == '중립':
            scores.append(0.5)
        elif sentiment == '부정':
            scores.append(0)

    return scores


def run_sentiment_score(category, channel):
    """댓글을 로드하고 감정 점수 평균을 계산합니다."""

    # 1. 새로운 댓글 로드
    new_comments = load_new_comments(category, channel)

    if not new_comments:
        print("새로운 댓글이 없습니다.")
        return None

    # 2. 댓글 점수 계산
    device = "cuda:1" if torch.cuda.device_count() > 1 else "cuda:0"
    checkpoint_path = "/home/metaai2/jinjoo_work/llama_finetuning/sentiment/llama3.2-3b-sentiment-2"
    base_model = "Bllossom/llama-3.2-Korean-Bllossom-3B"
    
    # 모델과 토크나이저 로드 및 디바이스 설정
    sent_model = AutoModelForCausalLM.from_pretrained(checkpoint_path).to(device).half()
    sent_tokenizer = AutoTokenizer.from_pretrained(base_model, trust_remote_code=True)

    scores = calculate_sentiment_score(new_comments, sent_tokenizer, sent_model)

    # 3. 평균 점수 계산
    if scores:
        average_score = sum(scores) / len(scores)
        print(f"평균 점수: {average_score}")
    else:
        print("점수를 계산할 댓글이 없습니다.")
        return None

    # 4. 점수 저장
    save_average_score(category, channel, average_score)

    return average_score


def save_average_score(category, channel, score):
    """평균 점수를 저장합니다."""
    result_file = f'./DB/{category}_{channel}/sentiment_scores.csv'
    df = pd.DataFrame([{"category": category, "channel": channel, "score": score}])
    df.to_csv(result_file, index=False)
    print(f"평균 점수가 {result_file}에 저장되었습니다.")


# 예제 실행
#if __name__ == "__main__":
#    category = 6
#    channel = 1562209
#    run_sentiment_score(category, channel)

