import pandas as pd
import re
import ast
from collections import Counter
from load_data import load_data_set

###########################
# 全局变量
# 加载品牌列表

# Fixme: 这里最好使用一个配置文件，不用全局变量
brands_list = []
file_path = './data/coumters_brands_list.txt'
with open(file_path) as f:
    line = f.readline().strip()
    while line:
        brands_list.append(line)
        line = f.readline().strip()

########################################
"""
    一些数据预处理函数
"""
def sub_func_1(x):
    """
    这个函数为了解决
        "品牌： 微星（MSI）" # 有冒号也有空格
        "品牌：微星（MSI）" # 只有冒号,没有空格
        的情况.
    (获得正确的品牌名)
    :param x:
    :return:
    """
    words = re.split(r'：| ', x)
    if len(words[1]) < 1:
        return words[2]
    else:
        return words[1]


def sub_func_2(x, tag=1):
    """
    这个函数是将brand中的，如：、戴尔(dell)、戴尔（DELL）等，拆成中文名和英文名的列表【戴尔、dell、DELL]
    :param x: 如：戴尔（dell）
    :param tag: 1: 如果同时存在中英文，返回中文；2：果同时存在中英文，返回英文；
    :return:
    """
    # 判断brand中是否有括号（分为中文括号，英文括号等）


def get_all_comput_brand():
    """
    将所有的品牌及其产品，弄成一个dataframe
    :return:
    """
    product_data = load_data_set('jingdong')

    data_1 = product_data[0]
    data_1['brand'] = data_1['attrs'].apply(lambda x: sub_func_1(x.split('\n')[0]))  #
    result = data_1[['brand', 'product_name']]
    sum = len(data_1)
    print(sum)
    for i in range(len(product_data)):
        if i == 0:
            continue
        data = product_data[i]
        print(len(data))
        sum += len(data)
        data['brand'] = data['attrs'].apply(lambda x: sub_func_1(x.split('\n')[0]))  #

        result = result.append(data[['brand', 'product_name']])
    result.to_csv('./data/brand_product_list.csv', index=False, encoding='utf-8')


def get_computer_brands_list():
    """
    获得整个电脑产品的品牌列表
    :return:
    """
    data = pd.read_csv('./data/brand_product_list.csv')
    brands_set = set(data['brand'].values)
    print(len(brands_set))
    print(brands_set)
    brands_list = []
    for brand in brands_set:
        if '（' in brand or '(' in brand:
            print(brand)
            # 存在中英两文
            brand_split = re.split(r'[（()）]', brand)
            brands_list.append(brand_split[0]) # 中文
            brands_list.append(brand_split[1]) # 英文
        else:
            # 只有一个（中文或英文）
            brands_list.append(brand)
    computer_brands = set(brands_list)
    print(len(computer_brands))
    print(computer_brands)
    file_path_save = './data/coumters_brands_list.txt'
    with open(file_path_save, 'w', encoding='utf-8') as f:
        for brand in computer_brands:
            f.write(brand)
            f.write('\n')


########################################
def mark_tag(tag, start, end, flag):
    """
    :param tag:
    :param start:
    :param end:
    :param flag:
    :return:
    """



def get_tags(data):
    """
    各种tag：品牌（brand）、处理器（processor）、内存（memory）、磁盘（disk）、显卡（GPU）
    :param data: 论坛数据，分为标题、内容、标签和文本。（内容和文本重复了）
    :return: data：与输入的data格式相同，但是tag列中，更新了相关的标签BIO
    """
    # 初始化tag，text：title + content
    data['text'] = data.apply(lambda x: x['title'] + ' ' + x['content'], axis=1)
    data['tag'] = data['text'].apply(lambda x: ['O']*len(x))

    # 获得brand的tag
    data['tag'] = data[['tag', 'text']].apply(lambda x: get_brand(x), axis=1)

    # 获得内存
    data['tag'] = data[['tag', 'text']].apply(lambda x: get_memory(x), axis=1)

    # 获得硬盘
    data['tag'] = data[['tag', 'text']].apply(lambda x: get_disk(x), axis=1)

    # 获得价格
    data['tag'] = data[['tag', 'text']].apply(lambda x: get_price(x), axis=1)

    # 获得CPU
    # data['tag'] = data[['tag', 'text']].apply(lambda x: get_cpu(x), axis=1)



    # # 获得CPU
    # data['tag'] = data[['tag', 'text']].apply(lambda x: get_GPU(x), axis=1)

    return data



