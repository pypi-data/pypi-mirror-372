import logging
import os
from logging.handlers import TimedRotatingFileHandler

logger = logging.getLogger("server.vop.info.log")


def setup_logger(log_dir):
    """
    配置日志
    :param log_dir: 日志文件目录
    :return: logger实例
    """
    os.makedirs(log_dir, exist_ok=True)

    logger.propagate = False
    logger.setLevel(logging.INFO)

    # 避免重复添加handler
    if not logger.handlers:
        log_file = os.path.join(log_dir, "vop.info.log")
        # when='H' 表示每小时轮转
        # interval=1 表示间隔为1小时
        # encoding='utf-8' 设置编码
        handler = TimedRotatingFileHandler(
            log_file,
            when='H',  # 按小时切分
            interval=1,  # 每1小时切分一次
            backupCount=168,  # 保留最近168个文件（7天）
            encoding='utf-8'
        )

        # 设置后缀格式为 .YYYY-MM-DD_HH
        handler.suffix = "%Y-%m-%d_%H"

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger


def process_data_no_vp(data):
    """
    用于处理不需要过声纹模型的数据,增加label标签为normal,产出最终数据，格式为：[[{"key":"","text":"","label":""},{},..],[]]
    :param data: vad及asr识别结果,格式为：[[{"key":"","text":""},{},..],[]]
    :return:
    """
    res_ls = []
    for batch in data:
        tmp_res = []
        for item in batch:
            tmp_res.append({"key": item["key"], "text": item["text"], "label": "normal"})
        if tmp_res:
            res_ls.append(tmp_res)
    return res_ls


def process_data_vp(vp_data, data):
    """
    将vp数据和asr数据融合，产出最终数据，格式为：[[{"key":"","text":"","label":""},{},..],[]]
    :param vp_data: 声纹模型识别结果，格式为：[[{"key":"","label":""},{},..],[]]
    :param data: vad及asr识别结果,格式为：[[{"key":"","text":""},{},..],[]]
    :return:
    """
    result = []

    # 将vp_data展平成一维并创建key到label的映射
    vp_dict = {}
    for group in vp_data:
        for item in group:
            vp_dict[item['key']] = item['label']

    # 处理data中的每一组
    for data_group in data:
        merged_group = []
        for item in data_group:
            merged_item = {
                'key': item['key'],
                'text': item['text'],
                'label': vp_dict.get(item['key'], 'normal')  # 默认值为'normal'
            }
            merged_group.append(merged_item)
        result.append(merged_group)

    # 验证所有key都被使用（可选）
    data_keys = {item['key'] for group in data for item in group}
    vp_keys = set(vp_dict.keys())
    if data_keys != vp_keys:
        print(f"Warning: Keys mismatch. Missing keys: {vp_keys - data_keys}, Extra keys: {data_keys - vp_keys}")

    return result


def get_audio_path(data, audios):
    """
    根据asr返回的数据格式获取对应的文件绝对路径列表
    :param data: vad及asr识别结果,格式为：[[{"key":"","text":""},{},..],[]]
    :param audios: 音频文件的绝对路径，格式为：["path",""]
    :return:
    """
    # 创建文件名到完整路径的映射字典
    path_dict = {path.split('/')[-1].rsplit('.', 1)[0]: path for path in audios}
    # 存储结果的列表
    result = []
    # 遍历二维列表
    for group in data:
        # 遍历每组中的字典
        for item in group:
            # 根据file字段查找对应的完整路径
            file_path = path_dict.get(item['key'])
            if file_path:
                result.append(file_path)
    return result


if __name__ == "__main__":
    pass
