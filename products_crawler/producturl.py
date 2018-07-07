#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import json
import urllib
import re
import time
import random
import os


######### CODE COPIED FROM URL-CLASSIFICATION project ##############

global feature_index_map 
feature_index_map = {} # feature key => key index ,index start from 0

global dir_name_index_map 
dir_name_index_map = {} # feature key => key index ,index start from 0

global doc_name_index_map 
doc_name_index_map = {} # feature key => key index ,index start from 0

global ext_name_index_map 
ext_name_index_map = {} # feature key => key index ,index start from 0

global params_name_index_map 
params_name_index_map = {} # feature key => key index ,index start from 0

global union_name_score_map
union_name_score_map = {} # feature key => score  ,index id 9 

global dir_name_score_map
dir_name_score_map = {} # feature key => score  ,index id 11

global res_name_score_map
res_name_score_map = {} # feature key => score  ,index id 12

global para_name_score_map
para_name_score_map = {} # feature key => score  ,index id 13

global para_value_score_map
para_value_score_map = {} # feature key => score  ,index id 14

global resname_digitlen_score_map
resname_digitlen_score_map = {} # feature key => score  ,index id 17

global paravalue_digitlen_score_map
paravalue_digitlen_score_map = {} # feature key => score  ,index id 17

global tmp_result_map
tmp_result_map = {} # feature key => score  ,index id 17


IS_NORMALIZTION = 1

infoid_params_name_list = ['aid','newsid','id','docid','itemid','tid']
indexid_params_name_list\
=['pageid','catid','cateid','typeid','sortid','classid','fid','c_id','class_id','columnid','Channelid','subid']


def max_continuity_digit(test_str):
    max_continuity_digit = 0
    num_len = 0
    for c in test_str:
        if c.isdigit():
            num_len += 1
        else :
            max_continuity_digit = max_continuity_digit if max_continuity_digit > num_len else num_len
            num_len = 0
    max_continuity_digit = max_continuity_digit if max_continuity_digit > num_len else num_len
    return max_continuity_digit 

#TODO 
def is_contain_date_string(path):
    dir_names = path.split('/')
    is_date_string = 0
    #"%Y%m%d","%Y-%m-%d",%Y/%m/%d,%Y%m/%d,2015-12/30/,2015/1230,/2015/12-30/
    #/detail_2015_12/29/,
    for dir_name in dir_names :
        if not dir_name.startswith('20'):
            continue
        tmp_date_str = dir_name[:6]
        try: 
            time.strptime(tmp_date_str,'%Y%m')
            is_date_string = 1
            break
        except Exception as e: 
            pass
        tmp_date_str = dir_name[:7]
        try: 
            time.strptime(tmp_date_str,'%Y-%m')
            is_date_string = 1
            break
        except Exception as e: 
            pass

    return is_date_string

def is_exist_doc_name(dir_names):
    value = 0
    n = len(dir_names)
    if n > 0 and dir_names[n-1] == '':
        value = -1
        if n > 1 and dir_names[n-2].isdigit():
            value = 1 
    '''
    if n > 0 and dir_names[n-1] == '':
        value = -1
    else:
        value = 1'''
    return value

def calc_paramter_name( query):
    return 0

    # just load different type score from conf/feature_url.txt
def make_key_rate(conf_file,line_key ):
    f = open(conf_file,'r',errors='ignore')
    conf_start = False
    conf_type_name = '' 
    key_rate_map = {}
    for l in f.readlines():
        l = l.strip()
        if l.startswith('['):
            conf_start = True
            conf_type_name = l[1:len(l)-1]
            continue
        if not conf_type_name.startswith(line_key) :
            continue
        arr_str = l.split()
        if len(arr_str)!= 3 :
            continue
        key_rate_map[arr_str[2]] = (float("%.6f"  % (float(arr_str[0]) )),float("%.6f"  %  (float(arr_str[1]) )))
        total_score =  float(arr_str[0]) +   float(arr_str[1])
        #key_rate_map[arr_str[2]] = (float("%.6f"  % (float(arr_str[0]) /total_score)) ,float("%.6f"  % (float(arr_str[1]) /total_score)))
    return key_rate_map

    
def path_name_keyword(dir_names):
    index_prefix_key_list = ['index','category','list','search']
    info_prefix_key_list = ['detail','content','system','news','article']
    info_key_list = ['a']
