from  twitter.tweet_conf import *
import re
from typing import List
from datetime import datetime, timezone, timedelta

import uuid
import sys, os
import uuid
# from Crypto.Cipher import AES
import logging
import subprocess

import re
import threading
from threading import Timer
import time
LOG_FILE_CLEAN_SECONDS = 60 * 60 * 24 * 7

__strCurrentDir__ = os.path.abspath(os.path.dirname(__file__))
__strModuleDir__ = os.path.dirname(__strCurrentDir__)

ACTIVE_USERS = set()

set_lock = threading.Lock()

timeBefore = 300  # 分钟
def InitLogger(logFile, logLevel):
    logger = logging.getLogger()
    fileHandler = logging.FileHandler(logFile)
    formatter = logging.Formatter("%(asctime)s %(filename)s %(funcName)s %(lineno)s \
      %(levelname)s - %(message)s", "%Y-%m-%d %H:%M:%S")

    fileHandler.setFormatter(formatter)
    logger.addHandler(fileHandler)
    logger.setLevel(logLevel)
    return logger

logger = InitLogger(
    f"./tweet-%s_%s_%s.log"
    % (
        datetime.now().year,
        datetime.now().month,
        datetime.now().day,
    ),
    logging.INFO,
)


class Cmd:
    def __init__(self, cmd, isPrint=False):
        self.cmd = cmd
        self.isPrint = isPrint

    def execute_cmd(self):
        # if self.isPrint:
        #     ColorPrint("CMD: %s" % self.cmd)
        code, output = subprocess.getstatusoutput(self.cmd)
        if code != 0:
            logger.error("Excute:%s code= %s  \n output= %s" % (self.cmd, code, output))
            return False, output
        else:
            logger.info("Excute:%s success \n output= %s" % (self.cmd, output))
            return True, output

class RepeatingTimer(Timer):
    def run(self):
        while not self.finished.is_set():
            self.function(*self.args, **self.kwargs)
            self.finished.wait(self.interval)

def gen_uuid():
    s_uuid=str(uuid.uuid4())
    l_uuid=s_uuid.split('-')
    s_uuid=''.join(l_uuid)

    return s_uuid

# import base58  # 需要安装：pip install base58
#from web3 import Web3
def is_crypto_kol(tweetUser, tClient):
    for key in bio_keys:
        if key.lower() in tweetUser.description.lower():
            return True

    response = tClient.get_users_tweets(tweetUser.id, max_results=10)

# By default, only the ID and text fields of each Tweet will be returned
    for tweet in response.data:
        if "crypto" in tweet.text.lower():
            return True

    return False

def contain_keywords(text, keywords):
    for key in keywords:
        if key.lower() in text.lower():
            return True

    return False

# def is_valid_ethereum_address(address: str) -> bool:
#     """验证单个以太坊地址的有效性（包含 EIP-55 校验和）"""
#     if not Web3.is_address(address):
#         return False
#     return address == Web3.to_checksum_address(address)

def contains_ethereum_address(text: str) -> bool:
    """判断文本中是否包含至少一个有效的以太坊地址"""
    # 匹配所有符合基础格式的候选地址（0x + 40 位十六进制）
    candidates = re.findall(r"\b0x[a-fA-F0-9]{40}\b", text)
    return candidates != None and len(candidates) > 0
    #return any(is_valid_ethereum_address(addr) for addr in candidates)
def contain_solana_addresses(text: str) -> list:
    """
    从文本中提取所有有效的 Solana 地址
    优化点：
    - 使用单词边界 \b 避免子串误匹配
    - 排除连续重复字符的常见误判（如全A/全B等）
    """
    # 匹配候选地址的正则表达式（排除纯数字/纯字母等情况）
    pattern = r"\b(?![1-9A-Za-z]{0,20}(?:AAAAA|BBBBB|CCCCC))([1-9A-HJ-NP-Za-km-z]{32,44})\b"
    candidates = re.findall(pattern, text)

    return candidates != None and len(candidates) > 0
    #return [addr for addr in candidates if is_valid_solana_address(addr)]

def contains_ca(text):
    if contains_ethereum_address(text):
        return True

    if contain_solana_addresses(text):
        return  True

    return False

def clean_logfiles():
   for root, dir, files in os.walk("./"):
      for file in files:
         if ".log" not in file:
            continue

         full_path = os.path.join(root, file)
         mtime = os.stat(full_path).st_mtime
         nowS = time.time()
         if nowS - mtime > LOG_FILE_CLEAN_SECONDS:
            os.remove(full_path)
   return
def get_isoTime():
    now = datetime.now(timezone.utc)
    # 减去30分钟
    thirty_minutes_ago = str(now - timedelta(minutes=timeBefore))
    dt = datetime.fromisoformat(thirty_minutes_ago.replace("Z", "+00:00"))
    # 截断微秒到3位并标准化时区
    return dt.replace(microsecond=dt.microsecond // 1000 * 1000).astimezone(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")

def add_tg_user(chatId):
    if not chatId:
        return 
    
    with set_lock:
       logger.warning(f"add user: {chatId} to set")
       ACTIVE_USERS.add(chatId)

# # --------------- 测试用例 ---------------
# if __name__ == "__main__":
#     test_text = """
#     我的地址是 0x52908400098527886E0F703057D2E41EE7，
#     无效地址示例：0xinvalid1234567890abcdef1234567890abcdef12345，
#     另一个有效地址 0xde709f210230622092106031471562902fb77，
#     以及错误长度的 0xabc。
#     """

#     # 检查是否存在有效地址
#     print("文本包含有效地址:", contains_ethereum_address(test_text))  # 输出 True

#     # 提取所有有效地址
#     # valid_addresses = extract_ethereum_addresses(test_text)
#     # print("有效地址列表:", valid_addresses)
#     # # 输出: ['0x52908400098527886E0F7030069857D2E4169EE7', '0xde709f2102306220921060314715629080e2fb77']

#     test_text = """
#     有效地址：
#     - H4RFkXiXZvjA2k4k1ZJq8Jvq8JvQmJvQmJvQmJvQmJvQmJvQmJvQmJvQmJvQm (虚构示例)
#     - 4wB4p9jqbd3gZgVvF6WQ7Kd7vq7Kd7vq7Kd7vq7Kd7vq7Kd7vq7Kd7vq7Kd

#     无效地址示例：
#     - 0xabc... (以太坊格式)
#     - AAAAABBBBBCCCCCAAAAABBBBBCCCCCAAAAABBBBB (连续重复)
#     - 1111111111111111111111111111111111111111 (全数字)
#     - ThisIsJustARandomTextWith44CharactersLongButInvalid!!
#     """

#     test_text = """
#     真实地址示例：
#     - 83astBRguLMdt2h5U1Tpdq5tjFoJ6noeGwaY3mDLVcri (随机生成测试地址)
#     - 83astBRguLMdt2h5U1Tpdq5tjFoJ6noeGwaY3mDLVcriewwwewe (虚构)
#     - H4RFkXiXZvjA2k4k1ZJq8Jvq8JvQmJvQmJvQmJvmww (虚构示例)
#     - 4wB4p9jqbd3gZgVvF6WQ7Kd7vq7Kd7vq7Kd7vq7Kd7vq7Kd7vq7Kd7vq7Kd
#     """

#     addresses = contain_solana_addresses(test_text)
#     print("检测到的有效地址:", addresses)
#     # 输出: [] （因示例地址为虚构，实际应替换为真实地址测试）

#     print(get_isoTime())
