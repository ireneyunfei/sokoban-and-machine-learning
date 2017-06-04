import os
import xml.etree.ElementTree as ET
import pandas as pd


class Info(object):
    varname = ['id', '性别', '出生日期', '测试日期', '姓名']

    def __init__(self, dirname):
        root = ET.parse(dirname + os.path.sep + "用户信息.xml").getroot()
        varname = ['id'] + [x.tag for x in root[1][0]]
        if len(varname) > len(Info.varname):
            Info.varname = varname
        self.data = [x.text for x in root[1][0]]

    def export_str(self):
        return '\t'.join(self.data) + '\n'


class Gene(object):
    common_varnames = []

    def __init__(self, dirname):
        # This list contains the subject-level data. dirname
        self.data = [dirname]
        # is the id of each subject.
        root = ET.parse(dirname + os.path.sep + "基因实验室.xml").getroot()
        common_varnames = ['id'] + \
            [x.tag for x in root[0]][1:]  # start from 1 to
        # omit the first variable the name of the game
        if Gene.common_varnames != []:
            assert Gene.common_varnames == common_varnames
        if Gene.common_varnames == []:
            Gene.common_varnames = common_varnames
        self.data.extend([x.text for x in root[0]][1:])
        self.guanlist = [GeneGuan(guan_element) for guan_element in root[1]]
        # guanlist contains the data of each guan.

    def export_str(self):
        sub_strlist = []
        for guan in self.guanlist:
            sub_strlist.append(guan.export_str(self.data))
        return ''.join(sub_strlist)


class GeneGuan(object):
    guan_varnames = []
    max_exp = 0
    max_ctrl = 0

    def __init__(self, guan_element):
        guan_varnames = ['关号'] + [x.tag for x in guan_element]
        # guan_varnames = guan_varnames[:-5] + [guan_varnames[-3]]
        if GeneGuan.guan_varnames != []:
            assert guan_varnames[2:] == GeneGuan.guan_varnames[2:]
        if GeneGuan.guan_varnames == []:
            GeneGuan.guan_varnames = guan_varnames
        guan_num = guan_element.tag
        if len(guan_num) == 5:
            guan_num = str(100 - int(guan_num[-2]))  # 用99 98 表示引导关卡
        else:
            guan_num = guan_num[1:-1]
        int(guan_num)
        guan_data = [guan_num] + [x.text.strip() for x in guan_element]
        # guan_data = guan_data[:-5] + [guan_data[-3]]
        guan_data = list(
            map(lambda x: 'NA' if x == '' else x, guan_data))
        self.guan_data = guan_data
        exp_time_str = guan_element[-5].text
        if exp_time_str.strip() == '':
            exp_time_ls = []
        else:
            exp_time_ls = exp_time_str.split('@')
            exp_time_ls = [x.split('~')[0] for x in exp_time_ls]
        # 引导第1关中，这3个变量都是 missing，因此手动赋值跳出。
        if guan_element.tag == '引导第1关':
            self.ctrl_path_ls = []
            self.ctrl_time_ls = []
            self.exp_path_ls = []
            self.exp_time_ls = exp_time_ls
            return None
        ctrl_time_str = guan_element[-4].text
        if ctrl_time_str.strip() == '':
            ctrl_time_ls = []
        else:
            ctrl_time_ls = ctrl_time_str.split('@')
            ctrl_time_ls = [x.split('~')[0] for x in ctrl_time_ls]
        exp_path_str = guan_element[-2].text
        for i in range(10):
            exp_path_str = exp_path_str.replace(str(i), '')
        if exp_path_str.strip() == '':
            exp_path_ls = []
        else:
            exp_path_ls = exp_path_str.split('&')[:-1]
        ctrl_path_str = guan_element[-1].text
        for i in range(10):
            ctrl_path_str = ctrl_path_str.replace(str(i), '')
        if ctrl_path_str.strip() == '':
            ctrl_path_ls = []
        else:
            ctrl_path_ls = ctrl_path_str.split('&')[:-1]
        if guan_element.tag[:2] != '引导':
            assert len(ctrl_path_ls) == len(ctrl_time_ls)
            assert len(exp_path_ls) == len(exp_time_ls)
        self.ctrl_path_ls = ctrl_path_ls
        self.ctrl_time_ls = ctrl_time_ls
        self.exp_path_ls = exp_path_ls
        self.exp_time_ls = exp_time_ls
        GeneGuan.max_exp = max((GeneGuan.max_exp, len(exp_path_ls)))
        GeneGuan.max_ctrl = max((GeneGuan.max_ctrl, len(ctrl_path_ls)))

    def export_str(self, subj_data):
        exp_path_nas = ['NA'] * (GeneGuan.max_exp - len(self.exp_path_ls))
        ctrl_path_nas = ['NA'] * (GeneGuan.max_ctrl - len(self.ctrl_path_ls))
        exp_time_nas = ['NA'] * (GeneGuan.max_exp - len(self.exp_time_ls))
        ctrl_time_nas = ['NA'] * (GeneGuan.max_ctrl - len(self.ctrl_time_ls))
        outstrls = subj_data + self.guan_data + self.exp_path_ls + \
            exp_path_nas + self.exp_time_ls + exp_time_nas + self.ctrl_path_ls + \
            ctrl_path_nas + self.ctrl_time_ls + ctrl_time_nas
        return '\t'.join(outstrls) + '\n'


