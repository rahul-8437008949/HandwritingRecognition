# -*- coding: utf-8 -*-
"""
Created on Thu Nov 12 20:35:51 2020

@author: Anant
"""
import os
from flask import Flask, render_template, request, jsonify
import keras
import numpy as np
import random
import matplotlib.pyplot as plt
model=keras.models.load_model("DL-part/Model/model_UJI2_new.h5")
from scalefn import scale_up,scale_down,scale_up_prime
app = Flask(__name__)

#=============================================================================
#MYSQL CONFIGURATION
app.config['SECRET_KEY'] = 'AjJ0lXaX5K9tai8QsUhwwQ'


#HOMEPAGE

@app.route('/',methods=['GET','POST'])
def home():
    if(request.method=='POST'):
        res=request.get_json(force=True)
        #print(res)
        char_stroke=[]
        prevmaxx=-1
        prevminx=1300
        prev_stroke_set=[]
        first=False
        stcount=0
        pos=[]
        curr=[]
        
        for stroke in res:
            lst=[]
            stcount+=1
            for c in stroke:
                  lst.append((float(c['x']),float(c['y'])))
                
            StrokeSet=np.array(lst)
        
            minx = min(StrokeSet[:, 0])
           
            maxx = max(StrokeSet[:, 0])
            
            StrokeSet=list(StrokeSet)
            if((minx<prevmaxx and minx>prevminx  ) or(maxx>prevminx and maxx<prevmaxx)or(minx<prevminx and maxx>prevmaxx) or (minx>prevminx and maxx<prevmaxx)or (minx<prevminx and maxx>prevmaxx)):
                
                prev_stroke_set.extend(StrokeSet)
                prevmaxx=max(maxx,prevmaxx)
                curr.append(stcount)
                
                prevminx=min(minx,prevminx)
            else:
                first=True
                char_stroke.append(np.array(prev_stroke_set))
                pos.append(curr)
                curr=[]
                curr.append(stcount)
                prev_stroke_set=StrokeSet
                prevmaxx=maxx
                prevminx=minx
                
                
        char_stroke.append(np.array(prev_stroke_set))
        word=""
        
        for x in char_stroke:
            print(type(x))
            if(len(x)>240):
                x=scale_down(x,True)
            if(len(x)>120):
                x=scale_down(x,False)
            if(len(x)>60 and len(x)<120):
                x=scale_up_prime(x)
            if(len(x)<=60):
                x=scale_up(x)
            if(len(x)<60):
                x=scale_up(x)
            
            lst=x
            StrokeSet=np.array(lst)
            
            #print(StrokeSet)
            minx = min(StrokeSet[:, 0])
            miny = min(StrokeSet[:, 1])
            maxx = max(StrokeSet[:, 0])
            maxy = max(StrokeSet[:, 1])
    
            #print(minx,miny,maxx,maxy)
    
            StrokeSet[:, 0] = StrokeSet[:, 0] - minx
            StrokeSet[:, 1] = StrokeSet[:, 1] - miny
    
            StrokeSet[:, 0] = StrokeSet[:, 0] / (maxx-minx)
            StrokeSet[:, 1] = StrokeSet[:, 1] / (maxy-miny)
    
    
            if(len(StrokeSet)<120):
                StrokeSet=np.vstack((StrokeSet,(np.zeros((120-len(StrokeSet),2)))))
    
            #print(StrokeSet.shape)
            StrokeSet=np.reshape(StrokeSet,(1,120,2))
    
    
            char_map=['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
           'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
           'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
           'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
           '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    
            #print(StrokeSet)
            y=model.predict(StrokeSet)
    
            y=np.array(y)
            y=np.reshape(y,(62,))
            word+=(str(char_map[np.argmax(y)]))
            

        #print(y[np.argmax(y)]*100)
        return (word+f"")
        
        
    return render_template('index.html',title='Home',character='default')

@app.route('/plot',methods=['GET','POST'])
def plot():
    if(request.method=='POST'):
        res=request.get_json(force=True)
        
        points=[]
        for stroke in res:
            for c in stroke:
                points.append((float(c['x']),float(c['y'])))

        StrokeSet=np.array(points)
        #print(StrokeSet)
        minx = min(StrokeSet[:, 0])
        miny = min(StrokeSet[:, 1])
        maxx = max(StrokeSet[:, 0])
        maxy = max(StrokeSet[:, 1])

        #print(minx,miny,maxx,maxy)

        points=sorted(points)
        # print(points)
        x=[]
        y=[]
        

        for i in points:
            x.append((i[0]-minx)/(maxx-minx))
            y.append((i[1]-miny)/(maxy-miny))
        #print(x,y)

        plt.scatter(x,y)
        plt.axis([0,1,1,0])
        plt.savefig('plot.png')
        plt.close()

    return render_template('index.html',title='Home',character='default')



if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5001, debug=True)