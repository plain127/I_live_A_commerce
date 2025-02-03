import argparse
import os
import glob
import torch
import numpy as np
import pandas as pd
from tqdm import tqdm, trange
from torch.utils.data import Dataset, DataLoader
import lightning as L
from functools import partial

class KoBARTSummaryDataset(Dataset):
    def __init__(self, file, tokenizer, max_len, ignore_index=-100):
        super().__init__()
        self.tokenizer = tokenizer
        self.max_len = max_len
        self.docs = pd.read_csv(file, sep='\t')

        # 열 이름 로깅
        print(f"Loaded dataset with columns: {self.docs.columns.tolist()}")

        # 데이터 확인 및 예외 처리
        if 'passage' not in self.docs.columns or 'summary' not in self.docs.columns:
            raise ValueError("Dataset must contain 'passage' and 'summary' columns.")

        self.len = self.docs.shape[0]
        self.pad_index = self.tokenizer.pad_token_id
        self.ignore_index = ignore_index

    def add_padding_data(self, inputs):
        """입력 데이터를 max_len에 맞게 패딩."""
        if len(inputs) < self.max_len:
            pad = np.array([self.pad_index] * (self.max_len - len(inputs)))
            inputs = np.concatenate([inputs, pad])
        else:
            inputs = inputs[:self.max_len]

        return inputs

    def add_ignored_data(self, inputs):
        """라벨 데이터를 max_len에 맞게 패딩."""
        if len(inputs) < self.max_len:
            pad = np.array([self.ignore_index] * (self.max_len - len(inputs)))
            inputs = np.concatenate([inputs, pad])
        else:
            inputs = inputs[:self.max_len]

        return inputs

    def __getitem__(self, idx):
        """데이터셋의 idx 위치 데이터를 반환."""
        instance = self.docs.iloc[idx]

        # 본문과 요약 텍스트
        input_ids = self.tokenizer.encode(instance['passage'])  # 열 이름 수정
        input_ids = self.add_padding_data(input_ids)

        label_ids = self.tokenizer.encode(instance['summary'])
        label_ids.append(self.tokenizer.eos_token_id)
        dec_input_ids = [self.tokenizer.eos_token_id]
        dec_input_ids += label_ids[:-1]
        dec_input_ids = self.add_padding_data(dec_input_ids)
        label_ids = self.add_ignored_data(label_ids)

        return {
            'input_ids': np.array(input_ids, dtype=np.int_),
            'decoder_input_ids': np.array(dec_input_ids, dtype=np.int_),
            'labels': np.array(label_ids, dtype=np.int_)
        }

    def __len__(self):
        return self.len

class KobartSummaryModule(L.LightningDataModule):
    def __init__(self, train_file, test_file, tok, max_len=512, batch_size=8, num_workers=4):
        super().__init__()
        self.batch_size = batch_size
        self.max_len = max_len
        self.train_file_path = train_file
        self.test_file_path = test_file
        self.tok = tok
        self.num_workers = num_workers

    @staticmethod
    def add_model_specific_args(parent_parser):
        parser = argparse.ArgumentParser(
            parents=[parent_parser], add_help=False)
        parser.add_argument('--num_workers',
                            type=int,
                            default=4,
                            help='num of worker for dataloader')
        return parser

    def setup(self, stage):
        """데이터 로드 및 데이터셋 초기화."""
        self.train = KoBARTSummaryDataset(self.train_file_path, self.tok, self.max_len)
        self.test = KoBARTSummaryDataset(self.test_file_path, self.tok, self.max_len)

    def train_dataloader(self):
        """훈련 데이터 로더 반환."""
        return DataLoader(self.train, batch_size=self.batch_size, num_workers=self.num_workers, shuffle=True)

    def val_dataloader(self):
        """검증 데이터 로더 반환."""
        return DataLoader(self.test, batch_size=self.batch_size, num_workers=self.num_workers, shuffle=False)

    def test_dataloader(self):
        """테스트 데이터 로더 반환."""
        return DataLoader(self.test, batch_size=self.batch_size, num_workers=self.num_workers, shuffle=False)
