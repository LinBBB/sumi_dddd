# encoding:utf-8
import asyncio
import json
import os
import random
import time
import tkinter
import datetime
import redis
import pandas as pd
import traceback
import httpx
import aiohttp
import loguru
import uuid
from model.model_stream import TreeOfData, TokenMapping,AllChain,EventTag
from core.mq import get_producer
from pyppeteer import launch
from config import settings
import os
import openai
openai.api_base = "https://api.openai-sb.com/v1"
openai.api_key = "sb-c4555dc97b5732dc0bed25d8650d4b3fc53fac2ae54e84ee"

class TwitterSpider:
    def __init__(self):
        self.last_update_time = int(time.time() + 100) * 1000
        self.first_entryId = None
        self.redis = redis.Redis(
            connection_pool=redis.ConnectionPool.from_url(settings.CELERY_BROKER_URL)
        )
        try:
            self.loop = asyncio.get_event_loop()
        except:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
        # redis_client = redis.Redis(connection_pool=redis.ConnectionPool.
        #    from_url(settings.CELERY_BROKER_URL))

    # def inti(slef):
    #     self.kafka = aiokafka.producer.AIOKafkaProducer

    def askGPT_event_tag(self,data, tag_config, retry_count=1):
        source = data["source"]
        related_cryptocurrency = ",".join(
            list(set([item["coin"] for item in data["suggestions"]]))
        )
        try:
            if source == "Twitter":
                askGPT_content = f"""
                Below is a cryptocurrency-related news, please help me analyze which events it belongs to:
                publisher: "{data['title']}"
                content: "{data['body']}"
                related crypto: "{related_cryptocurrency}"
                """
            else:
                askGPT_content = f"""
                Below is a cryptocurrency-related news, please help me analyze which events it belongs to:
                content: "{data['title']}"
                related crypto: "{related_cryptocurrency}"
                """
            ask_content = f"""
            Hint: Please answer according to the event types I provided. There are the following types of events:
            1.Partnership
            For example, Project A and Project B have formed a partnership, or Project A and Project B have jointly released a statement, etc.
            2.Deployment
            For example, the application has been deployed on the mainnet or testnet.
            3.Buy Back & Burn
            For example, an announcement of token burning or a statement of token buyback by the project team.
            4.Risk Alert
            This means that the project has encountered some risks, such as being hacked, being investigated by regulators, or being reviewed by courts.
            5.Rebranding
            For example, the project has changed its name or upgraded its brand.
            6.Version Update
            For example, a new version of the app has been released, or the product's roadmap has been updated.
            7.List on Exchange
            For example, the project's cryptocurrency has been listed on a Centralized Exchange or DEX such as Binance, OKX, Bitget, Kucoin, Coinbase, Uniswap, etc.
            8.Airdrop & Rewards
            For example, the project team announced a delay in airdrop distribution, announced airdrop rules, or disclosed activity rewards.
            9.Token Unlock
            For example, an announcement of token unlocking by the project team or a delay in token unlocking.
            If this news doesn't belong to any of the above events, please answer "None". Your answer format should be only event types.
        """
            ask = askGPT_content + "\n" + ask_content
            loguru.logger.info(f"ask content with gpt -->{ask}")
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo", messages=[{"role": "user", "content": ask}]
            )

            content = completion.choices[0].message.content
            loguru.logger.info(f"gpt analysis -- >{content}")
            if content == "None":
                return []

            else:
                tag_list = list(tag_config.keys())

                event_list = []
                # loguru.logger.info(f"event_list -- >{event_list}")
                for i in tag_list:
                    event_dict = {}
                    if i.lower() in content.lower():
                        event_dict["id"] = tag_config[i]
                        event_dict["tag_name"] = i
                        event_list.append(event_dict)
                        # event_dict[tag_config[i]] = i
                loguru.logger.info(f"event_list -- >{event_list}")
                if event_list:
                    return event_list
                return []
                # return ",".join([item for item in content.split() if item in event_list])

        except Exception:
            loguru.logger.error("error with askGPT_analysis")
            loguru.logger.error(traceback.format_exc())
            if retry_count < 2:
                time.sleep(2)
                return self.askGPT_event_tag(data, retry_count=+1)
            return []

    async def start(self):
        self.session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False))
        self.kafka_producer = get_producer()
        await self.kafka_producer.start()

    async def stop(self):
        if self.session is not None:
            await self.session.close()
        await self.kafka_producer.stop()

    def __del__(self):
        if not self.loop.is_closed():
            self.loop.run_until_complete(self.stop())

    async def send_data(self, data):
        json_data = json.dumps(data)
        await self.kafka_producer.send_and_wait("tree_of_data", json_data.encode())

    def screen_size(self):
        # 使用tkinter获取屏幕大小
        tk = tkinter.Tk()
        width = tk.winfo_screenwidth()
        height = tk.winfo_screenheight()
        tk.quit()
        return width, height
    async def fetch_address_price(self,address: str, chain_name: str):
      """
      Fetch token price from remote server
      """
      chain_list_pool = {
          "Ethereum": "ethereum",
          "BNB Smart Chain": "bsc",
          "Arbitrum": "arbitrum",
          "Optimism": "optimism",
          "Polygon": "polygon",
      }
      chain_name = chain_list_pool[chain_name]

      # url = f"https://app.geckoterminal.com/api/p1/candlesticks/{gecko_id}/{pairs_id}?resolution={resolution}&from_timestamp={from_timestamp}&to_timestamp={to_timestamp}&for_update=false&count_back=10&currency=usd&is_inverted=false"    use_proxy = os.getenv("ENV", "dev") == "production"
      url = f"https://coins.llama.fi/prices/current/{chain_name}:{address}"
      async with aiohttp.ClientSession() as session:
          use_proxy = os.getenv("ENV", "dev") == "production"
          # async with session.get(url, proxy=proxy_pool) as resp:
          if use_proxy:
              async with session.get(url, proxy=settings.PROXY) as resp:
                  data = await resp.json()
                  if data.get("coin"):
                      try:
                          return list(data["coins"].values())[0]["price"]
                      except:
                          return "-"
                  if data.get("errors"):
                      return "-"
          else:
              async with session.get(url) as resp:
                  data = await resp.json()
                  if data.get("errors"):
                      return "-"
                  try:
                      return list(data["coins"].values())[0]["price"]
                  except:
                      return "-"

    async def find_cell(self, page):
        # TODO:应该滚动找到小叮当
        # 缓慢滚动到底部
        total_height = await page.evaluate("document.body.scrollHeight")
        # 设置每次滚动的步长
        scroll_step = 300
        # 初始化滚动位置
        scroll_position = 0

        while scroll_position < total_height:
            loguru.logger.info(f"{scroll_position} {total_height}")
            total_height = await page.evaluate("document.body.scrollHeight")
            # 执行滚动操作
            await page.evaluate(f"window.scrollBy(0, {scroll_step})")

            # 等待一段时间
            # await asyncio.sleep(0.5)

            # 更新滚动位置
            scroll_position += scroll_step

            # 等待页面滚动到新位置
            await page.waitFor(scroll_step)

            # 找到小宁当位置
            divs = await page.xpath(
                '//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div[3]/section/div/div/div/div/div'
            )

            for div in divs:
                text_element = await div.xpath(".//span")
                for i in text_element:
                    text_property = await i.getProperty("textContent")
                    text = await text_property.jsonValue()
                    # loguru.logger.info(text)
                    if "New Tweet notifications for" in text:
                        # 找到小叮当,点击
                        await div.click()
                        # cell_div = await page.querySelector('div[data-testid="cellInnerDiv"]')
                        # await cell_div.click()
                        loguru.logger.info("找到小叮当了")
                        return

        loguru.logger.warning("滚动到底部还没有找到，准备滚回顶部")
        # 滚回页面顶部
        await page.evaluate("window.scrollTo(0, 0)")
        # 等待页面滚动到新位置,重新找小叮当
        await page.waitFor(scroll_step)
        await self.find_cell(page)

    def perpare_header(self, auth_token):
        try:
            url = "https://twitter.com/i/api/graphql/nK1dw4oV3k4w5TdtcAdSww/SearchTimeline"

            headers = {
                "authority": "twitter.com",
                "accept": "*/*",
                "accept-language": "zh-CN,zh;q=0.9",
                "authorization": "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA",
                "cache-control": "no-cache",
                "cookie": f"auth_token={auth_token};ct0=",
                "pragma": "no-cache",
                "referer": "https://twitter.com/",
                "sec-ch-ua": '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"',
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
                "x-csrf-token": "",  # ct0
                "x-twitter-active-user": "yes",
                "x-twitter-auth-type": "OAuth2Session",
                "x-twitter-client-language": "zh-cn",
            }

            client = httpx.Client(headers=headers)

            res1 = client.get(url)

            # 第一次访问用于获取response cookie中的ct0字段，并添加到x-csrf-token与cookie中
            ct0 = res1.cookies.get("ct0")

            client.headers.update(
                {"x-csrf-token": ct0, "cookie": f"auth_token={auth_token};ct0={ct0}"}
            )

            return client.headers
        except Exception as e:
            loguru.logger.error(e)
            loguru.logger.info("重新生成请球头")
            return self.perpare_header(random.choice(list(auth_token_lists.values())))


    def genrate_params(self, tweetId):
        variables = {
            "tweetId": tweetId,
            "count": 1,
            "includePromotedContent": True,
            "withQuickPromoteEligibilityTweetFields": True,
            "withSuperFollowsUserFields": True,
            "withDownvotePerspective": False,
            "withReactionsMetadata": False,
            "withReactionsPerspective": False,
            "withSuperFollowsTweetFields": True,
            "withVoice": True,
            "withV2Timeline": True,
            "responsive_web_twitter_blue_verified_badge_is_enabled": True,
            "verified_phone_label_enabled": False,
            "responsive_web_graphql_timeline_navigation_enabled": True,
            "withCommunity": True,
        }

        features = {
            "longform_notetweets_consumption_enabled": True,
            "tweetypie_unmention_optimization_enabled": True,
            "vibe_api_enabled": True,
            "responsive_web_edit_tweet_api_enabled": True,
            "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
            "view_counts_everywhere_api_enabled": True,
            "freedom_of_speech_not_reach_appeal_label_enabled": False,
            "standardized_nudges_misinfo": True,
            "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": False,
            "interactive_text_enabled": True,
            "responsive_web_text_conversations_enabled": False,
            "responsive_web_twitter_blue_verified_badge_is_enabled": True,
            "verified_phone_label_enabled": False,
            "responsive_web_graphql_timeline_navigation_enabled": True,
            "responsive_web_enhance_cards_enabled": False,
        }

        parameters = {
            "queryId": "jQRDIE-Pa0f5XKB0U7-GOg",
            "variables": json.dumps(variables),
            "features": json.dumps(features),
        }
        return parameters

    # 根据tweetid获取数据
    async def parse_tweet(self, tweetId, number=1):
        tweet_res = []
        # 每条帖子执行次数
        # number = 1

        # 第一步,先产生请求头
        headers = self.perpare_header(random.choice(list(auth_token_lists.values())))

        # while number < 100:
        async with httpx.AsyncClient(headers=headers) as client:
            response = await client.get(
                url="https://api.twitter.com/graphql/jQRDIE-Pa0f5XKB0U7-GOg/TweetResultByRestId",
                params=self.genrate_params(tweetId=tweetId),
                timeout=30000,
            )
            if response.status_code == 200:
                try:
                    data = response.json()

                    if (
                        data["data"]["tweetResult"]["result"]["__typename"]
                        == "TweetWithVisibilityResults"
                    ):
                        detail_data = data["data"]["tweetResult"]["result"]["tweet"]
                        created_at = detail_data["legacy"]["created_at"]
                        entryId = data["data"]["tweetResult"]["result"]["tweet"][
                            "rest_id"
                        ]
                    else:
                        detail_data = data["data"]["tweetResult"]["result"]
                        entryId = data["data"]["tweetResult"]["result"]["rest_id"]

                        created_at = data["data"]["tweetResult"]["result"]["legacy"][
                            "created_at"
                        ]
                    # 将字符串时间解析为 datetime 对象
                    dt = datetime.datetime.strptime(
                        created_at, "%a %b %d %H:%M:%S %z %Y"
                    )

                    # 将 datetime 对象转换为 UTC 时间戳
                    created_at = int(dt.timestamp()) * 1000

                    # 帖子信息

                    res_dict = {}
                    tweet_info = {}
                    loguru.logger.warning(f"user --> {detail_data}")
                    # 1.获取用户信息
                    user_id = detail_data["core"]["user_results"]["result"]["rest_id"]
                    loguru.logger.debug(f"我的用户id{user_id}")
                    twitter_user_info_data = detail_data["core"]["user_results"][
                        "result"
                    ]["legacy"]
                    # followers_count = twitter_user_info_data["followers_count"]
                    # favourites_count = twitter_user_info_data["favourites_count"]
                    screen_name = twitter_user_info_data["screen_name"]
                    # friends_count = twitter_user_info_data["friends_count"]
                    # statuses_count = twitter_user_info_data["statuses_count"]
                    user_profile_img_url = twitter_user_info_data[
                        "profile_image_url_https"
                    ]

                    # twitter info

                    views_count = detail_data.get("views", {}).get("count", 0)

                    tweet_info_data = detail_data["legacy"]

                    # 图片
                    entities = tweet_info_data.get("entities")
                    media = entities.get("media")
                    image_lists = []
                    if media:
                        for m in media:
                            image_lists.append(m.get("media_url_https"))

                    favourite_count = tweet_info_data.get("favorite_count", 0)
                    full_text = tweet_info_data.get("full_text")
                    is_quote_status = tweet_info_data.get("is_quote_status")
                    # 引用
                    quote_count = tweet_info_data.get("quote_count", 0)
                    reply_count = tweet_info_data.get("reply_count", 0)
                    retweet_count = tweet_info_data.get("retweet_count", 0)
                    # 回复
                    in_reply_to_screen_name = tweet_info_data.get(
                        "in_reply_to_screen_name"
                    )
                    is_reply = True if in_reply_to_screen_name else False

                    # 用户信息
                    # tweet_info["user_id"] = user_id
                    # tweet_info["screen_name"] = screen_name
                    # tweet_info["profile_image"] = user_profile_img_url
                    # user_info["followers_count"] = followers_count
                    # user_info["favourites_count"] = favourites_count
                    # user_info["friends_count"] = friends_count
                    # user_info["statuses_count"] = statuses_count

                    # 帖子信息
                    # tweet_info["entry_id"] = entryId
                    # tweet_info["view"] = views_count
                    # tweet_info["created_at"] = created_at
                    # tweet_info["entities"] = entities
                    # tweet_info["like"] = favourite_count
                    # tweet_info["body"] = full_text
                    # tweet_info["is_quote_status"] = is_quote_status
                    # tweet_info["quote"] = quote_count
                    # tweet_info["reply"] = reply_count
                    # tweet_info[
                    #     "link"
                    # ] = f"https://twitter.com/{screen_name}/status/{entryId}"
                    # tweet_info["time"] = created_at
                    # tweet_info["retweet"] = retweet_count
                    # if is_retweeted:
                    #     tweet_info["source"] = "retweet"
                    # if is_reply:
                    #     tweet_info["source"] = "reply"

                    # 如果是引用
                    if is_quote_status:
                        quote_user_info = {}
                        quote_tweet_info = {}
                        detail_tweet = data["data"]["tweetResult"]["result"]

                        # 引用的用户信息
                        tweet_quote_data = detail_tweet["quoted_status_result"][
                            "result"
                        ]["core"]["user_results"]["result"]["legacy"]
                        quote_user_id = detail_tweet["quoted_status_result"]["result"][
                            "core"
                        ]["user_results"]["result"]["rest_id"]
                        quote_user_screen_name = tweet_quote_data["screen_name"]
                        quote_user_followers_count = tweet_quote_data["followers_count"]
                        quote_user_favorite_count = tweet_quote_data["favourites_count"]
                        quote_user_description = tweet_quote_data["description"]
                        quote_user_info[
                            "quote_user_screen_name"
                        ] = quote_user_screen_name
                        quote_user_info[
                            "quote_user_followers_count"
                        ] = quote_user_followers_count
                        quote_user_info[
                            "quote_user_favorite_count"
                        ] = quote_user_favorite_count
                        quote_user_info[
                            "quote_user_description"
                        ] = quote_user_description

                        # 引用帖子的信息
                        quoted_status_id_str = data["data"]["tweetResult"]["result"][
                            "legacy"
                        ].get("quoted_status_id")
                        quote_create_at = data["data"]["tweetResult"]["result"][
                            "quoted_status_result"
                        ]["result"]["legacy"]["created_at"]
                        quote_conversation_id_str = data["data"]["tweetResult"][
                            "result"
                        ]["quoted_status_result"]["result"]["legacy"][
                            "conversation_id_str"
                        ]
                        quote_full_text = data["data"]["tweetResult"]["result"][
                            "quoted_status_result"
                        ]["result"]["legacy"]["full_text"]
                        quote_favorite_count = data["data"]["tweetResult"]["result"][
                            "quoted_status_result"
                        ]["result"]["legacy"].get("favorite_count", 0)
                        quote_quote_count = data["data"]["tweetResult"]["result"][
                            "quoted_status_result"
                        ]["result"]["legacy"].get("quote_count", 0)
                        quote_reply_count = data["data"]["tweetResult"]["result"][
                            "quoted_status_result"
                        ]["result"]["legacy"].get("reply_count", 0)
                        quote_retweet_count = data["data"]["tweetResult"]["result"][
                            "quoted_status_result"
                        ]["result"]["legacy"].get("retweet_count", 0)
                        quote_entities = data["data"]["tweetResult"]["result"][
                            "quoted_status_result"
                        ]["result"]["legacy"]["entities"]

                        quote_tweet_info["quoted_user_id"] = quote_user_id
                        quote_tweet_info["quoted_status_id_str"] = quoted_status_id_str
                        quote_tweet_info["quote_created_at"] = quote_create_at
                        quote_tweet_info[
                            "quote_conversation_id_str"
                        ] = quote_conversation_id_str
                        quote_tweet_info["quote_full_text"] = quote_full_text
                        quote_tweet_info["quote_quote_count"] = quote_quote_count
                        quote_tweet_info["quote_favorite_count"] = quote_favorite_count
                        quote_tweet_info["quote_reply_count"] = quote_reply_count
                        quote_tweet_info["quote_retweet_count"] = quote_retweet_count
                        # quote_tweet_info["quote_entities"] = quote_entities

                        # tweet_info["original_user_id"] = quote_user_id
                        # tweet_info[
                        #     "original_url"
                        # ] = f"https://twitter.com/{quote_user_screen_name}/status/{quoted_status_id_str}"
                        # tweet_info["original_screen_name"] = quote_user_screen_name
                        # tweet_info["original_profile"] = quote_user_info
                        # tweet_info["created_at"] = quote_create_at

                        res_dict["quote_user_info"] = quote_user_info
                        res_dict["quote_tweet_info"] = quote_tweet_info
                        tweet_res.append(res_dict)
                        # loguru.logger.info(res_dict)

                    elif is_reply:
                        reply_info = {}
                        in_reply_to_screen_name = data["data"]["tweetResult"]["result"][
                            "legacy"
                        ].get("in_reply_to_screen_name")
                        in_reply_to_user_id_str = data["data"]["tweetResult"]["result"][
                            "legacy"
                        ].get("in_reply_to_user_id_str")
                        in_reply_to_status_id_str = data["data"]["tweetResult"][
                            "result"
                        ]["legacy"].get("in_reply_to_status_id_str")
                        reply_info["in_reply_to_screen_name"] = in_reply_to_screen_name
                        reply_info["in_reply_to_user_id_str"] = in_reply_to_user_id_str
                        reply_info[
                            "in_reply_to_status_id_str"
                        ] = in_reply_to_status_id_str

                        res_dict["reply_info"] = reply_info
                        # tweet_info["original_user_id"] = in_reply_to_user_id_str
                        # tweet_info[
                        #     "original_url"
                        # ] = f"https://twitter.com/{in_reply_to_screen_name}/status/{in_reply_to_status_id_str}"
                        # tweet_info["original_screen_name"] = in_reply_to_screen_name
                        # tweet_info["original_profile"] = in_reply_to_user_id_str
                        # tweet_info["created_at"] = in_repl

                        tweet_res.append(res_dict)
                        # loguru.logger.info(res_dict)
                    else:
                        tweet_res.append(res_dict)
                        # loguru.logger.info(res_dict)


                    # TODO send data to kafka


                    for i in self.token_mapping:
                        twitter_id = i.get('twitter_id')
                        # 对比两者的推特id
                        if int(twitter_id) == int(user_id):
                            loguru.logger.debug("我是目标用户")
                            loguru.logger.error(i)
                            tweet_info["body"] = full_text
                            tweet_info["icon"] = user_profile_img_url
                            tweet_info["id"] = str(uuid.uuid4())
                            tweet_info["image"] = image_lists
                            tweet_info["isQuote"] = is_quote_status
                            tweet_info["isReply"] = is_reply
                            tweet_info["isRetweet"] = True if full_text.startswith("RT") else False
                            tweet_info["link"] = f"https://twitter.com/{screen_name}/status/{tweetId}"
                            tweet_info["platform"] = "dex"
                            tweet_info["requireInteraction"] = True
                            tweet_info["source"] = "Twitter"
                            # 1.suggestion
                            tweet_info["suggestions"] = [{"coin":i["symbol"]}]
                            tweet_info["symbol"] = i["symbol"]

                            tweet_info["time"] = created_at
                            tweet_info["title"] = screen_name
                            tweet_info["token_info"] = [{"symbol":i["symbol"],"chain_info":[{"address":i["address"],"chain_icon":i["chain_icon"],"chain_id":i["chain_id"],"chain_name":i["chain_name"]}],
                                                         "decimals":i["decimals"],
                                                         "price":await self.fetch_address_price(i["address"],i["chain_name"]),
                                                         "logo_url":i["logo_url"],
                                                         "name":i["name"]

                                                        }]
                            tweet_info["ts"] = int(time.time())
                            tweet_info["twitterId"] = twitter_id
                            # 进去拿tag
                            tag = self.askGPT_event_tag(data=tweet_info,tag_config=self.tag_config)
                            tweet_info["tag"] = tag
                            loguru.logger.info(tweet_info)
                            TreeOfData.insert(**tweet_info).execute()
                            await self.send_data(tweet_info)

                except Exception as e:
                    loguru.logger.warning(traceback.format_exc())
                    loguru.logger.warning(f"{e} {response.text} {headers}")
                    # await self.parse_tweet(tweetId=tweetId, number=number)
            else:
                loguru.logger.error(response.text)
                # 超时
                loguru.logger.warning(f"重新执行{tweetId} 目前第{number}次 {headers}")
                await self.parse_tweet(tweetId=tweetId, number=number)

    async def parse_data(self, page, redis_lists, flag):
        # 进入页面后,滚到直到没有重复数据
        loguru.logger.info(f"开始滚动,滚动到没有重复数据")
        # 缓慢滚动到底部
        total_height = await page.evaluate("document.body.scrollHeight")
        # 设置每次滚动的步长
        scroll_step = 600
        # 初始化滚动位置
        scroll_position = 0
        # 滚动次数
        scroll_position_count = 0

        while scroll_position < total_height and scroll_position_count < 10:
            scroll_position_count += 1
            # 缓慢滚动到底部
            total_height = await page.evaluate("document.body.scrollHeight")
            # 执行滚动操作
            await page.evaluate(f"window.scrollBy(0,{scroll_step})")
            # 等待一段时间
            await asyncio.sleep(0.5)
            # 更新滚动位置
            scroll_position += scroll_step
            # 等待页面滚动到新的位置
            await page.waitFor(scroll_step)
            # 一边滚动一边解析数据
            # 解析数据

            content_divs = await page.xpath(
                '//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div[1]/div/section/div/div/div/div/div'
            )
            for div in content_divs:
                # 根据帖子id判断滚轮退出
                entryId_element = await div.xpath(
                    "./div/div/article/div/div/div[2]/div[2]/div[1]/div/div[1]/div/div/div[2]/div/div[3]/a"
                )
                for i in entryId_element:
                    entryId_property = await i.getProperty("href")
                    entryId = await entryId_property.jsonValue()

                entryId = entryId.split("/")[-1]

                # 第一次进入,的第一条推
                if flag == 1:
                    # 如果是第一次启动程序,获取小叮当第一条数据时间
                    self.first_entryId = entryId
                    redis_lists.append(f"first_tweet:{self.first_entryId}")
                    loguru.logger.warning(f"第一进入的第一条推特是{self.first_entryId}")
                    return

                # 第二次进入
                else:
                    # 再次进入时,如果第一个是这个东西直接返回
                    if entryId == self.first_entryId:
                        loguru.logger.warning("已经滚到第一次启动程序的第一条推")
                        return

                    if entryId not in redis_lists:
                        redis_lists.append(entryId)
                        # 最新一帖子的时间(第一次进入小叮当时候第一条推的时间)
                        asyncio.create_task(self.parse_tweet(tweetId=entryId))

    async def main(self):
        await self.start()
        all_token_data = (TokenMapping
         .select(
             TokenMapping.symbol,
             TokenMapping.name,
             TokenMapping.address,
             TokenMapping.decimals,
             TokenMapping.logo_url,
             TokenMapping.pool_address,
             TokenMapping.chain_name,
             TokenMapping.chain_id,
             TokenMapping.twitter_id,
             AllChain.chain_icon
         ).where(TokenMapping.twitter_id.is_null(False))
         .join(AllChain, on=(TokenMapping.chain_id == AllChain.chain_id))
        )
        # for record in all_token_data:
        #       print(record.symbol, record.name, record.address, record.allchain.chain_icon)
        # all_token_data = TokenMapping.select().where(TokenMapping.twitter_id is not None)
        self.token_mapping = [
            {
                "symbol": row.symbol,
                "name": row.name,
                "address": row.address,
                "decimals": row.decimals,
                "logo_url": row.logo_url,
                "twitter_id": row.twitter_id,
                "pool_address": row.pool_address,
                "address": row.address,
                "chain_name": row.chain_name,
                "chain_id": row.chain_id,
                "chain_icon": row.allchain.chain_icon,
            }
            for row in all_token_data
        ]

        # loguru.logger.info(self.token_mapping)

        # 拿取tag

        tag_config_data = EventTag.select(EventTag.id,EventTag.tag_name)
        self.tag_config = {tag.tag_name:tag.id for tag in tag_config_data}
        # loguru.logger.debug(tag_config)



        width, height = self.screen_size()
        # 启动浏览器
        browser = await launch(
            {
                "executablePath": "/usr/bin/google-chrome",
                "headless": False,  # 无头
                "dumpio": True,  # 解决浏览器多开页面卡死
                "autoClose": False,
                "ignoreDefaultArgs": ["--enable-automation"],
                "args": [
                    "--no-sandbox",
                   "--window-size=1918,926",
                    "--disable-setuid-sandbox",
                ],
            }
        )

        # 创建一个页面
        page = await browser.newPage()

        # 设置视口大小为最大化

        await page.setViewport({"width": 1918, "height": 926})
        await page.setJavaScriptEnabled(enabled=True)  # 允许 javascript 执行

        # 导航到网页
        await page.goto("https://twitter.com/home")

        # 等待一段时间
        await asyncio.sleep(3)

        username_xpath = '//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[5]/label/div/div[2]/div/input'
        await page.waitForXPath(username_xpath)
        username = await page.xpath(username_xpath)

        # 输入文本
        await username[0].type("@cccbbb009")

        await asyncio.sleep(5)

        # 点击
        next_step_xpath = '//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[6]/div/span/span'
        await page.waitForXPath(next_step_xpath)
        next_step = await page.xpath(next_step_xpath)
        await next_step[0].click()

        await asyncio.sleep(4)

        # 密码
        password_xpath = '//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div/div[3]/div/label/div/div[2]/div[1]/input'
        await page.waitForXPath(password_xpath, options={"timeout": 30000000000})
        password = await page.xpath(password_xpath)
        await password[0].type("cb123456")

        # 点击登录
        login_button_xpath = '//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[2]/div/div[1]/div/div/div/div/span/span'
        await page.waitForXPath(login_button_xpath)
        login_button = await page.xpath(login_button_xpath)
        await login_button[0].click()

        await asyncio.sleep(5)

        redis_lists = []
        # 判断小叮当 等待元素出来
        xpath_expression = '//*[@id="react-root"]/div/div/div[2]/header/div/div/div/div[1]/div[2]/nav/a[3]/div/div/div'

        flag = 1
        while True:
            try:
                element = await page.waitForXPath(
                    xpath_expression, options={"timeout": 10000}
                )
                if element:
                    # 点击Notifications
                    notifications_xpath = '//*[@id="react-root"]/div/div/div[2]/header/div/div/div/div[1]/div[2]/nav/a[3]'
                    await page.waitForXPath(notifications_xpath)
                    notifications = await page.xpath(notifications_xpath)
                    await notifications[0].click()

                    await asyncio.sleep(2)
                    await page.reload()

                    # 找小叮当
                    await self.find_cell(page)

                    await asyncio.sleep(1)
                    # await page.waitForNavigation()

                    await self.parse_data(page, redis_lists, flag)

                    loguru.logger.info(f"目前的数据{redis_lists},总长{len(redis_lists)},第{flag}次")
                    flag += 1
            except Exception as e:
                loguru.logger.info(f"30s没有数据刷新{e}")
                # await page.goto("https://twitter.com/i/timeline")
                # await page.waitForNavigation()
                await page.reload(options={"timeout":10000})



