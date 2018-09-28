#!/usr/bin/env python
# _*_coding:utf8_*_
import urllib.parse
import urllib.request
import json
import sys
from pprint import pprint

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

if __name__ == "__main__":
    end_seg_dic = {}
    with open(sys.argv[1]) as file1:
        for line in file1:
            res =segmenter_http(line.strip())
            try:
                end_seg_dic[res[-1]] = end_seg_dic.get(res[-1],0) + 1
            except:
                print(line)
    pprint(end_seg_dic)
    with open(sys.argv[1]+'.end','w') as file2:
        for each in sorted(end_seg_dic.items(),key = lambda x:x[1],reverse = True):
            print(each,file=file2)


