#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun  4 09:07:14 2020

@author: smith
"""
import os
directory = '/d2/studies/ClearMap/SG_OC_IVSA/1LT'    

ACWS_cell_detection_parameter = dict( 
  #flatfield
  iullumination_correction = dict(flatfield = None,
                                  scaling = 'mean'),
                       
  #background removal
  background_correction = dict(shape = (8,8),
                               form = 'Disk',
                    save = None), #os.path.join(directory, 'Background.tif')),
  
  #equalization
  equalization = None,
  
  #difference of gaussians filter
  dog_filter = dict(shape = (5,5,6),
                    sigma = None,
                    sigma2 = None,
                    save = None), #os.path.join(directory, 'DoG/DoG_101010.tif')),
  
  #extended maxima detection
  maxima_detection = dict(h_max = None,
                          shape = (7,7,7),
                          threshold = 110,
                          save = None), #os.path.join(directory, 'Maxima/Maxima.tif')),

  #cell shape detection                                  
  shape_detection = dict(threshold = 125,
                         save = None), #os.path.join(directory, 'Shape_125.tif')),
  
  #cell intenisty detection                   
  intensity_detection = dict(method = 'max',
                             shape = (6,6,4),
                             measure = ['source', 'background']), 
)

ACWS_cell_detection_processing_parameter = dict(
  size_max = 60,
  size_min = 20,
  overlap = 10,
  axes = [2],
  optimization = True,
  optimization_fix = 'all',
  verbose = True,
  processes = 5
)
"""Parallel processing parameter for the cell detection pipeline. 
See :func:`ClearMap.ParallelProcessing.BlockProcessing.process` for details."""       



