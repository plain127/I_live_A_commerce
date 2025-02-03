from transformers import AutoTokenizer, BertForTokenClassification, logging
logging.set_verbosity_error()
import sys, os, torch
import numpy as np
sys.path.insert(0, '../')
import live_ner_label
import kss

os.environ["CUDA_DEVICE_ORDER"]="PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"]="0"

# tokenizer 및 model 불러오기
tokenizer = AutoTokenizer.from_pretrained("KPF/KPF-bert-ner")
# huggingface 개체명 인식 모델 불러오기
model = BertForTokenClassification.from_pretrained("KPF/KPF-bert-ner")

def ner_predict(text):
    text = text.replace('\n','')
    model.to("cuda")

    sents = kss.split_sentences(text)
    decoding_ner_sentence = ""
    word_list = list()
    pred_str = list()

    #text to model input
    for idx, sent in enumerate(sents):

        sent = sent.replace(" ", "-")
        test_tokenized = tokenizer(sent, return_tensors="pt")

        test_input_ids = test_tokenized["input_ids"].to("cuda")
        test_attention_mask = test_tokenized["attention_mask"].to("cuda")
        test_token_type_ids = test_tokenized["token_type_ids"].to("cuda")

        inputs = {
            "input_ids" : test_input_ids,
            "attention_mask" : test_attention_mask,
            "token_type_ids" : test_token_type_ids
        }

        if inputs['input_ids'].size()[1] > 512:
            cnt = int(inputs['input_ids'].size()[1])

            inp_np = inputs['input_ids'].cpu().numpy()
            att_np = inputs['attention_mask'].cpu().numpy()
            tok_np = inputs['token_type_ids'].cpu().numpy()

            for i in range(cnt):
                slice_inp = inp_np[0][(i*512):((i+1)*512)]
                slice_att = att_np[0][(i * 512):((i + 1) * 512)]
                slice_tok = tok_np[0][(i * 512):((i + 1) * 512)]

                slice_inp = slice_inp.reshape(1, len(slice_inp))
                slice_att = slice_att.reshape(1, len(slice_att))
                slice_tok = slice_tok.reshape(1, len(slice_tok))

                slice_inp = torch.tensor(slice_inp)
                slice_att = torch.tensor(slice_att)
                slice_tok = torch.tensor(slice_tok)

                slice_inp = torch.tensor(slice_inp).to("cuda")
                slice_att = torch.tensor(slice_att).to("cuda")
                slice_tok = torch.tensor(slice_tok).to("cuda")

                slice_inputs = {
                    "input_ids": slice_inp,
                    "attention_mask": slice_att,
                    "token_type_ids": slice_tok
                }

                # predict
                outputs = model(**slice_inputs)

                token_predictions = outputs[0].argmax(dim=2)
                token_prediction_list = token_predictions.squeeze(0).tolist()

                pred = [live_ner_label.id2label[l] for l in token_prediction_list]

                pred_str = np.concatenate((pred_str, pred))
        else:
            #predict
            outputs = model(**inputs)

            token_predictions = outputs[0].argmax(dim=2)
            token_prediction_list = token_predictions.squeeze(0).tolist()

            pred_str = [live_ner_label.id2label[l] for l in token_prediction_list]
        tt_tokenized = tokenizer(sent).encodings[0].tokens

        # decoding_ner_sentence = ""
        is_prev_entity = False
        prev_entity_tag = ""
        is_there_B_before_I = False
        _word = ""
        # word_list = list()
    
        #model output to text
        for i, (token, pred) in enumerate(zip(tt_tokenized, pred_str)):
            if i == 0 or i == len(pred_str) - 1:
                continue
            token = token.replace('#', '').replace("-", " ")

            if token == "":
                continue

            if 'B-' in pred:
                if is_prev_entity is True:
                    decoding_ner_sentence += ':' + prev_entity_tag+ '>'
                    word_list.append({"word" : _word, "label" : prev_entity_tag, "desc" : "1"})
                    _word = ""

                if token[0] == ' ':
                    token = list(token)
                    token[0] = ' <'
                    token = ''.join(token)
                    decoding_ner_sentence += token
                    _word += token
                else:
                    decoding_ner_sentence += '<' + token
                    _word += token
                is_prev_entity = True
                prev_entity_tag = pred[2:]
                is_there_B_before_I = True

            elif 'I-' in pred:
                decoding_ner_sentence += token
                _word += token

                if is_there_B_before_I is True:
                    is_prev_entity = True
            else:
                if is_prev_entity is True:
                    decoding_ner_sentence += ':' + prev_entity_tag+ '>' + token
                    is_prev_entity = False
                    is_there_B_before_I = False
                    word_list.append({"word" : _word, "label" : prev_entity_tag, "desc" : live_ner_label.ner_code[prev_entity_tag]})
                    _word = ""
                else:
                    decoding_ner_sentence += token

    # print("OUTPUT")
    # print("sentence : ", decoding_ner_sentence)
    # print("result : ", word_list)
    live_word = ' '.join(w['word'] for w in word_list)
    return live_word