#TODO add moew keyword
    file_name =  dir_names[len(dir_names)-1] 
    value = 0 
    for dir_name in dir_names:
        if dir_name in info_key_list :
            value = 1
            break
        for tmp_key in index_prefix_key_list :
            if dir_name.startswith(tmp_key):
                value = -1 
                break
        if value != 0 :
            break
        for tmp_key in info_prefix_key_list :
            if dir_name.startswith(tmp_key):
                value = 1 
                break
        if value != 0 :
            break
    return value 

    
def classify_doc_type(path):
    #info_key_list = ['id','','shtml','shtm','jhtml']
    #index_key_list = ['fid','catid','shtml','shtm','jhtml']
    dir_names = path.split('/')

    index_key_list = ['php','aspx','jsp','do']
    info_key_list = ['html','htm','shtml','shtm','jhtml']
    ext_name =  dir_names[len(dir_names)-1] 
    if '.' in ext_name:
        ext_name = ext_name[ext_name.rfind('.')+1:]
    else:
        ext_name = ''
    result_type = 0
    if ext_name != '':
        if ext_name in info_key_list :
            result_type = 1
        elif ext_name in index_key_list:
            result_type = -1
    return result_type

    # 0 . paramters nums 
def calc_paramter_number(query_str):
    if query_str == '':
        return 0
    query_params = query_str.split('&')
    max_paramter_num = 6
    if IS_NORMALIZTION :
        return "%.2f" % (float(len(query_params))  / max_paramter_num)
    else:
        return len(query_params)
    
    # 2 . all dir names chars length 
def calc_dirnames_length(dir_names):
    value = 0 
    if  len(dir_names)<3:
        return value 
    for i in range (1, len(dir_names) - 1):
        value += len(dir_names[i])
    if IS_NORMALIZTION :
        return "%.2f" % ( float( value) / 30)
    else:
        return value

    # 3 . average char length ???? 
def average_dirnames_length(dir_names):
    value = 0 
    if  len(dir_names)<3:
        return value 
    for i in range (1, len(dir_names) - 1):
        value += len(dir_names[i])

    if IS_NORMALIZTION :
        return "%.2f" % ( float( value)/(len(dir_names)-2 )/ 10)
    else:
        return "%.2f" % ( float( value)/(len(dir_names)-2 ))

    # 4. doc type judeyment? static or dynamic pages
def is_dynamic_page(query):
    if query is not None and query != '':
        return 1
    return 0

    # 5. whether the page is default page??
def is_default_page(dir_names):
    dafault_keyword = ['index','default']
    if len(dir_names) > 0 :
        file_name =  dir_names[len(dir_names)-1]
        if '.' in file_name:
            file_name = file_name[:file_name.rfind('.')]
        if file_name in dafault_keyword:
            return 1
    return 0

    
    # 6. the resource file name is digit ?
def is_digit_filename(dir_names,query):
    file_name = ''
    if len(dir_names) > 0 :
        file_name =  dir_names[len(dir_names)-1]
        if '.' in file_name:
            file_name = file_name[:file_name.rfind('.')]
    num = len(file_name)
    value = 0
    if num > 0 and file_name.isdigit() :
        value = 0.5
        if query is not None and query != '':
            value += 0.1
        if num > 4 :
            value += 0.4
        elif num > 3:
            value += 0.3
        elif num <= 3:
            value += 0.1
    return value 

    # 7  is contain date format for resource name 
def is_match_date_filename( file_name):
    value = 0
    #"%Y%m%d","%Y-%m-%d",%Y/%m/%d,%Y%m/%d,2015-12/30/,2015/1230,/2015/12-30/
    if '.' in file_name:
        file_name = file_name[:file_name.rfind('.')]
    if len(file_name) < 6 :
        return 0
    max_continuity_digit = 0
    num_len = 0
    for c in file_name:
        if c.isdigit():
            num_len += 1
        else :
            max_continuity_digit = max_continuity_digit if max_continuity_digit > num_len else num_len
            num_len = 0
    max_continuity_digit = max_continuity_digit if max_continuity_digit > num_len else num_len
    if max_continuity_digit  < 2 :
        return 0
    
    for i in range (0,len(file_name)-7):
        if file_name[i] == '2' and file_name[i+1] == '0' and \
            (file_name[i+2] == '0' or file_name[i+2] == '1') :
            if (i + 8) > len(file_name):
                break
            tmp_date_str = file_name[i:i+8]
            try: 
                time.strptime(tmp_date_str,'%Y%m%d')
                value = 1
                break
            except Exception as e: 
                pass
            tmp_date_str = file_name[i:10]
            try: 
                time.strptime(tmp_date_str,'%Y-%m-%d')
                value = 1
                break
            except Exception as e: 
                pass
            tmp_date_str = file_name[i:10]
            try: 
                time.strptime(tmp_date_str,'%Y_%m_%d')
                value = 1
                break
            except Exception as e: 
                pass
    return value
            
    # 8  is contain date format for dir name 
