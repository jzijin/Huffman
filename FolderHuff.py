import os
import shutil
import sys
import six
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from HaffumanUIfolder import Ui_Form


class Folder(object):
    """
    文件夹类
    """

    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.file_list = []
        self.folder_list = []


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


class Work(object):

    def __init__(self, input_file, output_file, input_file_stream, output_file_stream=None):
        self.input_file = input_file
        self.output_file = output_file
        self.output_file_stream = output_file_stream
        self.input_file_stream = input_file_stream

    def build_haffuman_tree(self, haffuman_dict):
        """
        给一个字典（键值对） 转化为哈弗曼树
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
        给一个 int类型数， 给一个文件流 一个字节一个字节的写入
        """
        tmp = bin(num_int)[2:]
        tmp = (32 - len(tmp)) * '0' + tmp
        for i in range(0, 4):
            code_tmp = int(tmp[i * 8:i * 8 + 8], 2)
            output.write(six.int2byte(code_tmp))

    def get_freq_dict(self, file_data, file_size):
        """
        给文件数据 文件大小 返回频率字典
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
        """
        reverse_char_freq = {}
        for key in char_freq.keys():
            new_key = char_freq[key]
            reverse_char_freq[new_key] = key

        return reverse_char_freq

    def get_encode_char_freq(self, char_freq):
        """
        得到编码的频率字典
        """
        # 得到哈弗曼树
        haffuman_tree = self.build_haffuman_tree(char_freq)
        # 编码哈弗曼树 编码完后  char_freq 已经编码完了
        haffuman_tree.encode_haffuman_tree(haffuman_tree.get_root(), '', char_freq)

        # 如果文件只有一种字符的话 进行修正
        if len(char_freq) == 1:
            for i in char_freq.keys():
                char_freq[i] = '00000000'

        return char_freq

    @property
    def haffuman_compress(self):

        f = open(self.input_file, 'rb')

        file_data = f.read()
        f.close()
        file_size = os.path.getsize(self.input_file)

        output = self.output_file_stream

        if file_size == 0:
            # 如果文件没有内容 写入文件长度（0） 退出
            self.write_an_int2byte(file_size, output)
            return "压缩完毕"

        # 得到频率字典
        char_freq = self.get_freq_dict(file_data, file_size)

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

        # 算一下应该写入多少次 写入这个次数 解压时才能知道在哪截断
        length_ = 0
        code = ''
        for x in range(file_size):
            key = file_data[x]
            code = code + char_freq[key]
            while len(code) > 8:
                code = code[8:]
                length_ = length_ + 1
        length_ = length_ + 1
        write_an_int2byte(length_, output)

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

        return '压缩完毕'

    def file_decompress(self, start, file_data, file_name):
        output = open(file_name, 'wb')

        # 得到文件的总字节数
        total_byte_code = ''
        for i in range(start, start + 4):
            tmp = bin(file_data[i])[2:]
            total_byte_code = total_byte_code + (8 - len(tmp)) * '0' + tmp
        total_byte = int(total_byte_code, 2)

        if total_byte == 0:
            # 如果文件为空文件 关闭文件 计算并返回结尾位置。
            end = start + 4
            output.close()
            return end

        start = start + 4

        # 得到叶子节点的个数
        the_code = ''
        for i in range(start, start + 4):
            tmp = bin(file_data[i])[2:]
            the_code = the_code + (8 - len(tmp)) * '0' + tmp
        leaf_nodes = int(the_code, 2)

        start = start + 4

        # 得到 字符频率字典
        char_freq = {}
        for i in range(leaf_nodes):
            key = file_data[start + i * 5 + 0]
            freq_code = ''
            for j in range(1, 5):
                tmp = bin(file_data[start + i * 5 + j])[2:]
                freq_code = freq_code + (8 - len(tmp)) * '0' + tmp
            the_value = int(freq_code, 2)
            char_freq[key] = the_value

        start = start + leaf_nodes * 5

        # 得到编码字符频率字典
        char_freq = self.get_encode_char_freq(char_freq)
        # 得到翻转后编码频率数组
        reverse_char_freq = self.reverse_dict(char_freq)
        file_end = get_an_int2byte(start, file_data)

        # 得到文件结束位置
        end = start + 4 + file_end

        # 开始根据编码解压缩
        # 把开头字符总数 频率字典的长度去除
        code = ''
        tmp_code = ''
        tmp_byte = 0  # 存放已经翻译好的字节数
        reverse_char_freq_keys = reverse_char_freq.keys()
        for x in range(start + 4, end):

            # 一个字节一个字节读取信息
            one_char = file_data[x]
            str_code = bin(one_char)[2:]
            str_code = (8 - len(str_code)) * '0' + str_code
            code = code + str_code

            # 只有一个字符的话 有bug 两个字符以上无bug
            while True:
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
        return end


