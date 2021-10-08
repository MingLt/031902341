import sys
from langconv import *
import pandas as pd
import copy
import pypinyin
from Radical import getRadical, is_leftandright

pinandzi = []

file_words = sys.argv[1]
file_org = sys.argv[2]
file_output = sys.argv[3]


class Word:  # 构建敏感词库
    def __init__(self, word):
        self.original_word = word

    def confuse(self):
        """
            构造敏感词的汉字、拼音、首字母、偏旁部首的混合
        """
        sen_thesaurus = []
        word = list(self.original_word)

        for i in range(len(word)):
            c = word[i]
            # 汉字
            if (u'\u4e00' <= c <= u'\u9fa5') or (u'\u3400' <= c <= u'\u4db5'):  # 常见字、繁体字、不常见字
                li = []
                # pinyin
                pin = pypinyin.lazy_pinyin(c)
                gap = ''
                # print(self.pinandzi)
                li.append(c)
                li.append(pin)  # 全拼
                pin = pin[0]
                li.append(pin[0])  # 首字母
                hanzi_part = []
                if is_leftandright(c):
                    hanzi_part = getRadical(c)
                    li.append(hanzi_part)

                word[i] = li  # 一个词添加完毕
                pinandzi.append([c, gap.join(pin), pin[0]] + hanzi_part)

            else:
                pass
        # print(pinandzi)       #word list 包括 pinyin first pinyin radical   [[[]],[[]]]
        for c in word:
            # 开始混合
            # 英文跳过
            if not isinstance(c, list):
                if len(sen_thesaurus) == 0:
                    sen_thesaurus.append([c])
                else:
                    for li in sen_thesaurus:
                        li.append(c)
            # 中文拼音偏旁部首混合
            else:
                if len(sen_thesaurus) == 0:
                    for alist in c:
                        if not isinstance(alist, list):
                            sen_thesaurus.append([alist])
                        else:
                            sen_thesaurus.append(alist)
                else:
                    temp = sen_thesaurus
                    new_confuse_enum = []
                    for alist in c:
                        new_confuse = copy.deepcopy(temp)
                        if not isinstance(alist, list):
                            for cur_confuse in new_confuse:
                                cur_confuse.append(alist)
                        else:
                            for cur_confuse in new_confuse:
                                for x in alist:
                                    cur_confuse.append(x)
                        new_confuse_enum = new_confuse_enum + new_confuse
                    sen_thesaurus = new_confuse_enum

        return sen_thesaurus


class node(object):
    def __init__(self):
        self.next = {}
        self.fail = None
        self.isWord = False
        self.word = ""
        self.confused_words = []


