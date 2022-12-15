'''
Data Web Analyser

This script parse webpage www.bankier.pl,
find some stock and exchange data, build
an database of each run and show data on
charts. Each step is save/read from txt
files to see the steps.

This script requires that 'matplotlib',
'pandas', 'requests', 'bs4', 'csv', tkinter be installed within the Python environment
you are running this script in.

'''
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout

import time
import numpy as np
import datetime
import csv
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import matplotlib.dates as mdates



def get_from_bankier():
    '''
    Parse data from bankier.pl and return str.
    '''
    link_www = 'http://www.bankier.pl/'
    obiekt = requests.get(link_www)
    soup = BeautifulSoup(obiekt.content, 'html.parser')
    heading_tags = ("span", {"class": "title"})
    context = ''
    for tags in soup.findAll(heading_tags):
        context =context + str(tags.text)
    return context


def write_indexes():
    '''
    Func open txt parsed data file
    "bankier.txt", find str with stock data
    and save in txt file 'index_data.txt'.
    '''
   
    maindata = get_from_bankier()
    maindata = maindata.replace('WIG20 ', '')
    maindata = maindata.replace('WIG20.', '')
    find_wig20 = maindata.find('WIG201')
    if find_wig20<10:
        find_wig20 = maindata.find('WIG202')
    find_ropa = maindata.find('ROPA')
    find_poropa = maindata.find('%',  find_ropa) +1
    all_main_indexes = maindata[find_wig20:find_poropa]
    all_main_indexes = all_main_indexes.replace('WIG20', 'Wig20')
    
    return all_main_indexes
    

def build_list(goods):
    '''
    Func read stock_data string from file
    'index_data.txt', split it and append
    to .csv file with datetime.
    
    :param goods: list of string names
        of goods
    :type goods: list
    '''
    
    data_value = []
    for item in (goods):
        all_main_indexes = write_indexes()
        find_data = all_main_indexes.find(item) + len(item)
        find_data_end = all_main_indexes.find(",", all_main_indexes.find(item), )+3
        data_result = all_main_indexes[find_data:find_data_end]
        if len(data_result)>8:
            data_result = ''.join((data_result.split()))
        data_result = data_result.replace(",", ".")
        data_result = data_result.replace(" ", "")
        data_value.append(data_result)
        
    with open('index_data.csv', 'a', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')
        time_stamp = datetime.datetime.now().strftime("%H:%M %d.%m.%Y")
        csvwriter.writerow([time_stamp] + data_value)


def build_chart(update_data=False):
    '''
    Get new data from bankier.pl, merge
    with old data and build chart. All good.
    '''
    t_1 = time.time()
    all_goods = [
                'Wig20', 'WIG', 'DAX',
                'NASDAQ','SP500', 'USD/PLN',
                'EUR/PLN', 'GBP/PLN',
                'EUR/USD', 'ZŁOTO',
                'MIEDŹ', 'ROPA'
                ]
    
    if update_data:
        build_list(all_goods)
    
    #show data on chart
    dat_frame = np.genfromtxt('index_data.csv', delimiter=',', dtype='float64')
    dat_frame = dat_frame[1:,:]
    timeline = np.genfromtxt('index_data.csv', delimiter=',', dtype='str')
    timeline = timeline[1:,:]
    timeline = timeline[:,0]
    timeline_c = []
    for n in timeline:
        nn = datetime.datetime.strptime(n, "%H:%M %d.%m.%Y")
        timeline_c.append(nn)
    dat_frame = dat_frame[:, 1:]
    #print(dat_frame)
    #print(timeline)
    
    plt.rcParams['figure.figsize'] = [10, 14]
    figure, axis = plt.subplots(4, 3)
    line_colors = ['y-', 'g-', 'c-']
    
    for ch_num, _ in enumerate(all_goods):
        if ch_num<5:
            color=0
        elif 9>ch_num>4:
            color=1
        else: color=2
        
        horiz = ch_num // 3
        vert = ch_num % 3
        dat = dat_frame[:, ch_num].tolist()
        axis[horiz, vert].plot(
            timeline_c,
            dat,
            line_colors[color], alpha=0.4)
        rol_mean = []
        num_mean = 10
        for w, _ in enumerate(dat):
            if w<=num_mean:
                t = dat[0:(w+num_mean)]
            if w>(len(dat)-num_mean):
                t = dat[(w-num_mean):-1]
            else:
                t = dat[(w-num_mean):(num_mean+w)]
            #rol_mean.append(sum(t)/len(t))
                
        #axis[horiz, vert].plot(timeline_c, rol_mean, 'r-')
        print(rol_mean)
        
        last_val = dat[-1]
        second_last_val = dat[-2]
        axis[horiz, vert].set_title(
        str(all_goods[ch_num]) + ': '+str(last_val)+' (' +str(round((last_val - second_last_val),2)) + ')'
        )
        
        axis[horiz, vert].xaxis.set_major_locator(mdates.MonthLocator())
        
        axis[horiz, vert].tick_params(axis='x', labelrotation = 30)
        
    plt.tight_layout()
    
    #runtime
    t_2 = time.time()
    run_time = t_2-t_1
    
    return run_time
    

class MainScreen(BoxLayout):
    
    def __init__(self, **kwargs):
        
        super(MainScreen, self).__init__(**kwargs)
        
        self.orientation = 'vertical'
        build_chart(update_data=False)
        self.add_widget(FigureCanvasKivyAgg(plt.gcf()))
        btn_1 = Button(size_hint=(1,0.06), text='Exit')
        btn_1.bind(on_release=self.btn_1_rel)
        self.add_widget(btn_1)
       
    
    def btn_1_rel(self, instances):
       App.get_running_app().stop()
        

class DwaApp(App):
    def build(self):
        return MainScreen()

if __name__ == '__main__':
    DwaApp().run()