def get_files(path, cla_folder_list=[]):
    """
    给我文件夹路径 我能得到建立 得到文件夹下的文件和 目录 返回Folder类对象的列表
    :param path:
    :param cla_folder_list:
    :return:
    """
    folder = Folder(path)
    cla_folder_list.append(folder)
    files = os.listdir(path)
    # print(files)
    for file in files:
        true_path = path + '/' + file
        if os.path.isfile(true_path):
            folder.file_list.append(true_path)

        elif os.path.isdir(true_path):
            folder.folder_list.append(true_path)
            get_files(true_path, cla_folder_list)


def write_an_int2byte(num_int, output):
    """
    给一个 int类型数， 给一个文件流 一个字节一个字节的写入
    """
    tmp = bin(num_int)[2:]
    tmp = (32 - len(tmp)) * '0' + tmp
    for i in range(0, 4):
        code_tmp = int(tmp[i * 8:i * 8 + 8], 2)
        output.write(six.int2byte(code_tmp))


def get_an_int2byte(start, file_data):
    # 得到原始文件字节总数
    the_code = ''
    for i in range(start, start + 4):
        tmp = bin(file_data[i])[2:]
        the_code = the_code + (8 - len(tmp)) * '0' + tmp
    return int(the_code, 2)


# 写如根path  写文件夹的名称 写入文件个数  写入文件名称  写入文件 写入文件在压缩文件占了多少个字节
def folder_compress(path, folder_path, file_list, output_file_name):
    """
    写入思路就是下面写的 顺序
    :param path:
    :param folder_path:
    :param file_list:
    :param output_file_name:
    :return:
    """

    # 写入 根路径的长度
    output = open(output_file_name, 'wb')
    write_an_int2byte(len(bytes(path, 'utf8')), output)
    # path_byte = struct.pack('i',path)

    # 写入根路径的名称
    output.write(bytes(path, 'utf8'))

    write_an_int2byte(len(folder_path), output)
    write_an_int2byte(len(file_list), output)

    for folder in folder_path:
        # 写入文件夹列表的个数 和名称
        write_an_int2byte(len(bytes(folder, 'utf8')), output)
        output.write(bytes(folder, 'utf8'))

    for file in file_list:
        # 写入文件列表的长度和名称
        write_an_int2byte(len(bytes(file, 'utf8')), output)
        output.write(bytes(file, 'utf8'))

    for file in file_list:
        # haffuman_compress()
        # 写入文件
        tmp = Work(file, output_file_name, '', output)
        # 调用单文件压缩
        tmp.haffuman_compress

    output.close()


