#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2025/2/14 10:26
# @Author   : songzb

import datetime
import os
from loguru import logger
from collections import OrderedDict
import re
import json
import requests
import asyncio
import copy


def init_logger(version, log_env, desc="", save_day="1", use_vllm=False):
    """
    初始化日志存储
    """
    now = datetime.datetime.now()
    # log_env_desc = "online" if log_env else "test"
    log_env_desc = copy.copy(log_env)  #
    if log_env_desc != "":
        vllm_desc = "_VLLM" if use_vllm else ""
        log_dir = os.path.expanduser(f"nohup_logs/{desc}{now.year}_{now.month}_{now.day}")
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        log_file = os.path.join(log_dir, f"{version}_{now.year}-{now.month}-{now.day}_{log_env_desc}{vllm_desc}.log")
        logger.add(log_file, enqueue=True, rotation=f"{save_day} day")
        logger.info("【开始存储日志】")
        logger.info(log_file)
        return logger
    else:
        logger.info("【不存储日志】")
        return logger


def contains(targets, items, exist=True, use_lcs=False):
    """
    exist为True：则认为targets中有items中的元素 返回True 有在就是True
    exist为False：则认为items中的元素都在targets中 返回True 都在才是True
    """
    if exist:
        for item in items:
            if use_lcs:
                if len(get_lcs(item, targets)) > 1:
                    return True
            else:
                if item in targets:
                    return True
        return False
    else:
        for item in items:
            if use_lcs:
                if len(get_lcs(item, targets)) < 1:
                    return False
            else:
                if item not in targets:
                    return False
        return True


def unique_sort(items, sort=False):
    """
    列表去重并且排序
    """
    if isinstance(items, list):
        unique_items = list(OrderedDict.fromkeys(items))
        if sort:
            unique_items.sort()
        return unique_items
    else:
        return items


def has_level_type(level_list, key, extra=None):
    """

    """
    if extra:
        return True if key in [lev.split("-")[0] for lev in level_list] or contains(extra, level_list) else False
    else:
        return True if key in [lev.split("-")[0] for lev in level_list] else False


def clean(lang, text, action2comb_map, level1_action):
    """
    清理（）/()两种括号的提示内容
    """
    pattern = r'\((.*?)\)' if lang == "en" else r'（(.*?)）'
    l = '(' if lang == "en" else '（'
    r = ')' if lang == "en" else '）'
    for a in re.findall(pattern, text):
        remove = True
        for _a in a.split("、"):
            if _a not in action2comb_map.values() and _a not in level1_action and "-" not in _a \
                    and _a not in [a_map.split("-")[-1] for a_map in action2comb_map.values()]:
                remove = False
                if "问：" in _a:
                    text = text.replace(f"{l}问：", "，").replace(f"{r}", "")
                elif "问" in _a:
                    if len(text) - text.index(f"{r}") < 3:
                        text = text.replace(f"{l}", "，").replace(f"{r}", "")
                    else:
                        text = text.replace(f"{l}{_a}{r}", "")
        if remove:
            text = text.replace(f"{l}{a}{r}", "")
    text = text.replace("【百度商家智能体】", "").replace("百度商家智能体】", "").replace("【商家智能体】", "").replace(
        "商家智能体】", "")
    if ")" in text:
        pos = text.index(")") + 1
        text = text[pos:]
    elif "、套电" in text:
        pos = text.index("、套电") + 3
        text = text[pos:]
    return text


def get_messages(history, query, system_prompt="", history_action=None, action2comb_map=None, logger=None):
    def add_user(messages, history_list, text):
        if messages[-1]["role"] == "user":
            messages[-1]["content"] += f"<sep>{text}"
            history_list[-1] += f"<sep>{text}"
        else:
            messages.append({"role": "user", "content": text})
            history_list.append(text)
        return messages, history_list

    history_list = []
    messages = [{"role": "system", "content": system_prompt}]
    for turn, (old_query, response) in enumerate(history):
        old_query = old_query.replace("\n", "")
        response = response.replace("\n", "")
        if history_action is not None:
            if len(history_action) > turn:
                trans_action_list = [action2comb_map.get(a, a) for a in history_action[turn].split('、')]
                resp_prompt = f"({'、'.join(unique_sort(trans_action_list))})"
            else:
                resp_prompt = ""
        else:
            resp_prompt = ""
        if logger is not None:
            logger.info(f"Round{turn} CLIENT: {old_query}")
            logger.info(f"Round{turn} SERVER: {resp_prompt}{response}")
        else:
            print(f"Round{turn} CLIENT: {old_query}")
            print(f"Round{turn} SERVER: {resp_prompt}{response}")
        if response != "":
            messages, history_list = add_user(messages, history_list, text=old_query)
            messages.append({"role": "assistant", "content": resp_prompt + response})
            history_list.append(response)
        else:
            messages.append({"role": "user", "content": old_query})
            history_list.append(old_query)
    if logger is not None:
        logger.info(f"Round{len(history_list) // 2} CLIENT: {query}")
    else:
        print(f"Round{len(history_list) // 2} CLIENT: {query}")
    messages, history_list = add_user(messages, history_list, text=query)
    return messages, history_list


