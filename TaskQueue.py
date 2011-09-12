#!/usr/bin/env python
import heapq
import datetime
class TaskItem:
    pass
class TaskQueue(list):
    
    def insert(self,item,every=60,now=True):
        titem = TaskItem()
        titem.item = item
        titem.every=every
        if now:
            next = datetime.datetime.now()
        else:
            next = datetime.datetime.now() + datetime.timedelta(seconds=every)
        heapq.heappush(self,(next,titem))
    
    def top(self):
        (next,item) = heapq.nsmallest(1,self)[0]
        if next < datetime.datetime.now():
            next = datetime.datetime.now() + datetime.timedelta(seconds=item.every)
            heapq.heappush(self,(next,item))
            heapq.heappop(self)
            return item

        return None
    
    def execTop(self):
        ltop = self.top()
        if ltop:
            ltop.item()
        
        
        
        
        
    def __init__(self):
        list.__init__(self)
        
        
import unittest
class TestSequence(unittest.TestCase):
    def setUp(self):
        self.taskq = TaskQueue()
    
    def test_taskqueue(self):
        self.taskq.insert("test",every=2,now=False)
        self.assertTrue(len(self.taskq)==1)
        self.assertTrue(self.taskq.top()==None)
        from time import sleep
        sleep(3)
        self.assertTrue(self.taskq.top()!=None)
        
if __name__ == '__main__':
    unittest.main()
