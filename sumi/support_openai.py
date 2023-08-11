import openai
import time
import loguru
import json
import base64
import traceback

# openai.api_key = "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"
openai.api_base = "https://api.openai-sb.com/v1"
openai.api_key = "sb-c4555dc97b5732dc0bed25d8650d4b3fc53fac2ae54e84ee"




def askGPT_event_tag(data, tag_config, retry_count=1):
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
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=[{"role": "user", "content": ask}]
        )

        content = completion.choices[0].message.content
        loguru.logger.info(f"gpt analysis -- >({content}")
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
            return askGPT_event_tag(data, retry_count=+1)
        return []
