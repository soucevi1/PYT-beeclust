import numpy
from pylab import *
from scipy.ndimage import measurements

class BeeClust:

    def __init__(self, map, p_changedir=0.2, p_wall=0.8, p_meet=0.8, k_temp=0.9,
                 k_stay=50, T_ideal=35, T_heater=40, T_cooler=5, T_env=22, min_wait=2):
        self.map = map
        self.p_changedir = p_changedir
        self.p_wall = p_wall
        self.p_meet = p_meet
        self.k_temp = k_temp
        self.k_stay = k_stay
        self.T_ideal = T_ideal
        self.T_heater = T_heater
        self.T_cooler = T_cooler
        self T_env = T_env
        self.min_wait = min_wait

        self.heatmap = numpy.zeros((map.shape)) #float map
        self.bees = get_all_bees() # list of tuples
        self.swarms = get_all_swarms() # list of list of tuples
        recalculate_heat()
        self.score = get_score()


    def tick():
        # vytvor novy seznam souradnic pro vcely
        # pro kazdou vcelu ve starem:
        #    spocitej pst pohybu
        #    spocitej novou pozici
        #    kontrola kolize se zdi nebo heaterem, pripadne prepocitani
        #    prohledej stary a novy seznam, jestli nedojde ke kolizi se vcelou
        pass


    def forget():
        # pro kazdou vcelu v bees:
        #    na jeji pozici v mape zapis -1
        pass


    def recalculate_heat():
        # projit celou mapu
        # pro kazde pole:
        #    pokud pole == 5 (zed): teplo = NaN
        #    pokud pole == 6 (ohrivac): teplo = T_heater
        #    pokud pole == 7 (chladic): teplo = T_cooler
        #    pokud pole < 4 (nic nebo vcely): teplo se musi spocitat
        #
        # vypocet tepla:
        #    dist_heater = vzdalenost v 8 smerech od nejblizsiho heateru
        #    dist_cooler = vzdalenost v 8 smerech od nejblizsiho cooleru
        #
        # vzdalenost od nejblizsiho: 
        #    separatni pole pro vzdalenosti od chladicu a ohrivacu
        #    metoda pomoci BFS pro kazde policko spocita nejkratsi vzdalenost k ohrivaci
        #        pro kazde policko: 
        #            pokud je ohrivacem: spust z nej BFS
        #                                prepisuj vyssi hodnoty (zacina se s +inf)


    def get_all_bees():
        l_bees = numpy.argwhere(self.map < 5) # seznam seznamu
        lt_bees = []
        for i in l_bees:
            lt_bees.append(tuple(i))
        return lt_bees


    def get_all_swarms():
        # vytvorit pole, kde vcela == 1, ostatni == 0
        # lw, num = measurements.label(pole)
        #    vrati pole, kde jsou 0 (nic) a cisla (oznaceni clusteru)
        #https://stackoverflow.com/questions/25664682/how-to-find-cluster-sizes-in-2d-numpy-array
        pass

   
    def get_score():
        # pro kazdou vcelu:
        #    pricti jeji teplotu k sume
        # vydel sumu opctem vcel
        pass


b = BeeClust(some_numpy_map)