def is_match_date_dirnames( dir_names):
    dir_str = ''.join(dir_names)
    value = 0
    #"%Y%m%d","%Y-%m-%d",%Y/%m/%d,%Y%m/%d,2015-12/30/,2015/1230,/2015/12-30/
    if len(dir_str) < 6 :
        return 0
    for i in range (0,len(dir_str)-5):
        if dir_str[i] == '2' and dir_str[i+1] == '0' and \
            (dir_str[i+2] == '0' or dir_str[i+2] == '1') :
            if (i + 5) > len(dir_str):
                break
            tmp_date_str = dir_str[i:i+6]
            try: 
                time.strptime(tmp_date_str,'%Y%m')
                value = 1
                break
            except Exception as e: 
                pass
            tmp_date_str = dir_str[i:i+7]
            try: 
                time.strptime(tmp_date_str,'%Y-%m')
                value = 1
                break
            except Exception as e: 
                pass
            tmp_date_str = dir_str[i:i+7]
            try: 
                time.strptime(tmp_date_str,'%Y_%m')
                value = 1
                break
            except Exception as e: 
                pass
    return value

    # 9. Union? 
def is_match_union(path,query ):
    global union_name_score_map
    if query != "" :
        path = path + "?" + query
    for key,value in union_name_score_map.items():
        static_arr = re.compile("\.\*|\*|\$").split(key)
        variable_arr = []
        i = 0
        while i < len(key) :
            if key[i] == "*" or key[i] == "$":
                variable_arr.append(key[i])
            i += 1
        tmp_variable_list = []
        pos = 0
        i = 0
        stop_flag = False
        while pos < len(path) and i < len(static_arr):
            if static_arr[i] not in path[pos:]:
                stop_flag = True
                tmp_variable_list = []
                break
            pos_2 = path[pos:].find(static_arr[i]) + pos 
            tmp_variable_list.append(path[pos:pos_2])
            pos = pos_2 + len(static_arr[i]) 
            i += 1
        if stop_flag == True or len(tmp_variable_list) == 0 or len(tmp_variable_list) !=\
            (len(variable_arr) + 1):
            continue
        i = 0
        match_num = 0
        for i in range (0 , len(variable_arr)) :
            if variable_arr[i] == "$" and tmp_variable_list[i+1].isdigit():
                match_num += 1
            elif len(tmp_variable_list[i+1]) > 0 :
                match_num += 1
        if match_num == len(variable_arr) :
            #print path,key,tmp_variable_list,variable_arr
            if value[0] > 0.8 :
                return -1
            elif value[1] > 0.8:
                return 1
            return 0
    return 0
    

def tool_plus_score(score_map,key,ori_score,load_tuple_index):
    ori_score += score_map[key][load_tuple_index]
    return ori_score
    
    # 11. match keyword in dri names 
def match_keyword_dirnames(dir_names,load_tuple_index = 0):
    global dir_name_score_map
    tmp_score = float(0)
    match_num = 0
    for dir_name in dir_names :
        if dir_name in dir_name_score_map.keys():
            #print('keyword in dirnames',dir_name)
            tmp_score = tool_plus_score(dir_name_score_map,dir_name,tmp_score,load_tuple_index)
            match_num += 1
    if match_num == 0 :
        return 0
    return tmp_score / match_num

    # 12. match keyword in resource names 
def match_keyword_filenames(res_name,load_tuple_index = 0):
    global res_name_score_map
    tmp_score = float(0)
    match_num = 0
    res_arr = re.compile("\.|_|-").split(res_name)
    for name in  res_arr:
        if name in res_name_score_map.keys():
            tmp_score = tool_plus_score(res_name_score_map,name,tmp_score,load_tuple_index)
            match_num += 1
    if match_num == 0 :
        return 0
    return tmp_score / match_num

    # 13. match keyword in paramter names 
