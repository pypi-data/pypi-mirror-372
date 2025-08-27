# -*- coding: utf-8 -*-
"""
:Author: ChenXiaolei
:Date: 2021-09-16 11:42:13
:LastEditTime: 2023-11-13 16:23:20
:LastEditors: ChenXiaolei
:Description: 
"""
import os,shutil


class OSHelper:
    def remove(self, path):
        """
        :description: 删除本地文件或文件夹
        :param path:文件或文件夹路径
        :return 文件存在并删除True  文件不存在 False
        :last_editors: ChenXiaolei
        """
        result = False
        if os.path.isfile(path):
            if os.path.exists(path):  # 如果文件存在
                # 删除文件，可使用以下两种方法。
                os.remove(path)
                result = True
            else:
                print('no such file:%s' % my_file)  # 则返回文件不存在
        elif os.path.isdir(path):
            os.removedirs(path)  # 递归地删除目录。如果子目录成功被删除，则将会成功删除父目录，子目录没成功删除，将抛异常。
            result = True
        else:
            print("it's a special file(socket,FIFO,device file)")

        return result

    def is_file_by_path(self, path):
        """
        :description: 根据路径判断是否是文件
        :param path:路径
        :return 是文件:True 非文件:False
        :last_editors: ChenXiaolei
        """
        return os.path.isfile(path)

    def is_dir_by_path(self, path):
        """
        :description: 根据路径判断是否是文件夹
        :param path: 路径
        :return 是文件夹:True 非文件夹:False
        :last_editors: ChenXiaolei
        """
        return os.path.isdir(path)

    def chdir(self, path):
        """
        :description: 改变当前工作目录
        :param path: 路径
        :return 如果允许访问返回 True , 否则返回False。
        :last_editors: ChenXiaolei
        """
        return os.chdir(path)

    def chmod(self, path, mode):
        """
        :description: 更改权限
        :param path: 文件名路径或目录路径。
        :param mode: 可用以下选项按位或操作生成， 目录的读权限表示可以获取目录里文件名列表， ，执行权限表示可以把工作目录切换到此目录 ，删除添加目录里的文件必须同时有写和执行权限 ，文件权限以用户id->组id->其它顺序检验,最先匹配的允许或禁止权限被应用。
            stat.S_IXOTH: 其他用户有执行权0o001
            stat.S_IWOTH: 其他用户有写权限0o002
            stat.S_IROTH: 其他用户有读权限0o004
            stat.S_IRWXO: 其他用户有全部权限(权限掩码)0o007
            stat.S_IXGRP: 组用户有执行权限0o010
            stat.S_IWGRP: 组用户有写权限0o020
            stat.S_IRGRP: 组用户有读权限0o040
            stat.S_IRWXG: 组用户有全部权限(权限掩码)0o070
            stat.S_IXUSR: 拥有者具有执行权限0o100
            stat.S_IWUSR: 拥有者具有写权限0o200
            stat.S_IRUSR: 拥有者具有读权限0o400
            stat.S_IRWXU: 拥有者有全部权限(权限掩码)0o700
            stat.S_ISVTX: 目录里文件目录只有拥有者才可删除更改0o1000
            stat.S_ISGID: 执行此文件其进程有效组为文件所在组0o2000
            stat.S_ISUID: 执行此文件其进程有效用户为文件所有者0o4000
            stat.S_IREAD: windows下设为只读
            stat.S_IWRITE: windows下取消只读
        :return 该方法没有返回值
        :last_editors: ChenXiaolei
        """
        return os.chmod(path, mode)

    def getcwd(self):
        """
        :description: 返回当前工作目录
        :return 返回当前进程的工作目录
        :last_editors: ChenXiaolei
        """
        return os.getcwd()

    def make_dirs(self, dir_path):
        """
        :description: 创建目录
        :return dir_path: 目录全路径
        :last_editors: ChenXiaolei
        """
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

    def copy_tree(self, source, dest, is_cover=False):
        """
        :description: 拷贝目录
        :return source: 源目录
        :return dest: 目标目录
        :return is_cover: 目标目录存在是否删除,False: 遍历目录,如果存在不覆盖,不存在则拷贝   True:目录存在先删除目录再进行操作
        :last_editors: ChenXiaolei
        """
        if not os.path.exists(dest):
            os.makedirs(dest)
        if os.path.exists(source):
            for file in os.listdir(source):
                file_path = os.path.join(source, file)
                dst_path = os.path.join(dest, file)
                if os.path.isfile(os.path.join(source, file)):
                    if is_cover or (not os.path.exists(dst_path)):
                        shutil.copyfile(file_path, dst_path)
                else:
                    self.copy_tree(file_path, dst_path)

    def print_dir_tree(self, path, level):
        """
        :description: 打印目录结构树
        :param path 目录路径
        :param level 目录级别
        :return 打印目录结构
        :last_editors: ChenXiaolei
        """
        for item in os.listdir(path):
            print('\t' * level + '|--' + item)
            new_path = os.path.join(path, item)
            if os.path.isdir(new_path):
                self.print_dir_tree(new_path, level + 1)