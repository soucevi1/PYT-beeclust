import numpy
from scipy.ndimage import measurements
import random
import queue

CONST_EMPTY = 0
CONST_BEE_UP = 1
CONST_BEE_RIGHT = 2
CONST_BEE_DOWN = 3
CONST_BEE_LEFT = 4
CONST_WALL = 5
CONST_HEATER = 6
CONST_COOLER = 7

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
        self.T_env = T_env
        self.min_wait = min_wait

        self.check_constructor_arg_types()
        self.check_constructor_arg_values()

        self.heatmap = numpy.full((map.shape), self.T_env, dtype=float) #float map
        self.bees = self.get_all_bees() # list of tuples
        self.swarms = self.get_all_swarms() # list of list of tuples
        self.recalculate_heat()
        self.score = self.get_score()


    def check_constructor_arg_values(self):
        # Check whether the constructor arguments have correct values

        # Only 2D map is alowed
        if len(self.map.shape) != 2:
            raise ValueError(f'Map shape is must be 2D, is {self.map.shape}')

        # Probability 0 <= p <= 1
        if (self.p_changedir < 0) or (self.p_changedir > 1):
            raise ValueError(f'probability p_changedir must be positive and between 0 and 1, is {self.p_changedir}')
        if (self.p_wall < 0) or (self.p_wall > 1):
            raise ValueError(f'probability p_wall must be positive and between 0 and 1, is {self.p_wall}')
        if (self.p_meet < 0) or (self.p_meet > 1):
            raise ValueError(f'probability p_meet must be positive and between 0 and 1, is {self.p_meet}')

        # Positive temperatures and waiting time
        if (self.k_temp < 0):
            raise ValueError(f'k_temp must be positive, is {self.k_temp}')
        if (self.k_stay < 0):
            raise ValueError(f'k_stay must be positive, is {self.k_stay}')
        if (self.min_wait < 0):
            raise ValueError(f'min_wait must be positive, is {self.min_wait}')

        # Environment must be colder than the heater and hotter than the cooler
        if self.T_env > self.T_heater:
            raise ValueError(f'T_heater colder than environment')
        if self.T_env < self.T_cooler:
            raise ValueError(f'T_cooler hotter than environment')


    def check_constructor_arg_types(self):
        # Check whether the constructor arguments all have correct types
        if type(self.map) is not numpy.ndarray:
            raise TypeError(f'map (type {type(self.map)}) must be numpy array')
        if (type(self.p_changedir) is not float) and (type(self.p_changedir) is not int):
            raise TypeError(f'p_changedir (type {type(self.p_changedir)}) must be float')
        if (type(self.p_wall) is not float) and (type(self.p_wall) is not int):
            raise TypeError(f'p_wall (type {type(self.p_wall)}) must be float')
        if (type(self.p_meet) is not float) and (type(self.p_meet) is not int):
            raise TypeError(f'p_meet (type {type(self.p_meet)}) must be float')
        if (type(self.k_temp) is not float) and (type(self.k_temp) is not int):
            raise TypeError(f'k_temp (type {type(self.k_temp)}) must float')
        if type(self.k_stay) is not int:
            raise TypeError(f'k_stay (type {type(self.k_stay)}) must be int')
        if type(self.T_ideal) is not int:
            raise TypeError(f'T_ideal (type {type(self.T_ideal)}) must be int')
        if type(self.T_heater) is not int:
            raise TypeError(f'T_heater (type {type(self.T_heater)}) must be int')
        if type(self.T_cooler) is not int:
            raise TypeError(f'T_cooler (type {type(self.T_cooler)}) must be int')
        if type(self.T_env) is not int:
            raise TypeError(f'T_env (type {type(self.T_env)}) must be int')
        if type(self.min_wait) is not int:
            raise TypeError(f'min_wait (type {type(self.min_wait)}) must be int')

    def move_bee(self, bee, direction):
        # Move bee in given direction, deal with obstacles
        new_coords = ()
        if direction == CONST_BEE_UP:
            new_coords = (bee[0]-1, bee[1])
        elif direction == CONST_BEE_RIGHT:
            new_coords = (bee[0], bee[1]+1)
        elif direction == CONST_BEE_DOWN:
            new_coords = (bee[0]+1, bee[1])
        elif direction == CONST_BEE_LEFT:
            new_coords = (bee[0], bee[1]-1)

        if ((new_coords[0] < 0) or (new_coords[1] < 0) or 
            (new_coords[0] >= self.map.shape[0]) or 
            (new_coords[1] >= self.map.shape[1])): 
            # out of range
            should_stop = random.randint(1,100)
            if should_stop <= self.p_wall*100:
                T_local = self.heatmap[bee]
                t = int(self.k_stay / (1 + abs(self.T_ideal - T_local))) # time to wait
                self.map[bee] = -max(t, self.min_wait)
            else:
                d = direction + 2 # 180 degree turn
                if d > 4:
                    d -= 4
                self.map[bee] = d
            return bee

        if ((self.map[new_coords] == CONST_WALL) or 
            (self.map[new_coords] == CONST_HEATER) or
            (self.map[new_coords] == CONST_COOLER)):  
            # obstacle in the way
            should_stop = random.randint(1,100)
            if should_stop <= self.p_wall*100:
                T_local = self.heatmap[bee]
                t = int(self.k_stay / (1 + abs(self.T_ideal - T_local))) # time to wait
                self.map[bee] = -max(t, self.min_wait)
            else:
                d = direction + 2 # 180 degree turn
                if d > 4:
                    d -= 4
                self.map[bee] = d
            return bee

        if (self.map[new_coords] <= CONST_BEE_LEFT) and (self.map[new_coords] != 0): #  another bee in the way
            should_stop = random.randint(1,100)
            if should_stop <= self.p_meet *100:
                T_local = self.heatmap[bee]
                t = int(self.k_stay / (1 + abs(self.T_ideal - T_local))) # time to wait
                self.map[bee] = -max(t, self.min_wait)
            return bee

        # move the bee
        self.map[new_coords] = direction
        self.map[bee] = 0
        return new_coords


    def tick(self):
        # Execute one tick of the clock
        new_bees = []
        moved_bees = 0
        for b in self.bees:
            bee_num = self.map[b]
            if bee_num < -1: 
                # bee is waiting
                self.map[b] += 1
                new_bees.append(b) # waiting on the same position
            elif bee_num == -1: 
                # bee was waiting, should move now
                direction = random.randint(1,4)
                new_coords = self.move_bee(b, direction)
                new_bees.append(new_coords)
                if new_coords != b:
                    moved_bees += 1
            else: 
                # bee is moving
                change_d = random.randint(1,100)
                direction = bee_num                
                if change_d <= self.p_changedir*100:
                    dirs = [1,2,3,4]
                    dirs.remove(direction)
                    direction = (random.sample(dirs, 1))[0] # choose 1 new random direction
                new_coords = self.move_bee(b, direction)
                new_bees.append(new_coords)
                if new_coords != b:
                    moved_bees += 1
        self.bees = new_bees
        self.swarms = self.get_all_swarms()
        self.score = self.get_score()
        return moved_bees


    def forget(self):
        # Every bee number is -1
        for b in self.bees:
            self.map[b] = -1


    def calculate_heat(self, coords, dist_cooler, dist_heater):
        # Calculate heat of the given map field
        if (numpy.isnan(dist_cooler)) and (numpy.isnan(dist_heater)):
            # No heater or cooler present
            return self.T_env
        if numpy.isnan(dist_cooler):
            dist_cooler = -1
        if numpy.isnan(dist_heater):
            dist_heater = -1
        cooling = (1 / dist_cooler) * (self.T_env - self.T_cooler)
        heating = (1 / dist_heater) * (self.T_heater - self.T_env)
        temp = self.T_env + self.k_temp * (max(heating, 0) - max(cooling, 0))    
        return temp


    def adjust_distance_map(self, dmap, dev):
        # Calculate distance of every field from giver heater/cooler
        # If distance is greater than what is already in the dmap, 
        #    do not change the value
        dmap[dev] = 0
        q = queue.Queue()
        q.put(dev)

        while not q.empty():
            x = q.get()
            neighbours = [(x[0]-1, x[1]-1), (x[0]-1, x[1]), (x[0]-1, x[1]+1),
                          (x[0], x[1]-1),   (x[0], x[1]+1),   
                          (x[0]+1, x[1]-1), (x[0]+1, x[1]), (x[0]+1, x[1]+1)]
            for n in neighbours:
                if (n[0] < 0) or (n[1] < 0) or (n[0] >= dmap.shape[0]) or (n[1] >= dmap.shape[1]):
                    continue # out of the map
                if self.map[n] == CONST_WALL:
                    continue # wall
                if (dmap[n] != numpy.NaN) and (dmap[n] < dmap[x]+1):
                    continue # field is closer to another device
                dmap[n] = dmap[x] + 1
                q.put(n)

        return dmap


    def get_device_distances(self, devices):
        # Fill the distance map -- map of numbers representing
        # the distances of the given field to the nearest device
        distance_map = numpy.full(self.map.shape, numpy.NaN)
        for d in devices:
            distance_map = self.adjust_distance_map(distance_map, tuple(d))
        return distance_map


    def recalculate_heat(self):
        # Recalculate the heatmap -- fill the heatmap with
        # values corersponding to every field's content

        # Walls have NaN temperature
        walls = numpy.argwhere(self.map == CONST_WALL)
        for w in walls:
            self.heatmap[tuple(w)] = numpy.NaN

        # Heaters have T_heater temperature
        heaters = numpy.argwhere(self.map == CONST_HEATER)
        for h in heaters:
            self.heatmap[tuple(h)] = self.T_heater
        heater_distances = self.get_device_distances(heaters)

        # Coolers have T_cooler temperature
        coolers = numpy.argwhere(self.map == CONST_COOLER)
        for c in coolers:
            self.heatmap[tuple(c)] = self.T_cooler
        cooler_distances = self.get_device_distances(coolers)

        # Other fields' (bees and empty) temperature needs to be calculated
        others = numpy.argwhere(self.map <= CONST_BEE_LEFT)
        for o in others:
            self.heatmap[tuple(o)] = self.calculate_heat(tuple(o), 
                cooler_distances[tuple(o)],heater_distances[tuple(o)])


    def get_all_bees(self):
        # Find positions of all the bees in the map
        l_bees = numpy.argwhere((self.map <= CONST_BEE_LEFT) & (self.map != 0))
        lt_bees = []
        for i in l_bees:
            lt_bees.append(tuple(i))
        return lt_bees


    def get_all_swarms(self):
        # Find positions of all the bee swarms in the map

        # Make map of 1s (bee opsition) and 0s (other)
        clusters = numpy.zeros(self.map.shape, dtype='int')
        for b in self.bees:
            clusters[b] = 1

        # Returns map of clusters with 0s (empty) and cluster numbers
        swarm_map, swarm_cnt = measurements.label(clusters)

        swarms = []
        for n in range(swarm_cnt):
            swarm_coords = numpy.argwhere(swarm_map == n+1)
            l = []
            for s in swarm_coords:
                l.append(tuple(s))
            swarms.append(l)
        return swarms


    def get_score(self):
        # Find average temperature of all the bees
        total = 0
        if len(self.bees) == 0:
            return 0
        for b in self.bees:
            total += self.heatmap[b]
        return total/len(self.bees)