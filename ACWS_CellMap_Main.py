#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CellMap
=======

This script is the main pipeline to analyze immediate early gene expression 
data from iDISCO+ cleared tissue [Renier2016]_.

See the :ref:`CellMap tutorial </CellMap.ipynb>` for a tutorial and usage.

References
----------
.. [Renier2016] `Mapping of brain activity by automated volume analysis of immediate early genes. Renier* N, Adams* EL, Kirst* C, Wu* Z, et al. Cell. 2016 165(7):1789-802 <https://doi.org/10.1016/j.cell.2016.05.007>`_
"""
__author__    = 'Christoph Kirst <christoph.kirst.ck@gmail.com>'
__license__   = 'GPLv3 - GNU General Pulic License v3 (see LICENSE)'
__copyright__ = 'Copyright © 2020 by Christoph Kirst'
__webpage__   = 'http://idisco.info'
__download__  = 'http://www.github.com/ChristophKirst/ClearMap2'

if __name__ == "__main__":
     
  #%%############################################################################
  ### Initialization 
  ###############################################################################
  
  #%% Initialize workspace
  
%gui qt5
from ClearMap.Environment import *  #analysis:ignore

#directories and files
directory = '/d2/studies/ClearMap/SG_OC_IVSA/1RB'    

expression_raw      = '1RB_cfos_stack.tif'  
expression_auto      = '1RB_auto_stack.tif'         

ws = wsp.Workspace('CellMap', directory=directory);
ws.update(raw=expression_raw, autofluorescence=expression_auto)
ws.info()

ws.debug = False
ws.info()

resources_directory = settings.resources_path
  
  #%% Initialize alignment 
  
  #init atals and reference files
#  annotation_file, reference_file, distance_file=ano.prepare_annotation_files(
#      slicing=(slice(None),slice(None),slice(8,303)), orientation=(3,2,1),
#      overwrite=True, verbose=True);
annotation_file = '/d2/studies/ClearMap/SG_OC_IVSA/Annotations_Horizontal_8-302_Full.tif'
reference_file = '/d2/studies/ClearMap/SG_OC_IVSA/Atlas_Horizontal_8-302_Full.tif'

  #alignment parameter files    
  align_channels_affine_file   = io.join(resources_directory, 'Alignment/align_affine.txt')
  align_reference_affine_file  = io.join(resources_directory, 'Alignment/align_affine.txt')
  align_reference_bspline_file = io.join(resources_directory, 'Alignment/align_bspline.txt')
  
  
  #%%############################################################################
  ### Data conversion
  ############################################################################### 
  
  #%% Convet raw data to npy file     
               
  source = ws.source('raw');
  sink   = ws.filename('stitched')
  io.delete_file(sink)
  io.convert(source, sink, processes=None, verbose=True);
  
  source = ws.source('autofluorescence');
  sink   = ws.filename('stitched', postfix='auto')
  io.delete_file(sink)
  io.convert(source, sink, processes=None, verbose=True);

  
  #%%############################################################################
  ### Resampling and atlas alignment 
  ###############################################################################
        
  #%% Resample 
             
  resample_parameter = {
      "source_resolution" : (5,5,4.5),
      "sink_resolution"   : (25,25,25),
      "processes" : 4,
      "verbose" : True,             
      };
  
  io.delete_file(ws.filename('resampled'))
  
  res.resample(ws.filename('stitched'), sink=ws.filename('resampled'), **resample_parameter)
  
  #%%
  p3d.plot(ws.filename('resampled'))
  
  #%% Resample autofluorescence
      
  resample_parameter_auto = {
      "source_resolution" : (5,5,4.5),
      "sink_resolution"   : (25,25,25),
      "processes" : 4,
      "verbose" : True,                
      };    
  
  res.resample(ws.filename('stitched', postfix='auto'), sink=ws.filename('resampled', postfix='autofluorescence'), **resample_parameter_auto)
  
  #p3d.plot([ws.filename('resampled'), ws.filename('resampled', postfix='autofluorescence')])
  
  #%% Aignment - resampled to autofluorescence
  
  # align the two channels
  align_channels_parameter = {            
      #moving and reference images
      "moving_image" : ws.filename('resampled', postfix='autofluorescence'),
      "fixed_image"  : ws.filename('resampled'),
      
      #elastix parameter files for alignment
      "affine_parameter_file"  : align_channels_affine_file,
      "bspline_parameter_file" : None,
      
      #directory of the alig'/home/nicolas.renier/Documents/ClearMap_Ressources/Par0000affine.txt',nment result
      "result_directory" :  ws.filename('resampled_to_auto')
      }; 
  
  elx.align(**align_channels_parameter);
  
  #%% Alignment - autoflourescence to reference
  
  # align autofluorescence to reference
  align_reference_parameter = {            
      #moving and reference images
      "moving_image" : reference_file,
      "fixed_image"  : ws.filename('resampled', postfix='autofluorescence'),
      
      #elastix parameter files for alignment
      "affine_parameter_file"  :  align_reference_affine_file,
      "bspline_parameter_file" :  align_reference_bspline_file,
      #directory of the alignment result
      "result_directory" :  ws.filename('auto_to_reference')
      };
  
  elx.align(**align_reference_parameter);
  
  
  #%%############################################################################
  ### Create test data
  ###############################################################################
  
  #%% Crop test data 
  
  #select sublice for testing the pipeline
  slicing = (slice(600,900),slice(600,900),slice(850,950));
  ws.create_debug('stitched', slicing=slicing);
  ws.debug = True; 
  ws.info()
  #p3d.plot(ws.filename('stitched'))
    
  
  #%%############################################################################
  ### Cell detection
  ###############################################################################
  
  #%% Cell detection:
  from ACWS_cell_detection_parameter import *
  import os

  #cell_detection_parameter = cells.default_cell_detection_parameter.copy();
  #cell_detection_parameter['illumination'] = None;
  #cell_detection_parameter['background'] = None;
  #cell_detection_parameter['intensity_detection']['measure'] = ['source'];
  #cell_detection_parameter['shape_detection']['threshold'] = 500;
  
  io.delete_file(ws.filename('cells', postfix='maxima'))
  ACWS_cell_detection_parameter['maxima_detection']['save'] = ws.filename('cells', postfix='maxima')
  ACWS_cell_detection_parameter['dog_filter']=None
  ACWS_cell_detection_parameter
  ACWS_cell_detection_processing_parameter
#  processing_parameter = cells.default_cell_detection_processing_parameter.copy();
#  processing_parameter.update(
#      processes = None, # 'serial',
#      size_max = 60, #100, #35,
#      size_min = 20,# 30, #30,
#      overlap  = 10, #32, #10,
#      verbose = True
#      )
  
  cells.detect_cells(ws.filename('stitched'), ws.filename('cells', postfix='raw'),
                     cell_detection_parameter=ACWS_cell_detection_parameter, 
                     processing_parameter=ACWS_cell_detection_processing_parameter)
  
  #%% visualization
  
  p3d.plot([[ws.filename('stitched'), ws.filename('cells', postfix='maxima')]])
  
  #%%
  coordinates = np.hstack([ws.source('cells', postfix='raw')[c][:,None] for c in 'xyz']);
  p = p3d.list_plot_3d(coordinates)
  p3d.plot_3d(ws.filename('stitched'), view=p, cmap=p3d.grays_alpha(alpha=1))
  
  
  #%% Cell statistics
  
  source = ws.source('cells', postfix='raw')
  
  plt.figure(1); plt.clf();
  names = source.dtype.names;
  nx,ny = p3d.subplot_tiling(len(names));
  for i, name in enumerate(names):
    plt.subplot(nx, ny, i+1)
    plt.hist(source[name]);
    plt.title(name)
  plt.savefig(os.path.join(directory, 'cells_stats.png'))
  plt.tight_layout();
  
  #%% Filter cells
  
  thresholds = {
      'source' : None,
      'size'   : (8,50)
      }
  
  cells.filter_cells(source = ws.filename('cells', postfix='raw'), 
                     sink = ws.filename('cells', postfix='filtered'), 
                     thresholds=thresholds);
  
  
  #%% Visualize
  
  coordinates = np.array([ws.source('cells', postfix='filtered')[c] for c in 'xyz']).T;
  coordinates.shape
  p = p3d.list_plot_3d(coordinates, color=(1,0,0,0.5), size=5)
  p3d.plot_3d(ws.filename('stitched'), view=p, cmap=p3d.grays_alpha(alpha=1))
  
  
  #%%############################################################################
  ### Cell atlas alignment and annotation
  ###############################################################################
  
  #%% Cell alignment
  
  source = ws.source('cells', postfix='filtered')
  
  def transformation(coordinates):
    coordinates = res.resample_points(
                    coordinates, sink=None, orientation=None, 
                    source_shape=io.shape(ws.filename('stitched')), 
                    sink_shape=io.shape(ws.filename('resampled')));
    
    coordinates = elx.transform_points(
                    coordinates, sink=None, 
                    transform_directory=ws.filename('resampled_to_auto'), 
                    binary=True, indices=False);
    
    coordinates = elx.transform_points(
                    coordinates, sink=None, 
                    transform_directory=ws.filename('auto_to_reference'),
                    binary=True, indices=False);
        
    return coordinates;
    
  
  coordinates = np.array([source[c] for c in 'xyz']).T;
  
  coordinates_transformed = transformation(coordinates);
  
  #%% Cell annotation
  
  label = ano.label_points(coordinates_transformed, key='order');
  names = ano.convert_label(label, key='order', value='name');
  
  #%% Save results
  
  coordinates_transformed.dtype=[(t,float) for t in ('xt','yt','zt')]
  label = np.array(label, dtype=[('order', int)]);
  names = np.array(names, dtype=[('name', 'a256')])
  
  import numpy.lib.recfunctions as rfn
  cells_data = rfn.merge_arrays([source[:], coordinates_transformed, label, names], flatten=True, usemask=False)
  
  io.write(ws.filename('cells'), cells_data)
  
  
  
  #%%############################################################################
  ### Cell csv generation for external analysis
  ###############################################################################
  
  #%% CSV export
  import pandas as pd
  source = ws.source('cells');
  header = ', '.join([h[0] for h in source.dtype.names]);
  np.savetxt(ws.filename('cells', extension='csv'), source[:], header=header, delimiter=',', fmt='%s')
  
  df = pd.read_csv(os.path.join(directory, 'cells.csv'))
  df['Full_Region'] = df.apply(lambda x: ', '.join(x[['region', 'subregion', 'subregion2', 'subregion3']].dropna().astype(str).tolist()), axis=1)
  counts = pd.DataFrame(df.Full_Region.value_counts())
  counts = counts.reset_index()
  counts.columns=['region', 'count']
  counts.to_csv(os.path.join(directory, 'counts.csv'))
  #%% ClearMap 1.0 export
  
  source = ws.source('cells');
  
  clearmap1_format = {'points' : ['x', 'y', 'z'], 
                      'points_transformed' : ['xt', 'yt', 'zt'],
                      'intensities' : ['source', 'dog', 'background', 'size']}
  
  for filename, names in clearmap1_format.items():
    sink = ws.filename('cells', postfix=['ClearMap1', filename]);
    data = np.array([source[name] if name in source.dtype.names else np.full(source.shape[0], np.nan) for name in names]);
    io.write(sink, data);
  
  
  #%%############################################################################
  ### Voxelization - cell density
  ###############################################################################
  
  source = ws.source('cells')
  
  coordinates = np.array([source[n] for n in ['xt','yt','zt']]).T;
  intensities = source['source'];
  
  #%% Unweighted 
  
  voxelization_parameter = dict(
        shape = io.shape(annotation_file), 
        dtype = None, 
        weights = None,
        method = 'sphere', 
        radius = (7,7,7), 
        kernel = None, 
        processes = None, 
        verbose = True
      )
  
  vox.voxelize(coordinates, sink=ws.filename('density', postfix='counts'), **voxelization_parameter);
  
  
  #%% 
  
  p3d.plot(ws.filename('density', postfix='counts'))
  
  
  #%% Weighted 
  
  voxelization_parameter = dict(
        shape = io.shape(annotation_file),
        dtype = None, 
        weights = intensities,
        method = 'sphere', 
        radius = (7,7,7), 
        kernel = None, 
        processes = None, 
        verbose = True
      )
  
  vox.voxelize(coordinates, sink=ws.filename('density', postfix='intensities'), **voxelization_parameter);
  
  #%%
  
  p3d.plot(ws.filename('density', postfix='intensities'))
