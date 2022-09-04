from tabulate import tabulate
import time as tm

filename="data_100s15.txt"

f=open(filename)
alldata=f.readlines()
f.close()

#question = input("Sonuc Gosterim Formatı Secin: Dakika (0) or Saat (1)?")
question = 1

#Fonksiyonlar
def time(a):
    #time=a.split(":")
    #return ((int(time[0])*60)+int(time[1]))
    return int(a)

def mtod(minutes):
    hours,mins = divmod(minutes,60)
    if mins<10:
        return str(int(hours))+":0"+str(int(mins))
    else:
        return str(int(hours))+":"+str(int(mins))

def dolist(*args):
    liste=[]
    for arg in args:
        liste.extend(arg)
    return liste

def dv(day):
    global patient
    global patapp
    return [i for i in patient if patapp[i, day] == 1]

info={}
data={}
stype_req={}
stype_dur = {}
staff_types=[]
staff_num = {}
staffs={}
allstaff=[]
nodes=[]
depot=[]
patient=[]
tpoint=[]
vehicledepot=[]
patdaytype={}
patapp = {}
patdelivery = {}
patpickup = {}

for line in alldata:
    if line[:1] == "#":
        continue
    col = line.strip().split("\t")

    if col[0] == "COI":
        coi = float(col[1])
        continue
    
    if col[0] == "VEHICLE_NUMBER":
        vehicle = [n for n in range(1,int(col[1])+1)]
        continue

    if col[0] == "VEHICLE_CAPACITY":
        vcap = int(col[1])
        continue   
    
    if col[0] == "TRANSFER_DURATION":
        transfer_duration = int(col[1])
        continue 
    
    if col[0] == "TIME_LIMIT":
        time_limit = int(col[1])*60
        continue 
    
    if col[0] == "PLANNING_HORIZON":
        days=[n for n in range(1,int(col[1])+1)]
        continue 
    
    if col[0] == "STAFF":
        
        for sta in range(1,len(col)):
            sta = col[sta].split('|')
            staff_types.append(sta[0])
            staff_num[sta[0]] = int(sta[1])
            staffs[sta[0]] = [str(sta[0]+str(sx)) for sx in range(1,int(sta[1])+1)]
            for sx in range(1,int(sta[1])+1):
                allstaff.append(str(sta[0]+str(sx)))
        continue 
    
    if col[0] == "SERVICE_TYPE":
        stype = col[1].split('|')
        continue
    
    if col[0] == "SERVICE_TYPE_REQUIREMENT":
        for each_types in col[1].split('|'):
            each_type = each_types.split('=')
            for each_services in each_type[1].split(','):
                each_service = each_services.split(':')
                stype_req[each_type[0],each_service[0]] = int(each_service[1])
        continue

    if col[0] == "SERVICE_TYPE_DURATION":
        for each_types in col[1].split('|'):
            each_type = each_types.split('=')
            stype_dur[each_type[0]] = time(each_type[1])
        continue

    if col[0] == "NODE":
        section = "NODE"
        node_info = col
        continue
    
    if section == 'NODE':
        
        if col[0][0] == "H":
            nodes.append(col[0])
            depot.append(col[0])
            data["VH"] = {node_info[1]:int(col[1]), node_info[2]:int(col[2]), node_info[3]:int(time(col[3])), node_info[4]:int(time(col[4])) }
            
            data[col[0]] = {node_info[ci]:int(col[ci]) for ci in range(1, 3)}
            data[col[0]].update({node_info[ci]:int(time(col[ci])) for ci in range(3, len(node_info))})
        elif col[0][0] == "T":
            nodes.append(col[0])            
            tpoint.append(col[0])
            data[col[0]] = {node_info[ci]:int(col[ci]) for ci in range(1, 3)}
            data[col[0]].update({node_info[ci]:int(time(col[ci])) for ci in range(3, len(node_info))})

    if col[0] == "PATIENTS":
        section = "PATIENTS"
        node_info = col
        continue
    
    if section == 'PATIENTS':
        if col[0][0] == "P":
            nodes.append(col[0])
            patient.append(col[0])
            data[col[0]] = {node_info[ci]:int(col[ci]) for ci in range(1, 3)}
            data[col[0]].update({node_info[ci]:int(time(col[ci])) for ci in range(3, 5)})
            data[col[0]].update({int(node_info[ci]):col[ci] for ci in range(5, len(node_info))})