def get_brand(data):
    """
    获得文本中品牌的标签：brand
    :param data: ['content':xxx, 'tag':XXX]
    :return: 新的tags
    """
    text = data['text']
    tag = data['tag']

    # 判断text中是否出现任意一个品牌
    for brand in brands_list:
        brand = brand.lower() # 变成全部小写
        text = text.lower() # 变成全部小写
        find_index = 0 # 表示text.find 的下标
        start_index = text.find(brand, find_index)
        while start_index != -1: # 发现到了brand
            end_index = start_index + len(brand) - 1 # 末尾下标
            # Fixme：这里没有考虑到与tag中的其他标签冲突的情况。
            if is_brand_chinese(brand):  # Fixme：这里没有考虑中文brand的一些情况：如“一台电脑”，"台电"是一个牌子
                tag[start_index] = 'B-Brand'
                tag[end_index] = 'E-Brand'
                for i in range(start_index + 1, end_index):
                    tag[i] = 'I-Brand'
            else:  # 纯英文
                ch_before = text[start_index - 1]  # 前一个字符
                ch_afer = text[end_index + 1]  # 后一个字符
                if ord(ch_before) in range(97, 123) or ord(ch_afer) in range(97, 123): # 跳过这一个
                    find_index = start_index + 1
                    start_index = text.find(brand, find_index)
                    continue
                else:  # 当前的brand是单独一个完整的英文单词
                    tag[start_index] = 'B-Brand'
                    tag[end_index] = 'E-Brand'
                    for i in range(start_index + 1, end_index):
                        tag[i] = 'I-Brand'
            find_index = start_index + 1    # 继续寻找后文是否存在另外的brand
            start_index = text.find(brand, find_index)
            print(brand)
    return tag


def is_brand_chinese(brand_str):
    """
    判断一个brand是否是中文名，还是英文名。
    注意：这里的前提是，brand name中，不是中文字符就是英文字符
    :param brand_str: 品牌名
    :return:
    """
    for ch in brand_str:
        num = ord(ch)
        if num < 65 or num > 123:  # 存在非英文字符
            return True  # 只要存在一个中文，就返回
    return False


def get_memory(data):
    """
    获得文本描写内存的标签：brand
    :param data: ['content':xxx, 'tag':XXX]
    :return: 新的tags
    """
    text = data['text']
    tag = data['tag']

    pathern = re.compile('内存.{,4}\d+[Gg]|\d+[Gg].{,4}内存')  # Fixme:小数点没有考虑；范围性(2~4G)没有考虑

    all_match_iter = pathern.finditer(text)  # 返回一个迭代器

    for match in all_match_iter:
        if match == None:
            break
        # 要在匹配得到的大文本中，获取确切的词的位置
        pathern_2 = re.compile('\d+[Gg]')
        second_match = re.search(pathern_2, match.group())  # 这里不可能匹配不成功
        match_start = match.start() + second_match.start()
        match_end = match.start() + second_match.end()
        tag[match_start] = 'B-Memory'
        tag[match_end - 1] = 'E-Memory'
        for i in range(match_start + 1, match_end - 1): # 注意这里的match_end 小彪
            tag[i] = 'I-Memory'
    ## 使用re中的finditer函数来重构下面代码
    # end_index_record = 0  # 记录字符串截断的位置83+998799842+7
    # temp = text
    # while len(temp) > 0 :
    #     first_match = re.search(pathern, temp)
    #     if first_match == None: # 没有能匹配的
    #         break
    #     first_match_text = first_match.group() # 匹配得到的文本
    #     first_begin = first_match.start()
    #     first_end = first_match.end()
    #     # 要在匹配得到的大文本中，获取确切的词的位置
    #     pathern_2 = re.compile('\d+[Gg]')
    #     second_match = re.search(pathern_2, first_match_text) # 这里不可能匹配不成功
    #     match_start = end_index_record + first_begin + second_match.start()
    #     match_end = end_index_record + first_begin + second_match.end()
    #     # Fixme:这里可以抽象成一个函数
    #     tag[match_start] = 'B-Memory'
    #     tag[match_end - 1] = 'E-Memory' # 注意这里的下标要减一
    #     for i in range(match_start + 1, match_end - 1): # 注意这里的match_end 小彪
    #         tag[i] = 'I-Memory'
    #     end_index_record += match_end  # 记录已经成功匹配的位置
    #     temp = text[end_index_record:len(text)] # 截取下一段继续寻找
    #     print(first_match_text)
    #     print(second_match.group())
    return tag


