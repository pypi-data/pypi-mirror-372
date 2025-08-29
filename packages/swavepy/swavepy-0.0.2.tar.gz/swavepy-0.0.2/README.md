# SWavePy - Seismic Wave Propagation Simulation

## Usage

Installing with pip

```python
pip install swavepy
```

--------------------------------

Original tutorial taken from Nienke Blom, see [this link](https://github.com/Phlos/WavePy). Updated by [Deborah Wehner](https://github.com/deborahwehner/Cam_WavePy) for use in Cambridge practicals, and updated again here to ensure animated plots work properly, and compiled into a pip-installable module.

Changes made:
- Plotting code rewritten - ensuring that animated plots work properly in updated binder environments
- Small changes to instructions to reflect this
- Branch version which turns the repo into a pip package, for use on colab
--------------------------------

Basic seismic wave propagation code for teaching purposes (python based). With this code, you can:

* run elastic seismic wavefield simulations
* select data windows
* compute sensitivity kernels

## Visualisation functionality
At each stage, visualisation functionality is included. 

### Visualising seismograms
If (after a forward simulation) a seismogram has been attached to a receiver, this can be visualised with:
```python
rec.plot_seismogram()
```

### Visualising window picks
Equally, window picks (and the resulting adjoint sources) can be visualised with
```python
pick = {}
pick['component'] = ['x']   # 'x' or 'z'
pick['times'] = [3.5, 7.5]  # seconds
print('window goes from {} to {} s'.format(pick['times'][0], pick['times'][1]))

receivers_Pwave = waveprop.make_adjoint_source(receivers, pick, plot=3)
```

### Visualising sensitivity kernels
Once sensitivity kernels have been computed, these can be visualised in different parametrisations and as absolute, or relative to a background model. For simple direct waves, it can be instructive to compare the sensitivity kernel to the Fresnel zone. This Fresnel zone can be visualised by setting `plot_Fresnel_zone` to `True`.
```python
kernels..plot_kernels(
    parametrisation='rhovsvp' # could be 'rhomulambda'
    mode='relative',          # could be 'absolute'
    model=model,              # necessary for all kernels other than absolute rhomulambda
    source=src, receiver=receivers[0], 
    plot_Fresnel_zone=True,
)