nodes.append("VH")
depot.append("VH")


xcoor=[]
ycoor=[]
for p in patient:
    xcoor.append(data[p]["X"])
    ycoor.append(data[p]["Y"])
mxcoor = (max(xcoor)+min(xcoor))/2
mycoor = (max(ycoor)+min(ycoor))/2

yatay = max(xcoor)-min(xcoor)
dikey = max(ycoor)-min(ycoor)
hiz=max([yatay,dikey])/2.0
#siniraulasmasuresi = 60
#kenar=(hiz/60.0)*siniraulasmasuresi
#sabit = (yatay*dikey)/(kenar*kenar)
data.update( {"H":{'X':mxcoor,'Y':mycoor,'open': 480, 'close': 1050}, "VH":{'X':mxcoor,'Y':mycoor,'open': 480, 'close': 1050}} )
for i in patient:
    for d in days:
        if data[i][d] != '-':
            patapp[i, d] = int(1)
        else:
            patapp[i, d] = int(0)
        for typ in stype:
            if data[i][d] == typ:
                patdaytype[i, d, typ] = int(1)
                for eachstaff in staffs:
                    patdelivery[i, d, eachstaff] = stype_req[typ, eachstaff]
                    patpickup[i, d, eachstaff] = stype_req[typ, eachstaff]
            else:   
                patdaytype[i, d, typ] = int(0)

print ("#############-DATA Ayristirildi.-#############")

from math import sqrt

c,t={},{}

for i in nodes:
    for j in nodes:
        if i != j:
            c[i,j] = round(sqrt((data[i]['X']-data[j]['X'])**2+(data[i]['Y']-data[j]['Y'])**2),0)
            t[i,j] = round(c[i,j]/hiz*60,0)
        elif i == j:
            c[i,j] = 0
            t[i,j] = 0
print ("#############-Mesafe ve Yol suresi matrisleri olusturuldu.-#############")

basla = tm.time()
from gurobipy import *
m = Model('bhdr')
K = int(570)
#M = int(10500000)
#ÇİZELGE
sp={}
for d in days:
    for s in allstaff:
        for p in dv(d):
            sp[d,p,s] = m.addVar( vtype=GRB.BINARY, name="sp[{},{},{}]".format(d,p,s) )
workload={}
for st in staff_types:
    workload[st] = m.addVar(vtype=GRB.INTEGER, name="workload")
#ROTALAMA
svflow={}
for d in days:
    for k in vehicle:
        for s in allstaff:
            for i in dolist(['H'],dv(d),tpoint):
                for j in dolist(dv(d),tpoint,['VH']):
                    if i != j:
                        svflow[d,k,i,j,s] = m.addVar( vtype=GRB.BINARY, name="svflow[{},{},{},{},{}]".format(d,k,i,j,s) )
vflow={}
for d in days:
    for k in vehicle:
        for i in dolist(['H'],dv(d),tpoint):
            for j in dolist(dv(d),tpoint,['VH']):
                if i != j:
                    vflow[d,k,i,j] = m.addVar( vtype=GRB.BINARY, name="vflow[{},{},{},{}]".format(d,k,i,j) )
vsurplus={}
for d in days:
    for i in dv(d):
        for k in vehicle:
            vsurplus[d,k,i] = m.addVar(vtype=GRB.INTEGER, name="vsurplus[{},{},{}]".format(d,k,i))
