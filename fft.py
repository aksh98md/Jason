import numpy as np
import queue

class FFT():
    def __init__(self, time_gap):
        self.avg = 1.0
        self.len = 64
        self.queue = []
        self.time_gap = time_gap
        self.time_span = self.time_gap * self.len
        
    def fft(self, val):
        if val > 850:
            return "並未連上心律量測器"
        
        if len(self.queue) < self.len:
            self.queue = [val] + self.queue
            return None
        else:
            self.queue = self.queue[1:self.len] + [val]
            d = np.array(self.queue)
            d = d - np.average(d)
            df = np.fft.fft(d)
            yf = abs(df)[range(int(self.len/2))]
            f = float(yf.argmax()) / self.time_span
            self.avg = 0.5*f + 0.5*self.avg
            hr = int(self.avg*60)
            ret = "心律："+str(hr)+"下/分 "
            if hr > 200:
                ret += "過快！！！"
            elif hr < 30:
                ret += "過慢！！！"
            else:
                ret += "正常"
            return ret
