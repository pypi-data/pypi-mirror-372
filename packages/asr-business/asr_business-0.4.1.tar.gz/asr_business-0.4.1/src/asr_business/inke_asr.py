import os
import sys
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

from asr import Asr

from utils import process_data_no_vp, get_audio_path, process_data_vp, setup_logger
from vad import Vad
from voiceprint import Voiceprint


class Inke_asr:
    def __init__(self,
                 asr_model_path="",
                 punc_model_path="",
                 vad_model_path="",
                 voiceprint_model_path="",
                 batch_size=16,
                 num_process=1,
                 log_dir="",
                 use_cpu=False,
                 device="cuda:0"):
        """
        :param asr_model_path: asr模型路径
        :param punc_model_path: 标点生成模型路径
        :param vad_model_path: 静音检测模型路径
        :param voiceprint_model_path: 声纹模型路径
        :param batch_size: 批处理大小
        :param num_process: 进程数
        :param log_dir: 日志文件路径，用于落vad的日志
        :param use_cpu: 是否使用cpu，默认为False，即使用gpu；如果传入True，则在cpu启动多进程处理vad
        :param device: 设备id
        """
        self.logger = setup_logger(log_dir)
        self.asr = Asr(asr_model_path=asr_model_path, punc_model_path=punc_model_path, batch_size=batch_size,
                       device=device)
        # self.vad = Vad(vad_model_path=vad_model_path, num_process=num_process, batch_size=batch_size, use_cpu=use_cpu,
        #                device_id=device.split(":")[1] if len(device.split(":")) > 1 else 0)
        self.vp = Voiceprint(voiceprint_model_path=voiceprint_model_path, batch_size=batch_size)

    def vp_inference(self, audios, data, is_voiceprint):
        """
        将asr及vad结果过vp模型，并处理成统一格式[[{"key":"","text":"","label":""},{},..],[]]
        :param audios: 音频文件的绝对路径列表
        :param data: vad或asr识别结果
        :param is_voiceprint: 是否需要进行声纹识别，默认为1
        :return
        """
        if is_voiceprint:
            audio_files = get_audio_path(data, audios)
            vp_result = self.vp.inference(audio_files)
            return process_data_vp(vp_result, data)
        else:
            return process_data_no_vp(data)

    def transcribe(self, audios, is_voiceprint=1):
        """
        对音频文件进行asr识别
        :param audios: 音频文件的绝对路径列表
        :param is_voiceprint: 是否需要进行声纹识别,默认为1
        :return:
        """
        # 进行静音检测
        # valid_audios, vad_result = self.vad.silence_detection(audios)
        # 添加vad静音检测日志
        # if vad_result:
        #     self.logger.info("vad result is: {}".format(vad_result))
        # 进行asr识别，有效音频列表不为空，进行asr翻译
        if audios:
            asr_result = self.asr.transcribe(audios)
            # asr_result.extend(vad_result)
            return self.vp_inference(audios, asr_result, is_voiceprint)
        # else:
        #     return self.vp_inference(audios, vad_result, is_voiceprint)


if __name__ == "__main__":
    import argparse
    import os

    parser = argparse.ArgumentParser()
    parser.add_argument('--asr_model_path', type=str, default="../llm_weight/paraformer-large-hotword")
    parser.add_argument('--punc_model_path', type=str, default="../llm_weight/ct-punc")
    parser.add_argument('--vad_model_path', type=str, default="../llm_weight/fsmn-vad")
    parser.add_argument('--voiceprint_model_path', type=str, default="../llm_weight/PANNs/panns_cnn14_16k.pth")
    parser.add_argument("--batch_size", type=int, default=32)
    parser.add_argument('--num_process', type=int, default=1)
    parser.add_argument("--log_dir", type=str, default="./")
    parser.add_argument("--is_voiceprint", type=int, default=1)
    parser.add_argument('--data_path', type=str, default="../dataset/test_data/vp")
    args = parser.parse_args()
    audios = sorted(os.listdir(args.data_path))
    audios = list(map(lambda x: args.data_path + '/' + x, audios))
    asr = Inke_asr(asr_model_path=args.asr_model_path, punc_model_path=args.punc_model_path,
                   vad_model_path=args.vad_model_path, voiceprint_model_path=args.voiceprint_model_path,
                   batch_size=args.batch_size, num_process=args.num_process, log_dir=args.log_dir)
    start_time = time.time()
    result = asr.transcribe(audios, args.is_voiceprint)
    end_time = time.time()
    print(result)
    print("推理速度为: {}ms/条".format((end_time - start_time) * 1000 / len(audios)))