if __name__ == "__main__":
    auth_token_lists = {
        "@cccbbb001.json": "9529eb99f534605b7afa27f46d956b15a32e4799",
        "@cccbbb002.json": "5b81fd7c1a70fbed11ae2b2cf438f8f869f36bd8",
        "@cccbbb003.json": "a73e1004e7c9f7e4932d228afcbc08265f06c128",
        "@cccbbb004.json": "85a04a70a8d3275e98dc93b098c3241f07d5e33f",
        "@cccbbb005.json": "274f72969b50ce1d830505cc3575f212ec4771d4",
        "@cccbbb006.json": "c75dde1a5ceb41c18468fb5f0047995aaf3b3a5f",
        "@cccbbb008.json": "c8253c0b1feb3dea5a6d6fea70fc19033bb680c8",
        "@cccbbb009.json": "10171721b4c31c6922f256da1ac27aa7d791eb83",
        "@cccbbb0100.json": "a09d6e37ccd83ed35b2a71ed4d241e530e527ee2",
        "@cccbbb011.json": "ba4169dc43ae082822d0c42e237893aa69aa69c6",
        "@cccbbb012a.json": "1dd67ce0aafeeba25360d948bfdd00dfb9c314ae",
        "@cccbbb013.json": "e9142ec8ecaea5c5eb5765f590e1dce5badeabf2",
        "@cccbbb014.json": "a0e4cbb5c8815d8f2e1855173cad1c59194eabe6",
        "@cccbbb015.json": "c70f52ff5296dcc9ddad78c1b193fc22af768873",
        "@cccbbb016.json": "6a0dc9a40d40656701638c0a7445dc162eddd44c",
        "@cccbbb017.json": "5e68c27dab719efe9fbd89926d8cb8702a9f2857",
        "@cccbbb018.json": "f0383e7d44ffa79383d649e762a9f166b5b02a1e",
        "@cccbbb019.json": "4f2dcb9b787c55ac586f0476ebdeed9a0d741297",
        "@cccbbb020.json": "fb2a564d4b1b00d1776bcb74fb0f8e279dd268e4",
        "@cccbbb021.json": "2c80fcb46602ae23029e0ca586f3d1533f743b61",
        "@cccbbb022.json": "db56c8a46b3795ab16c4dbad83a3483ddd4895c9",
        "@cccbbb023.json": "95b47048ce99d88f50579230852fa0e2ffe2beec",
        "@cccbbb024.json": "411b49dd7e9c2b9e5ff4e550600d18cdb6fad085",
        "@cccbbb025.json": "8ad034d2a403a9a6dcbbcb0ff0cad417f905fea7",
        "@cccbbb026.json": "0ebf64b8036c18371c84cf94befc6b9009e3571c",
        "@cccbbb027.json": "6e73e2595e70b68af0dce0efd506d8f6f55ec4f2",
        "@cccbbb028.json": "d79b1011145a2ff3c696381e9069bb90fb5682c1",
        "@cccbbb029.json": "6c53f0fa486c08a687c1ec531d1539e424e8ac26",
        "@cccbbb030.json": "49ff6d03c24f76694d2eb260c3fcda8034de8a67",
    }
    run = TwitterSpider()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run.main())
    loop.run_forever()