class Sokoban(object):
    common_varnames = ['id', '游戏总用时']

    def __init__(self, dirname):
        self.data = [dirname]  # id
        root = ET.parse(dirname + os.path.sep + "推箱子.xml").getroot()
        self.data.append(root[0][0].text)  # This is for 游戏总用时
        root = root[1:]
        # To store the data from each guan
        self.guanlist = [SokobanGuan(guan_element) for guan_element in root]

    def export_str(self):
        '''
        This function export the data of this subject. It sends the subject-level
        data to the export function of class SokobanGuan, which will add them at the
        beginning of guan data. It receives the returned string of each guan, and
        then join them into a block (multiple lines of string), which has the same
        subject-level data and each guan data.
        '''
        sub_strlist = []
        for guan in self.guanlist:
            sub_strlist.append(guan.export_str(self.data))
        return ''.join(sub_strlist)


class Timeineqdir(Exception):
    def __init__(self, lentime, lendir):
        Exception.__init__(self)
        self.lentime = lentime
        self.lendir = lendir


class SokobanGuan(object):
    max_path = 0
    guan_varnames = ['关号', '本关用时', ' 移动路径', '路径时间',
                     '第一次推动箱子前的时间', '本关结果', '推入几个箱子']

    def __init__(self, guan_element):
        self.na = 0
        # if this guan is empty, then skip it
        if guan_element[0].text.strip() == '':
            self.na = 1
            return None
        self.guan_data = [guan_element.tag[1:-1]]  # 关编号
        self.guan_data.append(guan_element[0].text)  # 本关用时
        pathdir_str = guan_element[1].text.strip()
        if pathdir_str == '':
            pathdir_str = 'NA'
            self.pathdir_ls = []
        else:
            self.pathdir_ls = pathdir_str.split(
                ',')[:-1]  # attention: 这里的分割符是英文","
        self.guan_data.append(pathdir_str)

        pathtime_str = guan_element[2].text.strip()  # 路径时间
        if pathtime_str == '':
            pathtime_str = 'NA'
            self.pathtime_ls = []
        else:
            self.pathtime_ls = pathtime_str.split(
                '，')[:-1]  # attention: 这里的分割符是中文"，" -1 是为了删掉最后的空字符串
            self.pathtime_ls = [x[:-1] for x in self.pathtime_ls]
        self.guan_data.append(pathtime_str)

        first_push_time = guan_element[4].text  # 第一次推动箱子时间
        if first_push_time.strip() == '':
            first_push_time = 'NA'
        else:
            first_push_time = first_push_time[:-2]  # 删除掉最后的'秒,'
        self.guan_data.append(first_push_time)
        result_string = guan_element[5].text  # 本关结果
        result_flag = result_string.split('：')[0]
        self.guan_data.append(result_flag)  # 步数过多、超时、放弃、成功。其中步数过多应该与成功合并。
        if result_string.find('：') == -1:
            boxes_comp = 'NA'
        else:
            boxes_comp = result_string.split('：')[1][4]
        self.guan_data.append(boxes_comp)  # 完成的箱子数目

        try:
            if len(self.pathtime_ls) != len(self.pathdir_ls):
                raise Timeineqdir(len(self.pathtime_ls), len(self.pathdir_ls))
        except Timeineqdir as ti:
            print('The length of pathtime list and pathdir list is not equal.')
            print('The former length is {}, while the latter is {}'.format(
                ti.lentime, ti.lendir))
        SokobanGuan.max_path = max(
            (SokobanGuan.max_path, len(self.pathdir_ls)))

    def export_str(self, subj_data):
        '''
        This function receives the subject-level data, adds those data to the
        beginning of the guan-level data, and then returns data as a string delimited
        by tab in one line with '\n'.
        '''
        if self.na == 1:
            return ''
        # if the current guan is NA, then return empty string.
        nas = ['NA'] * (SokobanGuan.max_path - len(self.pathdir_ls))
        outputdata = subj_data + self.guan_data + \
            self.pathtime_ls + nas + self.pathdir_ls + nas
        return '\t'.join(outputdata) + '\n'


