from transformers import PreTrainedTokenizerFast, BartForConditionalGeneration

def clean_summary(summary):
    """
    요약 결과를 깔끔하게 정리
    """
    summary = summary.strip()
    if not summary.endswith(('.', '!', '?')):
        summary += '.'
    return summary

def generate_summary(file_path, model, tokenizer, max_input_length=1024, max_output_length=300):
    """
    파일에서 텍스트를 읽고 요약을 생성
    """
    try:
        # 파일 읽기
        with open(file_path, "r", encoding="utf-8") as f:
            input_text = f.read().strip()
    except FileNotFoundError:
        print(f"파일을 찾을 수 없습니다: {file_path}")
        return None

    # 텍스트 토큰화
    inputs = tokenizer(
        input_text,
        return_tensors="pt",
        padding="max_length",
        truncation=True,
        max_length=max_input_length,
    )

    # 모델로 요약 생성
    summary_ids = model.generate(
        input_ids=inputs["input_ids"],
        attention_mask=inputs["attention_mask"],
        bos_token_id=model.config.bos_token_id,
        eos_token_id=model.config.eos_token_id,
        max_length=max_output_length,
        min_length=12,
        length_penalty=1.5,
        num_beams=4,
        repetition_penalty=1.3,
        no_repeat_ngram_size=3,
        early_stopping=True,
    )

    # 요약 디코딩 및 정리
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return clean_summary(summary)

def run_summary(category, channel_num):
    stt_path = f'DB/{category}_{channel_num}/streaming_{category}_{channel_num}.txt'
    
    tokenizer = PreTrainedTokenizerFast.from_pretrained("EbanLee/kobart-summary-v3")
    model = BartForConditionalGeneration.from_pretrained("EbanLee/kobart-summary-v3")
    
    summ = generate_summary(stt_path, model, tokenizer)
    
    return summ