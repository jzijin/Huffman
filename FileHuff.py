# -*- coding: utf-8 -*-
import os
import six
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from HuffmanUIfile import Ui_Form
import time


class LeafNode(object):
    """
    叶子节点类 初始化 叶子的值和权重
    """

    def __init__(self, value, freq):
        self.value = value
        self.freq = freq

    def is_leaf(self):
        return True

    def get_value(self):
        return self.value

    def get_freq(self):
        return self.freq


class IntermediateNode(object):
    """
    中间节点类
    """

    def __init__(self, left_child=None, right_child=None):
        """
        初始化 中间节点的权重 和左右子树
        """
        self.freq = left_child.get_freq() + right_child.get_freq()
        self.left_child = left_child
        self.right_child = right_child

    def is_leaf(self):
        return False

    def get_left_child(self):
        return self.left_child

    def get_right_child(self):
        return self.right_child

    def get_freq(self):
        return self.freq


class Haffuman(object):
    """
    Haffuman树类
    """

    def __init__(self, flag, value, freq, left_tree=None, right_tree=None):
        """
        flag==0 创建只有叶子节点的haffuman树 在根据这些haffuman树构建整棵树
        """
        if flag == 0:
            self.root = LeafNode(value, freq)
        else:
            self.root = IntermediateNode(left_tree.get_root(), right_tree.get_root())

    def get_root(self):
        # 返回根节点 
        return self.root

    def is_leaf(self):
        # 判断是否是树叶
        return False

    def get_freq(self):
        # 返回根节点的权重
        return self.root.get_freq()

    def encode_haffuman_tree(self, root, code, char_freq):
        """
        给 哈弗曼树的根节点（root) 未编码的hafuman频率数组 
        return 编码完的哈弗曼频率数组
        """
        if root.is_leaf():
            char_freq[root.get_value()] = code
            # print("the char '%c' and its freqency is %d the code is %s"%(chr(root.get_value()),root.get_freq(), code))
            return None
        else:
            self.encode_haffuman_tree(root.get_left_child(), code + '0', char_freq)
            self.encode_haffuman_tree(root.get_right_child(), code + '1', char_freq)


class WorkThread(QThread):
    """
    线程类
    """
    trigger = pyqtSignal(str, float)

    def __init__(self, flag, input_filename, output_filename, parent=None):
        super(WorkThread, self).__init__(parent)
        self.flag = flag
        self.input_filename = input_filename
        self.output_filename = output_filename

    def run(self):
        if self.flag == 0:
            last_time = time.time()
            MyHaffuman_compress = Work(self.input_filename, self.output_filename)
            reply_message = MyHaffuman_compress.haffuman_compress()
            self.trigger.emit(reply_message, last_time)
        else:
            last_time = time.time()
            MyHaffuman_compress = Work(self.input_filename, self.output_filename)
            reply_message = MyHaffuman_compress.haffuman_decompress()
            self.trigger.emit(reply_message, last_time)


