from lxml import etree
import datetime
import numpy as np 

def createInput(filename):
    buildGraph(filename)
    buildData(filename)
    xesReal(filename)
    graphReal(filename)

def xesReal(filename):
    f1=open("input/"+filename+".xes", "r")
    f2=open("input/"+filename+".real", "w")
    newTrace=False
    newEvent=False
    for line in f1:
        if("<trace>" in line):
            newTrace=True
        if(("concept:name" in line) & newTrace):
            id=line[line.index("value"):]
            id=id[id.index("=")+2:]
            id=id[:id.index("/")-1]
            f2.write(id+",")
            newTrace=False
            newEvent=True
        if(newEvent & ("cluster:label" in line)):
            cluster=line[line.index("value"):]
            cluster=cluster[cluster.index("=")+2:]
            cluster=cluster[:cluster.index("/")-1]
            cluster=int(cluster)-1
            cluster=str(cluster)
            f2.write(cluster+"\n")
            newEvent=False
    f1.close()
    f2.close()

def graphReal(filename):
    f1=open("input/"+filename+".xes", "r")
    f2=open("input/"+filename+".graph.real", "w")
    traceID=0
    newTrace=False
    for line in f1:
        if("<trace>" in line):
            newTrace=True
        if(newTrace & ("cluster:label" in line)):
            cluster=line[line.index("value"):]
            cluster=cluster[cluster.index("=")+2:]
            cluster=cluster[:cluster.index("/")-1]
            cluster=int(cluster)-1
            cluster=str(cluster)
            f2.write("trace_"+str(traceID)+","+cluster+"\n")
            newTrace=False
            traceID+=1
    f1.close()
    f2.close()

def buildGraph(filename):
    
    graph = open("input/"+filename+".graph",'w')
    
    tree = etree.parse("input/"+filename+".xes")
    root = tree.getroot()
    
    c_name = -1

    for element in root.iter():
        
        if(element.tag.endswith('trace')):
            
            vector_events = []
            
            c_name += 1
            
            avg_SUMleges = 0
            counter_avg_SUMleges = 0
            
            for childelement in element.iterchildren():
                               
                key = childelement.attrib.get('key')
                value = childelement.attrib.get('value')
                is_term_name = False
                is_SUMleges = False
                is_parts = False
                is_action_code = False
                is_responsible_actor = False
                is_last_phase = False
                is_artificial = False
                                
                if (childelement.tag.endswith('event')):
                    
                    for grandchildelement in childelement.iterchildren():

                        key = grandchildelement.attrib.get('key')
                        value = grandchildelement.attrib.get('value')
                                                
                        if value == 'artificial':
                            is_term_name = True
                            is_SUMleges = True
                            is_parts = True
                            is_action_code = True
                            is_responsible_actor = True
                            is_last_phase = True
                            is_artificial = True
                            break
                        
                        elif key == '(case)_SUMleges':
                            case_SUMleges = value
                            is_SUMleges = True
                            avg_SUMleges += float(value)
                            counter_avg_SUMleges += 1
                            
                        elif key == 'action_code':
                            is_action_code = True
                            action_code = value.replace('_','')
                            
                        elif key == 'activityNameEN':
                            activityNameEN = value.replace('-','').replace(' ','').replace(':','').replace('.','').replace(',','')
                            
                        elif key == '(case)_caseStatus':
                            case_caseStatus = value
                           
                        elif key == '(case)_Responsible_actor':
                            is_responsible_actor = True
                            case_Responsible_actor = value
                           
                        elif key == 'concept:name':
                            concept_name = value.replace('_','')
                           
                        elif key == '(case)_last_phase':
                            is_last_phase = True
                            case_last_phase = value.replace(' ','')
                        
                        elif key == '(case)_requestComplete':
                            if(value == 'TRUE'):
                                case_requestComplete = '1'
                            else:
                                case_requestComplete = '0'
                        
                        elif key == '(case)_parts':
                            is_parts = True
                            case_parts = value.replace(',','').replace(' ','').replace('(','').replace(')','').replace('/','').replace('-','').replace(':','').replace('.','')
                        
                        elif key == 'question':
                            if value == 'True' or value == 'False' or value == 'EMPTY':
                                question = value
                            else:
                                question = 'EMPTY'
                        
                        elif key == '(case)_termName':
                            is_term_name = True
                            case_termName = value.replace(' ','')
                           
                        elif key == 'monitoringResource':
                            monitoringResource = value
                           
                        elif key == 'org:resource':
                            org_resource = value
                           
                    if not is_term_name:
                        case_termName = 'EMPTY'
                        
                    if not is_SUMleges:
                        case_SUMleges = 'EMPTY'
                        
                    if not is_parts:
                        case_parts = 'EMPTY'
                        
                    if not is_action_code:
                        action_code = 'EMPTY'
                        
                    if not is_responsible_actor:
                        case_Responsible_actor = 'EMPTY'
                        
                    if not is_last_phase:
                        case_last_phase = 'EMPTY'
                    
                    if not is_artificial:    
                        event = 'e_' + str(c_name) + '_' + concept_name
                        vector_events.append(event)
                        
                        graph.write(event + ' eventName_' + concept_name + '\n')
                        graph.write(event + ' SUMleges_' + case_SUMleges + '\n')
                        graph.write(event + ' action_code_' + action_code + '\n')
                        graph.write(event + ' activityNameEN_' + activityNameEN + '\n')
                        graph.write(event + ' caseStatus_' + case_caseStatus + '\n')
                        graph.write(event + ' Responsible_actor_' + case_Responsible_actor + '\n')
                        graph.write(event + ' last_phase_' + case_last_phase + '\n')
                        graph.write(event + ' requestComplete_' + case_requestComplete + '\n')
                        graph.write(event + ' parts_' + case_parts + '\n')
                        graph.write(event + ' question_' + question + '\n')
                        graph.write(event + ' termName_' + case_termName + '\n')
                        graph.write(event + ' monitoringResource_' + monitoringResource + '\n')
                        graph.write(event + ' org_resource_' + org_resource + '\n')

            graph.write('trace_' + str(c_name) + ' ' + vector_events[0] + '\n')
            
            for i in range(1,len(vector_events)-1):
                graph.write(vector_events[i] + ' ' + vector_events[i+1] + '\n')
            
    graph.close()

