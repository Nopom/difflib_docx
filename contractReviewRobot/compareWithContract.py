import os
import zipfile
import difflib
import shutil
import time
from xml.dom.minidom import parse
from contractReviewRobot import zipManager,compareWorks

class crr():

    def __init__(self):
        self.com_time = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
        self.c = compareWorks.CompareWorks()

    def docx2zip(self):

        newtype = 'zip'
        oldtype = 'docx'
        self.zip_path = []
        self.rootpath = os.getcwd() + '\\compareRobot\\'

        os.makedirs(self.rootpath +self.com_time)

        all_file_list = os.listdir(self.rootpath)
        for file_name in all_file_list:
            currentdir = os.path.join(self.rootpath, file_name)
            fnames = os.path.splitext(file_name)[0:-1]
            fname = ''
            for i in fnames:
                fname += i
            ftype = os.path.splitext(file_name)[-1]
            if oldtype in ftype[1:]:
                shutil.move(currentdir, self.rootpath + self.com_time)

        self.rootpath += self.com_time +'\\'
        all_file_list = os.listdir(self.rootpath)
        for file_name in all_file_list:
            currentdir = os.path.join(self.rootpath, file_name)
            fnames = os.path.splitext(file_name)[0:-1]
            fname = ''
            for i in fnames:
                fname += i
            ftype = os.path.splitext(file_name)[-1]
            if oldtype in ftype[1:]:
                ftype = ftype.replace(oldtype, newtype)
                newname = os.path.join(self.rootpath, fname + ftype)
                os.rename(currentdir, newname)

        all_file_list = os.listdir(self.rootpath)
        self.files =  []

        for file_name in all_file_list:
            currentdir = os.path.join(self.rootpath, file_name)
            ftype = os.path.splitext(file_name)[-1]
            if newtype in ftype[1:]:
                s = zipfile.ZipFile(currentdir)
                f = s.open('word/document.xml', 'r')
                self.files.append(parse(f))
                s.close()

    def xml_index(self):

        self.file1 = self.files[0]
        self.file2 = self.files[1]
        self.rootdata1 = self.file1.documentElement
        self.rootdata2 = self.file2.documentElement

        self.document_xml_con1, self.document_xml_index1,\
            self.table_xml_con1,self.table_xml_doc1,self.table_xml_index1, \
                self.table_xml_tc1 = self.c.document_work(self.rootdata1,self.file1)

        self.document_xml_con2, self.document_xml_index2,\
            self.table_xml_con2,self.table_xml_doc2,self.table_xml_index2, \
                self.table_xml_tc2 = self.c.document_work(self.rootdata2,self.file2)

        self.table_xml_diff1 = {}
        self.table_xml_diff2 = {}
        self.table_xml_docu1 = {}
        self.table_xml_docu2 = {}

        self.table_xml_diff1 = self.table_xml_tc1
        self.table_xml_doc1 = self.table_xml_doc1

        self.sim_list = []
        for i1,v1 in self.table_xml_con1.items():
            for i2,v2 in self.table_xml_con2.items():
                sim = difflib.SequenceMatcher(None,v1,v2).quick_ratio()
                if sim > 0.8:
                    self.sim_list.append([i1,i2])

        tc1_list = []
        tc2_list = []
        for n in self.sim_list:
            tc1_list.append(n[0])
            tc2_list.append(n[-1])

        self.table_single1 = []
        self.table_single2 = []
        for i,v in self.table_xml_tc1.items():
            if i not in tc1_list:
                self.table_single1.append([i])
        for i, v in self.table_xml_tc2.items():
            if i not in  tc2_list:
                self.table_single2.append([i])

    def document_xml_compare(self):

        self.dict_file2_add_index = {}
        self.dict_file2_add_con = {}
        self.dict_file1_delete_index = {}
        self.dict_file1_delete_con = {}
        self.dict_file1_update_index = {}
        self.dict_file1_update_con = {}
        self.dict_file2_update_index = {}
        self.dict_file2_update_con = {}
        self.dict_file1_change_con = {}
        self.dict_file1_change_index = {}
        self.dict_file2_change_con = {}
        self.dict_file2_change_index = {}

        document_con1 = self.document_xml_con1
        document_con2 = self.document_xml_con2
        s = difflib.SequenceMatcher(lambda x: x == " ",
                                    document_con1, document_con2)
        diff = difflib.Differ()
        for (tag, i1, i2, d1, d2) in s.get_opcodes():

            if tag == 'replace' and (len(document_con1[i1:i2]) > 1
                                     or len(document_con2[d1:d2])) :
                # print(("%7s \n file1[%d:%d] (%s) \n file2[%d:%d] (%s)" %
                #        (tag, i1, i2, document_con1[i1:i2], d1, d2,
                #         document_con2[d1:d2])))
                content_diff = diff.compare(document_con1[i1:i2], document_con2[d1:d2])
                diff_words = list(content_diff)
                content_diff.close()
                diff_words_list = []
                cdl_all = {}
                for i in range(len(diff_words)):
                    if '-' == diff_words[i][0] or '+' == diff_words[i][0]:
                        cdl_all[i] = diff_words[i]
                        diff_words_list.append(diff_words[i])

                cdl_delete,cdl_add,cdl_update,cdl_other = self.c.diff2cdl(diff_words)

                cdl_file1 = {}
                cdl_file1_con = []
                cdl_file2 = {}
                cdl_file2_con = []
                for i,v in cdl_all.items():
                    if v[0] == '-':
                        cdl_file1[i] = v
                        cdl_file1_con.append(v[2:])
                    else:
                        cdl_file2[i] = v
                        cdl_file2_con.append(v[2:])

                doc1 = []
                doc1_index = []
                for e in range(i1, i2):
                    doc1.append(document_con1[e])
                    doc1_index.append(e)
                s_file1 = difflib.SequenceMatcher(lambda x: x == " ", cdl_file1_con,doc1)
                for (tag, i1_1, i2_1, d1_1, d2_1) in s_file1.get_opcodes():
                    if tag == 'insert':
                        for i in range(len(doc1)):
                            if i == i1_1:
                                r = doc1_index[i]
                                doc1_index.remove(r)
                doc2 = []
                doc2_index = []
                for e in range(d1, d2):
                    doc2.append(document_con2[e])
                    doc2_index.append(e)
                s_file2 = difflib.SequenceMatcher(lambda x: x == " ", cdl_file2_con, doc2)
                for (tag, i1_1, i2_1, d1_1, d2_1) in s_file2.get_opcodes():
                    # print(("%7s \n file1[%d:%d] (%s) \n file2[%d:%d] (%s)" %
                    #        (tag, i1_1, i2_1, doc1[i1_1:i2_1], d1_1, d2_1,
                    #         cdl_file1_con[d1_1:d2_1])))
                    if tag == 'insert':
                        for i in range(len(doc2)):
                            if i == i1_1:
                                r = doc2_index[i]
                                doc2_index.remove(r)

                flag_file1 = {}
                for i, e in zip(cdl_file1,doc1_index ):
                    flag_file1[i] = e

                flag_file2 = {}
                for i, e in zip(cdl_file2, doc2_index):
                    flag_file2[i] = e

                diff_doc1,diff_doc2 = self.c.cdl2diff(cdl_add)
                for (n1,m1),(n2,m2) in zip(diff_doc1.items(),diff_doc2.items()):
                    sim = self.c.document_xml_similar(m1,m2)
                    if sim[0] > 0.2:
                        ss = difflib.SequenceMatcher(lambda x: x == " ",m1[2:], m2[2:])
                        num_add_all = []
                        num_add_con = []
                        for (tag, i1_1, i2_1, d1_1, d2_1) in ss.get_opcodes():
                            # print(("%7s file1[%d:%d] (%s) file2[%d:%d] (%s)" %
                            #        (tag, i1_1, i2_1, m1[i1_1 + 2:i2_1 + 2],
                            #         d1_1, d2_1, m2[d1_1 + 2:d2_1 + 2])))
                            if tag == 'insert':

                                num_add = []
                                for num in range(d1_1, d2_1):
                                    num_add.append(num)
                                num_add_all.append(num_add)
                                num_add_con.append(m2[d1_1 + 2:d2_1 + 2])
                                for index, value in flag_file2.items():
                                    if n2 == index:
                                        self.dict_file2_add_con[value] = num_add_con
                                        self.dict_file2_add_index[value] = num_add_all
                    else:
                        num_change = []
                        for l in range(len(m1[2:])):
                            num_change.append(l)
                        num_change1_all = [num_change]
                        for index, value in flag_file1.items():
                            if n1 == index:
                                self.dict_file1_change_con[value] = m1[2:]
                                self.dict_file1_change_index[value] = num_change1_all
                        num_change = []
                        for l in range(len(m2[2:])):
                            num_change.append(l)
                        num_change2_all = [num_change]
                        for index, value in flag_file2.items():
                            if n2 == index:
                                self.dict_file2_change_con[value] = m2[2:]
                                self.dict_file2_change_index[value] = num_change2_all

                diff_doc1, diff_doc2 = self.c.cdl2diff(cdl_delete)
                for (n1,m1),(n2,m2) in zip(diff_doc1.items(),diff_doc2.items()):
                    sim = self.c.document_xml_similar(m1, m2)
                    if sim[0] > 0.2:
                        ss = difflib.SequenceMatcher(lambda x: x == " ", m1[2:], m2[2:])
                        num_delete_all = []
                        num_delete_con = []
                        for (tag, i1_1, i2_1, d1_1, d2_1) in ss.get_opcodes():

                            # print(("%7s file1[%d:%d] (%s) file2[%d:%d] (%s)" %
                            #        (tag, i1_1, i2_1, m1[i1_1 + 2:i2_1 + 2],
                            #         d1_1, d2_1, m2[d1_1 + 2:d2_1 + 2])))
                            if tag == 'delete':
                                num_delete = []
                                for num in range(i1_1, i2_1):
                                    num_delete.append(num)
                                num_delete_all.append(num_delete)
                                num_delete_con.append(m1[i1_1 + 2:i2_1 + 2])
                                for index, value in flag_file1.items():
                                    if n1 == index:
                                        self.dict_file1_delete_con[value] = num_delete_con
                                        self.dict_file1_delete_index[value] = num_delete_all
                    else:
                        num_change = []
                        for l in range(len(m1[2:])):
                            num_change.append(l)
                        num_change1_all = [num_change]
                        for index, value in flag_file1.items():
                            if n1 == index:
                                self.dict_file1_change_con[value] = m1[2:]
                                self.dict_file1_change_index[value] = num_change1_all
                        num_change = []
                        for l in range(len(m2[2:])):
                            num_change.append(l)
                        num_change2_all = [num_change]
                        for index, value in flag_file2.items():
                            if n2 == index:
                                self.dict_file2_change_con[value] = m2[2:]
                                self.dict_file2_change_index[value] = num_change2_all

                diff_doc1, diff_doc2 = self.c.cdl2diff(cdl_update)
                for (n1,m1),(n2,m2) in zip(diff_doc1.items(),diff_doc2.items()):
                    sim = self.c.document_xml_similar(m1, m2)
                    if sim[0] > 0.2:
                        ss = difflib.SequenceMatcher(lambda x: x == " ",m1[2:], m2[2:])
                        num_update1_all = []
                        num_update1_con = []
                        num_update2_all = []
                        num_update2_con = []
                        for (tag, i1_1, i2_1, d1_1, d2_1) in ss.get_opcodes():
                            if tag == 'replace':
                                # print(("%7s file1[%d:%d] (%s) file2[%d:%d] (%s)" %
                                #    (tag, i1_1, i2_1, m1[i1_1 + 2:i2_1 + 2],
                                #     d1_1, d2_1, m2[d1_1 + 2:d2_1 + 2])))
                                num_update1 = []
                                for num in range(i1_1, i2_1):
                                    num_update1.append(num)
                                num_update1_all.append(num_update1)
                                num_update1_con.append(m1[i1_1 + 2:i2_1 + 2])
                                for index, value in flag_file1.items():
                                    if n1 == index:
                                        self.dict_file1_update_con[value] = num_update1_con
                                        self.dict_file1_update_index[value] = num_update1_all
                                num_update2 = []
                                for num in range(d1_1, d2_1):
                                    num_update2.append(num)
                                num_update2_all.append(num_update2)
                                num_update2_con.append(m2[d1_1 + 2:d2_1 + 2])
                                for index, value in flag_file2.items():
                                    if n2 == index:
                                        self.dict_file2_update_con[value] = num_update2_con
                                        self.dict_file2_update_index[value] = num_update2_all
                    else:
                        num_change = []
                        for l in range(len(m1[2:])):
                            num_change.append(l)
                        num_change1_all = [num_change]
                        for index, value in flag_file1.items():
                            if n1 == index:
                                self.dict_file1_change_con[value] = m1[2:]
                                self.dict_file1_change_index[value] = num_change1_all
                        num_change = []
                        for l in range(len(m2[2:])):
                            num_change.append(l)
                        num_change2_all = [num_change]
                        for index, value in flag_file2.items():
                            if n2 == index:
                                self.dict_file2_change_con[value] = m2[2:]
                                self.dict_file2_change_index[value] = num_change2_all

                for n,m in cdl_other.items():
                    if m[0] == '+':
                        num_add_all = []
                        num_add = []
                        for l in range(len(m[2:])):
                            num_add.append(l)
                        num_add_all.append(num_add)
                        for index, value in flag_file2.items():
                            if n == index:
                                self.dict_file2_add_con[value] = m[2:]
                                self.dict_file2_add_index[value] = num_add_all
                    else:
                        num_delete_all = []
                        num_delete = []
                        for l in range(len(m[2:])):
                            num_delete.append(l)
                        num_delete_all.append(num_delete)
                        for index, value in flag_file1.items():
                            if n == index:
                                self.dict_file1_delete_con[value] = m[2:]
                                self.dict_file1_delete_index[value] = num_delete_all

            elif tag == 'replace' and len(document_con1[i1:i2]) == 1 and \
                                        len(document_con2[d1:d2]) == 1:

                sim = self.c.document_xml_similar(document_con1[i1],document_con2[d1])
                if sim[0] > 0.8:
                    ss = difflib.SequenceMatcher(lambda x: x == " ",
                                                 document_con1[i1], document_con2[d1])

                    num_add_all = []
                    num_add_con = []
                    num_delete_all = []
                    num_delete_con = []
                    num_update1_all = []
                    num_update1_con = []
                    num_update2_all = []
                    num_update2_con = []

                    for (tag, i1_1, i2_1, d1_1, d2_1) in ss.get_opcodes():
                        # print(("%7s file1[%d:%d] (%s) file2[%d:%d] (%s)" %
                        #                (tag, i1_1, i2_1, document_con1[i1][i1_1 + 2:i2_1 + 2],
                        #         d1_1, d2_1,document_con2[d1][d1_1 + 2:d2_1 + 2])))
                        if tag == 'insert':
                            num_add = []
                            for num in range(d1_1, d2_1):
                                num_add.append(num)
                            num_add_all.append(num_add)
                            num_add_con.append(document_con2[d1][d1_1 + 2:d2_1 + 2])
                            self.dict_file2_add_con[d1] = num_add_con
                            self.dict_file2_add_index[d1] = num_add_all
                        elif tag == 'delete':
                            num_delete = []
                            for num in range(i1_1, i2_1):
                                num_delete.append(num)
                            num_delete_all.append(num_delete)
                            num_delete_con.append(document_con1[i1][i1_1 + 2:i2_1 + 2])
                            self.dict_file1_delete_con[i1] = num_delete_con
                            self.dict_file1_delete_index[i1] = num_delete_all
                        elif tag == 'replace':
                            # print(("%7s file1[%d:%d] (%s) file2[%d:%d] (%s)" %
                            #        (tag, i1_1, i2_1, compare_diff_list[n - 1][i1_1 + 2:i2_1 + 2],
                            #         d1_1, d2_1,compare_diff_list[n][d1_1 + 2:d2_1 + 2])))
                            num_update1 = []
                            for num in range(i1_1, i2_1):
                                num_update1.append(num)
                            num_update1_all.append(num_update1)
                            num_update1_con.append(document_con1[i1][i1_1 + 2:i2_1 + 2])
                            self.dict_file1_update_con[i1] = num_update1_con
                            self.dict_file1_update_index[i1] = num_update1_all
                            num_update2 = []
                            for num in range(d1_1, d2_1):
                                num_update2.append(num)
                            num_update2_all.append(num_update2)
                            num_update2_con.append(document_con2[d1][d1_1 + 2:d2_1 + 2])
                            self.dict_file2_update_con[d1] = num_update2_con
                            self.dict_file2_update_index[d1] = num_update2_all
                else:
                    num_change = []
                    for l in range(len(document_con1[i1])):
                        num_change.append(l)
                    num_change1_all = [num_change]
                    self.dict_file1_change_con[i1] = document_con1[i1]
                    self.dict_file1_change_index[i1] = num_change1_all
                    num_change = []
                    for l in range(len(document_con2[d1])):
                        num_change.append(l)
                    num_change2_all = [num_change]
                    self.dict_file2_change_con[d1] = document_con2[d1]
                    self.dict_file2_change_index[d1] = num_change2_all

            elif tag == 'insert':
                for ls in range(d1,d2):
                    num_add_all = []
                    num_add = []
                    for l in range(len(document_con2[ls])):
                        num_add.append(l)
                    num_add_all.append(num_add)
                    self.dict_file2_add_con[ls] = document_con2[ls]
                    self.dict_file2_add_index[ls] = num_add_all

            elif tag == 'delete':
                # print(("%7s \n file1[%d:%d] (%s) \n file2[%d:%d] (%s)" %
                #        (tag, i1, i2, document_con1[i1:i2], d1, d2,
                #         document_con2[d1:d2])))
                for ls in range(i1,i2):
                    num_delete_all = []
                    num_delete = []
                    for l in range(len(document_con1[ls])):
                        num_delete.append(l)
                    num_delete_all.append(num_delete)
                    self.dict_file1_delete_con[ls] = document_con1[ls]
                    self.dict_file1_delete_index[ls] = num_delete_all

    def table_xml_compare(self):

        self.table_file2_add_index = {}
        self.table_file1_delete_index = {}
        self.table_file1_update_index = {}
        self.table_file2_update_index = {}

        table_files = [[self.table_file1_delete_index, self.table_file1_update_index],
                          [self.table_file2_add_index, self.table_file2_update_index]]
        table_indexs = [self.table_xml_index1,self.table_xml_index2]

        diff = difflib.Differ()
        flag_all = 0

        for index1,value1 in self.table_xml_tc1.items():
            for index2,value2 in self.table_xml_tc2.items():
                for n in self.sim_list:
                    if index1 == n[0] and index2 == n[-1]:
                        if len(value1) == len(value2) :

                            table_files, flag_all = self.c.cdl2index(flag_all, diff,
                                 index1, value1, index2, value2, table_indexs, table_files)

                        elif len(value1) != len(value2):

                            list_delete = []
                            list_add = []
                            for i1,v1 in self.table_xml_doc1.items():
                                for i2,v2 in self.table_xml_doc2.items():
                                    for n in self.sim_list:
                                        if i1 == n[0] and i2 == n[-1]:
                                            if i1 == index1 and i2 == index2:
                                                flag1 = 0
                                                for index1_1, value1_1 in value1.items():
                                                    flag1 = index1_1
                                                    break
                                                flag2 = 0
                                                for index1_1, value1_1 in value2.items():
                                                    flag2 = index1_1
                                                    break

                                                s = difflib.SequenceMatcher(lambda x: x == " ", v1, v2)
                                                for (tag, i1, i2, d1, d2) in s.get_opcodes():
                                                    # print(("%7s \n file1[%d:%d] (%s) \n file2[%d:%d] (%s)" %
                                                    #        (tag, i1, i2, v1[i1:i2], d1, d2,
                                                    #         v2[d1:d2])))
                                                    if tag == 'delete' :
                                                        list_delete.append(i1 + flag1)
                                                    if tag == 'insert':
                                                        list_add.append(d1 + flag2)
                                                    if tag == 'replace':
                                                        if (i2 - i1) > 1 or (d2 - d1) > 1:
                                                            value_diff = diff.compare(v1[i1:i2], v2[d1:d2])
                                                            diff_words = list(value_diff)
                                                            value_diff.close()
                                                            cdl_delete, cdl_add, cdl_update, cdl_other \
                                                                            = self.c.diff2cdl(diff_words)
                                                            for b,d in cdl_other.items():
                                                                if d[0] == '-':
                                                                    list_delete.append(b)
                                                                if d[0] == '+':
                                                                    list_add.append(b)

                            for p, q in self.table_xml_index1.items():
                                if index1 == p:
                                    for p1, q1 in q.items():
                                        for n in list_delete:
                                            if p1 == n:
                                                self.table_single1.append([p,p1])
                                            flag_all += 1
                            for p, q in self.table_xml_index2.items():
                                if index2 == p:
                                    for p1, q1 in q.items():
                                        for n in list_add:
                                            if p1 == n:
                                                self.table_single2.append([p,p1])
                                            flag_all += 1

                            table1 = {}
                            for i1,v1 in value1.items():
                                if i1 not in list_delete :
                                    table1[i1] = v1
                            table2 = {}
                            for i1,v1 in value2.items():
                                if i1 not in list_add :
                                    table2[i1] = v1

                            table_files, flag_all = self.c.cdl2index(flag_all, diff,
                                index1, table1, index2, table2, table_indexs, table_files)

        self.table_file1_delete_index = self.c.table_index_change(table_files[0][0])
        self.table_file1_update_index = self.c.table_index_change(table_files[0][1])
        self.table_file2_add_index = self.c.table_index_change(table_files[1][0])
        self.table_file2_update_index = self.c.table_index_change(table_files[1][1])

    def document_xml_diff(self):
        c = compareWorks.CompareWorks()
        self.file1_delete = {}
        self.file1_update = {}
        self.file1_change = {}
        c.document_work1(self.document_xml_index1,self.dict_file1_delete_index,self.file1_delete)
        c.document_work1(self.document_xml_index1,self.dict_file1_update_index,self.file1_update)
        c.document_work1(self.document_xml_index1,self.dict_file1_change_index,self.file1_change)

        self.file2_add = {}
        self.file2_update = {}
        self.file2_change = {}
        c.document_work1(self.document_xml_index2, self.dict_file2_add_index, self.file2_add)
        c.document_work1(self.document_xml_index2, self.dict_file2_update_index, self.file2_update)
        c.document_work1(self.document_xml_index2, self.dict_file2_change_index, self.file2_change)

    def document_xml_change(self):

        for child_docu in self.rootdata1.childNodes:
            num = 0
            for child_p in child_docu.childNodes:
                if child_p.nodeName == 'w:p':
                    self.c.document_work2(child_p,num,self.file1_delete,self.file1,'red')
                    self.c.document_work2(child_p,num,self.file1_update,self.file1,'yellow')
                    self.c.document_work2(child_p,num,self.file1_change,self.file1,'lightGray')
                    num+=1

        for child_docu in self.rootdata2.childNodes:
            num = 0
            for child_p in child_docu.childNodes:
                if child_p.nodeName == 'w:p' :
                    self.c.document_work2(child_p, num, self.file2_add, self.file2, 'green')
                    self.c.document_work2(child_p, num, self.file2_update, self.file2, 'yellow')
                    self.c.document_work2(child_p, num, self.file2_change, self.file2, 'lightGray')
                    num+=1

    def table_xml_change(self):

        for child_docu in self.rootdata1.childNodes:
            num_tbl = 0
            for child_tbl in child_docu.childNodes:
                if child_tbl.nodeName == 'w:tbl':
                    self.c.table_work2(child_tbl,num_tbl,
                                 self.table_file1_delete_index,self.file1,'red')
                    self.c.table_work2(child_tbl,num_tbl,
                                 self.table_file1_update_index,self.file1,'yellow')
                    self.c.table_work3(child_tbl, num_tbl,
                                       self.table_single1, self.file1, 'FF0000')
                    num_tbl += 1

        for child_docu in self.rootdata2.childNodes:
            num_tbl = 0
            for child_tbl in child_docu.childNodes:
                if child_tbl.nodeName == 'w:tbl':
                    self.c.table_work2(child_tbl, num_tbl,
                                 self.table_file2_add_index, self.file2, 'green')
                    self.c.table_work2(child_tbl, num_tbl,
                                 self.table_file2_update_index, self.file2, 'yellow')
                    self.c.table_work3(child_tbl,num_tbl,
                                       self.table_single2, self.file2, '00FF00')
                    num_tbl += 1

    def document_xml_replace(self):

        rootdata = []
        rootdata.append(self.rootdata1)
        rootdata.append(self.rootdata2)
        all_file_list = os.listdir(self.rootpath)
        for file_name,root in zip(all_file_list,rootdata):
            with open(self.rootpath + 'document.xml', 'w', encoding='utf-8') as file:
                root.writexml(file)
            currentdir = os.path.join(self.rootpath, file_name)
            ftype = os.path.splitext(file_name)[-1]
            newxml = ''
            for new in os.listdir(self.rootpath):
                if os.path.splitext(new)[-1] == '.xml':
                    newxml = os.path.join(self.rootpath, new)
            if ftype == '.zip':
                ss = zipManager.ZipManager(currentdir, 'a')
                compress_type = ss.getinfo('word/document.xml').compress_type
                ss.remove('word/document.xml')
                ss.write(newxml, 'word/document.xml', compress_type)
                ss.close()
            os.remove(self.rootpath + 'document.xml')

    def zip2docx(self):
        newtype = 'docx'
        oldtype = 'zip'
        all_file_list = os.listdir(self.rootpath )

        for file_name in all_file_list:
            currentdir = os.path.join(self.rootpath , file_name)
            fname = os.path.splitext(file_name)[0]
            ftype = os.path.splitext(file_name)[1]
            if oldtype in ftype[1:]:
                ftype = ftype.replace(oldtype, newtype)
                newname = os.path.join(self.rootpath  +fname +'_'+self.com_time + ftype)
                os.rename(currentdir, newname)

if __name__ == '__main__':

    c = crr()
    c.docx2zip()
    c.xml_index()
    c.table_xml_compare()
    c.document_xml_compare()
    c.document_xml_diff()
    c.document_xml_change()
    c.table_xml_change()
    c.document_xml_replace()
    c.zip2docx()

