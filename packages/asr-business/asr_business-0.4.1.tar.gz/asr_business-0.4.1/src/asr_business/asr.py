import os
import sys
import warnings

warnings.filterwarnings("ignore")

from funasr import AutoModel

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)
import chinese2digits as c2d
from decimal import DivisionByZero

digit_num = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']


class Asr:
    def __init__(self,
                 asr_model_path,
                 punc_model_path,
                 batch_size=16,
                 device="cuda:0"):
        """
        asr_model_path: asr模型 路径
        punc_model_path: 标点预测模型 路径
        batch_size: 单次batch识别的数量，默认为16
        device: 模型推理的设备，默认为cuda:0
        """
        self.batch_size = batch_size
        self.asr_model = AutoModel(
            model=asr_model_path,
            device=device,
            disable_update=True
        )
        self.punc_model = AutoModel(
            model=punc_model_path,
            device=device,
            disable_update=True,
            bf16=True
        )

    @staticmethod
    def convert_chinese_to_digits(item):
        """
        将文本中的 中文数字 转化为 阿拉伯数字
        :param item:
        :return:
        """
        text = item['text']
        key = item['key']
        try:
            converted_text = c2d.takeNumberFromString(text)['replacedText']
            converted_text = list(converted_text)
            for i in range(len(converted_text)):
                if converted_text[i] == "1" and converted_text[i + 1] not in digit_num:
                    converted_text[i] = "一"
            converted_text = "".join(converted_text)
            return {'key': key, 'text': converted_text}
        except DivisionByZero:
            return {'key': key, 'text': text}
        except Exception as e:
            return {'key': key, 'text': text}

    def add_punctuation(self, item):
        """
        为 文本添加标点
        :param item:
        :return:
        """
        text = item['text']
        key = item['key']
        if text:
            punc_text = self.punc_model.generate(input=text, disable_pbar=True)[0]['text']
        else:
            punc_text = ""
        return {"key": key, "text": punc_text}

    def generate(self, input_files=None):
        """
        model生成函数
        :param input_files:
        :return:
        """
        res = self.asr_model.generate(
            input=input_files,
            language="zh",
            use_itn=True,
            batch_size=len(input_files) if self.batch_size > len(input_files) else self.batch_size,
            disable_pbar=True
        )
        res = [self.add_punctuation(item) for item in res]
        res = [self.convert_chinese_to_digits(item) for item in res]
        return res

    def transcribe(self, audios):
        """
        将音频识别为文本
        :param audios: 音频文件，格式为列表
        :return:
        """
        res_ls = []
        # 判断音频文件格式是否为.mp3，如果不是.mp3格式则删除文件
        valid_audios = [audio for audio in audios if audio.endswith('.mp3')]
        if not audios:
            raise ValueError("asr in progress, audios list can't be empty")
        # 当batch size大于音频列表的长度时，将整个音频列表喂入模型
        if self.batch_size >= len(valid_audios):
            res = self.generate(valid_audios)
            res_ls.append(res)
        # 当batch size小于音频列表长度时，以batch size为step，将音频列表进行切割，分批次喂入模型
        else:
            batch = [valid_audios[i:i + self.batch_size] for i in range(0, len(valid_audios), self.batch_size)]
            for input_files in batch:
                res = self.generate(input_files)
                res_ls.append(res)
        return res_ls


if __name__ == "__main__":
    import argparse
    import time

    parser = argparse.ArgumentParser()
    parser.add_argument('--asr_model_path', type=str, default="../llm_weight/paraformer-large-hotword")
    parser.add_argument('--punc_model_path', type=str, default="../llm_weight/ct-punc")
    parser.add_argument('--batch_size', type=int, default=32)
    parser.add_argument('--data_path', type=str, default="../dataset/test_data/1v1")
    args = parser.parse_args()
    audios = sorted(os.listdir(args.data_path))
    audios = list(map(lambda x: args.data_path + '/' + x, audios))
    asr = Asr(asr_model_path=args.asr_model_path,
              punc_model_path=args.punc_model_path,
              batch_size=args.batch_size)
    start_time = time.time()
    result = asr.transcribe(audios)
    end_time = time.time()
    print("result is: {}".format(result[:2]))
    print("推理速度为 {} ms/条".format((end_time - start_time) * 1000 / len(audios)))
