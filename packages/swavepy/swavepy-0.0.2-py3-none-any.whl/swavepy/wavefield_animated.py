from IPython.display import HTML
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

def animate_wavefield(frames, grid, sources=None, receivers=None, interval=50, figsize=(10,5), cmaks=None, cmaks_factor=None):
    """
    Animate precomputed wavefield frames with sources and receivers overlaid.
    
    Parameters
    ----------
    frames : list or np.ndarray
        2D arrays representing wavefield snapshots.
    grid : Grid
        Grid object containing Lx, Lz for scaling axes.
    sources : list of Source or None
        List of sources to plot as circles.
    receivers : list of Receiver or None
        List of receivers to plot as triangles.
    interval : int
        Delay between frames in milliseconds.
    figsize : tuple
        Figure size.
    cmaks : float or None
        Max absolute value for color scaling.
    cmaks_factor: float or None
        Pre-factor to multiply cmaks by; defaults to 1e-12
    """
    plt.ioff()
    fig, ax = plt.subplots(figsize=figsize)
    plt.close(fig)
    
    x_min, x_max = 0, grid.Lx/1000.
    z_min, z_max = 0, grid.Lz/1000.

    stf = sources[0].stf 
    src_amp = [np.linalg.norm((x,z)) for x,z in zip(stf.x, stf.z)] 
    if cmaks_factor:
        cmaks = cmaks_factor*np.max(src_amp)
    else:
        cmaks = 1e-12*np.max(src_amp)
    

    im = ax.imshow(frames[0], animated=True, origin='upper',
                   extent=[x_min, x_max, z_max, z_min],
                   aspect='auto', vmin=-cmaks, vmax=cmaks)
    
    # plot sources
    src_x, src_z = [], []
    if sources is not None:
        for src in sources:
            loc = src.location.asarray() / 1000.
            src_x.append(loc[0])
            src_z.append(loc[1])
    source_scatter = ax.scatter(src_x, src_z, c='k', marker='o')
    
    # plot receivers
    rec_x, rec_z = [], []
    if receivers is not None:
        for rec in receivers:
            loc = rec.location.asarray() / 1000.
            rec_x.append(loc[0])
            rec_z.append(loc[1])
    receiver_scatter = ax.scatter(rec_x, rec_z, c='k', marker='^')

    ax.set(xlabel="horizontal distance / km",ylabel="depth / km")
    
    def update(it):
        im.set_data(frames[it])
        return [im, source_scatter, receiver_scatter]

    anim = FuncAnimation(fig, update, frames=len(frames), interval=interval, blit=True)
    return HTML(anim.to_jshtml())