varrival,vdeparture={},{}
tstart,tend = {},{}
for d in days:
    for i in dolist(depot,dv(d),tpoint):
        for k in vehicle:
            varrival[d,k,i] = m.addVar(vtype=GRB.INTEGER, name="varrival[{},{},{}]".format(d,k,i))
            vdeparture[d,k,i] = m.addVar(vtype=GRB.INTEGER, name="vdeparture[{},{},{}]".format(d,k,i))
    for i in tpoint:
        tstart[d,i] = m.addVar(vtype=GRB.INTEGER, name="tstart[{},{}]".format(d,i))
        tend[d,i] = m.addVar(vtype=GRB.INTEGER, name="tend[{},{}]".format(d,i))

vridetime={}
for d in days:
    for k in vehicle:
        vridetime[d,k] = m.addVar(vtype=GRB.INTEGER, name="vridetime[{},{}]".format(d,k))

maxvsurplus = m.addVar(vtype=GRB.INTEGER, name="maxvsurplus")
maxvwait = m.addVar(vtype=GRB.INTEGER, name="maxvwait")

print ("#############-Karar Degiskenleri Olusturuldu.-#############")

m.update()

m.setObjective(0
               +999999*quicksum(workload[st] for st in staff_types)
               +1*(maxvsurplus)
               +quicksum(c[i,j]*vflow[d,k,i,j] for d in days for k in vehicle for i in dolist(['H'],dv(d),tpoint) for j in dolist(dv(d),tpoint,['VH']) if i != j )
               +0.1*quicksum(vridetime[d,k] for d in days for k in vehicle)
		,
               GRB.MINIMIZE)

#m.params.TIME_LIMIT = 3600
#m.params.MIPGap = 0.04
#m.addConstr( workload['D'] == 12)
#m.addConstr( workload['N'] == 16)

#ATAMA 
#Personel ↔ Hasta Ataması
for d in days:
    for p in dv(d):
        for st in staff_types:
            m.addConstr(  quicksum( sp[d,p,s] for s in staffs[st] ) == stype_req[data[p][d],st] )
#The Continuity of Care Index (COCI)
for p in patient:
    m.addQConstr(
        (
            quicksum(
                quicksum(sp[d,p,s] for d in days if p in dv(d)) * 
                quicksum(sp[d,p,s] for d in days if p in dv(d)) 
                for s in staffs['N']
                     )
         - quicksum(patapp[p, d] for d in days if p in dv(d))
         )
        >=
        coi * quicksum(patapp[p, d] for d in days if p in dv(d)) * ( quicksum(patapp[p, d] for d in days if p in dv(d)) - 1.0 )
    )
#Workload
for st in staff_types:
    for s in staffs[st]:
        m.addConstr(
            quicksum(sp[d,p,s] for d in days for p in dv(d)) <= workload[st]
        )

#ROTALAMA

#Araç Takibi
for d in days:
    for k in vehicle:
        m.addConstr( 
            quicksum(vflow[d,k,'H',j] for j in dolist(dv(d),tpoint,['VH'])) <= 1
        ) #her araç depodan başlar
        m.addConstr( 
            quicksum(vflow[d,k,'H',j] for j in dolist(dv(d),tpoint,['VH'])) == 
            quicksum(vflow[d,k,i,'VH'] for i in dolist(dv(d),tpoint,['H']))
        ) #depodan çıkan her araç geri döner
        
        for h in dolist(dv(d),tpoint):
            m.addConstr(
                quicksum(vflow[d,k,i,h] for i in dolist(['H'], dv(d), tpoint) if i!=h) == 
                quicksum(vflow[d,k,h,j] for j in dolist(dv(d),tpoint,['VH']) if j!=h)
            ) #her araç geldiği düğümden ayrılmak durumunda

#Staff Takibi
for d in days:
    for s in allstaff:
        m.addConstr(
            quicksum(svflow[d,k,'H',j,s] for k in vehicle for j in dolist(dv(d),tpoint,['VH']) ) <= 1
        )#
        m.addConstr(
            quicksum(svflow[d,k,'H',j,s] for k in vehicle for j in dolist(dv(d),tpoint,['VH']) ) == 
            quicksum(svflow[d,k,i,'VH',s] for k in vehicle for i in dolist(['H'],dv(d),tpoint) ) 
        )#

