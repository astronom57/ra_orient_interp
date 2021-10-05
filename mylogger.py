#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct  4 11:20:35 2021

@author: mlisakov
"""
import logging

def create_logger(obj=None, dest=['stderr'], levels=['INFO']):
    """Creates a logger instance to write log information to STDERR.
    
    Args:
        obj: caller object or function with a __name__ parameter
        
        dest (list, default is ['stderr']): a destination where to write 
        logging information. Possible values: 'stderr', 'filename'. Every 
        non-'stderr' string is treated as a filename
            
        levels (list, default is ['INFO']): logging levels. One value per dest 
            is allowed. A single value will be applied to all dest. 
    
    Returns:
        logging logger object
        
    """
    
    # initialize a named logger    
    try:
        logger = logging.getLogger(obj.__name__)
        try:
            logger = logging.getLogger(obj)  # treat obj as a string
        except:
            pass
    except:
        logger = logging.getLogger('')

    # solve the issue of multiple handlers appearing unexpectedly
    if (logger.hasHandlers()):
        logger.handlers.clear()

    # match dimensions of dest and level
    if isinstance(dest, list):
        num_dest = len(dest)
        
    else:
        num_dest = 1
        dest = [dest]
    
    if isinstance(levels, list):
        num_levels = len(levels)
    else:
        num_levels = 1
        levels = [levels]
    
    if num_dest > num_levels:
        for i in np.arange(0, num_dest - num_levels):
            levels.append(levels[-1])
    
    if num_dest < num_levels:
        levels = levels[:len(num_dest)]


    # add all desired destinations with proper levels
    for i, d in enumerate(dest):
        
        if d.upper() in ['STDERR', 'ERR']:
            handler = logging.StreamHandler()   # stderr
        else:
            handler = logging.FileHandler(d, mode='w') # file
            
        
        level = levels[i]
        # set logging level
        if level.upper() not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
            original_level = level
            level = 'INFO'
            logger.setLevel(level)
            logger.error('Logging level was not properly set ({}). Fall back to INFO.'.format(original_level))
        else:
            logger.setLevel(level.upper())
        
        logger.addHandler(handler)
    
    return logger