def format_dialogs(dialog_record, keyword="", history_action_list=None):
    """
    将dialog_record整理成输入模型所需的格式
    """

    def get_sep_token(tmp_round, use_action=True):
        if use_action:
            return "、" if len(tmp_round) > 1 else ""
        else:
            return "<sep>" if len(tmp_round) > 1 else ""

    if len(dialog_record) > 1:
        use_history_action = True if "action" in dialog_record[1].keys() else False
    elif len(dialog_record) == 1:
        use_history_action = True if dialog_record[0].get("role") == "SERVER" and \
                                     "action" in dialog_record[0].keys() else False
    else:
        use_history_action = False
    history, tmp_history, tmp_round = [], [], []
    history_action, tmp_history_action, tmp_round_action = [], [], []
    current_role = ""
    for i, context in enumerate(dialog_record):
        if i == 0 and context["role"] == "SEARCH":
            keyword = context["sentence"]
            context["role"] = "CLIENT"
        if context["role"] == "CLIENT":
            if current_role == "SERVER":
                tmp_history.append(f"{get_sep_token(tmp_round, use_action=False)}".join(tmp_round))  # 拼接server
                history.append(tmp_history)
                if use_history_action:
                    tmp_history_action.append(f"{get_sep_token(tmp_round_action)}".join(tmp_round_action))
                    history_action.append("、".join(tmp_history_action))
                tmp_history, tmp_round, tmp_history_action, tmp_round_action = [], [], [], []
            if i == len(dialog_record) - 1:
                tmp_round.append(context["sentence"])
                tmp_history.append(f"{get_sep_token(tmp_round, use_action=False)}".join(tmp_round))
                tmp_history.append("")  # 最后一句为client的情况，需要补充一句空字符串的server
                history.append(tmp_history)
            tmp_round.append(context["sentence"])
            current_role = context["role"]
        elif context["role"] == "SERVER":
            if i == 0:
                tmp_history.append(keyword)
                if use_history_action and len(context["action"]) > 0:
                    if isinstance(context["action"][0], list):
                        tmp_history_action.extend(context["action"][0])
                    else:
                        tmp_history_action.append(context["action"][0])
            else:
                if current_role == "CLIENT":
                    tmp_history.append(f"{get_sep_token(tmp_round, use_action=False)}".join(tmp_round))  # 拼接client
                    tmp_round = []
            tmp_round.append(context["sentence"])
            if use_history_action and len(context["action"]) > 0:
                tmp_round_action.append("、".join(context["action"][0]))
            current_role = context["role"]
            if i == len(dialog_record) - 1:
                tmp_history.append(f"{get_sep_token(tmp_round, use_action=False)}".join(tmp_round))
                history.append(tmp_history)
                if use_history_action:
                    tmp_history_action.append(f"{get_sep_token(tmp_round_action)}".join(tmp_round_action))
                    history_action.append("、".join(tmp_history_action))
    if history_action_list is None:
        history_action_list = []
    if len(history_action_list) > 0 and len(history_action) == 0:
        history_action = history_action_list
    return history, history_action


def nlu_async_service(text, domain, url, logger, tasks):
    def request_nlu(text, domain, url, logger, task="intent"):
        data = {"sentence": text, "domain": domain, "task": task}
        try:
            return requests.post(url, data=json.dumps(data), timeout=3).json()['response']
        except Exception as e:
            logger.error(f"[{task}]请求接口失败：{e} ---{url}")
            return {} if task == "ner" else dict(zip(text, [""] * len(text)))

    async def async_nlu(text, domain, url, logger, task):
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, request_nlu, text, domain, url, logger, task)
        return result

    async def nlu_thread(text, domain, url, logger, task):
        logger.debug(f"[START]========== Task: {task} ==========")
        result = await async_nlu(text=text, domain=domain, url=url, logger=logger, task=task)
        return result

    coros = []
    for task in tasks:
        coros.append(nlu_thread(text=text, domain=domain, url=url, logger=logger, task=task))
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    threads = [loop.create_task(coro) for coro in coros]
    loop.run_until_complete(asyncio.wait(threads))
    outputs = {}
    for task, thread in zip(tasks, threads):
        outputs[task] = thread.result()
    return outputs