def get_disk(data):
    """

    :param data: ['content':xxx, 'tag':XXX]
    :return: 新的tags
    """
    text = data['text']
    tag = data['tag']

    pathern = re.compile('硬盘.{,4}\d+[GgTt]|\d+[GgTt].{,4}硬盘')  # Fixme:小数点没有考虑；范围性(2~4G)没有考虑

    all_match_iter = pathern.finditer(text)  # 返回一个迭代器

    for match in all_match_iter:
        if match == None:
            break
        # 要在匹配得到的大文本中，获取确切的词的位置
        pathern_2 = re.compile('\d+[GgTt]')
        second_match = re.search(pathern_2, match.group())  # 这里不可能匹配不成功
        match_start = match.start() + second_match.start()
        match_end = match.start() + second_match.end()
        tag[match_start] = 'B-Disk'
        tag[match_end - 1] = 'E-Disk'
        for i in range(match_start + 1, match_end - 1):  # 注意这里的match_end 小彪
            tag[i] = 'I-Disk'

        # end_index_record = 0  # 记录字符串截断的位置
        # temp = text
        # while len(temp) > 0 :
        # first_match = re.search(pathern, temp)
        # if first_match == None: # 没有能匹配的
        #     break
        # first_match_text = first_match.group() # 匹配得到的文本
        # first_begin = first_match.start()
        # first_end = first_match.end()
        # # 要在匹配得到的大文本中，获取确切的词的位置
        # pathern_2 = re.compile('\d+[GgTt]')
        # second_match = re.search(pathern_2, first_match_text) # 这里不可能匹配不成功
        # match_start = end_index_record + first_begin + second_match.start()
        # match_end = end_index_record + first_begin + second_match.end()
        # # Fixme:这里可以抽象成一个函数
        # tag[match_start] = 'B-Disk'
        # tag[match_end - 1] = 'E-Disk' # 注意这里的下标要减一
        # for i in range(match_start + 1, match_end - 1): # 注意这里的match_end 小彪
        #     tag[i] = 'I-Disk'
        # end_index_record += match_end  # 记录已经成功匹配的位置
        # temp = text[end_index_record:len(text)] # 截取下一段继续寻找
        # print(first_match_text)
        # print(second_match.group())
    return tag


def get_price(data):
    tag = data['tag']
    n_pattern = re.compile('\d+')
    # medium price
    m_pattern = re.compile('\d{4,5}.{,1}(?=左右|上下)')
    m_match_iter = m_pattern.finditer(data['text'])
    for m_match in m_match_iter:
        start_index = m_match.start(0)
        end_index = re.search(n_pattern, data['text'][start_index:]).end(0) + start_index
        tag[start_index] = 'B-Price_m'
        tag[end_index - 1] = 'E-Price_m'
        tag[start_index+1:end_index-1] = ['I-Price_m'] * (end_index-start_index-2)
        print(data['text'][start_index:end_index])
    # upper bound price
    u_pattern = re.compile('价.{,4}\d{4,}[^上]{,2}(?=[内下])|(?<=\d{4}[到\-~～`])\d{4,}')
    u_match_iter = u_pattern.finditer(data['text'])
    for u_match in u_match_iter:
        start_index = u_match.start(0)
        start_index = start_index + re.search(n_pattern, data['text'][start_index:]).start(0)
        end_index = re.search(n_pattern, data['text'][start_index:]).end(0) + start_index
        tag[start_index] = 'B-Price_u'
        tag[end_index - 1] = 'E-Price_u'
        tag[start_index+1:end_index-1] = ['I-Price_u'] * (end_index-start_index-2)
        print(data['text'][start_index:end_index])
    # lower bound price
    l_pattern = re.compile('\d{4,}(?=[到\-~～`]\d{4,})')
    l_match_iter = l_pattern.finditer(data['text'])
    for l_match in l_match_iter:
        start_index = l_match.start(0)
        end_index = l_match.end(0)
        tag[start_index] = 'B-Price_l'
        tag[end_index - 1] = 'E-Price_l'
        tag[start_index+1:end_index-1] = ['I-Price_l'] * (len(l_match[0])-2)
        print(data['text'][start_index:end_index])
    return tag

def get_cpu(data):
    tag = data['tag']
    # cpu
    cpu_pattern = re.compile('(?<=\D)(4|8|16|32|64)(?=G|g)')
    cpu_iter = cpu_pattern.finditer(data['text'])
    for cpu_match in cpu_iter:
        start_index = cpu_match.start(0)
        end_index = cpu_match.end(0)
        if end_index - start_index == 1:
            print(data['text'][start_index])
            tag[start_index] = 'S-Cpu'
        else:
            tag[start_index] = 'B-Cpu'
            tag[end_index - 1] = 'E-Cpu'
            print(data['text'][start_index:end_index])
    return tag


def get_GPU(data):
    """
    :param data: ['content':xxx, 'tag':XXX]
    :return: 新的tags
    """



if __name__ == '__main__':
    ############
    # 数据预处理部分
    # get_all_comput_brand()
    # get_computer_brands_list()

    ###########
    # 获得各种tag
    forum_data = pd.read_csv('./京东/forum')
    print(forum_data.head())
    print(forum_data.isnull().any())

    result_forum = get_tags(forum_data)

    result_forum.to_csv('./data/forum_tag.csv', index=False, encoding='utf-8')

    ### test
    # test = 'fdf内存够大（16g）fdfd'
    # test2 = '8G 的内存就好了'
    # pathern = re.compile('内存.{,4}\d{1,2}[Gg]\W')  #
    # pathern2= re.compile('{，3}\d[Gg]\W{,3}内存')
    # pathern2 = re.compile('\d{1,2}]')
    # mat = re.search(pathern2, test2)
    # print(mat)
    # # print(mat.group(1))
    # # print(mat.group(2))
    #
    # print(mat.end())
    # print(mat.start(0))