#Dugumler arasi aractaki personel sayisinin korunmasi
for d in days:
    for k in vehicle:
        for h in dv(d): 
            for s in allstaff:
                m.addConstr(
                    quicksum(svflow[d,k,i,h,s] for i in dolist(['H'],dv(d),tpoint) if i != h) == 
                    quicksum(svflow[d,k,h,j,s] for j in dolist(dv(d),tpoint,['VH']) if j != h)
                )#

#Transfer noktasina gelen personelin değiştirilmesi
for d in days:
    for tp in tpoint:
        for s in allstaff:
            m.addConstr(
                quicksum(svflow[d,k,i,tp,s] for i in dolist(['H'],dv(d)) for k in vehicle) == 
                quicksum(svflow[d,k,tp,j,s] for j in dolist(['VH'],dv(d)) for k in vehicle)
            )           

#her personel atandığı hastaya gitmeli
for d in days:
    for j in dv(d):
        for s in allstaff:
            m.addConstr( 
                quicksum(svflow[d,k,i,j,s] for k in vehicle for i in dolist(['H'],dv(d),tpoint) if i!=j) == sp[d,j,s]
            )

#personel akışının olduğu her arkta araç akışı olmalı
for d in days:
    for k in vehicle:
        for i in dolist(['H'],dv(d),tpoint):
            for j in dolist(dv(d),tpoint,['VH']):
                if i!=j:
                    for s in allstaff:
                        m.addConstr(
                            svflow[d,k,i,j,s]  <= vflow[d,k,i,j]
                        )

#her hastaya sadece 1 araç gitmeli
for d in days:
    for j in dv(d):
        for s in allstaff:
            m.addConstr(
                quicksum(vflow[d,k,i,j] for i in dolist(['H'],dv(d),tpoint) for k in vehicle if i!=j) == 1
            )

#Aractaki personelin toplami arac kapasitesini asamaz
for d in days:
    for k in vehicle:
        for i in dolist(['H'],dv(d),tpoint):
            for j in dolist(dv(d),tpoint,['VH']):
                if i!=j:
                    m.addConstr(
                        quicksum(svflow[d,k,i,j,s] for s in allstaff) <= vcap 
                    ) #

#zaman
for d in days:
    for i in tpoint:
        m.addConstr( tend[d,i] - tstart[d,i] == transfer_duration )#
    for k in vehicle:
        for i in tpoint:
            m.addConstr(varrival[d,k,i] <= tstart[d,i])#
            m.addConstr(vdeparture[d,k,i] >= tend[d,i])#
            m.addConstr( tend[d,i] <= data[i]['close'] )#
            m.addConstr( tstart[d,i] >= data[i]['open'] )#
    
        m.addConstr( varrival[d,k,'VH'] <= data['VH']['close'] )#
        m.addConstr( vdeparture[d,k,'H'] >= data['H']['open'] )#
        
        for i in dv(d):
            m.addConstr(varrival[d,k,i] >= data[i]['open'])#
            m.addConstr(vdeparture[d,k,i] <= data[i]['close']+maxvsurplus)#
            
            m.addConstr(varrival[d,k,i] + stype_dur[data[i][d]] == vdeparture[d,k,i]) #

        for i in dolist(['H'],dv(d),tpoint):
            for j in dolist(dv(d),tpoint,['VH']):
                if i != j:
                    m.addConstr(vdeparture[d,k,i] + t[i,j] - (K * (1 - vflow[d,k,i,j])) <= varrival[d,k,j])#
        
        m.addConstr(varrival[d,k,'VH'] - vdeparture[d,k,'H'] == vridetime[d,k])#ok

print ("#############- Cozuluyor- #############")
m.optimize()

status = m.status
if status == GRB.Status.UNBOUNDED:
    print('The model cannot be solved because it is unbounded')