def init_template(faq_answers, kn_answer_action, current_round, action2comb_map, logger):
    knowledges = faq_answers.get("answers", []) if faq_answers is not None else []
    call_knowledges = faq_answers.get("electricalAnswers", []) if faq_answers is not None else []
    if len(kn_answer_action) > 0:
        knowledge_action = ["、".join(one) for one in list(kn_answer_action.values())[0]]  # [["A", "B"]]
    else:
        knowledge_action = [""]
    valid_knowledge, valid_kn_action = [], []
    if len(knowledges) > 0:
        for knowledge, action in zip(knowledges[:1], knowledge_action[:1]):
            # valid_knowledge.append(BeautifulSoup(knowledge, 'html.parser').get_text())
            valid_knowledge.append(re.sub(r"<[^>]+>", "", knowledge))
            valid_kn_action.append("、".join([action2comb_map.get(a, a) for a in action.split("、")]))
    else:
        if len(call_knowledges) > 0:
            for knowledge in call_knowledges[:1]:
                valid_knowledge.append(re.sub(r"<[^>]+>", "", knowledge))
                valid_kn_action.append("套电")
    logger.debug(valid_knowledge)
    logger.debug(valid_kn_action)
    if len(valid_knowledge) > 0:
        template_types = []
        for action in valid_kn_action[0].split("、"):  # ["A、B"]
            if "-" not in action:
                if "套电" in action or "套联" in action:
                    template_types.append("套电")
                else:
                    template_types.append("答疑")  # 默认就是答疑 空字符串也是答疑
            else:
                template_types.append(action.split("-")[0])
        if contains(items=["答疑"], targets=template_types):  # 只要模板问答里面包含答疑
            return valid_knowledge, "答疑-续写", ["(问)", "(套电)"] if current_round > 3 else ["(问)"] * 2
        elif contains(items=["套电"], targets=template_types):  # 模板问答里面没有答疑，有套电的情况
            return valid_knowledge, "套电-续写", ["(答疑)"] * 2 if current_round > 3 else ["(答疑、问)", "(答疑)"]
        else:  # 模板问答里没有答疑也没有套电（可能识别错或者报错）
            return valid_knowledge, "无-续写", ["(答疑、问)", "(答疑、套电)"]
    else:  # 没有模板问答的情况
        return valid_knowledge, "无-续写", ["(答疑、问)", "(答疑、套电)"]


def template_continue(prompt, conti, no_list=[]):
    """
    由于模板问答需要进行续写，因此排除，对应类型的引导action
    """

    prompt_wo_answer = [""] * len(prompt)
    for i, tmp_p in enumerate(prompt):
        tmp_p_wo = []
        if ")" in tmp_p:
            tmp_p, outer_p = tmp_p.replace("(", "").replace(")", ""), True
        else:
            tmp_p, outer_p = tmp_p.replace("(", ""), False
        for p in tmp_p.split("、"):
            # 模板问答存在的部分或者特别的列表词包含在action则不做生成
            if conti.split("-")[0] not in p and not contains(items=no_list, targets=p):
                tmp_p_wo.append(p)
        if len(tmp_p_wo) > 0:
            prompt_wo_answer[i] = f"({'、'.join(tmp_p_wo)})" if outer_p else f"({'、'.join(tmp_p_wo)}"
        else:
            prompt_wo_answer[i] = ""
    return prompt_wo_answer


