import torch
from moviepy.editor import VideoFileClip
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline

#영상 -> 오디오 추출
def video2voice(category, channel_num):
    video = VideoFileClip(f'DB/{category}_{channel_num}/streaming_{category}_{channel_num}.mp4')
    video.audio.write_audiofile(f'DB/{category}_{channel_num}/streaming_{category}_{channel_num}.mp3')

#오디오 -> 텍스트 추출
def voice2text(category, channel_num):
    video2voice(category, channel_num)
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
    model_id = 'openai/whisper-large-v3'
    
    model = AutoModelForSpeechSeq2Seq.from_pretrained(
        model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
    )
    
    model.to(device)
    processor = AutoProcessor.from_pretrained(model_id)
    pipe = pipeline(
        'automatic-speech-recognition',
        model=model,
        tokenizer=processor.tokenizer,
        feature_extractor=processor.feature_extractor,
        max_new_tokens=256,
        chunk_length_s=30,
        batch_size=16,
        return_timestamps=True,
        torch_dtype=torch_dtype,
        device=device
    )
    
    result = pipe(f'DB/{category}_{channel_num}/streaming_{category}_{channel_num}.mp3')
    
    with open(f'DB/{category}_{channel_num}/streaming_{category}_{channel_num}.txt', 'w', encoding='utf-8') as f:
        f.write(result['text'])