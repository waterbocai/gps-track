# -*- coding: utf-8 -*-

import pylibmc
from model.common import db
#一个公众号最多支持10万个二维码，为了合理利用这个资源，设计SceneidManager来管理这个资源
#原理：1.每100设为1组，一共可以达到1000组，每组用字符串"0"*100来表示，1表示被用，0标识空闲
#      2.用scene_max_seq来标识最大队列
#      3.用scene_seq_n来标识第n个队列
class SceneidManager:
    def __init__(self):
        self.mc = pylibmc.Client()      #初始化一个memcache实例用来保存二维码索引
        if self.mc.get("scene_max_seq") is None:
            self.mc.set("scene_max_seq",0)
            self.mc.set("scene_seq_0","0"*100)
            
    def pop(self):
        for i in range(self.mc.get("scene_max_seq")+1):
                _new_scene_id = self.mc.get("scene_seq_%d"%i).find("0")
                if _new_scene_id != -1: 
                    seq = self.mc.get("scene_seq_%d"%i)
                    self.mc.set("scene_seq_%d"%i,seq[:_new_scene_id]+"1"+seq[_new_scene_id+1:])
                    new_scene_id = i*100+_new_scene_id+1

        #所有scene_id都已经用完，生成一个新的队列
        if _new_scene_id == -1: 
            self.mc.set("scene_max_seq",self.mc.get("scene_max_seq")+1)
            self.mc.set("scene_seq_%d"%self.mc.get("scene_max_seq"),"1"+"0"*99)
            new_scene_id = self.mc.get("scene_max_seq")*100 + 1
        return new_scene_id
         
    def push(self,scene_id):
        seq_no = scene_id/100
        no = scene_id%100
        seq = self.mc.set("scene_seq_%d"%seq_no)
        self.mc.set("scene_seq_%d"%seq_no,seq[:no]+"1"+seq[no+1:])
        db.delete("Scene",where=("scene_id=%d"%scene_id))
        return ""
        
    def push_scene(self,sceneid,_type,_type_id):
        db.insert("Scene",scene_id=sceneid,type=_type,type_id=_type_id)
        return ""
        