def repl(text, prompt, intent, domain):
    """
    将token进行替换
    """

    def remove_none(input_list):
        tmp_input_list = copy.copy(input_list)
        if "" in input_list:
            tmp_input_list.remove("")
        return tmp_input_list

    text = str(text)
    if domain == "hair":
        text = text.replace("新生植发", "雍禾植发").replace("碧莲盛", "雍禾").replace("雍禾是国企公立医院", "雍禾是上市公司")
    elif domain == "dentistry":
        text = text.replace("布洛芬", "药").replace("甲硝锉", "药").replace("甲肖锉", "药").replace("甲硝唑", "药").replace(
            "头孢克肟", "消炎药").replace("头孢拉定", "消炎药").replace("头孢", "消炎药").replace("阿莫西林", "消炎药")
    if re.search(r"去.{0,3}医院", text):
        pos = re.search(r"去.{0,3}医院", text).span()[0]
        text = text[:pos] + "来" + text[pos + 1:]
    if "user" in text:
        text = text.split("user")[0]

    text = re.sub("(1[3-9]\d{9}|1[3-9]\d{1}[-.,，]{0,1}\d{4}[-.,，]{0,1}\d{4})", "[[customerMobile]]", text)
    text = re.sub("微信是([a-zA-Z]{1}[-_a-zA-Z0-9]{5,19})", "微信是 [[customerWeixin]]", text)
    text = text.replace("<mobile>", "[[customerMobile]]").replace("<montage>", "").replace(
        "我们<organization>", "我们这里").replace("<organization>", "我们这里")
    text = text.replace("customerWeixin", "sep1").replace("customerMobile", "sep2")
    if "微信" in text and re.search(r"[a-zA-Z]{1}[-_a-zA-Z0-9]{5,19}", text):
        text = re.sub("[a-zA-Z]{1}[-_a-zA-Z0-9]{5,19}", "[[customerWeixin]]", text)
    text = text.replace("customerWeixin", "sep1")
    text = re.sub("((?!sep)[a-zé]{3,})", "", text)
    text = text.replace("sep1", "customerWeixin").replace("sep2", "customerMobile")
    if re.search("微信是(:|：|)[\[【]{0,2}([a-zA-Z]{1}[-_a-zA-Z0-9]{5,19})", text) is None and \
            re.search("微信是(:|：|)", text) and re.search("微信是(:|：|)(多少|？|什么)", text) is None:
        text = re.sub("微信是(:|：|)", "微信是 [[customerWeixin]]", text)
    if "价格" in prompt or "优惠活动" in prompt or "价格" in intent or "元" in text or \
            re.search(r"[零一二两三四五六七八九十百千万]{2,}|几[十百千万]", text):
        text_temp = copy.copy(text)
        text = re.sub("([1-9]\d*)", "**", text_temp)
        text = re.sub("([零一二两三四五六七八九十百千万]{2,})|(几[十百千万])", "**", text)
        if contains(items=["**根", "**."], targets=text):  # 如果是几根头发这种情况，就撤回数字替换的逻辑
            text = text_temp

    text = str(text).replace("<|im_start|>", "").replace("<|im_end|>", "").replace("<|endoftext|>", "").replace(
        "</s>", "").replace("<unk>", "").replace(" ", "").replace("&nbsp;", "").replace("u0026", "").replace(
        "<SEP>", "<sep>").replace("\xa0", "").replace("短信", "电话").replace("de", "").replace("\n", "").replace(
        "【百度AI机器人】", "").replace("没有办法做", "比较难").replace("彻底", "").replace("邮箱", "联系方式").replace(
        "qq", "联系方式").replace("QQ", "联系方式")
    return "<sep>".join(remove_none(text.split("<sep>"))) if "<sep>" in text else text


def get_lcs(str1, str2, full=False):
    """
    lcs最长公共子串的匹配，多重匹配策略，当匹配到的字符串长度不小于已匹配串，则同样给出来，full为True则是把所有长度一致的最长字串取出来
    """

    def lcs(s1, s2):
        lstr1, lstr2 = len(s1), len(s2)
        record = [[0 for i in range(lstr2 + 1)] for j in range(lstr1 + 1)]  # 开辟列表空间 多一位是为了处理边界问题
        maxNum = 0  # 最长匹配长度
        p = 0  # 匹配的起始位
        for i in range(lstr1):
            for j in range(lstr2):
                if s1[i] == s2[j]:
                    record[i + 1][j + 1] = record[i][j] + 1  # 相同则累加
                    if record[i + 1][j + 1] > maxNum:
                        maxNum = record[i + 1][j + 1]  # 获取最大匹配长度
                        p = i + 1  # 记录最大匹配长度的终止位置
        return s1[p - maxNum:p], maxNum

    if full:
        lcstr_list, lcstr, max_lcs_len = [], "", len(str2)
        while max_lcs_len > 1:
            lcstr, max_lcs_len = lcs(s1=str1, s2=str2)
            str2 = str2.replace(lcstr, "")
            lcstr_list.append(lcstr)
        return lcstr_list
    else:
        return lcs(s1=str1, s2=str2)[0]


def add_dict(target_dict, key, value):
    if key not in target_dict:
        target_dict[key] = [value] if str(value) != "nan" else []
    else:
        if value not in target_dict[key]:
            target_dict[key].append(value)
    return target_dict


def not_empty(target, key, exist=True):
    """
    判断字典/列表/字符串是否非空，exist=True只要有非空则为True exist=False需要都不为空才为True
    """
    if exist:
        if isinstance(target, dict):
            for k in key:
                if len(target.get(k, [])) > 0:
                    return True
        elif isinstance(target, list):
            for t in target:
                if len(t) > 0:
                    return True
        else:
            if len(target) > 0:
                return True
        return False
    else:
        if isinstance(target, dict):
            for k in key:
                if len(target.get(k, [])) == 0:
                    return False
        elif isinstance(target, list):
            for t in target:
                if len(t) == 0:
                    return False
        else:
            if len(target) == 0:
                return False
        return True
