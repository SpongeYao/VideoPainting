import threading
import json
import Queue
import random
import math
import time
import Tkinter
import tkFont
import cv2
import numpy as np
from PIL import Image
from PIL import ImageTk

random.seed(0)

class App:
    # Ininitalization
    def __init__(self , queue, frame , width , height , root):
        myfont14 = tkFont.Font(family="Verdana", size=14)
        #btnWidth = 15
        #btnHeight = 2
        self.root = root
        
        self.screen_width, self.screen_height = width, height
        self.frame_width, self.frame_height= int(width*0.8), height
        btn_width, btn_height= 15, 2
        print width,',', height,' ; ',btn_width,',', btn_height
        
        #=====Frame======
        frame= cv2.resize(frame,(self.frame_width,self.frame_height),interpolation=cv2.INTER_LINEAR)
        result = Image.fromarray(frame)
        result = ImageTk.PhotoImage(result)
        self.panel = Tkinter.Label(self.root , image = result)
        self.panel.image = frame
        self.panel.place(x=0, y=0)
        #self.panel.grid(row=0, column=0)
        #self.panel.pack(side = Tkinter.LEFT)

        self.queue = queue
        # ====== panel function setting ======
        self.panel.after(50, self.check_queue)
        self.panel.bind('<Motion>',self.mouse_motion)
        self.panel.bind('<Button-1>',self.mouse_Leftclick)
        
        # ====== Configuration ============
        self.btn_angle90= Tkinter.Button(self.root, text= 'A', command= self.set_Brush90,font= myfont14, width= 2, height=1)
        self.btn_angle90.place(x= self.frame_width+12, y=6)
        self.root.update()
        self.btn_angle180= Tkinter.Button(self.root, text= 'B', command= self.set_Brush180,font= myfont14, width= 2, height=1)
        self.btn_angle180.place(x= self.frame_width+self.btn_angle90.winfo_width()+24, y=6)
        '''
        self.btn_angle360= Tkinter.Button(self.root, text= 'C', command= self.set_Brush360,font= myfont14, width= 2, height=1)
        self.btn_angle360.place(x= self.frame_width+self.btn_angle90.winfo_width()*2+36, y=6)
        '''

        self.root.update()
        self.btn_clear= Tkinter.Button(self.root, text='Clear Image', command= self.btn_clear_click,font= myfont14, width= btn_width, height= btn_height)
        #self.btn_clear.grid(row=0, column=1, sticky = Tkinter.W)
        self.btn_clear.place(x= self.frame_width+12, y= self.btn_angle90.winfo_height()+ 12)
        self.root.update()
        self.btn_saveImg= Tkinter.Button(self.root, text='Save Image', command= self.btn_saveImg_click,font= myfont14, width= btn_width, height= btn_height)
        self.btn_saveImg.place(x= self.frame_width+12, y= self.btn_angle90.winfo_height()+ self.btn_clear.winfo_height()+18)
        print '>> ', self.btn_clear.winfo_height()

        self.mode= 0
        self.saveImg= False
        self.drawing= False
        self.x1, self.y1, self.x2, self.y2= -1,-1,-1,-1        
        self.line_info=[]

    def store(self):
        data = dict()
        data["x_min"] = self.x_min.get()
        data["y_min"] = self.y_min.get()
        data["x_max"] = self.x_max.get()
        data["y_max"] = self.y_max.get()
        with open("detect_area.json" , 'w') as out:
            json.dump(data , out)
        print "detect area set"
        #self.scales.destroy()

    def set_frame(self, frame):
        self.frame= frame

    
    def btn_saveImg_click(self):
        self.saveImg= True
        #cv2.imwrite('Frame1.png',frame)

    def set_Brush90(self):
        self.mode= 0

    def set_Brush180(self):
        self.mode= 1

    def set_Brush360(self):
        self.mode= 2

    def btn_clear_click(self):
        self.line_info= []

    def mouse_motion(self, event):
        #print event
        #print('Mouse position: (%s , %s)' % (event.x, event.y))
        if self.drawing== True:
            self.x2, self.y2= event.x, event.y
            self.line_info[-1][-2]=event.x
            self.line_info[-1][-1]=event.y
        #return True

    def mouse_Leftclick(self, event):        
        #print('Mouse Clicked at : (%s, %s)' % (event.x, event.y))
        if self.drawing == False:
            print 'Start drawing'
            self.drawing= True
            self.x1, self.y1= event.x, event.y
            self.line_info.append([event.x, event.y, -1, -1])
        elif self.drawing == True:
            print 'End drawing'
            self.drawing= False
            self.x2, self.y2= event.x, event.y
            self.line_info[-1][-2]= event.x
            self.line_info[-1][-1]= event.y
        #return True

    def mark_cross_line(self , frame):
        w = frame.shape[0] / 2
        h = frame.shape[1] / 2
        cv2.line(frame , (h - 15 , w) , (h + 15 , w) , (0 , 255 , 0) , 2)
        cv2.line(frame , (h , w - 15) , (h , w + 15) , (0 , 255 , 0) , 2)
        return frame


    def check_queue(self):
        try:
            frame = self.queue.get(block=False)
        except Queue.Empty:
            pass
        else:
            angle_beg=0
            angle_end=0
            frame = self.mark_cross_line(frame)
	    frame= cv2.resize(frame,(self.frame_width,self.frame_height    ),interpolation=cv2.INTER_LINEAR)
            for lines in self.line_info:
                if lines[3]>=0:
                    angle= (math.atan2((lines[3]-lines[1]),(lines[2]-lines[0]))*180/math.pi)
                    cv2.line(frame,(lines[0],lines[1]),(lines[2],lines[3]),(255,0,0),2)

                    #'''
                    if self.mode==0:
                        tmp_x2= lines[2]
                        tmp_y2= lines[1]
                        #angle= 180-abs(angle)

                        if abs(angle) > 90:
                            angle_beg= 180
                            angle= 180-abs(angle)
                            if lines[3]-lines[1] >0:
                                angle_end= 180- angle
                            else:
                                angle_end= 180+ angle
                        elif abs(angle) <90:
                            angle_beg=0 
                            if lines[3]-lines[1] >0:
                                angle_end= abs(angle)
                            else:
                                angle_end= -abs(angle)


                    elif self.mode==1:
                            tmp_x2= abs(lines[2]- lines[0])+lines[0]
                            tmp_y2= lines[1]
                            angle_beg= 0
                            angle_end= angle
                    #'''
                    cv2.line(frame,(lines[0],lines[1]),(tmp_x2,tmp_y2),(255,0,0),2)
                    cv2.ellipse(frame,(lines[0],lines[1]),(50,50),0,angle_beg,(angle_end),255,2)
                    text= '{0:.2f} degree'.format(abs(angle))
                    cv2.putText(frame,text,(lines[2],int((lines[3]+lines[1])*0.5)),cv2.FONT_HERSHEY_SIMPLEX, 0.8 , (200 , 255 , 0) ,2)

            if self.saveImg== True:
                tmp= cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                cv2.imwrite('Frame1.png',tmp)
                self.saveImg= False
            result = Image.fromarray(frame)
            result = ImageTk.PhotoImage(result)
            self.panel.configure(image = result)
            self.panel.image = result
        self.panel.after(1, self.check_queue)

def queue_create(queue, running , app , cap):
    #global cap
    while running:
        ret , frame = cap.read()
        frame = cv2.cvtColor(frame , cv2.COLOR_BGR2RGB)
        queue.put(frame)
        #app.set_frame(frame)
        time.sleep(0.01)

def run(cap):
    running = [True]

    root = Tkinter.Tk()
    root.title("[inQ] Anle Measurement Toolkit")
    root.attributes('-zoomed', True) # FullScreen


    queue = Queue.LifoQueue(5)
    ret , frame = cap.read()
    
    app = App(queue , frame, root.winfo_screenwidth() , root.winfo_screenheight(), root)
    app.panel.bind('<Destroy>', lambda x: (running.pop(), x.widget.destroy()))

    thread = threading.Thread(target=queue_create, args=(queue, running , app , cap))
    thread.start()

    root.mainloop()



cap = cv2.VideoCapture(0)
run(cap)
