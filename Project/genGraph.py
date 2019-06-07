import numpy as np
import matplotlib.pyplot as plt
plt.style.use('fivethirtyeight')

def plt_airstriker():
    '''
    airstriker-genesis
    '''
    brute_times = [1.07,3.6,14.2,60.9,70.3,86.9,99.4,191.5,195.1,259,279.7,404.5,582,733.2,862.4,953.5,965.2,969,1024,1034.1,1071,1103,1175,1203,1402.2,1554.8,1712.4,1956.9,1994.9,3596.4,3843.8,3859.5,3998.7,4305.4,5072.1,6126.9,6308,6820.4,6870,9162.5,9198,9433.3,9618,10316.6]
    brute_values = [200,240,320,340,360,380,420,440,480,500,520,600,620,640,660,700,720,740,760,800,820,940,960,980,1000,1020,1040,1060,1080,1100,1120,1140,1160,1180,1200,1240,1280,1300,1320,1340,1360,1380,1400,1420]
    
    default_times = [0.7,1.6,3.1,3.8,4.5,7.3,19.2,47.1,107.4,2169.5,2958]
    default_values = [100,140,160,200,220,240,280,300,340,360,560]
    
    '''
    gamma = 0.1
    '''
    g1_times = [0.8,5.4,18.7,46.8,225.1,649.9]
    g1_values = [200,240,280,300,340,450]
    
    '''
    explore = 1
    '''
    exp1_times = [1.3,11.4,23.4,214.2,694.8,6520.1]
    exp1_values = [200,240,260,320,400,540]
    
    '''
    explore = 10
    '''
    exp10_times = [0.8,2.2,6,209.8,317.2,2096.2,4839,5681.3]
    exp10_values = [140,160,300,320,360,380,400,420]
    
    '''
    depth = 20
    '''
    d20_times = [.1,66.7,95.7,488.1,1455.9]
    d20_values = [260,280,340,360,500]

    '''
    gamma = 0.1 depth=20 explore=1
    '''
    many_times = [1.5,33.3,270,1909,5031.5,6987]
    many_values = [260,280,360,380,400,460]
    
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_xlabel("time (sec)",fontsize=25)
    ax.set_ylabel("Score",fontsize=25)
    ax.set_title("Comparison of Learners: Airstriker-Genesis",fontsize=40)
    plt.plot(brute_times,brute_values,label="Brute Forcer")
    plt.plot(default_times,default_values,label="Default")
    plt.plot(g1_times,g1_values,label="gamma=0.1")
    plt.plot(exp1_times,exp1_values,label="explore=1")
    plt.plot(exp10_times,exp10_values,label="explore=10")
    plt.plot(d20_times,d20_values,label="depth=20")
    plt.plot(many_times, many_values, label="gamma=0.1,depth=20,explore=1",color='black')
    ax.legend(loc='center right')
    plt.show()

def plt_dkc():
    '''brute'''
    brute_vals = [6,15,18,23,28,29]
    brute_times = [17.4,71.4,231.1,286.7,1303,2182]

    '''default'''
    def_vals = [15,27,29,33]
    def_times = [16.2,208.8,356.5,2224.5]

    '''depth=100'''
    d100_vals = [10,12,14,23,24]
    d100_times = [18.1,37.1,108.1,178.2,1584.8]

    '''
    depth=100 explore=1
    '''
    d100e1_times = [18.3,37,611.2,3053.2]
    d100e1_vals = [7,23,25,34]
    
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_xlabel("time (sec)",fontsize=25)
    ax.set_ylabel("Score",fontsize=25)
    ax.set_title("Comparison of Learners: DonkeyKong Country",fontsize=40)
    plt.plot(brute_times, brute_vals, label="Brute Forcer")
    plt.plot(def_times, def_vals, label="Default")
    plt.plot(d100_times, d100_vals, label="depth=100")
    plt.plot(d100e1_times, d100e1_vals, label="depth=100 explore=1")
    ax.legend(loc='center right')
    plt.show()

def plt_smb():
    '''brute'''
    brute_times = [7.5,15,31,59.9,68.4,76.6,169.9,515.7,5000]
    brute_vals = [717,880,913,932,964,1160,1217,1313,1313]

    '''default'''
    def_times = [6.5,14.2,37.7,62.3,182.3,226.2,554.6,576.7,752.4,5000]
    def_vals = [575,909,935,1027,1067,1147,1174,1280,1456,1456]

    ''' depth=100 '''
    d100_times = [7.3,35.8,261.8,648.6,703.2,4361.9,5000]
    d100_vals = [744,931,1050,1056,1305,1336,1336]

    '''
    gamma = 0.1 depth = 50 explore = 1
    '''
    many_times = [14.2,37.8,46.4,143.7,216.7,674.2,1377.3,4063.4,5397.4]
    many_vals = [485,824,957,1026,1129,1204,1251,1296,1318]

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_xlabel("time (sec)",fontsize=25)
    ax.set_ylabel("Score",fontsize=25)
    ax.set_title("Comparison of Learners: Super Mario Bros",fontsize=40)
    plt.plot(brute_times, brute_vals, label="Brute Forcer")
    plt.plot(def_times, def_vals, label="Default")
    plt.plot(d100_times, d100_vals, label="depth=100")
    plt.plot(many_times, many_vals, label="gamma=0.1,depth=50,explore=1")
    ax.legend(loc='center right')
    plt.show()


def main():
    #plt_airstriker()
    #plt_dkc()
    plt_smb()

if __name__ == '__main__':
    main()
