import tweepy
import time
from twitter.tweet_conf import *
from twitter.tweet_util import *
import time
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED, ALL_COMPLETED
import _thread
import multitasking, threading # 用于多线程操作
import os
import json
from aiogram.enums import ParseMode
import asyncio
multitasking.set_max_threads(1)

tweets_lock = threading.Lock()


REFRESH_PERIOD = 60 * 30  # 30分钟
CUR_DIR = os.getcwd()
CURRENT_TWEETS=CUR_DIR+"/twitter/current_tweets.json"
BEFORE_TWEETS=CUR_DIR+"/twitter/before_tweets.json"
TWEETS_KOL_NAMES=CUR_DIR+"/twitter/tweet_kols.json"

bearer_token = "AAAAAAAAAAAAAAAAAAAAAFBjzwEAAAAAJyI7zTy6vf9LglJLs7qt27JfaRw%3DEI1jfO0HpKzUMIUuAL7XzjB2M1yvTdGmoMxcVNMgxvSAYb13jO"
client = tweepy.Client(bearer_token, wait_on_rate_limit=True)
USERS = None

def filter_tweet(tweet, user):
    priority_score = 0
    # Crypto/Web3，加分
    if contain_keywords(tweet.text, crypto_web3_keys):
        priority_score += 1

    # 提及美股宏观环境，加分
    if contain_keywords(tweet.text, stock_macroen_keys):
        priority_score += 1

    # 条件 4：包含 CA，加分最高
    if contains_ca(tweet.text):
        priority_score += 3

    if  priority_score == 0:
        return None

    # 返回结果:优先级分数越高越靠前
    return {
        "tweet": {
                  "retweet_count":tweet.public_metrics['retweet_count'],
                  "text":tweet.text,
                  "id":str(tweet.id),
                  "like_count":tweet.public_metrics['like_count'],
                   "created_at":tweet.created_at, "url": "https://twitter.com/twitter/statuses/"+str(tweet.id),
                   "user_name":user.username,
                   "user_url":"https://x.com/"+user.username
                },
        "is_valid": True,
        "priority": priority_score
    }

def filter_all_users():
    retUsers = []
    try:
      response = client.get_users(ids=user_ids, user_fields=["description"])
      for user in response.data:
          if is_crypto_kol(user, client):
              retUsers.append(user)

    except Exception as e:
        logger.error(f"filter all user error happen : {str(e)}")

    return retUsers

def get_userIds():

    if  os.path.exists(TWEETS_KOL_NAMES):
        try:
            with open(TWEETS_KOL_NAMES, 'r', encoding='utf-8') as file:
                data = json.load(file)

        except json.JSONDecodeError:
            logger.error(f"{TWEETS_KOL_NAMES} not right JSON file")
            return None
        user_names = data['user_names']
        response = client.get_users(usernames=user_names, user_fields=["username", "url"])
        logger.warning(f"get users : {response}")
        return response.data

def collect_valid_tweets(allTweets, fromTime):
    @multitasking.task
    def get_user_tweets(user):
        userId = user.id
        retTweets = []
        try:
            response = client.get_users_tweets(userId, start_time = fromTime, tweet_fields=["public_metrics", "created_at"])
            if response == None or  response.data == None:
                logger.warning(f"【step】2: user {userId} tweets count is 0 , from time: {fromTime}")
                return
            logger.warning(f"【step】2: user {userId} tweets count : {len(response.data)} , from time: {fromTime}")
            for tweet in response.data:
                newTweet = filter_tweet(tweet, user)
                if newTweet:
                    retTweets.append(newTweet)
            logger.warning(f"【step】2: user {userId} tweets match count : {len(retTweets)} , from time: {fromTime}")
        except Exception as e:
            logger.error(f"[step]2 error happen : {str(e)}")
        with tweets_lock:
           allTweets.extend(retTweets)

        logger.warning(f"【step】2: Collect user {userId} end")

    # response = client.get_users_tweets(user_id, tweet_fields=["public_metrics", "created_at", "article"])

    logger.warning("【step】2: Collect tweets start")

    allUsers = get_userIds()
    if allUsers == None:
        logger.error(f"get all user error, exit")
        return

    for user in allUsers:
        get_user_tweets(user)
        time.sleep(2)

    multitasking.wait_for_tasks()
    logger.warning("【step】2: Collect tweets finish")

def sort_tweets(allTweets):
    sorted_tweets = sorted(allTweets, key=lambda x: x["priority"], reverse=True)
    return sorted_tweets
def rename_file(source: str, target: str) -> None:
    try:
        if os.path.exists(CURRENT_TWEETS):
           os.replace(source, target)
           logger.warning(f"file {source}  rename to: {target} success")
    except FileNotFoundError:
        logger.error(f"error: {source}  not exist")
    except PermissionError:
        logger.error(f"error: permission deny: {source} or {target}")

