import jieba
from gensim import corpora, models, similarities
import difflib

class CompareWorks:

    def document_work(self,rootdata,file):

        document_xml_con = []
        document_xml_index = {}
        table_xml_con = {}
        table_xml_doc = {}
        table_xml_index = {}
        table_xml_tc = {}
        bodydata = rootdata.getElementsByTagName('w:body')
        for body in bodydata:
            for p in body.getElementsByTagName('w:p'):
                if len(p.getElementsByTagName('w:t')) == 0:
                    data = file.createTextNode(' ')
                    node = file.createElement('w:r')
                    node2_1 = file.createElement('w:rPr')
                    node2_2 = file.createElement('w:t')
                    node2_2.appendChild(data)
                    node.appendChild(node2_1)
                    node.appendChild(node2_2)
                    p.appendChild(node)
                for r in p.getElementsByTagName('w:r'):
                    names = []
                    for rs in r.childNodes:
                        name = rs.nodeName
                        names.append(name)
                    if 'w:t' in names:
                        if 'w:rPr' not in names:
                            child_t = r.getElementsByTagName('w:t')[0]
                            clone_t = child_t.cloneNode(True)
                            node_rpr = file.createElement('w:rPr')
                            r.appendChild(node_rpr)
                            r.appendChild(clone_t)
                            r.removeChild(child_t)
            # 段落
            num_p = 0
            for nodes in body.childNodes:
                if nodes.nodeName == 'w:p':
                    dict_index_index = {}
                    doc_con = ''
                    num_r = 0
                    for doc in nodes.childNodes:
                        if doc.nodeName == 'w:r':
                            for t in doc.getElementsByTagName('w:t'):
                                doc_con += t.firstChild.data
                                dict_index_index[num_r] = t.firstChild.data
                                document_xml_index[num_p] = dict_index_index
                        num_r += 1
                    num_p += 1
                    document_xml_con.append(doc_con)
            # 表格
            num_tbl = 0
            for nodes in body.childNodes:
                if nodes.nodeName == 'w:tbl':
                    num_tr = 0
                    dict_tr = {}
                    str_tr = ''
                    tr_list = []
                    list_tr = {}
                    for ts in nodes.childNodes:
                        if ts.nodeName == 'w:tr':
                            num_tc = 0
                            dict_tc = {}
                            str_tc = ''
                            list_tc = []
                            for tc in ts.childNodes:
                                if tc.nodeName == 'w:tc':
                                    num_p = 0
                                    dict_p = {}
                                    list_tp = []
                                    for tp in tc.childNodes:
                                        if tp.nodeName == 'w:p':
                                            num_r = 0
                                            dict_r = {}
                                            str_tt = ''
                                            for tr in tp.childNodes:
                                                if tr.nodeName == 'w:r':
                                                    num_tt = 0
                                                    dict_tt = {}
                                                    for tt in tr.childNodes:
                                                        if tt.nodeName == 'w:t':
                                                            dict_tt[num_tt] = tt.firstChild.data
                                                            dict_r[num_r] = dict_tt
                                                            dict_p[num_p] = dict_r
                                                            dict_tc[num_tc] = dict_p
                                                            dict_tr[num_tr] = dict_tc
                                                            table_xml_index[num_tbl] = dict_tr
                                                            str_tc += tt.firstChild.data
                                                            str_tt += tt.firstChild.data
                                                        num_tt += 1
                                                num_r += 1
                                            list_tp.append(str_tt)
                                        num_p += 1
                                    list_tc.append(list_tp)
                                num_tc += 1
                            str_tr += str_tc
                            tr_list.append(str_tc)
                            list_tr[num_tr] = list_tc
                        num_tr += 1
                    table_xml_con[num_tbl] = str_tr
                    table_xml_doc[num_tbl] = tr_list
                    table_xml_tc[num_tbl] = list_tr
                    num_tbl += 1

        return document_xml_con, document_xml_index, table_xml_con,\
               table_xml_doc, table_xml_index, table_xml_tc

    def document_xml_similar(self,train_doc,test_doc):

        doc1 = "我"
        doc2 = "北"
        doc3 = "上"
        doc4 = "海"

        all_doc = []
        all_doc.append(train_doc)
        all_doc.append(doc1)
        all_doc.append(doc2)
        all_doc.append(doc3)
        all_doc.append(doc4)
        all_doc_list = []
        for doc in all_doc:
            doc_list = [word for word in jieba.cut(doc)]
            all_doc_list.append(doc_list)
        doc_test_list = [word for word in jieba.cut(test_doc)]
        dictionary = corpora.Dictionary(all_doc_list)
        corpus = [dictionary.doc2bow(doc) for doc in all_doc_list]
        doc_test_vec = dictionary.doc2bow(doc_test_list)
        tfidf = models.TfidfModel(corpus)
        index = similarities.SparseMatrixSimilarity(tfidf[corpus], num_features=len(dictionary.keys()))
        sim = index[tfidf[doc_test_vec]]
        return sim

    def table_index_change(self,table_index):
        del_list = []
        for i1, v1 in table_index.items():
            for i2, v2 in table_index.items():
                if v1 == v2 and i1 != i2 and i1 < i2:
                    del_list.append(i2)
                if v1 != v2 and i1 != i2 and i1 < i2:
                    for i1_1, v1_1 in v1.items():
                        for i2_1, v2_1 in v2.items():
                            if i1_1 == i2_1:
                                for i1_2, v1_2 in v1_1.items():
                                    for i2_2, v2_2 in v2_1.items():
                                        if i1_2 == i2_2:
                                            for i1_3, v1_3 in v1_2.items():
                                                for i2_3, v2_3 in v2_2.items():
                                                    if i1_3 == i2_3:
                                                        for i1_4, v1_4 in v1_3.items():
                                                            for i2_4, v2_4 in v2_3.items():
                                                                if i1_4 == i2_4:
                                                                    for i1_4, v1_4 in v1_3.items():
                                                                        for i2_4, v2_4 in v2_3.items():
                                                                            if i1_4 == i2_4:
                                                                                for i1_5, v1_5 in v1_4.items():
                                                                                    for i2_5, v2_5 in v2_4.items():
                                                                                        if i1_5 == i2_5:
                                                                                            vs = []
                                                                                            vs2 = []
                                                                                            for i1_6, v1_6 in v1_5.items():
                                                                                                for i2_6, v2_6 in v2_5.items():
                                                                                                    if i1_6 == i2_6:
                                                                                                        vs.append(v1_6)
                                                                                                        vs.append(v2_6)
                                                                                                        del_list.append(
                                                                                                            i2)
                                                                                                [vs2.append(j) for j in
                                                                                                 vs if not j in vs2]
                                                                                                v1_5[i1_6] = vs2

        for i in del_list:
            table_index.pop(i)
        return table_index

    def document_work1(self,document_xml,dict_file,file):

        for index,value in document_xml.items():
            for index1,value1 in dict_file.items():
                diff_index_all = []
                flag_dict = {}
                for vs in value1:
                    if index == index1:
                        len_num = [0]
                        lens = 0
                        for index2,value2 in value.items():
                            lens += len(value2)
                            len_num.append(lens)

                        dict_index = {}
                        for flag, (n, m) in zip(value.keys(), zip(range(len(len_num) - 1),
                                                                  range(1, len(len_num)))):
                            dict_index[flag] = [len_num[n], len_num[m]]
                            flag += 1
                        for n,m in dict_index.items():
                            diff_index = []
                            for v in vs:
                                if m[0] <= v and v < m[1]:
                                    diff_index.append(v - m[0])
                            if len(diff_index) != 0:
                                diff_index_all.append(diff_index)
                                if n in flag_dict.keys():
                                    flag_dict[n] = diff_index_all
                                else:
                                    flag_dict[n] = [diff_index]
                            file[index] = flag_dict

    def document_work2(self,child_p,num,document_index,file,color):

        for indexs, values in document_index.items():
            if indexs == num:
                clone_dict = {}
                child_dict = {}
                num1 = 0
                for child_r in child_p.childNodes:
                    if child_r.nodeName == 'w:r':
                        child_dict[num1] = child_r
                        clone = child_r.cloneNode(True)
                        clone_dict[num1] = [clone]
                        for index, value in values.items():
                            if num1 == index:
                                child_t = clone.getElementsByTagName('w:t')[0]
                                str = child_t.firstChild.nodeValue
                                str_split = [0]
                                for v1 in value:
                                    str_split.append(v1[0])
                                    str_split.append(v1[-1] + 1)
                                str_split.append(100000)
                                str_split_con = []
                                str_split_index = []
                                for sp in range(len(str_split) - 1):
                                    index1 = str_split[sp]
                                    index2 = str_split[sp + 1]
                                    str_s = str[index1:index2]
                                    if len(str_s) != 0:
                                        str_split_con.append(str_s)
                                        str_split_index.append([index1, index2])
                                for (xi, x), y in zip(enumerate(str_split_con), str_split_index):
                                    if xi == 0:
                                        clone.getElementsByTagName('w:t')[0].firstChild.replaceData(
                                            offset=0,
                                            count=len(
                                                str),
                                            arg=x)
                                        for vv in value:
                                            if y[0] <= max(vv) and max(vv) < y[-1]:
                                                if len(clone.getElementsByTagName('w:highlight')) == 0:
                                                    node = file.createElement('w:highlight')
                                                    node.setAttribute('w:val', color)
                                                    clone.getElementsByTagName('w:rPr')[0].appendChild(node)
                                                else:
                                                    clone.getElementsByTagName('w:highlight')[-1].setAttribute('w:val',
                                                                                                           color)
                                    else:
                                        clones = child_r.cloneNode(True)

                                        wbr = clones.getElementsByTagName('w:br')
                                        for br in wbr:
                                            clones.removeChild(br)

                                        clones.getElementsByTagName('w:t')[0].firstChild.replaceData(
                                            offset=0,
                                            count=len(
                                                str),
                                            arg=x)
                                        for vv in value:
                                            if y[0] <= max(vv) and max(vv) < y[-1]:
                                                node = file.createElement('w:highlight')
                                                node.setAttribute('w:val', color)
                                                clones.getElementsByTagName('w:rPr')[0].appendChild(node)

                                        for ci, cv in clone_dict.items():
                                            cv.append(clones)

                    num1 += 1

                try:
                    for ci, cv in clone_dict.items():
                        for c in cv:
                            child_p.appendChild(c)

                    for ci, cv in child_dict.items():
                        child_p.removeChild(cv)
                except:
                    print('a death')

    def table_work2(self,child_tbl,num_tbl,table_index,file,color):

        for indexs, values in table_index.items():
            for index1, value1 in values.items():
                if index1 == num_tbl:
                    num_tr = 0
                    for ts in child_tbl.childNodes:
                        for index2, value2 in value1.items():
                            if num_tr == index2:
                                num_tc = 0
                                for tc in ts.childNodes:
                                    for index3, value3 in value2.items():
                                        if num_tc == index3:
                                            num_p = 0
                                            clone_dict = {}
                                            child_dict = {}
                                            for tp in tc.childNodes:
                                                for index4, value4 in value3.items():
                                                    if num_p == index4:
                                                        num_r = 0
                                                        for tr in tp.childNodes:
                                                            if tr.nodeName == 'w:r':
                                                                child_dict[num_r] = tr
                                                                clone = tr.cloneNode(True)
                                                                clone_dict[num_r] = [clone]
                                                                for index5, value5 in value4.items():
                                                                    if num_r == index5:
                                                                        num_tt = 0
                                                                        for tt in tr.childNodes:
                                                                            for index6, value6 in value5.items():
                                                                                if num_tt == index6:
                                                                                    t = str(type(value6[0]))
                                                                                    if "<class 'list'>" == t:
                                                                                        str_split = [0]
                                                                                        for vs in value6:
                                                                                            str_split.append(vs[0])
                                                                                            str_split.append(vs[-1])
                                                                                    else:
                                                                                        str_split = [0]
                                                                                        str_split.append(value6[0])
                                                                                        str_split.append(value6[-1])
                                                                                    strs = tt.childNodes[0].nodeValue
                                                                                    str_split.append(100000)
                                                                                    str_split_con = []
                                                                                    str_split_index = []
                                                                                    for sp in range(len(str_split) - 1):
                                                                                        index1 = str_split[sp]
                                                                                        index2 = str_split[sp + 1]
                                                                                        str_s = strs[index1:index2]
                                                                                        if len(str_s) != 0:
                                                                                            str_split_con.append(str_s)
                                                                                            str_split_index.append(
                                                                                                [index1, index2])
                                                                                    for (xi, x), y in zip(
                                                                                            enumerate(str_split_con),
                                                                                            str_split_index):
                                                                                        if xi == 0:
                                                                                            clone.getElementsByTagName(
                                                                                                'w:t')[0].firstChild. \
                                                                                                replaceData(offset=0,
                                                                                                            count=len(
                                                                                                                strs),
                                                                                                            arg=x)
                                                                                            t = str(type(value6[0]))
                                                                                            if "<class 'list'>" == t:
                                                                                                for vs in value6:
                                                                                                    if y[0] < max(vs) and max(
                                                                                                            vs) <= y[-1]:
                                                                                                        if len(clone.getElementsByTagName(
                                                                                                                        'w:highlight')) == 0:
                                                                                                            node = file.createElement(
                                                                                                                'w:highlight')
                                                                                                            node.setAttribute(
                                                                                                                'w:val',
                                                                                                                color)
                                                                                                            clone.getElementsByTagName(
                                                                                                                'w:rPr')[0].appendChild(
                                                                                                                node)
                                                                                                        else:
                                                                                                            clone.getElementsByTagName(
                                                                                                                'w:highlight')[-1]. \
                                                                                                                setAttribute(
                                                                                                                'w:val',color)
                                                                                            else:
                                                                                                if y[0] < max(value6) and max(
                                                                                                        value6) <= y[-1]:
                                                                                                    if len(
                                                                                                            clone.getElementsByTagName(
                                                                                                                    'w:highlight')) == 0:
                                                                                                        node = file.createElement(
                                                                                                            'w:highlight')
                                                                                                        node.setAttribute(
                                                                                                            'w:val',color)
                                                                                                        clone.getElementsByTagName(
                                                                                                            'w:rPr')[0].appendChild(
                                                                                                            node)
                                                                                                    else:
                                                                                                        clone.getElementsByTagName(
                                                                                                            'w:highlight')[-1].setAttribute(
                                                                                                            'w:val',color)

                                                                                        else:
                                                                                            clones = tr.cloneNode(True)

                                                                                            wbr = clones.getElementsByTagName(
                                                                                                'w:br')
                                                                                            for br in wbr:
                                                                                                clones.removeChild(br)

                                                                                            clones.getElementsByTagName(
                                                                                                'w:t')[0].firstChild. \
                                                                                                replaceData(offset=0,
                                                                                                            count=len(
                                                                                                                strs),
                                                                                                            arg=x)
                                                                                            t = str(type(value6[0]))
                                                                                            if "<class 'list'>" == t:
                                                                                                for vs in value6:
                                                                                                    if y[0] < max(vs) and max(
                                                                                                            vs) <= y[-1]:
                                                                                                        if len(clones.getElementsByTagName(
                                                                                                                        'w:highlight')) == 0:
                                                                                                            node = file.createElement(
                                                                                                                'w:highlight')
                                                                                                            node.setAttribute('w:val',
                                                                                                                color)
                                                                                                            clones.getElementsByTagName(
                                                                                                                'w:rPr')[0].appendChild(
                                                                                                                node)
                                                                                                        else:
                                                                                                            clones.getElementsByTagName(
                                                                                                                'w:highlight')[-1].setAttribute(
                                                                                                                'w:val',color)
                                                                                            else:
                                                                                                if y[0] < max(value6) and max(
                                                                                                        value6) <= y[-1]:
                                                                                                    if len(clone.getElementsByTagName(
                                                                                                                    'w:highlight')) == 0:
                                                                                                        node = file.createElement(
                                                                                                            'w:highlight')
                                                                                                        node.setAttribute('w:val', color)
                                                                                                        clones.getElementsByTagName(
                                                                                                            'w:rPr')[0].appendChild(
                                                                                                            node)
                                                                                                    else:
                                                                                                        clones.getElementsByTagName(
                                                                                                            'w:highlight')[-1].setAttribute(
                                                                                                            'w:val',color)
                                                                                            for ci, cv in clone_dict.items():
                                                                                                cv.append(clones)
                                                                                num_tt += 1
                                                            num_r += 1
                                                for ci, cv in clone_dict.items():
                                                    for c in cv:
                                                        tp.appendChild(c)
                                                for ci, cv in child_dict.items():
                                                    tp.removeChild(cv)

                                                num_p += 1
                                    num_tc += 1
                        num_tr += 1

    def table_work3(self,child_tbl,num_tbl,table_index,file,color):

        for i in table_index:
            if len(i) == 1:
                if i[0] == num_tbl:
                    for ts in child_tbl.childNodes:
                        for tc in ts.childNodes:
                            for tp in tc.childNodes:
                                if tp.nodeName == 'w:tcPr':
                                    if len(tp.getElementsByTagName('w:shd'))== 0:
                                       node = file.createElement('w:shd')
                                       node.setAttribute('w:fill',color)
                                       tp.appendChild(node)
                                    else:
                                       tp.getElementsByTagName('w:shd')[-1]. \
                                           setAttribute('w:fill', color)
            if len(i) == 2:
                if i[0] == num_tbl:
                    num = 0
                    for ts in child_tbl.childNodes:
                        if num == i[1]:
                            for tc in ts.childNodes:
                                for tp in tc.childNodes:
                                    if tp.nodeName == 'w:tcPr':
                                        if len(tp.getElementsByTagName('w:shd'))== 0:
                                           node = file.createElement('w:shd')
                                           node.setAttribute('w:fill',color)
                                           tp.appendChild(node)
                                        else:
                                           tp.getElementsByTagName('w:shd')[-1]. \
                                               setAttribute('w:fill', color)
                        num += 1

    def cdl2diff(self,cdl):

        diff_doc1 = {}
        diff_doc2 = {}
        for (i, v), n in zip(cdl.items(), range(len(cdl))):
            if n % 2 == 0:
                diff_doc1[i] = v
            else:
                diff_doc2[i] = v
        return diff_doc1,diff_doc2

    def diff2cdl(self,diff_words):

        index_list = []
        cdl_add = {}
        for i in range(len(diff_words)):
            if '?' == diff_words[i][0] and '+' in diff_words[i]:
                if diff_words[i - 2][0] == '?':
                    cdl_add[i - 3] = diff_words[i - 3]
                    index_list.append(i - 3)
                else:
                    cdl_add[i - 2] = diff_words[i - 2]
                    index_list.append(i - 2)
                cdl_add[i - 1] = diff_words[i - 1]
                index_list.append(i - 1)
        cdl_delete = {}
        for i in range(len(diff_words)):
            if '?' == diff_words[i][0] and '-' in diff_words[i]:
                cdl_delete[i - 1] = diff_words[i - 1]
                cdl_delete[i + 1] = diff_words[i + 1]
                index_list.append(i - 1)
                index_list.append(i + 1)
        cdl_update = {}
        for i in range(len(diff_words)):
            if '?' == diff_words[i][0] and '^' in diff_words[i]:
                cdl_update[i - 1] = diff_words[i - 1]
                index_list.append(i - 1)
        cdl_other = {}
        for i in range(len(diff_words)):
            if i not in index_list and diff_words[i][0] != '?':
                cdl_other[i] = diff_words[i]

        return  cdl_delete,cdl_add,cdl_update,cdl_other

    def cdl2index(self,flag_all,diff,
        index1, value1, index2, value2, table_indexs,table_files):
        for (i1, v1), (i2, v2) in zip(value1.items(), value2.items()):
            num_v = 0
            for v1s, v2s in zip(v1, v2):
                if v1s != v2s:
                    value_diff = diff.compare(v1s, v2s)
                    diff_words = list(value_diff)
                    value_diff.close()
                    cdl_delete, cdl_add, cdl_update, cdl_other \
                                            = self.diff2cdl(diff_words)
                    diff_doc1, diff_doc2 = self.cdl2diff(cdl_delete)
                    for (n1, m1), (n2, m2) in zip(diff_doc1.items(), diff_doc2.items()):
                        ss = difflib.SequenceMatcher(lambda x: x == " ", m1[2:], m2[2:])
                        for (tag, i1_1, i2_1, d1_1, d2_1) in ss.get_opcodes():
                            if tag == 'delete':
                                # print(("%7s file1[%d:%d] (%s) file2[%d:%d] (%s)" %
                                #        (tag, i1_1, i2_1, m1[2:][i1_1:i2_1],
                                #         d1_1, d2_1, m2[2:][d1_1:d2_1])))
                                for p, q in table_indexs[0].items():
                                    if index1 == p:
                                        for p1, q1 in q.items():
                                            if p1 == i1:
                                                for (p2, q2), np in zip(q1.items(), range(len(q1))):
                                                    if np == num_v:
                                                        flag2 = i2_1
                                                        flag2_1 = 0
                                                        for p3, q3 in q2.items():
                                                            for p4, q4 in q3.items():
                                                                for p5, q5 in q4.items():
                                                                    if len(q5) >= flag2 and flag2 > 0:
                                                                        table_files[0][0][flag_all] = \
                                                                            {p: {p1: {p2: {p3: {p4: {p5:
                                                                            [i1_1 - flag2_1,i2_1 - flag2_1]}}}}}}
                                                                    flag2_1 += len(q5)
                                                                    flag2 -= len(q5)
                                flag_all += 1

                    diff_doc1, diff_doc2 = self.cdl2diff(cdl_add)
                    for (n1, m1), (n2, m2) in zip(diff_doc1.items(), diff_doc2.items()):
                        ss = difflib.SequenceMatcher(lambda x: x == " ", m1[2:], m2[2:])
                        for (tag, i1_1, i2_1, d1_1, d2_1) in ss.get_opcodes():
                            if tag == 'insert':
                                for p, q in table_indexs[1].items():
                                    if index2 == p:
                                        for p1, q1 in q.items():
                                            if p1 == i1:
                                                for (p2, q2), np in zip(q1.items(), range(len(q1))):
                                                    if np == num_v:
                                                        flag2 = d2_1
                                                        flag2_1 = 0
                                                        for p3, q3 in q2.items():
                                                            for p4, q4 in q3.items():
                                                                for p5, q5 in q4.items():
                                                                    if len(q5) >= flag2 and flag2 > 0:
                                                                        table_files[1][0][flag_all] = \
                                                                            {p: {p1: {p2: {p3: {p4: {p5:
                                                                            [d1_1 - flag2_1,d2_1 - flag2_1]}}}}}}
                                                                    flag2_1 += len(q5)
                                                                    flag2 -= len(q5)
                                flag_all += 1

                    diff_doc1, diff_doc2 = self.cdl2diff(cdl_update)
                    for (n1, m1), (n2, m2) in zip(diff_doc1.items(), diff_doc2.items()):
                        ss = difflib.SequenceMatcher(lambda x: x == " ", m1[2:], m2[2:])
                        for (tag, i1_1, i2_1, d1_1, d2_1) in ss.get_opcodes():
                            if tag == 'replace':
                                for p, q in table_indexs[0].items():
                                    if index1 == p:
                                        for p1, q1 in q.items():
                                            if p1 == i1:
                                                for (p2, q2), np in zip(q1.items(), range(len(q1))):
                                                    if np == num_v:
                                                        flag2 = d2_1
                                                        flag2_1 = 0
                                                        for p3, q3 in q2.items():
                                                            for p4, q4 in q3.items():
                                                                for p5, q5 in q4.items():
                                                                    if len(q5) >= flag2 and flag2 > 0:
                                                                        table_files[0][1][flag_all] = \
                                                                            {p: {p1: {p2: {p3: {p4: {p5:
                                                                            [i1_1 - flag2_1,i2_1 - flag2_1]}}}}}}
                                                                    flag2_1 += len(q5)
                                                                    flag2 -= len(q5)
                                for p, q in table_indexs[1].items():
                                    if index2 == p:
                                        for p1, q1 in q.items():
                                            if p1 == i1:
                                                for (p2, q2), np in zip(q1.items(), range(len(q1))):
                                                    if np == num_v:
                                                        flag2 = d2_1
                                                        flag2_1 = 0
                                                        for p3, q3 in q2.items():
                                                            for p4, q4 in q3.items():
                                                                for p5, q5 in q4.items():
                                                                    if len(q5) >= flag2 and flag2 > 0:
                                                                        table_files[1][1][flag_all] = \
                                                                            {p: {p1: {p2: {p3: {p4: {p5:
                                                                            [d1_1 - flag2_1,d2_1 - flag2_1]}}}}}}
                                                                    flag2_1 += len(q5)
                                                                    flag2 -= len(q5)
                                flag_all += 1

                    for n, m in cdl_other.items():
                        if m[0] == '-':
                            for p, q in table_indexs[0].items():
                                if index1 == p:
                                    for p1, q1 in q.items():
                                        if p1 == i1:
                                            for (p2, q2), np in zip(q1.items(), range(len(q1))):
                                                if np == num_v:
                                                    tr_dict = {}
                                                    tr_con = {}
                                                    for p3, q3 in q2.items():
                                                        tc_dict = {}
                                                        tc_con = {}
                                                        for p4, q4 in q3.items():
                                                            for p5, q5 in q4.items():
                                                                tc_dict[p4] = {p5: [0, len(q5)]}
                                                                tc_con[p4] = {p5: q5}
                                                            tr_dict[p3] = tc_dict
                                                            tr_con[p3] = tc_con
                                                    table_files[0][0][flag_all] = \
                                                                    {p: {p1: {p2: tr_dict}}}
                            flag_all += 1
                        else:
                            for p, q in table_indexs[1].items():
                                if index2 == p:
                                    for p1, q1 in q.items():
                                        if p1 == i2:
                                            for (p2, q2), np in zip(q1.items(), range(len(q1))):
                                                if np == num_v:
                                                    tr_dict = {}
                                                    tr_con = {}
                                                    for p3, q3 in q2.items():
                                                        tc_dict = {}
                                                        tc_con = {}
                                                        for p4, q4 in q3.items():
                                                            for p5, q5 in q4.items():
                                                                tc_dict[p4] = {p5: [0, len(q5)]}
                                                                tc_con[p4] = {p5: q5}
                                                            tr_dict[p3] = tc_dict
                                                            tr_con[p3] = tc_con
                                                    table_files[1][0][flag_all] = \
                                                        {p: {p1: {p2: tr_dict}}}
                            flag_all += 1
                num_v += 1

        return table_files, flag_all