class Work(object):
    """
    干活的类
    """

    def __init__(self, input_file, output_file):
        self.input_file = input_file
        self.output_file = output_file

    def build_haffuman_tree(self, haffuman_dict):
        """
        给一个字典（键值对） 转化为哈弗曼树
        :param haffuman_dict:
        :return: 哈弗曼树
        """
        tmp_list = []
        for x in haffuman_dict.keys():
            tmp = Haffuman(0, x, haffuman_dict[x])
            tmp_list.append(tmp)

        while len(tmp_list) > 1:
            tmp_list.sort(key=lambda x: x.get_freq())
            # 取出最小的两个
            tmp1 = tmp_list[0]
            tmp2 = tmp_list[1]
            tmp_list = tmp_list[2:]

            new_tree = Haffuman(1, 0, 0, tmp1, tmp2)
            # 追加在列表末尾
            tmp_list.append(new_tree)

        return tmp_list[0]

    def write_an_int2byte(self, num_int, output):
        """
        给一个 int类型数， 给一个文件流 把int 型数据转化成bytes 写入文件
        :param num_int:
        :param output:
        :return:
        """
        tmp = bin(num_int)[2:]
        tmp = (32 - len(tmp)) * '0' + tmp
        for i in range(0, 4):
            code_tmp = int(tmp[i * 8:i * 8 + 8], 2)
            output.write(six.int2byte(code_tmp))

    def get_freq_dict(self, file_data, file_size):
        """
        给文件数据 文件大小 返回频率字典
        :param file_data:
        :param file_size:
        :return: char_freq
        """
        char_freq = {}
        for i in range(file_size):
            char_value = file_data[i]
            if char_value in char_freq.keys():
                char_freq[char_value] = char_freq[char_value] + 1
            else:
                char_freq[char_value] = 1

        return char_freq

    def reverse_dict(self, char_freq):
        """
        翻转字典： 键==》值 变成 值==》键
        :param char_freq:
        :return: reverse_char_freq
        """
        reverse_char_freq = {}
        for key in char_freq.keys():
            new_key = char_freq[key]
            reverse_char_freq[new_key] = key

        return reverse_char_freq

    def get_encode_char_freq(self, char_freq):
        """
        得到编码哈弗曼字典
        :param char_freq:
        :return: 编码后的字典
        """
        # 得到哈弗曼树
        haffuman_tree = self.build_haffuman_tree(char_freq)
        # 编码哈弗曼树 编码完后  char_freq 已经编码完了
        haffuman_tree.encode_haffuman_tree(haffuman_tree.get_root(), '', char_freq)

        # 如果文件只有一种字符的话 进行修正 
        # 其实只有一个字符还可以继续优化 例如直接写入 （字符and size）这样更加节省空间
        if len(char_freq) == 1:
            for i in char_freq.keys():
                char_freq[i] = '0'

        return char_freq

    def haffuman_compress(self):

        f = open(self.input_file, 'rb')

        file_data = f.read()
        f.close()
        file_size = os.path.getsize(self.input_file)
        output = open(self.output_file, 'wb')
        if file_size == 0:
            # 如果文件没有内容 写入文件长度（0） 退出
            self.write_an_int2byte(file_size, output)
            return "压缩完毕"

        # 得到频率字典
        char_freq = self.get_freq_dict(file_data, file_size)
        print(char_freq)

        # 开始写入信息
        # 写入文件总字节数：
        self.write_an_int2byte(file_size, output)

        # 写入字符的叶子节点总个数
        length = len(char_freq.keys())
        self.write_an_int2byte(length, output)

        # 开始写入 频率字典 解压缩用于重构hafuman树
        for i in char_freq.keys():
            output.write(six.int2byte(i))
            self.write_an_int2byte(char_freq[i], output)

        # 得到编码的字符频率字典
        char_freq = self.get_encode_char_freq(char_freq)
        # print(char_freq)

        # 开始写入文件数据
        code = ''
        for x in range(file_size):
            key = file_data[x]
            # 开始编码
            code = code + char_freq[key]
            # 如果长度大于8位 一个字节一个字节处理
            while len(code) > 8:
                out = int(code[0:8], 2)
                code = code[8:]
                output.write(six.int2byte(out))

        # 写入最后的八位
        code = code + (8 - len(code)) * '0'
        out = int(code, 2)
        output.write(six.int2byte(out))

        # 关闭文件
        output.close()
        return "压缩完毕"

    def haffuman_decompress(self):
        f = open(self.input_file, 'rb')
        output = open(self.output_file, 'wb')
        file_data = f.read()
        file_size = os.path.getsize(self.input_file)
        f.close()

        # 得到文件的字节数
        total_byte_code = ''
        for i in range(0, 4):
            tmp = bin(file_data[i])[2:]
            total_byte_code = total_byte_code + (8 - len(tmp)) * '0' + tmp
        total_byte = int(total_byte_code, 2)

        if total_byte == 0:
            # 如果压缩的是空文件
            output.close()
            return "解压完毕"

        # 得到原始频率字典键的总数
        the_code = ''
        for i in range(4, 8):
            tmp = bin(file_data[i])[2:]
            the_code = the_code + (8 - len(tmp)) * '0' + tmp
        leaf_nodes = int(the_code, 2)

        # 得到 字符频率字典
        char_freq = {}
        for i in range(leaf_nodes):
            key = file_data[8 + i * 5 + 0]
            freq_code = ''
            for j in range(1, 5):
                tmp = bin(file_data[8 + i * 5 + j])[2:]
                freq_code = freq_code + (8 - len(tmp)) * '0' + tmp
            the_value = int(freq_code, 2)
            char_freq[key] = the_value

        # 得到编码字符频率字典
        char_freq = self.get_encode_char_freq(char_freq)

        # 得到翻转后编码频率数组
        reverse_char_freq = self.reverse_dict(char_freq)

        # 开始根据编码解压缩
        # 把开头字符总数 频率字典的长度去除
        code = ''
        tmp_code = ''
        tmp_byte = 0  # 存放已经翻译好的字节数
        reverse_char_freq_keys = reverse_char_freq.keys()
        for x in range(leaf_nodes * 5 + 8, file_size):

            # 一个字节一个字节读取信息
            one_char = file_data[x]
            str_code = bin(one_char)[2:]
            str_code = (8 - len(str_code)) * '0' + str_code
            code = code + str_code

            while True:
                # 读到文件字节数和原文件字节数相等 解压完毕了
                if tmp_byte == total_byte:
                    break
                # 一个字符一个字符读取
                tmp_code = tmp_code + code[0]
                code = code[1:]

                # 得到临时字符串如果在翻转后的编码频率的键值中 那么把键对应的值写入
                if tmp_code in reverse_char_freq_keys:
                    tmp_byte = tmp_byte + 1
                    char_value = reverse_char_freq[tmp_code]
                    output.write(six.int2byte(char_value))
                    tmp_code = ''

                if len(code) == 0:
                    # code 长度为0 说明读取完毕了 跳出继续读取 补充code
                    break
        # 关闭文件
        output.close()
        return "解压完毕！"


