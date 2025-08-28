import os
import sys

import librosa
import numpy as np
import torch

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)
from models import Transfer_Cnn14_16k

classes_num = 2
labels = ["normal", "panting"]


class Voiceprint:
    def __init__(self, voiceprint_model_path, sample_rate=16000, window_size=512, hop_size=160, mel_bins=64, fmin=50,
                 fmax=8000, freeze_base=False, device="cuda:0", batch_size=16, threshold_prob=0.7):
        """
        :param voiceprint_model_path: 声纹模型 路径
        :param sample_rate: 采样率，16kHz
        :param window_size: 窗口size，512
        :param hop_size: hop大小，相邻帧间的样本数，160
        :param mel_bins: mel箱，64
        :param fmin: 50
        :param fmax: 8000
        :param freeze_base: 是否冻结base网络层，否
        :param device: 模型推理设备，默认为cuda:0
        :param batch_size: 单次batch识别的数量，默认为16
        """
        self.sample_rate = sample_rate
        self.batch_size = batch_size
        self.device = device
        self.threshold = threshold_prob
        self.checkpoint = torch.load(voiceprint_model_path)
        self.model = Transfer_Cnn14_16k(sample_rate=sample_rate, window_size=window_size, hop_size=hop_size,
                                        mel_bins=mel_bins, fmin=fmin, fmax=fmax, classes_num=2, freeze_base=freeze_base)
        self.model.load_state_dict(self.checkpoint['model'])
        # 并行
        if 'cuda' in str(device):
            self.model.to(device)
            self.model = torch.nn.DataParallel(self.model)

    @staticmethod
    def move_data_to_device(x, device):
        if 'float' in str(x.dtype):
            x = torch.Tensor(x)
        elif 'int' in str(x.dtype):
            x = torch.LongTensor(x)
        else:
            return x
        return x.to(device)

    def inference(self, audios, threshold=None):
        res_ls = []
        if not audios:
            raise ValueError("voiceprint in progress, audios list can't be empty")
        batch = [audios[i:i + self.batch_size] for i in range(0, len(audios), self.batch_size)]
        for input_files in batch:
            # 一次性加载所有音频文件
            waveforms = []
            for file in input_files:
                waveform, _ = librosa.core.load(file, sr=self.sample_rate, mono=True)
                waveforms.append(waveform)

            # 找出最大长度并进行padding
            max_length = max(len(w) for w in waveforms)
            waveforms = [np.pad(w, (0, max_length - len(w)), 'constant') if len(w) < max_length else w
                         for w in waveforms]
            waveforms = np.array(waveforms)
            waveforms = self.move_data_to_device(waveforms, self.device)
            # 前向传播
            tmp_ls = []
            with torch.no_grad():
                self.model.eval()
                batch_output_dict = self.model(waveforms)
            clipwise_output = batch_output_dict['clipwise_output'].data.cpu().numpy()
            for file, output in zip(input_files, clipwise_output):
                if threshold:
                    pred_label = "panting" if output[1] >= threshold else "normal"
                else:
                    pred_label = "panting" if output[1] >= self.threshold else "normal"
                tmp_ls.append({"key": os.path.basename(file).split(".")[0], "label": pred_label, "prob": float(output[1])})
            if tmp_ls:
                res_ls.append(tmp_ls)
        return res_ls


if __name__ == "__main__":
    import time
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--voiceprint_model_path', type=str, default="../llm_weight/PANNs/panns_cnn14_16k.pth")
    parser.add_argument("--batch_size", type=int, default=32)
    parser.add_argument("--data_path", type=str, default="../dataset/test_data/panting")
    parser.add_argument("--threshold_prob", type=float, default=0.78)
    args = parser.parse_args()
    audios = sorted(os.listdir(args.data_path))
    audios = list(map(lambda x: args.data_path + '/' + x, audios))
    vp = Voiceprint(voiceprint_model_path=args.voiceprint_model_path,
                    batch_size=args.batch_size)
    start_time = time.time()
    result = vp.inference(audios, args.threshold_prob)
    end_time = time.time()
    print("result is: {}".format(result[:10]))
    print("推理速度为: {}ms/条".format((end_time - start_time) * 1000 / len(audios)))