if status == GRB.Status.OPTIMAL:
    print('The optimal objective is %g' % m.objVal)
if status != GRB.Status.INF_OR_UNBD and status != GRB.Status.INFEASIBLE:
    print('Optimization was stopped with status %d' % status)
if status == GRB.INFEASIBLE:
    m.computeIIS()
    m.write("vrp.ilp")

header=[]
header.append("Randevu")
for d in days:
    header.append(d)
table=[]
for px,p in enumerate(patient):
    table.append([])
    table[px].append(p)
    for d in days:
        plist=[]
        if p in dv(d):
            for s in allstaff:
                if sp[d,p,s].x == 1:
                    plist.append(s)
    
            if len(plist) > 0:
                table[px].append(plist)
            else:
                table[px].append("-")
        else:
            table[px].append("-")

print (tabulate(table, headers=header, tablefmt="rst", numalign="center"))

print ("****")
print ("ROTALAR")
routes={(d,k):[] for k in vehicle for d in days}
for d in days:
    for k in vehicle:
        i = 'H'
        j = ''
        while j != 'VH':
            for j in dolist(dv(d),tpoint,['VH']):
                if i != j:
                    if vflow[d,k,i,j].x == 1:
                        if i not in routes[d,k]:
                            routes[d,k].append(i)
                        routes[d,k].append(j)
                        i = j
                        break

stop={}
for d in days:
    for i in dv(d):
        stop[d,i] = [sta for sta in allstaff if sp[d,i,sta].x == 1]

print ("ROTALARIN ZAMAN CIZELGESI")
#import networkx as nx
#import matplotlib.pyplot as plt
for d in days:
    
    for i in dv(d):
        temps=[]
        for s in allstaff:
            if sp[d,i,s].x==1:
                temps.append(s)
        print ("Gün →",d," ",i," →",temps)
        print ("---")

    for k in vehicle:
        if len(routes[d,k]) != 0:
            print ("Araç :", k)
            print ("Gün",d,"Rota #"+str(k),routes[d,k])

        i = 'H'
        j = ''
        while j != 'VH':
            for j in dolist(dv(d),tpoint,['VH']):
                if i != j and vflow[d,k,i,j].x == 1:
                    if j == 'VH':

                        print ("Hareket Noktası :", i, "Hareket Saati :", mtod(vdeparture[d,k,i].x), "Yolculuk Süresi :", mtod(t[i,j]), "Varış Noktası : ", j, "Varış Saati :", mtod(varrival[d,k,j].x), "Taşınan Personel →", [ staff for staff in allstaff if svflow[d,k,i,j,staff].x == 1])

                    elif i == 'H':
#"Need →", stop[d,j] if j in dv(d) else "\t" ,
                        print ("Hareket Noktası :", i, "Hareket Saati :", mtod(vdeparture[d,k,i].x), "Yolculuk Süresi :", mtod(t[i,j]), "Varış Noktası : ", j, "Varış Saati :", mtod(varrival[d,k,j].x), "Taşınan Personel →", [ staff for staff in allstaff if svflow[d,k,i,j,staff].x == 1])

                    else:

                        print ("Hareket Noktası :", i, "Departure :", mtod(vdeparture[d,k,i].x), "DrivingTime :", mtod(t[i,j]), "To : ", j, "Arrival :", mtod(varrival[d,k,j].x), "Carried Staffs →", [ staff for staff in allstaff if svflow[d,k,i,j,staff].x == 1])

                    i = j
                    break
    print ("-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-")
    #G = nx.Graph()
    #for i in dolist(depot,dv(d)):
        #G.add_node(i, pos=(data[i]['X'],data[i]['Y']), name=str(i) )
    #for i in tpoint:
        #if sum(vflow[d,k,i,j].x for j in dolist([depot[-1]],dv(d)) for k in vehicle) >= 1:
            #G.add_node(i, pos=(data[i]['X'],data[i]['Y']), name=str(i) )
    
    #for i in dolist(dv(d),tpoint,[depot[0]]):
        #for j in dolist(dv(d),tpoint,[depot[-1]]):
            #if i != j:
                #for k in vehicle:
                    #if vflow[d,k,i,j].x == 1:
                        #G.add_edge(i,j, route="V"+str(k)+","+str(j+"<-"+i)+","+str([ staff for staff in allstaff if svflow[d,k,i,j,staff].x == 1]))
    
    #pos=nx.get_node_attributes(G,'pos')
    #node_labels = nx.get_node_attributes(G, 'name')
    #edge_labels = nx.get_edge_attributes(G, 'route')
    
    #nx.draw_networkx(G, pos, with_labels=False)
    
    #nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=6, font_color='k', font_family='sans-serif', font_weight='normal', alpha=1.0, bbox=None, ax=None)
    #nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, label_pos=0.5, font_size=6, font_color='k', font_family='sans-serif', font_weight='normal', alpha=1.0, bbox=None, ax=None, rotate=True)
    ##nx.draw(G,pos, edge_labels, node_labels, with_labels=True)
    #plt.gcf().canvas.set_window_title('Gün '+str(d))
    #plt.show()    
    print ("\n")