def get_tweets_list():
    if  os.path.exists(CURRENT_TWEETS):
        try:
            with open(CURRENT_TWEETS, 'r', encoding='utf-8') as file:
                data = json.load(file)

        except json.JSONDecodeError:
            logger.error(f"error:{CURRENT_TWEETS} not right JSON")
            return None

        if not isinstance(data, list):
            logger.error(f"error:{CURRENT_TWEETS} JSON  root list not list ")
            return None

        return data

    if  os.path.exists(BEFORE_TWEETS):
        try:
            with open(BEFORE_TWEETS, 'r', encoding='utf-8') as file:
                data = json.load(file)
        except json.JSONDecodeError:
            logger.error(f"error:{BEFORE_TWEETS} not right JSON ")
            return None

        if not isinstance(data, list):
            logger.error(f"error:{BEFORE_TWEETS} JSON not root list")
            return None

        return data

    return None

def _truncate_tweet_(text, max_length=3500, ellipsis="..."):
    if len(text) > max_length:
        return text[:max_length - len(ellipsis)] + ellipsis
    return text

def query_formart_tweet_md(chatId)->List:
    # add chatId
    add_tg_user(chatId)
    tws = get_tweets_list()
    if tws == None or len(tws) == 0:
        logger.warning(f"find no tweets from users, please check, and return")
        return []

    formatTws = []
    for tw in tws:
        twText =(tw['text'])
        mdStr = f'''
                🐦 New Tweet from <a href="{tw['user_url']}">@{tw['user_name']}]</a>
{twText}
                \n
❤ {tw['like_count']}赞| {tw['retweet_count']} 转推
🕜 {tw['created_at']}
📎 <a href="{tw['url']}">View on Twitter</a>
                '''
        formatTws.append(mdStr)

    return formatTws

def remove_duplicat(targetTweets):
    beforTweets =  get_tweets_list()
    resultTweets = []

    if beforTweets == None or len(beforTweets) == 0:
        logger.warning(f"beforTweets is empty, and return")

        for tw in targetTweets:
            resultTweets.append(tw['tweet'])

        return resultTweets

    for nt in targetTweets:
        is_need = True
        for ot in beforTweets:
            if nt['tweet']['id'].lower() == ot['id'].lower():
                logger.warning(f"find duplicate tweet, and remove it")
                is_need = False
                break

        if is_need:
            resultTweets.append(nt['tweet'])

    return resultTweets

async def push_tweets_to_users():
    bot = get_bot()
    if not bot:
        logger.error(f"push tweet to user, but bot is not init, exit")
        return

    logger.warning(f"start push tweet to user, user count: {len(ACTIVE_USERS)}")
    tweets = query_formart_tweet_md(None)

    if len(tweets) == 0:
        logger.warning(f"no tweet to push to user, exit")
        return

    for user_id in ACTIVE_USERS.copy():  # 使用副本避免迭代修改
        for tw in tweets:
            try:
                await bot.send_message(
                    chat_id=user_id,
                    text=tw,
                    parse_mode=ParseMode.HTML
                )
            except Exception as e:
                logging.error(f"push tweet error userID: {user_id}: {e}")

            #无论成功失败都得间隔5s再发送
            await asyncio.sleep(5)

    logger.warning(f"start push tweet to user, user count: {len(ACTIVE_USERS)} finish")
def generate_tweet_list():
    # matchUsers = filter_all_users()
    # if len(matchUsers) == 0:
    #     print("【step】1: No match users, exit")
    #     exit(1)

    fromTime = get_isoTime()
    allTweets = []
    collect_valid_tweets(allTweets, fromTime)
    if len(allTweets) == 0:
        logger.warning(f"find no tweets from users, please check, and return")
        return

    logger.warning(f"【step】3 after filter tweets count is :{len(allTweets)}  fromTime: {fromTime}")
    logger.warning(f"【step】4: sorted tweets start fromTime: {fromTime}")
    sortedTweets = sort_tweets(allTweets)
    resultList = remove_duplicat(sortedTweets)

    if len(resultList) == 0:
        logger.warning(f"find no tweets after duicate from users, return")
        return 

    rename_file(CURRENT_TWEETS, BEFORE_TWEETS)

    logger.warning(f"【step】5:write new tweets count: {len(resultList)} data to json file")
    with open(CURRENT_TWEETS, "a+") as file:
        file.write(f"{json.dumps(resultList, indent=4, sort_keys=True, default=str)}")

    file.close()

    logger.warning(f"【step】5 write tweet json file, finish")

    #主动推送下新的消息给用户
    logger.warning(f"【step】6 start push tweet to users")
    asyncio.run(push_tweets_to_users())
    logger.warning(f"【step】6 finish push tweet to users")
    
    clean_logfiles()

# if __name__ == "__main__":

#     resultList = []
#     for tw in sortedTweets:
#         print(tw['tweet'])
#         resultList.append(tw["tweet"])

#     logger.warning(f"write count {len(resultList)} data to json file")
#     with open(CURRENT_TWEETS, "a+") as file:
#         file.write(f"{json.dumps(resultList)}")

#     file.close()

t = RepeatingTimer(REFRESH_PERIOD, generate_tweet_list)
t.start()