class Tower(object):
    common_varnames = ['id']

    def __init__(self, dirname):
        self.data = [dirname]
        root = ET.parse(dirname + os.path.sep + "伦敦塔.xml").getroot()
        self.guanlist = [TowerGuan(x) for x in root[1]]

    def export_str(self):
        sub_strlist = []
        for guan in self.guanlist:
            sub_strlist.append(guan.export_str(self.data))
        return ''.join(sub_strlist)


class TowerGuan(object):
    guan_varnames = ["题库号", "关号", "游戏结果", "单局时间", "游戏路径", "使用步骤"]
    max_step = 0

    def __init__(self, guan_element):
        guan_data = [x.text.strip() for x in guan_element]
        # guan_data = guan_data[:4] + guan_data[5:]
        guan_data = list(map(lambda x: 'NA' if x == '' else x, guan_data))
        self.guan_data = guan_data
        path_str = guan_element[4].text.strip()
        if path_str == '':
            self.path_ls1 = []
            self.path_ls2 = []
            self.path_ls3 = []
        else:
            path_ls = path_str.split('-')
            self.path_ls1 = path_ls[::3]
            self.path_ls2 = path_ls[1::3]
            self.path_ls3 = path_ls[2::3]
            assert len(path_ls) % 3 == 0
            TowerGuan.max_step = max((TowerGuan.max_step, len(self.path_ls1)))

    def export_str(self, subj_data):
        nas = ['NA'] * (TowerGuan.max_step - len(self.path_ls1))
        outstrls = subj_data + self.guan_data + self.path_ls1 + \
            nas + self.path_ls2 + nas + self.path_ls3 + nas
        return '\t'.join(outstrls) + '\n'


class CTC(object):
    common_varnames = ['id']

    def __init__(self, dirname):
        self.data = [dirname]
        root = ET.parse(dirname + os.path.sep + "CTC.xml").getroot()
        self.guanlist = [CTCGuan(x) for x in root[1]]

    def export_str(self):
        sub_strlist = [x.export_str(self.data) for x in self.guanlist]
        return ''.join(sub_strlist)