print ("işlem bitti. süre",tm.time()-basla)
print ("Sonuçlar")
temp=0
for p in patient:
    cox= (
        sum(   sum(sp[d,p,s].x for d in days if p in dv(d))**2
                 for s in staffs['N']
                 )
          - sum(patapp[p, d] for d in days if p in dv(d))
          ) / (
              sum(patapp[p, d] for d in days if p in dv(d)) * 
              ( sum(patapp[p, d] for d in days if p in dv(d)) - 1.0 )
          )
    temp += cox
    print (p,cox)

print (temp)
print ("Ortalama Coci",temp/len(patient))

for st in staff_types:
    print ("Workload",st,"→",workload[st].x)
    for s in staffs[st]:
        print (s," Workload →",sum(sp[d,p,s].x for d in days for p in dv(d)))
        sday=0
        for d in days:
            if sum(sp[d,p,s].x for p in dv(d)) >0.0:
                sday+=1
        print (s, "calistiği gün sayısı", sday)
print ("Toplam Mesafe", sum(c[i,j]*vflow[d,k,i,j].x for d in days for k in vehicle for i in dolist(['H'],dv(d),tpoint) for j in dolist(dv(d),tpoint,['VH']) if i != j ))
print (maxvsurplus.x)

##Grafik olusturma
#print "stop"
#import networkx as nx
#import matplotlib.pyplot as plt

#G = nx.Graph()
#for i in dolist(depot,patient):
    #G.add_node(i, pos=(data[i]['X'],data[i]['Y']), name=str(i) )
#for i in tpoint:
    #if sum(x[i,j,k].x for j in dolist([depot[-1]],patient) for k in vehicle) == 2:
    ##if trsp[i].x == 1:
        #G.add_node(i, pos=(data[i]['X'],data[i]['Y']), name=str(i) )

#for i in dolist(patient,tpoint,[depot[0]]):
    #for j in dolist(patient,tpoint,[depot[-1]]):
        #if i != j:
            #for k in vehicle:
                #if x[i,j,k].x == 1:
                    #G.add_edge(i,j, route="V"+str(k)+","+str(routes[k].index(j))+","+str(t[i,j]))

#pos=nx.get_node_attributes(G,'pos')
#node_labels = nx.get_node_attributes(G, 'name')
#edge_labels = nx.get_edge_attributes(G, 'route')

#nx.draw_networkx(G, pos, with_labels=False)

#nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=6, font_color='k', font_family='sans-serif', font_weight='normal', alpha=1.0, bbox=None, ax=None)
#nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, label_pos=0.5, font_size=6, font_color='k', font_family='sans-serif', font_weight='normal', alpha=1.0, bbox=None, ax=None, rotate=True)
##nx.draw(G,pos, edge_labels, node_labels, with_labels=True)
#plt.title('Center Title')
#plt.show()