def match_keyword_paramters(query_str,load_tuple_index = 0):
    global para_name_score_map
    tmp_score = float(0)
    match_num = 0
    query_params = query_str.split('&')
    for para_k_v in  query_params:
        if '=' not in para_k_v :
            continue
        name = para_k_v[:para_k_v.find('=')]
        if name in para_name_score_map.keys():
            tmp_score = tool_plus_score(para_name_score_map,name,tmp_score,load_tuple_index)
            match_num += 1
    if match_num == 0 :
        return 0
    return tmp_score / match_num


    # 14. match paramter value
def match_keyword_para_value(query_str,load_tuple_index = 0):
    global para_value_score_map
    tmp_score = float(0)
    match_num = 0
    query_params = query_str.split('&')
    for para_k_v in  query_params:
        if '=' not in para_k_v :
            continue
        value = para_k_v[para_k_v.find('=')+1:]
        if value in para_value_score_map.keys():
            tmp_score = tool_plus_score(para_value_score_map,value,tmp_score,load_tuple_index)
            match_num += 1
    if match_num == 0 :
        return 0
    return tmp_score / match_num

    
    # 16. the length when the resource file name is digit,
def is_digit_filename_len(dir_names):
    file_name = ''
    if len(dir_names) > 0 :
        file_name =  dir_names[len(dir_names)-1]
        if '.' in file_name:
            file_name = file_name[:file_name.rfind('.')]
    num = len(file_name)
    value = 0
    if num > 0 and file_name.isdigit() :
        if num > 4 :
            value = 1 
        else:
            value = 0.5
    return value 
    
    # 18. the length of file name or last dir name ,which is the most long serial number 
def serial_number_length_infilename(dir_names):
    file_name = ''
    value = 0
    if len(dir_names) <= 1 :
        return value
    file_name =  dir_names[len(dir_names)-1]
    is_dir_name = False
    if file_name == '' : 
        # last dir name
        is_dir_name = True
    if is_dir_name :
        file_name =  dir_names[len(dir_names)-2] 
    else:
        if '.' in file_name:
            file_name = file_name[:file_name.rfind('.')]

    if file_name == '' :
        return value

    num = max_continuity_digit( file_name)
    if num >= 8 :
        value = 1 
    elif num >= 6 :
        value = 0.9
    elif num > 4 :
        value = 0.8
    elif num == 4 :
        value = 0.4
    return value 

def para_value_number_len(query_str):
    if query_str == '':
        return 0
    query_params = query_str.split('&')
    for query in query_params :
        pos = query.find('=')
        if pos <= 0 :
            continue
        key = query[:pos]
        p_value = query[pos+1:]
        
        if key not in infoid_params_name_list :
            continue
        num = len(p_value)
        value = 0
        if num > 0 and p_value.isdigit() :
            if num >= 8 :
                value = 1 
            elif num >= 6 :
                value = 0.9
            elif num > 4 :
                value = 0.8
            elif num == 4 :
                value = 0.4
        return value 
    return 0