def compress(path, output):
    """
    压缩一个文件夹
    :param path: 文件夹的路径
    :param output: 输出的文件名
    :return:
    """
    cla_folder_list = []
    folder_names = []
    # print(path)
    get_files(path, cla_folder_list)
    for i in cla_folder_list:
        if len(i.folder_list) > 0:
            for folder_name in i.folder_list:
                # 得到所有文件夹的名称
                # folder_name = '.' + folder_name[len(path):]
                # print(folder_name)
                folder_names.append(folder_name)

    file_names = []
    for i in cla_folder_list:
        if len(i.file_list) > 0:
            # print(i.file_list)
            for file_name in i.file_list:
                # 这个可以切掉
                # file_name = '.' + file_name[len(path):]
                file_names.append(file_name)

    # print(folder_names, file_names)
    # exit()
    folder_compress(path, folder_names, file_names, output)
    return "压缩完毕"


def get_files_folds(file_data, start, end):
    # 得到文件或文件夹的长度
    file_length = ''
    for k in range(start, end):
        tmp = bin(file_data[k])[2:]
        file_length = file_length + (8 - len(tmp)) * '0' + tmp
    file_length = int(file_length, 2)

    # 得到文件或者文件夹的名字
    file_name = b''
    for j in range(end, end + file_length):
        file_name = file_name + bytes([file_data[j]])
    file_name = file_name.decode('utf8')
    # print(end+file_length)
    return file_name, end + file_length


def decompress(path):
    """
    :param path:
    :return:
    """
    # 得到根路径长度
    length_int = 4
    f = open(path, 'rb')
    file_data = f.read()
    total_byte_code = ''
    for i in range(0, length_int):
        tmp = bin(file_data[i])[2:]
        total_byte_code = total_byte_code + (8 - len(tmp)) * '0' + tmp
    total_byte = int(total_byte_code, 2)
    # print(len(path))
    # print(total_byte)

    # 得到根路径名字
    tmp_name = b''
    for i in range(length_int, length_int + total_byte):
        # tmp_name = ''
        tmp_name = tmp_name + bytes([file_data[i]])

    # print(tmp_name.decode('utf8'))
    # tmp_name = tmp_name.decode('utf8')
    # print(tmp_name)

    # 得到文件夹的个数
    folder_length = ''
    for j in range(length_int + total_byte, total_byte + length_int + length_int):
        tmp = bin(file_data[j])[2:]
        folder_length = folder_length + (8 - len(tmp)) * '0' + tmp
    folder_length = int(folder_length, 2)
    # print(folder_length)

    # 得到文件个数
    file_length = ''
    for k in range(total_byte + length_int + length_int, total_byte + 3 * length_int):
        tmp = bin(file_data[k])[2:]
        file_length = file_length + (8 - len(tmp)) * '0' + tmp
    file_length = int(file_length, 2)
    # print(file_length)

    # 得到文件夹和文件的具体信息
    all_folders = []
    all_files = []
    # 得到folderlist
    start = total_byte + 3 * length_int
    end = total_byte + 4 * length_int
    for i in range(0, folder_length):
        folder_name_end = get_files_folds(file_data, start, end)
        folder_name = folder_name_end[0]
        start = folder_name_end[1]
        end = start + 4
        all_folders.append(folder_name)

    for j in range(0, file_length):
        folder_name_end = get_files_folds(file_data, start, end)
        folder_name = folder_name_end[0]
        start = int(folder_name_end[1])
        end = start + 4
        all_files.append(folder_name)

    # print(all_files)
    # print(all_folders)

    # 创建目录
    for folder in all_folders:
        # folder = root + folder[1:]
        if os.path.exists(folder):
            return "对不起 解压文件夹已经存在"
        os.makedirs(folder)

    for file in all_files:
        # 调用解压函数 解压每一个文件
        tmp = Work('', '', '', '')
        end = tmp.file_decompress(start, file_data, file)
        start = end

    return "解压完毕"


class WorkThread(QThread):
    """
    线程类
    """
    trigger = pyqtSignal(str)

    def __init__(self, flag, input_filename, output_filename, parent=None):
        super(WorkThread, self).__init__(parent)
        self.flag = flag
        self.input_filename = input_filename
        self.output_filename = output_filename

    def run(self):
        if self.flag == 0:
            reply_message = compress(self.input_filename, self.output_filename)
            self.trigger.emit(reply_message)
        else:
            reply_message = decompress(self.input_filename)
            self.trigger.emit(reply_message)