class HaffumanForm(QWidget, Ui_Form):
    # TODO: 加个进度条？？？
    def __init__(self):
        super(HaffumanForm, self).__init__()
        self.input_filename = ''
        self.output_filename = ''
        self.setupUi(self)

        self.pushButton_compress.setEnabled(False)
        self.pushButton_decompress.setEnabled(False)
        self.lineEdit_open_path.setEnabled(False)
        self.lineEdit.setEnabled(False)
        self.pushButton_open_path.clicked.connect(self.compress_get_path)
        self.pushButton_compress.clicked.connect(self.compress)
        self.pushButton_decompress_path_.clicked.connect(self.decompress_get_path)
        self.pushButton_decompress.clicked.connect(self.depress)

    def compress_get_path(self):
        """
        压缩时获取文件路径
        :return:
        """
        file_name = QFileDialog.getOpenFileName(self, "选择一个文件", "/home/")
        # 得到元组
        if file_name[0] == '':
            QMessageBox.information(self, "警告", "请选择文件", QMessageBox.Yes)
        else:
            self.input_filename = file_name[0]

            self.lineEdit_open_path.setText(self.input_filename)

            self.pushButton_compress.setEnabled(True)

    def decompress_get_path(self):
        """
        解压时 获取文件路径
        :return:
        """
        file_name = QFileDialog.getOpenFileName(self, "选择一个文件", "/home/", "All Files(*.filebak)")
        # 得到元组
        if file_name[0] == '':
            QMessageBox.information(self, "警告", "请选择文件", QMessageBox.Yes)
        else:
            self.input_filename = file_name[0]
            self.lineEdit.setText(self.input_filename)
            self.pushButton_decompress.setEnabled(True)

    def stop_thread(self, reply, last_time):
        """
        线程结束 打印线程结束的提示信息 退出线程
        :param reply:
        :return:
        """
        # 计算耗时
        now_time = time.time()
        cost_time = now_time - last_time

        self.textBrowser_message.append(reply)
        self.textBrowser_message.append('耗时： ' + str(cost_time) + 's')
        self.work_thread.quit()

    def compress(self):
        """
        压缩文件函数
        :return:
        """
        # 得到文件
        if self.input_filename == '':
            QMessageBox.information(self, "警告", "请选择文件", QMessageBox.Yes)
            return

        # 显示提示信息
        self.textBrowser_message.append("正在压缩请稍后......")
        self.pushButton_compress.setEnabled(False)

        # 文件操作得到文件名
        dir_name = os.path.dirname(self.input_filename)
        self.output_filename = os.path.basename(self.input_filename) + '.filebak'
        self.output_filename = dir_name + '/' + self.output_filename

        # 开线程 防止UI卡顿
        self.work_thread = WorkThread(0, self.input_filename, self.output_filename)
        self.work_thread.trigger.connect(self.stop_thread)
        self.work_thread.start()

        self.lineEdit_open_path.clear()

    def depress(self):
        #  选择文件
        if self.input_filename == '':
            QMessageBox.information(self, "警告", "请选择文件", QMessageBox.Yes)
            return
        # 显示提示信息
        self.textBrowser_message.setText("正在解压，请稍后......")
        self.pushButton_decompress.setEnabled(False)

        # 文件操作 最终得到文件名
        dir_name = os.path.dirname(self.input_filename)

        self.output_filename = os.path.basename(self.input_filename)
        self.output_filename = os.path.splitext(self.output_filename)[0]
        self.output_filename = dir_name + '/' + self.output_filename

        # 检测解压文件是否已经存在
        if os.path.exists(self.output_filename):
            warning_message = self.output_filename + "已经存在 是否覆盖？？？"
            reply = QMessageBox.information(self, "警告", warning_message, QMessageBox.Yes, QMessageBox.No)

            if reply != QMessageBox.Yes:
                # print("yest")
                self.textBrowser_message.append("对不起 我未能获得覆盖权限")
                return

        # UI 与逻辑分开 防止UI 卡顿 开辟线程
        self.work_thread = WorkThread(1, self.input_filename, self.output_filename)
        self.work_thread.trigger.connect(self.stop_thread)
        self.work_thread.start()

        # 清空lineedit的文字
        self.lineEdit.clear()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    My_win = HaffumanForm()
    My_win.show()
    sys.exit(app.exec_())