class ac_automation(object):
    """
    AC自动机处理敏感词检测
    """

    def __init__(self):
        self.root = node()
        self.__line_cnt = 0
        self.pinandzi = []
        self.total = 0
        self.result = []
        self.confused_words = []

    # 添加敏感词函数
    def addword(self, word):
        """
        构造树
        """
        temp_root = self.root
        for char in word:
            if char not in temp_root.next:
                temp_root.next[char] = node()
            temp_root = temp_root.next[char]
        temp_root.isWord = True
        temp_root.word = word
        # print(temp_root.word)

    # 失败指针函数
    def make_fail(self):
        temp_que = [self.root]
        while len(temp_que) != 0:
            temp = temp_que.pop(0)
            p = None
            for key, value in temp.next.item():
                if temp == self.root:
                    temp.next[key].fail = self.root
                else:
                    p = temp.fail
                    while p is not None:
                        if key in p.next:
                            temp.next[key].fail = p.fail
                            break
                        p = p.fail
                    if p is None:
                        temp.next[key].fail = self.root
                temp_que.append(temp.next[key])

    def subtongyin(self, acha, content):
        """谐音字处理
        将文本中文字转为拼音
        拼音如果相同替换为敏感词中关键字
        """
        for i in range(len(content)):
            flag = False
            cur_word = content[i]
            curpy = pypinyin.lazy_pinyin(cur_word)
            gap = ''
            curpy = gap.join(curpy)
            for words in pinandzi:  # 获取敏感词对象
                if curpy == words[1] and (cur_word not in words or acha not in words):
                    flag = True  # 判断 该字的拼音 是否在 某个敏感词对象的拼音列表里
                    temp = content[:i] + words[0] + content[i + 1:]  # 如果在进行替换同音字，把同音字换成敏感词中的字
                    content = temp
                    break  # 找到了就不去下一个敏感词里查找了
                if flag:
                    break
        return content

    def search(self, content):
        """查找敏感词函数
            return result
        """
        p = self.root
        result = []
        currentposition = 0
        s = []
        gap = ''
        flag = False
        flag1 = False
        temp_cur = 0
        while currentposition < len(content):
            word1 = content[currentposition]

            if u'\u4e00' <= word1 <= u'\u9fa5':
                word = self.subtongyin(content[currentposition - 1], word1)
            elif 'a' <= word1 <= 'z':
                word = word1
            elif u'\u3400' <= word1 <= u'\u4db5':
                word = Converter('zh-hans').convert(word1)
            elif 'A' <= word1 <= 'Z':
                word = word1.lower()
            else:
                if flag:
                    s.append(word1)
                currentposition += 1
                continue
            while word in p.next is False and p != self.root:
                p = p.fail

            if word in p.next:
                if flag1 is False:
                    flag1 = True
                    temp_cur = currentposition
                p = p.next[word]
                if flag is False:
                    s.append(word1)
                    flag = True
                else:
                    s.append(word1)
            else:
                if flag1 is True:
                    flag1 = False
                    currentposition = temp_cur + 1
                p = self.root
                flag = False
                s = []

            if p.isWord:
                result.append(p.word)
                result.append(self.__line_cnt)
                temp = gap.join(s)
                result.append(temp)
                """
                if flag1 == False and p.fail!=None:
                    p = p.fail
                    temp_result=result
                    flag1=True
                if flag1 == True:
                    if temp_result in result:
                        self.result.append(result)
                        flag1=False
                    else:
                        if p.fail!=None:
                            self.result.append(temp_result)
                            temp_result = result
                            flag1 = True
                            p = p.fail
                """
                self.result.append(result)
                result = []
                s = []
                flag = False
                p = self.root
                self.total += 1
                if flag1 is True:
                    flag1 = False
            currentposition += 1
        return result

    # 加载敏感词库函数
    def parse(self, path):
        """读取敏感词文件
            按行处理，构造敏感词库
            建立敏感词trie
        """
        confused_word_list = []
        with open(path, encoding='utf-8') as f:
            for keyword in f:  # 跳去构建扩大敏感词树
                confuse = Word(str(keyword).strip())
                confused_word_list.append(confuse.confuse())
        gap = ''
        for words in confused_word_list:
            for keyword in words:
                self.addword(gap.join(keyword))
        self.confused_words = confused_word_list

    def read_org(self, path):
        # 读取文本处理文字
        try:  # 异常处理
            with open(path, 'r+', encoding='utf-8') as org:
                lines = org.readlines()
                for line in lines:
                    line = line.strip()
                    self.__line_cnt += 1
                    self.search(line)
        except IOError:
            raise IOError("[filter] Unable to open the file to be detected")

    def out_ans(self, path):
        """
        按格式输出函数
        """
        try:
            with open(path, 'w+', encoding='utf-8') as ans:
                print("Total: {}".format(self.total), file=ans)

                for i in self.result:
                    print('Line{}: <{}> {}'.format(i[1], i[0], i[2]), file=ans)
        except IOError:
            raise IOError("[answer export] Unable to open ans file")


if __name__ == '__main__':
    ah = ac_automation()
    # file_words = 'C:/keep/words.txt'
    ah.parse(file_words)
    # file_org = 'C:/keep/org.txt'
    ah.read_org(file_org)
    # file_output = 'C:/keep/ans.txt'
    ah.out_ans(file_output)
