# -*- coding: utf-8 -*-
"""
Created on Fri Sep 23 11:23:39 2016

@author: Matthias Sachs & Anton Martinsson
"""
import numpy as np
import abc


       
class Integrator(object):
    __metaclass__ = abc.ABCMeta
    
    def __init__(self,model, h):
        
        self.model = model
        self.h = h
        self.q = np.zeros(self.model.dim)
        self.force= np.zeros(self.model.dim) 
        self.outputsheduler = None

    
    def initialise(self, initial_values=None):
        if initial_values is not None:
            for key in initial_values.keys():
                setattr(self, key, initial_values[key])
        self.update_dyn_values();     
        
    def update_dyn_values(self):          
        self.force = self.model.comp_force(self.q)
        
    def run(self, initial_values=None):
        self.initialise(initial_values)
        self.outputsheduler.feed(0)
        for t in range(self.outputsheduler.Nsteps):
            self.traverse()
            self.outputsheduler.feed(t+1)
        
    def traverse(self):
        raise NotImplementedError()
         
    def print_summary(self):
        pass
    

class HamDynIntegrator(Integrator):
    __metaclass__ = abc.ABCMeta
    
    def __init__(self, model, h):
        super(HamDynIntegrator,self).__init__(model, h)
        self.p = np.zeros(self.model.dim)
        
class EulerHamDyn(HamDynIntegrator):
        
    def traverse(self):
        
        # Update gradient        
        self.force = self.model.comp_force(self.q)
        # Update q
        self.q += self.h * self.p
        # Update p
        self.p += self.h * self.force
        
class Thermostat(Integrator):
    __metaclass__ = abc.ABCMeta
    
    def __init__(self, model, h, Tk_B=1.0):
        super(Thermostat,self).__init__(model, h)
        self.Tk_B = None
        self.set_Tk_B(Tk_B)
        
    def set_Tk_B(self, Tk_B):
        self.Tk_B = Tk_B
            
    def anneal(self, tempering_scheme, initial_values=None):
        self.initialise(initial_values)
        for t in range(self.outputsheduler.Nsteps):
            Tk_B = tempering_scheme(t, self.p_h)
            self.set_Tk_B(Tk_B)
            self.traverse()
            self.outputsheduler.feed(t)
        
    def traverse(self):
        raise NotImplementedError()
         
    def print_summary(self):
        pass


class KineticThermostat(Thermostat):
    __metaclass__ = abc.ABCMeta
    
    def __init__(self, model, h, Tk_B=1.0):
        super(KineticThermostat,self).__init__(model, h)
        self.p = np.zeros(self.model.dim)
        
        
        