def features_extract(url,pretty=False):
    # output is list of eg:+1 1:0.708333 2:1 
    # the feature
    #scheme :// host / path / document . extension ? query=fragment
    index_value_list = []
    url = url.lower()
    url_portions = urllib.parse.urlparse(url)
    dir_names = url_portions.path.split('/')
    # 0 . paramters nums 
    tmp_index = 0 
    tmp_value = calc_paramter_number(url_portions.query)
    index_value_list.append(('num_paramters',tmp_value))
    # 1. path deepth 
    tmp_index = 1 
    tmp_value = len(dir_names) -1 
    if IS_NORMALIZTION :
        tmp_value = "%.2f" % ( float(len(dir_names) - 1 )/6)
    index_value_list.append(('path_depth',tmp_value))
    # 2 . all dir names chars length 
    tmp_index = 2 
    tmp_value = calc_dirnames_length(dir_names)
    index_value_list.append(('calc_dirnames_length',tmp_value))
    # 3 . average char length ???? 
    tmp_index = 3 
    tmp_value = average_dirnames_length(dir_names)
    index_value_list.append(('avg_dirnames',tmp_value))
    # 4. doc type judeyment? static or dynamic pages
    tmp_index = 4 
    tmp_value = is_dynamic_page(url_portions.query)
    index_value_list.append(('is_dynamic_page',tmp_value))
    # 5. whether the page is default page??
    tmp_index = 5 # is_default_page -> classify_doc_type
    tmp_value = classify_doc_type(url_portions.path)
    index_value_list.append(('classify_doc_type',tmp_value))
    # 6. the resource file name is digit ?
    tmp_index = 6
    tmp_value = is_digit_filename(dir_names,url_portions.query)
    index_value_list.append(('is_digit_filename',tmp_value))
    # 7. is contain date format in resource file name  ?
    tmp_index = 7
    tmp_value = is_match_date_filename(dir_names[len(dir_names)-1])
    index_value_list.append(('is-match-date-filename',tmp_value))
    # 8. is contain date format in dir names  ?
    tmp_index = 8 
    tmp_value = is_match_date_dirnames(dir_names[:len(dir_names)-1])
    index_value_list.append(('is-match-date-dirnames',tmp_value))

    tmp_index = 15
    tmp_value = len(dir_names[len(dir_names)-2]) if len(dir_names)>= 2 else 0
    if IS_NORMALIZTION :
        tmp_value = float(tmp_value) / 10
    index_value_list.append(('last_dir_len',tmp_value))
    # 17. url match "list" 
    tmp_index = 16 #TODO 
    tmp_value = -2 if 'list' in url_portions.path or 'blog' in url_portions.path or 'faq' in url_portions.path else 0
    index_value_list.append(('list_in',tmp_value))
    
    url_strings = dir_names[-1].lower().split('-') 
    tmp_value = -3 if 'c' in dir_names or 'cat' in dir_names or 'c' in url_strings or 'cat' in url_strings  else 0
    index_value_list.append(('category_in',tmp_value))
        
    tmp_value = 2 if 'p' in dir_names or 'product' in dir_names or 'p' in url_strings or 'product' in url_strings else 0
    index_value_list.append(('product_in',tmp_value))
    
    
    index_value_list.append(('num_of_spaces_all',len(url_strings)/15.0))
    tmp_value = dir_names[-1].split('-') if len(dir_names[-1])>0 else ''
    index_value_list.append(('num_of_spaces_filename',len(tmp_value)/15.0))
    
    # 18. the length of file name or last dir name ,which is the most long serial number 
    tmp_index = 17#
    tmp_value = serial_number_length_infilename(dir_names)
    index_value_list.append(('serial_num_infilename',tmp_value))
    # 19. the length of paramter value ,docid ,cid ,aid,
    tmp_index = 18#
    tmp_value = para_value_number_len(url_portions.query)
    index_value_list.append(('para_val_num_len',tmp_value))
    # 111. match keyword in dri names 
    tmp_index = 111 
    tmp_value = match_keyword_dirnames(dir_names[:len(dir_names)-1],1)
    index_value_list.append(('match_keywords_dir',tmp_value))
    # 112. match keyword in resource names 
    tmp_index = 112
    tmp_value = match_keyword_filenames(dir_names[len(dir_names)-1],1)
    index_value_list.append(('match_keywords_filename',tmp_value))
    # 113. match keyword in paramter names 
    tmp_index = 113
    tmp_value = match_keyword_paramters(url_portions.query,1)
    index_value_list.append(('match_keywords_para',tmp_value))
    # 114. match paramter value
    tmp_index = 114
    tmp_value = match_keyword_para_value(url_portions.query,1)
    index_value_list.append(('match_keywords_param_value',tmp_value))
    tmp_index = 115
    path_len =  len(url_portions.path) -1 if url_portions.path.startswith('/') else len(url_portions.path)
    tmp_value = "%.2f" % ( float(path_len)/50)
    index_value_list.append(('path_len',tmp_value))
    
    
    #print index_value_list
    if pretty:
        return index_value_list
    else:
        return [float(x[1]) for x in index_value_list]    
    


######### END OF CODE COPIED FROM URL-CLASSIFICATION project ##############



import pickle


def load_model(filename):
    with open(filename, 'rb') as f:
        model_struct = pickle.load(f)
        clf = model_struct['model']
    return clf

def predict_probability(clf,features):
    proba = clf.predict_proba([features])[0][1]
    return int(proba*100)

def check_if_product_url(url):
    features = features_extract(url)
    product_score = predict_probability(product_url_clf,features)
    return product_score     

product_url_model_path = os.path.join(os.path.dirname(__file__),'models','product-url.bin')
product_url_clf = load_model(product_url_model_path)

