import quantities as pq
import pylgn
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.animation as animation


class MidpointNormalize(colors.Normalize):
    """
    https://matplotlib.org/gallery/userdemo/colormap_normalizations.html
    """
    def __init__(self, vmin=None, vmax=None, midpoint=None, clip=False):
        self.midpoint = midpoint
        colors.Normalize.__init__(self, vmin, vmax, clip)

    def __call__(self, value, clip=None):
        x, y = [self.vmin, self.midpoint, self.vmax], [0, 0.5, 1]
        return np.ma.masked_array(np.interp(value, x, y))


def raster_plot(data, xlabel="Time", ylabel="Neuron",
                orientation='horizontal', lineoffsets=1, linelengths=0.5,
                linewidths=None, colors=None, linestyles="solid"):

    """
    Raster plot

    Parameters
    ----------
    data : list or ndarray
        list/array of spike trains for individual locations.
        Each row corresponds to a location.

    xlabel : str, optional

    ylabel : str, optional

    orientation : {'horizontal', 'vertical'}, optional

    lineoffsets :  scalar or sequence of scalars, optional

    linelengths : scalar or sequence of scalars, optional

    linewidths : scalar, scalar sequence or None, optional

    colors : color, sequence of colors or None, optional

    linestyles : str or tuple or a sequence of such values, optional

    """
    fig, ax = plt.subplots()
    ax.eventplot(np.array(data), colors=colors, lineoffsets=lineoffsets, linelengths=linelengths,
                 orientation=orientation, linewidths=linewidths, linestyles=linestyles)
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    plt.show()

    return fig, ax


def animate_cube(cube, title=None, dt=None,
                 vmin=None, vmax=None, cmap="RdBu_r",
                 save_anim=False, filename="anim.mp4", writer="ffmpeg"):
    """
    Animates 3d array

    Parameters
    ----------
    cube : quantity array/array_like
        input array (Nt x Nx x Ny)

    title : str, optional

    dt : quantity scalar, optional, default: None

    vmin : quantity scalar/float, optional, default: cube.min()

    vmin : quantity scalar/float, optional, default: cube.max()

    save_anim : bool, optional, default: False

    filename : str, optional, default: "anim.mp4"

    writer : str, optional, default: "ffmpeg"

    """
    fig = plt.figure()
    vmin = vmin or cube.min()
    vmax = vmax or cube.max()
    plt.title("") if title is None else plt.title(title)

    def init():
        im.set_data(cube[0, :, :])
        ttl.set_text("")
        return im, ttl

    def animate(j):
        im.set_data(cube[j, :, :])
        ttl.set_text("Frame = " + str(j)) if dt is None \
            else ttl.set_text("Time = {} {}".format(round(j*dt.magnitude, 2),
                                                    dt.dimensionality))
        return im, ttl

    ttl = plt.suptitle("")
    im = plt.imshow(cube[0, :, :], animated=True, vmin=vmin, vmax=vmax,
                    origin="lower", cmap=cmap,
                    norm=MidpointNormalize(midpoint=0.))

    plt.tight_layout()
    plt.subplots_adjust(top=0.9)

    anim = animation.FuncAnimation(fig, animate, init_func=init,
                                   frames=cube.shape[0], interval=50,
                                   repeat=True, repeat_delay=1000)

    plt.colorbar()
    if save_anim:
        anim.save(filename, writer=writer)
    plt.show()

    return anim


def animate_spike_activity(data, times, positions, title=None,
                           marker="o", marker_size=10, marker_color="C0",
                           save_anim=False, filename="anim.mp4", writer="ffmpeg"):

    """
    Animates spike activity

    Parameters
    ----------
    data : array_like
        input array (Nx x Ny x N_spikes)

    times : quantity array

    positions : quantity array

    title : str, optional

    marker : MarkerStyle, optional, default: 'o'
        marker style

    marker_size : float, optional, default: 10
        marker size

    marker_color : color, sequence, or sequence of color, optional, default: 'C0'
        marker color

    save_anim : bool, optional, default: False

    filename : str, optional, default: "anim.mp4"

    writer : str, optional, default: "ffmpeg"

    """
    fig, ax = plt.subplots(1)
    ax.set_xlabel("x (deg)")
    ax.set_ylabel("y (deg)")
    plt.title("") if title is None else plt.title(title)

    Nx, Ny = data.shape
    cube = np.zeros([times.shape[0], Nx, Ny])

    x, y = np.meshgrid(positions, positions)
    dt = times[1] - times[0]

    for m in range(Nx):
        for n in range(Ny):
            ids = np.round(data[m, n][:] / dt).astype(int).magnitude
            for i in ids:
                cube[i, m, n] = marker_size

    def init():
        scat.set_sizes(cube[0, :, :].flatten())
        ttl.set_text("")
        return scat, ttl

    def animate(j):
        scat.set_sizes(cube[j, :, :].flatten())
        ttl.set_text("Time = {} {}".format(round(j*dt.magnitude, 2),
                                           dt.dimensionality))
        return scat, ttl

    ttl = plt.suptitle("")
    scat = plt.scatter(x=x, y=y, s=cube[0, :, :],
                       marker=marker, c=marker_color)

    anim = animation.FuncAnimation(fig, animate, init_func=init,
                                   frames=cube.shape[0], interval=100,
                                   repeat=True, repeat_delay=1000)

    if save_anim:
        anim.save(filename, writer=writer)
    plt.show()

    return anim
