#!/usr/bin/env python
# _*_coding:utf8_*_
import urllib.parse
import urllib.request
import json
import sys, os
import time
from pprint import pprint
import logging
logging.basicConfig(level=logging.DEBUG)
try:
        import cPickle as pickle
except ImportError:
        import pickle
dir_path=os.path.split(os.path.realpath(__file__))[0]
def segmenter_http(src):
    url = "http://192.168.100.200:20005/segment"
    params = {"model":"standard", "query":src}
    data = bytes(urllib.parse.urlencode(params), encoding='utf8')
    response = urllib.request.urlopen(url, data=data)
    seg_list = json.loads(str(response.read(),'utf-8'))['response']
    # result = ' '.join([''.join(i.split('/')[:-1]) for i in seg_list])
    # result = " ".join([''.join(i[::-1].split('/',1)[1:])[::-1] for i in seg_list])
    result = [''.join(i[::-1].split('/',1)[1:])[::-1] for i in seg_list]
    return result


def segmenter_postag_http(src):
    url = "http://192.168.100.200:20005/segment"
    params = {"model":"standard", "query":src}
    data = bytes(urllib.parse.urlencode(params), encoding='utf8')
    response = urllib.request.urlopen(url, data=data)
    seg_list = json.loads(str(response.read(),'utf-8'))['response']
    # print(seg_list)
    # result = ' '.join([''.join(i.split('/')[:-1]) for i in seg_list])
    # result = " ".join([''.join(i[::-1].split('/',1)[1:])[::-1] for i in seg_list])
    result = [''.join(i[::-1].split('/',1)[1:])[::-1] for i in seg_list]
    postag_result = [''.join(i[::-1].split('/',1)[0])[::-1] for i in seg_list]
    return result, postag_result


def get_seg_pos(src):
    seg_pos_start = []
    seg_pos_end = []
    seg_result = segmenter_http(src)
    start = 0
    end = 0
    for word in seg_result:
        end = end + len(word)
        seg_pos_start.append(start)
        seg_pos_end.append(end)
        start = end
    return (seg_pos_start, seg_pos_end)

def get_postag_pos(src):
    seg_pos_start = []
    seg_pos_end = []
    postag = []
    seg_result, postag_result = segmenter_postag_http(src)
    start = 0
    end = 0
    for word, pos in zip(seg_result, postag_result):
        end = end + len(word)
        seg_pos_start.append(start)
        seg_pos_end.append(end)
        start = end
        postag.append(pos)
    return (seg_pos_start, seg_pos_end, postag)

class Sentence(object):
    '''
    第一次得到句子的时候，
    一次性将分词和词性标记都获取，
    减少分词被调用次数
    '''
    def __init__(self, text):
        self.raw_sent = text
        self.seg_pos_start, self.seg_pos_end, self.postag = get_postag_pos(self.raw_sent)

    def seg_pos(self):
        return (self.seg_pos_start, self.seg_pos_end)

    def postag_pos(self):
        return (self.seg_pos_start, self.seg_pos_end, self.postag)


def check_pos(used_pos, pos):
    '''
    used_pos : 已经被占用的位置
    pos: 查询是否冲突的位置
    return : 更新的used_pos, success
    '''

    success = True
    if pos in used_pos:
        success = False
        return used_pos, success
    for c_pos in used_pos:
        if c_pos[0] < pos[0] < c_pos[1]:
            success = False
            break
        if c_pos[0] <= pos[1] - 1 < c_pos[1] - 1:
            success = False
            break
    if success:
        new_used_pos = []
        for c_pos in used_pos:
            if (pos[0] <= c_pos[0] < pos[1]) and (pos[0] <= c_pos[1] <= pos[1]):
                continue
            else:
                new_used_pos.append(c_pos)
        new_used_pos.append(pos)
        return new_used_pos, success
    else:
        return used_pos, success

def check_seg_pos(seg_pos, pos):
    '''
    检查一个实体的pos是否与分词的位置有冲突
    '''
    return (pos[0] in seg_pos[0]) and (pos[1] in seg_pos[1])

def build_ending_dic(ending_file):
    end_dic = {}
    with open(ending_file) as file1:
        for line in file1:
            _key = line.strip()
            end_dic[_key]=ending_file
    result = end_dic
    
    return  result
    
def filtered_process(input_dic, *ending_dics):
    result = {}
    for line_key in input_dic:
        i = 0
        for end_dic in ending_dics:
            i+=1
            if input_dic[line_key] in end_dic:
                result[line_key] = str(i)
                break
    return result

def read_input(input_file):
    serialize_dir = dir_path+"/tmp"
    input_serialize = serialize_dir+"/input.pickle"
    info_file = serialize_dir+"/info.pickle"
    input_dic = {}
    if not os.path.isdir(serialize_dir):
        logging.info("创建文件夹%s" %serialize_dir)
        os.makedirs(serialize_dir)
    try:
       with open(input_serialize,'rb') as _file_1:
           input_dic = pickle.load(_file_1)
       logging.info("序列化文件读取完毕")
    except Exception as e:
        logging.info(e)
        logging.info("开始读取数据库并生成序列化文件.....")
        with open(input_file) as file1:
            for line in file1:
                res =segmenter_http(line.strip())
                try:
                    input_dic[line.strip()] = res[-1]
                except:
                    print(line)
        with open(input_serialize,'wb') as _file_3:
            pickle.dump(input_dic, _file_3)
        with open(info_file,'w') as _file_3:
            _file_3.write(time.ctime())
        logging.info("序列化文件已生成")
    return input_dic




if __name__ == "__main__":
    brand = build_ending_dic('./pr_brand.end.2')
    hotel = build_ending_dic('./hotel.end')
    restrant = build_ending_dic('./restrant.end')
    input_dic = read_input(sys.argv[1])
    out = filtered_process(input_dic,brand,hotel,restrant)
    with open(sys.argv[1]+'.try','w') as file2:
        for words,_type in sorted(out.items(),key = lambda x:x[1],reverse = True):
            print(_type,words,file=file2)