class CTCGuan(object):
    max_step = 0
    guan_varnames = ["关号", "本关用时", "完成期", "操作期", "潜伏期", "移动路径", "步数", "本关结果"]

    def __init__(self, guan_element):
        guan_varnames = [x.tag for x in guan_element]
        # guan_varnames = guan_varnames[:3] + guan_varnames[6:]
        self.guan_varnames = guan_varnames
        guan_data = [x.text.strip() for x in guan_element]
        guan_data[0] = guan_data[0][1:-1]
        int(guan_data[0])
        guan_data = list(map(lambda x: 'NA' if x == '' else x, guan_data))
        # guan_data = guan_data[:3] + guan_data[6:]
        guan_data[1:3] = list(
            map(lambda x: x[:-1] if x[-1] == '秒' else x, guan_data[1:3]))
        self.guan_data = guan_data
        op_str = guan_element[3].text
        if op_str.strip() == '':
            self.op_ls = []
        else:
            self.op_ls = op_str.split('+')
            self.op_ls = [x[:-1] for x in self.op_ls]
        po_str = guan_element[4].text
        if po_str.strip() == '':
            self.po_ls = []
        else:
            self.po_ls = po_str.split('+')
            self.po_ls = [x[:-1] for x in self.po_ls]
        path_str = guan_element[5].text
        if path_str.strip() == '':
            self.path_ls, self.path_ls1, self.path_ls2, self.path_ls3 = [], [], [], []
        else:
            self.path_ls = path_str.split('→')
            self.path_ls1 = [x[:2] for x in self.path_ls]
            self.path_ls2 = [x[2:4] for x in self.path_ls]
            self.path_ls3 = [x[4:] for x in self.path_ls]
        assert len(self.po_ls) == len(self.op_ls) and len(
            self.path_ls) == len(self.po_ls)
        CTCGuan.max_step = max((CTCGuan.max_step, len(self.po_ls)))

    def export_str(self, subj_data):
        nas = ['NA'] * (CTCGuan.max_step - len(self.path_ls))
        outstrls = subj_data + self.guan_data + self.op_ls + nas + self.po_ls + \
            nas + self.path_ls1 + nas + self.path_ls2 + nas + self.path_ls3 + nas
        return '\t'.join(outstrls) + '\n'


def write_sokoban(sokobans):
    if os.path.exists('Sokoban.txt'):
        os.remove('Sokoban.txt')
    f = open('Sokoban.txt', 'w+', encoding='utf-8')
    steptime = ['steptime{}'.format(x)
                for x in range(1, SokobanGuan.max_path + 1)]
    stepdir = ['stepdir{}'.format(x)
               for x in range(1, SokobanGuan.max_path + 1)]
    f.write('\t'.join(Sokoban.common_varnames +
                      SokobanGuan.guan_varnames + steptime + stepdir))
    f.write('\n')
    sokoban_strls = []
    for sokoban in sokobans:
        sokoban_strls.append(sokoban.export_str())
    f.write(''.join(sokoban_strls))
    f.close()
    long2wide('Sokoban.txt', Sokoban.common_varnames,
              SokobanGuan.guan_varnames)


def write_gene(genes):
    if os.path.exists('Gene.txt'):
        os.remove('Gene.txt')
    f = open('Gene.txt', 'w+', encoding='utf-8')
    exptime = ['exploring-step time{}'.format(x)
               for x in range(1, GeneGuan.max_exp + 1)]
    expdir = ['exploring-step move{}'.format(x)
              for x in range(1, GeneGuan.max_exp + 1)]
    ctrltime = ['ctrl-step time{}'.format(x)
                for x in range(1, GeneGuan.max_ctrl + 1)]
    ctrldir = ['ctrl-step move{}'.format(x)
               for x in range(1, GeneGuan.max_ctrl + 1)]
    f.write('\t'.join(Gene.common_varnames +
                      GeneGuan.guan_varnames + expdir + exptime +
                      ctrldir + ctrltime))
    f.write('\n')
    gene_strls = []
    for gene in genes:
        gene_strls.append(gene.export_str())
    f.write(''.join(gene_strls))
    f.close()
    long2wide('Gene.txt', Gene.common_varnames, GeneGuan.guan_varnames)


def write_tower(towers):
    if os.path.exists('Tower.txt'):
        os.remove('Tower.txt')
    f = open('Tower.txt', 'w+', encoding='utf-8')
    time1name = ['时间1_{}'.format(x) for x in range(1, TowerGuan.max_step + 1)]
    time2name = ['时间2_{}'.format(x) for x in range(1, TowerGuan.max_step + 1)]
    stepname = ['操作_{}'.format(x) for x in range(1, TowerGuan.max_step + 1)]
    f.write('\t'.join(Tower.common_varnames +
                      TowerGuan.guan_varnames + time1name + time2name + stepname))
    f.write('\n')
    tower_strls = [x.export_str() for x in towers]
    f.write(''.join(tower_strls))
    f.close()
    long2wide('Tower.txt', Tower.common_varnames, TowerGuan.guan_varnames)