class HaffumanForm(QWidget, Ui_Form):
    # TODO: 加个进度条？？？
    def __init__(self):
        super(HaffumanForm, self).__init__()
        self.input_folder_name = ''
        self.output_folder_name = ''
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
        file_name = QFileDialog.getExistingDirectory(self, "选择一个文件夹", "/home/")
        # 得到元组
        if file_name == '':
            QMessageBox.information(self, "警告", "请选择文件", QMessageBox.Yes)
        else:
            self.input_folder_name = file_name

            self.lineEdit_open_path.setText(self.input_folder_name)

            self.pushButton_compress.setEnabled(True)

    def decompress_get_path(self):
        """
        解压时 获取文件路径
        :return:
        """
        file_name = QFileDialog.getOpenFileName(self, "选择一个文件", "/home/", "All Files(*.folderbak)")
        # 得到元组
        if file_name[0] == '':
            QMessageBox.information(self, "警告", "请选择文件", QMessageBox.Yes)
        else:
            self.input_folder_name = file_name[0]
            self.lineEdit.setText(self.input_folder_name)
            self.pushButton_decompress.setEnabled(True)

    def stop_thread(self, reply):
        """
        线程结束 打印线程结束的提示信息 退出线程
        :param reply:
        :return:
        """
        self.textBrowser_message.append(reply)
        self.work_thread.quit()

    def compress(self):
        """
        压缩文件函数
        :return:
        """
        # 得到文件
        if self.input_folder_name == '':
            QMessageBox.information(self, "警告", "请选择文件", QMessageBox.Yes)
            return

        # 显示提示信息
        self.textBrowser_message.append("正在压缩请稍后......")
        self.pushButton_compress.setEnabled(False)

        # 文件操作得到文件名
        dir_name = os.path.dirname(self.input_folder_name)
        self.output_folder_name = os.path.basename(self.input_folder_name) + '.folderbak'
        self.output_folder_name = dir_name + '/' + self.output_folder_name

        # 开线程 防止UI卡顿
        self.work_thread = WorkThread(0, self.input_folder_name, self.output_folder_name)
        self.work_thread.trigger.connect(self.stop_thread)
        self.work_thread.start()

        self.lineEdit_open_path.clear()

    def depress(self):
        #  选择文件
        if self.input_folder_name == '':
            QMessageBox.information(self, "警告", "请选择文件", QMessageBox.Yes)
            return
        # 显示提示信息
        self.textBrowser_message.setText("正在解压，请稍后......")
        self.pushButton_decompress.setEnabled(False)

        # 文件操作 最终得到文件夹名
        dir_name = os.path.dirname(self.input_folder_name)
        self.output_folder_name = os.path.basename(self.input_folder_name)
        self.output_folder_name = os.path.splitext(self.output_folder_name)[0]
        self.output_folder_name = dir_name + '/' + self.output_folder_name

        # 检测解压文件夹是否已经存在
        if os.path.exists(self.output_folder_name):
            warning_message = self.output_folder_name + "已经存在 是否覆盖？？？"
            reply = QMessageBox.information(self, "警告", warning_message, QMessageBox.Yes, QMessageBox.No)

            if reply != QMessageBox.Yes:
                # print("yest")
                self.textBrowser_message.append("对不起 我未能获得覆盖权限")
                return
            else:
                # 如果要覆盖就级联删除掉
                shutil.rmtree(self.output_folder_name)

        # UI 与逻辑分开 防止UI 卡顿 开辟线程
        self.work_thread = WorkThread(1, self.input_folder_name, self.output_folder_name)
        self.work_thread.trigger.connect(self.stop_thread)
        self.work_thread.start()

        # 清空lineedit的文字
        self.lineEdit.clear()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    My_win = HaffumanForm()
    My_win.show()
    sys.exit(app.exec_())
