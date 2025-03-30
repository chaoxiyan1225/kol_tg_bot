user_ids = [2244994945, 6253282]

# kol  bio 关键词: 如果用户已经是按照上述的user_ids指定，该位置可以不设置
bio_keys = ["crypto", "cryptocurrency", "blockchain", "web3", "NFT", "DeFi", "bitcoin", "BTC", "ethereum", "ETH","token", "trader", "investor", "币圈", "加密货币" ]

#crypto  web3 关键词
Crypto_keys = ["crypto", "cryptocurrency", "bitcoin", "BTC", "ethereum", "ETH", "blockchain", "token", "NFT", "DeFi", "decentralized", "coin"]
Web3_keys = ["web3","dapp", "dao", "metaverse", "smart", "contract", "wallet"]
crypto_web3_keys = Crypto_keys + Web3_keys

# 美股 宏观环境关键词
stock_keys= ["stock", "NASDAQ", "NYSE", "SP500", "Dow Jones", "bull market", "bear market", "IPO", "earnings", "fed", "interest rate", "inflation", "recession, macro"]
macroen_keys = ["economy", "GDP", "unemployment", "trade", "policy", "fiscal", "monetary"]
stock_macroen_keys = stock_keys + macroen_keys

BOT=None
def set_bot(bot):
    print(f"init bot to global: {bot}")
    global BOT
    BOT = bot

def get_bot():
    global BOT
    return BOT

# 核心条件：Crypto 相关 KOL 发的 Tweet 或 Quote 评论
# 目标用户：识别与“Crypto”领域相关的 KOL（关键意见领袖）。判断依据：
# 用户简介（bio）中包含关键词：crypto, cryptocurrency, blockchain, web3, NFT, DeFi, bitcoin, BTC, ethereum, ETH, token, trader, investor, 币圈, 加密货币 等。
# 用户历史发帖主题与 Crypto 相关（可选：分析近期帖子是否频繁提及 Crypto 相关内容）。
# 内容类型：
# 原创 Tweet（tweets）。
# Quote Tweet（引用他人帖子并评论）。
# 实现建议：在后端维护一个 Crypto KOL 列表（可通过关键词匹配、粉丝数、发帖活跃度筛选），然后匹配发帖用户。

# def extract_ethereum_addresses(text: str) -> List[str]:
#     """从文本中提取所有有效的以太坊地址"""
#     candidates = re.findall(r"\b0x[a-fA-F0-9]{40}\b", text)
#     return [addr for addr in candidates if is_valid_ethereum_address(addr)]
#     return [addr for addr in candidates if is_valid_ethereum_address(addr)]

# def is_valid_solana_address(address: str) -> bool:
#     """
#     验证单个 Solana 地址的有效性（格式+Base58解码验证）
#     要求：
#     1. 长度严格为44字符
#     2. 仅包含Base58字符（排除0/O/I/l等易混淆字符）
#     3. Base58解码后为32字节
#     """
#     # 基础格式验证
#     if not re.fullmatch(r"[1-9A-HJ-NP-Za-km-z]{44}", address):
#         return False

#     # Base58解码验证
#     try:
#         decoded_bytes = base58.b58decode(address)
#         return len(decoded_bytes) == 32  # ed25519公钥长度为32字节
#     except (ValueError, TypeError):
#         return False
