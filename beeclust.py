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
        for b in self.bees:
            self.map[b] = -1


    def calculate_heat():
        # spocitej teplo konkretniho policka
        pass


    def get_cooler_distances(coolers):
        # coolers - tuple arrayi x a y souradnic
        # najit vsechny chladice
        # pro kazdy chladic:
        #    projit mapu BFS, brat ohled jenom na zdi
        #    prepisovat vyssi hodnoty mensimi
        pass


    def get_heater_distances(heaters):
        # heaters - tuple arrayi x a y souradnic
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
        walls = numpy.argwhere(self.map == 5)
        for w in walls:
            self.map[tuple(w)] = NaN

        heaters = numpy.argwhere(self.map == 6)
        heater_distances = get_heater_distances(heaters)
        for h in heaters:
            self.map[tuple(h)] = self.T_heater

        coolers = numpy.argwhere(self.map == 7)
        cooler_distances = get_cooler_distances(coolers)
        for c in coolers:
            self.map[tuple(c)] = self.T_cooler

        others = numpy.argwhere(self.map < 5)
        for o in others:
            self.map[tuple(o)] = calculate_heat()


    def get_all_bees():
        l_bees = numpy.argwhere(self.map < 5) # seznam seznamu
        lt_bees = []
        for i in l_bees:
            lt_bees.append(tuple(i))
        return lt_bees


    def get_all_swarms():
        # vytvorit pole, kde vcela == 1, ostatni == 0
        pole = numpy.zeros(self.map.shape, dtype='int')
        for b in self.bees:
            pole[b] = 1

        # vrati pole, kde jsou 0 (nic) a cisla (oznaceni clusteru)
        lw, num = measurements.label(pole)

        sw = [ [] * num ] # list prazdnych listu
        for n in range(num): # pro kazdy swarm
            x = numpy.argwhere(lw == n+1) # seznam seznamu
            for i in x: # pro kazdou souradnici
                sw[n].append(tuple(i)) # propoj do vysledku
        return sw

        #https://stackoverflow.com/questions/25664682/how-to-find-cluster-sizes-in-2d-numpy-array

   
    def get_score():
        # pro kazdou vcelu:
        #    pricti jeji teplotu k sume
        # vydel sumu poctem vcel
        total = 0
        for b in self.bees:
            total += self.heatmap[b]
        return total/len(bees)


b = BeeClust(some_numpy_map)