def write_info(infos):
    if os.path.exists('Info.txt'):
        os.remove('Info.txt')
    f = open('Info.txt', 'w+', encoding='utf-8')
    f.write('\t'.join(Info.varname))
    f.write('\n')
    info_strls = [x.export_str() for x in infos]
    f.write(''.join(info_strls))
    f.close()


def write_ctc(ctcs):
    if os.path.exists('CTC.txt'):
        os.remove('CTC.txt')
    f = open('CTC.txt', 'w+', encoding='utf-8')
    opname = ['操作期{}'.format(x) for x in range(1, CTCGuan.max_step + 1)]
    poname = ['潜伏期{}'.format(x) for x in range(1, CTCGuan.max_step + 1)]
    path1name = ['路径前{}'.format(x) for x in range(1, CTCGuan.max_step + 1)]
    path2name = ['路径颜色{}'.format(x) for x in range(1, CTCGuan.max_step + 1)]
    path3name = ['路径后{}'.format(x) for x in range(1, CTCGuan.max_step + 1)]
    f.write('\t'.join(CTC.common_varnames + CTCGuan.guan_varnames +
                      opname + poname + path1name + path2name + path3name))
    f.write('\n')
    ctc_strls = [x.export_str() for x in ctcs]
    f.write(''.join(ctc_strls))
    f.close()
    long2wide('CTC.txt', CTC.common_varnames, CTCGuan.guan_varnames)


def long2wide(file, common_varnames, guan_varnames):
    dt = pd.read_csv(file, sep='\t')
    num_variable = len(common_varnames) + len(guan_varnames)
    dt = dt.iloc[:, :num_variable]
    dt_com = dt.loc[:, common_varnames]
    dt_com = dt_com.iloc[~dt_com.duplicated().values, :]
    dt_guan = dt.loc[:, ['id'] + guan_varnames]
    dt_wide = dt_guan.pivot(index='id', columns='关号')
    guannum = len(dt_wide.columns.levels[1])
    reorder_i = []
    varlabel = dt_wide.columns.levels[0]
    for j in range(guannum):
        reorder_i = reorder_i + [j+guannum*i for i in range(len(varlabel))]
    dt_wide = dt_wide.iloc[:,reorder_i].reset_index()
    wide = pd.merge(dt_com, dt_wide, on='id').set_index('id')
    
    wide.to_csv('{}_wide.txt'.format(os.path.splitext(file)[0]), sep='\t')
    return None



dirnames = os.listdir()
dirnames = list(filter(os.path.isdir, dirnames))

sokobans, genes, towers, ctcs, infos = [], [], [], [], []
print('###############################################################')
for dirname in dirnames:
    if os.path.exists(dirname + os.path.sep + "基因实验室.xml"):
        genes.append(Gene(dirname))
        print('Folder {}: Gene detected.'.format(dirname), end='\t')
    else:
        print('Folder {}: Gene not found.'.format(dirname), end='\t')
    if os.path.exists(dirname + os.path.sep + "CTC.xml"):
        ctcs.append(CTC(dirname))
        print('CTC detected.'.format(dirname), end='\t')
    else:
        print('CTC not found.'.format(dirname), end='\t')
    if os.path.exists(dirname + os.path.sep + "推箱子.xml"):
        sokobans.append(Sokoban(dirname))
        print('Sokoban detected.'.format(dirname), end='\t')
    else:
        print('Sokoban not found.'.format(dirname), end='\t')
    if os.path.exists(dirname + os.path.sep + "伦敦塔.xml"):
        towers.append(Tower(dirname))
        print('Tower detected.'.format(dirname), end='\t')
    else:
        print('Tower not found.'.format(dirname), end='\t')
    if os.path.exists(dirname + os.path.sep + "用户信息.xml"):
        infos.append(Info(dirname))
        print('UserInfo detected.'.format(dirname), end='\n')
    else:
        print('UserInfo not found.'.format(dirname), end='\n')
        
print('###############################################################')
print("# Folders: {}".format(len(dirnames)))
print('Found: Gene:{}, CTC:{},Sokoban:{}, Tower:{}, UserInfo:{}'.format(
    len(genes), len(ctcs), len(sokobans), len(towers), len(infos)))
print('###############################################################')
write_sokoban(sokobans)
write_gene(genes)
write_tower(towers)
write_info(infos)
write_ctc(ctcs)

