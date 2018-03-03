# coding=utf-8
import requests
from bs4 import BeautifulSoup
import re
from CourseInfo import CourseInfo
import pandas as pd


class PointCheck(object):
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.headers = self.get_header()
        self.req = requests.Session()
        self.course_type = ''
        self.ci = CourseInfo()
        self.ci2 = CourseInfo()

    def get_header(self):
        return {
            'Host': 'zhjw.scu.edu.cn',
            'Connection': 'keep - alive',
            'Content-Length': '27',
            'Cache - Control': 'max-age=0',
            'Origin': 'http://zhjw.scu.edu.cn',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36',
            'Referer': 'http://202.115.47.141/loginAction.do',
        }

    def login(self):
        url = 'http://202.115.47.141/loginAction.do'
        res = self.req.post(url, data={'zjh': self.username, 'mm': self.password}, headers=self.headers)
        content = res.content.decode('GBK')
        if res.status_code == 200 and content.find('你输入的证件号不存在') == -1:
            print('登陆成功')
        else:
            print('登陆失败')
            print('你输入的证件号不存在')
            exit(1)

    def get_program_course(self):
        url = 'http://zhjw.scu.edu.cn/gradeLnAllAction.do?type=ln&oper=lnfaqk&flag=zx'
        content = self.req.get(url=url, headers=self.headers).content.decode('GBK')
        self.parse_info(content)

    def get_all_course(self):
        self.get_id()
        url = 'http://zhjw.scu.edu.cn/gradeLnAllAction.do?type=ln&oper=fainfo&fajhh=' + str(self.id)
        content = self.req.get(url=url, headers=self.headers).content.decode('GBK')
        soup = BeautifulSoup(content, 'html5lib')
        class_list = soup.find_all('tr')
        for i in range(6, len(class_list) - 9):
            text = class_list[i].text.replace('\n', '').replace('\t', '')
            text = re.subn(re.compile('[  ]+'), ':', text)
            info = text[0].split(':')
            self.ci2.name = info[3]
            self.ci2.code = info[1]
            self.ci2.point = info[-5]
            self.ci2.type = info[-4]
            self.ci2.push_data2()

        self.save_all()

    def get_id(self):
        pattern = 'gradeLnAllAction.do\?type\=ln\&oper=fainfo\&fajhh=([0-9]{4})'
        url = 'http://202.115.47.141/gradeLnAllAction.do?type=ln&oper=fa'
        content = self.req.get(url=url, headers=self.headers).content.decode('GBK')
        id = re.findall(re.compile(pattern=pattern), content)[0]
        print('id', id)
        self.id = id

    def parse_info(self, info):
        course_list = re.findall(re.compile('tree.add(.*)'), info)
        course_list = list(map(lambda x: x.replace('"', ''), course_list))
        for course in course_list:
            try:
                course_split = course.strip().split(',')
                # print(course_split)
                # -1 表示课程类型
                if course_split[1] == '-1':
                    course_type = course_split[2].replace('"', '').replace('\'', '')
                    if course_type.find('公共课') != -1 or course_type.find('中华文化') != -1:
                        self.ci.base_type = '通识课'
                    elif course_type.find('专业基础课') != -1 or course_type.find('专业课') != -1 or course_type.find(
                            '实践环节') != -1:
                        self.ci.base_type = '专业课'
                if course_split[2].find('](') != -1:
                    # 获取课程号
                    self.ci.code = re.findall(re.compile('([0-9]{9})'), course_split[2])[0]
                    self.ci.name = re.findall(re.compile('](.*)\['), course_split[2])[0]
                    self.ci.point = re.findall(re.compile('\[[0-9]\]'), course_split[2])[0][1:2]
                    self.ci.type = re.findall(re.compile('.修'), course_split[2])[0]
                    # print(self.ci.code, self.ci.name)
                    self.ci.push_data()
            except BaseException as e:
                print(e)
                pass
        self.ci.data_array.sort(key=lambda x: x[0])
        self.save_to_excel()

    def save_to_excel(self):
        data = pd.DataFrame(self.ci.data_array)
        pro_course = data.loc[data[0] == '专业课'].sort_values(by=2)
        other_course = data.loc[data[0] == '通识课'].sort_values(by=1)
        data = pd.concat([pro_course, other_course], axis=0)
        data.to_excel('培养方案中已完成课程.xlsx', header=False, index=False)
        print('根据方案统计课程完成')

    def save_all(self):
        data = pd.DataFrame(self.ci2.all_course).sort_values(by=0)
        data.to_excel('所有课程.xlsx', header=False, index=False)
        print('保存所有课程完成')


if __name__ == '__main__':
    # print('学号:')
    # username = input()
    # print('密码:')
    # password = input()
    data = ''
    data = data.split('=')
    username = data[0]
    password = data[1]
    check = PointCheck(username, password)
    check.login()
    check.get_all_course()
    # 重新登陆
    print('重新登陆，获取培养方案中已完成课程')
    check = PointCheck(username, password)
    check.login()
    check.get_program_course()
