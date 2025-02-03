import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import koreanize_matplotlib
from collections import deque

def run_cusum(category, channel_num):
    """
    CSV 파일의 (likeDelta, chatDelta)로부터 'score'를 계산하고,
    CUSUM(Upper) + 동적 임계치(윈도우 내 평균+ k×표준편차)로 하이라이트 지점을 찾는 예시
    """
    csv_path = f'DB/{category}_{channel_num}/{category}_{channel_num}_increase_log.csv'
    df = pd.read_csv(csv_path)

    # 하이라이트 점수 계산
    w1, w2 = 0.4, 0.6
    df["score"] = w1 * df["라이크증가"] + w2 * df["채팅증가수"]

    # CUSUM(Upper) 계산
    # S_t = max(0, S_{t-1} + (x_t - target_mean))
    # 여기서는 전체 score 평균을 target_mean으로 사용
    target_mean = df["score"].mean()
    cusum_vals = []
    S = 0.0

    # 동적 임계치 계산용 슬라이딩 윈도우 설정
    window_size = 20     # 최근 20개 CUSUM 값으로 동적 threshold 계산
    k = 2.0              # threshold = mean + k * std
    window = deque(maxlen=window_size)

    # 하이라이트 저장용
    thresholds = []
    highlight_flags = []

    for val in df["score"]:
        # (1) CUSUM 업데이트
        deviation = val - target_mean
        S = max(0, S + deviation)
        cusum_vals.append(S)

        # (2) 동적 threshold 계산
        #     현재 CUSUM 값을 window에 넣고, window의 평균 + k*표준편차
        window.append(S)
        mean_val = np.mean(window)
        std_val  = np.std(window)
        dynamic_threshold = mean_val + k * std_val
        thresholds.append(dynamic_threshold)

        # (3) 하이라이트 여부
        highlight_flag = (S > dynamic_threshold)
        highlight_flags.append(highlight_flag)

    df["cusum"] = cusum_vals
    df["dynamic_threshold"] = thresholds
    df["is_highlight"] = highlight_flags

    # 5) 그래프 그리기
    x = df['시간']  # 행 인덱스 사용 (또는 time_seconds 등)
    plt.figure(figsize=(10,5))

    # CUSUM
    plt.plot(x, df["cusum"], 'b-', label='관심도')

    # 하이라이트 지점
    highlight_indices = df.index[df['is_highlight']]
    highlight_vals = df.loc[df['is_highlight'], 'cusum']
    plt.scatter(highlight_indices, highlight_vals,
                color='red', marker='o', zorder=5, label='하이라이트')

    plt.xticks(ticks=df.index[::10], labels=df['시간'][::10], rotation=45, fontsize=8)
    plt.xlabel('영상 구간')
    plt.ylabel('관심도')
    plt.legend(loc='upper left')
    plt.tight_layout()
    
    output_dir = f'DB/{category}_{channel_num}/{category}_{channel_num}_graph.png'
    plt.savefig(output_dir, dpi=300, bbox_inches='tight')