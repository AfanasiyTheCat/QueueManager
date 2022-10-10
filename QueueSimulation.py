import random
import time
class QueueSimulation:

    DEFAULT_PERIOD_MIN = 0
    DEFAULT_PERIOD_MAX = 4
    DEFAULT_APPEND_PERIOD = 5
    DEFAULT_APPEND_SIZE = 5

    def __init__(self, queues_count):
        self.queues_count = 0
        self.queues = []
        self.queues_periods_min = []
        self.queues_periods_max = []
        self.queues_timers = []
        self.queues_periods_history = []

        self.queue_pop_event = lambda ind, new_size, avg_speed: None

        self.set_queues_count(queues_count)

        self.queue_append_period = self.DEFAULT_APPEND_PERIOD
        self.queue_append_size = self.DEFAULT_APPEND_SIZE

        self.queue_append_timer = 0

        self.is_simulation = False
    
    def _timer(self):
        while self.is_simulation:
            for i in range(len(self.queues)):
                if self.queues[i] == 0:
                    continue
                self.queues_timers[i] -= 1
                if self.queues_timers[i] <= 0:
                    self.queue_pop(i)
            if self.queue_append_timer == 0:
                self.queue_append_timer = self.queue_append_period
                self.append_items(self.queue_append_size)
            self.queue_append_timer -= 1
            time.sleep(1)
    
    def simulation_start(self):
        self.is_simulation = True
        self._timer()
    
    def simulation_stop(self):
        self.is_simulation = False

    def queue_pop(self, ind):
        self.queues[ind] -= 1
        self._update_queue_timer(ind)
    
    def _update_queue_timer(self, ind):
        new_timer = random.randint(self.queues_periods_min[ind], self.queues_periods_max[ind])
        self.queues_timers[ind] = new_timer       
        self.queues_periods_history[ind].append(new_timer)
        self._update_queue(ind) 
        return new_timer

    def _update_queue(self, ind):
        queue_story = self.queues_periods_history[ind][:-1]
        self.queue_pop_event(ind, self.queues[ind], sum(queue_story)*1.0/len(queue_story) if len(queue_story) != 0 else 0)
    
    def _update_queues(self):
        for ind in range(len(self.queues)):
            self._update_queue(ind)

    def append_items(self, n):
        min_queues_inds, delta = self._find_min_queues()
        min_queues_count = len(min_queues_inds)
        num_to_append = delta * min_queues_count if delta != 0 else n # элементы для добавления на этом шаге
        if num_to_append > n:
            num_to_append = n
        for i in range(min_queues_count):
            ind = min_queues_inds[i]
            num_per_queue = int(num_to_append / min_queues_count)
            self.queues[ind] += num_per_queue
        rnd_inds = list(range(len(self.queues)))
        random.shuffle(rnd_inds)
        for i in range(num_to_append % min_queues_count):
            self.queues[rnd_inds[i]] += 1
        n = n - num_to_append
        if n > 0:
            self.append_items(n)
        else:
            self._update_queues()
        
    def _find_min_queues(self):
        min_queues_inds = [0]
        min_queue_val = self.queues[0]
        delta = 0
        for i in range(1, self.queues_count):
            if self.queues[i] == min_queue_val:
                min_queues_inds.append(i)
            if self.queues[i] < min_queue_val:
                delta = min_queue_val - self.queues[i]
                min_queue_val = self.queues[i]
                min_queues_inds = [i]
            if self.queues[i] > min_queue_val and delta == 0:
                delta = self.queues[i] - min_queue_val
        return (min_queues_inds, delta)

    def set_queues_count(self, n):
        if n > self.queues_count:
            for i in range(n - self.queues_count):
                self.queues.append(0)
                self.queues_periods_min.append(self.DEFAULT_PERIOD_MIN)
                self.queues_periods_max.append(self.DEFAULT_PERIOD_MAX)
                self.queues_periods_history.append([])
                self.queues_timers.append(0)
                self._update_queue_timer(len(self.queues_timers)-1)
            self.queues_count = n
        if n < self.queues_count:
            sum = 0
            for i in range(self.queues_count - n):
                sum += self.queues.pop()
                self.queues_periods_min.pop()
                self.queues_periods_max.pop()
                self.queues_periods_history.pop()
                self.queues_timers.pop()
            self.queues_count = n
            self.append_items(sum)
    
    def set_queue_append_period(self, n):
        self.queue_append_period = n

    def set_queue_append_size(self, n):
        self.queue_append_size = n
    
    def set_queue_period_min(self, ind, v):
        self.queues_periods_min[ind] = v
    
    def set_queue_period_max(self, ind, v):
        self.queues_periods_max[ind] = v
        
        