def buildData(filename):
    
    data = []

    tree = etree.parse("input/"+filename+".xes")
    root = tree.getroot()

    for element in root.iter():
        
        if(element.tag.endswith('trace')):
            
            cluster = ''#nominal (label: 1,2,3,4,5)
            case_SUMleges_seq = ''#sequence of float
            action_code_seq = ''#sequence of nominal
            activityNameEN_seq = ''#sequence of nominal
            case_caseStatus_seq = ''#sequence of nominal
            case_Responsible_actor_seq = ''#sequence of nominal
            concept_name_seq = ''#sequence of nominal
            case_last_phase_seq = ''#sequence of nominal
            case_requestComplete_seq = ''#sequence of boolean
            case_parts_seq = ''#sequence of nominal
            question_seq = ''#sequence of nominal
            case_termName_seq = ''#sequence of nominal
            monitoringResource_seq = ''#sequence of nominal
            org_resource_seq = ''#sequence of nominal
           
            delta_df = ''#sequence of delta timestamps
            previous_dateFinished = 'null'
            delta_p = ''#sequence of delta timestamps
            previous_planned = 'null'
            delta = ''#sequence of delta timestamps
            previous_timestamp = 'null'
            
            min_date_df = datetime.date(2030, 1, 1)
            max_date_df = datetime.date(2000, 1, 1)
            min_date_p = datetime.date(2030, 1, 1)
            max_date_p = datetime.date(2000, 1, 1)
            min_date = datetime.date(2030, 1, 1)
            max_date = datetime.date(2000, 1, 1)
            
            avg_SUMleges = 0
            counter_avg_SUMleges = 0
            
            for childelement in element.iterchildren():
                               
                key = childelement.attrib.get('key')
                value = childelement.attrib.get('value')
                is_term_name = False
                is_SUMleges = False
                is_planned = False
                is_parts = False
                is_action_code = False
                is_responsible_actor = False
                is_last_phase = False
                if(key == 'cluster:label'):
                    cluster = value
                    
                if (childelement.tag.endswith('event')):
                    
                    for grandchildelement in childelement.iterchildren():
                        key = grandchildelement.attrib.get('key')
                        value = grandchildelement.attrib.get('value')
                                                
                        if value == 'artificial':
                            is_term_name = True
                            is_SUMleges = True
                            is_planned = True
                            is_parts = True
                            is_action_code = True
                            is_responsible_actor = True
                            is_last_phase = True
                            break
                        #agguinto
                        elif key == '(case)_cluster:label':
                            cluster=value
                        
                        elif key == '(case)_SUMleges':
                            case_SUMleges_seq += value + '/'
                            is_SUMleges = True
                            avg_SUMleges += float(value)
                            counter_avg_SUMleges += 1
                            
                        elif key == 'dateFinished':
                            dateFinished = datetime.datetime.strptime(value[:10], '%Y-%m-%d').date()
                            min_date_df = min(min_date_df,dateFinished)
                            max_date_df = max(max_date_df,dateFinished)
                            
                            if(previous_dateFinished == 'null'):
                                difference_df = '0'
                            else:
                                difference_df = str((dateFinished - previous_dateFinished).days)
                            
                            delta_df += difference_df+'/'
                            
                            previous_dateFinished = dateFinished
                            
                        elif key == 'action_code':
                            is_action_code = True
                            action_code_seq += value.replace('_','') + '/'
                            
                        elif key == 'activityNameEN':
                            activityNameEN_seq += value.replace('-','').replace(' ','').replace(':','').replace('.','').replace(',','') + '/'
                            
                        elif key == 'planned':
                            is_planned = True
                            planned = datetime.datetime.strptime(value[:10], '%Y-%m-%d').date()
                            min_date_p = min(min_date_p,planned)
                            max_date_p = max(max_date_p,planned)
                            
                            if(previous_planned == 'null'):
                                difference_p = '0'
                            else:
                                difference_p = str((planned - previous_planned).days)
                            
                            delta_p += difference_p+'/'
                            
                            previous_planned = planned
                            
                        elif key == '(case)_caseStatus':
                            case_caseStatus_seq += value + '/'
                           
                        elif key == '(case)_Responsible_actor':
                            is_responsible_actor = True
                            case_Responsible_actor_seq += value + '/'
                           
                        elif key == 'concept:name':
                            concept_name_seq += value.replace('_','') + '/'
                           
                        elif key == '(case)_last_phase':
                            is_last_phase = True
                            case_last_phase_seq += value.replace(' ','') + '/'
                        
                        elif key == '(case)_requestComplete':
                            if(value == 'TRUE'):
                                case_requestComplete_seq += '1/'
                            else:
                                case_requestComplete_seq += '0/'
                        
                        elif key == '(case)_parts':
                            is_parts = True
                            case_parts_seq += value.replace(',','').replace(' ','').replace('(','').replace(')','').replace('/','').replace('-','').replace(':','').replace('.','') + '/'
                        
                        elif key == 'question':
                            if value == 'True' or value == 'False' or value == 'EMPTY':
                                question_seq += value + '/'
                            else:
                                question_seq += 'EMPTY/'
                        
                        elif key == '(case)_termName':
                            case_termName_seq += value.replace(' ','') + '/'
                            is_term_name = True
                           
                        elif(key == 'time:timestamp'):
                            timestamp = datetime.datetime.strptime(value[:10], '%Y-%m-%d').date()
                            min_date = min(min_date,timestamp)
                            max_date = max(max_date,timestamp)
                            
                            if(previous_timestamp == 'null'):
                                difference = '0'
                            else:
                                difference = str((timestamp - previous_timestamp).days)
                            
                            delta += difference+'/'
                            
                            previous_timestamp = timestamp
                           
                        elif key == 'monitoringResource':
                            monitoringResource_seq += value + '/'
                           
                        elif key == 'org:resource':
                            org_resource_seq += value + '/'
                        
                    if not is_term_name:
                        case_termName_seq += 'EMPTY/'
                        
                    if not is_SUMleges:
                        case_SUMleges_seq += 'EMPTY/'
                    
                    if not is_planned:
                        delta_p += '0/'
                        
                    if not is_parts:
                        case_parts_seq += 'EMPTY/'
                        
                    if not is_action_code:
                        action_code_seq += 'EMPTY/'
                        
                    if not is_responsible_actor:
                        case_Responsible_actor_seq += 'EMPTY/'
                        
                    if not is_last_phase:
                        case_last_phase_seq += 'EMPTY/'
             
            duration = 0
            duration_p = 0
            duration_df = 0               
            
            diff = (max_date - min_date).days
            
            if(diff > 0):
                duration = str(diff)
                
            diff_df = (max_date_df - min_date_df).days
            
            if(diff_df > 0):
                duration_df = str(diff_df)
                
            diff_p = (max_date_p - min_date_p).days
            
            if(diff_p > 0):
                duration_p = str(diff_p)
                
            
            delta = delta[:len(delta)-1]
            delta_p = delta_p[:len(delta_p)-1]
            delta_df = delta_df[:len(delta_df)-1]
            
            if avg_SUMleges > 0 and counter_avg_SUMleges > 0:
                avg_SUMleges = avg_SUMleges/counter_avg_SUMleges
                case_SUMleges_seq = case_SUMleges_seq.replace('EMPTY',str(avg_SUMleges))
            elif avg_SUMleges == 0 and counter_avg_SUMleges == 0:
                case_SUMleges_seq = case_SUMleges_seq.replace('EMPTY','0')
                    
            case_SUMleges_seq = case_SUMleges_seq[:len(case_SUMleges_seq)-1]
            action_code_seq = action_code_seq[:len(action_code_seq)-1]
            activityNameEN_seq = activityNameEN_seq[:len(activityNameEN_seq)-1]
            case_caseStatus_seq = case_caseStatus_seq[:len(case_caseStatus_seq)-1]
            case_Responsible_actor_seq = case_Responsible_actor_seq[:len(case_Responsible_actor_seq)-1]
            concept_name_seq = concept_name_seq[:len(concept_name_seq)-1]
            case_last_phase_seq = case_last_phase_seq[:len(case_last_phase_seq)-1]
            case_requestComplete_seq = case_requestComplete_seq[:len(case_requestComplete_seq)-1]
            case_parts_seq = case_parts_seq[:len(case_parts_seq)-1]
            question_seq = question_seq[:len(question_seq)-1]
            case_termName_seq = case_termName_seq[:len(case_termName_seq)-1]
            monitoringResource_seq = monitoringResource_seq[:len(monitoringResource_seq)-1]
            org_resource_seq = org_resource_seq[:len(org_resource_seq)-1]
            
            line = case_SUMleges_seq+','+action_code_seq+','+activityNameEN_seq+','+case_caseStatus_seq+','+case_Responsible_actor_seq+','+concept_name_seq+','+case_last_phase_seq+','+case_requestComplete_seq+','+case_parts_seq+','+question_seq+','+case_termName_seq+','+monitoringResource_seq+','+org_resource_seq+','+str(delta)+','+str(delta_p)+','+str(delta_df)+','+str(duration)+','+str(duration_df)+','+str(duration_p)+','+str(cluster)+'\n'
            data.append(line)        
           
    
    data = np.array(data)
    
    attributes_line = 'case_SUMleges_seq,action_code_seq,activityNameEN_seq,case_caseStatus_seq,case_Responsible_actor_seq,concept_name_seq,case_last_phase_seq,case_requestComplete_seq,case_parts_seq,question_seq,case_termName_seq,monitoringResource_seq,org_resource_seq,delta,delta_p,delta_df,duration,duration_df,duration_p,cluster\n'
    
    log2015 = open("input/"+filename+".csv",'w')
    log2015.write(attributes_line)
    
    for item in data:
        log2015.write(item)

    log2015.close()